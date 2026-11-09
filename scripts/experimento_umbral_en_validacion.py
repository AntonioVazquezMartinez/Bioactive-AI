#!/usr/bin/env python3
"""¿Cuánto del derrumbe del MCC en la prueba recupera un umbral elegido en validación? (#191)

El MCC de la fase 1 cae 52% en la prueba reservada (0.7017 → 0.3385) mientras el AUROC cae
14% (0.9190 → 0.7928). Esa asimetría es la firma de un **punto de operación fijo** encima de
un cambio de distribución, no solo de pérdida de orden: el MCC corta la probabilidad en 0.5 y
el AUROC no corta en ninguna parte. A 0.5 el modelo declara BBB+ al 70.9% de las filas de
ajuste contra una prevalencia de 64.97%, y la prueba tiene 57.3% de BBB+.

Tres lecturas del MCC ya están medidas en la escalera
(`2026-11-04-artemio-1.2-mcc-en-la-escalera-permeabilidad`): el corte fijo, el de igual
prevalencia y el óptimo del pliegue. **La que falta, y es la única que se puede reportar como
resultado, es el umbral elegido con validación interna agrupada**, que es lo que el #191 deja
abierto y lo que la [1.5](../docs/decisiones.md#d1-5) dice que haría falta para recuperar parte
de la caída. El corte óptimo usa las etiquetas de lo que evalúa, así que es una cota y no un
número que se pueda entregar; el de igual prevalencia no usa etiquetas pero tampoco usa
validación, y en el peldaño del proyecto salió *peor* que 0.5 (−0.0225).

## El diseño, declarado antes de correr

**Fase A, sin tocar la prueba.** `svm_rbf` como se entrega, 151 descriptores, las 6,306 filas de
ajuste en 1,048 grupos, validación cruzada agrupada de 3 semillas × 5 pliegues. De las
probabilidades fuera de pliegue de cada semilla se elige el corte que maximiza el MCC. El
**corte congelado** es la mediana de los tres de semilla, redondeada a tres decimales; la
fórmula se fija aquí y no se cambia después de ver nada.

**La guarda que nadie había puesto: dejar una semilla fuera.** Elegir el corte con las mismas
etiquetas con las que luego se mide infla la ganancia, y es el mismo error de forma que el
corte óptimo. Así que para cada semilla se elige el corte con las **otras dos** y se mide en
ella. La diferencia entre la ganancia dentro de muestra y la de semilla dejada fuera es cuánto
de la ganancia era ajustar el corte a sus propias etiquetas; si la de fuera de muestra se cae,
la de dentro no se reporta.

**Fase B, una sola lectura de la prueba, y solo con `--leer-prueba`.** El modelo se reajusta con
las 6,306 filas y se evalúa una vez sobre las 1,499 reservadas, con el corte **ya congelado por
la fase A**. Se reportan cuatro números con las mismas predicciones: el corte fijo de 0.5
(control: tiene que reproducir el 0.3385 registrado), el corte congelado, el de igual
prevalencia del ajuste (0.650) y el óptimo de la prueba, que es **cota y no resultado** porque
usa sus etiquetas. El intervalo de la diferencia `congelado − 0.5` se obtiene remuestreando
**grupos de andamio**, no filas.

**La lectura, declarada antes.** La diferencia pareada no tiene umbral de paso, que es la
lección de la [1.10](../docs/decisiones.md#d1-10): su umbral se puso contra la dispersión del
nulo y dejó la regla con 26.6% de potencia sin que se notara hasta después de correr. Aquí se
reporta la diferencia con su intervalo y se dice qué queda descartado.

**Y se declara que un resultado negativo es un resultado.** La validación tiene 65.0% de BBB+ y
la prueba 57.3%: un corte elegido donde la prevalencia es más alta **no tiene por qué moverse en
la dirección que la prueba necesita**, y la escalera ya mostró que el corte de igual prevalencia
es peor que 0.5 en el peldaño del proyecto. Si el corte congelado no recupera nada, eso es lo
que se escribe, y la conclusión del Avance 5 no cambia: el AUROC de 0.7928 no depende del corte.

**Lo que no hace.** No reentrena, no afina ningún hiperparámetro, no cambia el modelo entregado
ni la partición, y no toca la fase 2. No arregla el otro defecto del #191 —que la calibración
interna del SVM parte sin agrupar—, que la [1.5](../docs/decisiones.md#d1-5) ya midió en −0.0012
de MCC y declaró como excepción.

    ./env/bin/python scripts/experimento_umbral_en_validacion.py                 # fase A
    ./env/bin/python scripts/experimento_umbral_en_validacion.py --leer-prueba   # A y B
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.metrics import matthews_corrcoef, roc_auc_score  # noqa: E402

from src.evaluation.cv import evaluar  # noqa: E402
from src.models.alternativos import seleccion  # noqa: E402
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar  # noqa: E402
from src.tracking import Corrida, tomar_prueba  # noqa: E402

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
MCC_CV_REGISTRADO = 0.7017        # de la 1.5; control de la fase A
MCC_PRUEBA_REGISTRADO = 0.3385    # de la 1.5; control de la fase B
AUROC_PRUEBA_REGISTRADO = 0.7928
TOLERANCIA = 0.003
PREVALENCIA_AJUSTE = 0.650        # declarada en la 1.2; el corte de igual prevalencia la usa
REMUESTREOS = 2000
REPETICIONES = 300                # particiones de grupos en mitades, por semilla
# Dos mallas de cortes, porque el resultado es sensible a ella y eso se reporta en lugar de
# elegir la que convenga: la de cuantiles de las probabilidades y una fija, la de la revisión.
MALLA_FIJA = np.arange(0.20, 0.8001, 0.005)
MOTIVO = ("#191: MCC de la prueba a un umbral elegido con validación interna agrupada, "
          "congelado antes de leerla; el corte fijo de 0.5 es el control")


def mcc(y, p, corte):
    return float(matthews_corrcoef(y, (p >= corte).astype(int)))


def rejilla(p):
    """Cortes candidatos: los cuantiles de las probabilidades, no una malla sobre [0, 1].

    Una malla fija gasta casi todos sus puntos donde no hay probabilidades y deja sin cubrir
    la zona densa, que es justo donde el corte decide.
    """
    return np.unique(np.quantile(p, np.linspace(0.02, 0.98, 193)))


def mejor_corte(y, p):
    """El corte que maximiza el MCC, y su MCC. Usa las etiquetas de lo que mira."""
    cortes = rejilla(p)
    valores = [mcc(y, p, c) for c in cortes]
    i = int(np.argmax(valores))
    return float(cortes[i]), float(valores[i])


def corte_de_igual_prevalencia(p, prevalencia=PREVALENCIA_AJUSTE):
    """El corte que declara positiva la misma fracción que tiene el ajuste. No usa etiquetas."""
    return float(np.quantile(p, 1.0 - prevalencia))


def lecturas(y, p, congelado):
    """Los cuatro números, con las mismas predicciones."""
    igual = corte_de_igual_prevalencia(p)
    optimo, mcc_optimo = mejor_corte(y, p)
    return {
        "fijo_0.5": {"corte": 0.5, "mcc": mcc(y, p, 0.5),
                     "fraccion_positiva": float((p >= 0.5).mean())},
        "congelado": {"corte": congelado, "mcc": mcc(y, p, congelado),
                      "fraccion_positiva": float((p >= congelado).mean())},
        "igual_prevalencia": {"corte": igual, "mcc": mcc(y, p, igual),
                              "fraccion_positiva": float((p >= igual).mean())},
        "optimo_cota": {"corte": optimo, "mcc": mcc_optimo,
                        "fraccion_positiva": float((p >= optimo).mean()),
                        "advertencia": "usa las etiquetas de lo que mide: cota, no resultado"},
        "auroc": float(roc_auc_score(y, p)),
        "prevalencia": float(np.mean(y)),
        "n": int(len(y)),
    }


def intervalo_por_grupos(y, p, grupos, a, b, remuestreos=REMUESTREOS, semilla=0):
    """IC95% de `mcc(b) − mcc(a)` remuestreando grupos de andamio, que es la unidad independiente."""
    rng = np.random.default_rng(semilla)
    unicos = np.unique(grupos)
    indices = {g: np.flatnonzero(grupos == g) for g in unicos}
    difs = []
    for _ in range(remuestreos):
        elegidos = rng.choice(unicos, size=len(unicos), replace=True)
        idx = np.concatenate([indices[g] for g in elegidos])
        if len(np.unique(y[idx])) < 2:
            continue
        difs.append(mcc(y[idx], p[idx], b) - mcc(y[idx], p[idx], a))
    difs = np.asarray(difs)
    return {"media": round(float(difs.mean()), 4),
            "ic95": [round(float(np.quantile(difs, 0.025)), 4),
                     round(float(np.quantile(difs, 0.975)), 4)],
            "remuestreos_validos": int(len(difs))}


def guarda_por_mitades(y, p, grupos, rejilla_de_cortes, repeticiones=REPETICIONES, semilla=0):
    """Elige el corte en una mitad de los **grupos** y lo mide en la otra, en las dos direcciones.

    Esta es la guarda que de verdad deja etiquetas fuera. La anterior —elegir el corte con dos
    semillas y medirlo en la tercera— no lo hacía: las tres semillas son el mismo conjunto de
    6,306 filas con las mismas etiquetas y solo cambia el reparto en pliegues, así que no
    distinguía «ajustar el corte a sus propias etiquetas» de «el máximo del MCC es inestable».
    Lo encontró una revisión del PR, no una comprobación.
    """
    rng = np.random.default_rng(semilla)
    unicos = np.unique(grupos)
    difs = []
    for _ in range(repeticiones):
        permutados = rng.permutation(unicos)
        mitad = permutados[: len(permutados) // 2]
        a = np.isin(grupos, mitad)
        for sel, otra in ((a, ~a), (~a, a)):
            if len(np.unique(y[sel])) < 2 or len(np.unique(y[otra])) < 2:
                continue
            corte = max(rejilla_de_cortes, key=lambda c: mcc(y[sel], p[sel], c))
            difs.append((mcc(y[otra], p[otra], corte) - mcc(y[otra], p[otra], 0.5), corte))
    g = np.array([d for d, _ in difs])
    cortes = np.array([c for _, c in difs])
    return {"ganancia_media": round(float(g.mean()), 4),
            "desviacion": round(float(g.std(ddof=1)), 4),
            "positivas": round(float((g > 0).mean()), 3),
            "evaluaciones": int(len(g)),
            "corte_medio": round(float(cortes.mean()), 4),
            "cortes_rango_5_95": [round(float(np.quantile(cortes, 0.05)), 4),
                                  round(float(np.quantile(cortes, 0.95)), 4)],
            "fraccion_de_cortes_bajo_0.5": round(float((cortes < 0.5).mean()), 3)}


def fase_a(y, p_por_semilla, grupos):
    """Elige el corte en validación y mide si se traslada a grupos cuyas etiquetas no lo eligieron."""
    por_semilla, dentro, entre_semillas = {}, [], []
    for i, s in enumerate(SEMILLAS):
        p = p_por_semilla[i]
        corte, mcc_corte = mejor_corte(y, p)
        por_semilla[str(s)] = {
            "corte": round(corte, 4), "mcc_en_el_corte": round(mcc_corte, 4),
            "mcc_en_0.5": round(mcc(y, p, 0.5), 4),
            "fraccion_positiva_en_0.5": round(float((p >= 0.5).mean()), 4),
            "fraccion_positiva_en_el_corte": round(float((p >= corte).mean()), 4)}
        dentro.append(mcc_corte - mcc(y, p, 0.5))
        # **Esto NO es una guarda de generalización, y decirlo importa.** Las tres semillas son
        # el mismo conjunto con las mismas etiquetas y solo cambia el reparto en pliegues, así
        # que elegir el corte con dos y medirlo en la tercera mide la estabilidad del máximo
        # entre repartos, no si el corte se traslada a etiquetas que no lo eligieron.
        otras = [p_por_semilla[j] for j in range(len(SEMILLAS)) if j != i]
        c_otras = float(np.median([mejor_corte(y, q)[0] for q in otras]))
        entre_semillas.append(mcc(y, p, c_otras) - mcc(y, p, 0.5))
    congelado = round(float(np.median([v["corte"] for v in por_semilla.values()])), 3)

    # La guarda que sí deja etiquetas fuera, con las dos mallas, porque el resultado es sensible
    mitades = {}
    for nombre_malla, hacer_rejilla in (("cuantiles", rejilla), ("fija", lambda _: MALLA_FIJA)):
        por = [guarda_por_mitades(y, p_por_semilla[i], grupos, hacer_rejilla(p_por_semilla[i]),
                                  semilla=s) for i, s in enumerate(SEMILLAS)]
        g = [d["ganancia_media"] for d in por]
        mitades[nombre_malla] = {
            "ganancia_media": round(float(np.mean(g)), 4),
            "por_semilla": por,
            "desviacion_media": round(float(np.mean([d["desviacion"] for d in por])), 4),
            "positivas": round(float(np.mean([d["positivas"] for d in por])), 3),
            "fraccion_de_cortes_bajo_0.5": round(
                float(np.mean([d["fraccion_de_cortes_bajo_0.5"] for d in por])), 3)}

    # Sensibilidad a la malla del propio corte congelado, que la revisión midió y hay que decir
    congelado_malla_fija = round(float(np.median(
        [max(MALLA_FIJA, key=lambda c: mcc(y, q, c)) for q in p_por_semilla])), 3)

    return congelado, {
        "por_semilla": por_semilla,
        "corte_congelado": congelado,
        "corte_congelado_con_malla_fija": congelado_malla_fija,
        "ganancia_dentro_de_muestra": {"media": round(float(np.mean(dentro)), 4),
                                       "por_semilla": [round(float(x), 4) for x in dentro]},
        "estabilidad_entre_semillas": {
            "media": round(float(np.mean(entre_semillas)), 4),
            "por_semilla": [round(float(x), 4) for x in entre_semillas],
            "advertencia": ("no es una guarda de generalización: las tres semillas comparten "
                            "las mismas filas y etiquetas")},
        "guarda_por_mitades_de_grupos": mitades,
    }


def main(leer_prueba: bool = False) -> None:
    t = cargar("permeabilidad", estratos="origen")
    y, grupos = np.asarray(t.y), t.grupos
    modelo = seleccion(("svm_rbf",))["svm_rbf"]
    params = {
        "modelo": "svm_rbf", "semillas": list(SEMILLAS), "pliegues": PLIEGUES,
        "filas_ajuste": int(len(y)), "grupos": int(len(np.unique(grupos))),
        "eleccion_del_corte": "máximo MCC sobre las probabilidades fuera de pliegue de cada semilla",
        "corte_congelado": "la mediana de los tres de semilla, a tres decimales",
        "guarda": "semilla dejada fuera: el corte de las otras dos, medido en ella",
        "lecturas": ["fijo_0.5", "congelado", "igual_prevalencia", "optimo_cota"],
        "intervalo": "bootstrap de grupos de andamio, 2,000 remuestreos",
        "sin_umbral_de_paso": "lección de la 1.10: se reporta el intervalo y la cota",
        "negativo_es_resultado": ("la validación tiene 65.0% de BBB+ y la prueba 57.3%: "
                                  "el corte puede no moverse en la dirección que la prueba pide"),
        "controles": {"mcc_cv_en_0.5": MCC_CV_REGISTRADO,
                      "mcc_prueba_en_0.5": MCC_PRUEBA_REGISTRADO,
                      "auroc_prueba": AUROC_PRUEBA_REGISTRADO, "tolerancia": TOLERANCIA},
        "toca_prueba": bool(leer_prueba),
        "motivo_de_la_lectura": MOTIVO if leer_prueba else None,
    }
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    nombre = "umbral-en-validacion" + ("-con-prueba" if leer_prueba else "")

    with Corrida(nombre, decision="C.5", params=params, semillas=list(SEMILLAS),
                 datos=datos) as c:
        _, fdp = evaluar({"svm_rbf": modelo}, t.X, y, grupos, estratos=t.estratos,
                         semillas=SEMILLAS, pliegues=PLIEGUES, verboso=True)
        p_cv = fdp["svm_rbf"]
        congelado, a = fase_a(y, p_cv, grupos)

        control_cv = abs(np.mean([v["mcc_en_0.5"] for v in a["por_semilla"].values()])
                         - MCC_CV_REGISTRADO)
        a["control_mcc_cv_en_0.5"] = {"diferencia": round(float(control_cv), 4),
                                      "pasa": bool(control_cv <= TOLERANCIA)}

        filas = [{"ambito": "validacion", "semilla": s, **{k: v for k, v in d.items()}}
                 for s, d in a["por_semilla"].items()]
        metricas = {"fase_a": a, "corte_congelado": congelado}

        if leer_prueba:
            # **El corte ya está congelado.** Lo que sigue no lo puede cambiar, y es la única
            # razón por la que esta lectura se puede reportar como resultado.
            tp = cargar("permeabilidad", estratos="origen", incluir_prueba=True, motivo=MOTIVO)
            prueba = tomar_prueba(tp.meta, final=True, motivo=MOTIVO)
            idx = prueba.index.to_numpy()
            es_prueba = np.isin(np.arange(len(tp.y)), idx)
            Xp = np.asarray(tp.X)
            yp = np.asarray(tp.y)[es_prueba]
            modelo_final = clone(modelo).fit(Xp[~es_prueba], np.asarray(tp.y)[~es_prueba])
            pp = modelo_final.predict_proba(Xp[es_prueba])[:, 1]

            b = lecturas(yp, pp, congelado)
            control = abs(b["fijo_0.5"]["mcc"] - MCC_PRUEBA_REGISTRADO)
            control_auroc = abs(b["auroc"] - AUROC_PRUEBA_REGISTRADO)
            b["control_mcc_en_0.5"] = {"diferencia": round(float(control), 4),
                                       "pasa": bool(control <= TOLERANCIA)}
            b["control_auroc"] = {"diferencia": round(float(control_auroc), 4),
                                  "pasa": bool(control_auroc <= TOLERANCIA)}
            gp = np.asarray(tp.grupos)[es_prueba]
            b["intervalo_congelado_menos_fijo"] = intervalo_por_grupos(
                yp, pp, gp, 0.5, congelado)
            b["intervalo_igual_prevalencia_menos_fijo"] = intervalo_por_grupos(
                yp, pp, gp, 0.5, b["igual_prevalencia"]["corte"])
            metricas["fase_b"] = b
            filas += [{"ambito": "prueba", "lectura": k, "corte": round(v["corte"], 4),
                       "mcc": round(v["mcc"], 4),
                       "fraccion_positiva": round(v["fraccion_positiva"], 4)}
                      for k, v in b.items() if isinstance(v, dict) and "mcc" in v]
            pd.DataFrame({"fila": idx, "y": yp, "probabilidad": pp,
                          "grupo": gp}).to_csv(c.carpeta / "prueba_predicciones.csv", index=False)

        pd.DataFrame(filas).to_csv(c.carpeta / "cortes.csv", index=False)
        c.metricas(metricas)

        print(f"\ncorte congelado: {congelado}")
        print(f"  corte congelado con la malla fija: {a['corte_congelado_con_malla_fija']}")
        print(f"  ganancia de MCC en validación, dentro de muestra: "
              f"{a['ganancia_dentro_de_muestra']['media']:+.4f}")
        for nm, d in a["guarda_por_mitades_de_grupos"].items():
            print(f"  guarda por mitades de grupos, malla {nm:9}: "
                  f"{d['ganancia_media']:+.4f} (desv {d['desviacion_media']:.4f}, "
                  f"positiva en {d['positivas']:.0%}, cortes bajo 0.5 "
                  f"{d['fraccion_de_cortes_bajo_0.5']:.0%})")
        print(f"  estabilidad entre semillas (no es guarda): "
              f"{a['estabilidad_entre_semillas']['media']:+.4f}")
        print(f"  control MCC a 0.5 contra {MCC_CV_REGISTRADO}: "
              f"{'pasa' if a['control_mcc_cv_en_0.5']['pasa'] else 'FALLA'} "
              f"(dif {a['control_mcc_cv_en_0.5']['diferencia']:+.4f})")
        for s, d in a["por_semilla"].items():
            print(f"  semilla {s}: corte {d['corte']:.4f} · MCC {d['mcc_en_0.5']:.4f} → "
                  f"{d['mcc_en_el_corte']:.4f} · declara BBB+ "
                  f"{d['fraccion_positiva_en_0.5']:.3f} → {d['fraccion_positiva_en_el_corte']:.3f}")
        if leer_prueba:
            b = metricas["fase_b"]
            print(f"\nprueba reservada ({b['n']} filas, {b['prevalencia']:.3f} de BBB+)")
            print(f"  control MCC a 0.5 contra {MCC_PRUEBA_REGISTRADO}: "
                  f"{'pasa' if b['control_mcc_en_0.5']['pasa'] else 'FALLA'} "
                  f"(dif {b['control_mcc_en_0.5']['diferencia']:+.4f}) · "
                  f"AUROC {'pasa' if b['control_auroc']['pasa'] else 'FALLA'}")
            for k in ("fijo_0.5", "congelado", "igual_prevalencia", "optimo_cota"):
                d = b[k]
                print(f"  {k:20} corte {d['corte']:.4f} · MCC {d['mcc']:.4f} · "
                      f"declara BBB+ {d['fraccion_positiva']:.3f}"
                      + ("   (cota, usa etiquetas)" if k == "optimo_cota" else ""))
            i = b["intervalo_congelado_menos_fijo"]
            print(f"  congelado − fijo: {i['media']:+.4f} IC95 {i['ic95']}")

        print(f"\n  carpeta: experimentos/{c.id}")


if __name__ == "__main__":
    main(leer_prueba="--leer-prueba" in sys.argv)
