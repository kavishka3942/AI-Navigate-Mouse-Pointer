# agents/state.py
from typing import TypedDict, Tuple, Optional, Dict

class AssistantState(TypedDict):
    # Inputs
    user_message: str
    current_state_screenshot: str
    
    # Intent & Goal
    intent: str  # "NEW_GOAL", "ITERATION", "GENERAL_GREETING"
    primary_goal: str 
    
    # Graph & VDB Derived Context
    scene_description: str       # Short VLM description of current screen
    current_state_name: str      # Matched from VDB
    goal_state_name: str         # Matched from VDB
    next_action_trigger: str     # The exact action to perform next
    rule_payload: Dict[str, str] # The UI rules (TARGET, VISUALS, POSITION, etc.)
    
    # Final VLM Outputs (Required by vision_grounding.py)
    vlm_returned_coordinates: Tuple[int, int]
    action_type: str             # "CLICK", "SCROLL_LOOK", "WAIT"
    
    # Kept specifically so vision_grounding.py can read the GUI bubble text
    vlm_return: Dict[str, str]   # Must contain "instructions" key