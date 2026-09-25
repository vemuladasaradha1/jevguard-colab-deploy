
from typing import TypedDict


class AgentState(TypedDict, total=False):
    query: str

    injection_probability: float

    decision: str
    decision_confidence: float

    calculator_probability: float
    web_probability: float
    complexity_score: float
    complexity_confidence: float

    selected_tools: list[str]
    tools_used: list[str]

    calculator_result: str
    web_result: str
    tool_errors: list[str]
    evidence: str

    draft_answer: str

    answer_quality: float
    answer_quality_confidence: float
    grounded_probability: float
    safe_probability: float
    composite_risk: float

    needs_more_tool_probability: float
    tool_round: int

    final_answer: str
    status: str
