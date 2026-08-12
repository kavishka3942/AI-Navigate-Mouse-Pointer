"""
services/context_creator.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Transforms the graph's raw transition history into a readable timeline context 
for the Gatekeeper/Intent LLM.
"""
from typing import List, Dict, Any

def format_execution_context(history_of_state_transitions: List[Dict[str, Any]]) -> str:
    """
    Parses the list of previous VLM states and returns a meaningful timeline.
    """
    if not history_of_state_transitions:
        return "No previous steps taken. The system is currently idle and waiting for a goal."

    context_lines = ["### PREVIOUS EXECUTION TIMELINE ###"]
    
    for i, step in enumerate(history_of_state_transitions):
        # Fallbacks included just in case the VLM missed a key in the past
        current_state = step.get("current_state_definition", "Unknown state")
        instruction = step.get("instructions", "No instruction given")
        expected_next = step.get("expected_next_state", "Unknown expected state")

        step_str = (
            f"[Step {i + 1}]\n"
            f" - Actual Screen State: {current_state}\n"
            f" - AI Instructed User To: {instruction}\n"
            f" - Expected Outcome: {expected_next}\n"
        )
        context_lines.append(step_str)

    # Return the chained history as a single block of text
    return "\n".join(context_lines)