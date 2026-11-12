"""Un PDF versionado no puede ser más viejo que el `.tex` del que sale.

Los PDF de la entrega final se versionan, y la razón está en
`docs/reportes/articulo-cientifico/README.md`: quien revisa la maquetación casi nunca tiene
la imagen de Docker de unos 4 GB con pdfLaTeX y Biber, y sin el PDF en el repositorio la
revisión se concentra en la única persona que la tiene levantada. El costo de esa decisión es
que **el PDF se desfasa de su fuente en silencio**, y desde que el sitio los publica el archivo
viejo no es solo un archivo: es una página publicada vieja.

Ya pasó, y es el caso que esta prueba habría atrapado. El PDF del artículo científico se
compiló en `85644f8`, del `.tex` anterior al arreglo de `tab:modelos`; `74a0543` arregló el
`.tex` y el PDF se quedó mostrando la tabla desbordada hasta que `bdc8d01` lo recompiló. En
medio, el PDF del repositorio contradecía a su propia fuente y nada fallaba. Lo encontró una
revisión página por página.

Comparar el PDF con su `.tex` de verdad pide compilar, que es justamente lo que no hay en CI.
Lo que sí se puede comprobar sin compilador es el orden: **el commit del PDF no puede ser
anterior al del `.tex`**. Si los dos se empujan juntos, como pide la regla del README, caen en
el mismo commit y las dos fechas coinciden. Esto no garantiza que el PDF se haya recompilado
—quien quiera burlarlo solo tiene que tocar el PDF— pero sí atrapa el descuido, que es el modo
en que esto se rompe.

Mide con `git log`, no con la fecha del archivo: en un checkout de CI todos los archivos se
escriben en el mismo instante.

Y por eso hace falta `fetch-depth: 0`, que no es el valor que trae `actions/checkout`. En un
clon superficial de un solo commit `git log` no devuelve vacío —que se notaría— sino **ese**
commit para todos los archivos: las dos fechas salen iguales y la comparación pasa sin medir
nada. `test_el_historial_alcanza_para_comparar` existe para eso, y se comprobó contra un clon
`--depth 1` de verdad.
"""

import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
REPORTES = RAIZ / "docs" / "reportes"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True,
                          text=True, check=True).stdout.strip()


def _ultimo_commit(ruta: Path) -> int | None:
    """Fecha del último commit que tocó el archivo, o None si no está versionado."""
    salida = _git("log", "-1", "--format=%ct", "--", str(ruta.relative_to(RAIZ)))
    return int(salida) if salida else None


def _commit(ruta: Path) -> str:
    """`abc1234 del 2026-11-12`, para que el mensaje diga qué commit mirar."""
    return _git("log", "-1", "--format=%h del %cs", "--", str(ruta.relative_to(RAIZ)))


def _atraso(segundos: int) -> str:
    """En la unidad que se lee: el desfase real que ya pasó fue de minutos, no de días."""
    for corte, divisor, unidad in ((7200, 60, "minutos"), (172800, 3600, "horas")):
        if segundos < corte:
            return f"{segundos / divisor:.0f} {unidad}"
    return f"{segundos / 86400:.1f} días"


def _parejas() -> list[tuple[Path, Path]]:
    """Cada `.tex` de `docs/reportes/` que tenga un PDF con su mismo nombre.

    Emparejar por nombre deja fuera lo que debe quedar fuera: la plantilla del curso, que es
    `.tex` y no se compila sola, y los reportes de los avances, que son Quarto y no tienen
    `.tex`.
    """
    parejas = []
    for carpeta in sorted(p for p in REPORTES.iterdir() if p.is_dir()):
        for tex in sorted(carpeta.glob("*.tex")):
            pdf = tex.with_suffix(".pdf")
            if pdf.exists():
                parejas.append((tex, pdf))
    return parejas


PAREJAS = _parejas()
COMPARABLES = [(tex, pdf, ct_tex, ct_pdf)
               for tex, pdf in PAREJAS
               if (ct_tex := _ultimo_commit(tex)) is not None
               and (ct_pdf := _ultimo_commit(pdf)) is not None]


def test_el_historial_alcanza_para_comparar():
    """Sin historial la guarda pasa en vacío, que es peor que no tenerla."""
    assert PAREJAS, (
        f"no hay ninguna pareja `.tex`/`.pdf` en {REPORTES.relative_to(RAIZ)}: la guarda dejó "
        "de vigilar algo, así que ajústala o quítala")
    assert _git("rev-parse", "--is-shallow-repository") != "true", (
        "el clon es superficial: `git log` atribuye todos los archivos a su único commit, así "
        "que las dos fechas salen iguales y cada comparación pasa en vacío. Añade "
        "`fetch-depth: 0` al `actions/checkout` del trabajo «Ruff y pytest» en "
        ".github/workflows/checks.yml")
    assert COMPARABLES, (
        "ninguna pareja tiene commit en las dos partes; si los archivos están versionados, "
        "`git log` no está devolviendo nada y la guarda quedó muerta")


@pytest.mark.parametrize("tex,pdf,ct_tex,ct_pdf", COMPARABLES,
                         ids=[str(t.relative_to(REPORTES)) for t, _, _, _ in COMPARABLES])
def test_el_pdf_no_es_mas_viejo_que_su_tex(tex: Path, pdf: Path, ct_tex: int, ct_pdf: int):
    assert ct_pdf >= ct_tex, (
        f"{pdf.relative_to(RAIZ)} quedó atrás de su fuente: el PDF es de "
        f"{_commit(pdf)} y el `.tex` de {_commit(tex)}, {_atraso(ct_tex - ct_pdf)} después. "
        f"El PDF del repositorio —y el que publica el sitio— no muestra los últimos cambios "
        f"del `.tex`: recompílalo con `sh scripts/compilar_articulo.sh {tex.parent.name}` y "
        f"empújalo junto al `.tex`.")
