import json

import pytest
import yaml

from src.tracking import Corrida, sha256


def _corrida(tmp_path, **kw):
    datos = tmp_path / "d.csv"
    datos.write_text("a,b\n1,2\n")
    args = dict(decision="1.7", params={"L": 64}, semillas=[0, 1], datos=[datos],
                autor="ana", fecha="2026-10-14", raiz=tmp_path)
    return Corrida("L", **{**args, **kw})


def test_escribe_los_cuatro_archivos(tmp_path):
    with _corrida(tmp_path) as c:
        c.metricas({"MCC": 0.7})
    assert c.id == "2026-10-14-ana-1.7-L"
    assert sorted(p.name for p in c.carpeta.iterdir()) == [
        "comando.txt", "entorno.json", "metricas.json", "params.yaml"]
    p = yaml.safe_load((c.carpeta / "params.yaml").read_text())
    assert p == {"decision": "1.7", "semillas": [0, 1], "params": {"L": 64}}
    assert json.loads((c.carpeta / "metricas.json").read_text()) == {"MCC": 0.7}
    env = json.loads((c.carpeta / "entorno.json").read_text())
    assert env["datos_sha256"] == {"d.csv": sha256(tmp_path / "d.csv")}


def test_no_sobrescribe(tmp_path):
    with _corrida(tmp_path) as c:
        c.metricas({"x": 1})
    with pytest.raises(FileExistsError), _corrida(tmp_path):
        pass


def test_una_corrida_fallida_no_deja_carpeta(tmp_path):
    with pytest.raises(ValueError), _corrida(tmp_path) as c:
        raise ValueError("falla")
    assert not c.carpeta.exists()


def test_sin_metricas_falla(tmp_path):
    with pytest.raises(RuntimeError), _corrida(tmp_path) as c:
        pass
    assert not c.carpeta.exists()


@pytest.mark.parametrize("decision", ["7", "1", "x.1", "1.7.2"])
def test_decision_con_forma_invalida(tmp_path, decision):
    with pytest.raises(ValueError):
        _corrida(tmp_path, decision=decision)
