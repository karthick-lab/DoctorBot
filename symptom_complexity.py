import json
import os
import sys

from gpt4all import GPT4All

exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
config_file = os.path.join(exe_dir, "config.json")

with open(config_file, "r") as f:
    CONFIG = json.load(f)


model_name = CONFIG["mistral_model_name"]
model_path = CONFIG["mistral_model_path"]

# Load model once at module level
model = GPT4All(model_name=model_name, model_path=model_path, allow_download=False)

def check_symptom_complexity(symptoms: str) -> str:
    print("inside complexity check")
    """
    Uses the local AI model to classify symptoms as 'mild' or 'complex'.
    Returns: 'mild' or 'complex' (lowercase string)
    """
    prompt = (
        f"Classify the following symptoms as either 'Mild' or 'Complex'. "
        f"Respond with only one word: Mild or Complex. No explanation.\n"
        f"Symptoms: {symptoms}"
    )
    response = ""
    for token in model.generate(prompt, streaming=True):
        response += token
        print("complexity is:", response.strip())
    return response.strip().lower()



def parse_complexity_output(raw_text: str) -> dict:
    result = {"classification": "", "flagged_symptoms": []}
    lines = raw_text.lower().splitlines()

    for line in lines:
        if "complex" in line:
            result["classification"] = "complex"
        elif "mild" in line:
            result["classification"] = "mild"
        if "complexity is:" in line:
            symptoms_part = line.split("complexity is:")[-1]
            symptoms = [s.strip() for s in symptoms_part.split(",") if s.strip()]
            result["flagged_symptoms"] = symptoms

    return result