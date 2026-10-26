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
    """Las filas de la partición de prueba, solo con `final=True` y dejando constancia.

    Fila 0.4 de `docs/roadmap-mlops.md`. La prueba se toca **una vez**, con el
    modelo ya elegido; el riesgo no es que alguien la mire a propósito, es que
    un `df[df.particion == "prueba"]` escrito para depurar se quede en el
    cuaderno y nadie lo note. Por eso la guarda vive en la **lectura** y no en
    el registro de métricas: es el único punto por el que la prueba sale del
    archivo.

    `final=True` escribe una línea en `experimentos/prueba.csv`, que se versiona.
    Que esté en git es lo que hace visible la segunda vez: un diff con dos
    líneas nuevas es una pregunta en la revisión, y un registro que vive solo en
    la máquina de quien corrió no la provoca.

    También imprime el tamaño de cada estrato, porque **el momento en que
    alguien pone `final=True` es el último momento en que se puede avisar**
    (#54, #91): la prueba trae 117 pares de solo NPASS y 229 mixtos contra más
    de 13,000 de solo ChEMBL, así que cualquier cifra sobre naturales sale con
    un intervalo ancho y conviene verlo venir antes de leer el resultado, no
    después.
    """
    if not final:
        raise RuntimeError(
            "la partición de prueba se evalúa una sola vez, con el modelo ya elegido "
            "(roadmap-mlops 0.4). Si es esa vez, llame tomar_prueba(..., final=True, "
            "motivo='por qué') y la corrida quedará anotada en experimentos/prueba.csv. "
            "Para entrenar y comparar modelos use las otras particiones: "
            f"pares[pares[{col!r}].ne({valor!r})]")
    if not motivo.strip():
        raise ValueError("tomar_prueba necesita `motivo`: qué modelo se evalúa y por qué es "
                         "el elegido. Es lo único que distingue una segunda vez legítima "
                         "de un descuido.")

    prueba = pares[pares[col] == valor]
    if col_estrato in prueba:
        conteo = prueba[col_estrato].value_counts()
        print(f"partición de prueba: {len(prueba):,} filas · " +
              " · ".join(f"{e} {n:,}" for e, n in conteo.items()))
        print("  cuidado: los estratos chicos dan intervalos anchos; léalos con su intervalo.")

    bitacora = Path(raiz) / "experimentos" / BITACORA
    nueva = not bitacora.exists()
    bitacora.parent.mkdir(parents=True, exist_ok=True)
    with open(bitacora, "a", encoding="utf-8", newline="") as f:
        if nueva:
            f.write("fecha,autor,commit,filas,motivo\n")
        f.write(",".join([date.today().isoformat(), _autor(Path(raiz)),
                          _git("rev-parse", "--short", "HEAD", raiz=Path(raiz)) or "",
                          str(len(prueba)), '"' + motivo.replace('"', "'") + '"']) + "\n")
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


def entorno(raiz: Path = RAIZ, datos: list[Path] | None = None) -> dict:
    """Todo lo que cambia una cifra sin cambiar el código: commit, sistema, versiones, datos."""
    estado = _git("status", "--porcelain", raiz=raiz)
    lock = raiz / "requirements.lock"
    return {
        "commit": _git("rev-parse", "HEAD", raiz=raiz),
        "arbol_sucio": None if estado is None else bool(estado),
        "sistema": platform.platform(),
        "python": platform.python_version(),
        "paquetes": {p: _version(p) for p in PAQUETES},
        "lock_sha256": sha256(lock) if lock.exists() else None,
        "datos_sha256": {str(Path(d).resolve().relative_to(raiz)): sha256(Path(d))
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
        guion = str(Path(guion).resolve().relative_to(raiz))
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
