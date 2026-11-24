from api.application.agents.graph import app_graph
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    print("🤖 Iniciando teste do Wayfinder AI Agent...")
    
    pergunta = "Quero viajar de São Paulo para Foz do Iguaçu. Uma passagem custa R$ 850 no PIX ou 32.000 milhas Smiles mais R$ 50 de taxa de embarque. Meu CPM acumulado é R$ 17,50. Vale a pena?"
    
    resposta = app_graph.invoke({"messages": [HumanMessage(content=pergunta)]})
    
    print("\n--- RESPOSTA DO AGENTE ---")
    print(resposta["messages"][-1].content)