# Guion · Cómo se construye lo que el modelo predice

**Duración de la animación:** 95 s (baja calidad).

**Por qué existe.** El video explicaba qué es una medición censurada y nunca
decía cómo se pasa de un montón de mediciones a **una fila con un objetivo**.
Es la pieza central de la fase dos: la unidad no es la medición, la agregación
no es obvia, y lo que se guarda no es la etiqueta. Sin esta escena, un
espectador entiende las piezas y no la construcción.

Va después de la escena del intervalo, que es la que enseña a leer el eje.

---

## 1 · La unidad es el par, no la medición *(0:00 – 0:17)*

> El modelo no predice sobre mediciones. Predice sobre **pares**: un compuesto
> contra una diana.
>
> Y eso obliga a agregar, porque el mismo par suele estar medido varias veces,
> en laboratorios distintos y con ensayos distintos. De los setenta mil
> trescientos ochenta y cuatro pares, quince mil ciento cincuenta y tres traen
> más de una medición.
>
> Así que la pregunta no es cuál medición es buena. Es qué número representa a
> todas.

*Entra con:* las mediciones de un par cayendo sobre una sola fila.

---

## 2 · Con números exactos, la mediana *(0:17 – 0:38)*

> Si el par tiene alguna medición exacta, se usa la **mediana** de ellas.
>
> No la más potente, que es la tentación: quedarse con el mejor valor premia al
> ensayo más generoso y convierte el objetivo en una colección de máximos. Y no
> el promedio, que un solo valor extremo arrastra.
>
> Hace falta, porque las mediciones del mismo par discrepan de verdad: en tres
> mil doscientos veintidós pares, el valor más alto y el más bajo se separan
> más de un orden de magnitud.
>
> La mediana no arregla esa discrepancia. La absorbe, y la deja declarada en
> una columna aparte para que se pueda mirar.

*Entra con:* los puntos en el eje, la mediana marcándose, y el máximo
apagándose al lado.

---

## 3 · Sin números exactos, las cotas se cruzan *(0:38 – 0:57)*

> Doce mil quinientos cincuenta y dos pares no tienen ni una medición exacta:
> solo cotas.
>
> Ahí no hay nada que promediar, pero sí algo que deducir. Un «mayor que» dice
> que la potencia no llega hasta cierto punto, y un «menor que» dice que lo
> pasa. Dos cotas del mismo par se cruzan y dejan un tramo: ahí dentro está la
> potencia real.
>
> Sigue sin ser un número. Es un intervalo, y con un intervalo se puede
> trabajar.

*Entra con:* las dos cotas entrando y el tramo que queda entre ellas.

---

## 4 · Lo que se guarda es el intervalo, no la etiqueta *(0:57 – 1:18)*

> Y aquí está la decisión que hace reversible todo lo demás: lo que se guarda
> es el intervalo, no la clase.
>
> La etiqueta se deduce al leer. Si el intervalo entero queda del lado potente
> del corte, activo. Si entero del otro, inactivo. Y si el corte lo atraviesa,
> la evidencia no alcanza para decidir: son dos mil seiscientos cuarenta y ocho
> pares, y se declaran en vez de inventarlos.
>
> Mover el corte de diez micromolar a uno es volver a leer. No reconstruir
> nada, y no volver a ejecutar un notebook.

*Entra con:* los tres intervalos contra la línea del corte, cada uno con su
desenlace.

---

## 5 · Y cuando la evidencia se contradice, se marca *(1:18 – 1:35)*

> Queda un caso que ninguna regla resuelve: que las mediciones del par no
> puedan ser ciertas a la vez. Una mediana que cae fuera de lo que sus propias
> cotas permiten, o dos cotas que se cruzan al revés.
>
> Son mil ciento veintiséis pares, y no se tiran: se marcan.
>
> Tirarlos sería una decisión del modelado disfrazada de limpieza de datos. El
> que modela decide si los quiere; el que prepara los datos solo tiene que
> dejar claro cuáles son.

*Entra con:* el par en conflicto, su marca, y el pie con la fuente.

---

## Notas para la locución

- **«mediana»** y **«media»** no son intercambiables en esta escena y la voz
  tiene que separarlas bien; es el punto del tramo 2.
- **«µM»** se lee «micromolar».
- Las cifras largas se dicen completas: «setenta mil trescientos ochenta y
  cuatro», «quince mil ciento cincuenta y tres».
- **Esta escena no habla de modelos.** Todo lo que cuenta ocurre antes de
  entrenar nada, y mezclarlo con desempeño fue lo que hizo confusa la primera
  versión del guion de la fase dos.
- El tramo 5 cierra con una idea que vale para todo el proyecto: separar la
  decisión de datos de la decisión de modelado. Si hay que recortar la escena,
  **ese remate no se toca**.
