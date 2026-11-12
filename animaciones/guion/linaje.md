# Guion · Del archivo a la matriz

**Duración de la animación:** 41 s (baja calidad).

**Por qué existe, y qué no hace.** El diagrama de linaje de
`datos-contenido.md` muestra el **grafo** —qué archivo alimenta a cuál— y lo
hace mejor que un video, porque se edita en un PR. Lo que un diagrama no puede
mostrar es una matriz encogiéndose. Esta escena hace solo eso: qué filas se
pierden, qué columnas caen y por qué.

---

## 1 · El embudo de filas *(0:00 – 0:14)*

> El archivo de actividad trae doscientas dos mil seiscientas cuarenta y siete
> mediciones. No doscientos dos mil compuestos: mediciones, varias del mismo
> compuesto contra la misma diana.
>
> De ahí, ciento diez mil setecientas veintitrés caen en las cinco categorías
> de enfermedad que la patrocinadora ratificó. Ciento seis mil seiscientas
> cuarenta y cinco traen además diana y una estructura que se puede calcular.
> Ciento seis mil cuatrocientas sesenta y cuatro tienen una unidad que se
> puede pasar a concentración molar.
>
> Y al agrupar por par compuesto-diana, que es la unidad sobre la que el
> modelo predice, quedan setenta mil trescientos ochenta y cuatro.

*Entra con:* cada cifra, una por una.

> Y las declaradas inactivas por texto quedan fuera: cinco mil novecientas
> veintidós de las que llegan hasta aquí, veintinueve mil setecientas treinta
> en todo el archivo. No salen porque su límite sea inventado, sino porque son
> una sola campaña de tamizaje: setecientos setenta y dos compuestos, veinte
> ensayos.

---

## 2 · Las columnas *(0:14 – 0:27)*

> Para cada compuesto, RDKit calcula doscientos diecisiete descriptores. No
> todos sirven.
>
> Tres son constantes: valen lo mismo en todas las moléculas, así que no
> distinguen nada.
>
> Doce tienen huecos, y scikit-learn no los acepta sin imputar.
>
> Y uno, el índice de contenido de información, llega a diez elevado a
> cuarenta y uno y desborda la precisión de treinta y dos bits con la que los
> modelos trabajan por dentro.
>
> Quedan doscientos uno. Son dos menos que los doscientos tres de la fase uno,
> y no es otro criterio: es el mismo filtro sobre otras moléculas.

*Entra con:* la matriz completa; después cada bloque de columnas tiñéndose de
rojo y cayendo, y la matriz recomponiéndose.

---

## 3 · La partición *(0:27 – 0:36)*

> Y antes de mirar nada, las filas se parten. Agrupando por estructura, para
> que un compuesto y sus análogos caigan siempre del mismo lado.
>
> Setenta por ciento para entrenar, diez para validar, veinte reservado. Esa
> prueba no se mira hasta el final: es la condición que la patrocinadora puso
> al entregar el archivo completo.

*Entra con:* los tres bloques apareciendo.

---

## 4 · Cierre *(0:36 – 0:41)*

> Cada paso quita filas o columnas, y cada uno dice por qué.
>
> Ninguno de estos filtros es obvio, y ninguno se puede comprobar mirando la
> matriz final: para eso está escrito el linaje completo, archivo por archivo,
> en la documentación del proyecto.

---

## Notas para la locución

- **«RDKit»** se lee *ar-de-kit*.
- **«scikit-learn»** se lee *sai-kit-lern*.
- Las cifras grandes se dicen completas la primera vez y se abrevian después
  si hace falta aire. Si queda muy larga, el tramo 1 es el que admite recorte:
  las cuatro cifras intermedias pueden resumirse en «tres filtros».
- Esta escena es la más cargada de números del conjunto. Todos están
  comprobados contra los parquet de `data/processed/`, no copiados de prosa.
- **Las dos cifras de los inactivos por texto van juntas a propósito.** El
  29,730 es del archivo entero y el 5,922 es lo que este embudo quita; decir
  solo el primero hacía pensar que el embudo se llevaba 29,730, cuando las
  otras 23,808 ya se habían ido por no estar en las cinco categorías. Si hace
  falta aire, la que se puede soltar es la del archivo entero, no la del
  embudo.
