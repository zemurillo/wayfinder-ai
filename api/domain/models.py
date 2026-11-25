# Define os modelos de dados da viagem e os calculos relacionados ao uso de milhas.
# É o núcleo do domínio da aplicação, encapsulando a lógica de negócios e as regras de cálculo.
from dataclasses import dataclass
from typing import Optional

#Descreva o que é o dataclass:
# Um dataclass é uma classe que automatiza a criação de métodos especiais, como __init__, __repr__, e __eq__, com base em atributos definidos.
#Data classes são úteis para armazenar dados de forma estruturada e concisa, sem a necessidade de escrever código repetitivo para inicialização e representação de objetos.
@dataclass
class RequisicaoViagem:
    origem: str
    destino: str
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    orcamento_maximo: Optional[float] = None
    usar_milhas: bool = False
    programa_fidelidade: Optional[str] = None

#Lógica matemática deterministica do cálculo de milhas, custo por milheiro (CPM) e análise de viabilidade de resgate de passagens com milhas.
#CPM = custo por milheiro, que é o custo por 1.000 milhas. É calculado dividindo o preço em dinheiro pelo número de milhas necessárias e multiplicando por 1.000.
@dataclass
class CalculoMilhas:
    preco_dinheiro: float
    pontos_necessarios: int
    taxas_brl: float
    cpm_usuario: float = 17.50
    #cpm_usuario é o custo por 1.000 milhas do usuário, que é usado para calcular o custo real de resgatar uma passagem com milhas.

    def calcular_cpm_de_corte(self) -> float:
        """Calcula o valor mínimo por 1.000 milhas para valer a pena a emissão."""
        if self.pontos_necessarios == 0:
            return 0.0
        return ((self.preco_dinheiro - self.taxas_brl) / self.pontos_necessarios) * 1000

    def vale_a_pena_usar_milhas(self) -> bool:
        """Retorna True se o custo equivalente em milhas for menor que o preço em dinheiro."""
        custo_real_milhas = (self.pontos_necessarios / 1000) * self.cpm_usuario + self.taxas_brl
        return custo_real_milhas < self.preco_dinheiro