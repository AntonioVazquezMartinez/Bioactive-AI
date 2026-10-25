"""El orden del video, en un solo sitio.

**Por qué existe.** Añadir una escena obligaba a tocar tres listas —`ORDEN` en
`ensamblar.py` y `ESCENAS` en `voz.py` y en `sonorizar.py`—, y olvidar una no
fallaba: simplemente la escena no entraba al video, o no se le grababa la voz,
sin que nada avisara. Es la misma clase de defecto que el `.gitignore` que vivía
en una sola rama.

Cada entrada es `(módulo, clase, papel en el hilo)`. El papel no es decoración:
el video sostiene una tesis —**los datos no son lo que parecen**— y cada escena
técnica es una instancia de ella. Si una escena no se puede describir así, o no
pertenece al video o el hilo cambió.

**El orden va por fases, y antes iba por afirmaciones.** La primera versión
montaba cuatro capítulos sobre las cuatro frases de la apertura, y funcionaba
mientras el video tenía esas cuatro escenas. Al entrar cómo se construye el
objetivo, la dirección del ensayo y los resultados, ninguna cabía en las cuatro
y el recorrido se volvió una lista de sorpresas. Ahora se recorre la fase 1
entera —de la molécula al resultado— y después la fase 2 —del archivo al
objetivo—, que es como está construido el proyecto.

El cambio arregla de paso una referencia que iba al revés: la escena del linaje
dice que los 201 descriptores de la fase 2 «son dos menos que los 203 de la
fase 1», y la fase 1 ahora ya se ha visto cuando eso se dice.
"""

ORDEN = [
    ("apertura", "Apertura", "el problema, la apuesta y el recorrido"),
    # Fase 1 · permeabilidad: de la molécula al resultado.
    ("matriz", "Matriz", "una molécula es una fila de números"),
    ("fingerprints", "Fingerprints", "un bit no es un fragmento"),
    ("particion", "Particion", "las filas no son independientes"),
    ("resultados", "Resultados", "qué tan bueno es «bueno», y los naturales"),
    # Fase 2 · actividad: del archivo al objetivo.
    ("linaje", "Linaje", "las mediciones no son compuestos"),
    ("intervalo", "Intervalo", "un «>» no es un hueco"),
    ("objetivo", "Objetivo", "cómo se construye lo que se predice"),
    ("direccion", "Direccion", "una medida apunta en una dirección"),
    ("cierre", "Cierre", "lo que sale, y lo que no se afirma"),
]

# `{módulo: Clase}`, que es como lo quieren `voz.py` y `sonorizar.py`.
ESCENAS = {modulo: clase for modulo, clase, _ in ORDEN}
