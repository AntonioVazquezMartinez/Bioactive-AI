# Guion · Por qué la partición no es un detalle

**Duración de la animación:** 37 s (baja calidad; la final puede alargarse si
la locución lo pide — los `wait()` de la escena son el margen de ajuste).

**Voz:** narración en primera persona del plural, como el resto del material
del proyecto. Tono explicativo, sin énfasis de venta.

**Cómo se ajusta:** cada bloque lleva el momento en que entra y el elemento de
la escena con el que tiene que coincidir. Si la locución queda más larga que
el tramo, se alarga el `wait()` correspondiente en `particion.py` y se vuelve
a renderizar; **no se recorta el guion para que quepa**, porque el video
existe para explicar y no para durar poco.

---

## 1 · El conjunto *(0:00 – 0:08)*

> Un conjunto de moléculas no es una bolsa de filas independientes.
> Se parecen entre sí por familias: comparten el andamio, que es el esqueleto
> de anillos sobre el que cuelga todo lo demás.

*Entra con:* el título, y después las cinco familias apareciendo en orden.

---

## 2 · La partición al azar *(0:08 – 0:17)*

> Si repartimos las moléculas al azar entre entrenamiento y evaluación, cada
> familia queda de los dos lados.
>
> Y entonces el modelo ya vio a los análogos casi idénticos de lo que tiene
> que predecir. Para acertar en la caja de la derecha le basta reconocer la
> familia. No necesita entender la química.

*Entra con:* las dos cajas; la segunda frase, cuando se resaltan en rojo las
moléculas repetidas.

---

## 3 · La partición por familia *(0:17 – 0:27)*

> Si en cambio repartimos familias enteras, ninguna se parte. Las familias
> grandes alimentan al modelo; las raras se guardan para evaluarlo.
>
> Ahora la caja de la derecha tiene química que el modelo no vio nunca. Es más
> difícil, y es la pregunta que de verdad importa: ¿sirve con algo nuevo?
>
> Las métricas van a bajar, y eso no es un problema: es que antes estaban
> infladas.

*Entra con:* las moléculas moviéndose en bloque por familia.

---

## 4 · Lo que cuesta *(0:27 – 0:37)*

> La diferencia no es cosmética. Sobre los datos de permeabilidad, con el
> mismo modelo y la misma matriz, agrupar solo por andamio da un AUROC de
> cero punto nueve cinco nueve. Uniendo el andamio al esqueleto de
> conectividad, cero punto nueve tres siete.
>
> Dos punto dos puntos, y la de arriba es la que infla.
>
> Y es un caso suave: lo único que cambia entre esas dos moléculas es la
> disposición espacial. Partir del todo al azar infla entre siete y trece
> puntos.

*Entra con:* la tabla; el remate, con la línea; el cierre, con el pie de
fuente.

---

## Notas para la locución

- **«AUROC»** se lee deletreado, *a-u-roc*, no como palabra.
- Los decimales se leen **«cero punto nueve tres siete»**, que es como se dice en México y lo que la pantalla escribe (`0.937`).
- No hay ninguna cifra en pantalla que la voz no diga, ni al revés. Si una
  cambia, cambian las dos y se vuelve a grabar — por eso el video lleva solo
  tres números.
