import os
import operator
from dotenv import load_dotenv

load_dotenv(override=True)

from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


class State(TypedDict):
    user_message: str
    agent_history: Annotated[list, operator.add]
    current_round: int
    judge_output: dict | None


class JuryOutput(BaseModel):
    thesis: str = Field(description="Değerlendirme yorumu")
    reasoning: str = Field(description="Tezini destekleyen argümanları belirt")
    counter_thesis: str = Field(description="Hangi Agent'ın hangi görüşüne karşı ise Agent'ın adını ve karşıt görüşünü belirt")
    counter_reasoning: str = Field(description="Karşıt görüşü destekleyen argümanları belirt")
    sources: list[str] = Field(description="Tavily ile elde ettiğin kaynakların listesi")

class JudgeOutput(BaseModel):
    thesis: str = Field(description="Kullanıcının sorusuna karşı verdiğin tezi belirt")
    reasoning: str = Field(description="Tezini destekleyen argümanları belirt")
    
    jury_1_score: int = Field(description="Jury 1 (Resmi/Tarihi Kaynaklar) için 1-10 arası performans puanı")
    jury_1_reason: str = Field(description="Jury 1 için puanlanma gerekçesi")
    
    jury_2_score: int = Field(description="Jury 2 (Sosyal Medya/Kamuoyu) için 1-10 arası performans puanı")
    jury_2_reason: str = Field(description="Jury 2 için puanlanma gerekçesi")
    
    jury_3_score: int = Field(description="Jury 3 (Akademik/Bilimsel Veriler) için 1-10 arası performans puanı")
    jury_3_reason: str = Field(description="Jury 3 için puanlanma gerekçesi")
    
    final_response: str = Field(description="Kullanıcıya verilen final yanıt")
    sources: list[str] = Field(description="Agentların getirdiği kaynaklar arasında en beğendiğin kaynakların listesi")

class JuryAgents:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = [TavilySearchResults(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=5)]
        self.agent = create_react_agent(self.llm, self.tools, response_format=JuryOutput)

    def context_input(self, system_prompt: str, state: State) -> list:
        history = state["agent_history"]
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
                Konu: {state['user_message']}
                
                Önceki turlarda söylenenler:
                {history if history else "İlk tur, henüz tartışma yok."}
                
                Görüşünü belirt.
            """)
        ]


class JudgeAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1, openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.agent = create_react_agent(self.llm, [], response_format=JudgeOutput)

    def context_input(self, system_prompt: str, state: State) -> list:
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
                Konu: {state['user_message']}
                
                Jüri Tartışması (3 tur):
                {state['agent_history']}
                
                Tüm argümanları değerlendirip final kararını ver.
            """)
        ]

jury_agents = JuryAgents()
judge_agent = JudgeAgent()
