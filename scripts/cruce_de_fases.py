#!/usr/bin/env python3
"""Cuántos esqueletos tienen medición en las dos fases, contado en los dos sitios donde se puede contar.

Evidencia de la decisión C.3 y del supuesto SC.2 de `docs/decisiones.md`.

El registro cita **1,033 esqueletos en ambas fases** y los presenta como el único lugar donde se
puede comprobar si combinar las dos predicciones selecciona mejor que cada una por separado. Esa
cifra es correcta y se calcula en `scripts/cifras_presentacion.py` sobre el **archivo crudo** de
actividad de la patrocinadora, que tiene 99,585 esqueletos.

Pero el archivo que alimenta al modelo de la fase 2 no es ese. Es `fase2_pares.parquet`, que
`src/models/tareas.py` lee en `cargar("actividad")` y que conserva los pares con potencia
utilizable. Ahí quedan menos esqueletos, así que el cruce con la fase 1 es más chico, y **ese** es
el tamaño real de la población donde la C.3 se puede medir con lo que los modelos ven.

Las dos cifras son verdaderas y cuentan cosas distintas. Este script imprime las dos juntas con su
definición, que es la única forma de que no se confundan:

    python scripts/cruce_de_fases.py

**No lee las etiquetas de la prueba reservada.** Cuenta cuántos compuestos comunes caen en cada
partición, que lo decide `grupos_cv` y no dice nada de las etiquetas, y la tasa de BBB+ la promedia
solo sobre las filas de ajuste. Conviene saber por qué eso hay que cuidarlo a mano: la guarda de
`tests/test_guarda_acceso_prueba.py` vigila los dos puntos de acceso declarado del arnés, y este
script no pasa por ninguno porque lee el parquet de `data/processed/` directamente. Ahí la guarda no
mira, así que la disciplina la pone quien escribe.

Necesita `data/processed/`, que no está versionado; se regenera con los cuadernos 02 y 02b. El
cruce sobre el archivo crudo no se recalcula aquí porque pide RDKit sobre 200 mil filas y ya lo
hace `cifras_presentacion.py`; se cita como referencia para poner las dos al lado.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROCESADOS = RAIZ / "data/processed"

# Del cruce sobre el archivo crudo, que calcula `scripts/cifras_presentacion.py`. Se deja aquí como
# constante y no se recalcula: la comparación que importa es contra el conteo de abajo.
CRUDO_FASE2 = 99_585
CRUDO_AMBAS = 1_033


def main() -> None:
    faltan = [r for r in ("bbb_meta.parquet", "fase2_pares.parquet") if not (PROCESADOS / r).exists()]
    if faltan:
        raise SystemExit(
            "faltan en data/processed/: " + ", ".join(faltan)
            + "\nse regeneran con los cuadernos 02 y 02b (ver CLAUDE.md, sección Environment)"
        )

    meta = pd.read_parquet(PROCESADOS / "bbb_meta.parquet")
    pares = pd.read_parquet(PROCESADOS / "fase2_pares.parquet")

    fase1 = set(meta["esqueleto"].dropna())
    fase2 = set(pares["esqueleto"].dropna())
    ambas = fase1 & fase2

    print("Esqueletos de conectividad con medición en las dos fases\n")
    print(f"  fase 1, `bbb_meta.parquet`                        {len(fase1):>7,}")
    print(f"  fase 2, archivo crudo de la patrocinadora         {CRUDO_FASE2:>7,}   (cifras_presentacion.py)")
    print(f"  fase 2, `fase2_pares.parquet` (lo que ve el modelo){len(fase2):>7,}")
    print()
    print(f"  en ambas, contra el archivo crudo                 {CRUDO_AMBAS:>7,}   "
          f"({100 * CRUDO_AMBAS / CRUDO_FASE2:.1f}% de la fase 2, {100 * CRUDO_AMBAS / len(fase1):.1f}% de la fase 1)")
    print(f"  en ambas, contra lo que ve el modelo              {len(ambas):>7,}   "
          f"({100 * len(ambas) / len(fase2):.1f}% de la fase 2, {100 * len(ambas) / len(fase1):.1f}% de la fase 1)")
    print(f"  diferencia                                        {CRUDO_AMBAS - len(ambas):>7,}   "
          f"({100 * (CRUDO_AMBAS - len(ambas)) / CRUDO_AMBAS:.0f}% menos de lo que el registro supone)")

    comunes = meta[meta["esqueleto"].isin(ambas)]
    pares_comunes = pares[pares["esqueleto"].isin(ambas)]
    # `y` solo se lee de las filas de ajuste. La columna existe para las 1,499 de la prueba
    # reservada y promediarla sobre el conjunto entero sería leerla sin declararlo; el reparto por
    # partición sí se imprime porque lo decide `grupos_cv` y no dice nada de las etiquetas.
    de_ajuste = comunes[comunes["particion"] != "prueba"]
    print("\nLa población donde la C.3 se puede medir hoy\n")
    print(f"  esqueletos                                        {len(ambas):>7,}")
    print(f"  compuestos de la fase 1 que les corresponden      {len(comunes):>7,}")
    print(f"    naturales según COCONUT                         {int(comunes['natural'].sum()):>7,}")
    print(f"    BBB+, solo las filas de ajuste                  {de_ajuste['y'].mean():>7.3f}   "
          f"({len(de_ajuste):,} filas; la prueba no se lee)")
    for particion, n in comunes["particion"].value_counts().items():
        print(f"    en la partición de {particion:<14}             {n:>7,}")
    print(f"  pares de actividad que les corresponden           {len(pares_comunes):>7,}")
    print(f"    dianas distintas                                {pares_comunes['target_gene'].nunique():>7,}")

    print("\nY el universo para una lista de candidatos, que es otra pregunta\n")
    naturales = set(meta.loc[meta["natural"] == True, "esqueleto"].dropna())  # noqa: E712
    print(f"  esqueletos naturales con permeabilidad medida     {len(naturales):>7,}")
    print(f"    sin medición de actividad                       {len(naturales - fase2):>7,}   "
          "la fase 2 predice algo nuevo; la fase 1 ya los vio")
    print(f"    con medición de actividad                       {len(naturales & fase2):>7,}")


if __name__ == "__main__":
    main()
