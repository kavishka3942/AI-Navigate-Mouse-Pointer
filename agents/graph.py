# agents/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.state import AssistantState

from agents.intent_classifier import classify_intent_node
from agents.scene_analyzer import scene_analyzer_node
from agents.graph_planner import graph_planner_node
from agents.visual_locator import visual_locator_node

# 1. Initialize the Graph
builder = StateGraph(AssistantState)

# 2. Add Nodes
builder.add_node("gatekeeper", classify_intent_node)
builder.add_node("scene_analyzer", scene_analyzer_node)
builder.add_node("graph_planner", graph_planner_node)
builder.add_node("visual_locator", visual_locator_node)

# 3. Set Entry Point
builder.set_entry_point("gatekeeper")

# 4. Define Routing Logic
def route_after_gatekeeper(state):
    intent = state.get("intent")
    if intent == "GENERAL_GREETING":
        return "end"
    # Both NEW_GOAL and ITERATION go through the same visual pipeline
    return "continue"

builder.add_conditional_edges(
    "gatekeeper",
    route_after_gatekeeper,
    {
        "continue": "scene_analyzer",
        "end": END
    }
)

# 5. Define the Linear Execution Pipeline
builder.add_edge("scene_analyzer", "graph_planner")
builder.add_edge("graph_planner", "visual_locator")
builder.add_edge("visual_locator", END)

# 6. Compile with Memory (Keeps primary_goal alive across "next" iterations)
workflow = builder.compile(checkpointer=MemorySaver())