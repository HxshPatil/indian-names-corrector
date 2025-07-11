import gradio as gr
import pandas as pd
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from ai_correction_model import fallback_ai_correction

# Load your reference CSVs
first_names_df = pd.read_csv("first_names.csv")
print("printing: first_names_df", first_names_df.to_string());
last_names_df = pd.read_csv("last_names.csv")

# Create clean sets of names
known_first_names = set(first_names_df['firstName'].dropna().str.strip().str.lower())
known_last_names = set(last_names_df['lastName'].dropna().str.strip().str.lower())

def correct_part(name_part, known_set):
    name_part = name_part.strip().lower()
    print(f"\n🔍 Trying to correct: {name_part}")

    results = process.extract(name_part, known_set, scorer=Levenshtein.distance, limit=5)

    for candidate, score, _ in results:
        print(f"→ Candidate: {candidate}, Distance: {score}")

    for candidate, score, _ in results:
        if score <= 2:
            print(f"✅ Using: {candidate} with distance {score}")
            return candidate

    print("❌ No close match found. Using fallback.")
    return fallback_ai_correction(name_part)

def correct_single_name(full_name):
    try:
        first, last = full_name.strip().split()
    except ValueError:
        return "Please enter a name in 'First Last' format."

    corrected_first = correct_part(first, known_first_names)
    corrected_last = correct_part(last, known_last_names)

    return f"{corrected_first.capitalize()} {corrected_last.capitalize()}"


def correct_csv(file):
    df = pd.read_csv(file.name)

    if 'name' not in df.columns:
        return "CSV must have a column named 'name'"

    def fix(row):
        try:
            first, last = row['name'].strip().split()
            corrected_first = correct_part(first, known_first_names)
            corrected_last = correct_part(last, known_last_names)
            return f"{corrected_first} {corrected_last}"
        except:
            return row['name']

    df['corrected_name'] = df.apply(fix, axis=1)
    output_path = "/tmp/corrected_names.csv"
    df.to_csv(output_path, index=False)
    return output_path

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Indian Name Corrector (Fuzzy + AI)")
    
    with gr.Tab("Single Name"):
        name_input = gr.Textbox(label="Enter Name (First Last)", placeholder="e.g. Ametabh Bacchan")
        name_output = gr.Textbox(label="Corrected Name")
        gr.Button("Correct").click(correct_single_name, inputs=name_input, outputs=name_output)
    
    with gr.Tab("CSV Upload"):
        file_input = gr.File(label="Upload CSV with `name` column")
        file_output = gr.File(label="Download Corrected CSV")
        gr.Button("Correct CSV").click(correct_csv, inputs=file_input, outputs=file_output)

demo.launch()
