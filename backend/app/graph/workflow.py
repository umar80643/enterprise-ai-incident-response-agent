from langgraph.graph import END, START, StateGraph

from app.agents.core_agents import (
    debugging,
    planner,
    repository_analysis,
    retrieval,
    reviewer,
    root_cause,
    solution,
    test_generation,
)
from app.graph.state import WorkflowState


def after_review(state):
    if state.get("approval_status") == "WAITING_APPROVAL":
        return END
    return END


def build_graph():
    g = StateGraph(WorkflowState)
    for name, fn in [
        ("planner", planner),
        ("repository_analysis", repository_analysis),
        ("retrieval", retrieval),
        ("debugging", debugging),
        ("root_cause", root_cause),
        ("solution", solution),
        ("testing", test_generation),
        ("reviewer", reviewer),
    ]:
        g.add_node(name, fn)
    g.add_edge(START, "planner")
    g.add_edge("planner", "repository_analysis")
    g.add_edge("repository_analysis", "retrieval")
    g.add_edge("retrieval", "debugging")
    g.add_edge("debugging", "root_cause")
    g.add_edge("root_cause", "solution")
    g.add_edge("solution", "testing")
    g.add_edge("testing", "reviewer")
    g.add_conditional_edges("reviewer", after_review)
    return g.compile()


graph = build_graph()
