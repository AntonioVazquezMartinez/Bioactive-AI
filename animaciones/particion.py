"""Por qué partir al azar infla el resultado, y partir por andamio no.

Es el concepto más contraintuitivo del proyecto y el que peor se explica
estático: una tabla de dos filas dice que hay 2.2 puntos de diferencia, pero no
deja *ver* por qué. Aquí se ve: las mismas moléculas, las mismas dos cajas, y
la diferencia está solo en qué cae de qué lado.

    manim -qh animaciones/particion.py Particion

Las cifras de la última escena salen de la decisión 1.2 del registro, medidas
en el notebook 03. Cualquier otra cifra se queda fuera del video a propósito:
un número dentro de un `.mp4` no se puede corregir en un PR.
"""

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, FadeIn, FadeOut,
                   Indicate, Line, Rectangle, Scene, VGroup, Write, config)

from comun import (AZUL, AZUL_CLARO, CREMA, FONDO, GRIS, NARANJA, ROJO, VERDE,
                   dato, pie, subtitulo, titulo)

config.background_color = FONDO

# Cinco familias químicas, cada una con sus análogos. Los tamaños imitan la
# forma real del conjunto: pocas familias grandes y una cola de familias de uno.
FAMILIAS = [("A", 6, AZUL), ("B", 5, AZUL_CLARO), ("C", 4, VERDE),
            ("D", 2, NARANJA), ("E", 1, GRIS)]


def _molecula(color: str, radio: float = 0.17) -> Circle:
    c = Circle(radius=radio, color=color, fill_opacity=0.85, stroke_width=1.5)
    return c


class Particion(Scene):
    def construct(self) -> None:
        self._presentar()
        self._al_azar()
        self._por_andamio()
        self._la_cifra()

    # -- 1. el conjunto, agrupado por familia -------------------------------
    def _presentar(self) -> None:
        t = titulo("Un conjunto de moléculas no es una bolsa de filas")
        s = subtitulo("Se parecen entre sí por familias: comparten el andamio,"
                      " el esqueleto de anillos")
        t.to_edge(UP, buff=0.8)
        s.next_to(t, DOWN, buff=0.3)
        self.play(Write(t), run_time=1.2)
        self.play(FadeIn(s, shift=DOWN * 0.2), run_time=0.8)
        self.wait(0.6)

        # Las filas y sus etiquetas se guardan por separado: si las etiquetas
        # viven dentro del mismo grupo, el FadeOut del final las vuelve a
        # añadir a la escena y terminan flotando sobre la tabla de cifras.
        self.grupos, self.etiquetas = VGroup(), VGroup()
        columnas = VGroup()
        for nombre, n, color in FAMILIAS:
            fila = VGroup(*[_molecula(color) for _ in range(n)])
            fila.arrange(RIGHT, buff=0.12)
            etiqueta = subtitulo(f"familia {nombre}", 16)
            etiqueta.next_to(fila, DOWN, buff=0.15)
            self.grupos.add(fila)
            self.etiquetas.add(etiqueta)
            columnas.add(VGroup(fila, etiqueta))
        columnas.arrange(RIGHT, buff=0.55, aligned_edge=DOWN)
        columnas.move_to(DOWN * 0.3)

        self.play(FadeIn(columnas, lag_ratio=0.1), run_time=1.6)
        self.wait(1.2)
        self.titulo_actual = t
        self.sub_actual = s

    def _cambiar_titulo(self, nuevo: str, nuevo_sub: str) -> None:
        """Con fundido y no con `Transform`.

        Transformar un texto en otro de largo distinto interpola letra a letra
        y deja medio segundo de revoltijo ilegible. Se vio al revisar los
        fotogramas del primer render.
        """
        t = titulo(nuevo).move_to(self.titulo_actual)
        s = subtitulo(nuevo_sub).next_to(t, DOWN, buff=0.3)
        self.play(FadeOut(self.titulo_actual), FadeOut(self.sub_actual),
                  run_time=0.35)
        self.play(FadeIn(t), FadeIn(s), run_time=0.5)
        self.titulo_actual, self.sub_actual = t, s

    def _cajas(self) -> tuple[VGroup, VGroup]:
        izq = Rectangle(width=5.4, height=2.6, color=VERDE, stroke_width=2)
        der = Rectangle(width=5.4, height=2.6, color=NARANJA, stroke_width=2)
        izq.to_edge(LEFT, buff=0.7).shift(DOWN * 0.6)
        der.to_edge(RIGHT, buff=0.7).shift(DOWN * 0.6)
        e1 = subtitulo("entrenamiento", 18).next_to(izq, UP, buff=0.15)
        e2 = subtitulo("evaluación", 18).next_to(der, UP, buff=0.15)
        return VGroup(izq, e1), VGroup(der, e2)

    # -- 2. la partición al azar --------------------------------------------
    def _al_azar(self) -> None:
        self._cambiar_titulo("Si se parten al azar…",
                             "cada familia queda repartida entre las dos cajas")
        # Las etiquetas se van con las moléculas: si se quedan, acaban
        # flotando sobre las cajas y sobre la tabla del final.
        izq, der = self._cajas()
        self.play(Create(izq), Create(der), FadeOut(self.etiquetas), run_time=0.9)

        rng = np.random.default_rng(7)
        destinos, moleculas = [], []
        for fila in self.grupos:
            for mol in fila:
                moleculas.append(mol)
                destinos.append(izq[0] if rng.random() < 0.75 else der[0])

        animaciones = []
        for mol, caja in zip(moleculas, destinos):
            objetivo = caja.get_center() + np.array([
                rng.uniform(-2.2, 2.2), rng.uniform(-0.9, 0.9), 0.0])
            animaciones.append(mol.animate.move_to(objetivo))
        self.play(*animaciones, lag_ratio=0.02, run_time=2.4)
        self.wait(0.4)

        aviso = dato("La misma familia está de los dos lados", 24, ROJO)
        aviso.next_to(der[0], DOWN, buff=0.45)
        gemelas = [m for m, c in zip(moleculas, destinos) if c is der[0]][:3]
        self.play(FadeIn(aviso), *[Indicate(m, color=ROJO, scale_factor=1.6)
                                   for m in gemelas], run_time=1.4)
        self.wait(0.8)

        explicacion = subtitulo(
            "El modelo ya vio a sus análogos casi idénticos.\n"
            "Para acertar en la caja de la derecha le basta\n"
            "reconocer la familia, no entender la química.", 20)
        explicacion.next_to(aviso, DOWN, buff=0.3)
        self.play(Write(explicacion), run_time=2.0)
        self.wait(1.6)
        self.play(FadeOut(aviso), FadeOut(explicacion), run_time=0.6)
        self.izq, self.der = izq, der
        self.moleculas = moleculas

    # -- 3. la partición por andamio ----------------------------------------
    def _por_andamio(self) -> None:
        self._cambiar_titulo("Si se parten por familia…",
                             "cada familia cae entera de un solo lado")
        rng = np.random.default_rng(3)
        animaciones, i = [], 0
        # Las familias grandes alimentan el modelo; las raras evalúan.
        for (_, n, _), fila in zip(FAMILIAS, self.grupos):
            caja = self.izq[0] if n >= 4 else self.der[0]
            for mol in fila:
                objetivo = caja.get_center() + np.array([
                    rng.uniform(-2.2, 2.2), rng.uniform(-0.9, 0.9), 0.0])
                animaciones.append(mol.animate.move_to(objetivo))
                i += 1
        self.play(*animaciones, lag_ratio=0.02, run_time=2.4)
        self.wait(0.5)

        bien = dato("Ninguna familia se reparte", 24, VERDE)
        bien.next_to(self.der[0], DOWN, buff=0.45)
        explicacion = subtitulo(
            "Ahora la caja de la derecha tiene química\nque el modelo no vio"
            " nunca.\nEs más difícil, y es la pregunta que importa.", 20)
        explicacion.next_to(bien, DOWN, buff=0.3)
        self.play(FadeIn(bien), run_time=0.8)
        self.play(Write(explicacion), run_time=2.2)
        self.wait(2.0)
        self.play(FadeOut(bien), FadeOut(explicacion),
                  FadeOut(self.izq), FadeOut(self.der),
                  *[FadeOut(m) for m in self.moleculas],
                  FadeOut(self.grupos), run_time=0.9)

    # -- 4. lo que cuesta confundirse ---------------------------------------
    def _la_cifra(self) -> None:
        self._cambiar_titulo(
            "La diferencia no es cosmética",
            "medido sobre la fase 1, con el mismo modelo y la misma matriz")

        # Los rótulos dicen **exactamente** lo que se midió. La escena ilustra
        # el caso extremo —partir al azar— pero las dos cifras comparan algo
        # más fino: agrupar solo por andamio contra unirlo al esqueleto de
        # conectividad. Una partición al azar infla mucho más, entre 7 y 13
        # puntos, y eso viene de la literatura y no de una corrida nuestra.
        bloque = VGroup()
        for rotulo, valor, color in (
                ("agrupando solo por andamio", "AUROC 0.959", ROJO),
                ("agrupando por andamio y esqueleto", "AUROC 0.937", VERDE)):
            r = dato(rotulo, 24, color)
            v = dato(valor, 26, color)
            v.next_to(r, RIGHT, buff=0.8)
            bloque.add(VGroup(r, v))
        bloque.arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(DOWN * 0.2)
        self.play(FadeIn(bloque, lag_ratio=0.2), run_time=1.4)
        self.wait(0.8)

        linea = Line(bloque.get_left() + DOWN * 1.1,
                     bloque.get_right() + DOWN * 1.1, color=GRIS, stroke_width=1)
        remate = dato("2.2 puntos, y la de arriba es la que infla", 24, CREMA)
        remate.next_to(linea, DOWN, buff=0.35)
        self.play(Create(linea), FadeIn(remate), run_time=1.2)
        self.wait(1.0)

        cierre = subtitulo(
            "Y es un caso suave: dos moléculas idénticas salvo la\n"
            "disposición espacial. Partir del todo al azar infla\n"
            "entre 7 y 13 puntos.", 20)
        cierre.next_to(remate, DOWN, buff=0.35)
        self.play(Write(cierre), run_time=2.0)

        fuente = pie("Decisión 1.2 · notebook 03_Baseline · bosque aleatorio,"
                     " validación cruzada agrupada, 3 semillas")
        fuente.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(fuente), run_time=0.8)
        self.wait(2.5)
