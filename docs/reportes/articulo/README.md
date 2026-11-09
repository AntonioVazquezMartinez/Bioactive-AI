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

**Estado de la última compilación:** sin errores ni advertencias de LaTeX ni de Biber, 16 páginas de las cuales
el cuerpo, del título a las referencias, ocupa 14 (la rúbrica pide 12 a 18); los anexos van aparte. Las secciones
llevan los nombres y la numeración de la plantilla del curso (el resumen y las referencias no se numeran, así que
«Implementación y operación» es la 5, como dice la rúbrica).

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

- Los campos en rojo del encabezado: **nombre del asesor** y **fecha de entrega**.
- La **declaración de uso de IA**: la redactó la herramienta; el equipo confirma que describe lo que hizo. Trae
  Claude Opus 5 (Pame) y Claude Sonnet 5.5 (Artemio, el de la sesión que la escribió: confirmar si usó otros);
  **falta el modelo de Antonio**, en rojo.
- El **`logo_empresa.png`** que la plantilla del resumen espera no viene en ningún zip. Preguntar si lo aporta la
  patrocinadora.
- Los **umbrales de alerta** de la tabla de supervisión de la sección 6 son propuestas y no se midieron.
