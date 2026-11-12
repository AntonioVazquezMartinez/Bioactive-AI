"""Los cuadernos del Avance 5 no vuelven a perder el hilo: ni celdas sin título ni muros.

Esta prueba existe porque el mismo defecto apareció dos veces y las dos lo
encontró alguien leyendo, no una comprobación:

1. La lectura de las cuatro figuras del 05b llegó a **11,119 caracteres en una
   celda**, porque rellenar un hueco cae siempre en la celda que ya era la
   mayor. El 05c pasó de 2,453 a 6,845 en un solo PR por lo mismo.
2. Al partir esas celdas, el #205 cortó en las entradillas en negrita **sin
   ascenderlas a título**, así que el 05 pasó de 2 a 7 celdas de markdown sin
   ningún encabezado y el 05c de 0 a 5. Una celda sin encabezado no sale en el
   índice, ni en el TOC del sitio, ni da corte al deck.

`CUBIERTOS` es la lista de cuadernos vigilados, como `CON_DECK` en
`tests/test_armar_deck.py`. Están los tres del Avance 5 y el 06. **Los demás
quedan fuera porque arrastran de 1 a 20 celdas huérfanas de antes de que la
regla existiera** (el 01 tiene 20 y el 02 quince), y meterlos pide primero
ponerlos al día, no bajar la vara.

El 06 entra porque el defecto volvió a pasar justo donde nadie medía: el #320
le añadió dos celdas de una línea con la entradilla en negrita (`**Fase 1,
permeabilidad.**` y `**Fase 2, potencia.**`) y pasó el CI, porque el cuaderno
que la patrocinadora recibe no estaba en esta lista. Se corrigieron en ese PR,
y la que arrastraba de antes (`**Cómo leerla.**`) es ahora `### Cómo leer la
tabla`, así que el 06 entra sin bajar la vara.

Los dos techos son **trinquetes medidos, no objetivos**: se fijaron justo por
encima del peor caso del día en que la prueba entró (párrafo 2,024 en el 05,
frase 421 en el 05b). Sirven para que la prosa no vuelva a crecer, y **hay que
bajarlos** a medida que el trabajo de legibilidad avance. El techo que de
verdad se quiere es del orden del 04, que es la referencia: 1,046 de párrafo.
"""

import pytest

from scripts.medir_prosa import CUADERNOS, medir

CUBIERTOS = (
    "05_Modelo_Final.ipynb",
    "05b_Ensambles_actividad.ipynb",
    "05c_Ensambles_permeabilidad_huellas.ipynb",
    "06_Uso_de_los_modelos.ipynb",
)

TECHO_PARRAFO = 2_100
TECHO_FRASE = 450


@pytest.fixture(scope="module", params=CUBIERTOS)
def medida(request):
    ruta = CUADERNOS / request.param
    assert ruta.exists(), f"{request.param} ya no está en notebooks/"
    return request.param, medir(ruta)


def test_ninguna_celda_de_markdown_se_queda_sin_titulo(medida):
    nombre, m = medida
    assert not m["huerfanas"], (
        f"{nombre}: las celdas {m['huerfanas']} no tienen ningún encabezado, así que "
        "no salen en el índice ni dan corte al deck. Asciende su entradilla en "
        "negrita a título, como hacen los `#### N.` del 05b")


def test_ningun_parrafo_pasa_del_techo(medida):
    nombre, m = medida
    largo, celda = m["parrafo"]
    assert largo <= TECHO_PARRAFO, (
        f"{nombre}: la celda {celda} tiene un párrafo de {largo:,} caracteres, por "
        f"encima del techo de {TECHO_PARRAFO:,}. Pártelo en los puntos que ya traen "
        "entradilla o numeración; el párrafo es la unidad de escaneo, no la celda")


def test_ninguna_frase_pasa_del_techo(medida):
    nombre, m = medida
    largo, celda = m["frase"]
    assert largo <= TECHO_FRASE, (
        f"{nombre}: la celda {celda} tiene una frase de {largo:,} caracteres, por "
        f"encima del techo de {TECHO_FRASE}. Son más de 70 palabras: hay que releerla "
        "para saber cuál era el sujeto")


def test_los_techos_siguen_apretados():
    """Un trinquete que nadie baja deja de medir. Si los tres cuadernos bajan
    bien del techo, es que toca bajarlo, y esta prueba lo recuerda fallando."""
    peor_parrafo = max(medir(CUADERNOS / n)["parrafo"][0] for n in CUBIERTOS)
    holgura = TECHO_PARRAFO - peor_parrafo
    assert holgura < 400, (
        f"el peor párrafo de los cuadernos cubiertos son {peor_parrafo:,} caracteres "
        f"y el techo está en {TECHO_PARRAFO:,}: sobran {holgura}. Baja "
        "TECHO_PARRAFO a ras del peor caso para que el trinquete siga sirviendo")
