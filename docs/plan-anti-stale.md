# Plan anti-stale

Qué guardas impiden que cada clase de desfase vuelva, cuáles ya existen y cuáles faltan. Sale de una auditoría del 12 de noviembre de 2026 (cuatro auditores, cada uno contrastado por un escéptico independiente, sobre el sitio, las cifras, el vocabulario y las propias guardas); esta página recoge lo que sirve a quien trabaje aquí después. **Es un documento interno**: no se publica en el sitio.

Un desfase («stale») es una cifra, una decisión o una estructura de archivos que cambió en un lugar y quedó vieja en otro. Las guardas más baratas son las que impiden que la lista exista; las demás comprueban que dos listas coincidan; la disciplina cubre lo que no se puede comprobar sin gastar más que el problema.

## Las guardas, por clase de desfase

| # | Clase | Ejemplo real que ocurrió | Guarda | Estado |
|--:|:--|:--|:--|:--|
| 1 | Una página o un cuaderno que se construye y no se alcanza, o que no se publica | El cuaderno 06 y `presentacion-final.qmd` fuera del menú; el 05 y el 05c antes | `tests/test_sitio_al_dia.py` y `tests/test_navegacion_sitio.py` | **Hecha** |
| 2 | Un PDF enlazado en el menú que no se copia o ya no existe | — (el menú enlaza ahora cuatro PDF de la entrega final) | `tests/test_sitio_al_dia.py` | **Hecha** |
| 3 | Un estado que caduca en la prosa («en curso», «vence el 25 oct», «sin redactar») | La portada dijo «Avance 4 en curso» dos semanas después | `FRASES_CADUCAS` en `tests/test_sitio_al_dia.py` | **Hecha**, solo para esas frases |
| 4 | Un árbol de archivos descrito en el README o en `CLAUDE.md` | El README listaba 5 de 14 cuadernos | **Quitar el árbol** y enlazar a la carpeta: lo que no se enumera no envejece | **Hecha** |
| 5 | Una cifra repetida en varios documentos | El 65 % que sobrevivió en el artículo científico; el README del resumen con otro ahorro | `tests/test_cifras_repetidas.py` | Existe; **falta** ampliar su corpus a `README.md`, `index.qmd`, `presentacion*.qmd` y los `.tex` del resumen y el póster, con las cifras 63.5/65.0/57.3, 0.793/0.919, 12.6, 4.2, 33.3, 151, 0.530/0.565 |
| 6 | Un PDF versionado que se atrasa de su `.tex` | La figura que decía «el equipo mantiene el sistema» estaba en el PDF y en el `.tex` | Sello `sha256` del `.tex` junto al PDF y una prueba que lo compare; o `pdftotext` contra las cifras canónicas | **Falta**; hoy es disciplina: recompilar y subir el PDF en el mismo PR |
| 7 | Los términos nuevos sin entrada en el glosario | KernelSHAP, Tanimoto, tercil, prueba reservada | Una lista corta `TERMINOS_CLAVE` que exija su entrada en `docs/glosario.md` | **Falta**; las entradas ya están añadidas |
| 8 | Un cuaderno nuevo que no entra en `CUBIERTOS` ni en `CON_DECK` | El 06 | Exigir que cada cuaderno esté en una lista o en una de excluidos con motivo | **Falta** |
| 9 | Un ID de corrida citado que no existe en `experimentos/` | — | Una expresión regular `AAAA-MM-DD-autor-…` contra las carpetas | **Falta** |
| 10 | Texto del PR o del commit con atribuciones de IA | Las descripciones de #314 a #320 | Convención, no prueba: la regla es no ponerlas | Disciplina |
| 11 | `pandoc` ausente del CI, y `test_articulo_tex` que se omite en silencio | — | Que el `skipif` falle si existe `CI`, o instalar pandoc | **Falta**; no hay evidencia de que el runner lo traiga |
| 12 | Figuras versionadas contra la corrida de la que salen | Las copias de `f0_palancas` y `f1_escalera` | Comparar el `md5` de las copias y que cada PNG tenga su SVG | **Falta**; regenerar y comparar el texto del SVG cuesta más y es opcional |

## Lo que no conviene automatizar

- **Una prueba por afirmación** («la lista es exploratoria y no validada», «la continuidad es autónoma»): el costo de mantener los patrones supera el problema. Esas afirmaciones se cuidan con la decisión que las registra (C.5 y C.8 en `docs/decisiones.md`) y con una búsqueda a mano antes de cada entrega.
- **Un escáner de cifras huérfanas**: el ruido de falsos positivos lo vuelve inútil.
- **Probar el registro de decisiones contra el código**: sale caro y el riesgo es bajo.

## Disciplina antes de cada entrega

1. Buscar en el repositorio las frases de estado («en curso», «vence», «pendiente», «sin redactar») y mover a «entregado» lo que ya pasó.
2. Si se cambia un `.tex`, recompilar y subir el PDF en el mismo PR.
3. Si se añade un término técnico, añadirlo al glosario en el mismo PR.
4. Si se cambia una cifra, buscarla con `grep` en `docs/`, los decks, los `.tex`, el README y los cuadernos.
5. Si una decisión cambia, marcar la versión anterior como superada y no reescribirla en silencio (`docs/decisiones.md`).

## Lo que la auditoría no pudo comprobar

No construyó el sitio ni corrió el verificador de enlaces (esta entrega sí: 43 páginas, 2,679 enlaces internos, todos resuelven). No abrió `test_cifras_repetidas.py`, así que su cobertura exacta sale de otra lectura. No comprobó si el runner de CI trae `pandoc`, ni si `Checks` es obligatorio en la protección de la rama `main`.
