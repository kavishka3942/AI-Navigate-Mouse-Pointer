import json
# pyrefly: ignore [missing-import]
import lancedb
import pyarrow as pa
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
from config.settings import JSON_FILEPATH

def seed_vector_database(json_filepath: str):
    # 1. Initialize the local embedding model and LanceDB connection
    print("Loading embedding model...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    db = lancedb.connect("database/lancedb_vault")
    
    with open(json_filepath, 'r') as file:
        app_data = json.load(file)

    formatted_data = []

    # 2. Iterate through the JSON to extract UI States (No actions!)
    print("Parsing JSON for UI states...")
    for state_block in app_data:
        current_state = state_block.get("source_state")
        details = state_block.get("source_state_details", {})
        
        purpose = details.get("PURPOSE", "N/A")
        layout = details.get("LAYOUT", "N/A")
        visual = details.get("VISUAL_APPEARANCE", "N/A")
        
        # Construct the semantic search key. 
        # We combine the state name + all visual/purpose details into one rich string.
        embedding_text = (
            f"State: {current_state}. "
            f"PURPOSE: {purpose}. "
            f"LAYOUT: {layout}. "
            f"VISUAL_APPEARANCE: {visual}."
        )
        
        # The simple identifier for the state
        state_key = current_state
        
        # Format the dictionary into a highly readable string for the VLM 
        # (This is what the AI will read once a match is found)
        payload_string = (
            f"STATE NAME: {current_state}. "
            f"PURPOSE: {purpose}. "
            f"LAYOUT: {layout}. "
            f"VISUAL_APPEARANCE: {visual}."
        )
        
        # Generate the vector embedding and append to our data array
        formatted_data.append({
            "vector": encoder.encode(embedding_text),
            "state_key": state_key,
            "rule_payload": payload_string
        })

    # 3. Define the PyArrow Schema
    schema = pa.schema([
        pa.field("vector", pa.list_(pa.float32(), 384)), # 384 dimensions for MiniLM
        pa.field("state_key", pa.string()),
        pa.field("rule_payload", pa.string())
    ])

    # 4. Create and populate the LanceDB table
    print(f"Writing {len(formatted_data)} UI states to LanceDB...")
    # mode="overwrite" ensures the old action-based data is wiped and replaced
    db.create_table("explicit_os_rules", data=formatted_data, schema=schema, mode="overwrite")
    print("🎯 Vector Database successfully initialized from master JSON!")

if __name__ == "__main__":
    seed_vector_database(JSON_FILEPATH)