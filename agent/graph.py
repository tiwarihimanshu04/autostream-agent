from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import classify_intent, retrieve_context, extract_lead_field, capture_lead, generate_response

def route_after_intent(state):
    if state.get("collecting_lead") and state.get("awaiting_field"): return "extract_lead_field"
    if state.get("intent") in ("pricing_inquiry","product_inquiry","greeting","high_intent_lead"): return "retrieve_context"
    return "generate_response"

def route_after_extraction(state):
    d = state.get("lead_data",{})
    if d.get("name") and d.get("email") and d.get("platform") and not state.get("lead_captured"): return "capture_lead"
    return "generate_response"

def compile_agent():
    g = StateGraph(AgentState)
    g.add_node("classify_intent", classify_intent)
    g.add_node("retrieve_context", retrieve_context)
    g.add_node("extract_lead_field", extract_lead_field)
    g.add_node("capture_lead", capture_lead)
    g.add_node("generate_response", generate_response)
    g.set_entry_point("classify_intent")
    g.add_conditional_edges("classify_intent", route_after_intent, {"extract_lead_field":"extract_lead_field","retrieve_context":"retrieve_context","generate_response":"generate_response"})
    g.add_edge("retrieve_context", "generate_response")
    g.add_conditional_edges("extract_lead_field", route_after_extraction, {"capture_lead":"capture_lead","generate_response":"generate_response"})
    g.add_edge("capture_lead", "generate_response")
    g.add_edge("generate_response", END)
    return g.compile()
