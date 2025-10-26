import time
from gpt4all import GPT4All

model_name = "mistral-7b-instruct-v0.2.Q5_K_S.gguf"
model_path = r"C:\Users\admin\Desktop\Models"

# Load model once at module level
model = GPT4All(model_name=model_name, model_path=model_path, allow_download=False)
from shared_state import BotState

def generate_medical_advice(user_question: str, mode="general"):
    if BotState.cancel_requested:
        return {"text": "Advice cancelled", "sections": {}}

    def ask(prompt):
        response = ""
        for token in model.generate(prompt, streaming=True):
            response += token
        return response.strip()

    advice_prompt = (
        f"Answer this medical doubt clearly and concisely: {user_question}\n"
        f"Use Tamil Nadu–specific context if relevant. Avoid disclaimers unless necessary.\n"
        f"Limit to 50 words. Use simple language. No introductions."
    )

    advice = ask(advice_prompt)

    result_text = f"❓ Question: {user_question}\n\n"
    result_text += f"💡 Advice:\n{advice.strip()}\n\n"

    # Optional safety checks
    lower_q = user_question.lower()
    if any(term in lower_q for term in ["pregnancy", "conceive", "breastfeeding"]):
        result_text += (
            "⚠️ This topic involves pregnancy or fertility. Please consult a doctor before following any advice.\n\n"
        )
    elif any(term in lower_q for term in ["diabetes", "blood pressure", "heart", "thyroid", "medication"]):
        result_text += (
            "⚠️ This may involve chronic conditions or medications. Always confirm with a healthcare provider.\n\n"
        )
    else:
        result_text += (
            "✅ This advice is general and may support wellness. For serious concerns, consult a doctor.\n\n"
        )

    return {
        "text": result_text.strip(),
        "sections": {
            "question": user_question,
            "mode": mode,
            "advice": advice.strip()
        }
    }