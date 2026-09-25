
from __future__ import annotations

import re
from dataclasses import dataclass

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

from .config import Settings
from .state import AgentState

#import os
#load_dotenv()


def get_jev_answer(response, name: str):
    if hasattr(response, "answers"):
        return response.answers[name]
    if hasattr(response, "choices"):
        return response.choices[name]
    raise RuntimeError(f"Unknown Jev response format: {dir(response)}")


@dataclass
class PlannerResult:
    decision: str
    decision_confidence: float
    calculator_probability: float
    web_probability: float
    complexity_score: float
    complexity_confidence: float


def build_jev(settings: Settings) -> TypeSafeClient:
    if not settings.typesafe_api_key:
        raise RuntimeError("TYPESAFE_API_KEY is not configured.")
    return TypeSafeClient(
        api_key= settings.typesafe_api_key,
        base_url="https://openrouter.ai/api"
    )


def deterministic_signals(query: str) -> tuple[bool, bool]:
    q = query.lower()

    arithmetic = bool(
        re.search(r"\b(calculate|compute|multiply|multiplied|divide|divided|sum|subtract|add|percentage|percent|average|sqrt)\b", q)
        or re.search(r"\d+\s*[\+\-\*/%]\s*\d+", q)
    )

    web = bool(
        re.search(
            r"\b(current|today|latest|recent|news|price|weather|stock|score|now|2026|this week)\b",
            q,
        )
    )

    return arithmetic, web


def fallback_plan(query: str) -> PlannerResult:
    arithmetic, web = deterministic_signals(query)

    if arithmetic and web:
        decision = "calculator_and_web"
    elif arithmetic:
        decision = "calculator"
    elif web:
        decision = "web"
    else:
        decision = "direct"

    return PlannerResult(
        decision=decision,
        decision_confidence=0.55,
        calculator_probability=0.95 if arithmetic else 0.05,
        web_probability=0.95 if web else 0.05,
        complexity_score=2.0,
        complexity_confidence=0.40,
    )


def jev_plan(jev: TypeSafeClient, state: AgentState) -> PlannerResult:
    query = state["query"]

    response = jev.system_one(
        state={"query": query},
        questions={
            "decision": Choice(
                instructions="""
                Choose the best execution mode for the user's request.

                direct = answer from the language model's general knowledge;
                calculator = mathematical computation is materially required;
                web_search = current/external information is materially required;
                calculator_and_web = both are materially required.

                Do not choose web_search merely because web could add
                extra context. Choose it when freshness or external facts
                are important to answering the question.
                """,
                choices=[
                    "direct",
                    "calculator",
                    "web_search",
                    "calculator_and_web",
                ],
            ),
            "needs_calculator": Noul(
                instructions="Does the request materially require mathematical calculation?"
            ),
            "needs_web": Noul(
                instructions="Does the request materially require current or external web information?"
            ),
            "complexity": Score(
                instructions="Assess the reasoning/tool complexity of this request.",
                criteria=[
                    "Very simple",
                    "Simple",
                    "Moderate",
                    "Complex",
                    "Very complex",
                ],
            ),
        },
    )

    decision = get_jev_answer(response, "decision")
    calc = get_jev_answer(response, "needs_calculator")
    web = get_jev_answer(response, "needs_web")
    complexity = get_jev_answer(response, "complexity")

    return PlannerResult(
        decision=str(decision.choice),
        decision_confidence=float(decision.confidence),
        calculator_probability=float(calc.noul),
        web_probability=float(web.noul),
        complexity_score=float(complexity.score),
        complexity_confidence=float(complexity.confidence),
    )


def validate_plan(query: str, plan: PlannerResult) -> PlannerResult:
    arithmetic, web = deterministic_signals(query)

    # Deterministic safety net: obvious arithmetic must not be sent to
    # the direct path merely because Jev under-called the calculator.
    if arithmetic and plan.decision == "direct":
        decision = "calculator_and_web" if web else "calculator"
        return PlannerResult(
            decision=decision,
            decision_confidence=min(plan.decision_confidence, 0.60),
            calculator_probability=max(plan.calculator_probability, 0.90),
            web_probability=max(plan.web_probability, 0.90 if web else plan.web_probability),
            complexity_score=plan.complexity_score,
            complexity_confidence=plan.complexity_confidence,
        )

    if web and plan.decision == "direct":
        return PlannerResult(
            decision="web_search",
            decision_confidence=min(plan.decision_confidence, 0.60),
            calculator_probability=plan.calculator_probability,
            web_probability=max(plan.web_probability, 0.90),
            complexity_score=plan.complexity_score,
            complexity_confidence=plan.complexity_confidence,
        )

    return plan
