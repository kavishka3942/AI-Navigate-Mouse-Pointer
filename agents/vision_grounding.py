"""
agents/vision_grounding.py
VisionWorker – the QThread that bridges the PyQt6 GUI with the new LangGraph 
Graph+VDB multi-agent workflow.

Changes in this version:
- Enhanced state initialization for the new modular agents.
- Rich terminal logging to show exactly what the Vector DB and NetworkX Graph 
  identified (Current State, Goal State, Next Action).
- Maintains the exact same PyQt signals so main.py remains untouched.
"""
import asyncio
import traceback
from PyQt6.QtCore import QThread, pyqtSignal

from config.settings import SCREENSHOT_DIR
from core.os_utils import capture_screen
from agents.graph import workflow 

class VisionWorker(QThread):
    """Background QThread that captures the screen and triggers the multi-agent graph."""
    
    # Signals (UNCHANGED to protect main.py)
    target_found = pyqtSignal(int, int)
    result_ready = pyqtSignal(int, int, str)

    def __init__(self, screen_width: int, screen_height: int, user_message: str = ""):
        super().__init__()
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.user_message = user_message.strip()

    def run(self):
        print(f"\n{'='*20} ORCHESTRATION TRIGGERED {'='*20}")
        print(f"[+] User Message: '{self.user_message}'")
        
        try:
            # 1. Capture the screen via core utility
            screenshot_path = capture_screen(SCREENSHOT_DIR)
            print(f"[+] Screen captured: {screenshot_path}")

            # 2. Define the initial state payload for LangGraph
            # We pass the raw inputs. The agents will fill in the rest.
            input_state = {
                "user_message": self.user_message,
                "current_state_screenshot": screenshot_path,
                # Initialize empty/default values for the new state keys
                "intent": "",
                "primary_goal": "",
                "scene_description": "",
                "current_state_name": "",
                "goal_state_name": "",
                "next_action_trigger": "",
                "rule_payload": {},
                "vlm_returned_coordinates": (-1, -1),
                "action_type": "WAIT",
                "vlm_return": {},
                "history_of_state_transitions": []
            }

            # 3. Configure the checkpointer thread ID
            # This keeps the "primary_goal" alive when the user says "next"
            config = {"configurable": {"thread_id": "desktop_session_1"}}

            # 4. Execute the Async LangGraph Workflow
            print("[>] Running LangGraph Graph+VDB state machine...")
            final_state = asyncio.run(workflow.ainvoke(input_state, config=config))

            # ==========================================
            # 5. RICH DEBUG LOGGING (New Architecture)
            # ==========================================
            print("\n=== LANGGRAPH FINAL STATE ===")
            print(f"🗣️  Intent Detected     : {final_state.get('intent')}")
            print(f"🎯 Primary Goal        : {final_state.get('primary_goal')}")
            print(f"👁️  Scene Description   : {final_state.get('scene_description', 'N/A')[:80]}...")
            print(f"📍 Current State (VDB) : {final_state.get('current_state_name', 'Unknown')}")
            print(f"🏁 Goal State (VDB)    : {final_state.get('goal_state_name', 'Unknown')}")
            print(f"⚡ Next Action Trigger : {final_state.get('next_action_trigger', 'None')}")
            print(f"🗺️  Rule Payload       : {final_state.get('rule_payload', {})}")
            print("=============================\n")

            # ==========================================
            # 6. EXTRACT FINAL GUI OUTPUTS
            # ==========================================
            # Coordinates for the cursor
            x, y = final_state.get("vlm_returned_coordinates", (-1, -1))
            
            # The text for the PyQt Notification Bubble
            vlm_return = final_state.get("vlm_return", {})
            guidance_text = vlm_return.get("instructions", "Processing complete.")
            
            # Action type (CLICK, WAIT, etc.)
            action_type = final_state.get("action_type", "CLICK")

            print(f"📍 Final Coordinates : X={x}, Y={y}")
            print(f"💬 GUI Bubble Text   : {guidance_text}")
            print(f"⚡ Final Action Type : {action_type}")
            print(f"{'='*58}\n")

            # 7. Emit results back to the PyQt GUI thread
            if x != -1 and y != -1:
                # Valid target found
                self.target_found.emit(int(x), int(y))
                self.result_ready.emit(int(x), int(y), guidance_text)
            else:
                # Target not found or human intervention required
                print("[-] Agent paused: No click target found or manual intervention needed.")
                self.result_ready.emit(-1, -1, guidance_text)

        except Exception as e:
            print(f"[-] CRITICAL ERROR during LangGraph execution: {e}")
            traceback.print_exc()
            self.result_ready.emit(-1, -1, f"⚠️ Workflow Error: {str(e)}")