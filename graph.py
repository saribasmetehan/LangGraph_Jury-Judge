from langgraph.graph import StateGraph, START, END
from agents import State
from nodes import (
    dispatch_node,
    jury_1_node,
    jury_2_node,
    jury_3_node,
    round_check_node,
    should_continue,
    judge_node
)

builder = StateGraph(State)

builder.add_node("dispatch", dispatch_node)
builder.add_node("jury_1", jury_1_node)
builder.add_node("jury_2", jury_2_node)
builder.add_node("jury_3", jury_3_node)
builder.add_node("round_check", round_check_node)
builder.add_node("judge", judge_node)

builder.add_edge(START, "dispatch")
builder.add_edge("dispatch", "jury_1")
builder.add_edge("dispatch", "jury_2")
builder.add_edge("dispatch", "jury_3")
builder.add_edge("jury_1", "round_check")
builder.add_edge("jury_2", "round_check")
builder.add_edge("jury_3", "round_check")

builder.add_conditional_edges(
    "round_check",
    should_continue,
    {
        "continue": "dispatch",
        "judge": "judge"
    }
)

builder.add_edge("judge", END)

graph = builder.compile()

