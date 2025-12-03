"""
Script para automatizar el flujo MongoDB → XML → HTML mediante XSLT,
adaptado a la estructura JSON anidada del proyecto (patients, samples,
variants, oncokb_genes, uniprot).

Cada documento MongoDB puede tener múltiples niveles de diccionarios,
listas y subcampos. Este script convierte correctamente dicha estructura
a XML válido y semántico, y luego aplica XSLT para generar HTML.
"""

import argparse
import json
from pymongo import MongoClient
from lxml import etree
import os
import re


# -------------------------------------------------------------
# NORMALIZACIÓN DE CLAVES PARA XML
# -------------------------------------------------------------
def normalize_key(key):
    """
    Convierte claves MongoDB en nombres válidos XML.
    """
    if key == "_id":
        return "id"
    key = key.replace(".", "_")
    key = key.replace("$", "DOLLAR_")
    return key


# -------------------------------------------------------------
# LECTOR DE CONSULTAS
# -------------------------------------------------------------
def load_queries(filepath):
    queries = {}
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                queries[current] = ""
            else:
                if current:
                    queries[current] += line + "\n"
    return queries


# -------------------------------------------------------------
# PARSEADOR DE CONSULTAS MongoDB estilo Compass
# -------------------------------------------------------------
def parse_mongo_query(raw_query):
    raw_query = raw_query.replace("\n", "")
    match = re.match(r"db\.(\w+)\.(\w+)\((.*)\)", raw_query)

    if not match:
        raise ValueError(f"Consulta no válida: {raw_query}")

    collection, op, args = match.groups()
    args = args.strip()

    # ==============================================================================
    # FIND
    # ==============================================================================
    if op == "find":
        query = json.loads(args) if args else {}
        return collection, lambda col: col.find(query)

    # ==============================================================================
    # AGGREGATE
    # ==============================================================================
    if op == "aggregate":
        pipeline = json.loads(args)
        return collection, lambda col: col.aggregate(pipeline)

    raise ValueError(f"Operación Mongo no soportada: {op}")


# -------------------------------------------------------------
# CONVERSIÓN GENERAL JSON → XML (ROBUSTA)
# -------------------------------------------------------------
def build_xml(parent, obj):
    """
    Convierte cualquier estructura JSON (dict, list, valor)
    en un árbol XML correcto.
    """

    if isinstance(obj, dict):
        parent.set("type", "object")
        for k, v in obj.items():
            node = etree.SubElement(parent, normalize_key(k))
            build_xml(node, v)

    elif isinstance(obj, list):
        parent.set("type", "list")
        for item in obj:
            node = etree.SubElement(parent, "element")
            build_xml(node, item)

    else:
        parent.text = "" if obj is None else str(obj)


def json_to_xml(json_obj):
    root = etree.Element("root")
    build_xml(root, json_obj)
    return root


# -------------------------------------------------------------
# APLICACIÓN XSLT
# -------------------------------------------------------------
def apply_xslt(xml_doc, xslt_path):
    xslt = etree.parse(xslt_path)
    transform = etree.XSLT(xslt)
    return transform(xml_doc)


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
def main():

    parser = argparse.ArgumentParser(description="Mongo → XML → XSLT → HTML (adaptado JSON anidado)")
    parser.add_argument("--uri", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--queries", required=True)
    parser.add_argument("--xslt", required=True)
    parser.add_argument("--outdir", required=True)

    args = parser.parse_args()

    # Conectar a Mongo
    try:
        client = MongoClient(
            args.uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000
        )
        db = client[args.db]
        #from pymongo import MongoClient
        #client = MongoClient("mongodb+srv://0611136468_db_user:123@proyecto-mzimiy1.i7rrfdu.mongodb.net/Estandares_proyecto?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
        #db = client["Estandares_proyecto"]
        print("Collections:", db.list_collection_names())
    except Exception as e:
        print(f"[ERROR] Conexión fallida: {e}")
        return


    # Leer consultas
    try:
        queries = load_queries(args.queries)
    except Exception as e:
        print(f"[ERROR] leyendo queries: {e}")
        return

    # Crear carpeta de salida
    os.makedirs(args.outdir, exist_ok=True)

    # Ejecutar cada consulta
    for name, raw_query in queries.items():
        print(f"\n[INFO] Ejecutando consulta '{name}'")

        try:
            collection_name, op = parse_mongo_query(raw_query)
            results = list(op(db[collection_name]))

            if not results:
                print(f"[WARN] La consulta '{name}' no devolvió resultados.")

            # Convertir JSON → XML
            xml_root = json_to_xml(results)
            xml_doc = etree.ElementTree(xml_root)

            xml_path = os.path.join(args.outdir, f"{name}.xml")
            xml_doc.write(xml_path, pretty_print=True, encoding="utf-8")
            print(f"[OK] XML generado: {xml_path}")

            # Aplicar XSLT → HTML
            html_doc = apply_xslt(xml_doc, args.xslt)
            html_path = os.path.join(args.outdir, f"{name}.html")
            html_doc.write(html_path, pretty_print=True, method="html", encoding="utf-8")
            print(f"[OK] HTML generado: {html_path}")

        except Exception as e:
            print(f"[ERROR] procesando '{name}': {e}")


if __name__ == "__main__":
    main()

"""
Se ejecuta así:

python codigo\scripts\mongoxml_to_html.py  
    --uri "mongodb+srv://0611136468_db_user:jJlwmCC65NhN5kvk@cluster0.5eoq4b5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  
    --db EstadaresProyecto 
    --queries codigo\scripts\queries.txt  
    --xslt codigo\scripts\template.xslt  
    --outdir resultados\mongo_a_html
"""
