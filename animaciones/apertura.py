"""El problema, la apuesta y la tesis que recorre todo lo demás.

Abre el video completo. Su trabajo no es explicar un método sino dar la razón
para ver los cuatro que siguen, y plantar la frase que los encadena: **los
datos no son lo que parecen**.

    manim -qh animaciones/apertura.py Apertura

Las cifras son del planteamiento del proyecto y del registro de decisiones.
Las de desempeño no van aquí: esta escena no afirma resultados.
"""

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, Dot, FadeIn, FadeOut, Indicate, Line, RoundedRectangle, VGroup, VMobject,
                   Write, config)

from comun import (Narrada, AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA,
                   VERDE, cabe, dato, pie, separados, subtitulo, titulo)

config.background_color = FONDO


class Apertura(Narrada):
    def construct(self) -> None:
        self._el_problema()
        self._la_apuesta()
        self._la_tesis()

    # -- 1. el problema ------------------------------------------------------
    # La silueta sagital, en coordenadas normalizadas de −1 a 1. Es un contorno
    # cerrado y no una elipse: lleva el polo frontal a la izquierda, el vértice
    # arriba, el occipital a la derecha y el lóbulo temporal colgando por
    # delante y abajo. Son los cuatro rasgos que hacen que se lea como cerebro
    # y no como nube.
    _SILUETA = [
        (-1.00, 0.08), (-0.95, 0.45), (-0.74, 0.74), (-0.38, 0.92),
        (0.05, 0.94), (0.46, 0.78), (0.78, 0.48), (0.93, 0.12),
        (0.86, -0.22), (0.62, -0.38), (0.34, -0.44), (0.02, -0.46),
        (-0.30, -0.52), (-0.60, -0.58), (-0.84, -0.44), (-0.98, -0.16),
    ]
    # Los surcos **nacen y mueren en el contorno**, que es lo que los vuelve
    # pliegues en vez de rayones sueltos. El primero es la cisura de Silvio,
    # que separa el lóbulo temporal y es la que más hace por el parecido.
    _SURCOS = [
        [(-0.86, -0.26), (-0.50, -0.34), (-0.10, -0.30), (0.26, -0.20)],
        [(-0.70, 0.78), (-0.62, 0.46), (-0.48, 0.22), (-0.40, 0.00)],
        [(-0.30, 0.93), (-0.26, 0.58), (-0.16, 0.30), (-0.14, 0.04)],
        [(0.12, 0.93), (0.20, 0.60), (0.28, 0.34), (0.26, 0.10)],
        [(0.52, 0.74), (0.54, 0.48), (0.56, 0.26), (0.48, 0.06)],
        [(-0.93, 0.36), (-0.74, 0.26), (-0.62, 0.12), (-0.60, -0.04)],
        [(0.86, 0.22), (0.66, 0.12), (0.54, -0.04), (0.50, -0.20)],
    ]

    @staticmethod
    def _cerebro(alto: float = 2.3) -> VGroup:
        """Un cerebro de perfil: silueta, surcos, cerebelo y tallo.

        No es anatomía exacta, es un signo — pero un signo tiene que leerse. La
        versión anterior era una elipse con arcos sueltos por dentro, y los
        arcos no tocaban el borde, así que parecían rayones. Un surco se lee
        como surco cuando **entra desde el contorno**.
        """
        k = alto / 1.9

        def puntos(lista):
            return [np.array([x * k * 1.15, y * k, 0.0]) for x, y in lista]

        corteza = VMobject(color=AZUL_CLARO, stroke_width=2.6)
        corteza.set_points_smoothly(puntos(Apertura._SILUETA + [Apertura._SILUETA[0]]))
        corteza.set_fill(AZUL_CLARO, opacity=0.16)

        surcos = VGroup()
        for traza in Apertura._SURCOS:
            c = VMobject(color=AZUL_CLARO, stroke_width=1.8, stroke_opacity=0.75)
            c.set_points_smoothly(puntos(traza))
            surcos.add(c)

        # El cerebelo, abajo y atrás, con sus estrías horizontales: es el
        # segundo rasgo que lo identifica, después de la silueta.
        cerebelo = VMobject(color=AZUL_CLARO, stroke_width=2.2)
        cerebelo.set_points_smoothly(puntos([
            (0.30, -0.44), (0.60, -0.46), (0.80, -0.62), (0.74, -0.84),
            (0.48, -0.92), (0.24, -0.80), (0.20, -0.60), (0.30, -0.44)]))
        cerebelo.set_fill(AZUL_CLARO, opacity=0.10)
        estrias = VGroup(*[
            Line(np.array([0.26 * k * 1.15, y * k, 0.0]),
                 np.array([0.76 * k * 1.15, (y - 0.06) * k, 0.0]),
                 color=AZUL_CLARO, stroke_width=1.0, stroke_opacity=0.6)
            for y in (-0.58, -0.68, -0.78)])

        # El tallo: baja desde el centro, por delante del cerebelo.
        tallo = VMobject(color=AZUL_CLARO, stroke_width=2.4)
        tallo.set_points_smoothly(puntos([
            (0.02, -0.46), (0.06, -0.66), (0.10, -0.86), (0.04, -1.04)]))

        return VGroup(corteza, surcos, cerebelo, estrias, tallo)

    @staticmethod
    def _barrera(alto: float = 3.4) -> VGroup:
        """La barrera como una hilera de células muy unidas, que es lo que es."""
        celulas = VGroup()
        n = 9
        for i in range(n):
            c = RoundedRectangle(width=0.34, height=alto / n * 0.92,
                                 corner_radius=0.06, color=NARANJA,
                                 fill_opacity=0.3, stroke_width=1.6)
            celulas.add(c)
        celulas.arrange(DOWN, buff=alto / n * 0.08)
        return celulas

    def _el_problema(self) -> None:
        self.abrir_tramo(1, compases=3)
        t = titulo("Casi nada llega al cerebro", 40).to_edge(UP, buff=0.8)
        cabe(t)
        self.play(Write(t), run_time=1.3)

        # El escenario: sangre a la izquierda, barrera en medio, cerebro a la
        # derecha. Se construye de izquierda a derecha, como se lee.
        cerebro = self._cerebro(2.4).shift(RIGHT * 3.9 + DOWN * 0.4)
        barrera = self._barrera(4.6).shift(LEFT * 0.2 + DOWN * 0.3)
        rotulo_b = subtitulo("barrera hematoencefálica", 17)
        rotulo_b.next_to(barrera, UP, buff=0.25)
        rotulo_s = subtitulo("sangre", 17).move_to(LEFT * 4.4 + DOWN * 2.1)
        cabe(cerebro, barrera, rotulo_b, rotulo_s)
        self.play(FadeIn(cerebro, shift=LEFT * 0.3), run_time=0.9)
        self.play(Create(barrera, lag_ratio=0.08), FadeIn(rotulo_b),
                  FadeIn(rotulo_s), run_time=1.2)

        # Las moléculas salen de la sangre y chocan. Dos de catorce pasan: es
        # la proporción que la frase dice, puesta en el dibujo.
        rng = np.random.default_rng(11)
        moleculas, pasan = VGroup(), []
        for i in range(14):
            m = Dot(radius=0.11, color=AZUL,
                    fill_opacity=0.9).move_to(
                        LEFT * 5.2 + UP * rng.uniform(-1.9, 1.1))
            moleculas.add(m)
            pasan.append(i in (4, 9))
        self.play(FadeIn(moleculas, lag_ratio=0.05), run_time=0.8)

        rebotes, cruces = [], []
        for m, pasa in zip(moleculas, pasan):
            y = m.get_center()[1]
            if pasa:
                cruces.append(m.animate.move_to(cerebro.get_center()
                                                + np.array([rng.uniform(-0.6, 0.6),
                                                            rng.uniform(-0.6, 0.6), 0]))
                              .set_color(VERDE))
            else:
                rebotes.append(m.animate.move_to(
                    np.array([rng.uniform(-2.6, -1.2), y, 0])).set_opacity(0.45))
        self.play(*rebotes, *cruces, run_time=2.2)
        self.play(Indicate(barrera, color=NARANJA, scale_factor=1.03),
                  run_time=0.8)

        marca = dato("casi todos rebotan", 22, NARANJA)
        marca.move_to(LEFT * 3.3 + UP * 1.9)
        cabe(marca)
        self.play(FadeIn(marca), run_time=0.7)
        self.respira()

        caro = subtitulo("Y probar uno en el laboratorio es lento y caro.", 21)
        caro.to_edge(DOWN, buff=0.95).set_x(0)
        separados(caro, rotulo_b)
        cabe(caro)
        self.play(Write(caro), run_time=1.6)
        self.respira()

        # Y el segundo golpe: los naturales, que es de lo que trata todo.
        self.play(FadeOut(marca), FadeOut(caro), run_time=0.5)
        sinteticos = VGroup(*[Dot(radius=0.075, color=AZUL, fill_opacity=0.85)
                              for _ in range(40)])
        sinteticos.arrange_in_grid(4, 10, buff=0.16)
        naturales = VGroup(*[Dot(radius=0.075, color=VERDE, fill_opacity=0.85)
                             for _ in range(8)])
        naturales.arrange_in_grid(4, 2, buff=0.16)
        grupos = VGroup(sinteticos, naturales).arrange(RIGHT, buff=1.1)
        grupos.move_to(DOWN * 0.5)
        e1 = subtitulo("sintéticos: muy explorados", 17)
        e1.next_to(sinteticos, DOWN, buff=0.3)
        e2 = subtitulo("naturales: apenas", 17).next_to(naturales, DOWN, buff=0.3)
        cabe(grupos, e1, e2)
        self.play(FadeOut(VGroup(cerebro, barrera, rotulo_b, rotulo_s,
                                 moleculas)), run_time=0.6)
        self.play(FadeIn(sinteticos, lag_ratio=0.02), FadeIn(e1), run_time=1.2)
        self.play(FadeIn(naturales, lag_ratio=0.08), FadeIn(e2), run_time=1.0)
        self.play(Indicate(naturales, color=VERDE, scale_factor=1.25),
                  run_time=1.0)

        remate = subtitulo("Y son una fuente prometedora.", 21)
        remate.to_edge(DOWN, buff=1.0).set_x(0)
        cabe(remate)
        self.play(Write(remate), run_time=1.3)
        self.cerrar_tramo(1)
        self.play(FadeOut(VGroup(t, grupos, e1, e2, remate)), run_time=0.7)

    def _la_apuesta(self) -> None:
        self.abrir_tramo(2, compases=3)
        t = titulo("La apuesta: predecir desde la estructura").to_edge(UP, buff=0.9)
        s = subtitulo("una molécula entra como texto, y salen dos respuestas", 22)
        s.next_to(t, DOWN, buff=0.3).set_x(0)
        cabe(t, s)
        self.play(Write(t), FadeIn(s), run_time=1.4)

        entrada = dato("CC(=O)Oc1ccccc1C(=O)O", 22, AZUL_CLARO)
        entrada.shift(UP * 0.35)
        pie_entrada = subtitulo("SMILES: la molécula escrita como una cadena",
                                17)
        pie_entrada.next_to(entrada, DOWN, buff=0.22).set_x(0)
        cabe(entrada, pie_entrada)
        self.play(FadeIn(entrada), FadeIn(pie_entrada), run_time=1.2)
        self.respira()

        preguntas = VGroup()
        for texto, color in (("¿cruza la barrera?", AZUL),
                             ("¿actúa sobre la diana?", VERDE)):
            caja = VGroup(
                Circle(radius=0.14, color=color, fill_opacity=0.9,
                       stroke_width=0),
                dato(texto, 22, CREMA),
            ).arrange(RIGHT, buff=0.3)
            preguntas.add(caja)
        preguntas.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        preguntas.next_to(pie_entrada, DOWN, buff=0.7).set_x(0)
        cabe(preguntas)
        self.play(FadeIn(preguntas, lag_ratio=0.3, shift=DOWN * 0.2),
                  run_time=1.3)
        self.respira()

        nota = subtitulo("No es una cascada: un «no cruza» predicho no descarta"
                         " nada.\nLas dos son evidencia que se combina al"
                         " priorizar.", 20)
        nota.next_to(preguntas, DOWN, buff=0.55).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=2.0)
        self.cerrar_tramo(2)
        self.wait(2.0)
        self.play(FadeOut(VGroup(t, s, entrada, pie_entrada, preguntas, nota)),
                  run_time=0.7)

    # -- 3. la tesis ---------------------------------------------------------
    def _la_tesis(self) -> None:
        self.abrir_tramo(3)
        t = titulo("Pero antes de predecir hay que mirar los datos", 34)
        t.to_edge(UP, buff=0.8)
        cabe(t)
        self.play(Write(t), run_time=1.5)
        self.wait(0.6)

        tesis = titulo("Y los datos no son lo que parecen.", 36)
        tesis.set_color(NARANJA).next_to(t, DOWN, buff=0.55).set_x(0)
        cabe(tesis)
        self.play(FadeIn(tesis, scale=0.92), run_time=1.2)
        self.wait(1.4)

        linea = Line(LEFT * 4.2, RIGHT * 4.2, color=GRIS, stroke_width=1)
        linea.next_to(tesis, DOWN, buff=0.5)
        lista = VGroup(
            subtitulo("Las mediciones no son compuestos.", 20),
            subtitulo("Un «mayor que» no es un dato faltante.", 20),
            subtitulo("Un bit no es un fragmento.", 20),
            subtitulo("Las filas no son independientes.", 20),
        ).arrange(DOWN, buff=0.24)
        lista.next_to(linea, DOWN, buff=0.35).set_x(0)
        cabe(linea, lista)
        self.play(Create(linea), run_time=0.6)
        for item in lista:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.5)
        self.wait(1.2)

        cierre = subtitulo("Cada una costó una medición.", 20)
        cierre.next_to(lista, DOWN, buff=0.4).set_x(0)
        cabe(cierre)
        self.play(Write(cierre), run_time=1.8)

        fuente = pie("Bioactive AI · Equipo 7 · Maestría en Inteligencia"
                     " Artificial Aplicada")
        fuente.to_edge(DOWN, buff=0.28)
        self.play(FadeIn(fuente), run_time=0.8)
        self.wait(2.2)

        self.cerrar_tramo(3)