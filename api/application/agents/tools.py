import os
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from api.domain.models import CalculoMilhas
from typing import Optional

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


# A ferramenta de pesquisa de passagens web utiliza a API do SerpAPI para buscar cotações atuais de voos na web, permitindo que o usuário encontre as melhores opções de viagem com base em critérios como origem, destino e data.

@tool
def pesquisar_passagens_web(origem: str, destino: str, data_ida: str, data_volta: Optional[str] = None) -> str:
    """Busca cotações atuais de voos na web (Somente Ida ou Ida e Volta).
    
    Args:
        origem: Código IATA ou nome da cidade de origem (ex: GRU, São Paulo).
        destino: Código IATA ou nome da cidade de destino (ex: IGU, Foz do Iguaçu).
        data_ida: Data da ida no formato YYYY-MM-DD.
        data_volta: Data da volta opcional no formato YYYY-MM-DD. Se fornecida, realiza busca de ida e volta.
    """
    # 1. Busca a chave de API da SerpAPI nas variáveis de ambiente (.env)
    api_key = os.getenv("SERPAPI_API_KEY")
    
    # 2. FALLBACK DE SEGURANÇA: Se a chave não existir no .env, não quebra a aplicação.
    # Retorna uma simulação textual para o agente continuar o desenvolvimento offline.
    if not api_key:
        tipo_str = f"Ida ({data_ida}) e Volta ({data_volta})" if data_volta else f"Somente Ida ({data_ida})"
        return f"[Dados Simulados] Voos de {origem} para {destino} [{tipo_str}]: Média de R$ 850,00 a R$ 1.600,00."

    try:
        # 3. DEFINE O TIPO DE VIAGEM SEGUNDO O PADRÃO DO GOOGLE FLIGHTS:
        # "1" = Round trip (Ida e Volta) | "2" = One way (Somente Ida)
        tipo_busca = "1" if data_volta else "2"
        
        # 4. MONTA O DICIONÁRIO DE PARÂMETROS DA REQUISIÇÃO:
        # Passamos a engine do Google Flights, códigos dos aeroportos/cidades, data de partida e moeda (BRL).
        params = {
            "engine": "google_flights",
            "departure_id": origem,
            "arrival_id": destino,
            "outbound_date": data_ida,
            "type": tipo_busca,
            "currency": "BRL",
            "hl": "pt",
            "serp_api_key": api_key
        }

        # 5. REGRA CONDICIONAL DE RETORNO:
        # O Google Flights exige o parâmetro 'return_date' APENAS quando o 'type' é "1" (Ida e Volta).
        # Adicionamos essa chave dinamicamente somente quando data_volta for informada pelo agente.
        if data_volta:
            params["return_date"] = data_volta

        # 6. INSTANCIA O WRAPPER DA SERPAPI NO LANGCHAIN COM OS PARÂMETROS MONTADOS
        search = SerpAPIWrapper(params=params)
        
        # 7. MONTA A STRING DE CONSULTA E EXECUTA A REQUISIÇÃO HTTP PARA A API EXTERNA
        termo_busca = f"voos de {origem} para {destino} ida {data_ida}" + (f" volta {data_volta}" if data_volta else "")
        resultado = search.run(termo_busca)
        
        # 8. Retorna o texto bruto retornado pela SerpAPI contendo as companhias, horários e valores
        return resultado

    except Exception as e:
        # 9. TRATAMENTO DE EXCEÇÃO (Resiliência):
        # Se ocorrer erro de cota esgotada, problema de rede ou parâmetro inválido da API externa,
        # capturamos a exceção e retornamos um aviso estruturado para o LLM não estourar Traceback.
        return (
            f"[Aviso SerpAPI] Não foi possível obter voos em tempo real devido ao erro: {str(e)}. "
            f"Considere estimativas médias de mercado para o trecho {origem} -> {destino}."
        )