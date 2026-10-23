"""La medida que apunta al revés: dirección buscada contra tipo de ensayo.

**Qué cuenta.** El archivo de actividad trae `diana_efecto_buscado`, que dice en
qué dirección hay que modular cada diana para que sirva como tratamiento, y
`src/data_prep/pares_fase2.py` no menciona `activity_type` ni una vez. En las
dianas donde lo buscado es activar, el 29% de las mediciones son IC50, que mide
potencia de **inhibir**: entran a la mediana del par como si midieran lo mismo.

**De dónde salen las cifras.** De `scripts/medicion_dianas_activacion.py`,
corrida `experimentos/2026-10-22-artemio-2.3-dianas-activacion/`. Están
escritas aquí como literales, igual que el resto del video, porque una escena
que lee un CSV al renderizar cambiaría de contenido sin que el diff lo muestre.
Si la corrida cambia, cambian estas tres líneas y el guion.

**Las dos mitades van juntas.** El tramo 3 cuenta qué se pierde al quitar lo
que contradice la dirección; el 4, qué se pierde al quitar lo que incomoda por
venir de una sola fuente. Por separado cada mitad parece tener salida fácil
—quitar lo raro—, y juntas enseñan que las dos salidas sesgan en sentidos
opuestos. Si alguna vez hay que recortar, se recortan las dos o ninguna.

**Por qué el tramo 5 no lleva números.** Es el que dice que el dato no decide;
una cifra ahí invitaría a pensar lo contrario.
"""

from manim import (DOWN, FadeIn, FadeOut, GrowFromCenter, LEFT, RIGHT, UP,
                   Create, Write, config)

# `ROJO` es `estado.alerta` y está reservado para estados, no para series: un
# IC50 no es un error, es una medición que apunta al otro lado. La dirección
# contraria se dibuja con `NARANJA`, que es la categoría que el proyecto ya usa
# para «lo que va en contra», y así el tramo 1 y el 2 dicen lo mismo con el
# mismo color.
from comun import (CREMA, FONDO, GRIS, NARANJA, Narrada, VERDE, VGroup, cabe,
                   dato, pie, subtitulo, titulo)
from figuras import flecha_direccion, reduccion

config.background_color = FONDO

# La corrida del 22 de octubre. Ver el encabezado.
PARES = 6140
SIN_EVIDENCIA = 832
UNA_SOLA = 752
# El mismo problema por el otro lado: de qué vive la clase negativa de los
# productos naturales. De la misma corrida.
NEGATIVOS_NPASS = 1914
DEPENDEN_DE_AC50 = 1161


class Direccion(Narrada):
    def construct(self) -> None:
        self._dianas()
        self._tipos()
        self._juego()
        self._negativos()
        self._cierre()

    # -- 1. cada diana pide una dirección ------------------------------------
    def _dianas(self) -> None:
        self.abrir_tramo(1, compases=3)
        t = titulo("Una diana pide una dirección")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        self.columnas = VGroup()
        for x, gen, que, hacia, color in (
                (-3.4, "ACHE", "destruye acetilcolina", "inhibirla", NARANJA),
                (3.4, "NFE2L2", "enciende las defensas", "activarlo", VERDE)):
            nombre = dato(gen, 30, CREMA)
            explica = subtitulo(que, 18)
            explica.next_to(nombre, DOWN, buff=0.2)
            bloque = VGroup(nombre, explica)
            bloque.move_to([x, 0.9, 0])
            self.columnas.add(bloque)
        cabe(self.columnas)
        self.play(FadeIn(self.columnas, lag_ratio=0.3), run_time=1.3)
        self.respira()

        self.flechas = VGroup()
        for x, hacia, color, sentido in ((-3.4, "inhibirla", NARANJA, -1),
                                         (3.4, "activarlo", VERDE, 1)):
            f = flecha_direccion([x, -0.4, 0], [x, -0.4 + 1.1 * sentido, 0],
                                 color)
            r = dato(hacia, 22, color)
            r.next_to(f, DOWN if sentido > 0 else UP, buff=0.25)
            self.flechas.add(VGroup(f, r))
        # Las flechas nacen a la misma altura y apuntan en sentidos opuestos:
        # es la imagen entera de la escena en un gesto.
        self.flechas.shift(DOWN * 0.9)
        cabe(self.flechas)
        self.play(*[GrowFromCenter(f) for f in self.flechas], run_time=1.2)

        self.nota = subtitulo("está escrito en una columna que el proyecto no"
                              " mira", 20)
        self.nota.to_edge(DOWN, buff=0.9)
        cabe(self.nota)
        self.play(Write(self.nota), run_time=1.2)
        self.cerrar_tramo(1)
        self.play(FadeOut(VGroup(t, self.columnas, self.flechas, self.nota)),
                  run_time=0.6)

    # -- 2. el tipo de medida también apunta ---------------------------------
    def _tipos(self) -> None:
        self.abrir_tramo(2, compases=3)
        t = titulo("Y el tipo de medida también apunta")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)

        diana = dato("NFE2L2", 26, CREMA)
        diana.move_to([3.2, 0.3, 0])
        busca = subtitulo("se busca activar", 17, )
        busca.next_to(diana, DOWN, buff=0.18)
        compuesto = dato("un compuesto", 22, GRIS)
        compuesto.move_to([-4.2, 0.3, 0])
        cabe(VGroup(diana, busca, compuesto))
        self.play(FadeIn(VGroup(diana, busca, compuesto)), run_time=0.9)
        self.respira()

        medidas = VGroup()
        for y, sigla, que, color in ((1.3, "EC50", "mide cuánto activa", VERDE),
                                     (-0.9, "IC50", "mide cuánto inhibe", NARANJA)):
            f = flecha_direccion([-2.6, y, 0], [1.9, y, 0], color)
            s = dato(sigla, 24, color)
            s.next_to(f, UP, buff=0.14).shift(LEFT * 1.2)
            q = subtitulo(que, 17)
            q.next_to(f, DOWN, buff=0.14).shift(RIGHT * 0.4)
            medidas.add(VGroup(f, s, q))
        cabe(medidas)
        for m in medidas:
            self.play(Create(m[0]), FadeIn(m[1], m[2]), run_time=0.8)
        self.respira()

        proporcion = dato("29 de cada 100 mediciones de esas dianas son IC50",
                          22, NARANJA)
        proporcion.to_edge(DOWN, buff=1.2)
        aviso = subtitulo("y la etiqueta toma la mediana de todas, sin mirar el"
                          " tipo", 19)
        aviso.next_to(proporcion, DOWN, buff=0.22)
        cabe(proporcion, aviso)
        self.play(Write(proporcion), run_time=1.1)
        self.play(FadeIn(aviso), run_time=0.7)
        self.cerrar_tramo(2)
        self.play(FadeOut(VGroup(t, diana, busca, compuesto, medidas,
                                 proporcion, aviso)), run_time=0.6)

    # -- 3. cuánto está en juego ---------------------------------------------
    def _juego(self) -> None:
        self.abrir_tramo(3, compases=3)
        t = titulo("Lo que se mueve no son las etiquetas")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        # La reducción dibuja los pares que se quedan **sin ninguna medición**
        # cuando la que contradice deja de contar: no cambian de clase, se
        # quedan sin evidencia.
        r = reduccion("pares sin evidencia que sobreviva", PARES,
                      SIN_EVIDENCIA, NARANJA, ancho=3.0)
        r.move_to([-3.6, -0.3, 0])
        cabe(r)
        self.play(Create(r[0]), run_time=0.7)
        self.play(GrowFromCenter(r.barra), FadeIn(r[2], r[3]), run_time=1.1)
        self.respira()

        # Y de esos, casi todos son una sola medición: la pregunta no es
        # arbitrar entre réplicas, es qué hacer con un dato suelto.
        partes = VGroup()
        for i, (n, texto, color) in enumerate((
                (UNA_SOLA, "con una sola medición", NARANJA),
                (SIN_EVIDENCIA - UNA_SOLA, "con dos o más", CREMA))):
            cifra = dato(f"{n:,}", 34, color)
            rotulo = subtitulo(texto, 18)
            rotulo.next_to(cifra, DOWN, buff=0.16)
            bloque = VGroup(cifra, rotulo)
            bloque.move_to([3.2, 0.7 - i * 1.7, 0])
            partes.add(bloque)
        cabe(partes)
        self.play(FadeIn(partes[0], shift=DOWN * 0.2), run_time=0.9)
        self.play(FadeIn(partes[1], shift=DOWN * 0.2), run_time=0.7)

        p = pie("medición: scripts/medicion_dianas_activacion.py")
        p.to_edge(DOWN, buff=0.45)
        cabe(p)
        self.play(FadeIn(p), run_time=0.5)
        self.cerrar_tramo(3)
        self.play(FadeOut(VGroup(t, r, partes, p)), run_time=0.6)

    # -- 4. el mismo problema por el otro lado -------------------------------
    def _negativos(self) -> None:
        """De qué vive la clase negativa de los productos naturales.

        Es el espejo del tramo anterior y la razón de que la pregunta no tenga
        una respuesta cómoda. Si se quitan los tipos de ensayo que incomodan,
        los naturales se quedan casi sin negativos, y un modelo sin clase
        negativa en un estrato no mide nada en ese estrato.
        """
        self.abrir_tramo(4, compases=6)
        t = titulo("Y el mismo problema, por el otro lado")
        t.to_edge(UP, buff=0.7)
        cabe(t)
        self.play(Write(t), run_time=1.2)
        self.respira()

        r = reduccion("negativos de los pares que solo tiene NPASS",
                      NEGATIVOS_NPASS, DEPENDEN_DE_AC50, VERDE, ancho=3.2)
        r.move_to([-3.4, -0.2, 0])
        cabe(r)
        self.play(Create(r[0]), run_time=0.7)
        self.respira()
        self.play(GrowFromCenter(r.barra), FadeIn(r[2], r[3]), run_time=1.1)
        self.respira()

        lineas = VGroup(
            subtitulo("dependen de un solo tipo de ensayo: AC50,", 21),
            subtitulo("que en este archivo solo existe en NPASS.", 21),
            subtitulo("Quitarlo por evitar el sesgo de fuente", 21),
            subtitulo("deja a los naturales casi sin clase negativa.", 21),
        ).arrange(DOWN, buff=0.24)
        lineas.move_to([3.1, 0.1, 0])
        cabe(lineas)
        self.play(FadeIn(lineas, lag_ratio=0.3), run_time=1.8)
        self.respira()

        cola = dato("se conserva, y se reporta con y sin esos pares", 21, CREMA)
        cola.to_edge(DOWN, buff=0.9)
        cabe(cola)
        self.play(Write(cola), run_time=1.2)
        self.respira()
        self.cerrar_tramo(4)
        self.play(FadeOut(VGroup(t, r, lineas, cola)), run_time=0.6)

    # -- 5. lo que el dato no decide -----------------------------------------
    def _cierre(self) -> None:
        # Siete compases: es un tramo sin figura, 33 s de voz sobre
        # cuatro líneas de texto. Revelarlas de golpe dejaba quince segundos de
        # pantalla fija, así que entran una a una.
        self.abrir_tramo(5, compases=7)
        t = titulo("Lo que el dato no decide")
        t.to_edge(UP, buff=0.9)
        cabe(t)
        self.play(Write(t), run_time=1.1)
        self.respira()

        lineas = VGroup(
            subtitulo("La columna dice qué modulación se busca como"
                      " tratamiento,", 22),
            subtitulo("no qué hizo el compuesto en el ensayo.", 22),
            subtitulo("Qué cuenta como evidencia en una diana que se quiere"
                      " activar", 22),
            subtitulo("es criterio de quien conoce la biología, no del código.",
                      22),
        ).arrange(DOWN, buff=0.26)
        lineas.move_to([0, -0.2, 0])
        cabe(lineas)
        for linea in lineas:
            self.play(FadeIn(linea, shift=DOWN * 0.12), run_time=0.55)
            self.respira()

        cola = dato("se mide, se escribe, y el etiquetado no cambia", 22, CREMA)
        cola.to_edge(DOWN, buff=1.0)
        cabe(cola)
        self.play(Write(cola), run_time=1.1)
        self.respira()
        self.cerrar_tramo(5)
