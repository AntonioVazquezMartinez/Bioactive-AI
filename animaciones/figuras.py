"""Primitivas de gráfica para las escenas, con la guarda de cuadro por dentro.

**Por qué existe.** La primera versión del video contaba casi todos sus datos
con texto apareciendo en pantalla: las cuatro cifras de cobertura eran cuatro
números, el tamizaje único era un subtítulo. Manim sirve justo para lo
contrario, y lo que faltaba no era voluntad sino piezas: cada escena que quería
un eje tenía que dibujarlo a mano, y dibujarlo a mano es donde aparecen los
defectos de composición que `cabe` detecta demasiado tarde.

Aquí viven los ejes, las curvas, el área entre dos, el histograma, el abanico,
la reducción y la columna naciendo. Cada constructora **comprueba su propio
encaje** antes de devolver, así que un eje demasiado ancho falla al construirse
y no al mirar el fotograma.

**Sin LaTeX, como el resto del video.** No se usa `Axes` de Manim porque sus
coordenadas pasan por `MathTex`; los ejes de aquí son dos líneas y texto Pango,
que es lo que `comun.py` ya impone.

**Las coordenadas de datos no se calculan a mano en las escenas.** `Ejes` las
traduce con `punto(x, y)`: una escena dice «el 84.8 por ciento con 2048
columnas» y no «3.1 unidades a la derecha y 1.8 arriba». Cuando una cifra
cambia, cambia el dato y no la geometría, que es lo mismo que `orden.py` hace
con el orden de las escenas.
"""

from __future__ import annotations

from manim import DOWN, LEFT, UP, Dot, Line, Polygon, Rectangle, VMobject

from comun import (ALTO, ANCHO, AZUL, CREMA, GRIS, REJILLA, VGroup, cabe,
                   dato, subtitulo)

# Grosores: trazo fino para los datos, más fino todavía para el eje, que es
# apoyo y no dato. Son los de la guía de visualización del proyecto.
TRAZO_DATO = 3.0
TRAZO_EJE = 1.6
TRAZO_REJILLA = 0.8


class Ejes:
    """Dos ejes y la traducción de coordenadas de datos a coordenadas de cuadro.

    `rango_x` y `rango_y` son los extremos de los **datos**; `ancho` y `alto`,
    el tamaño en pantalla. `punto(x, y)` devuelve la posición de ese dato, de
    modo que las escenas hablen en las unidades de su figura.

    Las marcas van como `((valor, "rótulo"), …)`, con el rótulo escrito a mano
    —ver el comentario de abajo: de eso depende que la prueba de «ninguna cifra
    sin voz» siga viendo lo que hay en pantalla.

    El grupo se construye centrado en el origen. Si la escena lo mueve, le toca
    volver a llamar a `cabe`: aquí solo se comprueba que el tamaño quepa.
    """

    def __init__(self, rango_x: tuple[float, float],
                 rango_y: tuple[float, float], ancho: float = 8.0,
                 alto: float = 4.0, etiqueta_x: str = "",
                 etiqueta_y: str = "", marcas_x: tuple = (),
                 marcas_y: tuple = ()) -> None:
        if rango_x[1] <= rango_x[0] or rango_y[1] <= rango_y[0]:
            raise ValueError(f"rangos vacíos o invertidos: {rango_x}, {rango_y}")
        self.rango_x, self.rango_y = rango_x, rango_y
        self.ancho, self.alto = ancho, alto

        eje_x = Line([0, 0, 0], [ancho, 0, 0], color=REJILLA,
                     stroke_width=TRAZO_EJE)
        eje_y = Line([0, 0, 0], [0, alto, 0], color=REJILLA,
                     stroke_width=TRAZO_EJE)
        self.grupo = VGroup(eje_x, eje_y)
        # El origen del dibujo queda en el (0,0) del grupo antes de centrarlo,
        # así que `punto` trabaja en ese sistema y el desplazamiento final se
        # aplica a todo el grupo por igual.
        self._origen = [0.0, 0.0, 0.0]

        # **Cada marca llega como `(valor, "rótulo")`, con el rótulo escrito.**
        # No es ceremonia: `tests/test_animaciones.py` garantiza que ninguna
        # cifra aparezca en pantalla sin que la voz la diga, y lo hace leyendo
        # las **cadenas literales** de la escena. Si estos ejes formatearan el
        # número ellos mismos, el rótulo saldría en el video sin existir en el
        # archivo, y esa prueba dejaría de ver justo lo que vigila. Escribir el
        # rótulo cuesta dos comillas y mantiene la garantía.
        self.marcas = VGroup()
        for x, rotulo in marcas_x:
            p = self._bruto(x, rango_y[0])
            marca = Line(p, [p[0], p[1] - 0.12, 0], color=REJILLA,
                         stroke_width=TRAZO_EJE)
            r = subtitulo(rotulo, 16)
            r.next_to(marca, DOWN, buff=0.1)
            self.marcas.add(marca, r)
        for y, rotulo in marcas_y:
            p = self._bruto(rango_x[0], y)
            marca = Line(p, [p[0] - 0.12, p[1], 0], color=REJILLA,
                         stroke_width=TRAZO_EJE)
            r = subtitulo(rotulo, 16)
            r.next_to(marca, LEFT, buff=0.1)
            self.marcas.add(marca, r)
        self.grupo.add(self.marcas)

        self.rotulos = VGroup()
        if etiqueta_x:
            r = subtitulo(etiqueta_x, 18)
            r.next_to(self.grupo, DOWN, buff=0.22)
            self.rotulos.add(r)
        if etiqueta_y:
            r = subtitulo(etiqueta_y, 18)
            r.rotate(90 * 3.141592653589793 / 180)
            r.next_to(self.grupo, LEFT, buff=0.22)
            self.rotulos.add(r)
        self.grupo.add(self.rotulos)

        self._centrar()
        if ancho > ANCHO - 2 or alto > ALTO - 2:
            raise ValueError(
                f"los ejes miden {ancho}×{alto} y no dejan sitio para título ni"
                f" pie en un cuadro de {ANCHO:.1f}×{ALTO:.1f}")
        cabe(self.grupo)

    def _bruto(self, x: float, y: float) -> list[float]:
        """La posición del dato antes de centrar el grupo."""
        fx = (x - self.rango_x[0]) / (self.rango_x[1] - self.rango_x[0])
        fy = (y - self.rango_y[0]) / (self.rango_y[1] - self.rango_y[0])
        return [fx * self.ancho, fy * self.alto, 0.0]

    def _centrar(self) -> None:
        antes = self.grupo.get_center().copy()
        self.grupo.move_to([0, 0, 0])
        self._desplazamiento = self.grupo.get_center() - antes

    def punto(self, x: float, y: float) -> list[float]:
        """Dónde cae el dato `(x, y)` en el cuadro, ya centrado el grupo."""
        p = self._bruto(x, y)
        d = self._desplazamiento
        return [p[0] + d[0], p[1] + d[1], 0.0]

    def curva(self, puntos, color: str = AZUL, trazo: float = TRAZO_DATO):
        """Una polilínea sobre estos ejes, en coordenadas de datos."""
        if len(puntos) < 2:
            raise ValueError("una curva necesita al menos dos puntos")
        c = VMobject(color=color, stroke_width=trazo)
        c.set_points_as_corners([self.punto(x, y) for x, y in puntos])
        return c

    def area_entre(self, arriba, abajo, color: str = AZUL,
                   opacidad: float = 0.18):
        """El área encerrada entre dos series, que es la brecha dibujada.

        Es la pieza que faltaba para contar la cobertura del vocabulario: la
        brecha entre entrenamiento y prueba **crece**, y eso en cuatro números
        no se ve. Como área, se ve.
        """
        if len(arriba) < 2 or len(abajo) < 2:
            raise ValueError("el área necesita dos series de dos puntos o más")
        vertices = ([self.punto(x, y) for x, y in arriba]
                    + [self.punto(x, y) for x, y in reversed(abajo)])
        return Polygon(*vertices, color=color, fill_opacity=opacidad,
                       stroke_width=0)

    def marca_en(self, x: float, y: float, color: str = CREMA,
                 radio: float = 0.06):
        return Dot(self.punto(x, y), radius=radio, color=color)

    def histograma(self, alturas, color: str = AZUL, hueco: float = 0.06,
                   opacidad: float = 0.75):
        """Barras sobre el eje x, una por valor de `alturas`.

        El hueco de 2 px entre barras no es estética: sin él dos barras
        contiguas del mismo color se leen como una sola.
        """
        if not alturas:
            raise ValueError("un histograma necesita al menos una barra")
        barras = VGroup()
        paso = (self.rango_x[1] - self.rango_x[0]) / len(alturas)
        for i, h in enumerate(alturas):
            x0 = self.rango_x[0] + i * paso
            izq, der = self.punto(x0, self.rango_y[0]), self.punto(
                x0 + paso, self.rango_y[0])
            ancho = max(0.02, (der[0] - izq[0]) - hueco)
            arriba = self.punto(x0, h)
            alto = max(0.01, arriba[1] - izq[1])
            b = Rectangle(width=ancho, height=alto, color=color,
                          fill_opacity=opacidad, stroke_width=0)
            b.move_to([(izq[0] + der[0]) / 2, izq[1] + alto / 2, 0])
            barras.add(b)
        return barras


def abanico(centro, radios: int, color: str = AZUL, largo: float = 1.5,
            etiquetas: tuple = (), desde: float = 150.0, hasta: float = 30.0):
    """Un punto del que salen `radios` líneas: un compuesto y sus dianas.

    Es la figura de la **promiscuidad**, que el cierre nombraba sin mostrar:
    un compuesto con diez dianas medidas se dibuja con diez radios, y al lado
    uno con una. La comparación se ve sin decir un número.
    """
    if radios < 1:
        raise ValueError("un abanico necesita al menos un radio")
    import math

    g = VGroup(Dot(centro, radius=0.08, color=color))
    paso = (hasta - desde) / max(1, radios - 1) if radios > 1 else 0.0
    for i in range(radios):
        a = math.radians(desde + i * paso)
        fin = [centro[0] + largo * math.cos(a),
               centro[1] + largo * math.sin(a), 0]
        g.add(Line(centro, fin, color=color, stroke_width=1.8))
        if i < len(etiquetas):
            r = subtitulo(etiquetas[i], 15)
            r.move_to([fin[0] + 0.45 * math.cos(a), fin[1] + 0.2 * math.sin(a), 0])
            g.add(r)
    cabe(g)
    return g


def reduccion(nombre: str, de: int, a: int, color: str = AZUL,
              ancho: float = 2.4) -> VGroup:
    """Una columna que se encoge: «de `de` grupos a `a`».

    Sirve para poner dos criterios de agrupación uno al lado del otro y ver
    que uno parte más fino que el otro. En texto eran dos pares de números.
    """
    if de < a or a < 1:
        raise ValueError(f"reducción imposible: de {de} a {a}")
    alto_max = 2.4
    g = VGroup()
    fuera = Rectangle(width=ancho, height=alto_max, color=REJILLA,
                      stroke_width=TRAZO_REJILLA, fill_opacity=0)
    dentro = Rectangle(width=ancho, height=alto_max * a / de, color=color,
                       fill_opacity=0.5, stroke_width=0)
    dentro.align_to(fuera, DOWN)
    r = subtitulo(nombre, 17)
    r.next_to(fuera, UP, buff=0.18)
    cifra = dato(f"{a:,}".replace(",", ","), 24, color)
    cifra.next_to(fuera, DOWN, buff=0.18)
    g.add(fuera, dentro, r, cifra)
    g.cifra = cifra
    g.barra = dentro
    cabe(g)
    return g


def columna_naciendo(alto: float = 2.6, ancho: float = 0.28, filas: int = 8,
                     color: str = AZUL) -> VGroup:
    """Una columna de celdas, para añadirla a una matriz ya dibujada.

    `matriz` en `comun.py` sabe quitar columnas y no añadirlas, y las tres
    características derivadas son columnas que **se añaden**. Sin esto, la
    escena de la matriz solo podía contarlo con palabras.
    """
    ch = alto / filas
    col = VGroup()
    for i in range(filas):
        c = Rectangle(width=ancho, height=ch, color=color, fill_opacity=0.55,
                      stroke_width=0.6, stroke_color=REJILLA)
        c.move_to([0, -i * ch, 0])
        col.add(c)
    col.move_to([0, 0, 0])
    return col


def flecha_direccion(inicio, fin, color: str = GRIS, grosor: float = 2.0):
    """Una flecha recta y fina, sin punta desproporcionada.

    `Arrow` de Manim escala la punta con la longitud y en trazos cortos se come
    la línea. Aquí la punta es fija.
    """
    from manim import Arrow

    return Arrow(inicio, fin, color=color, stroke_width=grosor,
                 max_tip_length_to_length_ratio=0.12, buff=0)


__all__ = ["Ejes", "abanico", "reduccion", "columna_naciendo",
           "flecha_direccion", "TRAZO_DATO", "TRAZO_EJE"]
