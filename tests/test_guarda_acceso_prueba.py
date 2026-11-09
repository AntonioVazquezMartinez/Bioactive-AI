"""Ningún script nuevo puede leer la prueba reservada sin que alguien lo decida a propósito.

`tomar_prueba` deja registro en `experimentos/prueba.csv`, pero `cargar(..., incluir_prueba=True)`
(`src/models/tareas.py`) no pide motivo ni deja rastro: es la única puerta ancha (#200). Hasta que
esa puerta pase por la misma guarda, esta prueba cierra el hueco por el otro lado:

1. Los únicos scripts que pueden pedir `incluir_prueba=True` o llamar `tomar_prueba` son los de la
   lista `PERMITIDOS`. Agregar uno es una decisión que se ve en la revisión.
2. Un script que pide `incluir_prueba=True` tiene que llamar también `tomar_prueba`, que es lo que
   deja la fila en la bitácora.

La lista incluye scripts que todavía no están en `main` (los de las ramas de la escalera y de la
prueba por rareza): una entrada sin archivo no falla.
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "scripts"

PERMITIDOS = {
    "cifras_graficos_05b.py",            # la lectura de la prueba para los gráficos del 05b
    "experimento_escalera_ampliada.py",  # acceso solo de SMILES, sin etiquetas (E1+)
    "experimento_prueba_rareza.py",      # la prueba por rareza (E2)
    "experimento_dificultad_de_la_prueba.py",  # distribución de la similitud de la prueba, solo SMILES (E14)
    "experimento_octava_lectura_origen.py",    # AUROC de la prueba por tercil de similitud y origen, con etiquetas (#268)
    "experimento_andamios_de_la_prueba.py",    # proporción de andamios y esqueletos nuevos en la prueba, sin etiquetas (#264)
    "experimento_raros_al_ajuste.py",          # pasa raros de la prueba al ajuste y devuelve comunes a la prueba, con etiquetas (1.11)
    "prevalencia_raros_al_ajuste.py",          # prevalencia de BBB+ en el entrenamiento de cada brazo de la 1.11, sin entrenar (1.11)
    "experimento_umbral_en_validacion.py",     # MCC de la prueba a un umbral congelado en validación, con etiquetas (#191)
}
PIDE_PRUEBA = re.compile(r"incluir_prueba\s*=\s*True")
LLAMA_GUARDA = re.compile(r"\btomar_prueba\s*\(")


def _scripts():
    return sorted(p for p in SCRIPTS.glob("*.py"))


@pytest.mark.parametrize("ruta", _scripts(), ids=lambda p: p.name)
def test_solo_los_scripts_permitidos_leen_la_prueba(ruta):
    codigo = ruta.read_text(encoding="utf-8")
    toca = bool(PIDE_PRUEBA.search(codigo) or LLAMA_GUARDA.search(codigo))
    assert not toca or ruta.name in PERMITIDOS, (
        f"{ruta.name} lee la prueba reservada y no está en PERMITIDOS. "
        "Si es a propósito, agrégalo aquí, declara `toca_prueba` en sus params y pasa por "
        "`tomar_prueba(final=True, motivo=...)`.")


@pytest.mark.parametrize("ruta", _scripts(), ids=lambda p: p.name)
def test_quien_pide_incluir_prueba_deja_rastro(ruta):
    codigo = ruta.read_text(encoding="utf-8")
    if PIDE_PRUEBA.search(codigo):
        assert LLAMA_GUARDA.search(codigo), (
            f"{ruta.name} pide incluir_prueba=True pero no llama `tomar_prueba`: "
            "esa lectura no quedaría en experimentos/prueba.csv.")


def test_la_lista_permitida_no_acumula_archivos_que_ya_no_leen_la_prueba():
    """Una entrada que existe y ya no toca la prueba se quita, para que la lista no se pudra."""
    for nombre in sorted(PERMITIDOS):
        ruta = SCRIPTS / nombre
        if not ruta.exists():
            continue
        codigo = ruta.read_text(encoding="utf-8")
        assert PIDE_PRUEBA.search(codigo) or LLAMA_GUARDA.search(codigo), (
            f"{nombre} está en PERMITIDOS pero ya no lee la prueba: quítalo.")
