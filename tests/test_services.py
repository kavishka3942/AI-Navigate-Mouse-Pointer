from agents.services.get_goal_state import get_goal_state
from agents.services.get_current_state import get_current_state
from agents.services.get_shortest_path import get_shortest_path
from agents.services.get_rule_payload import get_rule_payload

def main():
    print("\n" + "="*60)
    print("🚀 TESTING AUTOMATION SERVICES")
    print("="*60 + "\n")

    # 1. Test Goal State
    print("🎯 [Service 1] Get Goal State")
    goal_query = "I want to predict the price of a house"
    goal_state = get_goal_state(goal_query)
    print(f"Query: '{goal_query}'")
    print(f"Resulting Goal State: {goal_state}\n")

    # 2. Test Current State
    print("📍 [Service 2] Get Current State")
    curr_desc = "A screen with a light blue theme, a looks like a portfolio, there is monthly return, owned properties...etc"
    curr_state = get_current_state(curr_desc)
    print(f"Description: '{curr_desc}'")
    print(f"Resulting Current State: {curr_state}\n")

    # 3. Test Shortest Path
    print("🗺️ [Service 3] Get Shortest Path")
    # Let's navigate from Admin Dashboard to the Create Feature Form
    start = curr_state #"Reva_Admin_Dashboard"
    end = goal_state #"Reva_Create_Feature_Form"
    
    path_steps = get_shortest_path(start, end)
    print(f"Path from {start} ➡️ {end}:")
    if not path_steps:
        print("  No path found.")
    else:
        for i, step in enumerate(path_steps, 1):
            print(f"  Step {i}: Click [{step['action_trigger']}] to reach {step['to_state']}")
    print()

    # 4. Test Rule Payload
    print("📜 [Service 4] Get Rule Payload")
    
    # 4a. Get State Details
    state_details = get_rule_payload("Reva_Admin_Dashboard")
    print(f"State Purpose: {state_details.get('PURPOSE')}")
    
    # 4b. Get Specific Action Details
    action_details = get_rule_payload("Reva_Admin_Dashboard", "click_features_sidebar")
    print(f"Action Target: {action_details.get('TARGET')}")
    print(f"Action Visuals: {action_details.get('VISUALS')}")
    print(f"Action Interaction: {action_details.get('INTERACTION')}\n")

if __name__ == "__main__":
    main()