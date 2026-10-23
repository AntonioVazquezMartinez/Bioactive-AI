"""Por qué un «> 10 µM» no es un dato faltante, y qué se gana guardando el intervalo.

Es el concepto que más trabajo costó explicar por escrito en la propuesta de
variable objetivo: una medición censurada no es un hueco, es una cota, y la
etiqueta sale de dónde queda el intervalo respecto al corte. Dicho así son dos
párrafos; dibujado es un eje y tres trazos.

    manim -qh animaciones/intervalo.py Intervalo

Las cifras del cierre salen de la decisión 2.10 y del notebook 02b.
"""

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Create, Dot, FadeIn, FadeOut,
                   Line, NumberLine, VGroup, Write, config)

from comun import (Narrada, AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, ROJO, VERDE,
                   cabe, dato, pie, separados, subtitulo, titulo)

config.background_color = FONDO

# El eje es pActividad = 6 − log10(µM): a la derecha, más potente.
EJE_MIN, EJE_MAX = 3.0, 9.0
CORTE = 5.0  # 10 µM


class Intervalo(Narrada):
    def construct(self) -> None:
        self._el_eje()
        self._una_medicion_exacta()
        self._una_censurada()
        self._el_corte()
        self._lo_que_se_gana()

    # -- 1. el eje de potencia ----------------------------------------------
    def _el_eje(self) -> None:
        # Seis compases: al añadir la lectura en concentración, la narración de
        # este tramo pasó de siete segundos a treinta, y el silencio al final
        # dejaba veintiséis de imagen fija. Lo detectó `TOPE_CONGELADO`.
        self.abrir_tramo(1, compases=6)
        self.t = titulo("Una medición censurada no es un hueco")
        self.s = subtitulo("Es una cota: dice hasta dónde se miró sin ver efecto")
        self.t.to_edge(UP, buff=0.8)
        self.s.next_to(self.t, DOWN, buff=0.3)
        self.play(Write(self.t), run_time=1.1)
        self.respira()
        self.play(FadeIn(self.s, shift=DOWN * 0.2), run_time=0.7)
        self.respira()

        # Eje de 9 y no de 11: con 11 los rótulos de los extremos se salían del
        # cuadro. Y el nombre del eje va abajo del todo, porque a media altura
        # chocaba con la media recta del censurado.
        self.eje = NumberLine(
            x_range=[EJE_MIN, EJE_MAX, 1], length=8.6, color=GRIS,
            include_numbers=False, stroke_width=2)
        self.eje.move_to(UP * 0.1)
        izq = subtitulo("menos potente", 17).next_to(self.eje, LEFT, buff=0.3)
        der = subtitulo("más potente", 17).next_to(self.eje, RIGHT, buff=0.3)
        nombre = subtitulo("potencia  ·  6 − log₁₀ de la concentración en µM", 17)
        nombre.to_edge(DOWN, buff=0.45)
        cabe(self.eje, izq, der, nombre)
        self.play(Create(self.eje), run_time=1.3)
        self.respira()
        self.play(FadeIn(izq), FadeIn(der), FadeIn(nombre), run_time=0.9)
        self.respira()

        # **La misma recta, leída en concentración.** El eje es de potencia, así
        # que la concentración **baja** hacia la derecha, y sin eso en pantalla
        # la escena es incomprensible: un «0.5 µM» aparece a la derecha de un
        # «> 10 µM» y parece un error de dibujo. La pista vivía solo en la
        # fórmula del pie, que se lee una vez y dura lo que dura.
        #
        # No es un segundo eje con otra magnitud —lo que la guía de
        # visualización prohíbe— sino **la misma magnitud en otras unidades**,
        # como grados Celsius y Fahrenheit sobre un termómetro.
        self.concentraciones = VGroup()
        for potencia, rotulo in ((4.0, "100 µM"), (5.0, "10 µM"),
                                 (6.0, "1 µM")):
            marca = Line(self._x(potencia), self._x(potencia) + DOWN * 0.12,
                         color=GRIS, stroke_width=1.4)
            r = subtitulo(rotulo, 16)
            r.next_to(marca, DOWN, buff=0.08)
            self.concentraciones.add(marca, r)
        aviso = subtitulo("la concentración baja hacia la derecha", 16)
        aviso.next_to(self.concentraciones, DOWN, buff=0.18)
        self.concentraciones.add(aviso)
        cabe(self.concentraciones)
        self.play(FadeIn(self.concentraciones, lag_ratio=0.2), run_time=1.1)
        self.respira()

        self.bordes = VGroup(izq, der, nombre, self.concentraciones)
        self.cerrar_tramo(1)

    def _x(self, valor: float) -> np.ndarray:
        return self.eje.number_to_point(valor)

    def _cambiar(self, nuevo: str, sub: str) -> None:
        t = titulo(nuevo).move_to(self.t)
        s = subtitulo(sub).next_to(t, DOWN, buff=0.3)
        self.play(FadeOut(self.t), FadeOut(self.s), run_time=0.3)
        self.play(FadeIn(t), FadeIn(s), run_time=0.45)
        self.t, self.s = t, s

    # -- 2. una medición exacta ---------------------------------------------
    def _una_medicion_exacta(self) -> None:
        self.abrir_tramo(2)
        punto = Dot(self._x(6.3), radius=0.11, color=AZUL)
        # Arriba y a la derecha, no centrada sobre el punto: el corte de 1 µM
        # del acto 5 se dibuja en 6.0, a tres décimas de este punto, y la
        # etiqueta centrada le quedaba justo encima — la línea la atravesaba.
        etiqueta = dato("IC50 = 0.5 µM", 22, AZUL)
        etiqueta.next_to(punto, UP, buff=0.3).shift(RIGHT * 1.35)
        nota = subtitulo("una medición exacta es un punto:"
                         " el intervalo se colapsa", 20)
        nota.next_to(self.eje, DOWN, buff=1.6)
        self.play(FadeIn(punto, scale=0.5), FadeIn(etiqueta), run_time=0.9)
        self.play(Write(nota), run_time=1.3)
        self.cerrar_tramo(2)
        self.wait(1.2)
        self.play(FadeOut(nota), run_time=0.4)
        self.exacta = VGroup(punto, etiqueta)

    # -- 3. una censurada ----------------------------------------------------
    def _una_censurada(self) -> None:
        self.abrir_tramo(3, compases=3)
        self._cambiar("Y un «> 10 µM» es media recta",
                      "el ensayo llegó a 10 µM y no vio efecto: la potencia"
                      " está por debajo")
        inicio = self._x(CORTE)
        flecha = Arrow(inicio, self._x(EJE_MIN + 0.15), color=NARANJA,
                       stroke_width=5, buff=0, max_tip_length_to_length_ratio=0.05)
        flecha.shift(DOWN * 0.7)
        tope = Line(inicio + DOWN * 1.0, inicio + DOWN * 0.4, color=NARANJA,
                    stroke_width=5)
        etiqueta = dato("> 10 µM", 22, NARANJA).next_to(tope, RIGHT, buff=0.2)
        self.play(Create(tope), run_time=0.5)
        self.play(Create(flecha), FadeIn(etiqueta), run_time=1.1)
        self.respira()

        nota = subtitulo("No sabemos cuánto, pero sabemos que no llega hasta"
                         " aquí.\nTirarla sería tirar la única evidencia"
                         " negativa que tenemos.", 20)
        nota.next_to(self.eje, DOWN, buff=2.0)
        self.play(Write(nota), run_time=2.2)
        self.respira()
        self.cerrar_tramo(3)
        self.wait(1.6)
        self.play(FadeOut(nota), run_time=0.4)
        self.censurada = VGroup(flecha, tope, etiqueta)

    # -- 4. el corte decide --------------------------------------------------
    def _el_corte(self) -> None:
        self.abrir_tramo(4, compases=3)
        self._cambiar("La etiqueta sale de dónde cae el intervalo",
                      "no de un umbral aplicado a un número suelto")
        linea = Line(self._x(CORTE) + UP * 0.95, self._x(CORTE) + DOWN * 1.6,
                     color=CREMA, stroke_width=2)
        rotulo = dato("corte: 10 µM", 20, CREMA).next_to(linea, UP, buff=0.15)
        self.play(Create(linea), FadeIn(rotulo), run_time=0.9)
        self.respira()

        # A una altura fija bajo el eje, cada una de su lado del corte.
        activo = dato("activo", 24, VERDE).move_to(self._x(7.6) + DOWN * 1.9)
        inactivo = dato("inactivo", 24, ROJO).move_to(self._x(3.9) + DOWN * 1.9)
        cabe(activo, inactivo)
        separados(activo, rotulo)
        separados(inactivo, rotulo)
        self.play(FadeIn(activo, shift=DOWN * 0.2), run_time=0.7)
        self.play(FadeIn(inactivo, shift=UP * 0.2), run_time=0.7)
        self.respira()

        nota = subtitulo("El punto está entero a la derecha del corte."
                         "\nLa media recta está entera a la izquierda.", 20)
        nota.move_to(self.eje.get_center() + DOWN * 2.8)
        self.play(Write(nota), run_time=1.8)
        self.cerrar_tramo(4)
        self.wait(1.4)
        self.play(FadeOut(nota), FadeOut(activo), FadeOut(inactivo), run_time=0.5)
        self.corte = VGroup(linea, rotulo)

    # -- 5. mover el corte no reconstruye nada -------------------------------
    def _lo_que_se_gana(self) -> None:
        # Tres compases: el cambio de corte, las dos etiquetas y la tarjeta
        # de cierre, que ahora entra dentro del tramo.
        self.abrir_tramo(5, compases=3)
        self._cambiar("Por eso el umbral es una decisión de lectura",
                      "mover el corte no obliga a reconstruir la matriz")
        nuevo = 6.0  # 1 µM
        linea2 = Line(self._x(nuevo) + UP * 0.95, self._x(nuevo) + DOWN * 1.6,
                      color=AZUL_CLARO, stroke_width=2)
        rotulo2 = dato("corte: 1 µM", 20, AZUL_CLARO).next_to(linea2, UP, buff=0.15)
        # El corte nuevo cae en 6.0 y la medición exacta en 6.3: a tres décimas,
        # que en pantalla son centímetros. La etiqueta del acto 2 lleva un
        # desplazamiento a la derecha precisamente por esto, pero nada lo
        # comprobaba —y una separación que solo existe como comentario se
        # pierde en el primer ajuste de la escena. Aquí se comprueba.
        separados(self.exacta[1], rotulo2)
        separados(self.exacta[1], linea2)
        self.play(self.corte[0].animate.become(linea2),
                  self.corte[1].animate.become(rotulo2), run_time=1.4)
        self.respira()

        sigue = dato("sigue activo", 22, VERDE).move_to(self._x(7.6) + DOWN * 1.9)
        tambien = dato("sigue inactivo", 22, ROJO).move_to(self._x(3.9) + DOWN * 1.9)
        self.play(FadeIn(sigue), FadeIn(tambien), run_time=0.8)
        self.respira()

        # **La tarjeta de cierre entra dentro del tramo, no después.** Estaba
        # detrás de `cerrar_tramo(5)`, así que el remate de la escena —la frase
        # que resume el acto entero— aparecía cuando la voz ya había callado,
        # en el relleno de cola. El tramo dura 12.63 s y los actos gastaban
        # 3.45: sobraba sitio de sobra para decirla a tiempo. Igual que hace
        # `cierre.py` con la suya.
        self.play(FadeOut(sigue), FadeOut(tambien), FadeOut(self.exacta),
                  FadeOut(self.censurada), FadeOut(self.corte),
                  FadeOut(self.eje), FadeOut(self.bordes), run_time=0.8)

        cierre = VGroup(
            dato("Se guarda el intervalo, no la etiqueta.", 26, CREMA),
            subtitulo("La clasificación, la regresión y la regresión censurada"
                      "\nleen el mismo archivo. Cambiar de umbral es cambiar"
                      " qué columna se lee.", 20),
        ).arrange(DOWN, buff=0.45)
        cierre.move_to(DOWN * 0.2)
        cabe(cierre)
        self.play(FadeIn(cierre, lag_ratio=0.3), run_time=1.6)

        fuente = pie("Decisión 2.10 · notebook 02b · regla de la sección 7 del"
                     " diccionario de la patrocinadora")
        fuente.to_edge(DOWN, buff=0.3)
        cabe(cierre, fuente)
        self.play(FadeIn(fuente), run_time=0.8)
        self.respira()
        self.cerrar_tramo(5)
        self.wait(1.5)
