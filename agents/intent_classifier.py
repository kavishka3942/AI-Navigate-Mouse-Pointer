# agents/intent_classifier.py
import json
import re
from agents.vlm import agent_llm

INTENT_PROMPT = """
You are an intent classifier for a UI automation agent.
Classify the user's message and extract the primary goal if it's a new task.

User intent can be like this: 
ITERATION : ok, done, whats next, next,completed, continue....etc
NEW_GOAL  : how i insert this, where i can find this, tell me how to ....etc
GENERAL_GREETING : hi, thank you, ...etc

User Message: "{user_message}"

Return ONLY valid JSON:
{{
    "intent": "NEW_GOAL" | "ITERATION" | "GENERAL_GREETING",
    "primary_goal": "<Extracted goal if NEW_GOAL, otherwise empty string>"
}}
"""

async def classify_intent_node(state: dict) -> dict:
    user_query = state.get("user_message", "").strip()
    
    # If it's an iteration (e.g., "next", "done"), we keep the existing primary_goal
    existing_goal = state.get("primary_goal", "")
    
    prompt = INTENT_PROMPT.format(user_message=user_query)
    llm_response = await agent_llm(prompt, None) # No screenshot needed for intent
    
    try:
        clean_json = re.sub(r'```json|```', '', llm_response).strip()
        data = json.loads(clean_json)
        intent = data.get("intent", "GENERAL_GREETING")
        goal = data.get("primary_goal", "")
        
        if intent != "NEW_GOAL" or not goal:
            goal = existing_goal # Fallback to existing goal for iterations
            
    except Exception:
        intent = "ITERATION" if existing_goal else "NEW_GOAL"
        goal = existing_goal

    return {"intent": intent, "primary_goal": goal}