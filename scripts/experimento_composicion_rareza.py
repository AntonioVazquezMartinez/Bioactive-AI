#!/usr/bin/env python3
"""¿Una fila de química rara enseña más que una parecida? (decisión 1.11, fase 1)

La curva de aprendizaje (`2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales`) añade grupos
**al azar** y declara en sus propios límites que no mide si las filas raras aportan más o menos que
las parecidas. La 1.10 midió otra cosa —**repesar** las filas raras que ya están— y salió negativa.
Esta corrida mide la pregunta que quedaba: **la composición**. No mueve nada entre la prueba y el
entrenamiento; la prueba reservada **no se lee** (`cargar` la excluye y este archivo no está ni debe
estar en `PERMITIDOS`).

**Diseño.** Las mismas 15 evaluaciones agrupadas del arnés (`grupos_cv`, 5 pliegues × 3 semillas) y
el mismo `svm_rbf` del catálogo. En cada pliegue se ordenan los **grupos** del ajuste por su rareza y
se entrena con el 25, 50 y 75% de sus filas añadiendo grupos en tres órdenes, midiendo siempre sobre
el mismo pliegue de validación (diferencias pareadas):

| orden | qué entra primero |
|:--|:--|
| `raros` | los grupos de menor similitud: la química nueva primero |
| `parecidos` | los de mayor similitud |
| `azar` | la referencia, el orden de la curva de aprendizaje |

Al 100% los tres órdenes son el mismo conjunto, así que esa fila se corre una sola vez: es el ancla.

**Y el orden de rareza arrastra dos cosas más, que se controlan en vez de declararse solamente.** En un
pliegue de prueba, el 25% «raros primero» traía 68.1% de BBB+ y 1,504 filas, y el 25% «parecidos
primero» 53.9% y 1,370: catorce puntos de prevalencia y 10% de filas de diferencia, suficiente para
explicar cualquier brecha de AUROC sin que la química tenga nada que ver. Por eso cada orden se corre
en dos variantes:

| variante | cómo se arma la submuestra |
|:--|:--|
| `equilibrado` | **la que manda**: en cada paso entra, de los 40 primeros grupos aún no usados de la cola, el que deje la prevalencia de BBB+ más cerca de la del pliegue. El orden de rareza sigue mandando —nunca se salta más de 40 posiciones— y la prevalencia deja de confundirse con la química. Aísla la composición |
| `crudo` | el orden puro, sin restricción: es lo que daría añadir química rara sin mirar la clase, y la diferencia entre las dos variantes mide cuánto del efecto era prevalencia |

**La rareza es la de la 1.10**, para que las dos corridas hablen de lo mismo: la similitud de Tanimoto
(Morgan radio 2, 2048 bits) de una fila con su vecino más cercano **dentro del ajuste del pliegue y
excluyendo las filas de su mismo grupo** (`grupos_cv`); si no se excluyeran, sus estereoisómeros y
compañeros de andamio la harían parecer común. La rareza de un grupo es la media de las de sus filas.

**Lo que se declara antes de correr.**
- La lectura que manda es la diferencia pareada `raros − parecidos` de AUROC en cada fracción, con el
  intervalo del 95% corregido por Nadeau y Bengio, como en la 1.7.
- **No se fija un umbral de paso.** La 1.10 enseñó que un umbral puesto contra la dispersión del nulo
  deja la regla corta de potencia sin que se note (su regla tenía 26.6% de potencia para el efecto que
  nombraba), así que aquí se reporta el intervalo y se dice qué efecto queda descartado. «Una fila rara
  enseña más» se sostiene si la diferencia es positiva y su intervalo excluye el cero en las tres
  fracciones; se sostiene lo contrario con el signo al revés; y si el intervalo contiene el cero se
  reporta la cota, no un empate.
- Lecturas secundarias, sin criterio: el MCC (por el punto fijo de 0.5), la diferencia contra el orden
  `azar` (que es la comparación accionable: ¿conviene pedir química rara en lugar de más datos?) y el
  AUROC sobre el **tercil más raro de la validación**, por si la ganancia se concentra ahí.
- **Lo que sigue sin controlarse, y se declara:** los grupos raros son más pequeños (los andamios raros
  son casi todos solitarios), así que a igual número de filas el orden `raros` mete **más grupos** y más
  andamios distintos. Eso no se iguala, porque igualarlo sería igualar la diversidad, que es justamente
  el mecanismo por el que una fila rara podría enseñar más. Se mide y se reporta por submuestra
  (`submuestras.csv`), igual que la prevalencia alcanzada y la rareza media de cada una.
- Esta corrida no decide nada sobre el modelo entregado ni sobre la partición. Recomponer la prueba
  reservada **no es una consecuencia posible** de este resultado: subiría las cifras de la prueba por
  construcción, porque la prueba rinde 0.793 precisamente por tener los andamios raros.

    ./env/bin/python scripts/experimento_composicion_rareza.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import warnings
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from rdkit import Chem, RDLogger  # noqa: E402
from rdkit.Chem import rdFingerprintGenerator  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.metrics import matthews_corrcoef, roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402

from src.models.alternativos import seleccion  # noqa: E402
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar  # noqa: E402
from src.tracking import Corrida  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning)
RDLogger.DisableLog("rdApp.*")

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
FRACCIONES = (0.25, 0.50, 0.75, 1.00)
ORDENES = ("raros", "parecidos", "azar")
VENTANA = 40               # cuántos grupos de la cola se miran para no mover la prevalencia
VARIANTES = ((True, "equilibrado"), (False, "crudo"))
MIN_MINORITARIA = 20


def matriz_similitud(smiles) -> np.ndarray:
    """Tanimoto de todas contra todas (Morgan radio 2, 2048 bits). Misma definición que la 1.10."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    huellas = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, s in enumerate(smiles):
        huellas[i] = gen.GetFingerprintAsNumPy(Chem.MolFromSmiles(s))
    comunes = huellas @ huellas.T
    tam = huellas.sum(axis=1)
    union = tam[:, None] + tam[None, :] - comunes
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(union > 0, comunes / union, 0.0)
    return s.astype(np.float32)


def rareza_de_filas(similitud, grupos, idx) -> np.ndarray:
    """Similitud al vecino más cercano dentro de `idx`, sin contar las filas de su mismo grupo."""
    s = similitud[np.ix_(idx, idx)].copy()
    g = grupos[idx]
    s[g[:, None] == g[None, :]] = -1.0   # su mismo grupo no cuenta, tampoco ella misma
    return s.max(axis=1)


def orden_de_grupos(rareza_fila, grupos, idx, orden, rng):
    """Los grupos de `idx`, ordenados según `orden` (los primeros son los que entran antes)."""
    g = grupos[idx]
    por_grupo = pd.Series(rareza_fila, index=g).groupby(level=0).mean()
    if orden == "raros":          # menor similitud = más raro, entra primero
        return por_grupo.sort_values(kind="stable").index.to_numpy(), por_grupo
    if orden == "parecidos":
        return por_grupo.sort_values(kind="stable", ascending=False).index.to_numpy(), por_grupo
    return rng.permutation(por_grupo.index.to_numpy()), por_grupo


def submuestra(idx, grupos, y, secuencia, fraccion, equilibrar, ventana=VENTANA):
    """Índices de `idx`: los primeros grupos de `secuencia` hasta cubrir `fraccion` de sus filas.

    Sin `equilibrar`, entra el orden puro: es lo que daría añadir química rara sin mirar la clase.
    Con `equilibrar`, en cada paso se elige, **entre los `ventana` primeros grupos aún no usados de
    la cola**, el que deje la prevalencia de BBB+ más cerca de la del pliegue. Así el orden de rareza
    sigue siendo el criterio (nunca se salta más de `ventana` posiciones) y la prevalencia deja de
    confundirse con la composición. La regla es la misma para los tres órdenes, así que no favorece a
    ninguno. En las dos variantes el número de filas se ajusta al objetivo por el grupo más cercano.
    """
    if fraccion >= 1.0:
        return idx
    g, yi = grupos[idx], y[idx]
    tam = dict(zip(*np.unique(g, return_counts=True)))
    pos = pd.Series(yi, index=g).groupby(level=0).sum().to_dict()
    meta, objetivo = fraccion * len(idx), float(yi.mean())
    cola, elegidos, n, npos = list(secuencia), [], 0, 0
    while n < meta and cola:
        if equilibrar and n > 0:
            w = cola[:ventana]
            u = min(w, key=lambda v: abs((npos + pos[v]) / (n + tam[v]) - objetivo))
        else:
            u = cola[0]
        cola.remove(u)
        elegidos.append(u)
        n, npos = n + tam[u], npos + pos[u]
    if len(elegidos) > 1 and abs(n - tam[elegidos[-1]] - meta) < abs(n - meta):
        cola.insert(0, elegidos.pop())       # el último grupo sobra más de lo que faltaría sin él
        n -= tam[cola[0]]
    for u in sorted(cola[:ventana], key=lambda v: tam[v]):   # afinar el número de filas al objetivo
        if abs(n + tam[u] - meta) >= abs(n - meta):
            continue
        if equilibrar and abs((npos + pos[u]) / (n + tam[u]) - objetivo) > 0.01:
            continue                         # afinar el tamaño no puede desequilibrar la clase
        elegidos.append(u)
        n, npos = n + tam[u], npos + pos[u]
    return idx[np.isin(g, elegidos)]


def intervalo_nb(dif: np.ndarray) -> dict:
    """Media, desviación pareada y el IC95% corregido por Nadeau y Bengio (J evaluaciones, k pliegues)."""
    dif = dif[~np.isnan(dif)]
    j = len(dif)
    media, desv = float(dif.mean()), float(dif.std(ddof=1))
    ee = desv * np.sqrt(1 / j + (1 / PLIEGUES) / (1 - 1 / PLIEGUES))
    t = float(stats.t.ppf(0.975, j - 1))
    return {"media": round(media, 4), "desviacion": round(desv, 4),
            "ic95": [round(media - t * ee, 4), round(media + t * ee, 4)],
            "evaluaciones": j, "positivas": int((dif > 0).sum()),
            "peor": round(float(dif.min()), 4), "mejor": round(float(dif.max()), 4)}


def terciles(valores) -> np.ndarray:
    """0, 1, 2 por tercil de similitud (0 = el más raro)."""
    cortes = np.quantile(valores, [1 / 3, 2 / 3])
    return np.digitize(valores, cortes)


def main() -> None:
    t = cargar("permeabilidad")
    X, y, g = np.asarray(t.X, float), np.asarray(t.y), np.asarray(t.grupos)
    n = len(y)
    modelo = seleccion(("svm_rbf",))["svm_rbf"]
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"ordenes": list(ORDENES), "fracciones": list(FRACCIONES), "semillas": list(SEMILLAS),
              "pliegues": PLIEGUES, "filas": int(n), "grupos": int(len(np.unique(g))),
              "modelo": "svm_rbf", "submuestreo": "grupos", "toca_prueba": False,
              "rareza": "Tanimoto (Morgan r2, 2048) al vecino más cercano del ajuste del pliegue, "
                        "excluyendo su mismo grupo; la de un grupo es la media de sus filas",
              "lectura_que_manda": "diferencia pareada raros - parecidos de AUROC por fracción, IC "
                                   "de Nadeau y Bengio; sin umbral de paso declarado"}

    with Corrida("composicion-rareza-permeabilidad", decision="1.11", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        print(f"{n:,} filas · {len(np.unique(g)):,} grupos · {y.mean():.1%} BBB+\n", flush=True)
        sim = matriz_similitud(t.meta["SMILES"].to_numpy())

        filas, muestras = [], []
        for s_i, semilla in enumerate(SEMILLAS):
            cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
            for pliegue, (aj, val) in enumerate(cv.split(X, y, g), 1):
                t0 = time.perf_counter()
                rar_aj = rareza_de_filas(sim, g, aj)
                # Rareza de la validación: al ajuste de ESTE pliegue, sin excluir grupo (ya no está).
                rar_val = sim[np.ix_(val, aj)].max(axis=1)
                terc_val = terciles(rar_val)
                for orden in ORDENES:
                    rng = np.random.default_rng(1000 * semilla + pliegue)
                    secuencia, rareza_grupo = orden_de_grupos(rar_aj, g, aj, orden, rng)
                    for equilibrar, variante in VARIANTES:
                        for f in FRACCIONES:
                            if f >= 1.0 and (orden != ORDENES[0] or not equilibrar):
                                continue    # al 100% los tres órdenes son el mismo conjunto
                            sub = submuestra(aj, g, y, secuencia, f, equilibrar)
                            m = clone(modelo).fit(X[sub], y[sub])
                            p = m.predict_proba(X[val])[:, 1]
                            fila = {"semilla": semilla, "pliegue": pliegue, "orden": orden,
                                    "variante": "ambas" if f >= 1.0 else variante, "fraccion": f,
                                    "auroc": roc_auc_score(y[val], p),
                                    "mcc": matthews_corrcoef(y[val], (p >= 0.5).astype(int))}
                            for k in range(3):
                                sel = terc_val == k
                                ys = y[val][sel]
                                ok = min(int(ys.sum()), int((1 - ys).sum())) >= MIN_MINORITARIA
                                fila[f"auroc_t{k}"] = roc_auc_score(ys, p[sel]) if ok else np.nan
                            filas.append(fila)
                            muestras.append({
                                "semilla": semilla, "pliegue": pliegue, "orden": orden,
                                "variante": fila["variante"], "fraccion": f,
                                "n_filas": int(len(sub)), "n_grupos": int(len(np.unique(g[sub]))),
                                "bbb_mas": round(float(y[sub].mean()), 4),
                                "bbb_mas_del_pliegue": round(float(y[aj].mean()), 4),
                                "rareza_media": round(float(rareza_grupo.loc[np.unique(g[sub])].mean()), 4),
                                "n_validacion": int(len(val)),
                                "similitud_media_validacion": round(float(rar_val.mean()), 4)})
                print(f"  semilla {semilla} pliegue {pliegue}: {time.perf_counter() - t0:.0f} s",
                      flush=True)

        df, sub_df = pd.DataFrame(filas), pd.DataFrame(muestras)
        # Antes de metricas(): un fallo al cerrar no cuesta el cálculo.
        df.to_csv(c.carpeta / "pliegues.csv", index=False)
        sub_df.to_csv(c.carpeta / "submuestras.csv", index=False)

        # Control del arnés: al 100% los tres órdenes son el mismo ajuste.
        cien = df[df["fraccion"] == 1.0]
        assert len(cien) == len(SEMILLAS) * PLIEGUES, "el 100% debe correrse una sola vez"

        def pareado(metrica, a, b, f, variante):
            d = df[(df["fraccion"] == f) & (df["variante"] == variante)]
            piv = d.pivot_table(index=["semilla", "pliegue"], columns="orden", values=metrica)
            return (piv[a] - piv[b]).to_numpy()

        lecturas = {"niveles": {}, "control_100_por_ciento": {
            m: round(float(cien[m].mean()), 4) for m in ("auroc", "mcc")}}
        for equilibrar, variante in VARIANTES:
            bloque = {"raros_menos_parecidos": {}, "raros_menos_azar": {},
                      "parecidos_menos_azar": {}, "por_tercil_de_validacion": {}}
            for f in FRACCIONES[:-1]:
                clave = f"{int(f * 100)}%"
                for par, (a, b) in {"raros_menos_parecidos": ("raros", "parecidos"),
                                    "raros_menos_azar": ("raros", "azar"),
                                    "parecidos_menos_azar": ("parecidos", "azar")}.items():
                    bloque[par][clave] = {m: intervalo_nb(pareado(m, a, b, f, variante))
                                          for m in ("auroc", "mcc")}
                bloque["por_tercil_de_validacion"][clave] = {
                    f"t{k}": intervalo_nb(pareado(f"auroc_t{k}", "raros", "parecidos", f, variante))
                    for k in range(3)}
            lecturas[variante] = bloque
        for f in FRACCIONES:
            clave = f"{int(f * 100)}%"
            d = df[df["fraccion"] == f]
            lecturas["niveles"][clave] = {
                f"{o}|{v}": {m: round(float(x[m].mean()), 4) for m in ("auroc", "mcc")}
                for (o, v), x in d.groupby(["orden", "variante"])}

        resumen_sub = (sub_df.groupby(["orden", "variante", "fraccion"])
                       [["n_filas", "n_grupos", "bbb_mas", "rareza_media"]].mean().round(4))
        print("\n", resumen_sub.to_string(), "\n", flush=True)
        for variante in ("equilibrado", "crudo"):
            for f in ("25%", "50%", "75%"):
                r = lecturas[variante]["raros_menos_parecidos"][f]["auroc"]
                print(f"{variante:12s} raros − parecidos, AUROC al {f:3s}: {r['media']:+.4f} "
                      f"IC95 {r['ic95']} · positivas {r['positivas']}/15", flush=True)

        eq = sub_df[(sub_df["variante"] == "equilibrado") & (sub_df["fraccion"] < 1.0)]
        desvios = {
            "peor_desvio_relativo_de_n": round(float(
                (eq["n_filas"] / (eq["fraccion"] * eq["n_filas"].groupby(
                    [eq["semilla"], eq["pliegue"]]).transform("max") / 0.75) - 1).abs().max()), 4),
            "peor_desvio_de_prevalencia": round(float(
                (eq["bbb_mas"] - eq["bbb_mas_del_pliegue"]).abs().max()), 4)}
        print("desvíos de la variante equilibrada:", desvios, flush=True)

        c.metricas({"lecturas": lecturas, "desvios_del_equilibrado": desvios,
                    "submuestras": {f"{o}|{v}|{f}": resumen_sub.loc[(o, v, f)].to_dict()
                                    for (o, v, f) in resumen_sub.index},
                    "nota_control": "al 100% los tres órdenes son el mismo ajuste; se corre una vez"})


if __name__ == "__main__":
    main()
