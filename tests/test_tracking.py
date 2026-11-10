import json

import pytest
import yaml

from src.tracking import Corrida, exigir_corrida_reproducible, sha256


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


def test_un_archivo_sin_seguimiento_no_ensucia_el_arbol(tmp_path):
    """Lo que la bandera responde es si corrió el código del commit, y un archivo suelto no.

    Contándolos, una carpeta de `experimentos/` recién creada ensuciaba la corrida siguiente,
    así que 9 de las 46 corridas de `main` llevan `arbol_sucio: true` sin que se sepa si
    alguna corrió código modificado. Se cuentan aparte.
    """
    _repo(tmp_path)
    (tmp_path / "corrida-de-antes").mkdir()
    (tmp_path / "corrida-de-antes" / "metricas.json").write_text("{}\n")
    with _corrida(tmp_path, datos=[]) as c:
        c.metricas({"x": 1})
    entorno = json.loads((c.carpeta / "entorno.json").read_text())
    assert entorno["arbol_sucio"] is False
    assert entorno["sin_seguimiento"] == 1


def test_un_archivo_seguido_modificado_si_ensucia_y_se_cuenta_aparte(tmp_path):
    _repo(tmp_path)
    (tmp_path / "salida.csv").write_text("editado a mano\n")
    (tmp_path / "suelto.txt").write_text("basura\n")
    with _corrida(tmp_path, datos=[]) as c:
        c.metricas({"x": 1})
    entorno = json.loads((c.carpeta / "entorno.json").read_text())
    assert entorno["arbol_sucio"] is True
    assert entorno["sin_seguimiento"] == 1


def test_una_corrida_definitiva_con_el_arbol_sucio_aborta(tmp_path, monkeypatch):
    """Registrar bien que una cifra no se puede reproducir no la hace reproducible."""
    monkeypatch.setenv("BIOACTIVE_AUTOR", "t")
    _repo(tmp_path)
    (tmp_path / "salida.csv").write_text("sin commitear\n")
    with pytest.raises(SystemExit, match="arbol sucio"):
        exigir_corrida_reproducible(definitiva=True, raiz=tmp_path)


def test_el_arbol_sucio_solo_avisa_si_la_corrida_no_es_definitiva(tmp_path, monkeypatch):
    monkeypatch.setenv("BIOACTIVE_AUTOR", "t")
    _repo(tmp_path)
    (tmp_path / "salida.csv").write_text("sin commitear\n")
    # Una corrida de humo se lanza con el árbol sucio a propósito: es código a medio escribir.
    avisos = exigir_corrida_reproducible(definitiva=False, raiz=tmp_path)
    assert any("arbol" in a for a in avisos)
    # Y una definitiva también, si quien la lanza lo dice explícitamente.
    assert exigir_corrida_reproducible(definitiva=True, permitir_sucio=True, raiz=tmp_path)


def test_la_guarda_informa_de_los_sueltos_sin_abortar(tmp_path, monkeypatch):
    """Un archivo suelto no cambia ninguna cifra: la guarda informa pero no aborta."""
    monkeypatch.setenv("BIOACTIVE_AUTOR", "t")
    _repo(tmp_path)
    (tmp_path / "suelto.txt").write_text("archivo no seguido\n")
    avisos = exigir_corrida_reproducible(definitiva=True, raiz=tmp_path)
    assert any("sin seguimiento" in a for a in avisos)


def test_un_arbol_limpio_no_da_avisos(tmp_path, monkeypatch):
    monkeypatch.setenv("BIOACTIVE_AUTOR", "t")
    _repo(tmp_path)
    assert exigir_corrida_reproducible(definitiva=True, raiz=tmp_path) == []


def test_avisa_del_autor_largo_que_no_sigue_la_convencion(tmp_path, monkeypatch):
    """`antonio` y `joseantoniovazquezmartinez` nombran la misma carpeta de distinta forma."""
    monkeypatch.delenv("BIOACTIVE_AUTOR", raising=False)
    import subprocess
    _repo(tmp_path)
    subprocess.run(["git", "config", "user.name", "JoseAntonioVazquezMartinez"],
                   cwd=tmp_path, check=True)
    avisos = exigir_corrida_reproducible(definitiva=True, raiz=tmp_path)
    assert any("BIOACTIVE_AUTOR" in a for a in avisos), avisos
    # Con la variable puesta, el aviso desaparece aunque git siga diciendo lo mismo.
    monkeypatch.setenv("BIOACTIVE_AUTOR", "antonio")
    assert exigir_corrida_reproducible(definitiva=True, raiz=tmp_path) == []


def test_comando_sin_rutas_absolutas(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", [str(tmp_path / "scripts" / "exp.py"), "--rapido"])
    with _corrida(tmp_path) as c:
        c.metricas({"x": 1})
    comando = (c.carpeta / "comando.txt").read_text().split()
    assert comando[0].startswith("python3.") and comando[1:] == ["scripts/exp.py", "--rapido"]


def test_datos_sha256_usa_rutas_posix(tmp_path):
    sub = tmp_path / "data" / "processed"
    sub.mkdir(parents=True)
    f = sub / "archivo.parquet"
    f.write_text("x")
    with _corrida(tmp_path, datos=[f]) as c:
        c.metricas({"x": 1})
    env = json.loads((c.carpeta / "entorno.json").read_text())
    assert "data/processed/archivo.parquet" in env["datos_sha256"]
