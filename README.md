# Bioactive AI: Plataforma de IA para la predicción y priorización de compuestos bioactivos

[![Publicar sitio](https://github.com/AntonioVazquezMartinez/Bioactive-AI/actions/workflows/pages.yml/badge.svg)](https://github.com/AntonioVazquezMartinez/Bioactive-AI/actions/workflows/pages.yml)
[![Sitio](https://img.shields.io/website?url=https%3A%2F%2Fantoniovazquezmartinez.github.io%2FBioactive-AI%2F&label=sitio&up_message=en%20l%C3%ADnea&down_message=ca%C3%ADdo&color=brightgreen)](https://antoniovazquezmartinez.github.io/Bioactive-AI/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![RDKit](https://img.shields.io/badge/RDKit-2026.03.6-8C1D40)](https://www.rdkit.org/)
[![Quarto](https://img.shields.io/badge/Quarto-1.10-39729E?logo=quarto&logoColor=white)](https://quarto.org/)
[![Datos](https://img.shields.io/badge/datos-CC0%20%2B%20CC%20BY--NC-lightgrey)](https://antoniovazquezmartinez.github.io/Bioactive-AI/contenido/datos.html)


Este repositorio contiene el código fuente, los datos, y la documentación del Proyecto Integrador correspondiente a la **Maestría en Inteligencia Artificial Aplicada** del Tecnológico de Monterrey (TC5035.10).

## Descripción del Proyecto

**Bioactive AI** es una plataforma basada en Inteligencia Artificial diseñada para predecir la actividad biológica y clasificar o priorizar compuestos bioactivos de origen natural. El objetivo principal es identificar compuestos con potencial neuroprotector y nootrópico a través del análisis integrado de descriptores químicos, estructurales, biológicos y multi-ómicos.

El proyecto se desarrolla en colaboración con el **Departamento de Bioingeniería** del Tecnológico de Monterrey, bajo el patrocinio de la **Dra. Mariana Martínez Ávila** (Profesor Investigador SNII 1).

### Dominio de Aplicación
- **Modelos predictivos (Supervisados):** Utilización de algoritmos de Machine Learning para correlacionar características estructurales y químicas de los compuestos con su efectividad biológica.

---

## Estructura del Repositorio

Para mantener el orden y la reproducibilidad, los documentos y el código están organizados de la siguiente manera:

```text
bioactive-ai/
├── data/           # datos: raw/ (originales), external/ (de terceros y de la patrocinadora), processed/ (listos para modelar)
├── notebooks/      # un número es un avance (01 a 05) y el 06 es el cuaderno para la patrocinadora; una letra es un análisis compañero
├── src/            # código reutilizable: data_prep/, features/, models/, evaluation/, inferencia.py y tracking.py
├── scripts/        # experimentos, figuras, compilación de los documentos y verificaciones
├── tests/          # pruebas: cifras repetidas, cuadernos, documentos y datos
├── models/         # los dos modelos finales (models/finales/) y lo que hace falta para usarlos sin los datos
├── experimentos/   # una carpeta por corrida registrada: parámetros, entorno y métricas
├── docs/           # documentación, decisiones, reportes y literatura
└── presentacion-final.qmd, index.qmd, _quarto.yml   # el sitio y la presentación final
```

No se enumeran aquí los archivos de cada carpeta, porque la lista envejece cada semana: se ven con `ls` y el sitio publica el
índice de [entregas y avances](https://antoniovazquezmartinez.github.io/Bioactive-AI/contenido/reportes/index.html).

---

## Equipo 7

* **Ingrid Pamela Ruiz Puga** (A01021209)
* **Artemio Santiago Padilla Robles** (A01796613)
* **José Antonio Vázquez Martínez** (A01797208)

---

## Configuración Inicial

Para reproducir este proyecto de manera local, clona este repositorio y configura el entorno virtual:

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/bioactive-ai.git

# Moverse al directorio del proyecto
cd bioactive-ai

# Crear un entorno virtual (opcional pero recomendado)
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate

# Instalar las dependencias
pip install -r requirements.txt
```
