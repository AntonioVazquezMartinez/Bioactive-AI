"""Ninguna cifra en pantalla que la voz no diga.

Es la regla 3 de `animaciones/README.md`, y existe porque un número dentro de
un `.mp4` no se corrige en un PR: si cambia, hay que regrabar. La escribí y la
rompí cuatro veces en el mismo día —`0.637`, los tres conteos de la partición,
el corte de 1 µM y el 84.8%—, y lo encontró un repaso a mano. Esto lo
convierte en algo que falla solo.

**Cómo compara.** La pantalla escribe «0.937» y «70,384»; la voz dice «cero
punto nueve tres siete» y «setenta mil trescientos ochenta y cuatro». No se
puede comparar carácter por carácter, así que la prueba exige que el guion
contenga **una forma reconocible** de la cifra: los dígitos tal cual, o el
número deletreado, o —para los porcentajes y decimales— sus dígitos en
palabras. Cuando una cifra nueva no entra en esas formas, la prueba falla y
hay que escribirla en el guion: que es exactamente el punto.
"""

import ast
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
ANIMACIONES = RAIZ / "animaciones"
GUIONES = ANIMACIONES / "guion"

UNIDADES = {"0": "cero", "1": "un", "2": "dos", "3": "tres", "4": "cuatro",
            "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve"}

_UNO_A_NUEVE = ["", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete",
                "ocho", "nueve"]
_DIEZ_A_QUINCE = ["diez", "once", "doce", "trece", "catorce", "quince"]
_DECENAS = ["", "", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta",
            "setenta", "ochenta", "noventa"]
_CIENTOS = ["", "ciento", "doscientos", "trescientos", "cuatrocientos",
            "quinientos", "seiscientos", "setecientos", "ochocientos",
            "novecientos"]

# Cifras que no son datos del proyecto: la constante de la fórmula de potencia
# y los tamaños de matriz que la voz nombra de otra forma. Cada exención va
# con su motivo, para que añadir una sea una decisión y no un atajo.
EXENTAS = {
    "6": "la constante de «6 − log₁₀ µM»: fórmula, no dato",
    "10": "parte de «log₁₀» y de «10 µM», que la voz dice como unidad",
    "50": "parte de «IC50», el nombre del ensayo",
    "32": "parte de «float32», el nombre de un formato",
    "41": "parte de «10⁴¹», un orden de magnitud dentro de una frase",
    "1": "«fase 1» y «un bit»: no son cantidades medidas",
    "2": "«fase 2» y «dos fragmentos»: idem",
}


def _menos_de_mil(n: int) -> list[str]:
    """Las formas de un número por debajo de mil, en masculino y femenino."""
    if n == 0:
        return ["cero"]
    if n == 100:
        return ["cien"]
    cientos, resto = divmod(n, 100)
    decenas, unidades = divmod(resto, 10)

    if resto == 0:
        cola = [""]
    elif resto < 10:
        cola = [_UNO_A_NUEVE[resto]]
    elif resto <= 15:
        cola = [_DIEZ_A_QUINCE[resto - 10]]
    elif resto < 20:
        cola = ["dieci" + _UNO_A_NUEVE[unidades]]
    elif resto < 30:
        # veintidós, veintitrés y veintiséis llevan acento; los demás no.
        acentuados = {2: "veintidós", 3: "veintitrés", 6: "veintiséis"}
        cola = (["veinte"] if unidades == 0
                else [acentuados.get(unidades, "veinti" + _UNO_A_NUEVE[unidades])])
    elif unidades == 0:
        cola = [_DECENAS[decenas]]
    else:
        cola = [f"{_DECENAS[decenas]} y {_UNO_A_NUEVE[unidades]}"]

    formas = []
    for c in cola:
        base = _CIENTOS[cientos]
        junto = f"{base} {c}".strip() if base else c
        formas.append(junto)
        # «setecientas treinta» además de «setecientos treinta»: el español
        # concuerda en género y la narración habla de filas y mediciones.
        # El sufijo es «ientos» y no «cientos», porque «quinientos» no lleva
        # la ce — con «cientos» se quedaban fuera quinientos y sus parientes.
        if base.endswith("ientos"):
            formas.append(junto.replace("ientos", "ientas", 1))
        formas.append(junto.replace("un ", "una ") if junto.startswith("un ")
                      else junto)
    return [f for f in formas if f]


def en_palabras(n: int) -> list[str]:
    """Las formas en que una narración en español puede decir `n`."""
    if n < 1000:
        return _menos_de_mil(n)
    miles, resto = divmod(n, 1000)
    cabeza = (["mil"] if miles == 1
              else [f"{m} mil" for m in _menos_de_mil(miles)])
    if resto == 0:
        return cabeza
    return [f"{c} {r}" for c in cabeza for r in _menos_de_mil(resto)]


def _escenas() -> list[Path]:
    return sorted(p for p in ANIMACIONES.glob("*.py")
                  if p.stem not in {"comun", "ensamblar"})


def _cifras_en_pantalla(fuente: str) -> set[str]:
    """Las cifras de cualquier cadena de la escena, menos las documentaciones.

    Recorre el árbol sintáctico y no el texto con una expresión regular. La
    primera versión solo miraba cadenas escritas dentro de `dato(...)`, y por
    eso **no veía las que van en una tupla** —que es como están las cuatro
    cifras mudas que encontró la revisión: `("0.637", "mixtos", ...)`—. Una
    guarda que no ve el defecto que motivó escribirla no sirve.

    Las documentaciones de módulo, clase y función quedan fuera: ahí las
    cifras son explicación y no texto en pantalla. Los comentarios no son
    cadenas, así que `ast` ya los ignora.
    """
    arbol = ast.parse(fuente)

    # El pie de procedencia queda fuera: por definición son referencias
    # —«Decisión 2.3», «notebook 02b», «Equipo 7»— y no cifras que la voz
    # tenga que decir. Es la línea que dice de dónde salen las demás.
    en_el_pie = set()
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                and nodo.func.id == "pie"):
            for hijo in ast.walk(nodo):
                if isinstance(hijo, ast.Constant) and isinstance(hijo.value, str):
                    en_el_pie.add(id(hijo))

    documentaciones = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            cuerpo = getattr(nodo, "body", [])
            if (cuerpo and isinstance(cuerpo[0], ast.Expr)
                    and isinstance(cuerpo[0].value, ast.Constant)
                    and isinstance(cuerpo[0].value.value, str)):
                documentaciones.add(id(cuerpo[0].value))

    cifras = set()
    for nodo in ast.walk(arbol):
        if not (isinstance(nodo, ast.Constant) and isinstance(nodo.value, str)):
            continue
        if id(nodo) in documentaciones or id(nodo) in en_el_pie:
            continue
        for c in re.findall(r"\d[\d.,]*%?", nodo.value):
            limpia = c.rstrip(".,")
            if limpia:
                cifras.add(limpia)
    return cifras


def _formas(cifra: str) -> list[str]:
    """Las maneras en que un guion puede decir esa cifra."""
    limpia = cifra.rstrip("%")
    formas = [cifra, limpia, limpia.replace(",", "")]

    if "." in limpia:
        # «0.937» → «cero punto nueve tres siete», que es como se lee un
        # decimal largo en voz alta.
        entero, _, dec = limpia.partition(".")
        formas.append(f"{UNIDADES.get(entero, entero)} punto "
                      + " ".join(UNIDADES.get(d, d) for d in dec))
        # «84.8» → «ochenta y cuatro coma ocho» / «punto ocho»
        try:
            for e in en_palabras(int(entero)):
                for sep in ("punto", "coma"):
                    formas.append(f"{e} {sep} "
                                  + " ".join(UNIDADES.get(d, d) for d in dec))
        except ValueError:
            pass
    else:
        try:
            formas.extend(en_palabras(int(limpia.replace(",", ""))))
        except ValueError:
            pass
    return formas


@pytest.mark.parametrize("escena", _escenas(), ids=lambda p: p.stem)
def test_toda_cifra_en_pantalla_esta_en_el_guion(escena: Path):
    guion = GUIONES / f"{escena.stem}.md"
    if not guion.exists():
        pytest.skip(f"{escena.stem} todavía no tiene guion")

    # **Solo las líneas de cita son la narración.** El resto del guion son
    # acotaciones y notas, y ahí sí puede aparecer una cifra sin que la voz
    # la diga: la nota de `cierre.md` que explica la diferencia entre 0.863 y
    # 0.866 hacía pasar la prueba con el 0.863 puesto en pantalla.
    #
    # Y se aplana a una sola línea porque el guion va partido a 79 caracteres,
    # así que «cuatro mil noventa y seis» puede quedar cortado a la mitad.
    narracion = [l.lstrip()[1:] for l in guion.read_text(encoding="utf-8").splitlines()
                 if l.lstrip().startswith(">")]
    dicho = re.sub(r"\s+", " ", " ".join(narracion)).lower()
    mudas = []
    for cifra in sorted(_cifras_en_pantalla(escena.read_text(encoding="utf-8"))):
        if cifra in EXENTAS:
            continue
        if not any(f.lower() in dicho for f in _formas(cifra)):
            mudas.append(cifra)

    assert not mudas, (
        f"{escena.name} muestra cifras que {guion.name} no dice: "
        + ", ".join(mudas)
        + ". O la voz las dice, o salen de la escena (regla 3 del README)")


def test_hay_escenas_y_guiones_que_revisar():
    """Si alguien mueve las carpetas, la prueba deja de proteger en silencio."""
    assert _escenas(), "no hay escenas en animaciones/"
    assert list(GUIONES.glob("*.md")), "no hay guiones en animaciones/guion/"


# ---------------------------------------------------------------------------
# Las voces no se enciman
#
# Cada tramo del guion se coloca en el segundo donde la escena lo abrió. Si uno
# dura más que el hueco hasta el siguiente, se oyen dos voces a la vez — y eso
# no se ve en el código: hay que medirlo. Pasó en `intervalo` y `particion`,
# con cuatro y seis segundos de solape, porque el `cerrar_tramo` del primer
# acto había quedado dentro de un método auxiliar.
# ---------------------------------------------------------------------------

VOZ = ANIMACIONES / "voz"


def _duracion(ruta: Path) -> float:
    import subprocess
    s = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True, check=True)
    return float(s.stdout.strip())


def _escenas_con_voz() -> list[str]:
    ruta = VOZ / "offsets.json"
    if not ruta.exists():
        return []
    import json
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return [e for e in datos
            if any((VOZ / f"{e}-{n}.mp3").exists() for n in datos[e]["tramos"])]


@pytest.mark.parametrize("escena", _escenas_con_voz() or ["sin-voz"])
def test_ningun_tramo_se_encima_con_el_siguiente(escena: str):
    import json
    import shutil
    if escena == "sin-voz":
        pytest.skip("todavía no hay voz generada")
    if not shutil.which("ffprobe"):
        pytest.skip("hace falta ffprobe para medir los audios")

    datos = json.loads((VOZ / "offsets.json").read_text(encoding="utf-8"))[escena]
    tramos = sorted((int(n), float(s)) for n, s in datos["tramos"].items())
    solapes = []
    for i, (n, inicio) in enumerate(tramos):
        pista = VOZ / f"{escena}-{n}.mp3"
        if not pista.exists():
            continue
        fin = inicio + _duracion(pista)
        tope = tramos[i + 1][1] if i + 1 < len(tramos) else datos["duracion_s"]
        if fin > tope + 0.05:
            solapes.append(f"tramo {n} acaba en {fin:.1f} s y el siguiente"
                           f" empieza en {tope:.1f} s")
    assert not solapes, f"{escena}: se oirían dos voces a la vez · " + "; ".join(solapes)
