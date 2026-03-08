from agents import jury_agents, judge_agent, JuryOutput, JudgeOutput, State
from prompts import JURY_1_PROMPT, JURY_2_PROMPT, JURY_3_PROMPT, JUDGE_PROMPT


def jury_1_node(state: State) -> dict:
    messages = jury_agents.context_input(JURY_1_PROMPT, state)
    result = jury_agents.agent.invoke({"messages": messages})
    response = result["structured_response"]
    return {"agent_history": [{"round": state["current_round"], 
            "agent_name": "Jury 1 (Resmi/Tarihi Kaynaklar)",
            "thesis": response.thesis, 
            "counter_thesis": response.counter_thesis, 
            "counter_reasoning": response.counter_reasoning,
            "reasoning": response.reasoning,
            "sources": response.sources}]}


def jury_2_node(state: State) -> dict:
    messages = jury_agents.context_input(JURY_2_PROMPT, state)
    result = jury_agents.agent.invoke({"messages": messages})
    response = result["structured_response"]
    return {"agent_history": [{"round": state["current_round"], 
            "agent_name": "Jury 2 (Kamuoyu/Sosyal Medya)",
            "thesis": response.thesis, 
            "counter_thesis": response.counter_thesis, 
            "counter_reasoning": response.counter_reasoning,
            "reasoning": response.reasoning,
            "sources": response.sources}]}


def jury_3_node(state: State) -> dict:
    messages = jury_agents.context_input(JURY_3_PROMPT, state)
    result = jury_agents.agent.invoke({"messages": messages})
    response = result["structured_response"]
    return {"agent_history": [{"round": state["current_round"],
            "agent_name": "Jury 3 (Akademik/Bilimsel Veriler)",
            "thesis": response.thesis, 
            "counter_thesis": response.counter_thesis, 
            "counter_reasoning": response.counter_reasoning,
            "reasoning": response.reasoning,
            "sources": response.sources}]}


def judge_node(state: State) -> dict:
    messages = judge_agent.context_input(JUDGE_PROMPT, state)
    result = judge_agent.agent.invoke({"messages": messages})
    response = result["structured_response"]
    return {"judge_output": {
        "thesis": response.thesis, 
        "reasoning": response.reasoning,
        "jury_1_score": response.jury_1_score,
        "jury_1_reason": response.jury_1_reason,
        "jury_2_score": response.jury_2_score,
        "jury_2_reason": response.jury_2_reason,
        "jury_3_score": response.jury_3_score,
        "jury_3_reason": response.jury_3_reason,
        "final_response": response.final_response,
        "sources": response.sources
    }}


def dispatch_node(state: State) -> dict:
    """Hiçbir şey yapmaz, sadece paralel dağıtım noktası."""
    return {}


def round_check_node(state: State) -> dict:
    return {"current_round": state["current_round"] + 1}


def should_continue(state: State) -> str:
    if state["current_round"] < 3:
        return "continue"
    else:
        return "judge"


