# Resumen ejecutivo

Entrega 8, **15 de noviembre de 2026**. PDF de 3 páginas más anexos, nombre
`resumen_ejecutivo.#Equipo`.

**Estado:** primer borrador completo, compilado en `resumen_ejecutivo.pdf` (3 páginas hasta las referencias,
anexos en la 4 y la 5). Se compila con `bash scripts/compilar_articulo.sh resumen-ejecutivo` y se verifica con
`tests/test_resumen_ejecutivo_tex.py`.

| archivo | qué es |
|:--|:--|
| `resumen_ejecutivo.tex` | el resumen, sobre la plantilla del curso, con la bibliografía del proyecto |
| `resumen_ejecutivo.pdf` | el PDF compilado |
| `bibliografia.bib` | enlace simbólico a `docs/referencias/bibliografia.bib` |
| `logo.jpeg` | enlace simbólico a `docs/reportes/logo-tec.jpeg` |

## De dónde sale cada cifra

- **Desempeño:** las del artículo (`../articulo/borrador.md`); una prueba comprueba que coincidan.
- **Beneficio medido:** `scripts/ahorro_por_priorizacion.py` lee las predicciones de la lectura de la prueba
  reservada que ya estaba versionada y calcula qué parte de los permeables queda al ensayar solo lo mejor
  ordenado. **No abre la prueba de nuevo.** Su corrida está en `experimentos/*ahorro-por-priorizacion-fase1`.
- **Costos:** **son supuestos del equipo, a confirmar con la patrocinadora**, y el resumen lo dice. Los precios
  de ensayo se dan en **dos mercados**: los de EE. UU. (reactivos de una membrana artificial, un servicio de
  cribado y un ensayo ADME de servicio, en dólares y convertidos a 17.5) y los de México. **Para México no hay
  precios publicados de estos ensayos**: el escenario bajo es el de EE. UU. con IVA del 16% (sin flete ni aduana), el
  medio toma 2,500 pesos, mitad del rango de servicios analíticos de un centro público mexicano (que no son ensayos
  de permeabilidad) y el alto queda sin dato. No son precios de ella. Las horas de desarrollo,
  implementación y operación (856 en total) y el volumen de 50 compuestos al mes no vienen de ninguna fuente:
  hay que cambiarlos por los reales. La tarifa sale de un sueldo de 24,000 pesos al mes, dentro del rango de
  las guías salariales, con 1.35 de cargas.
- **La base del ahorro es el modelo contra el sorteo, no contra no ensayar.** Confirmar el 70% mejor ordenado
  evita el 30% de los candidatos, pero un sorteo que confirma el 70% también lo evita; lo que el modelo aporta es
  conservar el 85.3% de los permeables en lugar del 70%. Para igualar ese 85.3% un sorteo tendría que confirmar el
  85.3%: el modelo evita **15.3 puntos** de candidatos a igual recuperación, 0.51 al mes con 20 compuestos por
  semestre, y con eso **el ahorro (unos 2,770 pesos al mes con precios de EE. UU., 4,290 con los de México) no
  cubre la operación (4,320)**. El resumen lo dice: se compensa si confirmar un candidato cuesta más de unos 8,450
  pesos, o con más volumen. Lo calcula `tests/test_resumen_ejecutivo_tex.py` desde la corrida.
- **El punto de equilibrio** (Anexo B) es lo que sostiene la recomendación sin depender de un precio
  que no conocemos: dice cuánto debe costar un ensayo para que el ahorro compense el gasto.

## Lo que decidimos de la plantilla

Sus recuadros están escritos para un proceso que se automatiza (latencia, cobertura, horas ahorradas). Se
reencuadraron sobre la unidad real del proyecto —ensayos de confirmación que se evitan, permeables que se
conservan— y no se rellenaron con cifras que no existen. Se quitó el logo de empresa: la patrocinadora es una
académica del Tec y no hay empresa.

## Pendiente de confirmar

- Las **horas** y el **volumen mensual** de los anexos, y la tarifa.
- El **costo real de un ensayo de confirmación** de la patrocinadora, que mueve la recomendación.
- La **fecha de entrega** (la portada dice 15 de noviembre).
- La revisión del equipo, página por página, del PDF.

## La declaración de uso de IA

Lista los modelos en general, como en el artículo. Quien firma confirma que describe lo que se hizo.
