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

model = model = GPT4All(model_name=model_name, model_path=model_path, allow_download=True)
response = model.generate("Hello", max_tokens=10)

print(response)