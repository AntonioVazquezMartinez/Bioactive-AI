# Guía de estudio

Para quien tiene que explicar el proyecto a alguien que quiere entender **qué se hizo y por
qué**, y asegurarse de que todo hace sentido. Interna: no se publica en el sitio, como
`roadmap-mlops.md`.

No repite el registro de decisiones, el glosario ni los fundamentos: **los ordena para
estudiarlos** y dice, cuaderno por cuaderno, qué pregunta contesta, qué decisión genera y qué
haría una persona escéptica con él.

## Cómo está organizada

Cuatro capas, de abajo hacia arriba. Una pregunta mal contestada en una capa tira lo que hay
encima, así que se estudian en este orden.

| capa | cuadernos | estado |
|:--|:--|:--|
| **1 · datos, etiquetas y partición** | `01`, `02`, `01b`, `02b` | **escrita**: [`01-datos-y-etiquetas.md`](01-datos-y-etiquetas.md) |
| **2 · modelos y su comparación** | `03`, `03b`, `03c`, `04`, `04b`, `04c` | **escrita**: [`02-modelos-y-comparacion.md`](02-modelos-y-comparacion.md) |
| 3 · el modelo final | `05`, `05b`, `05c` | **sin escribir** |
| 4 · publicabilidad | todos | **sin escribir** |

Lo que cubre cada capa pendiente:

- **Capa 3.** La regla de mejora y por qué no se bajó; por qué el modelo final de la fase 1 no
  es la primera fila de su tabla; por qué el de la fase 2 no es el que gana el promedio; la
  prueba reservada y lo que significa que el AUROC caiga de 0.919 a 0.793.
- **Capa 4.** Qué es nuevo y contra qué literatura; qué se afirma y qué solo se propone; qué
  falta para que algo de esto se publique. Hoy el proyecto es un buen informe técnico, y
  situarlo en la literatura y medir su tesis de la representación (issue #215) son lo que lo
  separa de un artículo.

## Qué hay detrás de cada cifra

Cada cifra de estas guías lleva su cuaderno y su sección, o su corrida en `experimentos/`. Las
que dicen *medido aquí* se ejecutaron al preparar la guía y no salen de ningún cuaderno. **Una
cifra sin una de las dos cosas no debería entrar.**

## Cómo se lee cada tema

```
qué se hizo → por qué → la cifra y dónde está → la pregunta que haría un profesor → qué no sabemos
```

La última parte es la que más importa. Una respuesta que no dice dónde termina lo que se sabe
es la que se cae en la segunda pregunta.

## Lo que esta guía encontró al leer los cuadernos

Al preparar las dos primeras capas se leyeron diez cuadernos enteros y aparecieron
**dieciséis cosas que no cuadran o que no están dichas**, ocho por capa, listadas con su
ubicación al final de cada una. Ninguna cambia una conclusión, con una excepción que sí
importa: la capa 2 (fila 1) encontró que el 05 afirma que su regla de mejora «se fijó antes de
medir» cuando los cuadernos que la crearon, y el propio 05 en su celda de parámetros, dicen
que **no está pre-registrada**. El texto que lo afirma es de la sección 4, redactada como
primer borrador asistido y revisada después, y es el tipo de afirmación que un profesor detecta.

De las ocho de la capa 1, cuatro son cifras o frases que quedaron de una versión anterior (el
18.9 que el propio 01 superó con 28.3, las 171 columnas que hoy son 151, los 63 puntos que la
tabla da como 61.8, y un párrafo del 02 que contradice a otro del mismo cuaderno). Las otras
cuatro son preguntas que un lector atento haría y que hoy no tienen respuesta escrita.

De las ocho de la capa 2, la mayoría son diferencias de criterio que ningún cuaderno declara:
cuatro umbrales distintos para la misma regla, tres denominadores distintos para «cuánto
separa a los modelos», y un «dos de seis» frente a un «solo uno» sobre los mismos datos, que
se midió y resulta ser dos criterios.

**Esa lista es trabajo pendiente**, no una nota: los cuadernos están entregados y cada
corrección es de quien los escribió.
