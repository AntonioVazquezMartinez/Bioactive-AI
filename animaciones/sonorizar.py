#!/usr/bin/env python3
"""Pone la voz sobre el video de una escena, en el segundo exacto de cada tramo.

    python animaciones/sonorizar.py cierre
    python animaciones/sonorizar.py --todas --calidad alta

**No concatena los audios.** Cada tramo se coloca en el segundo donde la
escena lo abrió, que `voz/offsets.json` registra al renderizar. Concatenarlos
y confiar en que las pausas coincidan es lo que deja el montaje desfasado sin
que nadie se entere: basta que una animación cambie medio segundo.

Si la escena se re-renderiza, sus offsets cambian solos y esto los vuelve a
leer. Si cambia el guion, hay que regenerar el audio con `voz.py` — y la
comprobación de abajo lo detecta, porque el audio no cabría en su hueco.
"""

import argparse
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VOZ = RAIZ / "voz"
MEDIA = RAIZ / "media" / "videos"
CALIDADES = {"borrador": "480p15", "alta": "1080p60"}
from orden import ESCENAS


def duracion(ruta: Path) -> float:
    s = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True, check=True)
    return float(s.stdout.strip())


def sonorizar(escena: str, calidad: str) -> Path:
    offsets = json.loads((VOZ / "offsets.json").read_text())
    if escena not in offsets:
        raise SystemExit(f"{escena} no tiene offsets: renderiza la escena "
                         "primero, que los escribe al correr")
    tramos = offsets[escena]["tramos"]

    video = MEDIA / escena / CALIDADES[calidad] / f"{ESCENAS[escena]}.mp4"
    if not video.exists():
        raise SystemExit(f"falta {video.relative_to(RAIZ.parent)}")
    largo_video = duracion(video)

    pistas, filtros, etiquetas = [], [], []
    for i, (n, inicio) in enumerate(sorted(tramos.items(), key=lambda kv: int(kv[0]))):
        pista = VOZ / f"{escena}-{n}.mp3"
        if not pista.exists():
            raise SystemExit(f"falta {pista.name}: córrelo con «voz.py --solo "
                             f"{escena}»")
        largo = duracion(pista)
        fin = inicio + largo
        # **Que quepa antes del siguiente tramo**, no solo dentro del video.
        # Comprobar solo lo segundo es lo que dejó pasar cuatro y seis
        # segundos de voces encimadas en `intervalo` y `particion`: el tramo 1
        # seguía hablando cuando el 2 empezaba.
        siguiente = sorted(float(v) for v in tramos.values() if float(v) > inicio)
        tope = siguiente[0] if siguiente else largo_video
        if fin > tope + 0.05:
            que = (f"el tramo siguiente, que abre en {tope:.1f} s"
                   if siguiente else f"el final del video, en {tope:.1f} s")
            raise SystemExit(
                f"el tramo {n} de {escena} empieza en {inicio:.1f} s y dura "
                f"{largo:.1f} s, así que se encima {fin - tope:.1f} s con "
                f"{que}. Alarga la escena, no aceleres la voz.")
        pistas += ["-i", str(pista)]
        # `adelay` en milisegundos, a los dos canales.
        ms = int(round(inicio * 1000))
        filtros.append(f"[{i + 1}:a]adelay={ms}|{ms}[a{i}]")
        etiquetas.append(f"[a{i}]")

    mezcla = (f"{''.join(etiquetas)}amix=inputs={len(etiquetas)}:"
              "normalize=0:duration=longest[mezclado];"
              # Norma de sonoridad para web: sin esto, una escena suena más
              # fuerte que otra según cuánto hable.
              "[mezclado]loudnorm=I=-16:TP=-1.5:LRA=11[normalizado];"
              # **Silencio hasta el final de la imagen.** La voz acaba antes
              # que la escena —para eso está la holgura—, y si la pista termina
              # ahí, `ensamblar.py` encadena los audios uno tras otro y cada
              # escena adelanta la voz de las siguientes. Eran 15.4 s de
              # desfase acumulado al final del video, creciendo escena a
              # escena, sin que nada fallara.
              f"[normalizado]apad=whole_dur={largo_video:.3f}[voz]")
    # **Sin `-shortest`.** La mezcla acaba cuando termina la última pista de
    # voz, que casi siempre es antes que la imagen: con `-shortest`, ffmpeg
    # tiraba el video sobrante en silencio. Eran 0.9 s en la mayoría de las
    # escenas, pero 7.6 s en `intervalo` y 4.1 s en el cierre —el plano final
    # del video entero—, y nada fallaba: el archivo salía bien formado y más
    # corto. Sin la bandera, la duración la manda la imagen y el audio
    # simplemente termina antes.
    destino = video.with_name(f"{ESCENAS[escena]}-con-voz.mp4")
    orden = (["ffmpeg", "-v", "error", "-y", "-i", str(video)] + pistas
             + ["-filter_complex", ";".join(filtros) + ";" + mezcla,
                "-map", "0:v", "-map", "[voz]", "-c:v", "copy",
                # **48 kHz y dos canales, explícitos.** Sin fijarlos, el
                # formato lo decidía la cadena de filtros: `loudnorm` remuestrea
                # internamente y el resultado salía en 96 kHz mono, que es AAC
                # válido y que varios reproductores —QuickTime entre ellos— no
                # decodifican. El video se veía y no se oía, sin que nada
                # fallara ni avisara: `ffprobe` informaba de un flujo de audio
                # correcto y con nivel.
                "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
                str(destino)])
    subprocess.run(orden, check=True)
    print(f"  {escena:<14} {largo_video:>6.1f} s · {len(tramos)} tramos"
          f" → {destino.name}")
    return destino


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("escenas", nargs="*", choices=list(ESCENAS) + [[]])
    cli.add_argument("--todas", action="store_true")
    cli.add_argument("--calidad", default="borrador", choices=list(CALIDADES))
    args = cli.parse_args()

    escenas = list(ESCENAS) if args.todas else (args.escenas or [])
    if not escenas:
        raise SystemExit("di qué escena, o --todas")
    for escena in escenas:
        sonorizar(escena, args.calidad)


if __name__ == "__main__":
    main()
