# AI Navigate Mouse Pointer (AI Cursor Overlay)

An intelligent, transparent **AI-powered secondary cursor and assistant** built with PyQt6.  

Instead of manually searching for buttons or icons, you can simply ask the AI to find them for you. Press a hotkey to summon a contextual chat pill at your cursor, type what you're looking for, and a local Vision LLM (like Qwen-VL via Ollama) will analyze your screen. Once the target is found, a glowing overlay cursor smoothly glides to the detected element, accompanied by status notifications.

Under the hood, the project is evolving into a robust multi-agent LangGraph system that handles intent classification, scene analysis, visual grounding, and multi-step planning to autonomously accomplish tasks.

---

## 🏗 Project Structure

```
cursor/
├── agents/                  # Multi-agent LangGraph architecture
│   ├── services/            # State management (context, shortest path, goal state)
│   ├── cordination_agent.py # Agent coordination 
│   ├── intent_classifier.py # Interprets user intent from chat pill
│   ├── planner_agent.py     # Multi-step LangGraph planner
│   ├── scene_analyzer.py    # Analyzes screen context
│   ├── vision_grounding.py  # VisionWorker QThread – executes the VLM call
│   ├── visual_locator.py    # Locates elements in the DOM/Screen
│   ├── graph.py             # LangGraph StateGraph workflow
│   ├── state.py             # AgentState TypedDict definitions
│   └── vlm.py               # Vision Language Model interfaces
│
├── config/
│   └── settings.py          # All constants: model, hotkeys, animation params
│
├── core/
│   ├── os_utils.py          # Screen capture helper (mss + PIL)
│   └── signals.py           # Shared PyQt6 signals
│
├── gui/
│   ├── overlay_cursor.py    # Transparent overlay window + paint + DPR fix
│   └── chatbot_widget.py    # Contextual chat pill, processing indicators, notifications
│
├── .env                     # Local config overrides (gitignored)
├── requirements.txt
└── main.py                  # Entry point
```

---

## 🛠 Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Ollama | Running locally |
| Model | `qwen2.5vl:3b` (or preferred VLM) |

Make sure you have Ollama installed and pull the required model:
```powershell
ollama pull qwen2.5vl:3b
```

---

## ⚙️ Setup

```powershell
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

### Configuration
Edit **`.env`** (or set OS environment variables) to change target parameters or models:

```env
OLLAMA_MODEL=qwen2.5vl:3b
TARGET_ELEMENT=mongo db compass application leaf symbol
SCREENSHOT_DIR=screenshots
```
*Note: Hotkeys and animation constants can be tweaked in [`config/settings.py`](config/settings.py).*

---

## 🚀 How to Run and Use

Start the application from your terminal:

```powershell
python main.py
```

### User Workflow
1. **Summon the Assistant**: Press `Ctrl + Shift + A` anywhere on your screen. A contextual chat pill will appear right where your mouse currently is.
2. **Command**: Type the element you want to interact with (e.g., "Find the submit button" or "Spotify icon") and press `Enter`.
3. **Processing**: A processing indicator will appear while the VLM analyzes a screenshot of your primary monitor.
4. **Action**: The glowing cursor will smoothly glide (60 FPS LERP animation) to the exact pixel coordinates of the detected element, and a notification will pop up confirming the result. After 10 seconds, it will revert to following your real mouse.

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl + Shift + A` | Open/Hide the Chat Pill UI |
| `Enter` (in chat)  | Trigger AI Vision Search |
| `Esc`              | Exit the application gracefully |
| `Ctrl + C`         | Force exit from terminal |

---

## 📐 High-DPI Scaling Note

The OS display scale (e.g. 125% → DPR = 1.25) means PyQt6 logical coords do not match physical pixels.  
This project accounts for this natively:

```python
dpr       = QApplication.primaryScreen().devicePixelRatio()
logical_x = int(physical_x / dpr)
logical_y = int(physical_y / dpr)
```

Console output will clearly log these translation steps:
```
[DPI FIX] VLM Physical (1034, 568) -> PyQt6 Logical (827, 454) [DPR: 1.25]
```

---

## 🗺 Roadmap

- [x] LangGraph multi-step planner integration
- [x] Contextual chatbot overlay with chat pill and processing indicators
- [ ] Autonomous click and scroll execution after visual grounding
- [ ] Multi-monitor support
