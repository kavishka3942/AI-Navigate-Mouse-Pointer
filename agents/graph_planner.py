# agents/graph_planner.py
# Note: Ensure your services folder is in the PYTHONPATH or relative to root
from agents.services.get_goal_state import get_goal_state
from agents.services.get_current_state import get_current_state
from agents.services.get_shortest_path import get_shortest_path
from agents.services.get_rule_payload import get_rule_payload

async def graph_planner_node(state: dict) -> dict:
    intent = state.get("intent")
    user_msg = state.get("user_message", "")
    scene_desc = state.get("scene_description", "")
    existing_goal = state.get("primary_goal", "")
    
    # 1. Determine Goal State
    if intent == "NEW_GOAL":
        goal_state = get_goal_state(user_msg)
    else:
        goal_state = get_goal_state(existing_goal) # Re-use goal for iterations
        
    # 2. Determine Current State (using VLM's scene description)
    current_state = get_current_state(scene_desc)
    
    # 3. Get Shortest Path & Next Action
    next_action = None
    rule_payload = {}
    gui_message = "Navigating..."
    
    if current_state and goal_state:
        path = get_shortest_path(current_state, goal_state)
        if path:
            first_step = path[0]
            next_action = first_step["action_trigger"]
            
            # 4. Get the exact UI rules for this action
            rule_payload = get_rule_payload(current_state, next_action)
            target = rule_payload.get("TARGET", "the element")
            gui_message = f"Click {target}" # This goes to the GUI bubble
            
    elif not current_state:
        gui_message = "⚠️ Could not identify current screen state."
    elif not goal_state:
        gui_message = "⚠️ Could not identify goal state."

    # Prepare the vlm_return dict to satisfy vision_grounding.py's GUI bubble logic
    vlm_return = {
        "current_state_definition": scene_desc,
        "instructions": gui_message, 
        "expected_next_state": goal_state or "Unknown"
    }

    return {
        "goal_state_name": goal_state,
        "current_state_name": current_state,
        "next_action_trigger": next_action,
        "rule_payload": rule_payload,
        "vlm_return": vlm_return
    }