from gpt4all import GPT4All
import os

model = GPT4All(
    model_name="ggml-gpt4all-j-v1.2-jazzy.bin",
    model_path=os.path.expanduser("~/.cache/gpt4all")
)

model.open()
print("✅ Model loaded!")
print(model.generate("What is artificial intelligence?"))
