"""Qué sale del proyecto, y lo que todavía no se puede afirmar.

Cierra el video y cobra la tesis de la apertura. Si las cuatro escenas
técnicas muestran que los datos no son lo que parecen, esta muestra para qué
sirvió mirarlos bien: el modelo funciona sobre ChEMBL y **no se puede afirmar
todavía** que funcione sobre los productos naturales, que son el objeto del
proyecto.

Es un final incómodo a propósito. «No hay patrón aprendible» es un resultado
válido en este proyecto, y decirlo es parte del trabajo.

    manim -qh animaciones/cierre.py Cierre

Cifras del notebook 03 y de las decisiones 2.3 y C.5.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, Flash,
                   Indicate, Line, Rectangle, VGroup, Write, config)

from comun import (AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, Narrada, VERDE,
                   cabe, dato, pie, subtitulo, titulo)

config.background_color = FONDO


class Cierre(Narrada):
    def construct(self) -> None:
        self._funciona()
        self._pero()
        self._el_entregable()

    # -- 1. el modelo funciona ----------------------------------------------
    def _funciona(self) -> None:
        self.abrir_tramo(1)
        t = titulo("Con los datos bien mirados, el modelo funciona")
        s = subtitulo("validación cruzada agrupada por estructura, sin tocar"
                      " la prueba reservada", 21)
        t.to_edge(UP, buff=0.85)
        s.next_to(t, DOWN, buff=0.3).set_x(0)
        cabe(t, s)
        self.play(Write(t), FadeIn(s), run_time=1.5)

        filas = VGroup()
        for cifra, que, color in (
                # Las dos salen de `experimentos/`, del AUROC agrupado sobre
                # las predicciones fuera de pliegue. El promedio por pliegue
                # da 0.863 para la segunda, que es otro estimador: no se
                # mezclan, y el registro usa este.
                ("0.938", "permeabilidad de la barrera", VERDE),
                ("0.866", "actividad sobre la diana", VERDE)):
            n = dato(cifra, 32, color)
            q = subtitulo(que, 20).next_to(n, RIGHT, buff=0.45)
            filas.add(VGroup(n, q))
        filas.arrange(DOWN, buff=0.45, aligned_edge=LEFT).shift(DOWN * 0.3)
        etiqueta = subtitulo("AUROC", 18).next_to(filas, UP, buff=0.35).set_x(0)
        cabe(filas, etiqueta)
        self.play(FadeIn(etiqueta), run_time=0.5)
        for f in filas:
            self.play(FadeIn(f, shift=RIGHT * 0.25), run_time=0.7)
            # Un destello sobre la cifra al decirla: es el gesto que dirige la
            # mirada sin añadir nada que leer.
            self.play(Flash(f[0], color=f[0].color, line_length=0.18,
                            num_lines=10, flash_radius=0.55), run_time=0.6)
        # **Las dos cifras no son del mismo modelo, y hay que decirlo.** El
        # 0.938 es el boosting por histogramas y el 0.866 el bosque aleatorio:
        # cada uno es el de mayor MCC en su fase. Sin el pie, «el modelo» en
        # singular del título y los dos AUROC juntos se leen como una sola
        # canalización sobre las dos tareas.
        fuente = pie("boosting (fase 1) y bosque aleatorio (fase 2), cada uno el"
                     " de mayor MCC en la suya\n"
                     "experimentos/2026-10-18-artemio-*  ·  AUROC fuera de"
                     " pliegue, 3 semillas, agrupado por andamio y esqueleto")
        fuente.to_edge(DOWN, buff=0.3)
        cabe(fuente)
        self.play(FadeIn(fuente), run_time=0.6)
        self.cerrar_tramo(1)
        self.play(FadeOut(fuente), run_time=0.3)
        self.play(FadeOut(VGroup(t, s, filas, etiqueta)), run_time=0.7)

    # -- 2. pero no sobre lo que importa ------------------------------------
    def _pero(self) -> None:
        self.abrir_tramo(2, compases=3)
        t = titulo("Pero no igual en todas partes").to_edge(UP, buff=0.85)
        s = subtitulo("el mismo modelo, partido por de dónde viene la"
                      " evidencia", 21)
        s.next_to(t, DOWN, buff=0.3).set_x(0)
        cabe(t, s)
        self.play(Write(t), FadeIn(s), run_time=1.4)

        barras = VGroup()
        for valor, bajo, alto_ic, etiqueta_txt, color in (
                # Sin los conteos exactos: la voz da el contraste de orden de
                # magnitud —cincuenta mil contra dos mil— que es lo que hay
                # que entender, y un conteo exacto en pantalla que la voz no
                # dice obliga a regrabar si cambia.
                (0.858, 0.850, 0.867, "solo ChEMBL", VERDE),
                (0.637, 0.594, 0.687, "mixtos", AZUL_CLARO),
                (0.611, 0.572, 0.647, "solo NPASS", NARANJA)):
            # La barra se mide desde 0.5, que es el azar: una barra desde cero
            # haría parecer que 0.611 es «la mitad de bueno» que 0.858.
            escala = 6.5
            alto = max(0.08, (valor - 0.5) * escala)
            b = Rectangle(width=1.5, height=alto, color=color, fill_opacity=0.8,
                          stroke_width=0)
            # El intervalo del 95%, porque sin él tres puntos invitan a leer
            # una pendiente. El de mixtos y el de NPASS se solapan casi del
            # todo: no hay tendencia, hay dos valores indistinguibles.
            y0 = b.get_bottom()[1] + (bajo - 0.5) * escala
            y1 = b.get_bottom()[1] + (alto_ic - 0.5) * escala
            x = b.get_center()[0]
            barra_ic = VGroup(
                Line([x, y0, 0], [x, y1, 0], color=CREMA, stroke_width=2.5),
                Line([x - 0.22, y0, 0], [x + 0.22, y0, 0], color=CREMA,
                     stroke_width=2.5),
                Line([x - 0.22, y1, 0], [x + 0.22, y1, 0], color=CREMA,
                     stroke_width=2.5),
            )
            cifra = dato(f"{valor:.3f}", 21, color)
            cifra.next_to(barra_ic, UP, buff=0.18)
            nom = subtitulo(etiqueta_txt, 18).next_to(b, DOWN, buff=0.2)
            barras.add(VGroup(b, barra_ic, cifra, nom))
        barras.arrange(RIGHT, buff=1.0, aligned_edge=DOWN).shift(DOWN * 0.9)
        base = Line(barras.get_left() + LEFT * 0.3,
                    barras.get_right() + RIGHT * 0.3, color=GRIS,
                    stroke_width=1.5)
        base.move_to([barras.get_center()[0], barras[0][0].get_bottom()[1], 0])
        azar = dato("0.5 · el azar", 20, CREMA).next_to(base, LEFT, buff=0.3)
        cabe(barras, base)
        self.play(Create(base), FadeIn(azar), run_time=0.7)
        # Una barra por vez, creciendo desde la base: la voz las nombra en
        # este orden y el intervalo entra después, que es cuando lo menciona.
        for grupo in barras:
            columna, intervalo, cifra, nombre = grupo
            columna.save_state()
            columna.stretch_to_fit_height(0.01, about_edge=DOWN)
            self.play(FadeIn(nombre), run_time=0.3)
            self.play(columna.animate.restore(), run_time=0.9)
            self.play(FadeIn(cifra, shift=UP * 0.15), run_time=0.45)
        self.respira()
        self.play(*[Create(g[1]) for g in barras], run_time=1.1)
        self.respira()
        # Y el gesto que sostiene la lectura honesta: los dos de la derecha,
        # juntos, para que se vea que sus intervalos se tocan.
        self.play(Indicate(barras[1][1], color=CREMA, scale_factor=1.08),
                  Indicate(barras[2][1], color=CREMA, scale_factor=1.08),
                  run_time=1.2)

        nota = dato("Los dos de la derecha no se distinguen entre sí.", 23,
                    CREMA)
        nota.next_to(barras, DOWN, buff=0.55).set_x(0)
        cabe(nota)
        self.play(FadeIn(nota), run_time=1.0)
        fuente2 = pie("bosque aleatorio, fase 2 · AUROC por procedencia sobre"
                      " las predicciones fuera de pliegue\n"
                      "experimentos/2026-10-18-artemio-2.3-baseline-actividad-"
                      "descriptores-diana-10um  ·  intervalos por bootstrap de grupos")
        fuente2.to_edge(DOWN, buff=0.3)
        cabe(fuente2)
        self.play(FadeIn(fuente2), run_time=0.6)
        self.cerrar_tramo(2)
        self.play(FadeOut(fuente2), run_time=0.3)
        self.play(FadeOut(VGroup(t, s, barras, base, azar, nota)), run_time=0.7)

    # -- 3. lo que se entrega ------------------------------------------------
    def _el_entregable(self) -> None:
        self.abrir_tramo(3, compases=3)
        t = titulo("Lo que se entrega, y lo que no se afirma")
        t.to_edge(UP, buff=0.85)
        cabe(t)
        self.play(Write(t), run_time=1.3)

        entrega = VGroup(
            subtitulo("Una lista de candidatos priorizados,", 22),
            subtitulo("con su marca de origen natural y su alerta de"
                      " promiscuidad,", 22),
            subtitulo("y la curva completa en vez de un punto de corte.", 22),
        ).arrange(DOWN, buff=0.22)
        entrega.next_to(t, DOWN, buff=0.6).set_x(0)
        cabe(entrega)
        self.play(FadeIn(entrega, lag_ratio=0.3), run_time=1.8)
        self.respira()

        linea = Line(LEFT * 4.6, RIGHT * 4.6, color=GRIS, stroke_width=1)
        linea.next_to(entrega, DOWN, buff=0.55)
        no = VGroup(
            dato("Lo que no se afirma:", 23, NARANJA),
            subtitulo("que el modelo sirva para productos naturales.\n"
                      "Con tres dianas comparables, todavía no se puede"
                      " decir\nni que sí ni que no.", 21),
        ).arrange(DOWN, buff=0.3)
        no.next_to(linea, DOWN, buff=0.45).set_x(0)
        cabe(linea, no)
        self.play(Create(linea), run_time=0.6)
        self.play(FadeIn(no[0]), run_time=0.7)
        self.play(Write(no[1]), run_time=2.4)
        self.respira()

        # La tarjeta final va **dentro** del tramo 3, porque la voz dice esa
        # frase ahí. Puesta después de `cerrar_tramo`, el remate del video
        # entero sonaba sobre la pantalla anterior.
        self.play(FadeOut(VGroup(t, entrega, linea, no)), run_time=0.7)
        final = titulo("«No hay patrón aprendible»\nes un resultado válido.", 32)
        final.set_color(CREMA)
        cabe(final)
        self.play(FadeIn(final, scale=0.95), run_time=1.4)
        self.cerrar_tramo(3)

        fuente = pie("Bioactive AI · Equipo 7 ·"
                     " antoniovazquezmartinez.github.io/Bioactive-AI")
        fuente.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(fuente), run_time=0.9)
        self.wait(2.2)
