# Artículo científico · doble columna

**No es un entregable del curso.** El entregable es `docs/reportes/articulo/`, que sigue la rúbrica: una columna,
ocho secciones con los nombres y la numeración de la plantilla, 12 a 18 páginas. Este documento cuenta el mismo
trabajo con la forma de un artículo de investigación —doble columna, estructura IMRaD, un hallazgo al frente— y
está pensado para circular fuera del curso: ante la patrocinadora, el Departamento de Bioingeniería o un congreso.

| archivo | qué es |
|:--|:--|
| `articulo-cientifico.tex` | el artículo, **se edita a mano** (ver abajo por qué) |
| `articulo-cientifico.pdf` | el PDF compilado con `sh scripts/compilar_articulo.sh articulo-cientifico`; **no se versiona**, se compila cuando se necesita |
| `figuras/` | enlace simbólico a `../articulo/figuras`: las mismas figuras, generadas con `scripts/figuras_articulo.py` |
| `bibliografia.bib` | enlace simbólico a `docs/referencias/bibliografia.bib` |
| `logo.jpeg` | enlace simbólico a `docs/reportes/logo-tec.jpeg`; el preámbulo no lo usa, porque un artículo de revista no lleva logo |

## Por qué este sí se edita a mano

El entregable se genera desde `borrador.md` con `scripts/armar_articulo_tex.py`, y eso es lo correcto allí: su
`.tex` no debe desfasarse de la fuente en Markdown donde se revisan las cifras. Aquí no hay borrador por dos
razones. La estructura es otra —introducción, datos, métodos, resultados por fase, discusión— y no se puede
derivar de un documento organizado por las ocho secciones de la rúbrica sin reescribirlo entero. Y el formato a
doble columna necesita decisiones que Markdown no expresa: qué figura va a ancho de página (`figure*`) y qué
figura cabe en una columna, dónde flota cada una, cómo se ensancha el resumen. Un generador que admitiera todo
eso sería más frágil que el archivo que produce.

La consecuencia hay que asumirla: **una cifra que cambie hay que cambiarla en los dos documentos.** Ninguna cifra
nace aquí. Todas vienen de `docs/reportes/articulo/borrador.md` y, detrás de él, de una corrida registrada en
`experimentos/`. Para que esa coincidencia no dependa de la memoria de nadie, `tests/test_cifras_repetidas.py`
pasó a leer también los `.tex`: las cifras que vigila —entre ellas el 7.1 que solo vale para el bosque y los 612
esqueletos comunes— ahora fallan si una copia de este artículo discrepa de la del entregable. Lo que esa red
**no** cubre son las cifras que no están en su lista, así que al cambiar una conviene buscarla en los dos
archivos con `grep`.

## Qué comprueba CI

`tests/test_articulo_cientifico_tex.py`, sin compilar: que toda clave citada esté en la bibliografía, que las
figuras apunten a PNG existentes (pdfLaTeX no incluye SVG), que los entornos estén balanceados, que el documento
vaya a doble columna, que toda figura y toda tabla se referencie desde el texto, que no haya quedado sintaxis de
Markdown arrastrada del borrador y que estén la declaración de uso de IA y las referencias.

Lo que ninguna prueba cubre es el PDF: dónde cayó cada flotante, si un encabezado quedó huérfano al pie de una
columna y si alguna tabla se desbordó. Eso pide ojos humanos, página por página.

## Cómo se compila

```bash
sh scripts/compilar_articulo.sh articulo-cientifico
```

pdfLaTeX + Biber en Docker, el mismo script del entregable, que ahora toma el nombre de la carpeta. Necesita el
demonio de Docker levantado y, la primera vez, construye la imagen `tex-art` (unos 4 GB, varios minutos). Compila
en una copia porque Docker no sigue los enlaces simbólicos de la bibliografía, el logo y las figuras.

**En Overleaf** hay que resolver los enlaces antes de subir, igual que en el entregable:

```bash
cd docs/reportes/articulo-cientifico && mkdir -p /tmp/subir && cp -RL articulo-cientifico.tex bibliografia.bib figuras /tmp/subir/
```

## Decisiones

- **APA 7**, como el resto del proyecto. Un congreso que pida IEEE obliga a cambiar una línea del preámbulo y a
  revisar las citas narrativas, que en APA llevan el año entre paréntesis.
- **Doble columna, 10 pt, márgenes de 1.9 cm**, con el resumen a ancho de página. No es la plantilla de ninguna
  revista concreta: cuando haya una revista o un congreso destino, su plantilla manda y el cuerpo se traslada.
- **El título lleva el hallazgo**, no el nombre del sistema: la semejanza química, y no la familia de modelos,
  condiciona el desempeño. Es la diferencia de forma más visible con el entregable, que se titula por el proyecto.
- **Las figuras son las mismas seis** del entregable (de las ocho que hay), por la razón del `CLAUDE.md`: una
  figura que se dibuja dos veces deriva. Las dos que no entran son la de huellas por tramo de peso, que es de
  anexo, y la de arquitectura de despliegue, que es de operación y no de resultados.

## Pendiente

- **Revisar el PDF página por página.** Ya compila: en la revisión del [#305](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/305)
  salieron **9 páginas** a doble columna, tamaño carta, sin referencias sin resolver. Lo que sigue pendiente es
  más fino y ninguna prueba lo cubre: dónde cayó cada flotante, si algún encabezado quedó huérfano al pie de una
  columna y si la tabla de los once modelos cabe en una columna o conviene pasarla a `table*`.
- **Decidir el destino.** Si es un congreso o una revista, su plantilla reemplaza al preámbulo de aquí.
- **La afiliación de la patrocinadora y de la asesora** aparece como el Tec de Monterrey sin departamento;
  confirmar cómo quieren figurar y en qué orden de autoría.
