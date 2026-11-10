#!/bin/sh
# Compila docs/reportes/articulo/articulo.tex a PDF con TeX Live en Docker (pdfLaTeX + Biber), sin instalar
# LaTeX en la máquina. La primera vez construye la imagen `tex-art` (unos 4 GB, varios minutos).
#
#     sh scripts/compilar_articulo.sh
#
# Deja el PDF en docs/reportes/articulo/articulo.pdf. Se compila en una copia, porque la bibliografía y el
# logo son enlaces simbólicos que Docker no sigue.
set -e
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
CARPETA="$RAIZ/docs/reportes/articulo"
TMP=$(mktemp -d)

if ! docker image inspect tex-art >/dev/null 2>&1; then
  echo "construyendo la imagen tex-art (solo la primera vez)..."
  docker run --name tex-art-build texlive/texlive:latest-medium \
    tlmgr install collection-latexextra collection-bibtexextra collection-pictures collection-fontsrecommended
  docker commit tex-art-build tex-art >/dev/null
  docker rm tex-art-build >/dev/null
fi

cp -RL "$CARPETA/." "$TMP/"
docker run --rm -v "$TMP":/work -w /work tex-art latexmk -pdf -quiet -interaction=nonstopmode articulo.tex
cp "$TMP/articulo.pdf" "$CARPETA/articulo.pdf"
echo "listo: $CARPETA/articulo.pdf"
rm -rf "$TMP"
