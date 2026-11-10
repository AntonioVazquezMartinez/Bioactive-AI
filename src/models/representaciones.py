"""Medir una representación nueva con la misma vara que usa el proyecto.

La pregunta que esto responde: *«traigo una tabla de columnas por compuesto (ómicas, propiedades
calculadas con otro programa, lo que sea); ¿predicen mejor que los descriptores?»*. Se contesta sin
tocar `src/`, con tres piezas:

```python
from src.models import cargar
from src.models.representaciones import con_tabla, columnas_al_azar, comparar
from src.models.baseline import canalizaciones

base = cargar("permeabilidad", representacion="descriptores")
mia = con_tabla(base, mi_tabla, nombre="mi_omica", clave="smiles")      # reemplaza las columnas
suma = con_tabla(base, mi_tabla, nombre="descriptores+mi_omica", modo="agrega")
ruido = columnas_al_azar(base, mia.X.shape[1], nombre="ruido")          # el control
resumen, _ = comparar({"descriptores": base, "mi_omica": mia, "ruido": ruido},
                      canalizaciones(), referencia="descriptores")
```

**Qué garantiza y qué no.** Todas las representaciones se evalúan sobre **las mismas filas, los mismos
grupos y los mismos pliegues**, así que cada pliegue compara una representación con otra y no con el
azar de la partición. Lo que la herramienta no puede saber es si las columnas de la tabla se calcularon
mirando las etiquetas o todas las filas a la vez (un escalado, una selección de columnas o una
reducción de dimensión ajustados sobre el conjunto completo filtran el pliegue de evaluación): eso es de
quien trae la tabla, y la guía lo dice primero. Ver `docs/medir-una-representacion.md`.
"""

from __future__ import annotations

import dataclasses
import warnings
from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import BaseEstimator

from ..evaluation.cv import evaluar
from .tareas import Tarea

METRICAS = ("mcc", "auroc", "auprc_minoritaria")


def _columna_smiles(tabla: pd.DataFrame, clave: str | None) -> str:
    if clave is not None:
        if clave not in tabla.columns:
            raise ValueError(f"la columna {clave!r} no está; hay: {list(tabla.columns)[:8]}…")
        return clave
    candidatas = [c for c in tabla.columns if str(c).lower() == "smiles"]
    if not candidatas:
        raise ValueError("no encuentro una columna «smiles»; indique cuál es con `clave=`")
    return candidatas[0]


def canonico(smiles: pd.Series) -> pd.Series:
    """SMILES canónico de RDKit (con estereoquímica); NaN si no se puede interpretar."""
    from rdkit import Chem, RDLogger

    RDLogger.DisableLog("rdApp.*")

    def _una(s):
        m = Chem.MolFromSmiles(s) if isinstance(s, str) else None
        return Chem.MolToSmiles(m) if m is not None else np.nan

    return smiles.map(_una)


def con_tabla(tarea: Tarea, tabla: pd.DataFrame, *, nombre: str, columnas: Sequence[str] | None = None,
              clave: str | None = None, canonizar: bool = True, modo: str = "reemplaza") -> Tarea:
    """Una `Tarea` con las columnas de `tabla`, alineadas a las filas de `tarea` por SMILES.

    - `modo="reemplaza"`: la entrada son solo las columnas nuevas. `modo="agrega"`: se pegan a las que
      ya tenía la tarea (para medir si **añaden** algo).
    - `canonizar=True` pasa los SMILES de las dos partes por RDKit antes de unirlos; sin eso, dos
      escrituras de la misma molécula no se encuentran.
    - **No imputa nada.** Si falta algún compuesto, o algún valor no es finito, falla diciendo cuántos:
      rellenar en silencio cambia la representación que se está midiendo.
    """
    if modo not in ("reemplaza", "agrega"):
        raise ValueError("`modo` es «reemplaza» o «agrega»")
    clave_t = _columna_smiles(tabla, clave)
    clave_m = _columna_smiles(tarea.meta, None)
    columnas = list(columnas) if columnas is not None else [
        c for c in tabla.columns if c != clave_t and pd.api.types.is_numeric_dtype(tabla[c])]
    if not columnas:
        raise ValueError("no hay columnas numéricas que usar; indíquelas con `columnas=`")

    llave_t = canonico(tabla[clave_t]) if canonizar else tabla[clave_t].astype(str)
    llave_m = canonico(tarea.meta[clave_m]) if canonizar else tarea.meta[clave_m].astype(str)
    propia = tabla[columnas].copy()
    propia["__llave"] = llave_t.to_numpy()
    propia = propia.dropna(subset=["__llave"])
    # Un mismo compuesto puede repetirse (el conjunto trae SMILES que canonizan igual). Si las filas
    # repetidas dicen lo mismo se deja una; si se contradicen no hay forma honesta de elegir.
    propia = propia.drop_duplicates()
    contradicen = propia["__llave"].duplicated(keep=False)
    if contradicen.any():
        raise ValueError(
            f"{propia.loc[contradicen, '__llave'].nunique()} compuestos aparecen en la tabla con valores "
            "distintos (tras canonizar); deje una fila por compuesto, por ejemplo promediando, antes de unirla")
    unido = pd.DataFrame({"__llave": llave_m.to_numpy()}).merge(propia, on="__llave", how="left")
    X_nueva = unido[columnas].to_numpy(dtype=np.float64)
    faltan = np.isnan(X_nueva).any(axis=1)
    if faltan.any():
        raise ValueError(
            f"a {int(faltan.sum())} de {len(faltan)} compuestos de la tarea les faltan valores en la tabla "
            "(o no hay SMILES que coincida); no se imputa en silencio. Complete la tabla o reduzca la "
            "tarea a los compuestos que tiene")
    if not np.isfinite(X_nueva).all():
        raise ValueError("la tabla trae infinitos; límpielos antes de unirla")
    constantes = [c for c, v in zip(columnas, X_nueva.std(axis=0)) if v == 0]
    if constantes:
        warnings.warn(f"{len(constantes)} columnas son constantes y no aportan: {constantes[:5]}…",
                      stacklevel=2)

    X_nueva = X_nueva.astype(np.float32)
    if modo == "agrega":
        X = np.hstack([tarea.X, X_nueva])
        cols = tuple(tarea.columnas) + tuple(columnas)
    else:
        X, cols = X_nueva, tuple(columnas)
    return dataclasses.replace(tarea, X=X, columnas=cols, representacion=nombre)


def columnas_al_azar(tarea: Tarea, n_columnas: int, *, semilla: int = 0, nombre: str = "ruido") -> Tarea:
    """El control: la misma tarea con `n_columnas` columnas de ruido gaussiano.

    Una representación que no se distingue de esto no aporta nada; una que mejora al ruido pero no a los
    descriptores aporta, pero no más que lo que ya había. Sirve también para ver cuánto sube por azar el
    número de columnas.
    """
    ruido = np.random.default_rng(semilla).normal(size=(len(tarea.y), n_columnas)).astype(np.float32)
    return dataclasses.replace(tarea, X=ruido, columnas=tuple(f"ruido_{i}" for i in range(n_columnas)),
                               representacion=nombre)


def intervalo_nadeau_bengio(diferencias: np.ndarray, *, pliegues: int = 5) -> tuple[float, float, float]:
    """Media de las diferencias pareadas y su intervalo del 95% de Nadeau y Bengio.

    Las 15 evaluaciones (3 semillas × 5 pliegues) comparten filas, así que no son 15 réplicas
    independientes: la desviación sola da un intervalo demasiado estrecho. La corrección suma
    `n_prueba / n_ajuste` (1/4 con 5 pliegues) a `1/n` dentro de la raíz.
    """
    d = np.asarray(diferencias, dtype=float)
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 3:
        return float(d.mean()) if n else float("nan"), float("nan"), float("nan")
    rho = 1 / (pliegues - 1)
    mitad = stats.t.ppf(0.975, n - 1) * d.std(ddof=1) * np.sqrt(1 / n + rho)
    return float(d.mean()), float(d.mean() - mitad), float(d.mean() + mitad)


def comparar(tareas: Mapping[str, Tarea], canalizaciones: Mapping[str, BaseEstimator], *, referencia: str,
             metricas: Sequence[str] = METRICAS, semillas: Sequence[int] = (0, 1, 2), pliegues: int = 5,
             ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evalúa cada representación con `evaluar` y compara cada una contra `referencia`, pliegue a pliegue.

    Devuelve `(resumen, resultados)`. `resumen` trae, por (modelo, estrato, representación, métrica), la
    **diferencia media contra la referencia**, su intervalo de Nadeau y Bengio, en cuántas evaluaciones
    mejora y si el intervalo excluye el cero (`distingue`). `resultados` es la tabla larga de `evaluar`.

    Exige que todas las tareas tengan las mismas filas, etiquetas y grupos: es lo que hace que el
    pliegue k de una sea el pliegue k de la otra.
    """
    if referencia not in tareas:
        raise ValueError(f"la referencia {referencia!r} no está en {list(tareas)}")
    ref = tareas[referencia]
    for nombre, t in tareas.items():
        if not (np.array_equal(t.y, ref.y) and np.array_equal(t.grupos, ref.grupos)):
            raise ValueError(f"«{nombre}» no tiene las mismas etiquetas y grupos que «{referencia}»; "
                             "no se pueden parear los pliegues")
    trozos = []
    for nombre, t in tareas.items():
        res, _ = evaluar(canalizaciones, t.X, t.y, t.grupos, estratos=t.estratos,
                         semillas=semillas, pliegues=pliegues, verboso=False)
        trozos.append(res.assign(representacion=nombre))
    resultados = pd.concat(trozos, ignore_index=True)

    llaves = ["modelo", "estrato", "semilla", "pliegue"]
    base = resultados[resultados["representacion"].eq(referencia)].set_index(llaves)
    filas = []
    for nombre in tareas:
        if nombre == referencia:
            continue
        otra = resultados[resultados["representacion"].eq(nombre)].set_index(llaves)
        comunes = base.index.intersection(otra.index)
        for metrica in metricas:
            dif = (otra.loc[comunes, metrica] - base.loc[comunes, metrica]).reset_index(name="dif")
            for (modelo, estrato), g in dif.groupby(["modelo", "estrato"]):
                media, lo, hi = intervalo_nadeau_bengio(g["dif"].to_numpy(), pliegues=pliegues)
                filas.append({"modelo": modelo, "estrato": estrato, "representacion": nombre,
                              "metrica": metrica, "dif_media": media, "ic95_inf": lo, "ic95_sup": hi,
                              "mejora_en": int((g["dif"] > 0).sum()), "evaluaciones": len(g),
                              "distingue": bool(lo > 0 or hi < 0)})
    resumen = pd.DataFrame(filas).round(4)
    return resumen, resultados
