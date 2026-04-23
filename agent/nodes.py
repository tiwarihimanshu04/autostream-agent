import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from agent.state import AgentState
from tools.tools import mock_lead_capture, retrieve_knowledge

SYSTEM_PROMPT = """You are Alex, a friendly sales assistant for AutoStream — an AI-powered video editing SaaS for content creators.
- Answer product/pricing questions accurately using the knowledge base context provided
- When user shows high intent, collect name, email, platform ONE AT A TIME
- Never make up pricing or features
- Never ask for all 3 lead fields at once
- Never call lead capture until you have all 3 values
"""

def _llm():
    return ChatAnthropic(model="claude-haiku-4-5", temperature=0.3, anthropic_api_key=os.environ["ANTHROPIC_API_KEY"])

def classify_intent(state):
    msgs = state["messages"]
    last = next((m.content.lower() for m in reversed(msgs) if isinstance(m, HumanMessage)), "")
    if not last: return {"intent": "unknown"}
    if any(k in last for k in ["sign up","i want to","i want the","ready to","get started","buy","subscribe","try it","start my trial"]): return {"intent": "high_intent_lead"}
    if any(k in last for k in ["price","pricing","cost","plan","how much","$","basic","pro"]): return {"intent": "pricing_inquiry"}
    if any(k in last for k in ["feature","refund","cancel","support","4k","caption","what does","how does"]): return {"intent": "product_inquiry"}
    if any(k in last for k in ["hi","hello","hey","good morning"]) and len(last.split()) <= 5: return {"intent": "greeting"}
    result = _llm().invoke([HumanMessage(content=f'Classify into one label only: greeting, pricing_inquiry, product_inquiry, high_intent_lead, out_of_scope\nMessage: "{last}"\nRespond with ONLY the label.')])
    raw = result.content.strip().lower()
    return {"intent": raw if raw in {"greeting","pricing_inquiry","product_inquiry","high_intent_lead","out_of_scope"} else "unknown"}

def retrieve_context(state):
    last = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    return {"kb_context": retrieve_knowledge(last) if last else ""}

def extract_lead_field(state):
    last = next((m.content.strip() for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    awaiting = state.get("awaiting_field")
    lead = dict(state.get("lead_data", {}))
    if not awaiting or not last: return {}
    if awaiting == "name": lead["name"] = last; return {"lead_data": lead, "awaiting_field": "email"}
    if awaiting == "email":
        if re.match(r"[^@]+@[^@]+\.[^@]+", last): lead["email"] = last; return {"lead_data": lead, "awaiting_field": "platform"}
        return {"lead_data": lead, "awaiting_field": "email"}
    if awaiting == "platform": lead["platform"] = last; return {"lead_data": lead, "awaiting_field": None}
    return {}

def capture_lead(state):
    d = state.get("lead_data", {})
    mock_lead_capture(d.get("name",""), d.get("email",""), d.get("platform",""))
    return {"lead_captured": True, "collecting_lead": False}

def generate_response(state):
    intent = state.get("intent","unknown")
    kb = state.get("kb_context","")
    lead = state.get("lead_data",{})
    captured = state.get("lead_captured", False)
    collecting = state.get("collecting_lead", False)
    awaiting = state.get("awaiting_field")
    sys_content = SYSTEM_PROMPT
    if kb: sys_content += f"\n\nKnowledge Base:\n{kb}"
    if captured:
        sys_content += f"\n\nLead captured! Name={lead.get('name')}, Email={lead.get('email')}, Platform={lead.get('platform')}. Warmly confirm and tell them to expect a welcome email."
    elif collecting and awaiting:
        sys_content += f"\n\nCollecting lead. Collected so far: {lead}. Now ask ONLY for: {awaiting}. One field at a time."
    elif intent == "high_intent_lead" and not collecting:
        sys_content += "\n\nUser has HIGH intent. Ask for their full name to get started."
    msgs = [SystemMessage(content=sys_content)] + state["messages"][-10:]
    response = _llm().invoke(msgs)
    updates = {"messages": [AIMessage(content=response.content)], "turn_count": state.get("turn_count",0)+1}
    if intent == "high_intent_lead" and not collecting and not captured:
        updates["collecting_lead"] = True
        updates["awaiting_field"] = "name"
    return updates
