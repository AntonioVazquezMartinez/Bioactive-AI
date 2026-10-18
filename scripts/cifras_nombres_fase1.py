#!/usr/bin/env python3
"""El nombre del compuesto no lo identifica: las cifras del supuesto S1.14.

Evidencia del [diccionario de la matriz](../docs/diccionario-matriz.md) y de la
[1.8](../docs/decisiones.md#d1-8). Existe porque las cuatro cifras se habían
calculado dos veces a mano y salieron distintas las dos: la revisión del #83
obtuvo 347 / 949 / 1,077 / 5,095 donde el documento decía 348 / 952 / 1,076 /
5,092. Ninguna de las dos estaba mal de aritmética; **la diferencia es la
normalización del nombre**, que nadie había escrito:

- **Las filas sin nombre quedan fuera**, y son muchas: 1,109 nulas (el 14.2%
  de las 7,805) más siete llamadas «-». Con «-» dentro cuenta como un nombre
  con siete estructuras y mueve los cuatro números.
- **El nombre se compara sin espacios al borde.** Son tres los nombres que se
  juntan por eso (5,094 → 5,091). Pasarlo además a minúsculas no mueve nada en
  este archivo, y se hace igual para que la regla no dependa de eso.

Las dos perillas explican las tres respuestas que hubo, y están medidas:

| Normalización | «-» | nombres | >1 estructura | filas | esqueletos |
|:--|:--|--:|--:|--:|--:|
| cruda | dentro | 5,095 | 347 | 949 | 1,077 |
| cruda | fuera | 5,094 | 346 | 942 | 1,076 |
| sin espacios | dentro | 5,092 | 348 | 952 | 1,076 |
| sin espacios | fuera | 5,091 | 347 | 945 | 1,075 |

La última es la que este script usa y la que el proyecto cita. La tercera es la
que se había publicado y la primera la que obtuvo la revisión del #83: ninguna
estaba mal de aritmética.

**Los nulos se quitan con `dropna()` y no con `astype(str)`**, que es una
dependencia de versión escondida: con el dtype `str` de pandas 3 un nulo sigue
nulo, y con pandas 2 —que `requirements.txt` permite— `astype(str)` lo
convierte en el nombre literal `'nan'`, que entonces aparece como un nombre con
cientos de estructuras y da 348 ambiguos, 2,054 filas y 1,343 esqueletos. El
lock fija pandas 3.0.6, así que hoy no falla; lo señaló Pame en el #83.

Con esas dos reglas declaradas, las cifras son reproducibles:

    python scripts/cifras_nombres_fase1.py
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
META = RAIZ / "data/processed/bbb_meta.parquet"


def _normalizar(nombre: pd.Series) -> pd.Series:
    """Sin espacios al borde y en minúsculas, conservando los nulos como nulos.

    No se usa `astype(str)`: con pandas 2 convierte cada nulo en la cadena
    `'nan'`, que pasa a ser un nombre con cientos de estructuras.
    """
    return nombre.where(nombre.notna()).str.strip().str.lower()


def cifras(meta: pd.DataFrame) -> dict:
    """Las cuatro cifras, sin las filas sin nombre ni las llamadas «-»."""
    nombre = _normalizar(meta["compound_name"])
    d = pd.DataFrame({"nombre": nombre, "esqueleto": meta["esqueleto"]}).dropna(
        subset="nombre")
    guion = d["nombre"].eq("-")
    d = d[~guion]

    por_nombre = d.groupby("nombre")["esqueleto"].nunique()
    ambiguos = por_nombre[por_nombre > 1]
    por_esqueleto = d.groupby("esqueleto")["nombre"].nunique()
    return {
        "filas": len(meta),
        "filas_nulas": int(meta["compound_name"].isna().sum()),
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

    print(f"{c['filas']:,} filas, y {c['filas_nulas']:,} de ellas"
          f" ({c['filas_nulas'] / c['filas']:.1%}) no traen nombre")
    print(f"{c['nombres']:,} nombres distintos, fuera esas y las"
          f" {c['filas_sin_nombre']} llamadas «-»\n")
    print(f"  nombres con más de una estructura   {c['nombres_ambiguos']:>6,}"
          f"  ({c['nombres_ambiguos'] / c['nombres']:.1%} de los nombres)")
    print(f"  filas que abarcan                   "
          f"{c['filas_de_esos_nombres']:>6,}")
    print(f"  esqueletos con más de un nombre     "
          f"{c['esqueletos_con_varios_nombres']:>6,}")

    nombre = _normalizar(meta["compound_name"])
    d = pd.DataFrame({"nombre": nombre, "esqueleto": meta["esqueleto"]}).dropna(
        subset="nombre")
    d = d[d["nombre"].ne("-")]
    peores = (d.groupby("nombre")["esqueleto"].nunique()
              .sort_values(ascending=False).head(5))
    print("\n  Los nombres con más estructuras distintas")
    for n, k in peores.items():
        print(f"    {n:<28} {k} estructuras")


if __name__ == "__main__":
    main()
