"""¿La base externa de la fase 2 es más fácil que la prueba reservada, por cercanía al ajuste?

La corrida `2026-11-04-artemio-2.13-muestra-de-jorge` mide la concordancia del `aft` sobre la
base externa y sale **0.792**, por encima del 0.720 de la prueba reservada. Su propio cuerpo
avisa de que eso no prueba más generalización, porque no se midió qué tan cerca están esos
compuestos del ajuste y la base pudo separarse por InChIKey y no por andamio. Esto lo mide.

Importa más de lo que parece: el argumento del artículo es que la cifra depende de cuánta
semejanza se permite entre ajuste y evaluación, así que citar un número mejor sobre un
conjunto cuya semejanza nunca se midió contradice la tesis con la que se cita.

## Regla, escrita antes de correr

**Métrica principal:** la fracción de pares de la base externa cuyo **andamio de Bemis-Murcko
ya está en el ajuste**. El andamio y no el esqueleto, porque el andamio es el criterio con el
que se partió la fase 2 (`grupos_cv`, decisión 1.2) y es por tanto la escala en la que «ya
visto» significa lo mismo en los dos conjuntos.

**Lectura declarada:**

- Si la fracción queda **en el piso que fija el control**, la base externa está separada con
  el mismo criterio que la prueba reservada y el 0.792 se puede citar al lado del 0.720 sin
  salvedad de cercanía.
- Si **supera 0.05**, la base es estructuralmente más fácil: el 0.792 mide un problema
  distinto y no se compara con el 0.720 sin decirlo.
- Entre el piso y 0.05 se reporta el número y se dice que la comparación es aproximada.

**El piso no es cero, y por qué:** la columna `andamio` de `fase2_pares.parquet` no es
reproducible desde la columna `smiles` de su propia fila. `tabla_de_pares` guarda
`andamio=("andamio", "first")` y `smiles=("smiles_raw", mode)`, así que el andamio es el de la
primera medición del par y el SMILES el de la más frecuente, y para un 0.74% de las filas son
tautómeros distintos del mismo esqueleto. La base externa no trae columna `andamio`, así que
hay que recalcularlo, y entonces **las dos partes de la comparación tienen que recalcularlo o
la comparación mide la discrepancia de definición y no la contaminación**. El control mide
cuánto vale ese piso. Esta precisión de la regla se escribió **después de correr el control y
antes de ver la base externa**, que es para lo que el control está.

La similitud de Tanimoto al vecino más cercano del ajuste se reporta siempre, porque el
andamio es binario y la similitud ordena: dos bases con cero solapamiento de andamio pueden
estar a distancias muy distintas. **La referencia es el control de esta misma corrida**, que
la mide sobre la validación de la fase 2 contra el ajuste.

**Y no el 0.414 que este script citaba antes:** ese sale de
`2026-11-03-artemio-1.2-escalera-ampliada-permeabilidad`, que es la prueba reservada de la
**fase 1**. Todo lo que esta corrida compara —la base externa, el control, el 0.792 contra el
0.720— es de la fase 2, así que poner el 0.414 al lado contrasta dos fases y exagera la
distancia: contra el control en fase la diferencia es de 0.108 y no de 0.373. La similitud de
la prueba reservada **de la fase 2 no está medida**, porque medirla cuesta un acceso a la
prueba; mientras no se mida, la referencia es la validación y hay que escribir esa palabra al
citarla.

**Nada se decide con esto.** No cambia el modelo, ni la elección, ni ninguna cifra publicada:
solo dice si dos números son comparables.

## Control

Validación contra entrenamiento tiene que dar **cero** solapamiento de andamio y de
esqueleto, porque la partición de la fase 2 agrupa por los dos. Si no da cero, el medidor
está mal y la corrida se aborta antes de mirar la base externa. **El control no lee la prueba
reservada**, justamente para que medir la contaminación no cueste un acceso.

Uso::

    python scripts/experimento_contaminacion_externa.py [ruta/al/Testeo.csv]

Sin argumento corre solo el control, que es lo que se puede verificar sin el archivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ))

from src.data_prep.splits import andamio_murcko, esqueleto_conectividad  # noqa: E402
from src.tracking import Corrida, sha256  # noqa: E402

RDLogger.DisableLog("rdApp.*")

PARES = RAIZ / "data" / "processed" / "fase2_pares.parquet"
TESTEO_POR_OMISION = Path.home() / "Downloads" / "snc_activity_crudo_v3_final_2026-09-25_Testeo.csv"

# La referencia la mide el control de la propia corrida, no una constante: una cifra de otra
# fase no sitúa esta, y una constante escrita a mano no lleva su fase pegada.
REFERENCIA_SIMILITUD = "el control de esta corrida: la validacion de la fase 2 contra el ajuste"
# La lectura declarada arriba.
CORTE_COMPARABLE = 0.05

GENERADOR = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


def estructuras(smiles: pd.Series) -> pd.DataFrame:
    """SMILES canónico, andamio y esqueleto de cada estructura única.

    Se calcula una vez por estructura y no por par: la base externa repite compuestos
    entre dianas, y RDKit es lo caro de esta corrida.
    """
    unicos = pd.Index(smiles.dropna().unique())
    filas = []
    for s in unicos:
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            filas.append((s, None, None, None))
            continue
        filas.append((s, Chem.MolToSmiles(mol), andamio_murcko(mol), esqueleto_conectividad(mol)))
    return pd.DataFrame(filas, columns=["smiles", "canonico", "andamio", "esqueleto"])


def huellas(smiles: list[str]) -> list:
    """ECFP4 de 2048 bits; `radius=2` es ECFP4 porque el nombre lleva el diámetro."""
    salida = []
    for s in smiles:
        mol = Chem.MolFromSmiles(s)
        salida.append(GENERADOR.GetFingerprint(mol) if mol is not None else None)
    return salida


def similitud_al_vecino(consulta: list[str], referencia: list[str]) -> np.ndarray:
    """Tanimoto máximo de cada estructura de `consulta` contra todas las de `referencia`."""
    hr = [h for h in huellas(referencia) if h is not None]
    return np.array([max(DataStructs.BulkTanimotoSimilarity(h, hr)) if h is not None else np.nan
                     for h in huellas(consulta)], dtype=float)


def solapamiento(consulta: pd.DataFrame, ajuste: pd.DataFrame, n_pares: pd.Series | None = None
                 ) -> dict:
    """Las tres vías por las que una estructura puede estar ya vista, de más a menos estricta.

    `n_pares` pondera por pares cuando una estructura aparece contra varias dianas: la
    fracción que importa para comparar concordancias es por par, no por compuesto.
    """
    salida = {}
    for via, col in (("smiles_exacto", "canonico"), ("esqueleto", "esqueleto"),
                     ("andamio", "andamio")):
        vistos = set(ajuste[col].dropna())
        marca = consulta[col].isin(vistos)
        salida[f"{via}_compuestos"] = int(marca.sum())
        salida[f"{via}_fraccion_compuestos"] = round(float(marca.mean()), 4)
        if n_pares is not None:
            peso = consulta["smiles"].map(n_pares).fillna(0)
            salida[f"{via}_fraccion_pares"] = round(float(peso[marca].sum() / peso.sum()), 4)
    return salida


def main() -> None:
    externa = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if externa is not None and not externa.exists():
        sys.exit(f"no existe {externa}")
    if externa is None and TESTEO_POR_OMISION.exists():
        externa = TESTEO_POR_OMISION

    pares = pd.read_parquet(PARES)
    # El archivo externo queda fuera del repositorio: `Corrida` solo acepta rutas dentro de él, así que
    # su huella va en los parámetros (misma solución que la corrida de la muestra de Jorge).
    datos = [PARES]

    with Corrida("contaminacion-externa", decision="2.13", params={
            "metrica_principal": "fraccion de pares de la base externa con andamio ya en el ajuste",
            "corte_declarado": CORTE_COMPARABLE,
            "vias": ["smiles canonico", "esqueleto de conectividad", "andamio de Bemis-Murcko"],
            "huella_similitud": {"tipo": "ECFP4", "radio": 2, "bits": 2048},
            "referencia_de_similitud": REFERENCIA_SIMILITUD,
            "control": "validacion contra entrenamiento, cero por construccion; no lee la prueba",
            "regla": "declarada en el docstring antes de correr; nada se decide con esto",
            "externa_sha256": sha256(externa) if externa else None,
    }, semillas=[], datos=datos) as c:

        metricas: dict = {}

        # --- Control: validacion contra entrenamiento, que tiene que dar cero ---
        tr = pares[pares.particion.eq("entrenamiento")]
        va = pares[pares.particion.eq("validacion")]
        e_tr = estructuras(tr.smiles)
        e_va = estructuras(va.smiles)
        ctrl = solapamiento(e_va, e_tr, va.groupby("smiles").size())
        # Con las columnas guardadas, que es como se partio: tiene que dar cero en las dos.
        guardado = {
            "andamio": len(set(va.andamio.dropna()) & set(tr.andamio.dropna())),
            "esqueleto": len(set(va.esqueleto.dropna()) & set(tr.esqueleto.dropna())),
        }
        ctrl["con_las_columnas_guardadas"] = guardado
        print("control (validacion contra entrenamiento):", ctrl, flush=True)
        if guardado["andamio"] or guardado["esqueleto"]:
            raise AssertionError(
                "el control falla sobre las columnas con las que se particiono: validacion y "
                "entrenamiento comparten andamio o esqueleto, asi que hay fuga en la particion")
        if ctrl["esqueleto_compuestos"]:
            raise AssertionError(
                "el control falla: recalculado desde el SMILES, el esqueleto de conectividad se "
                "repite entre validacion y entrenamiento. El esqueleto si es reproducible desde "
                "el SMILES, asi que esto seria fuga y no discrepancia de definicion")
        # El andamio recalculado no da cero, y ese es el piso contra el que se juzga la externa.
        ctrl["piso_andamio_recalculado"] = ctrl["andamio_fraccion_pares"]
        ctrl["similitud_mediana_al_entrenamiento"] = round(
            float(np.nanmedian(similitud_al_vecino(list(e_va.smiles), list(e_tr.smiles)))), 4)
        print("control, similitud mediana:", ctrl["similitud_mediana_al_entrenamiento"], flush=True)
        metricas["control"] = ctrl

        # --- La base externa ---
        if externa is None:
            metricas["base_externa"] = "no disponible en esta maquina; el control si corre"
            print("\nAVISO: falta el archivo de la base externa. Solo se midio el control.")
        else:
            from src.data_prep.pares_fase2 import tabla_de_pares
            tabla = tabla_de_pares(pd.read_csv(externa, low_memory=False))
            ajuste = pares[pares.particion.ne("prueba")]
            e_aj = estructuras(ajuste.smiles)
            e_ex = estructuras(tabla.smiles)
            res = solapamiento(e_ex, e_aj, tabla.groupby("smiles").size())
            sim = similitud_al_vecino(list(e_ex.smiles), list(e_aj.smiles))
            res.update({
                "pares": int(len(tabla)),
                "compuestos": int(len(e_ex)),
                "similitud_mediana": round(float(np.nanmedian(sim)), 4),
                "similitud_media": round(float(np.nanmean(sim)), 4),
                "similitud_p90": round(float(np.nanpercentile(sim, 90)), 4),
                "fraccion_por_encima_de_0.6": round(float(np.nanmean(sim > 0.6)), 4),
                # En fase, y al lado de la cifra, para que nadie la contraste con otra fase.
                "similitud_mediana_del_control": ctrl["similitud_mediana_al_entrenamiento"],
            })
            f = res["andamio_fraccion_pares"]
            piso = ctrl["piso_andamio_recalculado"]
            res["piso_del_control"] = piso
            res["veredicto"] = (
                f"NO comparable sin decirlo: {f:.1%} de los pares tiene el andamio ya visto, "
                f"contra el {piso:.1%} del control" if f > CORTE_COMPARABLE
                else f"comparable: {f:.1%} contra el {piso:.1%} del control" if f <= piso * 2
                else f"comparacion aproximada: {f:.1%} contra el {piso:.1%} del control")
            print("\nbase externa:", res["veredicto"], flush=True)
            metricas["base_externa"] = res

        c.metricas(metricas)


if __name__ == "__main__":
    main()
