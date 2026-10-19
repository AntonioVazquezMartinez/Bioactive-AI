"""Estilo compartido de las animaciones, para que se parezcan al sitio.

Los colores salen de `estilos.scss` y de `recursos/graficas.js`, que es lo que
ya usan el sitio y el mazo. Si cambian allá, cambian aquí: una animación que
desentona del material que acompaña se lee como de otro proyecto.

**Sin LaTeX a propósito.** Todo el texto va con `Text`, que usa Pango, para que
renderizar no exija una instalación de TeX. Eso descarta `MathTex`, así que las
fórmulas se escriben con Unicode (`6 − log₁₀ µM`) o se dicen en la narración.
"""

from manim import BLACK, WHITE, Text, VGroup

# La paleta del sitio.
FONDO = "#1b2430"        # el azul oscuro de las secciones del mazo
AZUL = "#3b78d6"         # el primario
AZUL_CLARO = "#8fb3dd"
VERDE = "#2e8b57"        # «bien», entrenamiento
NARANJA = "#e07b1a"      # «ojo», lo que se reserva
ROJO = "#d64541"         # error, fuga
GRIS = "#9aa8b8"         # texto secundario
CREMA = "#e8edf3"        # texto principal sobre fondo oscuro

FUENTE = "Helvetica Neue"


def titulo(texto: str, tamano: int = 34) -> Text:
    return Text(texto, font=FUENTE, font_size=tamano, color=CREMA, weight="BOLD")


def subtitulo(texto: str, tamano: int = 22) -> Text:
    return Text(texto, font=FUENTE, font_size=tamano, color=GRIS)


def dato(texto: str, tamano: int = 26, color: str = CREMA) -> Text:
    return Text(texto, font=FUENTE, font_size=tamano, color=color)


def pie(texto: str) -> Text:
    """La línea de procedencia. Toda cifra en pantalla dice de dónde sale."""
    return subtitulo(texto, 16)


__all__ = ["FONDO", "AZUL", "AZUL_CLARO", "VERDE", "NARANJA", "ROJO", "GRIS",
           "CREMA", "FUENTE", "titulo", "subtitulo", "dato", "pie",
           "BLACK", "WHITE", "VGroup"]
