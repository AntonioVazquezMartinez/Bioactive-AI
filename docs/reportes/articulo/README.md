# Producto de difusión · artículo

Entrega 7, **8 de noviembre de 2026**. PDF, nombre `articulo.#Equipo`.

| archivo | qué es |
|:--|:--|
| `esqueleto.md` | el argumento y la tabla de cifras decisivas, con su corrida detrás |
| `articulo.tex` | la plantilla del curso, con APA 7 fijado y la bibliografía del proyecto |
| `bibliografia.bib` | enlace simbólico a `docs/referencias/bibliografia.bib` |
| `logo.jpeg` | enlace simbólico a `docs/reportes/logo-tec.jpeg` |
| `figura_ejemplo.png` | el marcador que la plantilla referencia; se sustituye |

## Cómo se compila

Con **pdfLaTeX + Biber**, que es lo que la plantilla declara y la opción predeterminada de
Overleaf. En esta máquina no hay `pdflatex` ni `biber` ni `quarto`, así que **el único sitio
donde compila hoy es Overleaf**, y el PDF no se puede verificar en CI.

Los dos `.bib` y el logo son **enlaces simbólicos**, por la razón que da el `CLAUDE.md`: tres
copias de la bibliografía ya habían divergido. Overleaf no los sigue, así que al subir hay
que resolverlos:

```bash
cd docs/reportes/articulo && cp -L bibliografia.bib logo.jpeg /tmp/subir-a-overleaf/
```

## Decidido

- **APA 7.** La plantilla ofrecía APA o IEEE y dejaba las dos líneas en el preámbulo; se
  quitó la de IEEE. El resto del proyecto ya cita en APA, con `docs/referencias/apa.csl`.

## Por resolver, y las dos valen puntos

- **La extensión.** El encabezado de la plantilla dice «3 páginas» y la rúbrica puntúa 12 a
  18 (20 pts). La línea viene heredada del resumen ejecutivo: los dos zips traen el mismo
  `referencias.bib` y el mismo `logo.jpeg` byte a byte. Manda la rúbrica, falta confirmarlo.
- **El `logo_empresa.png`** que la plantilla del resumen espera no viene en ningún zip.
  Preguntar si lo aporta la patrocinadora.

## Lo que todavía no existe

La **sección 5**, «Implementación y operación»: arquitectura de despliegue con diagrama,
requisitos de operación con responsables y qué se supervisa. Son 25 puntos y no hay una sola
línea escrita en el repositorio. El `docs/roadmap-mlops.md` alimenta el monitoreo y los
riesgos, pero es MLOps de registro de experimentos, no una arquitectura de producción.
