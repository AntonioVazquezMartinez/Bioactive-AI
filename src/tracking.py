"""Registro de una corrida: una carpeta de texto en `experimentos/<id>/`.

Convención (fases 0.1 y 0.2 de `docs/roadmap-mlops.md`). Git es la fuente de verdad: lo que
se versiona son archivos pequeños, no un servidor. Cada corrida deja

- `params.yaml`: parámetros y semillas con los que se repite;
- `metricas.json`: las métricas, nunca registros de los datos (licencias C.6);
- `entorno.json`: commit y si el árbol estaba sucio, sistema operativo, versiones, huella
  `sha256` del lock y de los datos de entrada;
- `comando.txt`: el comando que la lanzó.

Uso, con tres líneas::

    with Corrida("L", decision="1.7", params={...}, semillas=[0, 1, 2], datos=[ruta]) as c:
        ...
        c.metricas({"MCC": 0.71})

El `id` es `AAAA-MM-DD-<autor>-<decision>-<nombre>` (p. ej. `2026-10-14-ingrid-1.7-L`): lleva
la decisión a la que sirve, y el autor evita que dos personas escriban la misma carpeta.
Una corrida no se sobrescribe; si falla, su carpeta se borra. Si MLflow está instalado, la
corrida se registra también en su almacén local (opcional: el visor, no la verdad).

Sin dependencias de otros módulos de `src/`, para importarse igual como `tracking` (los
scripts ponen `src/` en el path) o como `src.tracking`.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import time
from datetime import date
from importlib import metadata
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
DECISION = re.compile(r"^(C|1|2)\.\d+[a-z]?$")
PAQUETES = ("numpy", "pandas", "scipy", "scikit-learn", "xgboost", "rdkit", "imbalanced-learn")
BITACORA = "prueba.csv"


def tomar_prueba(pares, *, final: bool = False, motivo: str = "", raiz: Path = RAIZ,
                 col: str = "particion", col_estrato: str = "estrato", valor: str = "prueba"):
    """Filtra y devuelve las filas del conjunto de prueba dejando registro en la bitácora.
    La guarda vive en la lectura y no en las métricas porque es el único punto de salida
    de los datos: evita que filtros exploratorios en el cuaderno miren la prueba sin aviso.
    No bloquea una segunda corrida para permitir correcciones legítimas, pero deja registro
    en git para que cualquier uso repetido sea visible en el diff durante la revisión.
    """
    if not final:
        raise ValueError(
            "La partición de prueba solo debe evaluarse al final con el modelo definitivo. "
            f"Para desarrollo o validación usa: pares[pares[{col!r}] != {valor!r}]"
        )
    if not motivo or not motivo.strip():
        raise ValueError("Debes especificar un 'motivo' para evaluar el conjunto de prueba.")
    prueba = pares[pares[col] == valor]
    if col_estrato in prueba:
        conteo = prueba[col_estrato].value_counts()
        print(f"Evaluando partición de prueba ({len(prueba):,} filas):")
        for estrato, n in conteo.items():
            print(f"  - {estrato}: {n:,}")
    bitacora = Path(raiz) / "experimentos" / BITACORA
    bitacora.parent.mkdir(parents=True, exist_ok=True)
    existe = bitacora.exists()
    with open(bitacora, mode="a", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        if not existe:
            escritor.writerow(["fecha", "autor", "commit", "filas", "motivo"])
        escritor.writerow([
            date.today().isoformat(),
            _autor(Path(raiz)),
            _git("rev-parse", "--short", "HEAD", raiz=Path(raiz)) or "",
            len(prueba),
            motivo.strip(),
        ])
    return prueba


def sha256(ruta: Path) -> str:
    """Huella de un archivo, leído por bloques (el de actividad pesa 74 MB)."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _git(*args: str, raiz: Path) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return r.stdout.strip()


def _autor(raiz: Path) -> str:
    """BIOACTIVE_AUTOR, o el primer nombre de `git config user.name`, en minúsculas."""
    nombre = os.environ.get("BIOACTIVE_AUTOR") or _git("config", "user.name", raiz=raiz) or ""
    corto = re.sub(r"[^a-z0-9]", "", (nombre.split() or [""])[0].lower())
    return corto or "anon"


def _version(paquete: str) -> str | None:
    try:
        return metadata.version(paquete)
    except metadata.PackageNotFoundError:
        return None


def exigir_corrida_reproducible(*, definitiva: bool, permitir_sucio: bool = False,
                                raiz: Path = RAIZ) -> list[str]:
    """Las dos cosas que hay que mirar **antes** de correr, porque después no se arreglan.

    `entorno()` las registra fielmente, y ahí está el problema: registrar bien que la
    corrida no se puede reproducir no la hace reproducible. Las dos salieron de revisar
    corridas ya hechas, no de una comprobación:

    1. **El árbol sucio.** `arbol_sucio: true` quiere decir que el código que corrió no
       es el del commit que la corrida registra, así que nadie —ni tú en diciembre— puede
       volver a esa cifra desde el registro. La guarda cuenta solo los seguidos, porque un
       archivo suelto no cambia ninguna cifra. En una corrida definitiva es un defecto, y
       aquí **aborta**; con `permitir_sucio=True` solo avisa, que es lo que quiere una
       corrida de humo o una prueba a medio escribir. Si hay archivos sin seguimiento,
       informa con un aviso pero no aborta.
    2. **El autor.** `_autor` deriva el primer nombre de `git config user.name`, y para
       quien lo tenga puesto como nombre completo sin espacios sale un identificador de
       27 caracteres que no se parece a los `antonio`, `artemio` e `ingrid` del resto de
       `experimentos/`. El nombre de la carpeta se cita en documentos, así que renombrarla
       después obliga a corregirlos. Se arregla con `BIOACTIVE_AUTOR`.

    Devuelve los avisos que encontró, para que quien llame los registre si quiere.
    """
    avisos = []
    autor = _autor(Path(raiz))
    if not os.environ.get("BIOACTIVE_AUTOR") and len(autor) > 12:
        avisos.append(
            f"el autor de la corrida saldria «{autor}» ({len(autor)} caracteres), que no "
            "sigue la convencion de experimentos/; definelo con BIOACTIVE_AUTOR"
        )
    estado = _git("status", "--porcelain", "--untracked-files=all", raiz=Path(raiz))
    lineas = estado.splitlines() if estado else []
    sucio = any(not ln.startswith("??") for ln in lineas)
    sueltos = sum(1 for ln in lineas if ln.startswith("??"))
    if sucio:
        avisos.append(
            "el arbol esta sucio: el codigo que corre no es el del commit que se registra, "
            "asi que la cifra no se podra reproducir desde entorno.json"
        )
    if sueltos > 0:
        avisos.append(
            f"hay {sueltos} archivo(s) sin seguimiento en el arbol (informativo; no ensucia)"
        )
    for a in avisos:
        print(f"AVISO: {a}", file=sys.stderr)
    if definitiva and sucio and not permitir_sucio:
        raise SystemExit(
            "ABORTA: no se lanza una corrida definitiva con el arbol sucio. Haz commit, o "
            "pasa --arbol-sucio si de verdad quieres una cifra que no se puede reproducir."
        )
    return avisos


def entorno(raiz: Path = RAIZ, datos: list[Path] | None = None) -> dict:
    """Todo lo que cambia una cifra sin cambiar el código: commit, sistema, versiones, datos.

    `arbol_sucio` cuenta **solo los archivos seguidos**, porque es lo único que responde a la
    pregunta que la bandera existe para responder: si el código que corrió es el del `commit`
    de al lado. Un archivo sin seguimiento no cambia ninguna cifra, y contarlo hacía que una
    carpeta de `experimentos/` recién creada ensuciara la corrida siguiente —`experimentos/
    README.md` documentaba el efecto y pedía intercalar un commit para esquivarlo—. Los
    sueltos se cuentan aparte, en `sin_seguimiento`, que informa y no acusa.
    """
    estado = _git("status", "--porcelain", "--untracked-files=all", raiz=raiz)
    lineas = estado.splitlines() if estado else []
    lock = raiz / "requirements.lock"
    return {
        "commit": _git("rev-parse", "HEAD", raiz=raiz),
        "arbol_sucio": None if estado is None else any(
            not ln.startswith("??") for ln in lineas),
        "sin_seguimiento": None if estado is None else sum(
            1 for ln in lineas if ln.startswith("??")),
        "sistema": platform.platform(),
        "python": platform.python_version(),
        "paquetes": {p: _version(p) for p in PAQUETES},
        "lock_sha256": sha256(lock) if lock.exists() else None,
        "datos_sha256": {Path(d).resolve().relative_to(raiz).as_posix(): sha256(Path(d))
                         for d in datos or []},
    }


class Corrida:
    """Contexto que crea `experimentos/<id>/` y lo completa al salir sin error."""

    def __init__(self, nombre: str, *, decision: str, params: dict, semillas: list[int],
                 datos: list[Path] | None = None, autor: str | None = None,
                 fecha: str | None = None, raiz: Path = RAIZ):
        if not DECISION.match(decision):
            raise ValueError(f"decisión {decision!r} no tiene la forma de docs/decisiones.md "
                             "(C.x, 1.x, 2.x)")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", nombre):
            raise ValueError(f"nombre {nombre!r}: solo letras, dígitos, «_» y «-»")
        self.raiz = Path(raiz)
        self.id = "-".join([fecha or date.today().isoformat(), autor or _autor(self.raiz),
                            decision, nombre])
        self.carpeta = self.raiz / "experimentos" / self.id
        self.decision = decision
        self.params = dict(params)
        self.semillas = list(semillas)
        self.datos = [Path(d) for d in datos or []]
        self._metricas: dict | None = None
        self._inicio = 0.0
        self._entorno: dict = {}

    def metricas(self, valores: dict) -> None:
        """Las métricas de la corrida (escalares o dicts de escalares; nada de registros)."""
        self._metricas = dict(valores)

    def __enter__(self) -> Corrida:
        # El entorno se captura antes de que el script escriba su producto: si no, un script
        # cuyo resultado es un archivo versionado siempre registraría `arbol_sucio: true`.
        self._entorno = entorno(self.raiz, self.datos)
        self.carpeta.mkdir(parents=True)  # FileExistsError si ya existe: no se sobrescribe
        self._inicio = time.time()
        return self

    def __exit__(self, tipo, valor, traza) -> bool:
        if tipo is not None:
            _borrar(self.carpeta)
            return False
        if self._metricas is None:
            _borrar(self.carpeta)
            raise RuntimeError("la corrida terminó sin llamar a metricas()")
        env = self._entorno
        env["decision"] = self.decision
        env["duracion_s"] = round(time.time() - self._inicio, 1)
        (self.carpeta / "params.yaml").write_text(
            yaml.safe_dump({"decision": self.decision, "semillas": self.semillas,
                            "params": self.params}, allow_unicode=True, sort_keys=False))
        _json(self.carpeta / "metricas.json", self._metricas)
        _json(self.carpeta / "entorno.json", env)
        (self.carpeta / "comando.txt").write_text(_comando(self.raiz) + "\n")
        _a_mlflow(self, env)
        return False


def _comando(raiz: Path) -> str:
    """El comando sin rutas de la máquina: versión de Python y el script relativo al repositorio."""
    guion, *resto = sys.argv or [""]
    try:
        guion = Path(guion).resolve().relative_to(raiz).as_posix()
    except ValueError:
        pass
    return shlex.join([f"python{platform.python_version()}", guion, *resto])


def _json(ruta: Path, objeto: dict) -> None:
    ruta.write_text(json.dumps(objeto, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _borrar(carpeta: Path) -> None:
    for f in carpeta.glob("*"):
        f.unlink()
    carpeta.rmdir()


def _a_mlflow(c: Corrida, env: dict) -> None:
    """Si MLflow está instalado, registra la corrida en `mlruns/` (ignorado por git)."""
    try:
        import mlflow
    except ImportError:
        return
    mlflow.set_tracking_uri((c.raiz / "mlruns").as_uri())
    mlflow.set_experiment(c.decision)
    with mlflow.start_run(run_name=c.id):
        mlflow.log_params({k: str(v) for k, v in c.params.items()})
        mlflow.set_tags({"commit": env["commit"] or "", "decision": c.decision})
        mlflow.log_metrics({k: v for k, v in c._metricas.items()
                            if isinstance(v, (int, float))})
