# pyrefly: ignore [missing-import]
from ollama import chat

response = chat(
    model='qwen2.5vl:3b',
    messages=[{'role': 'user', 'content': 'Hello!'}],
)
print(response.message.content)