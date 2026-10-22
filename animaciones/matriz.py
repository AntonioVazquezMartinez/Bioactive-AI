"""De una molécula a una fila, y de muchas filas a la matriz.

Es la costura que faltaba. El linaje muestra columnas cayendo y los
fingerprints explican los bits, pero entre una cosa y otra nunca se ve **cómo
una molécula se convierte en números**, ni que los tres bloques —descriptores,
subestructuras y derivadas— viven en la misma fila. Sin eso, los pasos se ven
aislados: cada uno se entiende y el conjunto no.

    manim -qh animaciones/matriz.py Matriz

Cifras de `data/processed/` y de las decisiones 1.3 y 1.7.

**Todavía no está en el video.** Falta `guion/matriz.md`, falta añadirla a
`ESCENAS` en `voz.py` y en `sonorizar.py` y a `ORDEN` en `ensamblar.py`, y
falta renderizarla y grabarla. Hasta entonces la escena existe pero no se
ensambla, que es a propósito: media escena en el video sería peor que ninguna.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, Indicate,
                   Line, Rectangle, Transform, VGroup, Write, config)

from comun import (AZUL, AZUL_CLARO, FONDO, GRIS, NARANJA, Narrada,
                   VERDE, cabe, dato, matriz, pie, subtitulo, titulo)

config.background_color = FONDO

# Los tres bloques y su ancho relativo en el dibujo. Las proporciones reales
# son 203, 2048 y 3; dibujadas así, el fingerprint se comería la pantalla y no
# se vería nada, así que se comprime y se dice el número.
#
# Las cifras son las del notebook 02: `bbb_descriptores.parquet` trae los 203
# utilizables, `bbb_morgan2048.npz` los 2,048 bits y la sección 6 añade las tres
# derivadas. Juntarlos en una sola fila es la representación
# `descriptores+morgan` de `src/models/tareas.py`, que es la que mejor sale en
# la prueba de humo; las otras usan un bloque a la vez.
# Los tres colores categóricos en su orden, no una tinta de apoyo en medio: los
# bloques son tres identidades y el de en medio llevaba el gris de los trazos
# secundarios, que es el mismo error de categoría que la paleta vieja tenía.
BLOQUES = [
    ("descriptores", 203, 3.0, AZUL),
    ("subestructuras", 2048, 4.4, NARANJA),
    ("derivadas", 3, 0.9, VERDE),
]


class Matriz(Narrada):
    def construct(self) -> None:
        self._una_molecula()
        self._una_fila()
        self._la_matriz()

    def _encabezado(self, t: str, s: str) -> VGroup:
        tt = titulo(t).to_edge(UP, buff=0.8)
        ss = subtitulo(s).next_to(tt, DOWN, buff=0.28).set_x(0)
        cabe(tt, ss)
        return VGroup(tt, ss)

    # -- 1. la molécula entra como texto ------------------------------------
    def _una_molecula(self) -> None:
        # Esta escena se montó sin un solo `respira()`, así que los tres
        # tramos juntaban todo el silencio al final: 29 s de imagen fija en el
        # segundo, con la voz hablando encima. Lo midió la guarda de
        # `TOPE_CONGELADO`, no una revisión de fotogramas.
        self.abrir_tramo(1, compases=3)
        cab = self._encabezado("Todo empieza con una cadena de texto",
                               "el SMILES es la única entrada del sistema")
        self.play(Write(cab[0]), FadeIn(cab[1]), run_time=1.4)

        smiles = dato("CC(=O)Oc1ccccc1C(=O)O", 30, AZUL_CLARO)
        smiles.move_to(UP * 0.6)
        cabe(smiles)
        self.play(FadeIn(smiles), run_time=1.0)
        self.respira()

        # El trozo que es el anillo, resaltado: la cadena no es opaca, tiene
        # partes que significan algo.
        anillo = smiles[7:15]
        marca = subtitulo("este trozo es un anillo aromático", 19)
        marca.next_to(smiles, DOWN, buff=0.7).set_x(0)
        cabe(marca)
        self.play(Indicate(anillo, color=NARANJA, scale_factor=1.25),
                  FadeIn(marca), run_time=1.3)
        self.respira()
        self.play(FadeOut(marca), run_time=0.4)
        self.smiles = smiles
        self.cab = cab
        self.cerrar_tramo(1)

    # -- 2. la fila: tres bloques, uno al lado del otro ---------------------
    def _una_fila(self) -> None:
        self.abrir_tramo(2, compases=len(BLOQUES) + 2)
        nueva = self._encabezado(
            "Y se convierte en una fila de números",
            "tres bloques distintos, pegados uno al lado del otro")
        self.play(FadeOut(self.cab), run_time=0.3)
        self.play(FadeIn(nueva), run_time=0.5)
        self.cab = nueva

        self.play(self.smiles.animate.scale(0.62).to_edge(LEFT, buff=0.7)
                  .shift(UP * 0.9), run_time=1.0)
        self.respira()

        fila, rotulos = VGroup(), VGroup()
        for nombre, cuantas, ancho, color in BLOQUES:
            celdas = VGroup(*[
                Rectangle(width=ancho / max(6, int(ancho * 4)), height=0.42,
                          color=color, fill_opacity=0.6, stroke_width=0.7,
                          stroke_color=FONDO)
                for _ in range(max(6, int(ancho * 4)))])
            celdas.arrange(RIGHT, buff=0)
            etiqueta = subtitulo(f"{nombre}\n{cuantas:,}", 16)
            etiqueta.next_to(celdas, DOWN, buff=0.22)
            fila.add(celdas)
            rotulos.add(etiqueta)
        fila.arrange(RIGHT, buff=0.22).move_to(DOWN * 0.3)
        for celdas, etiqueta in zip(fila, rotulos):
            etiqueta.next_to(celdas, DOWN, buff=0.22)
        cabe(fila, rotulos)

        # Cada bloque sale de la molécula: la flecha es la que une los pasos
        # que antes se veían sueltos.
        for celdas, etiqueta in zip(fila, rotulos):
            flecha = Line(self.smiles.get_bottom() + DOWN * 0.1,
                          celdas.get_top() + UP * 0.08, color=GRIS,
                          stroke_width=1.5)
            self.play(Create(flecha), run_time=0.45)
            self.play(Create(celdas, lag_ratio=0.05), FadeIn(etiqueta),
                      run_time=0.8)
            self.play(FadeOut(flecha), run_time=0.25)
            self.respira()

        nota = subtitulo("Son 2,254 números para una sola molécula, y los tres"
                         " bloques\nmiden cosas distintas: propiedades, trozos"
                         " y combinaciones.", 20)
        nota.to_edge(DOWN, buff=0.8).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=2.0)
        self.respira()
        self.fila, self.rotulos, self.nota = fila, rotulos, nota
        self.cerrar_tramo(2)

    # -- 3. muchas filas: la matriz -----------------------------------------
    def _la_matriz(self) -> None:
        self.abrir_tramo(3, compases=4)
        nueva = self._encabezado("Una fila por molécula, y eso es la matriz",
                                 "lo que el modelo ve, y lo único que ve")
        self.play(FadeOut(self.cab), FadeOut(self.nota), run_time=0.3)
        self.play(FadeIn(nueva), run_time=0.5)

        # La fila se encoge y se repite: el gesto que convierte un caso en un
        # conjunto.
        rej = matriz(9, 26, ancho=9.2, alto=3.0, color=AZUL)
        rej.move_to(DOWN * 0.35)
        cabe(rej)
        self.play(FadeOut(self.rotulos), FadeOut(self.smiles), run_time=0.4)
        self.play(Transform(self.fila, rej[0]), run_time=0.8)
        self.play(Create(rej, lag_ratio=0.015), run_time=2.0)
        self.play(FadeOut(self.fila), run_time=0.2)
        self.respira()

        lado = subtitulo("una fila\npor molécula", 17)
        lado.next_to(rej, LEFT, buff=0.3)
        arriba = subtitulo("las columnas de los tres bloques", 17)
        arriba.next_to(rej, UP, buff=0.25).set_x(0)
        cabe(lado, arriba)
        self.play(FadeIn(lado), FadeIn(arriba), run_time=0.8)
        self.respira()

        # Y el remate que ata esta escena con las dos siguientes.
        self.play(Indicate(VGroup(*rej[:7]), color=AZUL, scale_factor=1.02),
                  run_time=0.9)
        nota = subtitulo("De aquí en adelante, todo lo que sigue es quitarle\n"
                         "columnas a esta matriz, o filas — y decir por qué.",
                         20)
        nota.to_edge(DOWN, buff=0.75).set_x(0)
        cabe(nota)
        self.play(Write(nota), run_time=1.9)
        self.respira()

        fuente = pie("Decisiones 1.3 y 1.7 · notebook 02 · 7,805 moléculas"
                     " en la fase 1")
        fuente.to_edge(DOWN, buff=0.3)
        cabe(fuente)
        self.play(FadeIn(fuente), run_time=0.7)
        self.cerrar_tramo(3)
        self.wait(1.2)
