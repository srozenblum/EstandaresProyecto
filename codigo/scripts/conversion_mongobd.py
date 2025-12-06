import os
import pandas as pd
import json
import math
import requests

# ============================================================
# 🔵 COLUMNAS PERMITIDAS
# ============================================================

PATIENT_COLUMNS = [
    "PATIENT_ID",
    "OS_MONTHS",
    "OS_STATUS",
    "DFS_MONTHS",
    "DFS_STATUS",
    "AGE_AT_DIAGNOSIS",
    "SEX",
    "RACE",
    "METASTASIS",
    "TIME_TO_RECURRENCE_MONTHS",
    "SITE_FIRST_RECURRENCE",
    "TREATMENT",
    "LYMPH_NODE_EXAMINED_COUNT",
    "PRIMARY_MELANOMA_TUMOR_ULCERATION"
]

SAMPLE_COLUMNS = [
    "PATIENT_ID",
    "SAMPLE_ID",
    "STAGE_AT_PRESENTATION",
    "PRIMARY_SITE",
    "SAMPLE_TYPE",
    "METASTATIC_SITE",
    "PRIMARY_DEPTH",
    "CANCER_TYPE",
    "CANCER_TYPE_DETAILED",
    "TMB_NONSYNONYMOUS"
]

MUTATION_COLUMNS = [
    "Tumor_Sample_Barcode",
    "Matched_Norm_Sample_Barcode",
    "Hugo_Symbol",
    "Chromosome",
    "Start_Position",
    "End_Position",
    "Strand",
    "Consequence",
    "Variant_Classification",
    "Variant_Type",
    "Reference_Allele",
    "Tumor_Seq_Allele1",
    "HGVSc",
    "HGVSp",
    "HGVSp_Short",
    "t_ref_count",
    "t_alt_count",
    "t_depth",
    "Mutation_Status",
    "Verification_Status",
    "Validation_Status"
]


# ============================================================
# 🔵 LIMPIEZA COMPLETA NaN
# ============================================================

def clean_nan(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str) and value.strip().lower() == "nan":
        return None
    return value


def clean_record(record):
    return {k: clean_nan(v) for k, v in record.items()}


# ============================================================
# 🔵 REESTRUCTURACIÓN DE PACIENTES
# ============================================================

def parse_status(status_str):
    if status_str is None:
        return None
    try:
        code, label = status_str.split(":", 1)
        return {"code": int(code), "label": label}
    except:
        return {"code": None, "label": status_str}


def restructure_patient(p):
    return {
        "patient_id": p["PATIENT_ID"],

        "survival": {
            "overall": {
                "months": p["OS_MONTHS"],
                "status": parse_status(p["OS_STATUS"])
            },
            "disease_free": {
                "months": p["DFS_MONTHS"],
                "status": parse_status(p["DFS_STATUS"])
            }
        },

        "clinical": {
            "demographics": {
                "age_at_diagnosis": p["AGE_AT_DIAGNOSIS"],
                "sex": p["SEX"],
                "race": p["RACE"]
            },
            "tumor": {
                "ulceration": p["PRIMARY_MELANOMA_TUMOR_ULCERATION"],
                "lymph_node_examined": p["LYMPH_NODE_EXAMINED_COUNT"]
            }
        },

        "recurrence": {
            "metastasis": p["METASTASIS"],
            "details": {
                "time_to_recurrence_months": p["TIME_TO_RECURRENCE_MONTHS"],
                "site_first_recurrence": p["SITE_FIRST_RECURRENCE"]
            }
        },

        "treatment": {
            "received": p["TREATMENT"],
            "details": []
        }
    }


# ============================================================
# 🔵 REESTRUCTURACIÓN DE MUESTRAS
# ============================================================

def restructure_sample(s):
    return {
        "sample_id": s["SAMPLE_ID"],

        "patient": {
            "id": s["PATIENT_ID"]
        },

        "metadata": {
            "presentation": {
                "stage": s["STAGE_AT_PRESENTATION"],
                "primary_site": s["PRIMARY_SITE"]
            },
            "sample_info": {
                "type": s["SAMPLE_TYPE"],
                "metastatic_site": s["METASTATIC_SITE"]
            }
        },

        "tumor": {
            "primary_depth_mm": s["PRIMARY_DEPTH"]
        },

        "cancer": {
            "type": {
                "main": s["CANCER_TYPE"],
                "detailed": s["CANCER_TYPE_DETAILED"]
            }
        },

        "genomics": {
            "tmb": {
                "nonsynonymous": s["TMB_NONSYNONYMOUS"]
            }
        }
    }


# ============================================================
# 🔵 REESTRUCTURACIÓN DE VARIANTES
# ============================================================

def restructure_variant(v):
    return {
        "variant_id": f"{v['Hugo_Symbol']}_{v['Start_Position']}_{v['Variant_Type']}",

        "gene": {
            "symbol": v["Hugo_Symbol"]
        },

        "location": {
            "chromosome": v["Chromosome"],
            "coordinates": {
                "start": v["Start_Position"],
                "end": v["End_Position"],
                "strand": v["Strand"]
            }
        },

        "classification": {
            "consequence": v["Consequence"],
            "variant_class": v["Variant_Classification"],
            "variant_type": v["Variant_Type"]
        },

        "alleles": {
            "reference": v["Reference_Allele"],
            "tumor": {
                "allele1": v["Tumor_Seq_Allele1"]
            }
        },

        "samples": {
            "tumor_sample": v["Tumor_Sample_Barcode"],
            "normal_sample": v["Matched_Norm_Sample_Barcode"]
        },

        "sequencing": {
            "depth": {
                "tumor": {
                    "ref_count": v["t_ref_count"],
                    "alt_count": v["t_alt_count"],
                    "total_depth": v["t_depth"]
                }
            }
        },

        "annotations": {
            "HGVSc": v["HGVSc"],
            "HGVSp": v["HGVSp"],
            "HGVSp_short": v["HGVSp_Short"]
        },

        "validation": {
            "mutation_status": v["Mutation_Status"],
            "verification_status": v["Verification_Status"],
            "validation_status": v["Validation_Status"]
        }
    }


# ============================================================
# 🔵 ONCOKB (CURATED CANCER GENES)
# ============================================================

def restructure_oncokb_gene(g):
    return {
        "gene": {
            "symbol": g.get("hugoSymbol"),
            "ensembl": g.get("curatedGeneEnsemblGeneId"),
            "entrez": g.get("curatedGeneEntrezGeneId")
        },

        "roles": {
            "oncogenic": g.get("oncogenicCategory"),
            "sensitivity_level": g.get("highestSensitiveLevel"),
            "resistance_level": g.get("highestResistanceLevel")
        },

        "clinical_implications": {
            "diagnostic": g.get("highestDiagnosticImplicationLevel"),
            "prognostic": g.get("highestPrognosticImplicationLevel")
        },

        "alterations": [
            {
                "name": alt.get("alteration"),
                "evidence_level": alt.get("level")
            }
            for alt in g.get("alterations", [])
        ]
    }


def download_and_convert_oncokb(output_file):
    url = "https://www.oncokb.org/api/v1/utils/allCuratedGenes"
    data = requests.get(url).json()

    structured = [restructure_oncokb_gene(g) for g in data]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=4, ensure_ascii=False)

    print("Colección OncoKB creada:", output_file)


# ============================================================
# 🔵 UNIPROT
# ============================================================

def restructure_uniprot(entry):
    accession = entry.get("primaryAccession")

    # -------- gene ----------
    gene_name = None
    try:
        gene_name = entry["genes"][0]["geneName"]["value"]
    except:
        gene_name = None

    # -------- function summary ----------
    function_summary = None
    try:
        for c in entry.get("comments", []):
            if c.get("type") == "FUNCTION":
                function_summary = c.get("texts", [{}])[0].get("value")
                break
    except:
        function_summary = None

    # -------- keywords ----------
    keywords = []
    try:
        keywords = [
            kw.get("value", kw.get("id"))
            for kw in entry.get("keywords", [])
        ]
    except:
        keywords = []

    # -------- organism ----------
    organism_name = None
    organism_taxid = None
    try:
        organism_name = entry["organism"]["scientificName"]
        organism_taxid = entry["organism"]["taxonId"]
    except:
        pass

    return {
        "protein": {
            "accession": accession,
            "name": entry.get("uniProtkbId"),
            "gene": gene_name
        },

        "organism": {
            "name": organism_name,
            "taxonomy_id": organism_taxid
        },

        "function": {
            "summary": function_summary,
            "keywords": keywords
        }
    }


def download_uniprot_entries(accessions, output_file):
    base_url = "https://rest.uniprot.org/uniprotkb/"

    structured_entries = []

    for acc in accessions:
        print(f"Descargando UniProt: {acc}")

        url = f"{base_url}{acc}.json"
        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            structured_entries.append(restructure_uniprot(data))
        else:
            print("No encontrado:", acc)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured_entries, f, indent=4, ensure_ascii=False)

    print("Colección UniProt creada:", output_file)


# ============================================================
# 🔵 LIMPIEZA DE CSV
# ============================================================

def limpiar_datos(input_file, columnas_a_mantener=None):
    df = pd.read_csv(input_file, sep="\t", comment="#")
    df.columns = df.columns.str.strip()

    if columnas_a_mantener:
        cols = [c for c in columnas_a_mantener if c in df.columns]
        df = df[cols]

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df = df.where(pd.notnull(df), None)
    return df


# ============================================================
# 🔵 CONVERTIR A JSON + REESTRUCTURAR
# ============================================================

def convert_to_json(input_file, output_file, columnas=None):
    df = limpiar_datos(input_file, columnas)
    records = df.to_dict(orient="records")

    records = [clean_record(r) for r in records]

    if columnas == PATIENT_COLUMNS:
        records = [restructure_patient(r) for r in records]

    elif columnas == SAMPLE_COLUMNS:
        records = [restructure_sample(r) for r in records]

    elif columnas == MUTATION_COLUMNS:
        records = [restructure_variant(r) for r in records]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)


# ============================================================
# 🔵 MAIN (CORREGIDO)
# ============================================================

# ============================================================
# 🔵 MAIN (CORREGIDO Y GENÉRICO)
# ============================================================

def main():
    # (EstandaresProyecto/codigo/scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    codigo_dir = os.path.dirname(script_dir)

    project_root = os.path.dirname(codigo_dir)

    # Ruta: codigo/datos/mel_tsam_liang_2017
    base_input = os.path.join(codigo_dir, "datos", "mel_tsam_liang_2017")
    
    # Ruta: EstandaresProyecto/cleaned_data
    out_dir = os.path.join(project_root, "cleaned_data")

    print(f"📍 Script ejecutándose en: {script_dir}")
    print(f"🔎 Buscando datos en:     {base_input}")
    print(f"💾 Guardando datos en:    {out_dir}")

    # Comprobación de seguridad
    if not os.path.exists(base_input):
        print(f"\n❌ ERROR CRÍTICO: No se encuentra la carpeta de datos.")
        print(f"   Se esperaba en: {base_input}")
        return

    # Ejecutar conversiones usando las rutas dinámicas
    # -------------------------------
    convert_to_json(
        os.path.join(base_input, "data_clinical_patient.txt"),
        os.path.join(out_dir, "patients.json"),
        PATIENT_COLUMNS
    )

    convert_to_json(
        os.path.join(base_input, "data_clinical_sample.txt"),
        os.path.join(out_dir, "samples.json"),
        SAMPLE_COLUMNS
    )

    convert_to_json(
        os.path.join(base_input, "data_mutations.txt"),
        os.path.join(out_dir, "variants.json"),
        MUTATION_COLUMNS
    )

    download_and_convert_oncokb(
        os.path.join(out_dir, "oncokb_genes.json")
    )

    uniprot_accessions = ["P15056", "P04637", "P01111", "Q16539", "P25963"]
    download_uniprot_entries(
        uniprot_accessions,
        os.path.join(out_dir, "uniprot.json")
    )

    print("\n✅ Conversión completada exitosamente.")

if __name__ == "__main__":
    main()
