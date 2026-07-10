"""
config/settings.py
~~~~~~~~~~~~~~~~~~
All application-wide constants in one place.
Values can be overridden via environment variables or a .env file.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; fall back to OS env / hard-coded defaults

# ---------------------------------------------------------------------------
# AI / Ollama
# ---------------------------------------------------------------------------
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL",   "qwen2.5vl:3b")
TARGET_ELEMENT = os.getenv("TARGET_ELEMENT", "mongo db compass application leaf symbol")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")

# ---------------------------------------------------------------------------
# Hotkey bindings  (pynput GlobalHotKeys format)
# ---------------------------------------------------------------------------
HOTKEY_TRIGGER = "<ctrl>+<shift>+a"
HOTKEY_EXIT    = "<esc>"

# ---------------------------------------------------------------------------
# Animation / rendering
# ---------------------------------------------------------------------------
FPS                 = 60               # Timer tick rate
LERP_FACTOR         = 0.15             # Smooth-follow speed (% of gap per frame)
AI_LOCK_DURATION_MS = 10_000           # How long the cursor parks on the AI target
CURSOR_SCALE        = 0.7              # Visual size of the overlay cursor shape
