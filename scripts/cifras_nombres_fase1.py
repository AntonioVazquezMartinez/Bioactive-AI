#!/usr/bin/env python3
"""El nombre del compuesto no lo identifica: las cifras del supuesto S1.14.

Evidencia del [diccionario de la matriz](../docs/diccionario-matriz.md) y de la
[1.8](../docs/decisiones.md#d1-8). Existe porque las cuatro cifras se habían
calculado dos veces a mano y salieron distintas las dos: la revisión del #83
obtuvo 347 / 949 / 1,077 / 5,095 donde el documento decía 348 / 952 / 1,076 /
5,092. Ninguna de las dos estaba mal de aritmética; **la diferencia es la
normalización del nombre**, que nadie había escrito:

- Las siete filas llamadas «-» no son un nombre, así que quedan fuera. Dentro,
  «-» cuenta como un nombre con muchas estructuras y mueve los cuatro números.
- El nombre se compara sin espacios al borde y sin distinción de mayúsculas.
  Hay tres nombres que solo difieren en eso.

Con esas dos reglas declaradas, las cifras son reproducibles:

    python scripts/cifras_nombres_fase1.py
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
META = RAIZ / "data/processed/bbb_meta.parquet"


def cifras(meta: pd.DataFrame) -> dict:
    """Las cuatro cifras, con el nombre normalizado y sin las filas «-»."""
    nombre = meta["compound_name"].astype(str).str.strip().str.lower()
    d = pd.DataFrame({"nombre": nombre, "esqueleto": meta["esqueleto"]})
    guion = d["nombre"].eq("-")
    d = d[~guion]

    por_nombre = d.groupby("nombre")["esqueleto"].nunique()
    ambiguos = por_nombre[por_nombre > 1]
    por_esqueleto = d.groupby("esqueleto")["nombre"].nunique()
    return {
        "filas": len(meta),
        "filas_sin_nombre": int(guion.sum()),
        "nombres": int(d["nombre"].nunique()),
        "nombres_ambiguos": len(ambiguos),
        "filas_de_esos_nombres": int(d["nombre"].isin(ambiguos.index).sum()),
        "esqueletos_con_varios_nombres": int((por_esqueleto > 1).sum()),
    }


def main() -> None:
    if not META.exists():
        raise SystemExit(
            f"No está {META.relative_to(RAIZ)}; lo genera el notebook 02.")
    meta = pd.read_parquet(META)
    c = cifras(meta)

    print(f"{c['filas']:,} filas · {c['nombres']:,} nombres distintos"
          f" (fuera las {c['filas_sin_nombre']} filas llamadas «-»)\n")
    print(f"  nombres con más de una estructura   {c['nombres_ambiguos']:>6,}"
          f"  ({c['nombres_ambiguos'] / c['nombres']:.1%} de los nombres)")
    print(f"  filas que abarcan                   "
          f"{c['filas_de_esos_nombres']:>6,}")
    print(f"  esqueletos con más de un nombre     "
          f"{c['esqueletos_con_varios_nombres']:>6,}")

    nombre = meta["compound_name"].astype(str).str.strip().str.lower()
    d = pd.DataFrame({"nombre": nombre, "esqueleto": meta["esqueleto"]})
    d = d[d["nombre"].ne("-")]
    peores = (d.groupby("nombre")["esqueleto"].nunique()
              .sort_values(ascending=False).head(5))
    print("\n  Los nombres con más estructuras distintas")
    for n, k in peores.items():
        print(f"    {n:<28} {k} estructuras")


if __name__ == "__main__":
    main()
