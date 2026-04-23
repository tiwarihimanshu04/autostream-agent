import json, os, re
from datetime import datetime

_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "autostream_kb.json")
with open(_KB_PATH, "r") as f:
    _KB = json.load(f)

def mock_lead_capture(name, email, platform):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "="*55)
    print(f"  Lead captured successfully: {name}, {email}, {platform}")
    print(f"  Time: {ts}")
    print("="*55 + "\n")
    return {"success": True, "message": f"Lead captured successfully: {name}, {email}, {platform}"}

def retrieve_knowledge(query):
    q = query.lower()
    results = []
    if any(k in q for k in ["price","plan","cost","how much","basic","pro","pay"]):
        t = "**AutoStream Pricing Plans:**\n\n"
        for p in _KB["plans"]:
            t += f"* **{p['name']}** — ${p['price_monthly']}/month\n"
            for f in p["features"]: t += f"  • {f}\n"
        results.append(t)
    if any(k in q for k in ["refund","cancel","support","policy","24/7"]):
        t = "**Policies:**\n\n"
        for p in _KB["policies"]: t += f"* **{p['topic']}:** {p['details']}\n"
        results.append(t)
    if any(k in q for k in ["what","how","platform","format","install","youtube","instagram"]):
        t = "**FAQs:**\n\n"
        for f in _KB["faqs"]: t += f"* **{f['question']}** {f['answer']}\n"
        results.append(t)
    if any(k in q for k in ["what is","about","autostream","product"]):
        c = _KB["company"]
        results.append(f"**About AutoStream:** {c['description']} Tagline: \"{c['tagline']}\"")
    return "\n---\n".join(results) if results else "Basic Plan $29/month (10 videos, 720p). Pro Plan $79/month (unlimited, 4K, AI captions, 24/7 support). Free 7-day trial. No refunds after 7 days."
