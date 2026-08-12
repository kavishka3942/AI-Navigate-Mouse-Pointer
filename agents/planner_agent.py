"""
agents/planner_agent.py
~~~~~~~~~~~~~~~~~~~~~~~
Agent 2: The Planner / Initiator.
Triggered ONLY on a "NEW_GOAL". It takes the raw user query, establishes the 
primary goal, and visually analyzes the first screenshot to determine the 
VERY FIRST action to take. It does NOT plan the whole route, only the next move.
"""
import json
import re
from typing import Callable, Any
from agents.vlm import agent_llm, agent_vlm

# The specialized Vision Prompt for the First Step
PLANNER_VISION_PROMPT = """
You are the Strategic Vision Agent for a desktop AI assistant.
The user has submitted a NEW GOAL. You are looking at the current screenshot of their screen.

Your task is to establish the overarching goal and determine the VERY FIRST physical action the user needs to take to begin. Do NOT write out all the steps. Only focus on the immediate next step from this exact screen state.

### INSTRUCTIONS:
1. Identify the Primary Goal from the user query.
2. Analyze the screenshot to define the "Current State".
3. Determine the "Instruction" (what to do right now, e.g., "Click the Start Menu", "Scroll down to find the settings icon").
4. Predict the "Expected Next State" (what the screen will look like after this action).
5. Provide the exact 2D pixel coordinates [X, Y] for the target element. 
6. Define the action type: "CLICK", "SCROLL_LOOK", or "WAIT".

### STRICT OUTPUT FORMAT:
You MUST return ONLY a valid JSON object. Do not include markdown formatting like ```json.
{{
    "primary_goal": "<A clean, concise summary of the end goal>",
    "current_state_definition": "<Brief description of what is currently on the screen>",
    "instructions": "<The exact, immediate next physical step for the user>",
    "expected_next_state": "<What the screen should look like after this step>",
    "point_2d": [X, Y],
    "action_type": "<CLICK | SCROLL_LOOK | WAIT>",
    "reasoning": "<Why this is the correct first step>"
}}

### DYNAMIC RUNTIME CONTEXT (DO NOT CACHE BEYOND THIS POINT):
### USER QUERY:
"{user_query}"

"""

async def planner_node(state: dict) -> dict:
    """
    LangGraph Node for Agent 2.
    :param state: The current LangGraph AssistantState dictionary.
    """
    user_query = state.get("user_message", "").strip()
    screenshot_path = state.get("current_state_screenshot")
    
    # Format the specialized prompt
    prompt = PLANNER_VISION_PROMPT.format(
        user_query=user_query,
    )
    
    # Call the Vision LLM (passing both the image and the prompt)
    vlm_response = await agent_vlm(prompt,screenshot_path)
    
    # Safely parse the JSON response
    try:
        clean_json_str = re.sub(r'```json|```', '', vlm_response).strip()
        parsed_data = json.loads(clean_json_str)
        
        primary_goal = parsed_data.get("primary_goal", user_query)
        point_2d = parsed_data.get("point_2d", [-1, -1])
        
        # Build the VLMStateData object precisely as defined in state.py
        vlm_return = {
            "current_state_definition": parsed_data.get("current_state_definition", "Unknown"),
            "instructions": parsed_data.get("instructions", "No instruction generated"),
            "expected_next_state": parsed_data.get("expected_next_state", "Unknown")
        }
        
    except json.JSONDecodeError:
        # Fallback safeguard
        primary_goal = user_query
        point_2d = [-1, -1]
        vlm_return = {
            "current_state_definition": "Error parsing vision data",
            "instructions": "⚠️ I couldn't process the screen. Please try again.",
            "expected_next_state": "Error"
        }
    
    # Create the state update dictionary
    state_update = {
        "primary_goal": primary_goal,
        "vlm_return": vlm_return,
        "vlm_returned_coordinates": point_2d,
        # We append this very first step to the history list
        "history_of_state_transitions": [vlm_return]
    }
    
    # Send the instruction back to the UI bubble (if action_type/guidance_text are tracked at root)
    if "action_type" in parsed_data:
        state_update["action_type"] = parsed_data["action_type"]
    
    return state_update