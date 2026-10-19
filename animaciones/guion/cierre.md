# Guion · Cierre

**Duración:** 30 s. **Papel en el hilo:** cobra la tesis de la apertura.

---

## 1 · Funciona *(0:00 – 0:07)*

> Con los datos bien mirados, el modelo funciona. Cero punto nueve tres ocho
> de AUROC para la permeabilidad de la barrera, cero punto ocho seis seis para
> la actividad sobre la diana.

---

## 2 · Pero *(0:07 – 0:15)*

> Pero no igual en todas partes.
>
> El mismo modelo, partido por de dónde viene la evidencia. Cincuenta mil
> pares vienen de ChEMBL: cero punto ocho cinco ocho. Mil quinientos son
> mixtos: cero punto seis tres siete. Y dos mil cien vienen solo de las bases
> de productos naturales: cero punto seis uno uno.
>
> Las barras arrancan en cero punto cinco, que es el azar, y llevan su
> intervalo del noventa y cinco por ciento. Los dos de la derecha se solapan:
> no es una pendiente, son dos valores que no se distinguen entre sí.

*Nota visual:* las barras se miden desde 0.5, que es el azar. Desde cero
parecería que 0.611 es «la mitad de bueno», y no es eso lo que dice. Y llevan
su intervalo del 95% porque sin él tres puntos invitan a leer una tendencia
que los datos no sostienen — lo encontró el brainstorm yendo a `experimentos/`.

---

## 3 · Lo que se entrega *(0:15 – 0:30)*

> Lo que el proyecto entrega es una lista de candidatos priorizados, con su
> marca de origen natural, su alerta de promiscuidad y la curva completa en
> vez de un punto de corte.
>
> Y lo que no afirma: que el modelo sirva para productos naturales. Con tres
> dianas comparables, todavía no se puede decir ni que sí ni que no.
>
> «No hay patrón aprendible» es un resultado válido.

---

## Notas

- La última frase es el remate del video entero. Va sola, sin prisa.
- Si alguna cifra cambia con los modelos afinados del Avance 4, esta escena es
  la que hay que volver a grabar. Es el precio de que el cierre diga algo.
- **Las ocho cifras de esta escena salen de
  `experimentos/2026-10-18-artemio-*/metricas.json`**, del AUROC agrupado
  sobre predicciones fuera de pliegue. El promedio por pliegue da otros
  valores (0.863 en vez de 0.866); son dos estimadores y no se mezclan.
