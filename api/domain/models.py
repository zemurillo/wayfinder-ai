# Define os modelos de dados da viagem e os calculos relacionados ao uso de milhas.
from dataclasses import dataclass
from typing import Optional

@dataclass
class RequisicaoViagem:
    origem: str
    destino: str
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    orcamento_maximo: Optional[float] = None
    usar_milhas: bool = False
    programa_fidelidade: Optional[str] = None

@dataclass
class CalculoMilhas:
    preco_dinheiro: float
    pontos_necessarios: int
    taxas_brl: float
    cpm_usuario: float = 17.50

    def calcular_cpm_de_corte(self) -> float:
        """Calcula o valor mínimo por 1.000 milhas para valer a pena a emissão."""
        if self.pontos_necessarios == 0:
            return 0.0
        return ((self.preco_dinheiro - self.taxas_brl) / self.pontos_necessarios) * 1000

    def vale_a_pena_usar_milhas(self) -> bool:
        """Retorna True se o custo equivalente em milhas for menor que o preço em dinheiro."""
        custo_real_milhas = (self.pontos_necessarios / 1000) * self.cpm_usuario + self.taxas_brl
        return custo_real_milhas < self.preco_dinheiro