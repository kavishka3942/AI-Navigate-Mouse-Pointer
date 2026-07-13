# pyrefly: ignore [missing-import]
import lancedb
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer

# ==========================================
# 1. LOAD MODEL & DB ONLY ONCE (Global Scope)
# ==========================================
print("🚀 Starting up... Loading embedding model into memory...")
# This runs exactly once when the script starts. 
# It takes a few seconds, but you only pay this cost once!
GLOBAL_ENCODER = SentenceTransformer('all-MiniLM-L6-v2')

print("🔗 Connecting to LanceDB...")
DB = lancedb.connect("database/lancedb_vault")
TABLE = DB.open_table("explicit_os_rules")

print("✅ System ready! You can now search.\n")


# ==========================================
# 2. THE SEARCH FUNCTION (Lightning Fast)
# ==========================================
def search_os_rules(query_text: str, top_k: int = 3):
    # Because GLOBAL_ENCODER is already in RAM, this takes milliseconds!
    query_vector = GLOBAL_ENCODER.encode(query_text)
    
    # Execute the similarity search (using .to_list() to avoid pandas dependency)
    results = TABLE.search(query_vector).limit(top_k).to_list()
    
    # Print the formatted results
    print(f"\n--- Top Matches for: '{query_text}' ---")
    if not results:
        print("No matches found.")
        return

    for i, row in enumerate(results):
        distance = row['_distance'] 
        similarity_pct = max(0, (1 - distance) * 100) 
        
        print(f"\nMatch {i + 1} (Distance: {distance:.4f} | ~{similarity_pct:.1f}% similar):")
        print(f"  📍 State/Action: {row['state_key']}")
        print(f"  📜 Rule Payload: {row['rule_payload']}")
        
    return results


# ==========================================
# 3. THE CONTINUOUS LOOP (Keeps script alive)
# ==========================================
if __name__ == "__main__":
    print("Welcome to the OS Rules Search Engine!")
    print("Type 'quit' or 'exit' to stop the program.\n")
    
    while True:
        # Get input from the user
        user_query = input("type user query here ").strip()
        
        # Check if the user wants to exit
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        # Ignore empty inputs
        if not user_query:
            continue
            
        # Call the search function (It will be instant now!)
        search_os_rules(user_query, top_k=2)
        print("\n" + "="*50 + "\n")