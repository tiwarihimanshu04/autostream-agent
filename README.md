# AutoStream AI Sales Agent 
> **Stack:** Python · LangGraph · Claude 3 Haiku · RAG · Tool Calling

---

## 📁 Project Structure

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/tiwarihimanshu04/autostream-agent.git
cd autostream-agent
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your API key
```bash
export ANTHROPIC_API_KEY="your-claude-api-key-here"
```

### 5. Run the agent
```bash
python main.py
```

---

## 🧠 Architecture Explanation

This agent is built using **LangGraph**, a graph-based orchestration framework from the LangChain ecosystem. LangGraph was chosen over AutoGen because it offers explicit, inspectable state management through a typed StateGraph — every conversation turn flows through a deterministic graph of nodes, making the logic transparent, testable, and easy to extend.

**State Management:** All conversation context — message history, detected intent, lead collection progress, and retrieved knowledge — lives in a single AgentState TypedDict. LangGraph's add_messages reducer automatically appends new messages without overwriting history, giving the agent persistent memory across 5–6+ turns.

**Graph Flow:**
1. `classify_intent` — Classifies user input using rule-based heuristics + LLM fallback
2. `retrieve_context` — Performs RAG retrieval from the local JSON knowledge base
3. `extract_lead_field` — Parses the awaited lead field (name → email → platform) from user input
4. `capture_lead` — Calls mock_lead_capture() only when all three fields are collected
5. `generate_response` — Builds a context-aware system prompt and generates a reply via Claude 3 Haiku

Conditional edges enforce correct sequencing: the lead tool is never triggered prematurely, and field collection happens one-at-a-time through the awaiting_field state variable.

---

## 💬 Expected Conversation Flow

---

## 📱 WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, use the **WhatsApp Business API (Meta Cloud API)** with a webhook integration.

**Architecture:**

**Steps:**
1. Register a WhatsApp Business App on Meta for Developers
2. Set up a FastAPI webhook endpoint to receive messages
3. On each incoming message, restore the user's session state, run the agent, extract the AI reply
4. Send the reply back via `POST /messages` to the WhatsApp Cloud API
5. Add a GET endpoint to verify the webhook with Meta
6. Deploy on a public HTTPS server (Railway, Render, AWS)
7. Replace in-memory session storage with Redis for persistence across restarts

---

## ✅ Evaluation Checklist

| Criterion | Status |
|-----------|--------|
| Intent detection (greeting / inquiry / high-intent) | ✅ |
| RAG from local knowledge base | ✅ |
| Lead collection one field at a time | ✅ |
| Tool not triggered prematurely | ✅ |
| Memory across 5–6 turns | ✅ |
| Clean code structure | ✅ |
| WhatsApp deployment explanation | ✅ |
