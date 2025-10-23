from gpt4all import GPT4All

model_name = "mistral-7b-instruct-v0.2.Q5_K_S.gguf"
model_path = r"C:\Users\admin\Desktop\Models"
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