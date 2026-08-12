"""
agents/coordination_agent.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Agent 3: The Coordination Agent.
Triggered when the intent is an "ITERATION". It evaluates the current screenshot
against the backdrop of the entire execution history to determine the next physical step.
"""
import json
import re
from typing import Callable, Any
from agents.services.context import format_execution_context
from agents.vlm import agent_llm, agent_vlm

# The advanced evolutionary vision prompt for sequential coordination
COORDINATION_VISION_PROMPT = """
You are the Lead Coordination Agent for a desktop AI assistant.
An ongoing plan is currently active. Your job is to look at the current screenshot and the history of past state transitions to safely determine the VERY NEXT step.



### STRICT OPERATIONAL RULES:
1. Examine the history context carefully. Do NOT output the exact same coordinates and instructions as a previous step if the screen state indicates that action failed or got stuck.
2. Determine what action type is required right now:
   - "CLICK": A precise location to press.
   - "SCROLL_LOOK": An area or scroll bar container where the user must scroll down/up to find an element.
   - "WAIT": A state where the desktop is loading or updating, and the user must pause.
3. If the next expected element is missing or an error pop-up has appeared, look for a recovery target (like an Undo button, a Close X icon, or a parent menu tab) to correct the UI layout.

### STRICT OUTPUT FORMAT:
You MUST return ONLY a valid JSON object. Do not include markdown formatting like ```json.
{{
    "current_state_definition": "<Brief description of what is currently visible on the screen>",
    "instructions": "<The exact, immediate instruction text for the user bubble>",
    "expected_next_state": "<What the screen should look like after this step is performed>",
    "point_2d": [X, Y],
    "action_type": "<CLICK | SCROLL_LOOK | WAIT>",
    "reasoning": "<Explanation of why this step is next and how it avoids previous loops>"
}}
### DYNAMIC RUNTIME CONTEXT (DO NOT CACHE BEYOND THIS POINT):
### OVERARCHING USER GOAL:
"{primary_goal}"

### LATEST USER SIGNAL:
"{user_query}"

### HISTORY OF PAST STATE TRANSITIONS ( Previous state transitions):
{context}
"""

async def coordination_node(state: dict) -> dict:
    """
    LangGraph Node for Agent 3.
    :param state: The current LangGraph AssistantState dictionary.
    :param vlm_callable: Your async function to call the Vision LLM (accepts image_path, prompt).
    """
    primary_goal = state.get("primary_goal", "Unknown Task")
    user_query = state.get("user_message", "").strip()
    screenshot_path = state.get("current_state_screenshot")
    raw_history = state.get("history_of_state_transitions", [])
    
    # 1. Compile the meaningful string history using our context creator service
    formatted_context = format_execution_context(raw_history)
    
    # 2. Inject parameters into the operational prompt
    prompt = COORDINATION_VISION_PROMPT.format(
        primary_goal=primary_goal,
        user_query=user_query,
        context=formatted_context
    )
    
    # 3. Fire the async Vision model call
    vlm_response = await agent_vlm(prompt,screenshot_path)
    
    # 4. Parse the output securely
    try:
        clean_json_str = re.sub(r'```json|```', '', vlm_response).strip()
        parsed_data = json.loads(clean_json_str)
        
        point_2d = parsed_data.get("point_2d", [-1, -1])
        
        # Build the exact VLMStateData matching our state dict rules
        vlm_return = {
            "current_state_definition": parsed_data.get("current_state_definition", "Unknown"),
            "instructions": parsed_data.get("instructions", "Proceeding with next sequence"),
            "expected_next_state": parsed_data.get("expected_next_state", "Unknown")
        }
        
    except json.JSONDecodeError:
        # Emergency processing fallback
        point_2d = [-1, -1]
        vlm_return = {
            "current_state_definition": "Error decoding transition metrics",
            "instructions": "⚠️ Checking screen state again. Please hit your advance key.",
            "expected_next_state": "Retry"
        }
        
    # 5. Prepare the state delta update mutations
    state_update = {
        "vlm_return": vlm_return,
        "vlm_returned_coordinates": point_2d
    }
    
    # Extract action type if verified by the VLM
    if "action_type" in parsed_data:
        state_update["action_type"] = parsed_data["action_type"]
        
    # Safely append the new step transition data to our persistent history block
    # We create a new copy of the history list to ensure LangGraph catches the state modification
    updated_history = list(raw_history)
    updated_history.append(vlm_return)
    state_update["history_of_state_transitions"] = [vlm_return]
    
    return state_update