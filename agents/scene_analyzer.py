# agents/scene_analyzer.py
import json
import re
from agents.vlm import agent_vlm

SCENE_PROMPT = """
Look at this screenshot. Describe the main UI layout, key visible elements, and current screen purpose in exactly ONE short sentence. 
Do not give instructions. Just describe what is visually present.
Example: "Admin dashboard showing a left sidebar with Features/Users and a main content area with statistics cards."
"""

async def scene_analyzer_node(state: dict) -> dict:
    screenshot = state.get("current_state_screenshot")
    
    vlm_response = await agent_vlm(SCENE_PROMPT, screenshot)
    
    # Clean up any markdown or extra text
    description = re.sub(r'```.*?```', '', vlm_response).strip().replace('\n', ' ')
    
    return {"scene_description": description}