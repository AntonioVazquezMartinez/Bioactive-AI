# Bioactive AI: Plataforma de IA para la predicción y priorización de compuestos bioactivos

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
│
├── data/                   # Carpeta para almacenar los datos (ignorar en git los datos crudos/pesados)
│   ├── raw/                # Datos originales sin procesar
│   ├── processed/          # Datos limpios y listos para modelado
│   └── external/           # Datos de fuentes externas (LipidMaps, PubChem, etc.)
│
├── notebooks/              # Jupyter Notebooks para exploración y prototipado
│   ├── 01_EDA.ipynb        # Análisis Exploratorio de Datos (Avance 1)
│   ├── 02_Feature_Eng.ipynb# Ingeniería de características (Avance 2)
│   ├── 03_Baseline.ipynb   # Modelos base (Avance 3)
│   └── 04_Models.ipynb     # Modelos alternativos y evaluación (Avance 4 y 5)
│
├── src/                    # Código fuente del proyecto (scripts de Python)
│   ├── data_prep/          # Scripts para limpieza y transformación
│   ├── features/           # Scripts para generación de descriptores químicos
│   └── models/             # Scripts de entrenamiento y evaluación
│
├── models/                 # Modelos entrenados y serializados (.pkl, .h5, etc.)
│
├── docs/                   # Documentación, entregables y presentaciones
│   ├── planteamiento/      # Entregables de las semanas 1 y 2
│   ├── reportes/           # Resumen ejecutivo y producto de difusión
│   └── referencias/        # Literatura médica y artículos base
│
├── .gitignore              # Archivos y carpetas a ignorar (ej. datos pesados, pycache)
├── requirements.txt        # Dependencias necesarias para ejecutar el proyecto
└── README.md               # Este archivo
```

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
