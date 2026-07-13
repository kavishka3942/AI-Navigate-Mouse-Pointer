"""
agents/vision_grounding.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
VisionWorker – the single AI agent in the current implementation.

Formerly ``OllamaWorker`` in main.py.  Responsibilities (unchanged):
  1. Capture the screen using core.os_utils.capture_screen().
  2. Build the VLM prompt and call the local Ollama model.
  3. Parse the JSON response and emit target_found(physical_x, physical_y).

No logic has been added or modified; only import paths have changed.
"""
import re
import json

from PyQt6.QtCore import QThread, pyqtSignal
from ollama import chat

from config.settings import OLLAMA_MODEL, TARGET_ELEMENT, SCREENSHOT_DIR
from core.os_utils import capture_screen


class VisionWorker(QThread):
    """Background QThread that captures the screen and queries the local VLM.

    Emits ``target_found(physical_x, physical_y)`` when the model returns
    a valid coordinate pair.
    """

    # Signal carries raw physical pixel coordinates returned by the VLM
    target_found = pyqtSignal(int, int)
    result_ready = pyqtSignal(int, int, str)

    def __init__(self, screen_width: int, screen_height: int, target_element: str | None = None):
        super().__init__()
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.target_element = (target_element or TARGET_ELEMENT).strip() or TARGET_ELEMENT

    # ------------------------------------------------------------------
    def run(self):
        print(f"\n[+] AI Vision Triggered! Looking for: '{self.target_element}'...")

        try:
            # 1. Capture the screen via core utility
            filename = capture_screen(SCREENSHOT_DIR)

            # 2. Build the VLM prompt
            prompt = (
                "You are an expert UI grounding engine. Your sole task is to locate "
                "user interface elements within screenshots and return their precise "
                "center coordinates.\n\n"
                "### Objective\n"
                f"Locate the center point of the following target element in the "
                f"provided image: \"{self.target_element}\"\n\n"
                "### Coordinate System Rules\n"
                "- Find the exact center point coordinates of the element \n\n"
                "### Output Constraint\n"
                "- You must ONLY output a single valid raw JSON object matching the "
                "schema below.\n"
                "- Absolutely DO NOT include any conversational filler, introductory "
                "phrases, explanations, or markdown syntax wrappers like \"```json\". "
                "Your response must start exactly with '{' and end with '}'.\n\n"
                "### Expected JSON Schema\n"
                "{\n"
                "  \"point_2d\": [X, Y],\n"
                "  \"label\": \"A brief one-sentence explanation of why these "
                "coordinates were selected.\"\n"
                "}\n\n"
                "Output:"
            )

            # 3. Query local Vision Model via Ollama
            print(f"[>] Analyzing screen with '{OLLAMA_MODEL}'...")
            response = chat(
                model=OLLAMA_MODEL,
                messages=[{
                    'role':    'user',
                    'content': prompt,
                    'images':  [filename],
                }],
            )
            content = response.message.content

            # Clean up markdown code blocks if the model added them
            clean_content = content.strip()
            if clean_content.startswith("```"):
                lines = clean_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_content = "\n".join(lines).strip()

            print("\n=== OLLAMA RESPONSE ===")
            print(clean_content)
            print("=======================\n")

            # 4. Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', clean_content)
            json_text  = json_match.group(0).strip() if json_match else clean_content.strip()
            try:
                data = json.loads(json_text)
            except Exception as e:
                print(f"[-] Failed to parse JSON from LLM response: {e}")
                print("[DEBUG] Raw cleaned content:")
                print(clean_content)
                data = None

            if data and isinstance(data, dict):
                x, y           = data.get('point_2d', (0, 0))
                interpretation = data.get('label', '')
                print(f"📍 Raw Model Coordinates: X={x}, Y={y}")
                print(f"💬 Interpretation: {interpretation}")
                target_x = x
                target_y = y
                print(f"[DEBUG] Model gave ({x}, {y}) -> target pixel ({target_x}, {target_y})")
                self.target_found.emit(target_x, target_y)
                self.result_ready.emit(target_x, target_y, interpretation)
            else:
                print("[-] No valid coordinate data extracted from LLM response.")

        except Exception as e:
            print(f"[-] Error during processing: {e}")
