"""Estilo compartido de las animaciones, para que se parezcan al sitio.

Los colores salen de `estilos.scss` y de `recursos/graficas.js`, que es lo que
ya usan el sitio y el mazo. Si cambian allá, cambian aquí: una animación que
desentona del material que acompaña se lee como de otro proyecto.

**Sin LaTeX a propósito.** Todo el texto va con `Text`, que usa Pango, para que
renderizar no exija una instalación de TeX. Eso descarta `MathTex`, así que las
fórmulas se escriben con Unicode (`6 − log₁₀ µM`) o se dicen en la narración.
"""

import json
from pathlib import Path

from manim import BLACK, Scene, WHITE, Text, VGroup

# La paleta del sitio.
# **Los colores salen de `recursos/paleta.json`, no de aquí.** Vivían duplicados
# en este archivo, en `graficas.js` y en las dos hojas de estilo, y tres se
# habían desviado entre sí —el azul, el verde y el naranja— lo bastante poco
# para parecer un descuido. `scripts/paleta.py` los reparte y `--revisar` falla
# si alguno queda desfasado.
#
# Se usan los pasos de **modo oscuro**, porque el video siempre va sobre fondo
# oscuro. Los tres categóricos pasan las cinco comprobaciones de la guía de
# visualización con todas las parejas en juego; la paleta anterior fallaba tres,
# y la seria era que verde y naranja —«natural» y «BBB−»— quedaban a 5.9 de
# separación en protanopía.
_PALETA = json.loads(
    (Path(__file__).resolve().parents[1] / "recursos" / "paleta.json")
    .read_text(encoding="utf-8"))


def _c(grupo: str, rol: str) -> str:
    return _PALETA[grupo][rol]["oscuro"]


FONDO = _c("tintas", "fondo")
AZUL = _c("categoricos", "positivo")        # BBB+, entrenamiento
AZUL_CLARO = _c("tintas", "secundaria")     # trazo de apoyo, no una serie
VERDE = _c("categoricos", "natural")        # producto natural
NARANJA = _c("categoricos", "negativo")     # BBB−, lo que se reserva
ROJO = _c("estado", "alerta")               # error, fuga
GRIS = _c("tintas", "tenue")                # texto secundario
REJILLA = _c("tintas", "rejilla")           # contenedor, eje, cuadrícula
CREMA = _c("tintas", "texto")               # texto principal

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


# El cuadro de Manim en 16:9, con un margen para que nada quede pegado al borde.
ANCHO, ALTO = 14.222, 8.0
MARGEN = 0.25


def cabe(*objetos, margen: float = MARGEN) -> None:
    """Falla si algo se sale del cuadro, al renderizar y no al mirar el video.

    De los siete defectos de la primera versión de estas escenas, tres eran
    texto saliéndose por un borde, y los encontré extrayendo fotogramas a mano.
    Esto los convierte en un error con nombre y posición, que es lo que un
    defecto de composición debería ser.

    No sustituye mirar el resultado: no detecta solapamientos ni jerarquías
    mal puestas. Detecta la clase que más veces se repitió.
    """
    limite_x, limite_y = ANCHO / 2 - margen, ALTO / 2 - margen
    for o in objetos:
        izq, der = o.get_left()[0], o.get_right()[0]
        abajo, arriba = o.get_bottom()[1], o.get_top()[1]
        # `original_text` conserva los espacios; `text` no.
        texto = getattr(o, "original_text", None) or getattr(
            o, "text", type(o).__name__)
        if izq < -limite_x or der > limite_x:
            raise ValueError(
                f"se sale por los lados: «{texto}» ocupa de {izq:.2f} a"
                f" {der:.2f} y el cuadro llega a ±{limite_x:.2f}."
                " Acorta el texto, bájale el tamaño o pártelo en más líneas")
        if abajo < -limite_y or arriba > limite_y:
            raise ValueError(
                f"se sale por arriba o abajo: «{texto}» ocupa de {abajo:.2f} a"
                f" {arriba:.2f} y el cuadro llega a ±{limite_y:.2f}")


class Narrada(Scene):
    """Una escena cuyos actos duran lo que dura su narración.

    El audio manda sobre el tiempo, no al revés. Cada acto llama a
    `abrir_tramo(n)` al empezar y `cerrar_tramo(n)` al terminar: el segundo
    espera lo que falte del tramo, así que el dibujo y la voz acaban juntos.
    Si las animaciones del acto ya se pasaron, lo avisa — la respuesta
    entonces es quitar animación o escribir más narración, nunca acelerar la
    voz.

    Las duraciones salen de `voz/tiempos.json`, que escribe `voz.py` midiendo
    los audios de verdad. Es la fuente única: sin ella cada escena tendría sus
    tiempos a ojo y el montaje se arreglaría a mano.

    Sin ese archivo —o sin el tramo— la escena corre con tiempos por omisión,
    para poder trabajar el dibujo antes de tener voz.
    """

    POR_OMISION = 8.0
    # Una cola después del **último** tramo de la escena. Sin ella el video
    # acaba en el mismo fotograma que la voz, y entre que la síntesis no
    # devuelve dos veces la misma duración y el montaje redondea, el audio se
    # pasa unas décimas del final y `sonorizar.py` se niega a montarlo. Vivía
    # como un `wait` suelto en `fingerprints.py`, que es el único sitio donde
    # alguien se acordó de ponerlo.
    COLA = 1.0

    # **El congelado más largo que se tolera con la voz hablando encima.**
    # La auditoría del video midió 50 s en el embudo del linaje, 30 en Sort &
    # Slice y 24.9 en el cierre: la pantalla quieta mientras la narración
    # seguía, que es justo lo que una animación no debe hacer. `respira()`
    # reparte el silencio, pero repartirlo entre dos compases en un tramo de
    # treinta segundos todavía deja quince de imagen fija, así que hacía falta
    # medirlo y no suponerlo.
    #
    # Nueve segundos no sale de ninguna norma: es el tope que deja margen sobre
    # lo medido. Al poner la guarda, el peor tramo se quedaba 29.2 s quieto
    # (`matriz` 2, que se montó sin un solo `respira()`); repartidos los cinco
    # que pasaban del tope, el peor es ahora 7.9 s (`particion` 4). El margen
    # se estrecha cuando el reparto mejore, no antes, y la cifra de cada tramo
    # queda en `voz/offsets.json` para no tener que volver a renderizar.
    TOPE_CONGELADO = 9.0

    def setup(self) -> None:
        super().setup()
        self._tramos = self._cargar_tramos()
        self._inicio = 0.0
        self._offsets = {}
        self._compases = 1
        self._compases_totales = 1
        self._animado = 0.0
        self._respirado = 0.0
        self._quietos = []           # (tramo, segundos) de cada espera

    def tear_down(self) -> None:
        """Deja por escrito en qué segundo empieza cada tramo.

        Es lo que permite colocar el audio exactamente donde va, en vez de
        concatenarlo y confiar en que las pausas coincidan. Lo escribe la
        escena al renderizar porque es la única que lo sabe: los tiempos
        dependen de las animaciones que de verdad se jugaron.
        """
        if not self._offsets:
            return super().tear_down()
        ruta = Path(__file__).resolve().parent / "voz" / "offsets.json"
        ruta.parent.mkdir(exist_ok=True)
        datos = json.loads(ruta.read_text()) if ruta.exists() else {}
        clave = type(self).__module__.rsplit(".", 1)[-1]
        quietos = {}
        for n, q in getattr(self, "_quietos", []):
            quietos[str(n)] = max(quietos.get(str(n), 0.0), round(q, 2))
        datos[clave] = {"tramos": {str(n): round(s, 3)
                                   for n, s in sorted(self._offsets.items())},
                        # El congelado más largo de cada tramo, para poder ver
                        # el reparto sin volver a renderizar.
                        "quieto_max_s": quietos,
                        "duracion_s": round(self.renderer.time, 3)}
        ruta.write_text(json.dumps(datos, indent=1, ensure_ascii=False) + "\n")
        return super().tear_down()

    def _cargar_tramos(self) -> dict:
        ruta = Path(__file__).resolve().parent / "voz" / "tiempos.json"
        if not ruta.exists():
            return {}
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        # El nombre del módulo de la escena es la llave: `cierre.py` → «cierre».
        clave = type(self).__module__.rsplit(".", 1)[-1]
        return {t["n"]: t for t in datos.get(clave, {}).get("tramos", [])}

    def dura(self, n: int) -> float:
        return self._tramos.get(n, {}).get("segundos", self.POR_OMISION)

    def abrir_tramo(self, n: int, compases: int = 1) -> None:
        """Abre el tramo `n`, que se repartirá en `compases` respiros.

        `compases` es cuántas veces va a llamar el acto a `respira()`, contando
        el relleno final que hace `cerrar_tramo`. Con el valor por omisión, 1,
        se comporta como antes: todo el silencio al final.
        """
        self._inicio = self.renderer.time
        self._tramo_actual = n
        self._offsets[n] = self._inicio
        self._respirado = 0.0
        self._compases = max(1, compases)
        self._compases_totales = self._compases
        self._animado = 0.0          # segundos de dibujo, sin contar respiros

    def respira(self) -> None:
        """Espera **la parte que le toca** del silencio que falta.

        El acto se escribe como se cuenta —un paso, un respiro, otro paso— y
        cada respiro se queda con `falta / compases_restantes`. Al dividir
        sobre lo que falta y no sobre el total, se corrige solo: si un paso se
        alargó, los respiros siguientes se acortan.

        **Por qué existe.** `cerrar_tramo` rellenaba con un único `wait` al
        final, así que todo el dibujo ocurría en el primer cuarto del tramo y
        la pantalla se quedaba congelada el resto: cincuenta segundos en el
        embudo del linaje, treinta en Sort & Slice, veinticuatro en el cierre.
        La voz seguía hablando sobre una imagen fija, que es justo lo que una
        animación no debe hacer.
        """
        if self._tramo_actual is None:
            raise RuntimeError("`respira()` fuera de un tramo abierto")
        transcurrido = self.renderer.time - self._inicio
        falta = self.dura(self._tramo_actual) - transcurrido
        self._animado = transcurrido - self._respirado

        # **Hay que descontar la animación que todavía no ocurrió.** Repartir
        # `falta / compases_restantes` a secas es goloso: el primer respiro se
        # queda con su parte sin saber cuánto dibujo viene después, y el acto se
        # pasa del tramo. Pasó con `linaje` 2 (3.6 s de más) y `fingerprints` 1
        # (1.7 s). Como los compases marcan pasos de tamaño parecido, lo ya
        # dibujado por compás usado estima lo que falta por dibujar.
        usados = self._compases_totales - self._compases + 1
        restantes = self._compases
        por_compas = self._animado / max(1, usados)
        reserva = por_compas * max(0, restantes - 1)

        espera = (falta - reserva) / restantes
        # Un `respira()` de más —el caso típico es uno dentro de un bucle cuyas
        # vueltas no se contaron— dejaría a los últimos quedándose con todo lo
        # que falta, y el acto se pasa del tramo. Pasó con `linaje` 2 y
        # `fingerprints` 1: tres vueltas cada uno, declaradas como una.
        if self._compases <= 1 and usados > self._compases_totales:
            raise RuntimeError(
                f"el tramo {self._tramo_actual} llamó a `respira()` "
                f"{usados} veces y declaró {self._compases_totales} compases. "
                "Si el respiro va dentro de un bucle, cuenta sus vueltas en "
                "`abrir_tramo(n, compases=…)`")
        self._compases = max(1, self._compases - 1)
        # `manim` rechaza `wait(0)`, y aquí llega a cero de forma legítima: si
        # al acto no le sobra tiempo, el respiro que toca es ninguno. Si se pasa
        # de verdad, el aviso lo da `cerrar_tramo`, que mide el total.
        if espera > 0.04:
            self.wait(espera)
            self._respirado += espera
            self._quietos.append((self._tramo_actual, espera))

    def cerrar_tramo(self, n: int) -> None:
        # Cerrar un tramo que no es el abierto significa que la llamada acabó
        # en el método equivocado —un auxiliar, por ejemplo— y entonces el
        # relleno ocurre en otro momento y la voz se encima con la siguiente.
        # Pasó con `intervalo` y `particion`: el cierre del tramo 1 terminó
        # dentro de `_cambiar`, y el audio se solapó cuatro y seis segundos.
        abierto = getattr(self, "_tramo_actual", None)
        if abierto != n:
            raise RuntimeError(
                f"se cierra el tramo {n} pero el abierto es {abierto}. "
                "Cada `cerrar_tramo(n)` va al final del mismo acto que llamó "
                "a `abrir_tramo(n)`, nunca en un método auxiliar")
        self._tramo_actual = None
        self._compases = 1
        objetivo = self.dura(n)
        gastado = self.renderer.time - self._inicio
        if gastado > objetivo + 0.05:
            titulo = self._tramos.get(n, {}).get("titulo", "")
            print(f"  [tramo {n} {titulo}] la animación dura {gastado:.1f} s y"
                  f" la voz {objetivo:.1f} s: se pasa {gastado - objetivo:.1f} s."
                  " Quita animación o escribe más narración; no aceleres la voz.")
            return
        relleno = max(0.0, objetivo - gastado)
        self.wait(relleno)
        if relleno > 0.04:
            self._quietos.append((n, relleno))

        # El tope se revisa aquí y no al final de la escena para que el aviso
        # diga **qué tramo** se queda quieto, que es donde hay que repartir.
        largo = max((q for t, q in self._quietos if t == n), default=0.0)
        if largo > self.TOPE_CONGELADO and self._tramos:
            titulo = self._tramos.get(n, {}).get("titulo", "")
            raise RuntimeError(
                f"el tramo {n} ({titulo}) se queda {largo:.1f} s con la imagen"
                f" fija y la voz hablando, y el tope son {self.TOPE_CONGELADO:.0f} s."
                " Súbele los compases a `abrir_tramo` y reparte el dibujo, o"
                " pártelo en varios tramos en el guion")

        if self._tramos and n == max(self._tramos):
            self.wait(self.COLA)


def matriz(filas: int, columnas: int, ancho: float = 7.0, alto: float = 2.6,
           color: str = AZUL, relleno: float = 0.55):
    """Una cuadrícula que representa una matriz, para poder quitarle columnas.

    No dibuja las celdas reales —serían decenas de miles— sino una rejilla que
    se lee como matriz: cada columna del dibujo representa un bloque de
    columnas reales. Lo que importa es **ver** la matriz encogerse, no contar
    celdas.

    Devuelve un `VGroup` de columnas, cada una un `VGroup` de celdas, para que
    quitar columnas sea quitar elementos del grupo.
    """
    from manim import Rectangle

    cw, ch = ancho / columnas, alto / filas
    rejilla = VGroup()
    for j in range(columnas):
        col = VGroup()
        for i in range(filas):
            celda = Rectangle(width=cw, height=ch, color=color,
                              fill_opacity=relleno, stroke_width=0.6,
                              stroke_color=FONDO)
            celda.move_to([j * cw, -i * ch, 0])
            col.add(celda)
        rejilla.add(col)
    rejilla.move_to([0, 0, 0])
    return rejilla


def separados(a, b, minimo: float = 0.08) -> None:
    """Falla si dos objetos se solapan. El otro defecto que se repitió."""
    ax1, ax2 = a.get_left()[0], a.get_right()[0]
    ay1, ay2 = a.get_bottom()[1], a.get_top()[1]
    bx1, bx2 = b.get_left()[0], b.get_right()[0]
    by1, by2 = b.get_bottom()[1], b.get_top()[1]
    solapa_x = min(ax2, bx2) - max(ax1, bx1)
    solapa_y = min(ay2, by2) - max(ay1, by1)
    if solapa_x > -minimo and solapa_y > -minimo:
        ta = getattr(a, "original_text", None) or getattr(a, "text", type(a).__name__)
        tb = getattr(b, "original_text", None) or getattr(b, "text", type(b).__name__)
        raise ValueError(f"se enciman: «{ta}» y «{tb}»")


__all__ = ["FONDO", "AZUL", "AZUL_CLARO", "VERDE", "NARANJA", "ROJO", "GRIS",
           "CREMA", "REJILLA", "FUENTE", "ANCHO", "ALTO", "MARGEN", "titulo", "subtitulo",
           "dato", "pie", "cabe", "matriz", "separados", "Narrada", "BLACK",
           "WHITE", "VGroup"]
