import json

import pytest
import yaml

from src.tracking import Corrida, sha256


def _corrida(tmp_path, **kw):
    args = dict(decision="1.7", params={"L": 64}, semillas=[0, 1], autor="ana",
                fecha="2026-10-14", raiz=tmp_path)
    if "datos" not in kw:
        datos = tmp_path / "d.csv"
        datos.write_text("a,b\n1,2\n")
        args["datos"] = [datos]
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


def _repo(tmp_path):
    import subprocess
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "salida.csv").write_text("v1\n")
    subprocess.run([*git, "add", "."], cwd=tmp_path, check=True)
    subprocess.run([*git, "commit", "-qm", "base"], cwd=tmp_path, check=True)


def test_arbol_sucio_se_mide_antes_de_que_el_script_escriba_su_producto(tmp_path):
    _repo(tmp_path)
    with _corrida(tmp_path, datos=[]) as c:
        (tmp_path / "salida.csv").write_text("v2\n")     # el script reescribe su CSV versionado
        c.metricas({"x": 1})
    assert json.loads((c.carpeta / "entorno.json").read_text())["arbol_sucio"] is False


def test_arbol_sucio_si_ya_lo_estaba_al_empezar(tmp_path):
    _repo(tmp_path)
    (tmp_path / "salida.csv").write_text("editado a mano\n")
    with _corrida(tmp_path, datos=[]) as c:
        c.metricas({"x": 1})
    assert json.loads((c.carpeta / "entorno.json").read_text())["arbol_sucio"] is True


def test_comando_sin_rutas_absolutas(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", [str(tmp_path / "scripts" / "exp.py"), "--rapido"])
    with _corrida(tmp_path) as c:
        c.metricas({"x": 1})
    comando = (c.carpeta / "comando.txt").read_text().split()
    assert comando[0].startswith("python3.") and comando[1:] == ["scripts/exp.py", "--rapido"]
