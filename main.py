import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from langchain_core.messages import HumanMessage
from agent.graph import compile_agent
from agent.state import AgentState

def run():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: set ANTHROPIC_API_KEY first"); sys.exit(1)
    agent = compile_agent()
    state: AgentState = {"messages":[],"intent":"unknown","lead_data":{},"lead_captured":False,"collecting_lead":False,"awaiting_field":None,"kb_context":"","turn_count":0}
    print("\n=== AutoStream AI Agent (type 'quit' to exit) ===\n")
    print("Alex: Hey! Welcome to AutoStream. I can help with pricing, features, or getting you started. What can I help you with?\n")
    while True:
        try: user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt): break
        if not user: continue
        if user.lower() in ("quit","exit","bye"): print("Alex: Thanks! Happy creating!"); break
        state["messages"].append(HumanMessage(content=user))
        result = agent.invoke(state)
        state.update(result)
        ai_msgs = [m for m in state["messages"] if hasattr(m,"type") and m.type=="ai"]
        if ai_msgs: print(f"\nAlex: {ai_msgs[-1].content}\n")

if __name__ == "__main__":
    run()
