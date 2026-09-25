
from __future__ import annotations

import ast
import operator as op
import re
from typing import Any

from ddgs import DDGS

_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_safe_eval(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")
        if abs(left) > 1e100 or abs(right) > 1e100:
            raise ValueError("Number is too large.")

        return _ALLOWED_BINOPS[type(node.op)](left, right)

    raise ValueError("Only basic arithmetic expressions are allowed.")


def calculator_tool(expression: str) -> str:
    expression = expression.strip().replace("^", "**")

    if len(expression) > 200:
        raise ValueError("Expression is too long.")

    if not re.fullmatch(r"[0-9\s\+\-\*\/\%\(\)\.]+", expression):
        raise ValueError("Unsafe calculator expression.")

    tree = ast.parse(expression, mode="eval")
    value = _safe_eval(tree.body)

    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def extract_expression(query: str) -> str | None:
    # Prefer an explicit arithmetic expression.
    candidates = re.findall(r"(?<!\w)\d+(?:\s*[\+\-\*\/%]\s*\d+)+(?!\w)", query)
    if candidates:
        return candidates[0]

    # Handle common natural-language multiplication/division/addition.
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:times|multiplied by|x)\s*(\d+(?:\.\d+)?)",
        query,
        flags=re.IGNORECASE,
    )
    if m:
        return f"{m.group(1)} * {m.group(2)}"

    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:divided by)\s*(\d+(?:\.\d+)?)",
        query,
        flags=re.IGNORECASE,
    )
    if m:
        return f"{m.group(1)} / {m.group(2)}"

    return None


def web_search_tool(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    results = DDGS().text(query, max_results=max_results)
    if not results:
        return []

    return [
        {
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", ""),
        }
        for item in results
    ]
