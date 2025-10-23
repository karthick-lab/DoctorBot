from gpt4all import GPT4All


model_name = "mistral-7b-instruct-v0.2.Q5_K_S.gguf"
model_path = r"C:\Users\admin\Desktop\PythonProjects\Doctor Bot\models"

model = model = GPT4All(model_name=model_name, model_path=model_path, allow_download=True)
response = model.generate("Hello", max_tokens=10)

print(response)