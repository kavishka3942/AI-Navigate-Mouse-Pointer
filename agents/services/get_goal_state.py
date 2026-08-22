from agents.services.shared import ENCODER, TABLE

def get_goal_state(user_query: str) -> str:
    """
    Fun01: Finds the target/goal state based on a semantic user query.
    Returns the exact state name (string).
    """
    query_vector = ENCODER.encode(user_query)
    results = TABLE.search(query_vector).limit(1).to_list()
    
    if results:
        return results[0]['state_key']
    return None