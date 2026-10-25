#!/usr/bin/env python3
"""Cuántos pares y cuántos activos cambian si el tipo de medida respeta la dirección.

Insumo para el [hallazgo 1 del issue
#95](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/95). **No
decide nada**: mide, para que la pregunta a la patrocinadora se haga con una
cifra al lado.

## La pregunta que mide

`src/data_prep/pares_fase2.py` no menciona `activity_type` ni una vez: no filtra
por tipo de medida. Eso no se nota en la mayoría de las dianas, porque el filtro
de gen ya deja fuera los ensayos fenotípicos (GI50, TGI, CC50 no traen gen). Pero
el archivo trae además `diana_efecto_buscado`, que dice **qué modulación de la
diana se busca como tratamiento**, y en cuatro dianas esa dirección es
«Activación». Ahí un EC50 mide activar, que es lo buscado, pero un IC50 **no dice
por sí solo** en qué sentido actúa el compuesto: si el ensayo es de unión
(desplazamiento de un radioligando, competencia por fluorescencia) mide cuánto se
une, como el Ki, también para un agonista; solo si es funcional mide inhibición.
En las tres dianas de activación el 92.5% de los IC50 de ChEMBL son de unión, así
que el tipo de ensayo se pide a ChEMBL (`scripts/descargar_tipos_ensayo.py`) y
decide la dirección de cada IC50. Una primera versión de este script los
clasificaba a todos como inhibición, y esa lectura era falsa; la señaló Artemio
al revisar el correo para la patrocinadora.

El diccionario de la patrocinadora advierte que `diana_efecto_buscado` **no dice
qué hizo el compuesto en el ensayo**, así que la columna no resuelve el caso por
su cuenta: un IC50 sobre PPARG puede ser un antagonista medido a propósito. Qué
tipos cuentan como evidencia de neuroprotección en una diana de activación es
criterio de la patrocinadora (decisión 2.3). Lo que sí se puede medir sin ella es
**cuánto está en juego**, y es lo que hace este script.

## Las dos variantes, que acotan la respuesta por arriba y por abajo

En las dianas cuyo efecto buscado es «Activación», y solo en ellas:

| Variante | Qué quita | Lectura |
|:--|:--|:--|
| `sin_contrarias` | los tipos que miden en la dirección opuesta | el cambio **mínimo**: solo lo que contradice |
| `solo_activacion` | todo lo que no mida activación, afinidad incluida | el cambio **máximo** |

La verdad está entre las dos. `Potency` queda en «ambigua» a propósito: en NPASS
y CMAUP viene de curvas dosis-respuesta cuya dirección no se declara, así que
`sin_contrarias` la conserva y `solo_activacion` la quita, y la diferencia entre
las dos variantes dice cuánto pesa esa duda.

Hay una tercera, `solo_inhibicion`, que **no es un candidato a adoptar**: sirve
para tratar los IC50 **aparte** en lugar de quitarlos, que es la otra mitad de lo
que pide el issue. Comparada con `solo_activacion` dice qué opina cada dirección
por su cuenta sobre el mismo par, y si se contradicen donde las dos opinan. Si
coincidieran casi siempre, mezclarlas sería inofensivo y la pregunta a la
patrocinadora perdería urgencia.

## Y la segunda medición: de qué depende la clase negativa de NPASS

AC50 existe solo en NPASS y casi todo es censurado, así que es de donde sale la
mayoría de sus negativos (lo midió Pame en el #95). Quitarlo por evitar el sesgo
por fuente dejaría a los productos naturales casi sin clase negativa, que sesga en
el otro sentido. Aquí se cuenta cuántos pares **dependen solo de AC50** —
desaparecen si se quita — y a cuántos les cambia la etiqueta.

    python scripts/medicion_dianas_activacion.py          # ~4 minutos

Salida: `notebooks/datos/medicion_dianas_activacion.csv` en formato largo, una
fila por diana y variante, y una corrida en `experimentos/`.

**Por qué se puede medir por subconjuntos.** El par es `esqueleto × gen`, así que
filtrar filas de una diana no toca los pares de las demás: la tabla de pares de un
subconjunto de dianas es idéntica a la tabla completa restringida a esas dianas.
Eso permite correr las variantes sobre miles de filas en lugar de 202,647, y es
lo que hace que el script tarde minutos y no horas.
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd

from src.data_prep.pares_fase2 import tabla_de_pares
from tracking import Corrida

ACTIVIDAD = (RAIZ / "data/external/profesora"
             / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")
ETIQUETAS = RAIZ / "data/external/profesora/etiquetas_dianas_2026-09-25.csv"
SALIDA = RAIZ / "notebooks/datos/medicion_dianas_activacion.csv"

# Qué mide cada tipo de medida, en términos de dirección, y está aquí explícita para
# que se pueda discutir línea por línea en lugar de quedar implícita en su ausencia.
# No es una decisión del proyecto. Los tipos IC dependen del ensayo y se resuelven
# aparte (`resolver_ic`).
#
# - `activacion`: la potencia con la que el compuesto **activa** la diana.
# - `inhibicion`: la potencia con la que la **inhibe**.
# - `afinidad`: cuánto se une, sin decir en qué dirección actúa.
# - `ambigua`: el nombre no declara la dirección del ensayo.
#
# GI50, TGI y CC50 están por completitud y no llegan al par: son fenotípicos y no
# traen gen, así que el filtro de `tabla_de_pares` ya los deja fuera.
DIRECCION_DE_TIPO = {
    "EC50": "activacion", "EC1.5": "activacion", "EC30": "activacion",
    # `AC50` **no** es de activación aunque el nombre lo sugiera: es la
    # concentración al 50% de actividad en un ensayo de cribado, y el cribado
    # puede medir en cualquiera de las dos direcciones. Lo señaló Pame al
    # revisar el #119, corrigiendo también su propia propuesta del #95. En las
    # dianas de activación son 77 filas, todas de `PPARG` y 65 de ellas
    # censuradas, así que solo mueve la variante estricta.
    "AC50": "ambigua",
    # IC50/IC33/IC60: ambigua por defecto; `resolver_ic` la cambia según el tipo de ensayo.
    "IC50": "ambigua", "IC33": "ambigua", "IC60": "ambigua",
    "Inhibition": "inhibicion", "INH": "inhibicion", "DC50": "inhibicion",
    "MIC": "inhibicion", "GI50": "inhibicion", "TGI": "inhibicion",
    "CC50": "inhibicion",
    "Ki": "afinidad", "Kd": "afinidad", "Kb": "afinidad", "Kic": "afinidad",
    "KiL": "afinidad", "KiH": "afinidad", "Kc": "afinidad",
    "Potency": "ambigua", "Activity": "ambigua", "CD": "ambigua",
}

VARIANTES = {
    # nombre: las direcciones que se conservan en las dianas de activación
    "sin_contrarias": ("activacion", "afinidad", "ambigua", "sin_clasificar"),
    "solo_activacion": ("activacion",),
    # La tercera no es un candidato a adoptar: existe para **tratar los IC50
    # aparte**, que es la otra mitad de lo que pide el #95. Con ella y con
    # `solo_activacion` se puede ver qué dice cada dirección por su cuenta sobre
    # el mismo par, y si se contradicen.
    "solo_inhibicion": ("inhibicion",),
}

UMBRAL_UM = 10.0

TIPOS_IC = ("IC50", "IC33", "IC60")
TIPOS_ENSAYO = RAIZ / "notebooks/datos/tipos_ensayo_chembl.csv"
# Tipo de ensayo de ChEMBL → dirección de un IC. `B` es unión (desplazamiento,
# competencia): afinidad. `F` es funcional: el IC mide inhibición. Otro tipo
# (ADME, toxicidad) o ninguno —NPASS y CMAUP no traen identificador de ensayo—
# queda ambigua.
DIRECCION_DE_ENSAYO = {"B": "afinidad", "F": "inhibicion"}


def resolver_ic(actividad: pd.DataFrame, direccion: pd.Series,
                tipos_ensayo: pd.Series) -> pd.Series:
    """Reemplaza la dirección de los IC por la que dice el tipo de su ensayo.

    `tipos_ensayo` va de `assay_chembl_id` a `assay_type`. Si el archivo ya trae
    `assay_type` en la fila se usa como respaldo del identificador.
    """
    tipo = actividad["assay_chembl_id"].map(tipos_ensayo).fillna(actividad["assay_type"])
    resuelta = tipo.map(DIRECCION_DE_ENSAYO).fillna("ambigua")
    return direccion.where(~actividad["activity_type"].isin(TIPOS_IC), resuelta)


def _resumen(pares: pd.DataFrame, mediciones: int) -> dict:
    """Las cifras de un grupo de pares: tamaño y reparto de la etiqueta."""
    etiqueta = pares["activo_10um"]
    return {"mediciones": mediciones, "pares": len(pares),
            "activos": int(etiqueta.sum()),
            "inactivos": int((~etiqueta.fillna(True)).sum()),
            "sin_decidir": int(etiqueta.isna().sum())}


def _por_gen(actividad: pd.DataFrame, pares: pd.DataFrame, genes: tuple[str, ...],
             bloque: str, variante: str) -> list[dict]:
    """Una fila de resumen por gen, para el CSV largo."""
    filas = []
    for gen in genes:
        sub = pares[pares["target_gene"].eq(gen)]
        n = int(actividad["target_gene"].eq(gen).sum())
        filas.append({"bloque": bloque, "gen": gen, "variante": variante,
                      **_resumen(sub, n)})
    return filas


def _medir(corrida: Corrida) -> None:
    print(f"Leyendo {ACTIVIDAD.name}")
    actividad = pd.read_csv(ACTIVIDAD, low_memory=False)
    actividad.columns = [c.lstrip("﻿") for c in actividad.columns]
    print(f"  {len(actividad):,} mediciones")

    direccion = actividad["activity_type"].map(DIRECCION_DE_TIPO).fillna(
        "sin_clasificar")
    tipos_ensayo = pd.read_csv(TIPOS_ENSAYO).set_index("assay_chembl_id")["assay_type"]
    direccion = resolver_ic(actividad, direccion, tipos_ensayo)
    sin_clasificar = actividad.loc[direccion.eq("sin_clasificar"),
                                   "activity_type"]
    if not sin_clasificar.empty:
        print(f"  tipos sin dirección declarada: "
              f"{sin_clasificar.value_counts().to_dict()}")

    # Las dianas de activación salen de la lista de la patrocinadora, no de una
    # constante: si ella cambia la dirección de una diana, la medición la sigue.
    etiquetas = pd.read_csv(ETIQUETAS)
    activacion = tuple(sorted(
        etiquetas.loc[etiquetas["diana_efecto_buscado"].eq("Activación"),
                      "gen"].dropna()))
    print(f"\nDianas con efecto buscado «Activación»: {', '.join(activacion)}")

    ic = actividad["activity_type"].isin(TIPOS_IC) & actividad["target_gene"].isin(activacion)
    print(f"\nIC en las dianas de activación: {int(ic.sum()):,} mediciones, por dirección:"
          f" {direccion[ic].value_counts().to_dict()}")

    print("\nTabla de pares completa (la referencia)…")
    base = tabla_de_pares(actividad)
    print(f"  {len(base):,} pares · {int(base['activo_10um'].sum()):,} activos"
          f" a {UMBRAL_UM:g} µM")

    filas = []
    de_activacion = base[base["target_gene"].isin(activacion)]
    print(f"\nEn las {len(activacion)} dianas de activación:"
          f" {len(de_activacion):,} pares"
          f" ({len(de_activacion) / len(base):.1%} del total)")
    filas += _por_gen(actividad, de_activacion, activacion, "direccion", "base")

    # Una diana puede tener mediciones y ningún par: `tabla_de_pares` se queda
    # con las cinco categorías que la patrocinadora ratificó (decisión 2.1), y
    # hay dianas de la lista cuya categoría quedó fuera de esas cinco.
    for gen in activacion:
        if not de_activacion["target_gene"].eq(gen).any():
            categoria = etiquetas.loc[etiquetas["gen"].eq(gen),
                                      "diana_categoria"].iat[0]
            print(f"  ojo: {gen} aporta 0 pares ·"
                  f" {int(actividad['target_gene'].eq(gen).sum()):,} mediciones"
                  f" · su categoría «{categoria}» no está entre las cinco"
                  " ratificadas")

    # --- bloque 1 · la dirección en las dianas de activación
    en_activacion = actividad["target_gene"].isin(activacion)
    resumenes = {"base": _resumen(
        de_activacion, int(en_activacion.sum()))}
    tablas, evidencia = {}, {}
    for nombre, conservadas in VARIANTES.items():
        recortado = actividad[en_activacion & direccion.isin(conservadas)]
        print(f"\nVariante «{nombre}»: {len(recortado):,} de"
              f" {int(en_activacion.sum()):,} mediciones sobreviven")
        variante = tabla_de_pares(recortado)
        tablas[nombre] = variante
        resumenes[nombre] = _resumen(variante, len(recortado))
        filas += _por_gen(recortado, variante, activacion, "direccion", nombre)
        _comparar(de_activacion, variante, nombre)
        evidencia[nombre] = _sobre_cuanta_evidencia(
            _ausentes(de_activacion, variante))

    acuerdo = _acuerdo(tablas["solo_activacion"], tablas["solo_inhibicion"])

    # --- bloque 2 · de qué depende la clase negativa de NPASS
    es_ac50 = actividad["activity_type"].eq("AC50")
    genes_ac50 = tuple(sorted(actividad.loc[es_ac50, "target_gene"].dropna()
                              .unique()))
    print(f"\nAC50: {int(es_ac50.sum()):,} mediciones en"
          f" {len(genes_ac50)} dianas, todas de"
          f" {actividad.loc[es_ac50, 'source'].unique().tolist()}")
    en_ac50 = actividad["target_gene"].isin(genes_ac50)
    con_ac50 = base[base["target_gene"].isin(genes_ac50)]
    filas += _por_gen(actividad, con_ac50, genes_ac50, "ac50", "base")

    recortado = actividad[en_ac50 & ~es_ac50]
    sin_ac50 = tabla_de_pares(recortado)
    filas += _por_gen(recortado, sin_ac50, genes_ac50, "ac50", "sin_ac50")
    desaparecen, cambian = _comparar(con_ac50, sin_ac50, "sin_ac50")

    # El argumento de fondo del #95: AC50 es de donde sale la clase negativa de
    # los productos naturales, así que quitarlo por evitar el sesgo por fuente
    # sesga en el otro sentido. Esto lo cuenta.
    solo_ac50 = _ausentes(con_ac50, sin_ac50)
    print(f"\nLos {len(solo_ac50):,} pares que dependen solo de AC50")
    print(f"  por estrato: {solo_ac50['estrato'].value_counts().to_dict()}")
    etiqueta = solo_ac50["activo_10um"]
    print(f"  activos {int(etiqueta.sum()):,} ·"
          f" inactivos {int((~etiqueta.fillna(True)).sum()):,} ·"
          f" sin decidir {int(etiqueta.isna().sum()):,}")

    negativo = base["activo_10um"].eq(False)
    npass = base["estrato"].eq("solo_npass")
    neg_npass = int((negativo & npass).sum())
    neg_npass_ac50 = int((solo_ac50["activo_10um"].eq(False)
                          & solo_ac50["estrato"].eq("solo_npass")).sum())
    print(f"  de los {neg_npass:,} negativos de pares solo de NPASS en toda la"
          f" tabla, {neg_npass_ac50:,} dependen solo de AC50"
          f" ({neg_npass_ac50 / max(neg_npass, 1):.0%})")
    print(f"  (negativos en toda la tabla: {int(negativo.sum()):,})")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).to_csv(SALIDA, index=False)
    print(f"\n[guardado] {SALIDA.relative_to(RAIZ)}")

    corrida.metricas({
        "pares_totales": len(base),
        "activos_totales": int(base["activo_10um"].sum()),
        "dianas_de_activacion": len(activacion),
        "activacion": resumenes,
        "ac50_pares_que_dependen_solo_de_ac50": desaparecen,
        "ac50_pares_que_cambian_de_etiqueta": cambian,
        "negativos_totales": int(negativo.sum()),
        "negativos_de_pares_solo_npass": neg_npass,
        "negativos_solo_npass_que_dependen_de_ac50": neg_npass_ac50,
        "ic50_aparte": acuerdo,
        "pares_sin_evidencia": evidencia,
    })


def _codigo(etiqueta: pd.Series) -> pd.Series:
    """La etiqueta como entero, con el «sin decidir» como un valor más.

    Comparar dos series `boolean` con `!=` **no** sirve aquí: `pd.NA != pd.NA`
    da `pd.NA`, no `False`, así que un par que sigue sin decidirse de los dos
    lados contaría como cambio. Con el nulo convertido en −1, «sin decidir» es
    un estado comparable, que es lo que hace falta: pasar de activo a sin
    decidir **es** un cambio y hay que contarlo.
    """
    return etiqueta.map({True: 1, False: 0}).fillna(-1).astype(int)


def _acuerdo(activacion: pd.DataFrame, inhibicion: pd.DataFrame) -> dict:
    """Qué dice cada dirección por su cuenta sobre el mismo par.

    Es la otra mitad de lo que pide el #95: no «quitar los IC50» sino
    **tratarlos aparte**, para ver si las dos direcciones se contradicen donde
    las dos opinan. Si coincidieran casi siempre, mezclarlas sería inofensivo y
    la pregunta a la patrocinadora perdería urgencia.
    """
    clave = ["esqueleto", "target_gene"]
    j = activacion[clave + ["activo_10um"]].merge(
        inhibicion[clave + ["activo_10um"]], on=clave,
        suffixes=("_act", "_inh"))
    a, b = _codigo(j["activo_10um_act"]), _codigo(j["activo_10um_inh"])
    deciden = (a != -1) & (b != -1)
    discrepan = int((deciden & (a != b)).sum())
    print("\nLos IC50 tratados aparte, no quitados")
    print(f"  pares con evidencia de las dos direcciones: {len(j):,}")
    print(f"  de ellos, los dos lados deciden:            "
          f"{int(deciden.sum()):,}")
    print(f"  y discrepan:                               {discrepan:,}"
          f"  ({discrepan / max(int(deciden.sum()), 1):.1%})")
    NOMBRE = {1: "activo", 0: "inactivo", -1: "sin decidir"}
    tabla = pd.crosstab(a.map(NOMBRE), b.map(NOMBRE))
    print("  activación (filas) contra inhibición (columnas):")
    print("    " + tabla.to_string().replace("\n", "\n    "))
    return {"pares_con_las_dos_direcciones": len(j),
            "pares_donde_las_dos_deciden": int(deciden.sum()),
            "pares_donde_discrepan": discrepan}


def _ausentes(antes: pd.DataFrame, despues: pd.DataFrame) -> pd.DataFrame:
    """Las filas de `antes` cuyo par ya no existe en `despues`."""
    clave = ["esqueleto", "target_gene"]
    marca = antes.merge(despues[clave].assign(_sigue=True), on=clave, how="left")
    return antes[marca["_sigue"].isna().to_numpy()]


def _sobre_cuanta_evidencia(perdidos: pd.DataFrame) -> dict:
    """Cuántas mediciones sostenían a los pares que se quedan sin ninguna.

    El conteo de pares solo no basta para pesar la pregunta: varios IC50
    concordantes son más evidencia que uno solo, y lo que se decida vale
    distinto en cada caso. Lo pidió Pame al revisar el #119.
    """
    n = perdidos["n_mediciones"]
    etiqueta = perdidos["activo_10um"]
    una = int(n.eq(1).sum())
    print(f"    de ellos, con una sola medición: {una:,}"
          f"  ({una / max(len(perdidos), 1):.1%})"
          f" · con dos o más: {int(n.ge(2).sum()):,}"
          f" · máximo {int(n.max()) if len(n) else 0}")
    print(f"    y su etiqueta de hoy: activos {int(etiqueta.sum()):,}"
          f" · inactivos {int((~etiqueta.fillna(True)).sum()):,}"
          f" · sin decidir {int(etiqueta.isna().sum()):,}")
    return {"pares": len(perdidos), "con_una_sola_medicion": una,
            "con_dos_o_mas": int(n.ge(2).sum()),
            "hoy_activos": int(etiqueta.sum())}


def _comparar(antes: pd.DataFrame, despues: pd.DataFrame,
              nombre: str) -> tuple[int, int]:
    """Qué pares desaparecen y a cuántos les cambia la etiqueta."""
    clave = ["esqueleto", "target_gene"]
    j = antes[clave + ["activo_10um"]].merge(
        despues[clave + ["activo_10um"]], on=clave, how="left",
        suffixes=("_antes", "_despues"), indicator=True)
    desaparecen = int(j["_merge"].eq("left_only").sum())
    presentes = j[j["_merge"].eq("both")]
    cambian = int((_codigo(presentes["activo_10um_antes"])
                   != _codigo(presentes["activo_10um_despues"])).sum())
    print(f"  pares que desaparecen:        {desaparecen:>6,}"
          f"  ({desaparecen / max(len(antes), 1):.1%} de los {len(antes):,})")
    print(f"  pares con etiqueta distinta:  {cambian:>6,}")
    NOMBRE = {1: "activo", 0: "inactivo", -1: "sin decidir"}
    transicion = (presentes.assign(a=_codigo(presentes["activo_10um_antes"]),
                                   b=_codigo(presentes["activo_10um_despues"]))
                  .query("a != b").groupby(["a", "b"]).size())
    for (a, b), n in transicion.sort_values(ascending=False).items():
        print(f"    {NOMBRE[a]:>11} → {NOMBRE[b]:<11} {n:>6,}")
    activos_antes = int(antes["activo_10um"].sum())
    activos_despues = int(despues["activo_10um"].sum())
    print(f"  activos: {activos_antes:,} → {activos_despues:,}"
          f"  ({activos_despues - activos_antes:+,})")
    return desaparecen, cambian


def main() -> None:
    if not ACTIVIDAD.exists():
        raise SystemExit(f"No está el archivo de actividad: {ACTIVIDAD}")
    with Corrida("dianas-activacion", decision="2.3",
                 params={"umbral_um": UMBRAL_UM,
                         "variantes": {k: list(v) for k, v in VARIANTES.items()},
                         "direccion_de_tipo": DIRECCION_DE_TIPO},
                 semillas=[], datos=[ACTIVIDAD]) as corrida:
        _medir(corrida)


if __name__ == "__main__":
    main()
