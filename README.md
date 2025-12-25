# EstandaresProyecto

# 🧬 Proyecto de Integración de Datos Clínicos de Melanoma

Este proyecto implementa un flujo de trabajo completo (**ETL**) para la gestión, almacenamiento y visualización de datos clínicos y genómicos de pacientes con melanoma. 

El sistema procesa datos crudos, los enriquece con fuentes externas (**OncoKB, UniProt**), los almacena en una base de datos NoSQL (**MongoDB**) y genera reportes web automáticos (**HTML**) mediante tecnologías semánticas (**XML/XSLT**).

Además, el proyecto incorpora una **capa semántica basada en ontologías OWL**, que permite representar formalmente el conocimiento clínico y genómico, aplicar razonamiento automático y realizar consultas avanzadas mediante **SPARQL**.

---

## 🚀 Funcionalidades Principales

El proyecto consta de cuatro fases automatizadas por un orquestador principal:

1. **ETL y Enriquecimiento (Python):**  
   * Limpia y estandariza datos clínicos (pacientes, muestras) y genómicos (mutaciones).
   * Descarga información biológica actualizada desde APIs externas.
   * Transforma datos tabulares en estructuras JSON anidadas.

2. **Persistencia de Datos (MongoDB):**  
   * Carga automática de los datos procesados a MongoDB Atlas.

3. **Generación de Reportes (XML/XSLT):**  
   * Consulta la base de datos.
   * Transforma los resultados JSON a XML.
   * Aplica plantillas XSLT para generar dashboards HTML visuales.

4. **Modelado Ontológico y Razonamiento Semántico (OWL/SPARQL):**  
   * Representa el dominio clínico-genómico mediante una ontología OWL.
   * Permite inferir nuevo conocimiento mediante razonamiento automático.
   * Facilita consultas semánticas avanzadas con SPARQL.

---

## 🧠 Ontología y Razonamiento Semántico

La ontología ha sido diseñada y validada utilizando **Protégé**, reflejando fielmente la estructura de las colecciones almacenadas en MongoDB.

### 📐 Modelado Ontológico

#### Clases principales
- `Paciente`
- `Muestra`
- `Variante`
- `Gen`
- `Proteina`

#### Clases auxiliares (estructuras anidadas)
- `Supervivencia`, `Clinica`, `Demografia`, `Tumor`
- `Recurrencia`, `Tratamiento`
- `UbicacionVariante`, `Coordenadas`
- `ClasificacionVariante`, `Alelos`, `AlelosTumor`

#### Relaciones (propiedades de objeto)
- `Paciente → tieneMuestra → Muestra`
- `Muestra → tieneVariante → Variante`
- `Variante → afectaAGen → Gen`
- `Gen → tieneProteina → Proteina`
- Relaciones adicionales para representar estructuras anidadas del modelo JSON.

#### Propiedades de datos
Se definen propiedades para representar información literal como:
- identificadores (`idPaciente`, `idMuestra`, `idVariante`),
- datos clínicos (edad, sexo, estado de supervivencia),
- métricas genómicas (TMB, coordenadas, alelos),
- anotaciones moleculares (HGVSc, HGVSp).

---

### 🧩 Individuos

Se han añadido manualmente múltiples **individuos** para todas las clases principales y auxiliares, permitiendo:
- obtener múltiples resultados en las consultas SPARQL,
- validar el modelo ontológico,
- demostrar la inferencia automática de conocimiento.

---

### 🤖 Razonamiento Automático

Se ha aplicado el **razonador HermiT**  para inferir nuevo conocimiento a partir de clases definidas y restricciones.

Ejemplos de inferencias:
- `PacienteFallecido`: pacientes cuyo estado de supervivencia global es *DECEASED*.
- `MuestraMetastasis`: muestras cuyo tipo es *Metastasis*.

Estas inferencias mejoran la accesibilidad y la capacidad de consulta de la información.

---

### 🔎 Consultas SPARQL

Se han diseñado y ejecutado múltiples consultas **SPARQL** para cubrir todo el espacio de búsqueda de la ontología, incluyendo:
- relaciones entre pacientes, muestras y variantes,
- información clínica y de supervivencia,
- genes afectados y proteínas asociadas,
- resultados inferidos por el razonador.

---

### 📁 Archivos Ontológicos

Los archivos OWL del proyecto se encuentran en el directorio:

```text
├── codigo/
│   ├── datos/                
│   │   └── ontologia/
│   │       ├── ontologia_.owl
│   │       └── ontologia_reasoned.owl


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
