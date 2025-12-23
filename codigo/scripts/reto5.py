#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict, Iterable, Optional

from pymongo import MongoClient
from bson import ObjectId, DBRef

from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD


# =========================
# Namespaces
# =========================

MEL = Namespace("http://example.org/melanoma_es#")
BASE = Namespace("http://example.org/melanoma_es/")  # individuos


# =========================
# Utilidades
# =========================

def safe_predicate(ns: Namespace, key: str) -> URIRef:
    key = key.strip().replace(" ", "_")
    key = "".join(ch for ch in key if ch.isalnum() or ch in ["_", "-"])
    if not key:
        key = "field"
    return ns[key]


def doc_uri(collection: str, _id: Any) -> URIRef:
    return URIRef(f"{str(BASE)}{collection}/{str(_id)}")


def is_primitive(v: Any) -> bool:
    return isinstance(v, (str, int, float, bool)) or v is None or isinstance(v, (datetime, date))


def to_literal(v: Any) -> Literal:
    if v is None:
        return Literal("", datatype=XSD.string)
    if isinstance(v, bool):
        return Literal(v, datatype=XSD.boolean)
    if isinstance(v, int):
        return Literal(v, datatype=XSD.integer)
    if isinstance(v, float):
        return Literal(v, datatype=XSD.decimal)
    if isinstance(v, datetime):
        return Literal(v.isoformat(), datatype=XSD.dateTime)
    if isinstance(v, date):
        return Literal(v.isoformat(), datatype=XSD.date)
    return Literal(str(v), datatype=XSD.string)


# =========================
# Carga de ontología
# =========================

def load_ontology_classes(owl_path: str) -> set:
    g = Graph()
    g.parse(owl_path)
    return set(g.subjects(RDF.type, OWL.Class))


# =========================
# Conversión de valores
# =========================

def add_value(
    g: Graph,
    subj: URIRef,
    pred: URIRef,
    value: Any,
    collection_hint: Optional[str] = None,
) -> None:

    if isinstance(value, list):
        for item in value:
            add_value(g, subj, pred, item, collection_hint)
        return

    if isinstance(value, DBRef):
        g.add((subj, pred, doc_uri(value.collection, value.id)))
        return

    if isinstance(value, ObjectId):
        if collection_hint:
            g.add((subj, pred, doc_uri(collection_hint, value)))
        else:
            g.add((subj, pred, URIRef(f"{str(BASE)}ref/{str(value)}")))
        return

    if isinstance(value, dict):
        obj = doc_uri(collection_hint, value["_id"]) if "_id" in value else BNode()
        g.add((subj, pred, obj))

        for k, v in value.items():
            if k == "_id":
                continue
            p2 = safe_predicate(MEL, k)
            hint2 = None
            if k.lower().endswith(("id", "_id")):
                hint2 = k[:-2] if k.lower().endswith("id") else k[:-3]
                hint2 = hint2.strip("_").lower() or None
            add_value(g, obj, p2, v, hint2)
        return

    if is_primitive(value):
        g.add((subj, pred, to_literal(value)))
        return

    g.add((subj, pred, Literal(str(value), datatype=XSD.string)))


# =========================
# Documento Mongo -> RDF
# =========================

def add_document(
    g: Graph,
    collection: str,
    doc: Dict[str, Any],
    classes_in_ont: set,
) -> None:

    _id = doc.get("_id")
    subj = doc_uri(collection, _id) if _id else BNode()

    class_uri = MEL[collection]
    g.add((subj, RDF.type, class_uri))

    if class_uri not in classes_in_ont:
        g.add((class_uri, RDF.type, RDFS.Class))

    for k, v in doc.items():
        if k == "_id":
            continue

        pred = safe_predicate(MEL, k)

        hint = None
        if k.lower().endswith(("id", "_id")):
            hint = k[:-2] if k.lower().endswith("id") else k[:-3]
            hint = hint.strip("_").lower() or None

        add_value(g, subj, pred, v, hint)


# =========================
# Exportación principal
# =========================

def export_mongo_to_rdf(
    mongo_uri: str,
    db_name: str,
    ontology_owl: str,
    out_path: str,
    include_collections: Optional[Iterable[str]] = None,
) -> None:

    classes_in_ont = load_ontology_classes(ontology_owl)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    g = Graph()
    g.bind("mel", MEL)
    g.bind("base", BASE)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)

    collections = include_collections or db.list_collection_names()

    for col in collections:
        if col.startswith("system."):
            continue
        for doc in db[col].find():
            add_document(g, col, doc, classes_in_ont)

    g.serialize(destination=out_path, format="turtle")
    print(f"✔ Grafo RDF generado: {out_path}")
    print(f"✔ Tripletas: {len(g)}")


# =========================
# Main
# =========================

def main():
    ap = argparse.ArgumentParser(description="Reto 5: MongoDB → RDF (melanoma_es)")
    ap.add_argument("--mongo-uri", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--ontology", required=True)
    ap.add_argument("--collections", default="")
    ap.add_argument("--out", default=None)

    args = ap.parse_args()

    # 👉 RAÍZ DEL REPOSITORIO (EstandaresProyecto)
    BASE_DIR = Path(__file__).resolve().parents[2]

    # 👉 resultados/reto5 (al mismo nivel que codigo/)
    RESULTS_DIR = BASE_DIR / "resultados" / "reto5"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    out_path = RESULTS_DIR / "grafo_melanoma.ttl" if args.out is None else Path(args.out)

    cols = [c.strip() for c in args.collections.split(",") if c.strip()] or None

    export_mongo_to_rdf(
        mongo_uri=args.mongo_uri,
        db_name=args.db,
        ontology_owl=args.ontology,
        out_path=str(out_path),
        include_collections=cols,
    )


if __name__ == "__main__":
    main()
