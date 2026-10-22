# Animaciones

Dos ideas de este proyecto son **temporales**: se entienden viendo algo
cambiar, y por eso se explican mal con un diagrama estático. Para todo lo
demás —fases, fuentes, flujo de datos— están los diagramas mermaid y las
gráficas interactivas del mazo, que además se revisan como un diff y están
atadas a los datos.

## El video completo

Siete escenas, 10:22, unidas por una tesis: **los datos no son lo que
parecen**. Las cinco técnicas no son viñetas sueltas — cada una es una
instancia de esa frase, y el cierre la cobra.

| # | Escena | Papel en el hilo | Dura |
|:--|:--|:--|--:|
| 1 | `apertura.py` | el problema y la apuesta | 62 s |
| 2 | `linaje.py` | las mediciones no son compuestos | 141 s |
| 3 | `matriz.py` | de una cadena de texto a 2,254 números | 74 s |
| 4 | `intervalo.py` | un «>» no es un hueco | 81 s |
| 5 | `fingerprints.py` | un bit no es un fragmento | 92 s |
| 6 | `particion.py` | las filas no son independientes | 94 s |
| 7 | `cierre.py` | lo que sale, y lo que no se afirma | 79 s |

Las duraciones salen de la voz y no al revés, así que cambian al regrabar un
tramo: las imprime `voz.py --medir` y quedan en `voz/tiempos.json`.

```bash
python animaciones/ensamblar.py                 # borrador, 480p
python animaciones/ensamblar.py --calidad alta  # 1080p
python animaciones/ensamblar.py --solo linaje intervalo
```

**El orden vive en `orden.py`**, que es de donde lo leen `ensamblar.py`,
`voz.py`, `sonorizar.py` y el CI. Estaba escrito en cada uno de ellos, y
olvidar una copia no fallaba: la escena simplemente no entraba, o entraba sin
voz, o no se renderizaba en CI. `ensamblar.py` comprueba tres cosas antes de
unir: que no falte ninguna parte, que todas sean de la misma calidad,
y que ninguna sea más vieja que su escena. Esa tercera es la que importa: si
se toca `linaje.py` y no se vuelve a renderizar, el video llevaría la versión
anterior — que es exactamente cómo el mazo se desincronizó dos veces de sus
cifras.

Las transiciones son fundidos de medio segundo. Sin efectos: la atención tiene
que estar en lo que se explica.

## Las tres reglas

Salen de que el material de este proyecto ya se desincronizó dos veces de las
cifras que decía citar, y un video es mucho peor que un texto en eso: nadie lo
vuelve a renderizar.

1. **El `.py` se versiona; el `.mp4` no.** La escena es código revisable en un
   PR. El video es un artefacto generado, como los PDF de los reportes.
2. **Lo mínimo de cifras dentro del cuadro, y siempre con su pie de
   procedencia.** Un número dentro de un `.mp4` no se puede corregir en una
   línea. `particion.py` tiene tres, y las tres salen de la decisión 1.2.
3. **Ninguna cifra en pantalla que la voz no diga, ni al revés.** Si cambia
   una, cambian las dos y hay que regrabar. Es caro a propósito: obliga a
   poner pocas.

   Esta la escribí y la rompí el mismo día, en cuatro sitios, y lo encontró un
   repaso a mano. Ahora la comprueba `tests/test_animaciones.py`: recorre el
   árbol sintáctico de cada escena, saca las cifras de toda cadena que no sea
   documentación, y exige que el guion las diga —en
   dígitos o en palabras, con un conversor de números al español que sabe de
   géneros y acentos—. Busca **solo en las líneas de cita**, que son la
   narración: una nota explicativa que mencione la cifra no cuenta.

   Del pie de procedencia se exentan **solo sus referencias** —«decisión 1.2»,
   «notebook 03», «2048 bits», «una semilla»—, y no lo que alguien midió. La
   exención era del pie entero, con la premisa escrita en su propio comentario
   («por definición son referencias»), y por ahí se coló «densidad 1.91% contra
   2.33% del plegado»: una medición que solo aparecía ahí y que la voz nunca
   dijo. Lo encontró una auditoría, no la guarda.

## Tres guardas, porque mirar fotogramas no escala

La primera versión de estas dos escenas tuvo **siete defectos de composición**
—texto saliéndose del cuadro, etiquetas encimadas, títulos ilegibles a media
transición—, y los encontré extrayendo fotogramas a mano y mirándolos. Eso no
escala y no se puede pedir en una revisión.

`comun.py` trae tres comprobaciones que fallan **al renderizar**, con el
nombre y la posición del objeto culpable:

- `cabe(*objetos)` — si algo se sale del cuadro.
- `separados(a, b)` — si dos objetos se encinan.
- `TOPE_CONGELADO` — si un tramo se queda más de nueve segundos con la imagen
  fija y la voz hablando encima.

La tercera salió de medir: la pantalla quieta es el defecto que una auditoría
señaló cinco veces y que nadie podía cuantificar. Al ponerla, el peor tramo se
quedaba **29.2 s** congelado; repartido el dibujo con `respira()`, el peor es
**7.9 s**. El congelado de cada tramo queda en `voz/offsets.json`, así que se
puede revisar sin volver a renderizar.

Las escenas las llaman en los puntos donde ya falló algo. No sustituyen mirar
el resultado: no detectan una jerarquía mal puesta ni un color que no contrasta.
Detectan las tres clases que más veces se repitieron.

**Lo que sigue sin guarda, y hay que mirar a ojo:**

- Transiciones de texto. Cambiar un título con `Transform` interpola letra a
  letra entre textos de largo distinto y deja medio segundo ilegible: va con
  fundido.
- Saltos de línea. En el código son `\n` de verdad; escritos con doble barra
  salen literales en pantalla.
- Que lo que la escena *ilustra* y lo que la cifra *mide* sean lo mismo. El
  defecto más caro de la primera versión fue ese: la escena mostraba una
  partición al azar y la cifra de abajo venía de agrupar por andamio.

## Cómo se renderiza

Manim queda **fuera de `requirements.lock`** a propósito: el lock fija el
entorno con el que se midieron las cifras, y Manim arrastra cairo, pango y
ffmpeg, que no tienen nada que ver con eso.

```bash
uv venv --python 3.12 env-anim
uv pip install --python env-anim -r requirements-animaciones.txt
brew install ffmpeg          # hace falta en el sistema

cd animaciones
../env-anim/bin/python -m manim -ql particion.py Particion   # borrador, 480p
../env-anim/bin/python -m manim -qh particion.py Particion   # final, 1080p
```

**No hace falta LaTeX.** Las escenas usan `Text` y no `MathTex`, para que
cualquiera del equipo pueda renderizarlas. Eso obliga a escribir las fórmulas
con Unicode o a decirlas en la narración.

La salida cae en `animaciones/media/`, que está en el `.gitignore`.

## El guion y la voz

Cada escena tiene su guion en `guion/`, con los tiempos y el elemento de la
escena con el que cada bloque tiene que coincidir. El guion se afina **antes**
de grabar: es texto, se revisa en un PR y corregirlo no cuesta nada.

La voz se graba después con ElevenLabs y se monta con `ffmpeg`. Si la locución
queda más larga que su tramo, se alarga el `wait()` de la escena y se vuelve a
renderizar; no se recorta el guion para que quepa.
