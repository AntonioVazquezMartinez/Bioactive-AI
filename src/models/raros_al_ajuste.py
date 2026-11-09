"""Pasar compuestos raros de la prueba reservada al ajuste y devolver comunes a la prueba (decisión 1.11, fase 1).

Es un **experimento**: no cambia la partición del proyecto ni el modelo entregado. La pregunta es si el
entrenamiento mejora en lo raro cuando recibe química rara que hoy solo existe en la prueba.

**Unidad: el grupo** (`grupos_cv`, calculado sobre las 7,805 filas). Se mueven grupos enteros, nunca filas
sueltas: un estereoisómero a cada lado de la frontera es justo la fuga que `grupos_cv` evita.

**Rareza de un grupo:** media de la similitud de Tanimoto de sus filas con su vecino más cercano *de otro
grupo* dentro de las 7,805 filas; terciles dentro de cada tramo de peso (el tramo de la primera fila del
grupo). Tercil 0 = el más raro. Es una propiedad del compuesto respecto al conjunto completo, igual para
todos los brazos, y no cambia con lo que cada brazo tenga en el ajuste.

**Un sorteo** (`repartir`), con la semilla como única fuente de azar:

1. De los grupos de la prueba original que no comparten grupo con el ajuste, la mitad de cada tercil forma
   el **núcleo de evaluación** `E`, igual en todos los brazos; la otra mitad es la **reserva móvil** `M`.
2. `M_raro` son las filas de los grupos de `M` en el tercil 0; `n` es cuántas son.
3. `M_azar` son filas de grupos de `M` tomados al azar, de cualquier tercil, hasta llegar a `n` filas.
4. `Q` son filas de grupos **comunes** (tercil 2) del ajuste, al azar, hasta llegar a `n` filas: salen del
   entrenamiento y pasan a la prueba, que es lo que quedó mezclado.

Los brazos entrenan con: `A` el ajuste original; `D` el ajuste sin `Q`; `C` el ajuste sin `Q` más
`M_azar`; `B` el ajuste sin `Q` más `M_raro`. `B`, `C` y `D` tienen casi el mismo tamaño, así que `B − C`
no confunde «más raro» con «más datos».
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .rareza_entrenamiento import terciles_en_tramos

PRUEBA = "prueba"


def similitud_fuera_del_grupo(similitud: np.ndarray, grupos: np.ndarray, bloque: int = 1000) -> np.ndarray:
    """Similitud de cada fila con su vecino más cercano de otro grupo, entre todas las filas."""
    grupos = np.asarray(grupos)
    salida = np.empty(len(grupos), dtype=np.float32)
    for i in range(0, len(grupos), bloque):
        b = similitud[i:i + bloque].copy()
        b[grupos[i:i + bloque, None] == grupos[None, :]] = -1.0
        salida[i:i + bloque] = b.max(axis=1)
    return salida


def terciles_de_grupos(similitud_fila: np.ndarray, grupos: np.ndarray, tramo: np.ndarray) -> np.ndarray:
    """Tercil de rareza (0 = más raro) de cada fila, tomado por grupo y dentro de cada tramo de peso."""
    d = pd.DataFrame({"g": np.asarray(grupos), "s": np.asarray(similitud_fila, float),
                      "t": np.asarray(tramo)})
    por_grupo = d.groupby("g").agg(s=("s", "mean"), t=("t", "first"))
    terc = pd.Series(terciles_en_tramos(por_grupo["s"].to_numpy(), por_grupo["t"].to_numpy()),
                     index=por_grupo.index)
    return terc.reindex(d["g"]).to_numpy()


@dataclass
class Reparto:
    ajuste: np.ndarray          # filas del ajuste original (todo lo que no es prueba)
    evaluacion: np.ndarray      # E: núcleo de evaluación, igual en todos los brazos
    movibles: np.ndarray        # M: grupos de la prueba que se pueden mover
    movidas_raras: np.ndarray   # M_raro
    movidas_azar: np.ndarray    # M_azar
    quitadas: np.ndarray        # Q: comunes del ajuste que pasan a la prueba
    cruzados: int               # grupos de la prueba que también tienen filas en el ajuste (se excluyen)

    def entrenamiento(self, brazo: str) -> np.ndarray:
        sin_q = np.setdiff1d(self.ajuste, self.quitadas)
        if brazo == "A":
            return self.ajuste
        if brazo == "D":
            return sin_q
        if brazo == "C":
            return np.union1d(sin_q, self.movidas_azar)
        if brazo == "B":
            return np.union1d(sin_q, self.movidas_raras)
        raise ValueError(f"brazo {brazo!r}; use A, B, C o D")


def _filas_hasta(grupos_orden, grupos_fila: np.ndarray, n: int, permitidas: np.ndarray) -> np.ndarray:
    """Filas de los grupos, en el orden dado y solo entre las `permitidas`, hasta juntar al menos `n`."""
    filas, total = [], 0
    for g in grupos_orden:
        if total >= n:
            break
        r = np.flatnonzero((grupos_fila == g) & permitidas)
        filas.append(r)
        total += len(r)
    return np.sort(np.concatenate(filas)) if filas else np.array([], int)


def repartir(particion: np.ndarray, grupos: np.ndarray, tercil: np.ndarray, semilla: int) -> Reparto:
    particion, grupos, tercil = np.asarray(particion), np.asarray(grupos), np.asarray(tercil)
    en_prueba = particion == PRUEBA
    ajuste = np.flatnonzero(~en_prueba)
    cruzan = np.isin(grupos, grupos[~en_prueba])
    limpio = en_prueba & ~cruzan
    rng = np.random.default_rng(semilla)

    e_grupos, m_grupos = [], []
    for k in (0, 1, 2):
        gk = np.unique(grupos[limpio & (tercil == k)])
        gk = gk[rng.permutation(len(gk))]
        mitad = (len(gk) + 1) // 2
        e_grupos += list(gk[:mitad])
        m_grupos += list(gk[mitad:])
    evaluacion = np.flatnonzero(np.isin(grupos, e_grupos))
    movibles = np.flatnonzero(np.isin(grupos, m_grupos))
    raras = movibles[tercil[movibles] == 0]
    n = len(raras)

    orden_m = np.array(m_grupos)[rng.permutation(len(m_grupos))]
    azar = _filas_hasta(orden_m, grupos, n, en_prueba)
    comunes = np.unique(grupos[~en_prueba & (tercil == 2)])
    if int((np.isin(grupos, comunes) & ~en_prueba).sum()) < n:
        raise ValueError("el ajuste no tiene tantas filas comunes como raras hay que mover")
    q = _filas_hasta(comunes[rng.permutation(len(comunes))], grupos, n, ~en_prueba)
    return Reparto(ajuste, evaluacion, movibles, raras, azar, q,
                   int(len(np.unique(grupos[en_prueba & cruzan]))))
