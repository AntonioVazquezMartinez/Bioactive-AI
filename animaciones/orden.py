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
"""

ORDEN = [
    ("apertura", "Apertura", "el problema y la apuesta"),
    ("linaje", "Linaje", "las mediciones no son compuestos"),
    ("matriz", "Matriz", "una molécula es una fila de números"),
    ("intervalo", "Intervalo", "un «>» no es un hueco"),
    ("direccion", "Direccion", "una medida apunta en una dirección"),
    ("fingerprints", "Fingerprints", "un bit no es un fragmento"),
    ("particion", "Particion", "las filas no son independientes"),
    ("cierre", "Cierre", "lo que sale, y lo que no se afirma"),
]

# `{módulo: Clase}`, que es como lo quieren `voz.py` y `sonorizar.py`.
ESCENAS = {modulo: clase for modulo, clase, _ in ORDEN}
