import mss
import json
import pyautogui
from PIL import Image
import requests

# 1. Capture the screen
with mss.mss() as sct:
    # Grab the primary monitor screen
    monitor = sct.monitors[1]
    sct_img = sct.grab(monitor)
    # Convert to PIL Image
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    img.save("/screenshots/screenshot.jpg") # Save temporarily for the model

# 2. Ask the local Vision Model
# Assumes Ollama is running 'qwen2-vl' locally
url = "http://localhost:11434/api/chat"
payload = {
    "model": "qwen2-vl:3b",
    "messages": [
        {
            "role": "user",
            "content": "Where is the Microsoft Word 'File' menu? Return only the X and Y percentages like [X%, Y%].",
            "images": ["screenshot.jpg"]
        }
    ],
    "stream": False
}

response = requests.post(url, json=payload)
result = response.json()['message']['content']

# 3. Parse result and move the cursor
# Let's say the model returned "[5%, 3%]"
# Convert those percentages to match actual monitor width/height
screen_width, screen_height = pyautogui.size()
target_x = int(screen_width * 0.05)
target_y = int(screen_height * 0.03)

# Move the actual mouse (or trigger your visual overlay cursor)
pyautogui.moveTo(target_x, target_y, duration=1.0)