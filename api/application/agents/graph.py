import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from api.application.agents.tools import calcular_viabilidade_milhas, pesquisar_passagens_web

load_dotenv()

tools = [calcular_viabilidade_milhas, pesquisar_passagens_web]
tool_node = ToolNode(tools)

# Groq oferece Llama 3.1 com execuções extremamente rápidas e gratuitas
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
).bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = """Você é o Wayfinder AI, um assistente especialista em planejamento de viagens e engenharia de milhas aéreas.
Sua missão é ajudar o usuário com itinerários, pesquisas de passagens e cálculos entre pagar em dinheiro ou usar milhas.
Sempre utilize as ferramentas disponíveis para realizar cálculos precisos de milhas ou buscar cotações quando o usuário fornecer dados específicos."""

def call_model(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

app_graph = workflow.compile()