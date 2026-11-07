#!/usr/bin/env python3
"""¿Es la ceguera a la quiralidad lo que hace que las huellas dañen el estrato de análogos? (#183)

En el 05c las huellas Sort & Slice perjudican a los **nueve** modelos en el estrato
`análogo estereoquímico`, sin una sola excepción. El #183 guarda dos explicaciones enredadas:

1. **Las huellas son ciegas a la quiralidad.** `GetMorganGenerator` no recibe `includeChirality`,
   cuyo valor por omisión es `False`, así que dos enantiómeros dan la misma huella. Y el estrato
   está definido por eso: lo arma `asignar_origen` con los compuestos que coinciden con un
   natural solo en la `key14`, los primeros 14 caracteres del InChIKey, que codifican únicamente
   la conectividad.
2. **El estrato está enriquecido en registros incompletos.** Un compuesto cuyo registro no
   declara la estereoquímica cae en `análogo estereoquímico` sin que haya ninguna diferencia
   estereoquímica real, y el 54.4% del estrato tiene al menos un centro sin declarar.

**El diseño, declarado en el #183 antes de esta corrida.** Las huellas se comparan **contra sí
mismas**, con `includeChirality` en `False` y en `True`, y se cuenta cuántas filas comparten
huella exacta con otra de clase contraria —lo que ningún modelo puede separar—. Si la quiralidad
es el mecanismo, ese conteo tiene que bajar al activarla.

Dos diseños que el #183 descartó, y por qué, para no repetirlos:

- **Rehacer las huellas con `True` y mirar el estrato entero.** Es inerte donde la estereoquímica
  no está declarada, así que «no mejora ahí» está garantizado por construcción.
- **Comparar la brecha de choques entre huellas y descriptores por subgrupo.** Los descriptores
  llevan `NumUnspecifiedAtomStereoCenters`, que es un sensor específico de registro incompleto, y
  las huellas no tienen nada equivalente: la comparación entre representaciones no aísla la
  quiralidad. Por eso aquí no entra ninguna otra representación.

**Lo que esta corrida añade al diseño del #183.** Una fila puede dejar de chocar sin que su propia
huella cambie, porque la que chocaba *con* ella se movió. Eso importa justo en la mitad sin
declarar, donde la explicación 1 predice que no hay nada que codificar: sin separarlo, una caída
ahí se leería como quiralidad cuando es efecto de la pareja. Así que de cada fila que deja de
chocar se reporta si su propia huella cambió.

**Y lo que el interruptor cuesta**, que no sale del conteo de inseparables: activarlo parte cada
subestructura con estereocentro en sus variantes, así que con el mismo presupuesto de 2,048 columnas
el vocabulario cubre una fracción menor de las apariciones. Sin esa cifra, un reajuste con la bandera
activada mezclaría «gana resolución» con «pierde cobertura».

Se mide sobre las 6,306 filas de ajuste (entrenamiento y validación). **No toca la prueba
reservada** y no ajusta ningún modelo.

    ./env/bin/python scripts/experimento_quiralidad_huellas.py
"""
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from rdkit import Chem

from src.features.huellas import identificadores_morgan
from src.features.molecular import a_mol
from src.models.tareas import DESCRIPTORES, ORIGENES, PROCESADOS, cargar
from src.tracking import Corrida

N_BITS = 2048
RADIO = 2


def conjuntos(huellas, identificadores) -> np.ndarray:
    """Una fila → el conjunto de subestructuras que tiene, para comparar huellas exactas.

    Se compara el conjunto y no el vector denso porque la matriz sin plegar tiene decenas de
    miles de columnas; dos filas con el mismo conjunto tienen el mismo vector.
    """
    huellas = huellas.tocsr()
    return np.array([frozenset(identificadores[huellas.indices[a:b]].tolist())
                     for a, b in zip(huellas.indptr[:-1], huellas.indptr[1:])], dtype=object)


def inseparables(llaves: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Máscara de las filas que comparten su huella exacta con otra de clase contraria."""
    por_llave = pd.DataFrame({"k": llaves, "y": y}).groupby("k")["y"].nunique()
    return pd.Series(llaves).isin(set(por_llave.index[por_llave > 1])).to_numpy()


def sort_and_slice(llaves: np.ndarray, n_bits: int) -> np.ndarray:
    """Las `n_bits` subestructuras más frecuentes, que es lo que el modelo acaba viendo.

    Mismo criterio que `AgregarHuellas.fit`: frecuencia por fila, empates por identificador. El
    vocabulario se aprende aquí sobre las filas de ajuste —no hay pliegues porque no se ajusta
    ningún modelo— y cada brazo aprende el suyo, que es lo que haría cada canalización.
    """
    frecuencia = Counter()
    for s in llaves:
        frecuencia.update(s)
    vocabulario = {k for k, _ in sorted(frecuencia.items(), key=lambda kv: (-kv[1], kv[0]))[:n_bits]}
    return np.array([s & vocabulario for s in llaves], dtype=object)


def vocabulario(llaves: np.ndarray, n_bits: int) -> dict:
    """Cuántas subestructuras distintas hay y qué fracción de las apariciones cubren las `n_bits`.

    Es el costo del interruptor que no se ve en el conteo de inseparables: activar la quiralidad
    parte cada subestructura con estereocentro en sus variantes, así que con el mismo presupuesto de
    columnas el vocabulario cubre menos. Sin esto, un reajuste con la bandera activada mezcla «gana
    resolución» con «pierde cobertura» y un resultado plano no se puede leer.
    """
    frecuencia = Counter()
    for conjunto in llaves:
        frecuencia.update(conjunto)
    ordenadas = sorted(frecuencia.items(), key=lambda kv: (-kv[1], kv[0]))
    total = sum(frecuencia.values())
    elegidas = ordenadas[:n_bits]
    return {"distintas": len(frecuencia),
            "apariciones": total,
            "cubiertas_por_n_bits": sum(c for _, c in elegidas),
            "cobertura_pct": round(sum(c for _, c in elegidas) / total * 100, 1),
            "corte_de_frecuencia": elegidas[-1][1] if elegidas else 0}


def tabla(mascara_falso, mascara_verdadero, grupos: dict[str, np.ndarray]) -> dict:
    """Por subconjunto: cuántas filas son inseparables con cada brazo."""
    salida = {}
    for nombre, sel in grupos.items():
        n = int(sel.sum())
        salida[nombre] = {
            "n": n,
            "sin_quiralidad": int(mascara_falso[sel].sum()),
            "con_quiralidad": int(mascara_verdadero[sel].sum()),
            "sin_quiralidad_pct": round(float(mascara_falso[sel].mean() * 100), 1),
            "con_quiralidad_pct": round(float(mascara_verdadero[sel].mean() * 100), 1),
        }
    return salida


def main() -> None:
    t = cargar("permeabilidad", estratos="origen")
    smiles = t.meta["SMILES"].tolist()
    y = t.y
    columnas = pd.read_parquet(PROCESADOS / DESCRIPTORES["descriptores"]).columns
    declarados = t.X[:, columnas.get_loc("NumAtomStereoCenters")]
    sin_declarar = t.X[:, columnas.get_loc("NumUnspecifiedAtomStereoCenters")] > 0

    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"radio": RADIO, "n_bits": N_BITS, "brazos": ["includeChirality=False",
                                                           "includeChirality=True"],
              "filas": "ajuste (entrenamiento y validación); la prueba no se toca",
              "lectura": "filas que comparten huella exacta con otra de clase contraria"}
    with Corrida("quiralidad-huellas", decision="1.3", params=params, semillas=[],
                 datos=datos) as c:
        llaves = {}
        for quiral in (False, True):
            huellas, ident = identificadores_morgan(smiles, radio=RADIO, quiralidad=quiral)
            llaves[quiral] = conjuntos(huellas, ident)
        # Control del arnés: con `False` tiene que reproducir las cifras que el #183 ya midió
        # por otra vía (88 de 768 en el estrato de análogos). Si no, no se compara nada.
        choca = {q: inseparables(llaves[q], y) for q in (False, True)}
        plegado = {q: inseparables(sort_and_slice(llaves[q], N_BITS), y) for q in (False, True)}
        cambia = np.array([a != b for a, b in zip(llaves[False], llaves[True])])

        es = {o: t.meta["origen"].eq(o).to_numpy() for o in ORIGENES}
        analogo = es[ORIGENES[1]]
        grupos = {**es,
                  "análogo · estereoquímica declarada": analogo & ~sin_declarar,
                  "análogo · estereoquímica sin declarar": analogo & sin_declarar}

        # De las que dejan de chocar: ¿cambió su propia huella, o se movió la pareja?
        descomposicion = {}
        for nombre in ("análogo · estereoquímica declarada",
                       "análogo · estereoquímica sin declarar"):
            dejan = grupos[nombre] & choca[False] & ~choca[True]
            descomposicion[nombre] = {
                "dejan_de_chocar": int(dejan.sum()),
                "su_huella_cambia": int((dejan & cambia).sum()),
                "su_huella_no_cambia": int((dejan & ~cambia).sum()),
            }

        # Qué hace el interruptor, para no atribuirle lo que no hace: cambia la huella de las
        # filas con estereoquímica declarada, de átomo o de enlace.
        con_enlace = np.array([any(b.GetStereo() != Chem.BondStereo.STEREONONE
                                   for b in a_mol(s).GetBonds()) for s in smiles])
        sin_centro = declarados == 0
        # Piso que ninguna representación puede bajar: el mismo SMILES con clase contraria.
        identico = inseparables(np.asarray(smiles, dtype=object), y)

        sin_plegar = tabla(choca[False], choca[True], grupos)
        c.metricas({
            "filas": len(y),
            "sin_plegar": sin_plegar,
            "sort_and_slice_2048": tabla(plegado[False], plegado[True], grupos),
            "por_que_dejan_de_chocar": descomposicion,
            "huella_cambia_al_activar": {
                "filas": int(cambia.sum()),
                "pct": round(float(cambia.mean() * 100), 1),
                "con_estereocentro_de_atomo_declarado": int((cambia & ~sin_centro).sum()),
                "de_un_total_con_estereocentro": int((~sin_centro).sum()),
                "sin_estereocentro_de_atomo": int((cambia & sin_centro).sum()),
                "de_esas_con_estereo_de_enlace": int((cambia & sin_centro & con_enlace).sum()),
                "sin_cambio_y_con_estereo_de_enlace": int((~cambia & sin_centro & con_enlace).sum()),
            },
            "vocabulario": {"sin_quiralidad": vocabulario(llaves[False], N_BITS),
                            "con_quiralidad": vocabulario(llaves[True], N_BITS)},
            "smiles_identico_con_clase_contraria": int(identico.sum()),
            "choques_restantes_con_quiralidad": int(choca[True].sum()),
        })

        print(f"{len(y):,} filas de ajuste\n")
        for nombre, d in sin_plegar.items():
            print(f"  {nombre:40s} {d['sin_quiralidad']:4d}/{d['n']:4d} "
                  f"({d['sin_quiralidad_pct']:5.1f}%) → {d['con_quiralidad']:4d} "
                  f"({d['con_quiralidad_pct']:5.1f}%)")
        print()
        for nombre, d in descomposicion.items():
            print(f"  {nombre}: dejan de chocar {d['dejan_de_chocar']}, "
                  f"su huella cambia {d['su_huella_cambia']}, "
                  f"no cambia {d['su_huella_no_cambia']}")
        voc = {q: vocabulario(llaves[q], N_BITS) for q in (False, True)}
        print(f"\n  vocabulario: {voc[False]['distintas']:,} subestructuras distintas sin quiralidad "
              f"-> {voc[True]['distintas']:,} con; cobertura de los {N_BITS:,} bits "
              f"{voc[False]['cobertura_pct']}% -> {voc[True]['cobertura_pct']}%")
        print(f"\n  carpeta: experimentos/{c.id}")


if __name__ == "__main__":
    main()
