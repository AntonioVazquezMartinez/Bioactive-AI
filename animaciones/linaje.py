"""Del archivo a la matriz: qué filas se pierden, qué columnas caen y por qué.

Es la escena que el diagrama de linaje de `datos-contenido.md` no puede dar.
Un mermaid muestra el **grafo** —qué archivo alimenta a cuál— y eso lo hace
mejor que un video, porque se edita en un PR. Lo que no puede mostrar es una
matriz encogiéndose: que de 217 columnas lleguen 201, y por qué cae cada una.

    manim -qh animaciones/linaje.py Linaje

Todas las cifras salen de `data/processed/` y de la salida de
`scripts/construir_pares_fase2.py`; están comprobadas contra los parquet, no
copiadas de la prosa.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Create, FadeIn, Flash, FadeOut, VGroup, Write, config)

from comun import (Narrada, AZUL, AZUL_CLARO, CREMA, FONDO, NARANJA, ROJO, VERDE,
                   cabe, dato, matriz, pie, subtitulo, titulo)

config.background_color = FONDO

# El embudo de la fase 2, de `scripts/cifras_etiqueta_fase2.py`.
EMBUDO = [
    ("202,647", "mediciones en el archivo", CREMA),
    ("110,723", "en las cinco categorías ratificadas", AZUL_CLARO),
    ("106,645", "con diana y estructura calculable", AZUL_CLARO),
    ("106,464", "con unidad convertible a molar", AZUL_CLARO),
    ("70,384", "pares compuesto-diana", VERDE),
]

# Las columnas que no llegan, y por qué. De `limpiar_descriptores`.
CAIDAS = [
    (3, "constantes", "no distinguen nada"),
    (12, "con huecos", "scikit-learn no las toma sin imputar"),
    (1, "Ipc", "llega a 10⁴¹ y desborda float32"),
]


class Linaje(Narrada):
    def construct(self) -> None:
        self._embudo()
        self._columnas()
        self._particion()
        self._cierre()

    def _encabezado(self, t: str, s: str) -> VGroup:
        tt = titulo(t)
        ss = subtitulo(s)
        tt.to_edge(UP, buff=0.7)
        ss.next_to(tt, DOWN, buff=0.28)
        cabe(tt, ss)
        return VGroup(tt, ss)

    # -- 1. las filas: de mediciones a pares --------------------------------
    def _embudo(self) -> None:
        # Siete compases: el encabezado, las cinco cifras una por una —que es
        # lo que el guion pide— y la nota del final.
        self.abrir_tramo(1, compases=7)
        cab = self._encabezado(
            "El archivo trae mediciones, no compuestos",
            "la unidad del modelo —el par compuesto-diana— hay que construirla")
        self.play(Write(cab[0]), FadeIn(cab[1]), run_time=1.4)
        self.respira()

        filas = VGroup()
        for cifra, motivo, color in EMBUDO:
            n = dato(cifra, 30, color)
            m = subtitulo(motivo, 19)
            m.next_to(n, RIGHT, buff=0.4)
            filas.add(VGroup(n, m))
        filas.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        filas.move_to(DOWN * 0.4)
        cabe(filas)

        for fila in filas:
            self.play(FadeIn(fila, shift=RIGHT * 0.3), run_time=0.55)
            # Un destello sobre la cifra al decirla: dirige la mirada sin
            # añadir nada que leer.
            self.play(Flash(fila[0], color=fila[0].color, line_length=0.14,
                            num_lines=8, flash_radius=0.42), run_time=0.45)
            self.respira()

        # El 29,730 es del archivo entero y solo 5,922 llegan hasta este punto
        # del embudo: las demás ya se habían ido por no estar en las cinco
        # categorías. Decir el primero aquí hacía pensar que el embudo quitaba
        # 29,730. Y la campaña es una, pero se reparte en veinte ensayos.
        nota = subtitulo("Y las declaradas inactivas por texto quedan fuera:"
                         " 5,922 de las que\nllegan hasta aquí, 29,730 en todo"
                         " el archivo. Son una sola campaña\nde tamizaje: 772"
                         " compuestos, veinte ensayos.", 19)
        nota.next_to(filas, DOWN, buff=0.5)
        cabe(nota)
        self.play(Write(nota), run_time=1.8)
        self.cerrar_tramo(1)
        self.wait(1.8)
        self.play(FadeOut(filas), FadeOut(nota), FadeOut(cab), run_time=0.7)

    # -- 2. las columnas: la matriz encogiéndose ----------------------------
    def _columnas(self) -> None:
        # La rejilla, una por cada caída —el `respira()` va dentro del bucle—,
        # el cambio de rótulo y el relleno final.
        self.abrir_tramo(2, compases=len(CAIDAS) + 3)
        cab = self._encabezado(
            "De 217 descriptores llegan 201",
            "RDKit los calcula todos; no todos sirven para un modelo")
        self.play(FadeIn(cab), run_time=0.8)

        # 64 columnas y no 24: lo que cae son 16 de 217, el 7.4%, y el dibujo
        # quitaba 5 de 24, el 21% — tres veces más. Quien leyera «217 columnas»
        # y viera irse un quinto inferiría unas 45 bajas. Con 64, las mismas 5
        # columnas son el 7.8% y el dibujo dice lo que dicen sus rótulos.
        rej = matriz(6, 64, ancho=9.0, alto=2.4, color=AZUL)
        rej.move_to(DOWN * 0.3)
        rotulo = dato("217 columnas", 22, CREMA)
        rotulo.next_to(rej, UP, buff=0.35)
        cabe(rej, rotulo)
        self.play(Create(rej, lag_ratio=0.02), FadeIn(rotulo), run_time=1.8)
        self.respira()

        # Cada motivo tiñe sus columnas y se las lleva, en proporción entre sí
        # (3, 12 y 1) y sobre el total (16 de 217).
        # Tras cada corte, lo que queda se recompone y se recentra: si no, las
        # columnas desaparecen y la matriz parece del mismo tamaño. Lo que
        # tiene que verse es que mengua.
        pos, restante = 0, VGroup(*rej)
        for cuantas, nombre, porque in CAIDAS:
            cols = max(1, round(cuantas / 16 * 5))
            objetivo = VGroup(*rej[pos:pos + cols])
            pos += cols
            etiqueta = dato(f"{cuantas}  {nombre}", 22, ROJO)
            detalle = subtitulo(porque, 18)
            etiqueta.next_to(rej, DOWN, buff=0.75)
            detalle.next_to(etiqueta, DOWN, buff=0.18)
            cabe(etiqueta, detalle)
            self.play(objetivo.animate.set_color(ROJO), FadeIn(etiqueta),
                      FadeIn(detalle), run_time=0.8)
            self.respira()
            restante = VGroup(*rej[pos:])
            self.play(FadeOut(objetivo, shift=DOWN * 1.2),
                      FadeOut(etiqueta), FadeOut(detalle),
                      restante.animate.move_to(DOWN * 0.3), run_time=0.8)

        nuevo_rotulo = dato("201 columnas", 22, VERDE).move_to(rotulo)
        self.play(restante.animate.set_color(VERDE),
                  FadeOut(rotulo), FadeIn(nuevo_rotulo), run_time=1.0)
        self.respira()
        quedan = restante

        nota = subtitulo("Son dos menos que las 203 de la fase 1, y no es otro"
                         " criterio:\nes el mismo filtro sobre otras moléculas.",
                         19)
        nota.next_to(quedan, DOWN, buff=0.7)
        cabe(nota)
        self.play(Write(nota), run_time=1.8)
        self.cerrar_tramo(2)
        self.wait(1.8)
        self.play(FadeOut(quedan), FadeOut(nuevo_rotulo), FadeOut(nota),
                  FadeOut(cab), run_time=0.7)

    # -- 3. la partición ----------------------------------------------------
    def _particion(self) -> None:
        self.abrir_tramo(3, compases=5)
        cab = self._encabezado(
            "Y las filas se parten antes de mirar nada",
            "agrupando por estructura, con una prueba que el modelo nunca ve")
        self.play(FadeIn(cab), run_time=0.8)

        bloques = VGroup()
        # Los porcentajes y no los conteos: la voz dice «setenta, diez,
        # veinte» y no dice 49,425. Una cifra en pantalla que la voz no dice
        # obliga a regrabar si cambia, así que no se pone.
        for n, nombre, frac, color in (
                ("70%", "entrenamiento", 0.70, VERDE),
                ("10%", "validación", 0.10, AZUL_CLARO),
                ("20%", "prueba", 0.20, NARANJA)):
            col = matriz(5, max(2, round(frac * 20)), ancho=9.0 * frac,
                         alto=1.9, color=color)
            cifra = dato(n, 20, color)
            etiqueta = subtitulo(nombre, 17)
            cifra.next_to(col, UP, buff=0.22)
            etiqueta.next_to(col, DOWN, buff=0.22)
            bloques.add(VGroup(col, cifra, etiqueta))
        bloques.arrange(RIGHT, buff=0.4)
        bloques.move_to(DOWN * 0.3)
        cabe(bloques)
        # Un bloque por vez y no los tres de golpe: la voz los nombra uno a uno
        # —«setenta, diez, veinte»— y entrando juntos sobraban casi nueve
        # segundos de imagen fija al final del tramo.
        for bloque in bloques:
            self.play(FadeIn(bloque, lag_ratio=0.2), run_time=0.7)
            self.respira()

        nota = subtitulo("La prueba es el 20% y no se mira hasta el final."
                         "\nEs la condición que puso al entregar el archivo.", 19)
        nota.next_to(bloques, DOWN, buff=0.6)
        cabe(nota)
        self.play(Write(nota), run_time=1.8)
        self.respira()
        self.cerrar_tramo(3)
        self.wait(1.8)
        self.play(FadeOut(bloques), FadeOut(nota), FadeOut(cab), run_time=0.7)

    # -- 4. el cierre --------------------------------------------------------
    def _cierre(self) -> None:
        self.abrir_tramo(4, compases=2)
        linea1 = dato("Cada paso quita filas o columnas,", 26, CREMA)
        linea2 = dato("y cada uno dice por qué.", 26, CREMA)
        cierre = VGroup(linea1, linea2).arrange(DOWN, buff=0.3)
        sub = subtitulo("El linaje completo, archivo por archivo, está en la"
                        " documentación del proyecto.", 19)
        sub.next_to(cierre, DOWN, buff=0.5)
        bloque = VGroup(cierre, sub).move_to(DOWN * 0.1)
        cabe(bloque)
        self.play(FadeIn(cierre, lag_ratio=0.3), run_time=1.3)
        self.play(Write(sub), run_time=1.5)

        fuente = pie("Cifras de data/processed/ · construir_pares_fase2.py ·"
                     " decisiones 2.1, 2.3 y 2.7")
        fuente.to_edge(DOWN, buff=0.3)
        cabe(fuente)
        self.play(FadeIn(fuente), run_time=0.8)
        self.respira()

        self.cerrar_tramo(4)