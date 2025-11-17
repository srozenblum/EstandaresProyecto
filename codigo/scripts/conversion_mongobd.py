import os
import pandas as pd
import json

# ---------------------------
# Columnas permitidas
# ---------------------------

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

# ---------------------------
# Funciones limpias
# ---------------------------

def limpiar_datos(input_file, columnas_a_mantener=None):
    df = pd.read_csv(input_file, sep="\t", comment="#")
    df.columns = df.columns.str.strip()  # limpiar nombres
    
    # Mantener solo las columnas presentes y permitidas
    if columnas_a_mantener:
        columnas = [c for c in columnas_a_mantener if c in df.columns]
        df = df[columnas]

    # Limpiar espacios en columnas de texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Convertir NaN → None
    df = df.where(pd.notnull(df), None)
    return df


def save_cleaned_csv(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


def convert_to_json(input_file, output_file, columnas=None):
    # Limpiar y seleccionar columnas
    df = limpiar_datos(input_file, columnas)
    # Convertir DataFrame a JSON
    json_str = df.to_json(orient="records", force_ascii=False)
    records = json.loads(json_str)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False, allow_nan=False)


# ---------------------------
# Flujo principal
# ---------------------------

def main():
    base = "datos/mel_tsam_liang_2017"
    out_dir = "resultados/cleaned_data"

    # Pacientes
    patient_file = os.path.join(base, "data_clinical_patient.txt")
    convert_to_json(patient_file, os.path.join(out_dir, "patients.json"), PATIENT_COLUMNS)

    # Muestras
    sample_file = os.path.join(base, "data_clinical_sample.txt")
    convert_to_json(sample_file, os.path.join(out_dir, "samples.json"), SAMPLE_COLUMNS)

    # Mutaciones
    mutation_file = os.path.join(base, "data_mutations.txt")
    convert_to_json(mutation_file, os.path.join(out_dir, "variants.json"), MUTATION_COLUMNS)

    print("\nArchivos procesados correctamente:")
    print(os.path.abspath(out_dir))



if __name__ == "__main__":
    main()
