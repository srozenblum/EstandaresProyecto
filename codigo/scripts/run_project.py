import subprocess
import sys
import os
import json
from pymongo import MongoClient

# ==============================================================================
# ⚙️ CONFIGURACIÓN DE RUTAS GENÉRICAS (PORTABLE)
# ==============================================================================

# 1. Detectar dónde está ESTE archivo (run_project.py)
# Ejemplo: .../EstandaresProyecto/codigo/scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Calcular la Raíz del Proyecto (subiendo 2 niveles)
# Ejemplo: .../EstandaresProyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# 3. Definir rutas relativas calculadas
SCRIPT_CONVERSION = os.path.join(SCRIPT_DIR, "conversion_mongobd.py")
SCRIPT_REPORTES   = os.path.join(SCRIPT_DIR, "mongoxml_to_html.py")

# Carpetas de datos y resultados (siempre relativas a la raíz)
DIR_DATOS_LIMPIOS = os.path.join(PROJECT_ROOT, "cleaned_data")
DIR_RESULTADOS    = os.path.join(PROJECT_ROOT, "resultados", "mongo_a_html")

# Archivos de configuración para los reportes (están junto a los scripts)
QUERIES_FILE = os.path.join(SCRIPT_DIR, "queries.txt")
XSLT_FILE    = os.path.join(SCRIPT_DIR, "template.xslt")

# Configuración MongoDB
MONGO_URI = "mongodb+srv://0611136468_db_user:jJlwmCC65NhN5kvk@cluster0.5eoq4b5.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "EstadaresProyecto"

# Mapeo de archivos JSON a Colecciones Mongo
ARCHIVOS_A_COLECCIONES = {
    "patients.json": "patients",
    "samples.json": "samples",
    "variants.json": "variants",
    "oncokb_genes.json": "oncokb_genes",
    "uniprot.json": "uniprot"
}

# ==============================================================================
# PASO 1: CONVERSIÓN (ETL)
# ==============================================================================
def paso_1_conversion():
    print("\n" + "="*50)
    print("🚀 PASO 1: Ejecutando Conversión y Limpieza...")
    print("="*50)
    
    # Verificar que el script existe
    if not os.path.exists(SCRIPT_CONVERSION):
        print(f"❌ Error: No encuentro el script en: {SCRIPT_CONVERSION}")
        sys.exit(1)

    try:
        # sys.executable asegura que usamos el mismo Python del entorno virtual actual
        subprocess.run([sys.executable, SCRIPT_CONVERSION], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Falló la ejecución del script de conversión: {e}")
        sys.exit(1)

# ==============================================================================
# PASO 2: CARGA A MONGODB
# ==============================================================================
def paso_2_upload():
    print("\n" + "="*50)
    print("🚀 PASO 2: Subiendo datos a MongoDB...")
    print("="*50)

    if not os.path.exists(DIR_DATOS_LIMPIOS):
        print(f"❌ Error: La carpeta de datos limpios no existe: {DIR_DATOS_LIMPIOS}")
        sys.exit(1)

    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client[DB_NAME]
        
        for filename, col_name in ARCHIVOS_A_COLECCIONES.items():
            fpath = os.path.join(DIR_DATOS_LIMPIOS, filename)
            
            if os.path.exists(fpath):
                print(f"📥 Procesando: {filename} -> Colección: {col_name}")
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if data:
                    # Limpiar colección previa e insertar nuevos
                    db[col_name].delete_many({})
                    
                    if isinstance(data, list):
                        db[col_name].insert_many(data)
                        count = len(data)
                    else:
                        db[col_name].insert_one(data)
                        count = 1
                    print(f"   ✅ Insertados {count} documentos.")
                else:
                    print(f"   ⚠️ El archivo {filename} está vacío.")
            else:
                print(f"   ⚠️ Archivo no encontrado (se omite): {filename}")
        
        client.close()
    
    except Exception as e:
        print(f"❌ Error crítico en MongoDB: {e}")
        sys.exit(1)

# ==============================================================================
# PASO 3: REPORTES HTML
# ==============================================================================
def paso_3_reportes():
    print("\n" + "="*50)
    print("🚀 PASO 3: Generando Reportes HTML...")
    print("="*50)

    # Verificar inputs
    if not os.path.exists(QUERIES_FILE):
        print(f"❌ Falta el archivo queries.txt en: {QUERIES_FILE}")
        sys.exit(1)
    if not os.path.exists(XSLT_FILE):
        print(f"❌ Falta el archivo template.xslt en: {XSLT_FILE}")
        sys.exit(1)

    cmd = [
        sys.executable, SCRIPT_REPORTES,
        "--uri", MONGO_URI,
        "--db", DB_NAME,
        "--queries", QUERIES_FILE,
        "--xslt", XSLT_FILE,
        "--outdir", DIR_RESULTADOS
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Proceso finalizado. Resultados en:\n   {DIR_RESULTADOS}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generando reportes: {e}")
        sys.exit(1)

# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    print(f"📂 Raíz del proyecto detectada: {PROJECT_ROOT}")
    paso_1_conversion()
    paso_2_upload()
    paso_3_reportes()