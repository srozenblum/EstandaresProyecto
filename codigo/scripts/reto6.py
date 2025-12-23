#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import csv
import re

from rdflib import Graph


# =========================================================
# Utilidades
# =========================================================

def split_queries(text: str):
    # Captura bloques que empiezan por "# Consulta N" hasta antes de la siguiente "# Consulta M"
    pattern = re.compile(r"(?ms)^\s*#\s*Consulta\s+\d+.*?(?=^\s*#\s*Consulta\s+\d+|\Z)")
    blocks = [m.group(0).strip() for m in pattern.finditer(text)]

    # De cada bloque, nos quedamos desde el primer PREFIX/SELECT/ASK/CONSTRUCT/DESCRIBE
    cleaned = []
    for b in blocks:
        lines = b.splitlines()
        start = 0
        for i, ln in enumerate(lines):
            s = ln.strip().upper()
            if s.startswith("PREFIX") or s.startswith("SELECT") or s.startswith("ASK") or s.startswith("CONSTRUCT") or s.startswith("DESCRIBE"):
                start = i
                break
        q = "\n".join(lines[start:]).strip()
        if q:
            cleaned.append(q)
    return cleaned



def write_select_results(csv_path: Path, result):
    """
    Guarda resultados SELECT en CSV.
    """
    vars_ = list(result.vars)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([str(v) for v in vars_])

        for row in result:
            writer.writerow(
                [str(row.get(v)) if row.get(v) is not None else "" for v in vars_]
            )


# =========================================================
# Main
# =========================================================

def main():
    ap = argparse.ArgumentParser(
        description="Reto 6: Ejecución automática de consultas SPARQL sobre grafo RDF"
    )
    ap.add_argument(
        "--graph",
        default=None,
        help="Ruta al grafo RDF (por defecto: resultados/reto5/grafo_melanoma.ttl)",
    )
    ap.add_argument(
        "--queries",
        required=True,
        help="Fichero Consultas SPARQL.txt",
    )
    ap.add_argument(
        "--format",
        default="turtle",
        help="Formato del grafo RDF (turtle por defecto)",
    )

    args = ap.parse_args()

    # -----------------------------------------------------
    # Raíz del repositorio
    # -----------------------------------------------------
    BASE_DIR = Path(__file__).resolve().parents[2]

    # Grafo por defecto (salida del reto 5)
    if args.graph is None:
        graph_path = BASE_DIR / "resultados" / "reto5" / "grafo_melanoma.ttl"
    else:
        graph_path = Path(args.graph)

    # Carpeta de salida resultados/reto6
    RESULTS_DIR = BASE_DIR / "resultados" / "reto6"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------
    # Carga del grafo RDF
    # -----------------------------------------------------
    print(f"Cargando grafo RDF: {graph_path}")

    g = Graph()
    g.parse(graph_path, format=args.format)

    print(f"Tripletas cargadas: {len(g)}")

    # -----------------------------------------------------
    # Lectura y separación de consultas
    # -----------------------------------------------------
    queries_text = Path(args.queries).read_text(encoding="utf-8")
    queries = split_queries(queries_text)

    print(f"Consultas detectadas: {len(queries)}")

    # -----------------------------------------------------
    # Ejecución de consultas
    # -----------------------------------------------------
    for i, q in enumerate(queries, start=1):
        print(f"\nEjecutando Consulta {i}...")

        try:
            result = g.query(q)
        except Exception as e:
            print(f"ERROR en Consulta {i}: {e}")
            continue

        # SELECT
        if hasattr(result, "vars") and result.vars:
            csv_path = RESULTS_DIR / f"Consulta_{i}.csv"
            write_select_results(csv_path, result)
            print(f"✔ Resultados guardados en {csv_path}")

        # ASK
        elif isinstance(result, bool):
            txt_path = RESULTS_DIR / f"Consulta_{i}.txt"
            txt_path.write_text(str(result), encoding="utf-8")
            print(f"✔ Resultado booleano guardado en {txt_path}")

        # CONSTRUCT / DESCRIBE
        else:
            ttl_path = RESULTS_DIR / f"Consulta_{i}.ttl"
            result.serialize(destination=str(ttl_path), format="turtle")
            print(f"✔ Grafo resultado guardado en {ttl_path}")

    print("\nReto 6 completado correctamente.")


if __name__ == "__main__":
    main()
