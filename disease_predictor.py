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
from shared_state import BotState

def predict_disease(symptoms):
    if BotState.cancel_requested:
        return {"text": "Diagnosis cancelled", "sections": {}}

    model = GPT4All(model_name=model_name, model_path=model_path, allow_download=False)
    prompt = f"""
Symptoms: {symptoms}
Based on these symptoms, predict the most likely disease or condition. Respond with just the disease name in English.
"""
    response = model.generate(prompt)
    import os
    print("Full model path:", os.path.join(model_path, model_name))
    print("predicted is:",  response.strip())
    return response.strip()