"""Pruebas para la función de guarda de la partición de prueba."""

from __future__ import annotations

import csv

import pandas as pd
import pytest

from src.tracking import tomar_prueba


@pytest.fixture
def pares_ejemplo():
    return pd.DataFrame({
        "particion": ["entrenamiento", "validacion", "prueba", "prueba"],
        "estrato": ["solo_chembl", "solo_npass", "solo_chembl", "solo_npass"],
    })


def test_sin_bandera_final_lanza_error_y_sugiere_alternativa(pares_ejemplo, tmp_path):
    with pytest.raises(ValueError, match="pares\\[.*!=.*prueba"):
        tomar_prueba(pares_ejemplo, raiz=tmp_path)

    # Asegura que no se cree el archivo si no se pasa final=True
    assert not (tmp_path / "experimentos" / "prueba.csv").exists()


def test_sin_motivo_lanza_error(pares_ejemplo, tmp_path):
    with pytest.raises(ValueError, match="motivo"):
        tomar_prueba(pares_ejemplo, final=True, motivo="", raiz=tmp_path)

    with pytest.raises(ValueError, match="motivo"):
        tomar_prueba(pares_ejemplo, final=True, motivo="   ", raiz=tmp_path)


def test_devuelve_filas_de_prueba_e_imprime_estratos(pares_ejemplo, tmp_path, capsys):
    resultado = tomar_prueba(
        pares_ejemplo,
        final=True,
        motivo="Evaluación de modelo final",
        raiz=tmp_path,
    )

    # Solo debe retornar las filas correspondientes a la prueba
    assert len(resultado) == 2
    assert (resultado["particion"] == "prueba").all()

    # Comprobar que se imprimió el resumen de estratos
    salida = capsys.readouterr().out
    assert "solo_chembl" in salida
    assert "solo_npass" in salida


def test_registra_en_bitacora_csv(pares_ejemplo, tmp_path):
    tomar_prueba(pares_ejemplo, final=True, motivo="Primera corrida", raiz=tmp_path)
    tomar_prueba(pares_ejemplo, final=True, motivo="Segunda corrida", raiz=tmp_path)

    archivo_csv = tmp_path / "experimentos" / "prueba.csv"
    assert archivo_csv.exists()

    with open(archivo_csv, mode="r", encoding="utf-8") as f:
        filas = list(csv.reader(f))

    assert len(filas) == 3
    assert filas[0] == ["fecha", "autor", "commit", "filas", "motivo"]
    assert filas[1][4] == "Primera corrida"
    assert filas[2][4] == "Segunda corrida"


def test_motivo_con_comillas_y_comas_preserva_texto_exacto(pares_ejemplo, tmp_path):
    """Comprueba que comillas y comas se escapen bien y no muten el texto original."""
    motivo = 'el "mejor" modelo, por concordancia'
    tomar_prueba(pares_ejemplo, final=True, motivo=motivo, raiz=tmp_path)

    archivo_csv = tmp_path / "experimentos" / "prueba.csv"
    with open(archivo_csv, mode="r", encoding="utf-8") as f:
        filas = list(csv.reader(f))

    assert len(filas) == 2
    encabezado, fila_datos = filas[0], filas[1]

    # Deben ser 5 columnas y el motivo debe leerse idéntico, sin sustituir " por '
    assert len(encabezado) == 5
    assert len(fila_datos) == 5
    assert fila_datos[4] == motivo
