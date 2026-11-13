#!/usr/bin/env python3
"""La lista priorizada de compuestos naturales por diana y por enfermedad (el objetivo de la primera diapositiva).

**Es una lista exploratoria, no una validada.** La ordena el modelo de potencia de la fase 2, que en los productos
naturales **no supera a una línea base sencilla** (concordancia 0.530 contra 0.565 de peso, TPSA y diana, en 117 pares de
la prueba reservada): sirve para decidir qué probar primero, no para afirmar que un compuesto actúa. Cada fila lleva lo
que hace falta para leerla así: la probabilidad de cruzar la barrera (o la etiqueta medida, si existe), la similitud con
lo que el modelo vio y la bandera de extrapolación.

La regla, fijada antes de mirar el resultado final:

1. **Universo:** compuestos de las **filas de ajuste** (la prueba reservada no se lee) que NPASS o CMAUP, bases de
   productos naturales, aportan a la fase 2, sin repetir esqueleto. **No se usa la marca de COCONUT de la fase 1**: una
   primera corrida con ella devolvió una lista dominada por fármacos sintéticos (loxapina, fenobarbital, mezlocilina),
   porque «natural» ahí es solo «coincide con COCONUT» y COCONUT los incluye.
2. **Se excluyen** los SMILES que no se pueden usar; los compuestos con alerta **PAINS** (A, B o C de RDKit), porque
   la guía del proyecto pide filtrarlos antes de reportar un candidato; y los de **puntaje de semejanza a productos
   naturales** (Ertl et al. 2008, `ertl2008natural`, implementación de RDKit) menor de 0.5, porque NPASS y CMAUP traen
   algunos fármacos sintéticos (prazosina, sunitinib, clorpromazina). Se cuenta cuántos salen por cada motivo.
   **El corte era 0 y se subió a 0.5** al ver que la ciglitazona, un fármaco sintético (PubChem, CID 2750), entraba
   con 0.23 al tercer lugar de «Depresión». Se cambió la regla y se repitió la corrida completa, en lugar de excluir
   ese compuesto a mano; la corrida anterior (`2026-11-12-artemio-C.5-lista-priorizada-naturales`) se conserva como
   la versión superada. El corte no es una frontera nítida: el puntaje es una probabilidad aprendida, no una etiqueta.
3. **Por diana:** los 10 con mayor potencia predicha (`pActividad`) entre los compuestos **sin medición contra esa
   diana** en las filas de ajuste (los pares ya medidos no son hipótesis nuevas). **La probabilidad de cruzar la
   barrera no filtra**: un compuesto que no cruza por difusión puede llegar al cerebro por un transportador o con una
   formulación, y un BBB− no descarta (C.5). Va siempre al lado (`p_bbb_mas`) para que quien lea decida, y la
   variante que sí exige barrera probable (≥ 0.5) se guarda aparte (`por_diana_con_barrera_probable.csv`).
4. **Por enfermedad:** lo mismo, con el máximo de la potencia predicha entre las dianas sin medir de esa categoría (la
   columna `diana_categoria` del archivo de la patrocinadora), y la diana que da ese máximo.

Dirección del efecto buscado (`Inhibición` o `Activación`) viene del archivo de etiquetas de dianas de la patrocinadora;
el modelo predice **potencia**, sin saber en qué sentido.

    ./env312/bin/python scripts/lista_priorizada_naturales.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

from src import inferencia
from src.tracking import Corrida

RDLogger.DisableLog("rdApp.*")
TOP = 10
BARRERA = 0.5
CRUDO = RAIZ / "data" / "external" / "profesora" / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv"
ETIQUETAS = RAIZ / "data" / "external" / "profesora" / "etiquetas_dianas_2026-09-25.csv"
NP_MINIMO = 0.5
# Nombres comunes verificados en PubChem el 13 de noviembre de 2026 (por InChIKey), para los compuestos que el dato trae
# sin nombre o con una descripción química; la clave es el primer bloque del InChIKey, igual que `esqueleto`.
NOMBRES_VERIFICADOS = {
    "LXTKNVLLWOLCOV": "Fisovenina",                      # CID 442113, alcaloide de Physostigma venenosum
    "ZKPVWZDNDNCTBB": "3-(3,4-dimetoxifenil)serina",     # CHEMBL4647106
    # Sin nombre común en PubChem (solo identificadores de ChEMBL). Estos dos van con una descripción **por su
    # estructura**, no verificada en una base de datos: la clase, no el compuesto.
    "VBRSHBGIUDRWEJ": "Lignano (NPC483651)",              # CHEMBL4634863
    "JHPIJMUNSMWWAA": "Hidroxi-cantin-6-ona (NPC53144)",  # alcaloide; posición del hidroxilo sin confirmar
}
INCHIKEY = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")


def nombre_util(n) -> bool:
    return isinstance(n, str) and n.strip().lower() not in ("", "n.a.", "na", "nan") and not INCHIKEY.match(n.strip())


def universo() -> pd.DataFrame:
    """Naturales (NPASS y CMAUP) de las filas de ajuste, sin repetir esqueleto, con el mejor nombre que el dato traiga."""
    meta = pd.read_parquet(RAIZ / "data" / "processed" / "bbb_meta.parquet")
    meta = meta[meta["particion"] != "prueba"]
    pares = pd.read_parquet(RAIZ / "data" / "processed" / "fase2_pares.parquet")
    pares = pares[pares["particion"] != "prueba"]
    nat2 = pares[pares["natural_por_fuente"]].drop_duplicates("esqueleto")
    u = pd.DataFrame({"esqueleto": nat2["esqueleto"].to_numpy(), "smiles": nat2["smiles"].to_numpy()})
    medida = meta.drop_duplicates("esqueleto").set_index("esqueleto")
    u["bbb_medido"] = u["esqueleto"].map(medida["y"]).astype(float)
    # nombre: el de la fase 1 si existe; si no, el del archivo crudo; si no, el identificador de la fuente
    crudo = pd.read_csv(CRUDO, usecols=["source", "source_compound_id", "compound_name", "inchikey_source"], dtype=str)
    crudo["esqueleto"] = crudo["inchikey_source"].str.split("-").str[0]
    crudo = crudo[crudo["esqueleto"].isin(u["esqueleto"])]
    buenos = crudo[crudo["compound_name"].map(nombre_util)].drop_duplicates("esqueleto").set_index("esqueleto")["compound_name"]
    ids = crudo.drop_duplicates("esqueleto").set_index("esqueleto")
    ids = (ids["source"].str.upper() + ":" + ids["source_compound_id"].fillna("?"))
    nombre = u["esqueleto"].map(medida["compound_name"])
    nombre = nombre.where(nombre.map(nombre_util), u["esqueleto"].map(buenos))
    u["nombre"] = nombre.where(nombre.map(nombre_util), u["esqueleto"].map(ids)).fillna("(sin nombre)")
    u["nombre"] = u["esqueleto"].map(NOMBRES_VERIFICADOS).fillna(u["nombre"])
    u["nombre_corto"] = u["nombre"].str.slice(0, 60)
    return u


def puntaje_np(smiles: pd.Series) -> pd.Series:
    """Natural-product-likeness de Ertl et al. 2008 (positivo: se parece a los productos naturales; negativo: a los sintéticos)."""
    import os

    from rdkit import RDConfig

    sys.path.append(os.path.join(RDConfig.RDContribDir, "NP_Score"))
    import npscorer

    modelo = npscorer.readNPModel()
    out = []
    for s in smiles:
        m = Chem.MolFromSmiles(s) if isinstance(s, str) else None
        out.append(float(npscorer.scoreMol(m, modelo)) if m is not None else float("nan"))
    return pd.Series(out, index=smiles.index)


def con_alerta_pains(smiles: pd.Series) -> pd.Series:
    p = FilterCatalogParams()
    for c in (FilterCatalogParams.FilterCatalogs.PAINS_A, FilterCatalogParams.FilterCatalogs.PAINS_B,
              FilterCatalogParams.FilterCatalogs.PAINS_C):
        p.AddCatalog(c)
    cat = FilterCatalog(p)
    out = []
    for s in smiles:
        m = Chem.MolFromSmiles(s) if isinstance(s, str) else None
        out.append(bool(m is not None and cat.HasMatch(m)))
    return pd.Series(out, index=smiles.index)


def tabla(df: pd.DataFrame, con_diana: bool) -> str:
    """Tabla en Markdown: lugar, compuesto, (diana), potencia predicha, probabilidad de cruzar y qué tan visto es."""
    enc = "| Lugar | Compuesto | " + ("Diana (efecto buscado) | " if con_diana else "") + "Potencia predicha | Cruzar la barrera | Parecido a lo visto |"
    sep = "|--:|:--|" + (":--|" if con_diana else "") + "--:|--:|:--|"
    filas = [enc, sep]
    for _, r in df.iterrows():
        cerca = "bajo (extrapola)" if r["aviso_extrapolacion"] else "razonable"
        dn = f"{r['diana']} ({str(r['efecto_buscado']).lower()}) | " if con_diana else ""
        barrera = (f"{'BBB+' if r['bbb_medido'] == 1 else 'BBB-'} medido" if pd.notna(r["bbb_medido"]) else f"{r['p_bbb_mas']:.2f}")
        nombre = str(r["nombre_corto"]).replace("[", "\\[") + ("..." if len(str(r["nombre_corto"])) >= 60 else "")
        filas.append(f"| {int(r['lugar'])} | {nombre} | {dn}{r['pActividad_predicha']:.1f} | {barrera} | {cerca} |")
    return "\n".join(filas)


def escribir_documento(pe: pd.DataFrame, pd_potencia: pd.DataFrame, cifras: dict, carpeta: Path) -> None:
    """`docs/lista-priorizada.md`: la lista, con las advertencias antes que las tablas."""
    rel = carpeta.relative_to(RAIZ)
    out = [
        "# Lista priorizada de compuestos naturales", "",
        "> **Es una lista exploratoria, no una validada.** La ordena el modelo de potencia de la fase 2, que **en los productos "
        "naturales no supera a una línea base sencilla** (concordancia 0.530 contra 0.565 de peso, TPSA y diana, en 117 pares de la "
        "prueba reservada, [C.5](decisiones.md#dc-5)). Sirve para decidir **qué probar primero**, no para afirmar que un compuesto "
        "actúa. Ninguna fila es un resultado de laboratorio.", "",
        "## Cómo se hizo", "",
        f"- **Universo:** {cifras['universo']:,} compuestos de las filas de ajuste que NPASS o CMAUP aportan a la fase 2 (la prueba "
        "reservada no se lee). Salen "
        f"{cifras['pains']} con alerta PAINS y {cifras['np']} con puntaje de semejanza a productos naturales menor de 0.5 "
        "(Ertl et al., 2008, `ertl2008natural`), porque esas bases traen algunos fármacos sintéticos; quedan "
        f"{cifras['candidatos']:,}.",
        "- **Por diana:** los 10 de mayor potencia predicha entre los que **no tienen medición contra esa diana** (los pares ya "
        "medidos no son hipótesis nuevas). **Ordena solo la potencia: la barrera hematoencefálica no filtra**, porque un compuesto "
        "que no cruza por difusión puede llegar al cerebro por un transportador o con una formulación, y un BBB− no descarta "
        "([C.5](decisiones.md#dc-5)). La probabilidad de cruzar va en su columna, al lado; la variante que exige barrera probable "
        f"(0.5 o más) se guarda aparte (`por_diana_con_barrera_probable.csv` en `{rel}`).",
        "- **Por enfermedad:** lo mismo, con el máximo entre las dianas de esa categoría (las categorías son las del archivo de la patrocinadora).", "",
        "## Cómo leerla", "",
        "- **Potencia predicha:** pActividad (5 es unos 10 µM, 6 es 1 µM, 7 es 0.1 µM). El modelo predice potencia, **sin saber en qué "
        "sentido** debe actuar el compuesto (inhibir o activar): el efecto buscado viene del archivo de dianas de la patrocinadora.",
        "- **Parecido a lo visto:** «bajo» si el compuesto se parece menos de 0.4 a lo que los modelos vieron al entrenarse; entonces su lugar vale menos.",
        "- **Se repiten:** la química que pesa es casi la misma en todas las dianas (la diana pone el 15% de la atribución, ver el anexo F del "
        f"artículo), así que **los mismos compuestos suben en varias listas**: las {len(pd_potencia)} filas por diana tienen solo "
        f"{cifras['distintos']} compuestos distintos. Lo que dice la lista es qué compuestos de entrada parecen potentes, más que "
        "cuál es el mejor para cada diana.",
        "- **Identificadores:** si el dato no trae un nombre usable, el compuesto va con su identificador de NPASS (`NPASS:NPC...`). "
        "SMILES, esqueleto y todas las columnas están en los CSV de la corrida.", "",
        f"Corrida: `{rel.name}` (`scripts/lista_priorizada_naturales.py`).", "",
        "## Por enfermedad", "",
    ]
    for enf, g in pe.groupby("enfermedad", sort=True):
        out += [f"### {enf}", "", tabla(g, True), ""]
    out += ["## Por diana (los cinco primeros)", ""]
    for diana, g in pd_potencia.groupby("diana", sort=True):
        out += [f"### {diana}: {g['enfermedad'].iloc[0]} ({str(g['efecto_buscado'].iloc[0]).lower()})", "",
                tabla(g.head(5), False), ""]
    (RAIZ / "docs" / "lista-priorizada.md").write_text("\n".join(out), encoding="utf-8")


def main() -> None:
    params = {"top_por_lista": TOP, "barrera_como_filtro": False, "toca_prueba": False, "combina_fases": False,
              "exploratoria": True, "filtro_pains": "A, B y C de RDKit", "np_likeness_minimo": NP_MINIMO, "universo": "NPASS y CMAUP, filas de ajuste"}
    with Corrida("lista-priorizada-naturales-corte-np-05", decision="C.5", params=params, semillas=[0]) as c:
        u = universo()
        modelos = inferencia.cargar()
        pred = inferencia.predecir(u["smiles"].tolist(), modelos).reset_index(drop=True)
        d = pd.concat([u, pred.drop(columns=["smiles"], errors="ignore")], axis=1)
        d["pains"] = con_alerta_pains(d["smiles"])
        d["np_likeness"] = puntaje_np(d["smiles"])
        usables = d[d["motivo"] == ""]
        validos = d[(d["motivo"] == "") & ~d["pains"] & (d["np_likeness"] >= NP_MINIMO)].reset_index(drop=True)

        et = pd.read_csv(ETIQUETAS, encoding="utf-8-sig").set_index("gen")
        pares = pd.read_parquet(RAIZ / "data" / "processed" / "fase2_pares.parquet")
        ajuste = pares[pares["particion"] != "prueba"]
        medidos = set(zip(ajuste["esqueleto"], ajuste["target_gene"], strict=True))
        dianas = list(modelos.dianas)
        categoria = {g: str(et.loc[g, "diana_categoria"]) if g in et.index else "" for g in dianas}
        efecto = {g: str(et.loc[g, "diana_efecto_buscado"]) if g in et.index else "" for g in dianas}
        cols_p = [f"pActividad_{g}" for g in dianas]
        validos["pActividad_promedio_26"] = validos[cols_p].mean(axis=1)
        validos["dianas_medidas"] = validos["esqueleto"].map(ajuste.groupby("esqueleto")["target_gene"].nunique()).fillna(0).astype(int)

        comunes = ["nombre_corto", "esqueleto", "smiles", "bbb_medido", "p_bbb_mas", "similitud_fase1", "similitud_fase2",
                   "aviso_extrapolacion", "np_likeness", "pActividad_promedio_26", "dianas_medidas"]

        def por_diana(con_barrera: bool) -> pd.DataFrame:
            filas = []
            for g in dianas:
                libres = validos[[(e, g) not in medidos for e in validos["esqueleto"]]]
                if con_barrera:
                    libres = libres[libres["p_bbb_mas"] >= BARRERA]
                top = libres.nlargest(TOP, f"pActividad_{g}").copy()
                top["diana"], top["enfermedad"], top["efecto_buscado"] = g, categoria[g], efecto[g]
                top["pActividad_predicha"] = top[f"pActividad_{g}"]
                top["lugar"] = range(1, len(top) + 1)
                top["candidatos_sin_medir"] = len(libres)
                filas.append(top[["diana", "enfermedad", "efecto_buscado", "lugar", "pActividad_predicha", *comunes,
                                  "candidatos_sin_medir"]])
            return pd.concat(filas, ignore_index=True)

        # La lista principal ordena solo por potencia: un compuesto que no cruza por difusión puede llegar al cerebro por
        # un transportador o con una formulación, así que la probabilidad de cruzar va al lado y no filtra. La variante
        # con barrera probable se guarda aparte para quien quiera ese criterio.
        pd_potencia = por_diana(False)
        pd_barrera = por_diana(True)
        pd_potencia.to_csv(c.carpeta / "por_diana.csv", index=False)
        pd_barrera.to_csv(c.carpeta / "por_diana_con_barrera_probable.csv", index=False)

        def por_enfermedad(con_barrera: bool) -> pd.DataFrame:
            filas = []
            base = validos[validos["p_bbb_mas"] >= BARRERA] if con_barrera else validos
            for enf in sorted(set(categoria.values()) - {""}):
                gs = [g for g in dianas if categoria[g] == enf]
                mejores = []
                for _, fila in base.iterrows():
                    cand = [(fila[f"pActividad_{g}"], g) for g in gs if (fila["esqueleto"], g) not in medidos]
                    if cand:
                        p, g = max(cand)
                        mejores.append((fila["esqueleto"], p, g))
                m = pd.DataFrame(mejores, columns=["esqueleto", "pActividad_predicha", "diana"]).nlargest(TOP, "pActividad_predicha")
                m = m.merge(base[comunes], on="esqueleto", how="left")
                m.insert(0, "enfermedad", enf)
                m["efecto_buscado"] = m["diana"].map(efecto)
                m.insert(3, "lugar", range(1, len(m) + 1))
                filas.append(m)
            return pd.concat(filas, ignore_index=True)

        pe = por_enfermedad(False)
        pe.to_csv(c.carpeta / "por_enfermedad.csv", index=False)
        por_enfermedad(True).to_csv(c.carpeta / "por_enfermedad_con_barrera_probable.csv", index=False)

        escribir_documento(pe, pd_potencia, {
            "universo": len(u), "pains": int(usables["pains"].sum()),
            "np": int((~usables["pains"] & (usables["np_likeness"] < NP_MINIMO)).sum()), "candidatos": len(validos),
            "distintos": int(pd_potencia["esqueleto"].nunique())}, c.carpeta)
        c.metricas({
            "universo_naturales": int(len(u)),
            "sin_usar": int((d["motivo"] != "").sum()),
            "con_alerta_pains": int(usables["pains"].sum()),
            "fuera_por_np_likeness_menor_de_0_5": int((~usables["pains"] & (usables["np_likeness"] < NP_MINIMO)).sum()),
            "candidatos": int(len(validos)),
            "candidatos_con_barrera_probable": int((validos["p_bbb_mas"] >= BARRERA).sum()),
            "dianas": len(dianas),
            "enfermedades": sorted(set(categoria.values()) - {""}),
            "compuestos_distintos_en_las_listas_por_diana": int(pd_potencia["esqueleto"].nunique()),
            "filas_en_las_listas_por_diana": int(len(pd_potencia)),
            "con_aviso_de_extrapolacion_en_las_listas": int(pd_potencia["aviso_extrapolacion"].sum()),
        })
        print(f"universo {len(u)} · sin usar {(d['motivo'] != '').sum()} · PAINS {usables['pains'].sum()} "
              f"· NP<0.5 {(~usables['pains'] & (usables['np_likeness'] < NP_MINIMO)).sum()} "
              f"· candidatos {len(validos)} · con barrera probable {(validos['p_bbb_mas'] >= BARRERA).sum()}")
        print(f"compuestos distintos en las {len(pd_potencia)} filas por diana: {pd_potencia['esqueleto'].nunique()}")
        print(pe[["enfermedad", "lugar", "nombre_corto", "diana", "pActividad_predicha", "p_bbb_mas", "aviso_extrapolacion"]]
              .round(2).to_string(index=False))


if __name__ == "__main__":
    main()
