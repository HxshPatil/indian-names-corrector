import gradio as gr
import pandas as pd
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from ai_correction_model import fallback_ai_correction
import os
import uuid
import chardet

# Load reference names
first_names_df = pd.read_csv("first_names.csv")
last_names_df = pd.read_csv("last_names.csv")

known_first_names = set(first_names_df["firstName"].dropna().str.strip().str.lower())
known_last_names = set(last_names_df["lastName"].dropna().str.strip().str.lower())

# Common salutation words
SALUTATIONS = {"mr", "mr.", "mrs", "mrs.", "ms", "ms.", "miss", "dr", "dr.", "prof", "prof."}

def remove_salutation(text):
    words = text.strip().split()
    if words and words[0].lower().rstrip(".") in SALUTATIONS:
        return " ".join(words[1:])
    return text

def correct_part(name_part, known_set):
    name_part = name_part.strip().lower()
    results = process.extract(name_part, known_set, scorer=Levenshtein.distance, limit=3)
    for candidate, score, _ in results:
        if score <= 2:
            return candidate
    return fallback_ai_correction(name_part)

# SINGLE NAME TEXT INPUT MODE
def correct_single_name(full_name):
    full_name = remove_salutation(full_name)
    parts = full_name.strip().split()

    if len(parts) == 0:
        return "Please enter a name"
    elif len(parts) == 1:
        first, last = parts[0], ""
    else:
        first, last = parts[0], parts[1]

    corrected_first = correct_part(first, known_first_names) if first else ""
    corrected_last = correct_part(last, known_last_names) if last else ""

    corrected_name = f"{corrected_first.capitalize()} {corrected_last.capitalize()}".strip()
    return corrected_name

# CSV UPLOAD MODE
def correct_csv(file_path):
    try:
        with open(file_path, "rb") as f:
            encoding = chardet.detect(f.read(10000))["encoding"]
        df = pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        return f"Error reading file: {e}"

    if "firstName" not in df.columns or "lastName" not in df.columns:
        return "CSV must contain `firstName` and `lastName` columns."

    output_rows = []

    for _, row in df.iterrows():
        original_first = str(row["firstName"]).strip()
        original_last = str(row["lastName"]).strip()

        # Remove salutation from first name only
        cleaned_first = remove_salutation(original_first)

        corrected_first = correct_part(cleaned_first, known_first_names) if cleaned_first else ""
        corrected_last = correct_part(original_last, known_last_names) if original_last else ""

        corrected_full = f"{corrected_first} {corrected_last}".strip()
        was_corrected = (
            corrected_first.lower() != cleaned_first.lower()
            or corrected_last.lower() != original_last.lower()
        )

        output_rows.append({
            "Original First Name": original_first,
            "Corrected First Name": corrected_first,
            "Original Last Name": original_last,
            "Corrected Last Name": corrected_last,
            "Corrected Name": corrected_full,
            "Was Corrected": "Yes" if was_corrected else "No"
        })

    output_df = pd.DataFrame(output_rows)

    os.makedirs("tmp", exist_ok=True)
    output_path = os.path.join("tmp", f"corrected_names_{uuid.uuid4().hex[:6]}.csv")
    output_df.to_csv(output_path, index=False)

    return output_path

# GRADIO UI
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Indian Name Corrector")

    with gr.Tab("Correct a Single Name"):
        name_input = gr.Textbox(label="Enter Name (First Last)", placeholder="e.g. Mr. Ametabh Bacchan")
        name_output = gr.Textbox(label="Corrected Name")
        gr.Button("Correct").click(correct_single_name, inputs=name_input, outputs=name_output)

    with gr.Tab("Correct a CSV File"):
        file_input = gr.File(label="Upload CSV with `firstName` and `lastName` columns", file_types=[".csv"])
        corrected_file_output = gr.File(label="Download Corrected CSV")
        gr.Button("Correct CSV").click(correct_csv, inputs=file_input, outputs=corrected_file_output)

demo.launch()
