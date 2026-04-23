from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

IntentType = Literal["greeting","product_inquiry","pricing_inquiry","high_intent_lead","out_of_scope","unknown"]

class LeadData(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: IntentType
    lead_data: LeadData
    lead_captured: bool
    collecting_lead: bool
    awaiting_field: Optional[Literal["name", "email", "platform", None]]
    kb_context: str
    turn_count: int
