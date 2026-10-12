import hashlib
import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verificar_datos", RAIZ / "scripts/verificar_datos.py")
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)


def test_huella_de_un_archivo(tmp_path):
    f = tmp_path / "a.csv"
    f.write_bytes(b"x,y\n1,2\n")
    assert vd.huella(f) == {"sha256": hashlib.sha256(b"x,y\n1,2\n").hexdigest(), "bytes": 8}


def test_un_puntero_lfs_da_la_huella_del_contenido_real(tmp_path):
    oid = "ab" * 32
    f = tmp_path / "grande.csv"
    f.write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize 123\n")
    assert vd.huella(f) == {"sha256": oid, "bytes": 123}


def test_comparar_detecta_cambio_falta_y_nuevo():
    a = {"x": {"sha256": "1", "bytes": 1}, "y": {"sha256": "2", "bytes": 1}}
    b = {"x": {"sha256": "9", "bytes": 1}, "z": {"sha256": "3", "bytes": 1}}
    assert vd.comparar(a, a) == []
    assert vd.comparar(a, b) == ["cambió: x", "falta: y", "sin registrar: z"]


def test_el_manifiesto_del_repositorio_coincide():
    """El manifiesto versionado describe los datos que hay en el árbol."""
    import json
    esperado = json.loads((RAIZ / "data/MANIFEST.json").read_text())
    assert vd.comparar(esperado, vd.calcular(RAIZ)) == []
