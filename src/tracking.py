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

    def metricas(self, valores: dict) -> None:
        """Las métricas de la corrida (escalares o dicts de escalares; nada de registros)."""
        self._metricas = dict(valores)

    def __enter__(self) -> Corrida:
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
        env = entorno(self.raiz, self.datos)
        env["decision"] = self.decision
        env["duracion_s"] = round(time.time() - self._inicio, 1)
        (self.carpeta / "params.yaml").write_text(
            yaml.safe_dump({"decision": self.decision, "semillas": self.semillas,
                            "params": self.params}, allow_unicode=True, sort_keys=False))
        _json(self.carpeta / "metricas.json", self._metricas)
        _json(self.carpeta / "entorno.json", env)
        (self.carpeta / "comando.txt").write_text(shlex.join([sys.executable, *sys.argv]) + "\n")
        _a_mlflow(self, env)
        return False


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
