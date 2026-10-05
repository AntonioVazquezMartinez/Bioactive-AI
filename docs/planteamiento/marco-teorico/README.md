# Marco teórico

Los fundamentos del proyecto, en tres partes. Se construyó a partir de siete ramas de investigación documentadas en [`docs/referencias/`](../../referencias/README.md), que conservan la evidencia completa y las advertencias de acceso sobre cada fuente.

Si un término no se entiende, el [glosario](../../glosario.md) lo define sin suponer formación previa en química ni en aprendizaje automático.

Lo que la patrocinadora y los asesores plantearon de viva voz está en las [notas de la reunión del 22 de septiembre](../reunion-2026-09-22.md); varias decisiones del proyecto salen de ahí y no de la literatura.

## Las tres partes

### [1 · Biología de la barrera y de la enfermedad](01-biologia.md)

Qué es la barrera hematoencefálica y por qué bloquea a la mayoría de los fármacos; qué enfermedades neurodegenerativas se quieren atacar y sobre qué dianas moleculares; y por qué los productos naturales son el punto de partida de este proyecto.

**No supone conocimiento de modelado.** Es la entrada natural para quien viene de ciencias de la computación.

### [2 · Métodos computacionales](02-metodos-computacionales.md)

Cómo se predice actividad biológica a partir de la estructura química —la tradición QSAR, sus principios de validación y sus trampas— y cómo se convierte una molécula en una tabla que un modelo pueda consumir: descriptores, fingerprints y representaciones aprendidas.

**No supone conocimiento de química.** Es la entrada natural para quien viene de bioingeniería.

### [3 · Modelado, explicabilidad y hueco identificado](03-modelado-y-explicabilidad.md)

Qué se ha publicado en aprendizaje automático sobre permeabilidad BBB, cómo se justifica una predicción a nivel de subestructura, y qué trabajo no existe todavía y este proyecto pretende hacer.

**Es la parte menos desarrollada**, y a propósito queda visible: son los capítulos donde el proyecto aporta algo propio y donde falta trabajo.

## Estado

Borrador para revisión del equipo y los asesores. **Antes de entregar** hay que verificar contra doi.org toda referencia marcada como de acceso parcial o sin acceso: varias entradas tienen metadatos que nadie del equipo ha leído.

La bibliografía completa está en [`bibliografia.bib`](../../referencias/bibliografia.bib), con 208 entradas. Cada documento de `docs/referencias/` incluye la lista de lo que no se pudo verificar para su ámbito.
