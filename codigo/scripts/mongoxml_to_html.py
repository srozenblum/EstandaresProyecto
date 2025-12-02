"""
Script para automatizar el flujo MongoDB → XML → HTML mediante XSLT.
El programa recibe una URI de conexión, una base de datos, un archivo con consultas,
una plantilla XSLT y un directorio de salida. Para cada consulta, obtiene los datos 
desde MongoDB, genera un XML con los resultados y posteriormente transforma dicho XML 
en un archivo HTML usando la plantilla XSLT proporcionada. Este script está diseñado 
para ser reutilizable con distintas bases de datos, consultas y plantillas.
"""

import argparse
import json
from pymongo import MongoClient
from lxml import etree
import os
import re


# Lee consultas desde un archivo de texto
def load_queries(filepath):
    queries = {}
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Cuando la línea está entre corchetes, es el nombre de la consulta
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                queries[current] = ""
            # Se acumulan las líneas que forman la consulta
            else:
                if current:
                    queries[current] += line + "\n"
    return queries


# Parsear consultas tipo db.collection.aggregate(...) o db.collection.find(...)
def parse_mongo_query(raw_query):
    raw_query = raw_query.replace("\n", "")
    match = re.match(r"db\.(\w+)\.(\w+)\((.*)\)", raw_query)

    if not match:
        raise ValueError(f"Consulta no válida: {raw_query}")

    collection, op, args = match.groups()
    args = args.strip()

    # Consultas tipo find
    if op == "find":
        query = json.loads(args) if args else {}
        return collection, lambda col: col.find(query)

    # Consultas tipo aggregate
    if op == "aggregate":
        pipeline = json.loads(args)
        return collection, lambda col: col.aggregate(pipeline)

    raise ValueError(f"Operación Mongo no soportada: {op}")


# Convertir un objeto JSON en estructura XML
def json_to_xml(json_obj):
    root = etree.Element("root")

    def build(parent, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                e = etree.SubElement(parent, k)
                build(e, v)
        elif isinstance(obj, list):
            for item in obj:
                e = etree.SubElement(parent, "item")
                build(e, item)
        else:
            parent.text = str(obj)

    build(root, json_obj)
    return root


# Aplicar transformación XSLT a un XML dado
def apply_xslt(xml_doc, xslt_path):
    xslt = etree.parse(xslt_path)
    transform = etree.XSLT(xslt)
    return transform(xml_doc)


def main():

    # Definición de parámetros del script
    parser = argparse.ArgumentParser(description="Mongo → XML → XSLT → HTML")
    parser.add_argument("--uri", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--queries", required=True)
    parser.add_argument("--xslt", required=True)
    parser.add_argument("--outdir", required=True)

    args = parser.parse_args()

    # Conexión a MongoDB
    try:
        client = MongoClient(args.uri)
        db = client[args.db]
    except Exception as e:
        print(f"[ERROR] Conexión a Mongo fallida: {e}")
        return

    # Cargar archivo de consultas
    try:
        queries = load_queries(args.queries)
    except Exception as e:
        print(f"[ERROR] leyendo queries: {e}")
        return

    # Crear carpeta de salida si no existe
    os.makedirs(args.outdir, exist_ok=True)

    # Procesar cada consulta
    for name, raw_query in queries.items():
        print(f"\n[INFO] Ejecutando consulta: {name}")

        try:
            # Interpretar consulta Mongo
            collection_name, op = parse_mongo_query(raw_query)

            # Ejecutar y convertir resultados
            data = list(op(db[collection_name]))

            if not data:
                print(f"[WARN] La consulta '{name}' no devolvió resultados.")

            # Convertir JSON a XML
            xml_root = json_to_xml(data)
            xml_doc = etree.ElementTree(xml_root)

            # Guardar XML generado
            xml_path = os.path.join(args.outdir, f"{name}.xml")
            xml_doc.write(xml_path, pretty_print=True, encoding="utf-8")
            print(f"[OK] Guardado XML: {xml_path}")

            # Aplicar XSLT para generar HTML
            html_doc = apply_xslt(xml_doc, args.xslt)

            html_path = os.path.join(args.outdir, f"{name}.html")
            html_doc.write(html_path, pretty_print=True, method="html", encoding="utf-8")
            print(f"[OK] Guardado HTML: {html_path}")

        except Exception as e:
            print(f"[ERROR] procesando '{name}': {e}")


if __name__ == "__main__":
    main()
# se ejecuata con el siguite comando python ProyectoT2.py --uri "mongodb://localhost:27017" --db Estandares_proyecto --queries queries.txt --xslt template.xslt --outdir out