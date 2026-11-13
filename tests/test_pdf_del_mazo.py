"""El PDF del mazo es el del mazo: lleva la huella de `presentacion-final.qmd` y de sus imágenes.

Un PDF versionado se desfasa de su fuente en silencio. Aquí no se compara por fechas de git (que en un clon superficial
dan lo mismo para todo) sino por contenido: el exportador escribe la huella en los metadatos y esta prueba la recalcula.
Si falla, se regenera con `./env312/bin/python scripts/exportar_mazo_pdf.py` y se sube en el mismo cambio.
"""
from scripts.exportar_mazo_pdf import SALIDA, huella, huella_del_pdf


def test_el_pdf_del_mazo_existe_y_lleva_su_huella():
    assert SALIDA.exists(), "falta docs/reportes/presentacion/presentacion-final.pdf: genéralo con scripts/exportar_mazo_pdf.py"
    assert huella_del_pdf(SALIDA), "el PDF del mazo no trae la huella en sus metadatos: regenéralo con scripts/exportar_mazo_pdf.py"


def test_el_pdf_del_mazo_no_se_quedo_atras():
    assert huella_del_pdf(SALIDA) == huella(), (
        "presentacion-final.qmd o una de sus imágenes cambió después de exportar el PDF: "
        "regenéralo con scripts/exportar_mazo_pdf.py y súbelo en el mismo cambio")
