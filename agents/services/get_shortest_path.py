import networkx as nx
from agents.services.shared import GRAPH

def get_shortest_path(current_state: str, goal_state: str) -> list:
    """
    Fun03: Finds the shortest path from current to goal.
    Returns a list of dictionaries containing the exact steps/actions needed.
    """
    if not GRAPH.has_node(current_state) or not GRAPH.has_node(goal_state):
        raise ValueError("One or both states do not exist in the graph.")

    try:
        # This returns a simple list of nodes: ['A', 'B', 'C']
        path_nodes = nx.shortest_path(GRAPH, source=current_state, target=goal_state)
    except nx.NetworkXNoPath:
        return [] # No path exists

    # Translate the list of nodes into actionable steps (Edges)
    steps = []
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        edge_data = GRAPH.get_edge_data(u, v)

        steps.append({
            "from_state": u,
            "to_state": v,
            "action_trigger": edge_data.get('action', 'Unknown'),
            "reason": edge_data.get('reason', 'Unknown')
        })

    return steps