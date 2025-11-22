import json
import os
import sys
import time
from gpt4all import GPT4All

exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
config_file = os.path.join(exe_dir, "config.json")

with open(config_file, "r") as f:
    CONFIG = json.load(f)

model_name = CONFIG["mistral_model_name"]
model_path = CONFIG["mistral_model_path"]


# Load model once at module level
model = GPT4All(model_name=model_name, model_path=model_path, allow_download=False)
from shared_state import BotState

def renumber_remedies(remedy_text: str) -> str:
    lines = remedy_text.strip().split("\n")
    numbered = []
    count = 1
    for line in lines:
        # Remove any leading numbers like "1." or "2."
        clean = line.lstrip("1234567890. ").strip()
        if clean:
            numbered.append(f"{count}. {clean}")
            count += 1
    return "\n".join(numbered)

def generate_remedy_local(disease, symptoms, mode="basic"):
    if BotState.cancel_requested:
        return {"text": "Diagnosis cancelled", "sections": {}}

    def ask(prompt):
        response = ""
        for token in model.generate(prompt, streaming=True):
            response += token
        return response.strip()

    remedies = []
    for i in range(5):

        remedy_prompt = (
            f"Give remedy {i+1} for {disease} with symptoms: {symptoms}. "
            f"Use Tamil Nadu–specific ingredients only if relevant. "
            f"Include ingredient quantities in grams or ml and a short preparation step. "
            f"Limit to 25 words. No introductions or disclaimers."
        )
        remedy = ask(remedy_prompt)
        remedies.append(f"{i+1}. {remedy}")
        time.sleep(0.5)  # Optional pause for smoother UI


    remedy_text = renumber_remedies("\n".join(remedies))

    result_text = f"🩺 Predicted Condition: {disease}\n\n"
    result_text += f"🧾 Reported Symptoms: {symptoms}\n\n"
    result_text += f"🌿 Natural Remedies:\n{remedy_text}\n\n"

    from symptom_complexity import check_symptom_complexity, parse_complexity_output

    raw_complexity = check_symptom_complexity(symptoms)
    parsed = parse_complexity_output(raw_complexity)

    if parsed["classification"] == "complex":
        advisory = (
            "⚠️ These symptoms needs medical tests to predict the problem.\n"
            "Please consult a doctor and identify the root cause and once its done i can give u the natural remedies.\n"
            "All will be good soon."
        )
        result_text += advisory + "\n\n"
        result_text += f"🔍 Flagged Symptoms: {', '.join(parsed['flagged_symptoms'])}\n\n"

    if "pregnancy" in symptoms.lower() or "trying to conceive" in symptoms.lower():
        result_text += (
            "⚠️ Some remedies may affect pregnancy. Please consult a doctor before use.\n\n"
        )
    elif "pregnancy" not in symptoms.lower():
        result_text += (
            "✅ These remedies may support hormonal balance if you're not trying for pregnancy.\n\n"
        )

    return {
        "text": result_text.strip(),
        "sections": {
            "disease": disease,
            "symptoms": symptoms,
            "mode": mode,
            "remedies": remedy_text
        }
    }