"""Qué tan bueno es «bueno»: el piso, las tres familias y lo que memorizan.

**Qué cuenta.** El video terminaba sin decir qué dio el modelo de referencia, y
una cifra sola no contesta: hace falta el piso contra el que compararla y la
distancia entre lo que el modelo sabe de memoria y lo que generaliza.

**De dónde salen las cifras.** De `scripts/experimento_rubrica3.py`, promediando
semillas y pliegues sobre `notebooks/datos/rubrica3_piso.csv`,
`rubrica3_ajuste.csv` y `rubrica3_curva.csv`. Van como literales, igual que en
el resto del video: una escena que leyera el CSV al renderizar cambiaría de
contenido sin que el diff lo muestre.

**Todo es validación, nunca la prueba reservada.** No se ha mirado, que es la
condición que la patrocinadora puso al entregar el archivo completo
([2.6](../docs/decisiones.md#d2-6)), y el issue #54 es la guarda que todavía
falta. Si alguna vez se reporta la prueba, es otra escena y lleva su aviso.
"""

from manim import (DOWN, UP, Create, FadeIn, FadeOut, GrowFromEdge, Write,
                   config)

from comun import (AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, Narrada,
                   VERDE, VGroup, cabe, dato, pie, subtitulo, titulo)
from figuras import Ejes

config.background_color = FONDO

# Promedios sobre tres semillas y cinco pliegues. Ver el encabezado.
PISO_MCC = 0.0                       # mayoritaria y proporción constante
FAMILIAS = (("logística", 0.687, 0.739, AZUL),
            ("bosque", 0.698, 0.955, VERDE),
            ("boosting", 0.702, 0.972, NARANJA))
# MCC de validación y de ajuste por fracción del conjunto, promediando las tres
# familias: la forma es la misma en las tres y una curva por familia sería seis
# trazos para decir lo mismo.
CURVA_VALIDACION = ((0.2, 0.648), (0.4, 0.672), (0.6, 0.685), (0.8, 0.688),
                    (1.0, 0.696))
CURVA_AJUSTE = ((0.2, 0.913), (0.4, 0.897), (0.6, 0.892), (0.8, 0.893),
                (1.0, 0.889))


class Resultados(Narrada):
    def construct(self) -> None:
        self._piso()
        self._familias()
        self._memoria()
        self._curva()

    # -- 1. el piso ----------------------------------------------------------
    def _piso(self) -> None:
        self.abrir_tramo(1, compases=3)
        t = titulo("Antes de celebrar, el piso")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        e = Ejes((0, 3), (0, 0.8), ancho=7.0, alto=3.2,
                 etiqueta_y="coeficiente de Matthews",
                 marcas_y=((0.0, "cero"),))
        e.grupo.shift(DOWN * 0.3)
        cabe(e.grupo)
        self.play(Create(e.grupo), run_time=1.0)

        # Barras planas: los tres triviales dan cero. Se dibujan con una altura
        # mínima visible para que se lean como barras y no como ausencia.
        barras = e.histograma([0.012, 0.012, 0.012], GRIS)
        rotulos = VGroup()
        for i, nombre in enumerate(("mayoritaria", "al azar", "proporción"
                                    " fija")):
            r = subtitulo(nombre, 17)
            r.next_to(barras[i], DOWN, buff=0.18)
            rotulos.add(r)
        cabe(barras, rotulos)
        self.play(FadeIn(barras), FadeIn(rotulos, lag_ratio=0.3), run_time=1.2)
        self.respira()

        linea = dato("cero: lo que da no aprender", 22, CREMA)
        linea.to_edge(DOWN, buff=0.75)
        cabe(linea)
        self.play(Write(linea), run_time=1.1)
        self.cerrar_tramo(1)
        self.play(FadeOut(VGroup(t, e.grupo, barras, rotulos, linea)),
                  run_time=0.6)

    # -- 2. las tres familias ------------------------------------------------
    def _familias(self) -> None:
        self.abrir_tramo(2, compases=3)
        t = titulo("Las tres acaban en el mismo sitio")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        e = Ejes((0, 3), (0, 0.8), ancho=7.0, alto=3.2,
                 etiqueta_y="coeficiente de Matthews",
                 marcas_y=((0.0, "cero"),))
        e.grupo.shift(DOWN * 0.3)
        self.play(Create(e.grupo), run_time=0.9)

        # Sin cifras en pantalla a propósito: la idea es que son iguales, y
        # tres decimales casi idénticos la estorban. Ver el guion.
        barras = VGroup()
        rotulos = VGroup()
        for i, (nombre, validacion, _, color) in enumerate(FAMILIAS):
            b = e.histograma([0, 0, 0], color)[i]
            alto_real = e.punto(0, validacion)[1] - e.punto(0, 0)[1]
            b.stretch_to_fit_height(alto_real)
            b.move_to([b.get_center()[0], e.punto(0, validacion / 2)[1], 0])
            r = subtitulo(nombre, 18)
            r.next_to(e.grupo, DOWN, buff=0.12)
            r.set_x(b.get_center()[0])
            barras.add(b)
            rotulos.add(r)
        cabe(barras, rotulos)
        self.play(*[GrowFromEdge(b, DOWN) for b in barras],
                  FadeIn(rotulos, lag_ratio=0.2), run_time=1.6)
        self.respira()

        nota = subtitulo("que coincidan dice que el resultado viene de los"
                         " datos, no del modelo", 20)
        nota.to_edge(DOWN, buff=0.75)
        p = pie("validación agrupada · script experimento_rubrica3.py")
        p.next_to(nota, DOWN, buff=0.16)
        cabe(nota, p)
        self.play(Write(nota), run_time=1.2)
        self.play(FadeIn(p), run_time=0.5)
        self.cerrar_tramo(2)
        self.play(FadeOut(VGroup(t, e.grupo, barras, rotulos, nota, p)),
                  run_time=0.6)

    # -- 3. lo que las separa es cuánto memorizan ----------------------------
    def _memoria(self) -> None:
        self.abrir_tramo(3, compases=3)
        t = titulo("Lo que las separa es cuánto memorizan")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        e = Ejes((0, 3), (0, 1.0), ancho=7.2, alto=3.0,
                 etiqueta_y="coeficiente de Matthews",
                 marcas_y=((0.0, "cero"), (1.0, "perfecto")))
        e.grupo.shift(DOWN * 0.25)
        self.play(Create(e.grupo), run_time=0.9)

        grupos = VGroup()
        for i, (nombre, validacion, ajuste, color) in enumerate(FAMILIAS):
            base = e.punto(i + 0.5, 0)
            par = VGroup()
            for j, (valor, tono, opa) in enumerate(
                    ((ajuste, AZUL_CLARO, 0.45), (validacion, color, 0.85))):
                from manim import Rectangle

                alto = e.punto(0, valor)[1] - e.punto(0, 0)[1]
                b = Rectangle(width=0.7, height=alto, color=tono,
                              fill_opacity=opa, stroke_width=0)
                b.move_to([base[0] + (j - 0.5) * 0.78, base[1] + alto / 2, 0])
                par.add(b)
            r = subtitulo(nombre, 17)
            r.next_to(e.grupo, DOWN, buff=0.12)
            r.set_x(base[0])
            par.add(r)
            grupos.add(par)
        cabe(grupos)
        self.play(FadeIn(grupos, lag_ratio=0.25), run_time=1.5)
        self.respira()

        brechas = VGroup(
            dato("0.05", 26, AZUL), subtitulo("de brecha", 17),
            dato("0.27", 26, NARANJA), subtitulo("cinco veces más", 17))
        brechas[0].next_to(grupos[0], UP, buff=0.25)
        brechas[1].next_to(brechas[0], UP, buff=0.08)
        brechas[2].next_to(grupos[2], UP, buff=0.25)
        brechas[3].next_to(brechas[2], UP, buff=0.08)
        leyenda = subtitulo("claro: lo que vio · oscuro: lo que no", 17)
        leyenda.to_edge(DOWN, buff=0.75)
        cabe(brechas, leyenda)
        self.play(FadeIn(brechas, lag_ratio=0.2), FadeIn(leyenda), run_time=1.3)
        self.cerrar_tramo(3)
        self.play(FadeOut(VGroup(t, e.grupo, grupos, brechas, leyenda)),
                  run_time=0.6)

    # -- 4. la curva de aprendizaje ------------------------------------------
    def _curva(self) -> None:
        self.abrir_tramo(4, compases=3)
        t = titulo("Lo que falta son datos, no modelo")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        e = Ejes((0.2, 1.0), (0.6, 1.0), ancho=7.4, alto=3.0,
                 etiqueta_x="fracción del conjunto de ajuste",
                 etiqueta_y="coeficiente de Matthews",
                 marcas_x=((0.2, "un quinto"), (0.6, "tres quintos"),
                           (1.0, "todo")))
        e.grupo.shift(DOWN * 0.25)
        cabe(e.grupo)
        self.play(Create(e.grupo), run_time=1.0)
        self.respira()

        area = e.area_entre(CURVA_AJUSTE, CURVA_VALIDACION, GRIS, 0.16)
        ajuste = e.curva(CURVA_AJUSTE, AZUL_CLARO)
        validacion = e.curva(CURVA_VALIDACION, VERDE)
        r_aj = subtitulo("lo que sabe de memoria", 17)
        r_aj.next_to(ajuste, UP, buff=0.12).shift(DOWN * 0.05)
        r_val = subtitulo("lo que generaliza", 17)
        r_val.next_to(validacion, DOWN, buff=0.14)
        cabe(area, ajuste, validacion, r_aj, r_val)
        self.play(Create(ajuste), FadeIn(r_aj), run_time=1.0)
        self.play(Create(validacion), FadeIn(r_val), run_time=1.0)
        self.play(FadeIn(area), run_time=0.7)

        cola = dato("sube, y no se ha aplanado", 22, CREMA)
        cola.to_edge(DOWN, buff=0.7)
        cabe(cola)
        self.play(Write(cola), run_time=1.1)
        self.cerrar_tramo(4)
