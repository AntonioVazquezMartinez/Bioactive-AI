"""Por qué plegar rompe la explicabilidad, y qué cuesta no plegar.

El proyecto exige poder decir **qué subestructura** empuja una predicción. Un
fingerprint plegado no lo permite: la función de dispersión mete fragmentos
distintos en el mismo bit, así que un bit importante no se traduce a una
estructura. Sort & Slice no pliega —ordena por frecuencia y corta—, y por eso
cada columna es una sola subestructura.

Eso se explica mal con palabras y bien con dos cajas y unas flechas.

    manim -qh animaciones/fingerprints.py Fingerprints

Cifras comprobadas contra `data/processed/` y la decisión 1.7.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Create, FadeIn, FadeOut,
                   Rectangle, Scene, VGroup, Write, config)

from comun import (AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, ROJO, VERDE,
                   cabe, dato, pie, subtitulo, titulo)

config.background_color = FONDO


def _bit(color: str = GRIS, lado: float = 0.42) -> Rectangle:
    return Rectangle(width=lado, height=lado, color=color, fill_opacity=0.25,
                     stroke_width=1.2, stroke_color=GRIS)


def _fragmento(etiqueta: str, color: str) -> VGroup:
    caja = Rectangle(width=1.5, height=0.5, color=color, fill_opacity=0.2,
                     stroke_width=2)
    texto = subtitulo(etiqueta, 16).move_to(caja)
    return VGroup(caja, texto)


class Fingerprints(Scene):
    def construct(self) -> None:
        self._la_colision()
        self._ordenar_y_cortar()
        self._lo_que_cuesta()
        self._cierre()

    def _encabezado(self, t: str, s: str) -> VGroup:
        tt = titulo(t).to_edge(UP, buff=0.7)
        ss = subtitulo(s).next_to(tt, DOWN, buff=0.28)
        cabe(tt, ss)
        return VGroup(tt, ss)

    # -- 1. el plegado y su colisión ----------------------------------------
    def _la_colision(self) -> None:
        cab = self._encabezado(
            "Plegar mete dos fragmentos en el mismo bit",
            "y entonces un bit importante ya no se puede dibujar")
        self.play(Write(cab[0]), FadeIn(cab[1]), run_time=1.3)

        # Los fragmentos arriba y los bits abajo: las flechas caen en vertical
        # y se ve en cuál aterriza cada una. Con los fragmentos a un lado, las
        # flechas cruzaban la fila entera y no se leía dónde terminaban.
        fragmentos = VGroup(
            _fragmento("anillo aromático", AZUL),
            _fragmento("grupo nitro", NARANJA),
            _fragmento("amina terciaria", VERDE),
        ).arrange(RIGHT, buff=0.7).shift(UP * 1.15)

        bits = VGroup(*[_bit(lado=0.5) for _ in range(9)])
        bits.arrange(RIGHT, buff=0.14).shift(DOWN * 0.9)
        etiqueta_bits = subtitulo("una fila de 2,048 bits", 17)
        etiqueta_bits.next_to(bits, DOWN, buff=0.3).set_x(0)
        cabe(fragmentos, bits, etiqueta_bits)
        self.play(FadeIn(fragmentos, lag_ratio=0.2), Create(bits),
                  FadeIn(etiqueta_bits), run_time=1.5)
        self.wait(0.5)

        # El primero y el tercero caen en el mismo bit: eso es la colisión.
        destinos = (3, 6, 3)
        self.flechas = []
        for frag, j in zip(fragmentos, destinos):
            destino = bits[j]
            flecha = Arrow(frag.get_bottom(), destino.get_top() + UP * 0.08,
                           color=frag[0].color, stroke_width=3.5, buff=0.1,
                           max_tip_length_to_length_ratio=0.12)
            self.flechas.append(flecha)
            self.play(Create(flecha),
                      destino.animate.set_fill(frag[0].color, opacity=0.75),
                      run_time=0.75)
            self.wait(0.15)
        self.wait(0.5)

        aviso = dato("dos fragmentos distintos, el mismo bit", 24, ROJO)
        aviso.next_to(etiqueta_bits, DOWN, buff=0.5).set_x(0)
        cabe(aviso)
        self.play(bits[3].animate.set_color(ROJO).set_fill(ROJO, opacity=0.8),
                  FadeIn(aviso), run_time=1.0)
        self.wait(0.7)

        nota = subtitulo("Si ese bit pesa en la predicción, no se puede decir\n"
                         "cuál de los dos fragmentos la empujó.", 19)
        nota.next_to(aviso, DOWN, buff=0.3).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=1.8)
        self.wait(1.7)
        # Objetos explícitos y no `self.mobjects`: ese incluye un Mobject
        # plano que VGroup no acepta, y además barrer todo a ciegas esconde
        # qué se está quitando.
        self.play(FadeOut(fragmentos), FadeOut(bits), FadeOut(etiqueta_bits),
                  FadeOut(aviso), FadeOut(nota), FadeOut(cab),
                  *[FadeOut(f) for f in self.flechas], run_time=0.7)

    # -- 2. ordenar y cortar -------------------------------------------------
    def _ordenar_y_cortar(self) -> None:
        cab = self._encabezado(
            "Sort & Slice no pliega: ordena y corta",
            "las subestructuras por frecuencia, y se queda con las primeras")
        self.play(FadeIn(cab), run_time=0.8)

        barras = VGroup()
        alturas = [1.5, 1.32, 1.16, 1.02, 0.9, 0.79, 0.69, 0.6, 0.52, 0.45,
                   0.39, 0.33, 0.28, 0.24, 0.2, 0.17, 0.14, 0.12, 0.1, 0.08]
        for i, h in enumerate(alturas):
            color = VERDE if i < 9 else GRIS
            b = Rectangle(width=0.4, height=h, color=color, fill_opacity=0.75,
                          stroke_width=0)
            barras.add(b)
        barras.arrange(RIGHT, buff=0.08, aligned_edge=DOWN).move_to(DOWN * 0.5)
        eje = subtitulo("subestructuras del entrenamiento, de más a menos"
                        " frecuente", 17)
        eje.next_to(barras, DOWN, buff=0.35)
        cabe(barras, eje)
        self.play(Create(barras, lag_ratio=0.06), FadeIn(eje), run_time=1.8)
        self.wait(0.7)

        corte = dato("corte: las 2,048 más frecuentes", 20, VERDE)
        corte.next_to(barras, UP, buff=0.5)
        cabe(corte)
        self.play(FadeIn(corte), run_time=0.7)
        self.play(VGroup(*barras[9:]).animate.set_opacity(0.18), run_time=0.9)
        self.wait(0.6)

        nota = subtitulo("Cada columna es una sola subestructura, así que un\n"
                         "bit importante se puede dibujar. No hay colisiones.",
                         19)
        nota.next_to(eje, DOWN, buff=0.45).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=1.9)
        self.wait(1.7)
        self.play(FadeOut(VGroup(barras, eje, corte, nota, cab)), run_time=0.7)

    # -- 3. lo que cuesta ----------------------------------------------------
    def _lo_que_cuesta(self) -> None:
        cab = self._encabezado(
            "Pero la cola se corta, y la prueba vive en la cola",
            "el vocabulario se aprende solo con entrenamiento")
        self.play(FadeIn(cab), run_time=0.8)

        filas = VGroup()
        for cifra, motivo, color in (
                ("11,475", "subestructuras distintas hay en entrenamiento", CREMA),
                ("2,048", "caben en el vocabulario: el 18%", VERDE),
                ("84.8%", "de las del entrenamiento quedan cubiertas", AZUL_CLARO),
                ("68%", "de las de la prueba", NARANJA)):
            n = dato(cifra, 28, color)
            m = subtitulo(motivo, 18).next_to(n, RIGHT, buff=0.4)
            filas.add(VGroup(n, m))
        filas.arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to(DOWN * 0.3)
        cabe(filas)
        for f in filas:
            self.play(FadeIn(f, shift=RIGHT * 0.25), run_time=0.55)
        self.wait(0.9)

        nota = subtitulo("La prueba trae los andamios raros, que son justo\n"
                         "los que el corte deja fuera. Y la brecha crece con\n"
                         "el vocabulario: 13.6 puntos con 512, 17.8 con 4,096.",
                         19)
        nota.next_to(filas, DOWN, buff=0.5).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=2.4)
        self.wait(2.0)
        self.play(FadeOut(VGroup(filas, nota, cab)), run_time=0.7)

    # -- 4. cierre -----------------------------------------------------------
    def _cierre(self) -> None:
        cierre = VGroup(
            dato("Se paga cobertura por trazabilidad.", 26, CREMA),
            subtitulo("El proyecto exige poder señalar la subestructura\n"
                      "responsable, así que es el intercambio correcto\n"
                      "— y queda declarado.", 19),
        ).arrange(DOWN, buff=0.45).move_to(DOWN * 0.1)
        cabe(cierre)
        self.play(FadeIn(cierre[0]), run_time=1.0)
        self.play(Write(cierre[1]), run_time=2.0)

        fuente = pie("Decisión 1.7 · notebook 02 · densidad 1.91% contra 2.33%"
                     " del plegado")
        fuente.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(fuente), run_time=0.8)
        self.wait(2.5)
