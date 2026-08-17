import json
# pyrefly: ignore [missing-import]
import lancedb
import networkx as nx
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
from config.settings import JSON_FILEPATH

print("🔄 Loading shared resources (Model, DB, Graph)...")

# 1. Load AI Model and Vector DB
ENCODER = SentenceTransformer('all-MiniLM-L6-v2')
DB = lancedb.connect("database/lancedb_vault")
TABLE = DB.open_table("explicit_os_rules")

# 2. Helper to clean JSON keys/values (removes accidental trailing spaces)
def clean_json(obj):
    if isinstance(obj, dict):
        return {k.strip(): clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(elem) for elem in obj]
    elif isinstance(obj, str):
        return obj.strip()
    return obj

# 3. Load and Clean Master JSON
with open(JSON_FILEPATH, 'r') as file:
    APP_DATA = clean_json(json.load(file))

# 4. Build the NetworkX Graph
GRAPH = nx.DiGraph()
for state_block in APP_DATA:
    current_state = state_block.get("source_state")
    details = state_block.get("source_state_details", {})
    
    # Add Node
    GRAPH.add_node(current_state, 
                   purpose=details.get("PURPOSE", ""),
                   layout=details.get("LAYOUT", ""),
                   visual=details.get("VISUAL_APPEARANCE", ""))
    
    # Add Edges
    for trigger in state_block.get("triggered_actions", []):
        GRAPH.add_edge(current_state, trigger.get("next_state"), 
                       action=trigger.get("action_trigger"), 
                       reason=trigger.get("transition_reason"))

print(f"✅ Shared resources loaded! Graph has {GRAPH.number_of_nodes()} nodes.")