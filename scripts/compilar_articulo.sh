#!/bin/sh
# Compila a PDF un artículo de docs/reportes/ con TeX Live en Docker (pdfLaTeX + Biber), sin instalar
# LaTeX en la máquina. La primera vez construye la imagen `tex-art` (unos 4 GB, varios minutos).
#
#     sh scripts/compilar_articulo.sh                      # el entregable de la rúbrica (una columna)
#     sh scripts/compilar_articulo.sh articulo-cientifico  # el artículo científico (doble columna)
#     sh scripts/compilar_articulo.sh resumen-ejecutivo    # el resumen ejecutivo (entrega 8)
#
# Toma el nombre de la carpeta bajo docs/reportes/ y compila el .tex que se llama igual que ella
# (articulo/articulo.tex, articulo-cientifico/articulo-cientifico.tex). Deja el PDF junto al .tex.
# Se compila en una copia, porque la bibliografía, el logo y las figuras son enlaces simbólicos que
# Docker no sigue; `cp -RL` los resuelve.
set -e
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
NOMBRE=${1:-articulo}
CARPETA="$RAIZ/docs/reportes/$NOMBRE"
TMP=$(mktemp -d)

# El .tex se llama como la carpeta; si no existe así, se prueba con guiones bajos
# (resumen-ejecutivo/resumen_ejecutivo.tex, que es como lo nombra la plantilla del curso).
if [ ! -f "$CARPETA/$NOMBRE.tex" ]; then
  ARCHIVO=$(echo "$NOMBRE" | tr '-' '_')
else
  ARCHIVO=$NOMBRE
fi
if [ ! -f "$CARPETA/$ARCHIVO.tex" ]; then
  echo "no existe $CARPETA/$NOMBRE.tex ni $CARPETA/$ARCHIVO.tex" >&2
  exit 1
fi

if ! docker image inspect tex-art >/dev/null 2>&1; then
  echo "construyendo la imagen tex-art (solo la primera vez)..."
  docker run --name tex-art-build texlive/texlive:latest-medium \
    tlmgr install collection-latexextra collection-bibtexextra collection-pictures collection-fontsrecommended
  docker commit tex-art-build tex-art >/dev/null
  docker rm tex-art-build >/dev/null
fi

cp -RL "$CARPETA/." "$TMP/"
docker run --rm -v "$TMP":/work -w /work tex-art latexmk -pdf -quiet -interaction=nonstopmode "$ARCHIVO.tex"
cp "$TMP/$ARCHIVO.pdf" "$CARPETA/$ARCHIVO.pdf"
echo "listo: $CARPETA/$ARCHIVO.pdf"
rm -rf "$TMP"
