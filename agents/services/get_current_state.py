from agents.services.shared import ENCODER, TABLE

def get_current_state(screen_description: str) -> str:
    """
    Fun02: Identifies the current state based on visual/functional description.
    Returns the exact state name (string).
    """
    query_vector = ENCODER.encode(screen_description)
    results = TABLE.search(query_vector).limit(1).to_list()
    
    if results:
        return results[0]['state_key']
    return None