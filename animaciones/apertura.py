"""El problema, la apuesta y la tesis que recorre todo lo demás.

Abre el video completo. Su trabajo no es explicar un método sino dar la razón
para ver los cuatro que siguen, y plantar la frase que los encadena: **los
datos no son lo que parecen**.

    manim -qh animaciones/apertura.py Apertura

Las cifras son del planteamiento del proyecto y del registro de decisiones.
Las de desempeño no van aquí: esta escena no afirma resultados.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, FadeIn, FadeOut,
                   Line, Scene, VGroup, Write, config)

from comun import (AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, VERDE,
                   cabe, dato, pie, subtitulo, titulo)

config.background_color = FONDO


class Apertura(Scene):
    def construct(self) -> None:
        self._el_problema()
        self._la_apuesta()
        self._la_tesis()

    # -- 1. el problema ------------------------------------------------------
    def _el_problema(self) -> None:
        t = titulo("Casi nada llega al cerebro", 40).shift(UP * 1.2)
        cabe(t)
        self.play(Write(t), run_time=1.4)
        self.wait(0.5)

        s = subtitulo("La barrera hematoencefálica deja fuera a la gran mayoría"
                      "\nde los fármacos. Probar uno en laboratorio es lento y"
                      " caro.", 22)
        s.next_to(t, DOWN, buff=0.6).set_x(0)
        cabe(s)
        self.play(FadeIn(s, shift=DOWN * 0.2), run_time=1.5)
        self.wait(1.6)

        s2 = subtitulo("Y los productos naturales, que son una fuente"
                       " prometedora,\nestán mucho menos explorados que los"
                       " compuestos sintéticos.", 22)
        s2.next_to(s, DOWN, buff=0.5).set_x(0)
        cabe(s2)
        self.play(FadeIn(s2, shift=DOWN * 0.2), run_time=1.5)
        self.wait(1.8)
        self.play(FadeOut(t), FadeOut(s), FadeOut(s2), run_time=0.7)

    # -- 2. la apuesta -------------------------------------------------------
    def _la_apuesta(self) -> None:
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
        self.wait(1.0)

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
        self.wait(0.8)

        nota = subtitulo("No es una cascada: un «no cruza» predicho no descarta"
                         " nada.\nLas dos son evidencia que se combina al"
                         " priorizar.", 20)
        nota.next_to(preguntas, DOWN, buff=0.55).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=2.0)
        self.wait(2.0)
        self.play(FadeOut(VGroup(t, s, entrada, pie_entrada, preguntas, nota)),
                  run_time=0.7)

    # -- 3. la tesis ---------------------------------------------------------
    def _la_tesis(self) -> None:
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
