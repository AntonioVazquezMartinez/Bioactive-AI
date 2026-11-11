# Producto de difusión · artículo

Entrega 7, **plazo duro el 15 de noviembre de 2026**. PDF, nombre `articulo.#Equipo`. El primer borrador completo
se comparte antes, para recibir comentarios.

| archivo | qué es |
|:--|:--|
| `esqueleto.md` | el argumento y la tabla de cifras decisivas, con su corrida detrás |
| `borrador.md` | el texto del artículo: **aquí se editan las cifras y el texto** |
| `articulo.tex` | el artículo en LaTeX, **generado** desde el borrador con `scripts/armar_articulo_tex.py`; no se edita a mano |
| `articulo.pdf` | el PDF compilado con `scripts/compilar_articulo.sh`; se regenera cada vez que cambia el borrador |
| `plantilla.tex` | la plantilla del curso, con APA 7 fijado y la bibliografía del proyecto; de aquí sale el preámbulo |
| `figuras/` | las figuras del artículo, generadas con `scripts/figuras_articulo.py`; el `.tex` usa los PNG |
| `bibliografia.bib` | enlace simbólico a `docs/referencias/bibliografia.bib` |
| `logo.jpeg` | enlace simbólico a `docs/reportes/logo-tec.jpeg` |
| `figura_ejemplo.png` | el marcador que la plantilla referencia; se sustituye |

## Cómo se compila

Con **pdfLaTeX + Biber**, que es lo que la plantilla declara y la opción predeterminada de Overleaf.

**En local, con Docker** (no hace falta instalar LaTeX):

```bash
python3 scripts/armar_articulo_tex.py    # borrador.md -> articulo.tex (necesita pandoc)
sh scripts/compilar_articulo.sh          # articulo.tex -> articulo.pdf
```

La primera vez construye una imagen `tex-art` a partir de `texlive/texlive:latest-medium` más las colecciones
`latexextra`, `bibtexextra`, `pictures` y `fontsrecommended` (unos 4 GB, varios minutos); después tarda segundos.
Compila en una copia porque Docker no sigue los enlaces simbólicos de la bibliografía y el logo.

**Estado de la última compilación:** sin errores ni advertencias de LaTeX ni de Biber. El PDF del repositorio
tiene **19 páginas**: el cuerpo, del título a las referencias, ocupa **17** (la rúbrica pide 12 a 18) y los
anexos son las dos últimas, que van aparte. Así que **queda una página de margen, no dos ni cinco**: una sección
nueva no entra, y lo que se añada conviene que sustituya. Esta cuenta se rehace en cada compilación y ya se quedó
corta una vez, así que conviene verificarla en el PDF y no heredarla de aquí. **Y hay que decidirlo a conciencia:**
si quien califica cuenta el PDF completo en lugar de contar hasta las referencias, ve 19 contra un máximo de 18.
Lo que crezca de aquí en adelante conviene que vaya a los anexos, que quedan fuera de la cuenta. Las secciones llevan los nombres y la numeración de la
plantilla del curso. **Ojo con la numeración, que esta frase decía algo falso:** la rúbrica lista las ocho
secciones numerando el resumen como 1 y las referencias como 8, de modo que para ella «Implementación y
operación» es la **6**. El artículo la numera **5** porque no numera el resumen ni las referencias, que es lo
normal. Las ocho están y en el orden que pide, así que **no hay que renumerar nada**; lo que no se puede decir
es que el 5 venga de la rúbrica.

**Pendiente, y son dos cosas.** La primera: **el PDF del repositorio es anterior a los nombres de corrida de los
anexos y a los seis arreglos de redacción que entraron con ellos**, así que hay que volver a compilar con
`sh scripts/compilar_articulo.sh`, que **necesita Docker**. La segunda: revisar el PDF resultante página por
página, mirando dónde cayó cada figura y si algún encabezado quedó solo al pie. Eso pide ojos humanos y no lo
cubre ninguna prueba.

Lo que sí está comprobado sin compilar: el `.tex` se regenera byte a byte igual desde el borrador y las ocho
figuras se regeneran idénticas desde sus corridas, salvo la fecha y los identificadores internos que matplotlib
escribe en cada SVG.

**Y al compilar hay que mirar el conteo,** porque una frase añadida en el cuerpo puede empujar una página entera
cuando parte un párrafo o deja un encabezado huérfano. Con una sola página de margen, lo que no entre sale de lo
que ya está.

**Por qué se midió la prosa.** Las frases más largas llegaban a 929 caracteres (las limitaciones, nueve
cláusulas con punto y coma) y 1,112 (el trabajo futuro, de la a a la e sin un punto), contra el techo de 421
que `tests/test_prosa_cuadernos.py` le pone a los cuadernos. El artículo quedó fuera de esa medición y por eso
creció. Tras el repaso ninguna frase pasa de 414 y la mediana es de 170.

**En Overleaf**: los dos `.bib` y el logo son **enlaces simbólicos**, por la razón que da el `CLAUDE.md`: tres
copias de la bibliografía ya habían divergido. Overleaf no los sigue, así que al subir hay que resolverlos:

```bash
cd docs/reportes/articulo && cp -L bibliografia.bib logo.jpeg /tmp/subir-a-overleaf/
```

Hay que subir también `articulo.tex` y la carpeta `figuras/` con sus PNG (pdfLaTeX no incluye SVG).
`tests/test_articulo_tex.py` falla si el `.tex` no coincide con el borrador. El campo `note` de la bibliografía
son anotaciones internas del equipo («LEÍDO PARCIAL»…) y el `.tex` lo suprime al imprimir las referencias.

## Decidido

- **APA 7.** La plantilla ofrecía APA o IEEE y dejaba las dos líneas en el preámbulo; se
  quitó la de IEEE. El resto del proyecto ya cita en APA, con `docs/referencias/apa.csl`.
- **Extensión: la que pide la rúbrica, 12 a 18 páginas** del título a las referencias, anexos aparte. El
  encabezado de la plantilla dice «3 páginas» por herencia del resumen ejecutivo (los dos zips traen el mismo
  `referencias.bib` y el mismo `logo.jpeg` byte a byte).

## Por confirmar con el equipo

- El encabezado ya trae asesora, patrocinadora y fecha de entrega (13 de noviembre de 2026).
- La **declaración de uso de IA**: la redactó la herramienta; el equipo confirma que describe lo que hizo. La rúbrica pide herramienta, modelo y finalidad, no quién usó cuál, así que lista los modelos en general (Opus 5, Sonnet 5.5 y Sonnet 5 cuando los guardrails en biología y química lo impidieron). Antonio confirma que no usó otro.
- El **`logo_empresa.png`** que la plantilla del resumen espera no viene en ningún zip. Preguntar si lo aporta la
  patrocinadora.
- Los **umbrales de alerta** de la tabla de supervisión de la sección 6 son propuestas y no se midieron.
