from agents.services.shared import APP_DATA

def get_rule_payload(state_name: str, action_name: str = None) -> dict:
    """
    Fun04: Gets the rule payload for a state, or a specific action within that state.
    If action_name is None, returns the state's overall details.
    """
    for state_block in APP_DATA:
        if state_block.get("source_state") == state_name:
            
            # If no action specified, return state details
            if action_name is None:
                return state_block.get("source_state_details", {})

            # Look for the specific action
            for action in state_block.get("actions", []):
                if action.get("action_trigger") == action_name:
                    return action.get("rule_payload", {})
                    
            return {"error": f"Action '{action_name}' not found in state '{state_name}'"}

    return {"error": f"State '{state_name}' not found"}