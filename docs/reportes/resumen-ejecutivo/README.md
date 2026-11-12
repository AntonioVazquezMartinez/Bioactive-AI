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
- **Costos: son estimaciones del equipo, sin cotización**, y el resumen lo dice. La patrocinadora no responde, así
  que se dan estimaciones razonadas con su rango en lugar de esperar un dato. Los «ensayos» son pruebas de
  laboratorio in vitro, no ensayos clínicos. Confirmar un candidato cuesta **el compuesto más dos pruebas**
  (permeabilidad y actividad celular con curva de dosis y réplicas), en dos escenarios:
  **insumos propios** (unos 365 USD: compuesto de unos 290 USD, que es el promedio de dos estándares USP, más unos
  75 USD de reactivos) y **servicio contratado** (unos 2,040 USD: el mismo compuesto más unos 250 USD por la
  permeabilidad y unos 1,500 USD por la curva celular). **Los precios de servicio no tienen cotización**: son
  nuestra estimación del orden de magnitud de un laboratorio de servicio. Los de lista (kit de membrana
  artificial, cribado universitario, estándares) sí son reales y de EE. UU., convertidos a 17.5 pesos por dólar;
  para México se suma el 16% de IVA (sin flete ni aduana) y se supone el mismo precio de servicio.
  **Las horas de desarrollo, puesta en marcha y operación (856 en total) y el volumen de 20 compuestos por semestre
  no vienen de ninguna fuente**: hay que cambiarlos por los reales. La tarifa sale de un sueldo de 24,000 pesos al
  mes, dentro del rango de las guías salariales, con 1.35 de cargas. **El resultado depende de dos supuestos**: las
  horas de operación (con 76 en lugar de 176, lo que se financia baja de 51,840 a unos 31,590) y el precio de la
  confirmación (con insumos propios el ahorro queda debajo de la operación; contratando el servicio la cubre varias
  veces).
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
