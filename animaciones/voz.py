#!/usr/bin/env python3
"""Convierte la narración de los guiones en audio, y mide si cabe.

**La clave de la API va en el entorno y nunca en un archivo.** Este
repositorio es público: una clave en un commit sigue ahí aunque se borre
después.

    export ELEVENLABS_API_KEY=...
    python animaciones/voz.py              # todas las escenas
    python animaciones/voz.py --solo cierre
    python animaciones/voz.py --medir      # sin generar: solo compara duraciones

## Qué hace, y por qué así

Lee **solo las líneas de cita** de cada `guion/*.md`, que son la narración —el
resto son acotaciones y notas—, y genera un audio por escena. Después mide ese
audio contra el video de esa escena y escribe `voz/tiempos.json`.

Ese archivo es el que faltaba. Sin él, grabar deja el montaje en un estado que
solo se arregla a mano: las escenas tienen sus `wait()` escritos a ojo, y
`ensamblar.py` calcula los fundidos desde la duración del **video**. Con él,
una sola fuente dice cuánto dura cada tramo y qué escena hay que alargar.

**No estira el audio para que quepa.** Si la locución es más larga que su
escena, lo dice y hay que subir el `wait()` correspondiente y volver a
renderizar. Acelerar la voz para encajar es la forma fácil de volver el video
imposible de seguir, que es justo lo que se quiere evitar.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
GUIONES = RAIZ / "guion"
SALIDA = RAIZ / "voz"
TIEMPOS = SALIDA / "tiempos.json"
MEDIA = RAIZ / "media" / "videos"

# Miguel Paz. La eligió el equipo entre cuatro mexicanas, oyendo la frase más
# difícil del guion: decimales leídos y la sigla ChEMBL.
VOZ = "qK97aPuDo74niFLxjFrK"
MODELO = "eleven_multilingual_v2"

# El orden lo manda `ensamblar.py`; aquí solo hace falta saber qué escena es
# cuál para medir contra su video.
ESCENAS = {"apertura": "Apertura", "linaje": "Linaje", "intervalo": "Intervalo",
           "fingerprints": "Fingerprints", "particion": "Particion",
           "cierre": "Cierre"}


def _limpiar(texto: str) -> str:
    """El énfasis de markdown no se dice en voz alta."""
    return re.sub(r"\*+([^*]+)\*+", r"\1", texto).replace("—", ", ")


def narracion_por_tramo(guion: Path) -> list[dict]:
    """La narración partida por los encabezados `## N · Título`.

    **Un audio por tramo y no uno por escena**, porque es lo que permite
    sincronizar: cada acto de la escena espera exactamente lo que dura su
    tramo, y así el dibujo y la voz terminan juntos. Con un solo audio por
    escena, el único ajuste posible es el total.

    Solo se toman las líneas de cita. El resto del guion —acotaciones
    «*Entra con:*», notas de pronunciación— es para quien produce, no para
    quien narra: metería en el audio cosas como «entra con la tabla».
    """
    tramos, actual = [], None
    for linea in guion.read_text(encoding="utf-8").splitlines():
        encabezado = re.match(r"^##\s+(\d+)\s*·\s*(.+?)(?:\s*\*\(.*)?$", linea)
        if encabezado:
            actual = {"n": int(encabezado.group(1)),
                      "titulo": encabezado.group(2).strip(),
                      "parrafos": []}
            tramos.append(actual)
            continue
        if linea.lstrip().startswith("#"):
            actual = None          # «## Notas» y demás cierran la narración
            continue
        if actual is None or not linea.lstrip().startswith(">"):
            continue
        dicho = linea.lstrip()[1:].strip()
        if dicho:
            if actual["parrafos"] and actual["parrafos"][-1]:
                actual["parrafos"][-1] += " " + dicho
            else:
                actual["parrafos"].append(dicho)
        elif actual["parrafos"] and actual["parrafos"][-1]:
            actual["parrafos"].append("")

    for tr in tramos:
        parrafos = [p for p in tr["parrafos"] if p]
        tr["texto"] = _limpiar("\n\n".join(parrafos))
        del tr["parrafos"]
    return [t for t in tramos if t["texto"]]


def narracion(guion: Path) -> str:
    """Toda la narración de una escena, para contar palabras."""
    return "\n\n".join(t["texto"] for t in narracion_por_tramo(guion))


def duracion(ruta: Path) -> float:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ruta)], capture_output=True, text=True, check=True)
    return round(float(salida.stdout.strip()), 2)


def _video(escena: str, calidad: str = "480p15") -> Path | None:
    ruta = MEDIA / escena / calidad / f"{ESCENAS[escena]}.mp4"
    return ruta if ruta.exists() else None


def generar(escena: str, texto: str, clave: str, tramo: int | None = None) -> Path:
    destino = SALIDA / (f"{escena}.mp3" if tramo is None
                        else f"{escena}-{tramo}.mp3")
    cuerpo = json.dumps({
        "text": texto,
        "model_id": MODELO,
        # Estabilidad alta y poca exageración: es una narración explicativa,
        # no una lectura dramatizada.
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75,
                           "style": 0.0, "use_speaker_boost": True},
    }).encode()
    peticion = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOZ}",
        data=cuerpo, method="POST",
        headers={"xi-api-key": clave, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(peticion, timeout=180) as r:
            destino.write_bytes(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs respondió {e.code}: {e.read()[:200]!r}")
    return destino


HUELLAS = SALIDA / "huellas.json"


def _huella(texto: str) -> str:
    return hashlib.sha256(f"{VOZ}|{MODELO}|{texto}".encode()).hexdigest()[:16]


def _huellas() -> dict:
    return json.loads(HUELLAS.read_text()) if HUELLAS.exists() else {}


def _cambio(escena: str, tr: dict) -> bool:
    """Hay que volver a pedir este tramo si falta el mp3 o si cambió su texto.

    La huella es del **texto que se manda**, junto con la voz y el modelo: así
    editar una nota de producción del `.md`, o reordenar la sección, no cuesta
    cuota. Cambiar de voz sí la invalida, que es lo correcto.

    **Por qué existe.** `voz.py --solo linaje` regrababa los cuatro tramos de
    la escena —1,917 caracteres— para corregir una frase de 291. Y como la
    síntesis no devuelve dos veces la misma duración, regrabar de más movía
    `voz/tiempos.json` y obligaba a re-renderizar escenas que nadie había
    tocado. Con la huella, expandir el video cuesta lo que cuesta lo nuevo.
    """
    if not (SALIDA / f"{escena}-{tr['n']}.mp3").exists():
        return True
    return _huellas().get(f"{escena}-{tr['n']}") != _huella(tr["texto"])


def _anotar(escena: str, tr: dict) -> None:
    h = _huellas()
    h[f"{escena}-{tr['n']}"] = _huella(tr["texto"])
    HUELLAS.write_text(json.dumps(h, indent=1, ensure_ascii=False) + "\n")


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--solo", nargs="+", choices=list(ESCENAS))
    cli.add_argument("--rehacer", action="store_true",
                     help="regraba aunque el texto no haya cambiado")
    cli.add_argument("--medir", action="store_true",
                     help="no genera audio; solo compara lo que ya existe")
    args = cli.parse_args()

    clave = os.environ.get("ELEVENLABS_API_KEY", "")
    if not args.medir and not clave:
        raise SystemExit("falta ELEVENLABS_API_KEY en el entorno. No se "
                         "guarda en ningún archivo: este repositorio es público")

    SALIDA.mkdir(exist_ok=True)
    nuevos: list[str] = []
    escenas = args.solo or list(ESCENAS)
    tiempos = json.loads(TIEMPOS.read_text()) if TIEMPOS.exists() else {}

    for escena in escenas:
        guion = GUIONES / f"{escena}.md"
        if not guion.exists():
            print(f"{escena:<14} sin guion")
            continue

        print(f"\n{escena}")
        partes = narracion_por_tramo(guion)
        detalle, total = [], 0.0
        for tr in partes:
            audio = SALIDA / f"{escena}-{tr['n']}.mp3"
            if not args.medir:
                if args.rehacer or _cambio(escena, tr):
                    audio = generar(escena, tr["texto"], clave, tr["n"])
                    _anotar(escena, tr)
                    nuevos.append(f"{escena}-{tr['n']}")
            if not audio.exists():
                print(f"  tramo {tr['n']} · sin audio todavía")
                continue
            d = duracion(audio)
            total += d
            detalle.append({"n": tr["n"], "titulo": tr["titulo"],
                            "segundos": d,
                            "palabras": len(tr["texto"].split())})
            print(f"  tramo {tr['n']} · {tr['titulo']:<26} {d:>6.1f} s")

        video = _video(escena)
        d_video = duracion(video) if video else None
        tiempos[escena] = {"voz_s": round(total, 2), "video_s": d_video,
                           "tramos": detalle, "voz_id": VOZ, "modelo": MODELO}
        if d_video:
            falta = total - d_video
            print(f"  {'total':<34} {total:>6.1f} s  ·  video {d_video:.1f} s"
                  + (f"  → faltan {falta:.0f} s de animación" if falta > 0
                     else f"  → sobran {-falta:.0f} s"))

    TIEMPOS.write_text(json.dumps(tiempos, indent=1, ensure_ascii=False) + "\n")
    print(f"\n[guardado] {TIEMPOS.relative_to(RAIZ.parent)}")

    voz = sum(t["voz_s"] for t in tiempos.values())
    vid = sum(t["video_s"] or 0 for t in tiempos.values())
    print(f"narración {voz / 60:.1f} min · animación {vid / 60:.1f} min")
    if voz > vid:
        print("Las escenas se alargan hasta su narración; la voz no se acelera.")


if __name__ == "__main__":
    main()
