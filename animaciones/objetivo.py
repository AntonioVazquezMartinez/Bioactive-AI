"""Cómo se pasa de un montón de mediciones a una fila con un objetivo.

**Qué cuenta.** La pieza central de la fase 2, y la que el video no tenía: la
unidad es el par compuesto-diana y no la medición, la agregación no es obvia, y
lo que se guarda es el **intervalo** y no la clase. Sin esto, un espectador
entiende las piezas sueltas y no la construcción.

**De dónde salen las cifras.** De `src/data_prep/pares_fase2.py` aplicado al
archivo de la patrocinadora, que es lo que corre
`scripts/construir_pares_fase2.py`. Van como literales, igual que en el resto
del video.

**El eje es el mismo de la escena del intervalo**, que es la que enseña a
leerlo: potencia, con la concentración bajando hacia la derecha. Esta escena
repite la fila de concentraciones a propósito — es la pista que hace falta cada
vez que aparece el eje, no una sola vez en el video.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, Flash,
                   GrowFromCenter, Line, Write, config)

from comun import (AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, Narrada,
                   ROJO, VERDE, VGroup, cabe, dato, pie, separados, subtitulo,
                   titulo)
from figuras import Ejes

config.background_color = FONDO

# Del archivo de la patrocinadora, con las reglas de `pares_fase2.py`.
PARES = "70,384"
CON_VARIAS = "15,153"
DISCREPAN_UN_LOG = "3,222"
SOLO_COTAS = "12,552"
SIN_DECIDIR = "2,648"
EN_CONFLICTO = "1,126"

# Potencia: 6 − log10(µM). El corte de 10 µM cae en 5.0.
CORTE = 5.0


def _eje_de_potencia(ancho: float = 8.4) -> Ejes:
    """El eje de la escena del intervalo, con su fila de concentraciones."""
    e = Ejes((3.0, 8.0), (0.0, 1.0), ancho=ancho, alto=0.001,
             etiqueta_x="potencia  ·  6 − log₁₀ de la concentración en µM")
    return e


class Objetivo(Narrada):
    def construct(self) -> None:
        self._la_unidad()
        self._la_mediana()
        self._las_cotas()
        self._el_intervalo()
        self._el_conflicto()

    def _recta(self, y: float = 0.0, ancho: float = 8.4) -> VGroup:
        """Una recta de potencia con su lectura en concentración debajo.

        Se redibuja en cada tramo en lugar de guardarse una sola: los tramos
        limpian la pantalla entre sí, y arrastrar un objeto vivo entre actos es
        justo lo que hacía que `cerrar_tramo` se llamara desde el sitio
        equivocado en las primeras versiones de estas escenas.
        """
        recta = Line([-ancho / 2, y, 0], [ancho / 2, y, 0], color=GRIS,
                     stroke_width=2)
        g = VGroup(recta)
        for potencia, rotulo in ((4.0, "100 µM"), (5.0, "10 µM"),
                                 (6.0, "1 µM")):
            x = self._x(potencia, ancho)
            marca = Line([x, y, 0], [x, y - 0.12, 0], color=GRIS,
                         stroke_width=1.4)
            r = subtitulo(rotulo, 15)
            r.next_to(marca, DOWN, buff=0.08)
            g.add(marca, r)
        g.recta = recta
        return g

    @staticmethod
    def _x(potencia: float, ancho: float = 8.4) -> float:
        """La posición de una potencia sobre la recta, de 3.0 a 8.0."""
        return (potencia - 3.0) / 5.0 * ancho - ancho / 2

    # -- 1. la unidad es el par ----------------------------------------------
    def _la_unidad(self) -> None:
        self.abrir_tramo(1, compases=3)
        t = titulo("El modelo predice sobre pares, no sobre mediciones")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.2)
        self.respira()

        mediciones = VGroup()
        # Sin valores de ejemplo: la regla 3 pide que la voz diga toda cifra
        # en pantalla, y aquí los números serían inventados. Lo que importa es
        # que son cuatro ensayos distintos del mismo par, no cuánto dieron.
        for i, texto in enumerate(("IC50, un laboratorio",
                                   "IC50, otro laboratorio", "Ki",
                                   "una cota « > »")):
            m = subtitulo(texto, 19)
            m.move_to([-3.6, 1.6 - i * 0.52, 0])
            mediciones.add(m)
        par = dato("un compuesto  ×  una diana", 24, CREMA)
        par.move_to([3.0, 0.3, 0])
        marco = subtitulo("una fila", 17)
        marco.next_to(par, DOWN, buff=0.18)
        cabe(mediciones, par, marco)
        self.play(FadeIn(mediciones, lag_ratio=0.2), run_time=1.2)
        self.play(FadeIn(VGroup(par, marco), shift=LEFT * 0.3), run_time=0.9)
        self.respira()

        cifra = dato(f"{CON_VARIAS} de {PARES} pares traen más de una medición",
                     22, AZUL)
        cifra.to_edge(DOWN, buff=1.0)
        nota = subtitulo("la pregunta no es cuál medición es buena, sino qué"
                         " número representa a todas", 19)
        nota.next_to(cifra, DOWN, buff=0.2)
        cabe(cifra, nota)
        self.play(Write(cifra), run_time=1.2)
        self.play(FadeIn(nota), run_time=0.8)
        self.cerrar_tramo(1)
        self.play(FadeOut(VGroup(t, mediciones, par, marco, cifra, nota)),
                  run_time=0.6)

    # -- 2. con exactas, la mediana ------------------------------------------
    def _la_mediana(self) -> None:
        self.abrir_tramo(2, compases=4)
        t = titulo("Con números exactos, la mediana")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)

        recta = self._recta(y=0.4)
        cabe(recta)
        self.play(Create(recta.recta), FadeIn(recta[1:]), run_time=1.0)
        self.respira()

        from manim import Dot

        valores = (5.4, 6.1, 6.3, 6.5, 7.4)
        puntos = VGroup(*[Dot([self._x(v), 0.4, 0], radius=0.09, color=AZUL)
                          for v in valores])
        self.play(FadeIn(puntos, lag_ratio=0.2), run_time=1.0)
        self.respira()

        mediana = Line([self._x(6.3), 0.95, 0], [self._x(6.3), -0.15, 0],
                       color=VERDE, stroke_width=3)
        r_med = dato("mediana", 22, VERDE)
        r_med.next_to(mediana, UP, buff=0.12)
        maximo = Line([self._x(7.4), 0.95, 0], [self._x(7.4), -0.15, 0],
                      color=NARANJA, stroke_width=2)
        r_max = subtitulo("el más potente: premia al ensayo más generoso", 17)
        r_max.next_to(maximo, UP, buff=0.12).shift(LEFT * 1.4)
        cabe(mediana, r_med, maximo, r_max)
        self.play(Create(mediana), FadeIn(r_med), run_time=0.9)
        self.play(Create(maximo), FadeIn(r_max), run_time=0.9)
        self.play(maximo.animate.set_opacity(0.25),
                  r_max.animate.set_opacity(0.35), run_time=0.6)
        self.respira()

        cifra = dato(f"en {DISCREPAN_UN_LOG} pares, el valor más alto y el más"
                     " bajo se separan más de un orden de magnitud", 20, CREMA)
        cifra.to_edge(DOWN, buff=1.0)
        nota = subtitulo("la mediana no arregla la discrepancia: la absorbe, y"
                         " la deja declarada aparte", 19)
        nota.next_to(cifra, DOWN, buff=0.2)
        cabe(cifra, nota)
        self.play(Write(cifra), run_time=1.3)
        self.play(FadeIn(nota), run_time=0.8)
        self.cerrar_tramo(2)
        self.play(FadeOut(VGroup(t, recta, puntos, mediana, r_med, maximo,
                                 r_max, cifra, nota)), run_time=0.6)

    # -- 3. sin exactas, las cotas se cruzan ---------------------------------
    def _las_cotas(self) -> None:
        self.abrir_tramo(3, compases=4)
        t = titulo("Sin números exactos, las cotas se cruzan")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)

        recta = self._recta(y=0.4)
        cabe(recta)
        self.play(Create(recta.recta), FadeIn(recta[1:]), run_time=1.0)
        self.respira()

        # Un «> 10 µM» acota la potencia **por arriba**: no llega a 5.0.
        superior = Line([self._x(5.0), 0.4, 0], [self._x(3.0), 0.4, 0],
                        color=NARANJA, stroke_width=5)
        r_sup = subtitulo("« > 10 µM »  ·  no llega hasta aquí", 18)
        r_sup.next_to(superior, UP, buff=0.3)
        cabe(superior, r_sup)
        self.play(Create(superior), FadeIn(r_sup), run_time=1.0)
        self.respira()

        # Un «< 100 µM» acota por abajo: pasa de 4.0.
        inferior = Line([self._x(4.0), 0.4, 0], [self._x(8.0), 0.4, 0],
                        color=AZUL_CLARO, stroke_width=5)
        r_inf = subtitulo("« < 100 µM »  ·  lo pasa", 18)
        r_inf.next_to(inferior, DOWN, buff=0.75)
        cabe(inferior, r_inf)
        self.play(Create(inferior), FadeIn(r_inf), run_time=1.0)
        self.respira()

        tramo = Line([self._x(4.0), 0.4, 0], [self._x(5.0), 0.4, 0],
                     color=VERDE, stroke_width=8)
        r_tramo = dato("ahí dentro está la potencia", 21, VERDE)
        r_tramo.next_to(tramo, UP, buff=0.95)
        cifra = subtitulo(f"{SOLO_COTAS} pares viven solo de cotas", 19)
        cifra.to_edge(DOWN, buff=1.0)
        cabe(tramo, r_tramo, cifra)
        self.play(GrowFromCenter(tramo), FadeIn(r_tramo), run_time=1.0)
        self.play(FadeIn(cifra), run_time=0.7)
        self.cerrar_tramo(3)
        self.play(FadeOut(VGroup(t, recta, superior, r_sup, inferior, r_inf,
                                 tramo, r_tramo, cifra)), run_time=0.6)

    # -- 4. lo que se guarda es el intervalo ---------------------------------
    def _el_intervalo(self) -> None:
        self.abrir_tramo(4, compases=4)
        t = titulo("Se guarda el intervalo, no la etiqueta")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)

        recta = self._recta(y=1.5)
        cabe(recta)
        self.play(Create(recta.recta), FadeIn(recta[1:]), run_time=0.9)

        # La línea del corte empieza **debajo** de la fila de concentraciones:
        # arrancándola en la recta atravesaba el rótulo «10 µM», que es justo el
        # que explica dónde cae el corte. Lo vio `separados`, no yo.
        corte = Line([self._x(CORTE), 1.0, 0], [self._x(CORTE), -2.3, 0],
                     color=CREMA, stroke_width=2)
        r_corte = subtitulo("corte: 10 µM", 17)
        r_corte.next_to(corte, DOWN, buff=0.12)
        cabe(corte, r_corte)
        for rotulo in recta[1:]:
            separados(corte, rotulo)
        self.play(Create(corte), FadeIn(r_corte), run_time=0.9)
        self.respira()

        casos = VGroup()
        for i, (desde, hasta, etiqueta, color) in enumerate((
                (6.0, 7.2, "activo", VERDE),
                (3.4, 4.6, "inactivo", NARANJA),
                (4.4, 6.2, "sin decidir", GRIS))):
            y = 0.6 - i * 0.95
            barra = Line([self._x(desde), y, 0], [self._x(hasta), y, 0],
                         color=color, stroke_width=7)
            r = dato(etiqueta, 20, color)
            r.next_to(barra, RIGHT, buff=0.3)
            casos.add(VGroup(barra, r))
        cabe(casos)
        for c in casos:
            self.play(GrowFromCenter(c[0]), FadeIn(c[1]), run_time=0.65)
        self.respira()

        cifra = dato(f"{SIN_DECIDIR} pares que el corte atraviesa: se declaran,"
                     " no se inventan", 21, CREMA)
        cifra.to_edge(DOWN, buff=0.95)
        nota = subtitulo("mover el corte a 1 µM es volver a leer, no"
                         " reconstruir nada", 19)
        nota.next_to(cifra, DOWN, buff=0.2)
        cabe(cifra, nota)
        self.play(Write(cifra), run_time=1.2)
        self.play(FadeIn(nota), run_time=0.8)
        self.cerrar_tramo(4)
        self.play(FadeOut(VGroup(t, recta, corte, r_corte, casos, cifra,
                                 nota)), run_time=0.6)

    # -- 5. el conflicto se marca --------------------------------------------
    def _el_conflicto(self) -> None:
        self.abrir_tramo(5, compases=3)
        t = titulo("Y cuando la evidencia se contradice, se marca")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.2)

        recta = self._recta(y=0.8)
        cabe(recta)
        self.play(Create(recta.recta), FadeIn(recta[1:]), run_time=0.9)
        self.respira()

        from manim import Dot

        cota = Line([self._x(5.0), 0.8, 0], [self._x(3.0), 0.8, 0],
                    color=NARANJA, stroke_width=5)
        r_cota = subtitulo("una cota dice: no llega hasta aquí", 18)
        r_cota.next_to(cota, UP, buff=0.35)
        punto = Dot([self._x(6.8), 0.8, 0], radius=0.1, color=AZUL)
        r_punto = subtitulo("y una exacta cae aquí", 18)
        r_punto.next_to(punto, DOWN, buff=0.75)
        cabe(cota, r_cota, punto, r_punto)
        self.play(Create(cota), FadeIn(r_cota), run_time=0.9)
        self.play(FadeIn(punto, scale=0.5), FadeIn(r_punto), run_time=0.8)
        self.play(Flash(punto, color=ROJO, line_length=0.2, num_lines=10),
                  run_time=0.6)
        self.respira()

        cifra = dato(f"{EN_CONFLICTO} pares", 30, ROJO)
        cifra.move_to([0, -1.2, 0])
        marca = subtitulo("se marcan, no se tiran", 20)
        marca.next_to(cifra, DOWN, buff=0.2)
        cabe(cifra, marca)
        self.play(Write(cifra), FadeIn(marca), run_time=1.1)

        cierre = subtitulo("tirarlos sería una decisión del modelado"
                           " disfrazada de limpieza de datos", 20)
        cierre.to_edge(DOWN, buff=0.9)
        p = pie("regla: src/data_prep/pares_fase2.py")
        p.next_to(cierre, DOWN, buff=0.18)
        cabe(cierre, p)
        self.play(Write(cierre), run_time=1.3)
        self.play(FadeIn(p), run_time=0.5)
        self.cerrar_tramo(5)
