import json
import networkx as nx
import matplotlib.pyplot as plt
from config.settings import JSON_FILEPATH

def build_automation_graph(json_filepath: str) -> nx.DiGraph:
    # 1. Initialize the Directed Graph
    G = nx.DiGraph()

    # 2. Load the master JSON data
    with open(json_filepath, 'r') as file:
        app_data = json.load(file)

    # 3. Iterate through every state block in the JSON
    for state_block in app_data:
        current_state = state_block.get("source_state")
        
        # Extract node details (ignoring AVAILABLE_ACTIONS as requested)
        details = state_block.get("source_state_details", {})
        node_attributes = {
            "purpose": details.get("PURPOSE", ""),
            "layout": details.get("LAYOUT", ""),
            "visual_appearance": details.get("VISUAL_APPEARANCE", "")
        }
        
        # Add the node to the graph with its metadata
        G.add_node(current_state, **node_attributes)

        # 4. Map the edges (Transitions)
        triggered_actions = state_block.get("triggered_actions", [])
        for trigger in triggered_actions:
            next_state = trigger.get("next_state")
            action_name = trigger.get("action_trigger")
            reason = trigger.get("transition_reason")
            
            # Add the edge connecting the current state to the next state
            G.add_edge(
                current_state, 
                next_state, 
                action=action_name, 
                reason=reason
            )

    print(f"Graph built successfully! Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}")
    return G

if __name__ == "__main__":
    # Assuming you saved your data block to 'master_kb.json'
    OS_GRAPH = build_automation_graph(JSON_FILEPATH)
    
    # Optional: Quick check to verify connections leaving a specific node
    # print(OS_GRAPH.edges(data=True))
       # ==========================================
    # PLOTTING THE GRAPH
    # ==========================================
    plt.figure(figsize=(14, 10)) # Set the figure size
    
    # Calculate node positions using the spring layout algorithm
    # 'seed' ensures the layout is reproducible, 'k' controls the distance between nodes
    pos = nx.spring_layout(OS_GRAPH, seed=42, k=0.5) 
    
    # Draw the nodes and edges
    nx.draw(
        OS_GRAPH, 
        pos, 
        with_labels=True,           
        node_size=3000,          # Size of the nodes
        node_color="lightblue",  # Color of the nodes
        font_size=9,             # Font size for node labels
        font_weight="bold",      # Font weight for node labels
        edge_color="gray"        # Color of the edges
    )
    
    # Optional: Add edge labels to show the 'action' triggers on the edges
    edge_labels = nx.get_edge_attributes(OS_GRAPH, 'action')
    nx.draw_networkx_edge_labels(
        OS_GRAPH, 
        pos, 
        edge_labels=edge_labels, 
        font_color='red',        # Make edge labels stand out
        font_size=8
    )
    
    plt.title("OS Automation State Graph", fontsize=16)
    plt.axis('off')  # Hide the axes for a cleaner look
    plt.tight_layout()
    
    # Render the plot
    plt.show()