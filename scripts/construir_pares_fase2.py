#!/usr/bin/env python3
"""Construye la matriz de la fase 2: una fila por par compuesto-diana.

Es el equivalente, para la fase 2, de lo que el notebook 02 hizo con la matriz
de permeabilidad. Deja tres artefactos en `data/processed/`:

| Archivo | Qué trae | Filas |
|:--|:--|--:|
| `fase2_pares.parquet` | identidad del par, metadatos, las cuatro columnas objetivo y la partición | 70,384 |
| `fase2_descriptores.parquet` | los 217 descriptores 2D de RDKit, **por compuesto** | 59,781 |
| `fase2_descriptores_limpios.parquet` | los mismos tras `limpiar_descriptores` | 59,781 |

Los descriptores van **por compuesto y no por par** a propósito: 59,781
compuestos sostienen 70,384 pares, así que guardarlos por par repetiría cada
fila 1.18 veces en promedio y mucho más para los compuestos medidos contra
varias dianas. El modelado une por `smiles`.

    python scripts/construir_pares_fase2.py          # ~5 minutos
    python scripts/construir_pares_fase2.py --rapido  # sin descriptores

**Las cuatro columnas objetivo y por qué son cuatro** están explicadas en
`src/data_prep/pares_fase2.py` y en la propuesta de variable objetivo. En
resumen: la binaria se deriva del intervalo de potencia, así que cambiar el
umbral —o adoptar la regresión de la decisión 2.9— no obliga a reconstruir
nada. La fase 1 aprendió esa lección al revés: congeló las 171 columnas sobre
la matriz de Yeo-Johnson y cambiar la transformación obliga a repetir todo.

**La partición se calcula aquí a propósito.** La patrocinadora puso una sola
condición al entregar el archivo completo: que se reserve una prueba que el
modelo nunca vea. Si esa partición viviera en una celda del notebook, cada
reejecución podría moverla; guardada en el artefacto, es la misma para todos.
La *guarda* que hace fallar una evaluación en prueba sin marcarla es otra cosa
y sigue abierta (issue #54).

Lo que este script **no** decide, porque es del modelado: si se quitan los
pares en `conflicto`, si se usa la etiqueta o la potencia, y qué se hace con los
2,648 pares cuyo intervalo no alcanza para decidir con 10 µM.
"""

import argparse
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ACTIVIDAD = (RAIZ / "data/external/profesora"
             / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")
SALIDA = RAIZ / "data/processed"


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--rapido", action="store_true",
                     help="solo la tabla de pares, sin calcular descriptores")
    args = cli.parse_args()

    import sys
    sys.path.insert(0, str(RAIZ))
    from src.data_prep.pares_fase2 import (grupos_de_pares,
                                           particion_de_pares, tabla_de_pares)
    from src.data_prep.splits import SIN_ANDAMIO, verificar_fuga
    from src.features.molecular import (a_mol, descriptores_rdkit,
                                        limpiar_descriptores)

    if not ACTIVIDAD.exists():
        raise SystemExit(f"No está el archivo de actividad: {ACTIVIDAD}")
    SALIDA.mkdir(parents=True, exist_ok=True)

    print(f"Leyendo {ACTIVIDAD.name}")
    actividad = pd.read_csv(ACTIVIDAD, low_memory=False)
    print(f"  {len(actividad):,} mediciones\n")

    pares = tabla_de_pares(actividad)
    pares["grupo_cv"] = grupos_de_pares(pares)
    pares["particion"] = particion_de_pares(pares)

    print(f"Pares compuesto-diana: {len(pares):,}")
    print(f"  compuestos distintos          {pares['esqueleto'].nunique():>7,}")
    print(f"  dianas                        {pares['target_gene'].nunique():>7,}")
    print(f"  grupos para la partición      {pares['grupo_cv'].nunique():>7,}")
    print(f"  con potencia (medición exacta){pares['pActividad'].notna().sum():>7,}")
    print(f"  solo con cotas                {pares['pActividad'].isna().sum():>7,}")
    print(f"  en conflicto                  {int(pares['conflicto'].sum()):>7,}")

    print("\nLas dos etiquetas derivadas")
    for columna, umbral in (("activo_10um", "10 µM"), ("activo_1um", "1 µM")):
        s = pares[columna]
        print(f"  {umbral:<6} {s.notna().sum():>7,} con etiqueta ·"
              f" {s.mean():.1%} activos · {s.isna().sum():,} sin decidir")

    print("\nEstratos de procedencia, que son disjuntos")
    for estrato, n in pares["estrato"].value_counts().items():
        activos = pares.loc[pares["estrato"].eq(estrato), "activo_10um"].mean()
        print(f"  {estrato:<13} {n:>7,} · activos {activos:.1%}")

    print("\nLa partición, con la prueba reservada que pidió la patrocinadora")
    marca = pares.assign(andamio=pares["andamio"].fillna(SIN_ANDAMIO),
                         y=pares["activo_10um"])
    informe = verificar_fuga(marca[marca["y"].notna()])
    for nombre, n in pares["particion"].value_counts().items():
        activos = pares.loc[pares["particion"].eq(nombre), "activo_10um"].mean()
        print(f"  {nombre:<13} {n:>7,} · activos {activos:.1%}")
    print(f"  sin fuga: {informe['sin_fuga']} ·"
          f" andamios cruzados {informe['andamios_cruzados']} ·"
          f" esqueletos cruzados {informe['esqueletos_cruzados']}")
    print("  la prueba no se mira hasta el Avance 5; la guarda es el issue #54")

    print("\nTasa de activos por diana, que es la cifra que no hay que esconder")
    por_diana = (pares.groupby("target_gene")
                 .agg(pares=("activo_10um", "size"),
                      activos=("activo_10um", "mean"))
                 .sort_values("activos", ascending=False))
    grandes = por_diana[por_diana["pares"] >= 200]
    print(f"  de {grandes['activos'].min():.1%} ({grandes['activos'].idxmin()})"
          f" a {grandes['activos'].max():.1%} ({grandes['activos'].idxmax()})"
          f", en las {len(grandes)} dianas con 200 pares o más")
    print("  el mismo umbral no mide lo mismo en todas: decisión 2.3")

    destino = SALIDA / "fase2_pares.parquet"
    pares.to_parquet(destino, index=False)
    print(f"\n[guardado] {destino.relative_to(RAIZ)}"
          f"  ({destino.stat().st_size / 1e6:.1f} MB)")

    if args.rapido:
        print("\n--rapido: no se calcularon descriptores")
        return

    compuestos = pares["smiles"].drop_duplicates().reset_index(drop=True)
    print(f"\nDescriptores de {len(compuestos):,} compuestos distintos…")
    mols = [a_mol(s) for s in compuestos]
    desc = descriptores_rdkit([m for m in mols if m is not None])
    validos = compuestos[[m is not None for m in mols]].reset_index(drop=True)
    desc.insert(0, "smiles", validos)
    print(f"  {desc.shape[0]:,} × {desc.shape[1] - 1} descriptores")

    destino = SALIDA / "fase2_descriptores.parquet"
    desc.to_parquet(destino, index=False)
    print(f"[guardado] {destino.relative_to(RAIZ)}"
          f"  ({destino.stat().st_size / 1e6:.1f} MB)")

    limpios, descartadas = limpiar_descriptores(desc.drop(columns="smiles"))
    limpios.insert(0, "smiles", desc["smiles"])
    print(f"\nTras limpiar: {limpios.shape[1] - 1} descriptores")
    for motivo, columnas in descartadas.items():
        if columnas:
            print(f"  {motivo}: {len(columnas)}")
    destino = SALIDA / "fase2_descriptores_limpios.parquet"
    limpios.to_parquet(destino, index=False)
    print(f"[guardado] {destino.relative_to(RAIZ)}"
          f"  ({destino.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
