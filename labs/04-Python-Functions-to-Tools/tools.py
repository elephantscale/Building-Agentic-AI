"""
Lab 4 - Plain Python functions, promoted to agentic tools.

A "tool" is just a Python function PLUS three things the model needs:
    - a name and description  (so the model knows WHEN to call it)
    - a JSON Schema           (so the model knows WHAT args are legal)
    - a safety class          (so YOUR code knows what gate to apply)

This module owns the tools and their metadata. `tool_agent.py` owns the
tool-calling loop that validates args, dispatches, and gates by safety class.

Safety classes (see course-materials/tool-spec-template.md):
    safe      - read-only, no side effects            -> run freely
    guarded   - writes, but reversible                -> log + validate
    dangerous - irreversible (send/delete/pay)        -> human approval required
"""

import ast
import operator
from pathlib import Path

# Shared help-center asset (labs/assets/help_center.md), relative to this file.
HELP_CENTER = Path(__file__).resolve().parents[1] / "assets" / "help_center.md"


# --- The plain functions -----------------------------------------------------

# A tiny fake order database so the lab runs with no network.
_ORDERS = {
    "88123": {"status": "shipped_twice", "items": 2, "total_usd": 240.00,
              "note": "Duplicate shipment detected; eligible for refund of one charge."},
    "88124": {"status": "in_transit", "items": 1, "total_usd": 120.00,
              "note": "Expected delivery in 2 business days."},
    "88125": {"status": "delivered", "items": 3, "total_usd": 360.00,
              "note": "Delivered and signed for."},
}


def get_order_status(order_id: str) -> dict:
    """Look up an order's status by ID. Read-only -> safe."""
    order = _ORDERS.get(order_id)
    if order is None:
        return {"ok": False, "error": "not_found", "order_id": order_id}
    return {"ok": True, "order_id": order_id, **order}


def lookup_help_center(query: str, max_chars: int = 500) -> dict:
    """Search the Northwind help center for lines matching a query. Read-only -> safe.

    Returns bounded, structured data - never dumps the whole file into context.
    """
    if not HELP_CENTER.exists():
        return {"ok": False, "error": "help_center_missing", "path": str(HELP_CENTER)}
    text = HELP_CENTER.read_text(encoding="utf-8")
    terms = [t for t in query.lower().split() if t]
    hits = [ln.strip(" -") for ln in text.splitlines()
            if ln.strip() and any(t in ln.lower() for t in terms)]
    snippet = "\n".join(hits)[:max_chars]
    return {"ok": True, "query": query, "matches": len(hits),
            "snippet": snippet or "No matching help-center content found."}


# A safe arithmetic evaluator: parse to an AST and allow ONLY math operators.
_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


def calc(expression: str) -> dict:
    """Evaluate a basic arithmetic expression, e.g. '2 * (17 + 42)'. Pure -> safe.

    Uses an AST walk, NOT eval(), so no names, calls, or attribute access are possible.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        return {"ok": True, "expression": expression, "result": _eval_node(tree.body)}
    except Exception as exc:  # tool errors are data, not crashes
        return {"ok": False, "error": "bad_expression", "detail": str(exc)}


# --- Tool metadata: schema + safety class ------------------------------------
# One registry entry per tool. `tool_agent.py` reads this to build the API
# `tools` payload, to validate args, and to decide which calls need a human gate.

TOOLS = {
    "get_order_status": {
        "fn": get_order_status,
        "safety": "safe",
        "description": "Look up the current status of a customer order by its ID. "
                       "Use when the user references an order number. Read-only.",
        "schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "pattern": "^[0-9]{4,6}$",
                             "description": "Numeric order ID, e.g. 88123"},
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    "lookup_help_center": {
        "fn": lookup_help_center,
        "safety": "safe",
        "description": "Search the Northwind help center for policy/how-to answers "
                       "(refunds, billing, accounts, seats). Read-only. Use for "
                       "'how do I...' or policy questions; do NOT use for order status.",
        "schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keywords to search for"},
                "max_chars": {"type": "integer", "minimum": 50, "maximum": 2000,
                              "default": 500},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    "calc": {
        "fn": calc,
        "safety": "safe",
        "description": "Evaluate a basic arithmetic expression (add, subtract, multiply, "
                       "divide, power). Use for any math instead of computing it yourself.",
        "schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string",
                               "description": "Arithmetic only, e.g. '2 * (17 + 42)'"},
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
}


def openai_tool_specs():
    """Render TOOLS into the OpenAI `tools` payload shape."""
    return [{
        "type": "function",
        "function": {
            "name": name,
            "description": meta["description"],
            "parameters": meta["schema"],
        },
    } for name, meta in TOOLS.items()]


def anthropic_tool_specs():
    """Render TOOLS into the Anthropic `tools` payload shape (same schema, different keys)."""
    return [{
        "name": name,
        "description": meta["description"],
        "input_schema": meta["schema"],
    } for name, meta in TOOLS.items()]
