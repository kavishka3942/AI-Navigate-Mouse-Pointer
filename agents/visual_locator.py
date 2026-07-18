# agents/visual_locator.py
import json
import re
from agents.vlm import agent_vlm

LOCATOR_PROMPT = """
You are a precise visual grounding AI. Look at the screenshot and find the exact center pixel coordinates [X, Y] of the target element.

TARGET DETAILS:
- Target Name: {TARGET}
- Visuals: {VISUALS}
- Position: {POSITION}
- Interaction: {INTERACTION}

Return ONLY a valid JSON object with the coordinates and action type:
{{
    "point_2d": [X, Y],
    "action_type": "CLICK"
}}
If the element is absolutely not visible, return [-1, -1].
"""

async def visual_locator_node(state: dict) -> dict:
    screenshot = state.get("current_state_screenshot")
    payload = state.get("rule_payload", {})
    
    if not payload or not payload.get("TARGET"):
        return {
            "vlm_returned_coordinates": (-1, -1),
            "action_type": "WAIT"
        }

    prompt = LOCATOR_PROMPT.format(
        TARGET=payload.get("TARGET", "Unknown"),
        VISUALS=payload.get("VISUALS", "Unknown"),
        POSITION=payload.get("POSITION", "Unknown"),
        INTERACTION=payload.get("INTERACTION", "Single CLICK")
    )
    
    vlm_response = await agent_vlm(prompt, screenshot)
    
    try:
        clean_json = re.sub(r'```json|```', '', vlm_response).strip()
        data = json.loads(clean_json)
        coords = tuple(data.get("point_2d", [-1, -1]))
        action = data.get("action_type", "CLICK")
    except Exception:
        coords = (-1, -1)
        action = "WAIT"

    return {
        "vlm_returned_coordinates": coords,
        "action_type": action
    }