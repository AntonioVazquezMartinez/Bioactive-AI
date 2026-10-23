# Guion · Por qué no plegamos el fingerprint

**Duración de la animación:** 37 s (baja calidad).

**Por qué existe.** El proyecto exige poder señalar **qué subestructura**
empuja una predicción. Esa exigencia es la que decide entre los dos
fingerprints, y la razón es puramente visual: una función de dispersión mete
fragmentos distintos en el mismo bit. Con dos cajas y unas flechas se ve; en
prosa hay que creerlo.

---

## 1 · La colisión *(0:00 – 0:13)*

> Un fingerprint plegado reparte las subestructuras de una molécula entre un
> número fijo de bits, con una función de dispersión.
>
> El problema es que son muchas más subestructuras que bits. Así que tarde o
> temprano dos fragmentos distintos caen en el mismo.
>
> Y si ese bit pesa en la predicción, no se puede decir cuál de los dos la
> empujó.

*Entra con:* los tres fragmentos; después cada flecha, una a una; el aviso
rojo cuando el bit compartido se tiñe.

---

## 2 · Ordenar y cortar *(0:13 – 0:23)*

> Sort & Slice no pliega. Ordena las subestructuras por frecuencia en el
> conjunto de entrenamiento y se queda con las primeras: una columna, una
> subestructura.
>
> Sin colisiones. Un bit importante se puede dibujar.

*Entra con:* las barras ordenándose; el corte, cuando la cola se apaga.

---

## 3 · Lo que cuesta *(0:23 – 0:33)*

> Pero la cola se corta, y hay cola. El entrenamiento tiene once mil
> cuatrocientas setenta y cinco subestructuras distintas, y en el vocabulario
> caben dos mil cuarenta y ocho: el dieciocho por ciento.
>
> Con eso se cubre el ochenta y cuatro coma ocho por ciento de las
> subestructuras del entrenamiento, y solo el sesenta y ocho de las de la
> prueba. La prueba trae los andamios raros, que son justo los que el corte
> deja fuera.
>
> Y lo que no se espera: esa brecha **crece** con el vocabulario. Trece coma
> seis puntos con quinientas doce columnas, diecisiete coma ocho con cuatro
> mil noventa y seis.

*Entra con:* las cuatro cifras, una a una.

---

## 4 · Cierre *(0:33 – 0:37)*

> Se paga cobertura por trazabilidad. Como el proyecto exige señalar la
> subestructura responsable, es el intercambio correcto — y queda declarado.

---

## Notas para la locución

- **«Sort & Slice»** se dice en inglés, *sort and slice*, que es como lo
  llama el equipo.
- **«fingerprint»** se deja en inglés; traducirlo a «huella molecular» no es
  lo que nadie dice en voz alta aquí.
- El tramo 3 es el que más cifras tiene, y **ninguna puede quedarse solo en
  pantalla**: la regla 3 dice que si la voz no la dice, no va. Si hace falta
  aire, la salida es quitar 13.6 y 17.8 **de la escena también** y dejar solo
  «la brecha crece con el vocabulario», que es lo que importa.
- **Las cifras de cobertura son las de la prueba reservada, y por eso la
  escena dice «la prueba».** Hay otra medición de lo mismo sobre la
  validación, dentro de la validación cruzada, que da 71.0% con 2048 columnas
  y brechas de 11.9, 13.8 y 14.8 (`notebooks/datos/resultados_L_sortslice.csv`
  y la tabla de la [1.7](../../docs/decisiones.md#d1-7)). **No se mezclan**: si
  alguien cambia el 68.0 por el 71.0 tiene que cambiar las tres brechas y
  decir que habla de validación. La [1.5](../../docs/decisiones.md#d1-5) las
  distingue explícitamente.
