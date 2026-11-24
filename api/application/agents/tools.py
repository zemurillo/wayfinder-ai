import os
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from api.domain.models import CalculoMilhas

@tool
def calcular_viabilidade_milhas(preco_dinheiro: float, pontos_necessarios: int, taxas_brl: float, cpm_acumulo: float = 17.50) -> str:
    """Calcula matematicamente se vale a pena pagar uma passagem em dinheiro ou resgatar em milhas.
    
    Args:
        preco_dinheiro: Valor em Reais (R$).
        pontos_necessarios: Total de milhas/pontos cobrados.
        taxas_brl: Taxas de embarque em Reais (R$).
        cpm_acumulo: Custo por 1.000 milhas do usuário (padrão médio: R$ 17.50).
    """
    calculo = CalculoMilhas(
        preco_dinheiro=preco_dinheiro,
        pontos_necessarios=pontos_necessarios,
        taxas_brl=taxas_brl,
        cpm_usuario=cpm_acumulo
    )

    cpm_corte = calculo.calcular_cpm_de_corte()
    vale_a_pena = calculo.vale_a_pena_usar_milhas()
    custo_milhas = (pontos_necessarios / 1000) * cpm_acumulo + taxas_brl
    economia = preco_dinheiro - custo_milhas

    if vale_a_pena:
        parecer = f"VALE A PENA USAR MILHAS! Economia estimada de R$ {economia:.2f}."
    else:
        parecer = f"MELHOR PAGAR EM DINHEIRO. Resgatar em milhas sairá R$ {abs(economia):.2f} mais caro."

    return (
        f"--- ANÁLISE DE MILHAS ---\n"
        f"Preço em dinheiro: R$ {preco_dinheiro:.2f}\n"
        f"Custo em milhas (CPM R$ {cpm_acumulo:.2f}): R$ {custo_milhas:.2f} (com taxas)\n"
        f"CPM limite para empatar: R$ {cpm_corte:.2f}/milheiro\n"
        f"Parecer: {parecer}"
    )

@tool
def pesquisar_passagens_web(origem: str, destino: str, data: str) -> str:
    """Busca cotações atuais de voos na web."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return f"[Dados Simulados] Voos de {origem} para {destino} em {data}: Média de R$ 850,00 a R$ 1.250,00 (Insira a SERPAPI_API_KEY no arquivo .env para buscas reais)."

    params = {
        "engine": "google_flights",
        "departure_id": origem,
        "arrival_id": destino,
        "outbound_date": data,
        "currency": "BRL",
        "hl": "pt"
    }
    search = SerpAPIWrapper(params=params)
    return search.run(f"voos de {origem} para {destino} em {data}")