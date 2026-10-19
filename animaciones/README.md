# Animaciones

Dos ideas de este proyecto son **temporales**: se entienden viendo algo
cambiar, y por eso se explican mal con un diagrama estático. Para todo lo
demás —fases, fuentes, flujo de datos— están los diagramas mermaid y las
gráficas interactivas del mazo, que además se revisan como un diff y están
atadas a los datos.

| Escena | Qué explica | Estado |
|:--|:--|:--|
| `particion.py` | Por qué partir al azar infla el resultado | guion escrito, sin voz |
| `intervalo.py` | Por qué un «> 10 µM» no es un dato faltante | guion escrito, sin voz |

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

## Dos guardas, porque mirar fotogramas no escala

La primera versión de estas dos escenas tuvo **siete defectos de composición**
—texto saliéndose del cuadro, etiquetas encimadas, títulos ilegibles a media
transición—, y los encontré extrayendo fotogramas a mano y mirándolos. Eso no
escala y no se puede pedir en una revisión.

`comun.py` trae dos comprobaciones que fallan **al renderizar**, con el nombre
y la posición del objeto culpable:

- `cabe(*objetos)` — si algo se sale del cuadro.
- `separados(a, b)` — si dos objetos se encinan.

Las escenas las llaman en los puntos donde ya falló algo. No sustituyen mirar
el resultado: no detectan una jerarquía mal puesta ni un color que no contrasta.
Detectan las dos clases que más veces se repitieron.

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
