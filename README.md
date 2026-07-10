# AI Cursor Overlay

A lightweight, transparent **AI-powered secondary cursor** built with PyQt6.  
Press a hotkey → the local Vision LLM (Qwen-VL via Ollama) analyses your screen → the glowing overlay cursor glides to the detected element.

---

## Project Structure

```
cursor/
├── config/
│   ├── __init__.py
│   └── settings.py          # All constants: model, hotkeys, animation params
│
├── core/
│   ├── __init__.py
│   ├── os_utils.py          # Screen capture helper (mss + PIL)
│   └── signals.py           # Reserved for future shared PyQt6 signals
│
├── gui/
│   ├── __init__.py
│   ├── overlay_cursor.py    # Transparent overlay window + paint + DPR fix
│   └── chatbot_widget.py    # Stub – future contextual chat panel
│
├── agents/
│   ├── __init__.py
│   ├── vision_grounding.py  # VisionWorker QThread – the single AI agent
│   ├── planner_agent.py     # Stub – future LangGraph planner node
│   ├── graph.py             # Stub – future LangGraph StateGraph
│   └── state.py             # Stub – future AgentState TypedDict
│
├── .env                     # Local config overrides (gitignored)
├── requirements.txt
└── main.py                  # Entry point only (~35 lines)
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Ollama | Running locally |
| Model | `qwen2.5vl:3b` pulled |

```powershell
ollama pull qwen2.5vl:3b
```

---

## Setup

```powershell
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Edit **`.env`** (or set OS environment variables) to change the target element or model:

```env
OLLAMA_MODEL=qwen2.5vl:3b
TARGET_ELEMENT=mongo db compass application leaf symbol
SCREENSHOT_DIR=screenshots
```

All hotkeys and animation constants live in [`config/settings.py`](config/settings.py).

---

## Running

```powershell
python main.py
```

### Hotkeys

| Key | Action |
|---|---|
| `Ctrl + Shift + A` | Trigger AI Vision – captures screen, queries VLM, moves cursor |
| `Esc` | Exit the application |
| `Ctrl + C` (terminal) | Clean exit |

---

## How It Works

```
Ctrl+Shift+A pressed
      │
      ▼
core/os_utils.capture_screen()     ← saves JPEG of primary monitor
      │
      ▼
agents/VisionWorker.run()          ← sends screenshot + prompt to Ollama
      │
      ▼
Ollama (qwen2.5vl:3b)              ← returns {"point_2d": [X, Y], "label": "..."}
      │
      ▼
target_found signal emitted        ← physical pixel coords
      │
      ▼
gui/AICursorOverlay.set_new_target()
  • Divides by DPR (High-DPI fix)
  • Sets logical target position
      │
      ▼
60 FPS LERP animation              ← cursor glides to target
      │
      ▼
After 10 s → reverts to following real mouse
```

---

## High-DPI Scaling Note

The OS display scale (125 % → DPR = 1.25) means PyQt6 logical coords ≠ physical pixels.  
The fix in `set_new_target()`:

```python
dpr       = QApplication.primaryScreen().devicePixelRatio()
logical_x = int(physical_x / dpr)
logical_y = int(physical_y / dpr)
```

Console output to verify:

```
[DPI FIX] VLM Physical (1034, 568) -> PyQt6 Logical (827, 454) [DPR: 1.25]
```

---

## Roadmap

- [ ] LangGraph multi-step planner (`agents/graph.py`)
- [ ] Contextual chatbot overlay (`gui/chatbot_widget.py`)
- [ ] Autonomous click execution after grounding
