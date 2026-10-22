#!/usr/bin/env python3
"""Une las escenas en un solo video, sin perder que sean piezas sueltas.

**Por qué no es un `cat` de archivos.** Las escenas tienen que seguir siendo
independientes —cada una se inserta junto a la decisión que explica, se
re-renderiza sola y se regraba sola— y a la vez verse de corrido. Este script
es la única pieza que sabe el orden, y el orden vive aquí y en ningún otro
sitio.

    python animaciones/ensamblar.py                 # borrador, 480p
    python animaciones/ensamblar.py --calidad alta  # 1080p
    python animaciones/ensamblar.py --solo linaje intervalo

**Qué comprueba antes de unir**, porque son los tres modos de que salga un
video mal sin que nadie se entere:

1. Que estén **todas** las partes del orden declarado. Si falta una, dice cuál
   y con qué comando se renderiza, en vez de entregar un video incompleto.
2. Que todas sean de **la misma calidad**. Mezclar 480p con 1080p produce un
   archivo que se reproduce pero se ve mal en la mitad.
3. Que ninguna esté **más vieja que su escena**. Si se tocó `linaje.py` y no
   se volvió a renderizar, el video llevaría la versión anterior — que es
   exactamente cómo el mazo se desincronizó dos veces de sus cifras.

Las transiciones son fundidos de medio segundo con `xfade`. No hay efectos: la
atención tiene que estar en lo que se explica.
"""

import argparse
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
MEDIA = RAIZ / "media" / "videos"
CALIDADES = {"borrador": "480p15", "alta": "1080p60"}
FUNDIDO = 0.5

from orden import ORDEN


def _parte(modulo: str, escena: str, calidad: str, con_voz: bool = True) -> Path:
    """La parte con voz si existe, y si no la muda.

    Prefiere la sonorizada a propósito: una vez que hay voz, montar las mudas
    por descuido da un video silencioso que parece terminado.
    """
    carpeta = MEDIA / modulo / CALIDADES[calidad]
    sonora = carpeta / f"{escena}-con-voz.mp4"
    if con_voz and sonora.exists():
        return sonora
    return carpeta / f"{escena}.mp4"


def _tiene_audio(ruta: Path) -> bool:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=codec_type", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True)
    return "audio" in salida.stdout


def _duracion(ruta: Path) -> float:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ruta)], capture_output=True, text=True, check=True)
    return float(salida.stdout.strip())


def _comprobar(partes: list[tuple[str, str, str]], calidad: str) -> list[Path]:
    rutas, faltan, viejas = [], [], []
    for modulo, escena, _ in partes:
        ruta = _parte(modulo, escena, calidad)
        fuente = RAIZ / f"{modulo}.py"
        if not ruta.exists():
            faltan.append((modulo, escena))
            continue
        if fuente.exists() and fuente.stat().st_mtime > ruta.stat().st_mtime:
            viejas.append(modulo)
        rutas.append(ruta)

    if faltan:
        print("Faltan partes. Renderízalas y vuelve a correr esto:\n")
        for modulo, escena in faltan:
            bandera = "-ql" if calidad == "borrador" else "-qh"
            print(f"    ../env-anim/bin/python -m manim {bandera}"
                  f" {modulo}.py {escena}")
        raise SystemExit(1)
    if viejas:
        raise SystemExit(
            "Estas partes son más viejas que su escena, así que el video "
            "llevaría la versión anterior: " + ", ".join(viejas))
    return rutas


def ensamblar(partes: list[tuple[str, str, str]], calidad: str,
              destino: Path) -> None:
    rutas = _comprobar(partes, calidad)
    duraciones = [_duracion(r) for r in rutas]
    total = sum(duraciones) - FUNDIDO * (len(rutas) - 1)

    print(f"{len(rutas)} partes · {total:.0f} s en total\n")
    for (modulo, _, papel), d in zip(partes, duraciones):
        print(f"  {modulo:<14} {d:>5.1f} s   {papel}")

    orden = ["ffmpeg", "-v", "error", "-y"]
    for r in rutas:
        orden += ["-i", str(r)]

    # Encadenado: cada fundido empieza justo antes de que acabe lo acumulado.
    filtros, etiqueta, acumulado = [], "[0:v]", duraciones[0]
    for i in range(1, len(rutas)):
        salida = f"[v{i}]"
        filtros.append(
            f"{etiqueta}[{i}:v]xfade=transition=fade:duration={FUNDIDO}"
            f":offset={acumulado - FUNDIDO:.3f}{salida}")
        etiqueta = salida
        acumulado += duraciones[i] - FUNDIDO
    # El audio se encadena con `acrossfade` en los mismos puntos que el video:
    # si solo se cruzara la imagen, la voz se cortaría en seco en cada unión.
    # Todas con voz o ninguna. Mezclarlas no da un video a medio sonorizar:
    # `ffmpeg` descarta el audio y devuelve uno mudo que parece terminado, que
    # es justo el descuido contra el que avisa `_parte`.
    audios = [_tiene_audio(r) for r in rutas]
    if any(audios) and not all(audios):
        mudas = [m for (m, _, _), a in zip(partes, audios) if not a]
        raise SystemExit(
            "unas partes traen voz y otras no, así que el montaje saldría mudo. "
            "Sonoriza estas antes de ensamblar: " + ", ".join(mudas))
    con_audio = all(audios)
    if con_audio:
        etiqueta_a, acum = "[0:a]", duraciones[0]
        for i in range(1, len(rutas)):
            salida_a = f"[s{i}]"
            filtros.append(f"{etiqueta_a}[{i}:a]acrossfade=d={FUNDIDO}"
                           f":c1=tri:c2=tri{salida_a}")
            etiqueta_a = salida_a
            acum += duraciones[i] - FUNDIDO
    if filtros:
        orden += ["-filter_complex", ";".join(filtros), "-map", etiqueta]
        if con_audio:
            orden += ["-map", etiqueta_a]
    orden += ["-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18"]
    if con_audio:
        # El mismo formato que `sonorizar.py`: 48 kHz y estéreo, explícitos.
        orden += ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
    orden += [str(destino)]

    print("\nuniendo…", flush=True)
    subprocess.run(orden, check=True)
    print(f"[listo] {destino.relative_to(RAIZ.parent)}"
          f"  ({destino.stat().st_size / 1e6:.1f} MB,"
          f" {_duracion(destino):.0f} s)")


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--calidad", default="borrador", choices=list(CALIDADES))
    cli.add_argument("--solo", nargs="+", metavar="MODULO",
                     help="arma solo con estas partes, en este orden")
    cli.add_argument("--salida", type=Path)
    args = cli.parse_args()

    partes = ORDEN
    if args.solo:
        por_nombre = {m: (m, e, p) for m, e, p in ORDEN}
        desconocidas = [m for m in args.solo if m not in por_nombre]
        if desconocidas:
            raise SystemExit(f"no están en el orden: {', '.join(desconocidas)}."
                             f" Hay: {', '.join(por_nombre)}")
        partes = [por_nombre[m] for m in args.solo]

    destino = args.salida or (MEDIA / f"Bioactive-{args.calidad}.mp4")
    destino.parent.mkdir(parents=True, exist_ok=True)
    ensamblar(partes, args.calidad, destino)


if __name__ == "__main__":
    main()
