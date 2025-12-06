# EstandaresProyecto

# 🧬 Proyecto de Integración de Datos Clínicos de Melanoma

Este proyecto implementa un flujo de trabajo completo (**ETL**) para la gestión, almacenamiento y visualización de datos clínicos y genómicos de pacientes con melanoma. 

El sistema procesa datos crudos, los enriquece con fuentes externas (**OncoKB, UniProt**), los almacena en una base de datos NoSQL (**MongoDB**) y genera reportes web automáticos (**HTML**) mediante tecnologías semánticas (**XML/XSLT**).

---

## 🚀 Funcionalidades Principales

El proyecto consta de tres fases automatizadas por un orquestador principal:

1.  **ETL y Enriquecimiento (Python):** 
    *   Limpia y estandariza datos clínicos (pacientes, muestras) y genómicos (mutaciones).
    *   Descarga información biológica actualizada desde APIs externas.
    *   Transforma datos tabulares en estructuras JSON anidadas.
2.  **Persistencia de Datos (MongoDB):** 
    *   Carga automática de los datos procesados a MongoDB Atlas.
3.  **Generación de Reportes (XML/XSLT):** 
    *   Consulta la base de datos.
    *   Transforma los resultados JSON a XML.
    *   Aplica plantillas XSLT para generar dashboards HTML visuales.

---

## 📂 Estructura del Proyecto

El sistema utiliza rutas dinámicas para funcionar en cualquier entorno.

```text
EstandaresProyecto/
│
├── cleaned_data/             # 📂 Datos JSON generados (Salida del Paso 1)
├── resultados/
│   └── mongo_a_html/         # 📊 Reportes HTML finales (Salida del Paso 3)
│
├── codigo/
│   ├── datos/                # 📄 Datos crudos de entrada (txt/csv)
│   └── scripts/
│       ├── run_project.py          # ⚡ SCRIPT PRINCIPAL (Orquestador)
│       ├── conversion_mongobd.py   # Script de limpieza y ETL
│       ├── mongoxml_to_html.py     # Script de consultas y reportes
│       ├── queries.txt             # Definición de consultas a Mongo
│       └── template.xslt           # Plantilla de estilo para el HTML
│
└── README.md


---

## 🛠️ Requisitos e Instalación

### Prerrequisitos
*   **Python 3.8+**
*   Una cuenta y cluster en **MongoDB Atlas** (o una instancia local).

### Instalación de dependencias
Ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install pandas pymongo requests lxml
```

---

## ▶️ Ejecución

Gracias al script principal `run_project.py`, todo el flujo se ejecuta con un solo comando desde la raíz del proyecto o desde la carpeta de scripts.

**Comando principal:**

```bash
python codigo/scripts/run_project.py
```

### ¿Qué sucede al ejecutarlo?

1.  **Paso 1:** Se leen los `.txt` de `codigo/datos/`, se consulta OncoKB/UniProt y se generan archivos `.json` en `cleaned_data/`.
2.  **Paso 2:** Se conecta a MongoDB y sube las colecciones (`patients`, `samples`, `variants`, etc.).
3.  **Paso 3:** Se ejecutan las consultas definidas en `queries.txt` y se generan los reportes en `resultados/mongo_a_html/`.

---

## ⚙️ Configuración

Si se necesita cambiar la base de datos, habrá que editar el archivo `codigo/scripts/run_project.py`:

```python
# run_project.py

MONGO_URI = "mongodb+srv://TU_USUARIO:TU_PASSWORD@tu-cluster.mongodb.net/..."
DB_NAME = "NombreDeTuBaseDeDatos"
```

---

## 📊 Tecnologías Utilizadas

*   **Lenguaje:** Python
*   **Base de Datos:** MongoDB
*   **Formatos de Intercambio:** JSON, XML
*   **Transformación y Vistas:** XSLT, HTML5
*   **APIs Externas:** OncoKB, UniProt

---

## ✒️ Autores

*   Karen Michell Herrera Sierra
*   Gabriela Milenova Yordanova
*   Achraf Ousti El Moussati
*   Anabel Yu Flores Moral
*   Sebastián Joel Rozenblum
*   *Universidad de Málaga (UMA)*
