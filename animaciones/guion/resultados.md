# Guion · Qué tan bueno es «bueno»

**Duración de la animación:** 62 s (baja calidad).

**Por qué existe.** El video terminaba sin decir qué dio el modelo de
referencia, y la pregunta que un espectador trae es justo esa. Pero una cifra
sola no contesta nada: hace falta el piso contra el que compararla y la
distancia entre lo que el modelo sabe de memoria y lo que generaliza. Las tres
cosas son gráficas, y en una tabla no se ven.

---

## 1 · El piso *(0:00 – 0:13)*

> Antes de celebrar un número hay que saber qué da no hacer nada.
>
> Tres modelos que no aprenden: responder siempre la clase mayoritaria,
> responder al azar con la proporción de la clase, y una proporción fija.
>
> Los tres dan cero de coeficiente de Matthews. Esa es la línea: cualquier
> cifra por encima de cero es información, y cualquiera por debajo es ruido.

*Entra con:* las tres barras, planas, y la línea del cero.

---

## 2 · Las tres familias acaban en el mismo sitio *(0:13 – 0:28)*

> Contra ese piso corren tres familias: una regresión logística, un bosque
> aleatorio y un boosting por gradiente, con la misma matriz y la misma
> partición agrupada.
>
> Y acaban en el mismo sitio. Entre la mejor y la peor hay una diferencia que
> cabe dentro del ruido entre semillas.
>
> Que las tres coincidan no es decepcionante: es lo que dice que el resultado
> viene de los datos y no del modelo.

*Entra con:* las tres barras creciendo a la vez, y la banda que las cubre.

---

## 3 · Lo que las separa es cuánto memorizan *(0:28 – 0:45)*

> Donde sí se distinguen es en lo que saben de memoria.
>
> La logística acierta casi lo mismo sobre los datos que vio y sobre los que
> no: su brecha es de cero punto cero cinco.
>
> El bosque y el boosting aciertan casi perfecto sobre lo que vieron y caen al
> mismo sitio que la logística al salir. Su brecha es de cero punto dos siete,
> cinco veces más.
>
> Memorizar el conjunto de ajuste no es un defecto en sí: lo es creerse esa
> cifra. Por eso la que se reporta es siempre la de validación.

*Entra con:* la pareja de barras de cada familia, y la brecha marcada entre las
dos.

---

## 4 · Y todavía no se acaba *(0:45 – 1:02)*

> La última pregunta es si el problema es el modelo o los datos. Se contesta
> entrenando con una fracción del conjunto y subiéndola.
>
> Con la quinta parte, la validación da cero punto seis cinco. Con todo,
> cero punto siete cero. Sigue subiendo, y no se ha aplanado.
>
> Mientras tanto, lo que el modelo sabe de memoria se queda donde estaba desde
> el principio.
>
> Eso dice que lo que falta son datos, no modelo. Y es la respuesta más útil
> que puede dar un modelo de referencia, porque dice en qué gastar el esfuerzo
> siguiente.

*Entra con:* las dos curvas, y el área entre ellas que no se cierra.

---

## Notas para la locución

- **«coeficiente de Matthews»** se dice completo la primera vez; después, «la
  cifra» o «el coeficiente».
- **«boosting»** se deja en inglés, como lo dice el equipo.
- Los decimales se leen **dígito a dígito**, como en el resto del video:
  «cero punto cero cinco», «cero punto dos siete», «cero punto seis cinco».
  No es capricho: `tests/test_animaciones.py` reconoce esa forma, y es la que
  usan las otras escenas («cero punto nueve tres seis»).
- **Las cifras de esta escena son de validación, nunca de la prueba
  reservada.** La prueba no se ha mirado y no se mira aquí: es la condición que
  la patrocinadora puso. Si alguna vez se reporta, es otra escena y lleva su
  aviso.
- El tramo 2 no pone números en pantalla a propósito: la idea es que las tres
  barras son iguales, y tres decimales casi idénticos la estorban en lugar de
  sostenerla.
