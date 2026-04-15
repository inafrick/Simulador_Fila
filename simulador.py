"""
Simulador de Rede de Filas - Versão 2.0
Arquitetura preparada para topologia genérica com duas filas em tandem
"""

import heapq
from typing import Dict, List, Tuple, Optional


class LimiteAleatoriosAtingido(Exception):
    """Sinaliza que o limite de aleatórios foi atingido durante a simulação."""


class GeradorAleatorio:
    """Gerador de números pseudoaleatórios centralizado."""
    def __init__(self, semente=12345):
        self.semente = semente
        self.a = 1103515245
        self.c = 12345
        self.m = 2**31
        self.aleatorios_consumidos = 0
        self.limite_aleatorios: Optional[int] = None

    def definir_limite(self, limite: Optional[int]):
        """Define limite de consumo de aleatórios (None para sem limite)."""
        self.limite_aleatorios = limite
    
    def proximo(self) -> float:
        """Gera o próximo número pseudoaleatório entre 0 e 1."""
        if (self.limite_aleatorios is not None and
                self.aleatorios_consumidos >= self.limite_aleatorios):
            raise LimiteAleatoriosAtingido(
                f"Limite de {self.limite_aleatorios} aleatórios atingido"
            )

        self.semente = (self.a * self.semente + self.c) % self.m
        self.aleatorios_consumidos += 1
        return self.semente / self.m


class Fila:
    """Representa uma fila individual em uma rede."""
    
    def __init__(self, nome: str, servidores: int, capacidade: int, 
                 tempo_chegada_min: float, tempo_chegada_max: float,
                 tempo_atendimento_min: float, tempo_atendimento_max: float):
        self.nome = nome
        self.num_servidores = servidores
        self.capacidade = capacidade
        self.tempo_chegada_min = tempo_chegada_min
        self.tempo_chegada_max = tempo_chegada_max
        self.tempo_atendimento_min = tempo_atendimento_min
        self.tempo_atendimento_max = tempo_atendimento_max
        
        # Estado
        self.clientes_no_sistema = 0
        self.total_clientes_processados = 0
        self.total_clientes_perdidos = 0
        
        # Estatísticas
        self.tempo_no_estado = [0.0] * (capacidade + 1)
        self.ultimo_tempo_evento = 0.0
    
    def pode_aceitar_cliente(self) -> bool:
        """Verifica se há espaço na fila."""
        return self.clientes_no_sistema < self.capacidade
    
    def aceitar_cliente(self):
        """Adiciona um cliente à fila."""
        if self.pode_aceitar_cliente():
            self.clientes_no_sistema += 1
            return True
        else:
            self.total_clientes_perdidos += 1
            return False
    
    def remover_cliente(self):
        """Remove um cliente que saiu do sistema."""
        if self.clientes_no_sistema > 0:
            self.clientes_no_sistema -= 1
            self.total_clientes_processados += 1
            return True
        return False
    
    def atualizar_estatisticas(self, tempo_atual: float):
        """Atualiza tempo acumulado no estado atual."""
        delta_t = tempo_atual - self.ultimo_tempo_evento
        if 0 <= self.clientes_no_sistema <= self.capacidade:
            self.tempo_no_estado[self.clientes_no_sistema] += delta_t
        self.ultimo_tempo_evento = tempo_atual


class SimuladorRede:
    """Simulador de rede de filas com topologia genérica."""
    
    def __init__(self):
        self.gerador = GeradorAleatorio()
        self.filas: Dict[str, Fila] = {}
        self.roteamento: Dict[str, Dict[str, float]] = {}  # {origem: {destino: prob}}
        self.eventos: List[Tuple[float, str, dict]] = []  # Heap de (tempo, tipo, dados)
        self.tempo_atual = 0.0
        self.tempo_final = 0.0
    
    def adicionar_fila(self, nome: str, servidores: int, capacidade: int,
                      tempo_chegada_min: float, tempo_chegada_max: float,
                      tempo_atendimento_min: float, tempo_atendimento_max: float):
        """Adiciona uma fila à rede."""
        self.filas[nome] = Fila(nome, servidores, capacidade,
                               tempo_chegada_min, tempo_chegada_max,
                               tempo_atendimento_min, tempo_atendimento_max)
        self.roteamento[nome] = {}
    
    def adicionar_rota(self, origem: str, destino: str, probabilidade: float):
        """Define rota probabilística entre filas."""
        if origem in self.roteamento:
            self.roteamento[origem][destino] = probabilidade
    
    def gerar_tempo_entre_chegadas(self, fila: Fila) -> float:
        """Gera tempo até próxima chegada."""
        u = self.gerador.proximo()
        return fila.tempo_chegada_min + (fila.tempo_chegada_max - fila.tempo_chegada_min) * u
    
    def gerar_tempo_atendimento(self, fila: Fila) -> float:
        """Gera tempo de atendimento."""
        u = self.gerador.proximo()
        return fila.tempo_atendimento_min + (fila.tempo_atendimento_max - fila.tempo_atendimento_min) * u
    
    def obter_proxima_fila(self, fila_atual: str) -> Optional[str]:
        """Determina próxima fila usando roteamento probabilístico."""
        rotas = self.roteamento.get(fila_atual, {})
        if not rotas:
            return None
        
        u = self.gerador.proximo()
        acumulado = 0.0
        
        for destino, prob in rotas.items():
            acumulado += prob
            if u <= acumulado:
                return destino
        
        return list(rotas.keys())[-1] if rotas else None
    
    def agendar_evento(self, tempo: float, tipo: str, dados: dict):
        """Agenda um evento na fila de prioridade."""
        heapq.heappush(self.eventos, (tempo, tipo, dados))
    
    def processar_chegada_externa(self, tempo: float, nome_fila: str):
        """Processa chegada de cliente da entrada externa."""
        fila = self.filas[nome_fila]
        fila.atualizar_estatisticas(tempo)
        self.tempo_atual = tempo
        
        # Tenta aceitar cliente
        if fila.aceitar_cliente():
            # Se há servidores livres, agenda saída
            if fila.clientes_no_sistema <= fila.num_servidores:
                tempo_atendimento = self.gerar_tempo_atendimento(fila)
                self.agendar_evento(tempo + tempo_atendimento, "SAIDA",
                                  {"fila": nome_fila})
        
        # Agenda próxima chegada externa
        tempo_proxima_chegada = self.gerar_tempo_entre_chegadas(fila)
        self.agendar_evento(tempo + tempo_proxima_chegada, "CHEGADA_EXTERNA",
                          {"fila": nome_fila})
    
    def processar_saida(self, tempo: float, nome_fila: str):
        """Processa saída de cliente de uma fila."""
        fila = self.filas[nome_fila]
        fila.atualizar_estatisticas(tempo)
        self.tempo_atual = tempo
        
        fila.remover_cliente()
        
        # Se há clientes esperando, agenda próxima saída
        if fila.clientes_no_sistema > 0:
            tempo_atendimento = self.gerar_tempo_atendimento(fila)
            self.agendar_evento(tempo + tempo_atendimento, "SAIDA",
                              {"fila": nome_fila})
        
        # Roteia cliente para próxima fila
        proxima_fila = self.obter_proxima_fila(nome_fila)
        if proxima_fila and proxima_fila in self.filas:
            self.agendar_evento(tempo, "CHEGADA_INTERNA",
                              {"fila": proxima_fila})
    
    def processar_chegada_interna(self, tempo: float, nome_fila: str):
        """Processa chegada de cliente de outra fila."""
        fila = self.filas[nome_fila]
        fila.atualizar_estatisticas(tempo)
        
        # Tenta aceitar cliente
        if fila.aceitar_cliente():
            # Se há servidores livres, agenda saída
            if fila.clientes_no_sistema <= fila.num_servidores:
                tempo_atendimento = self.gerar_tempo_atendimento(fila)
                self.agendar_evento(tempo + tempo_atendimento, "SAIDA",
                                  {"fila": nome_fila})
    
    def executar(self, tempo_simulacao: float = 10000.0,
                 max_aleatorios: Optional[int] = None,
                 tempo_primeira_chegada: float = 2.0):
        """Executa a simulação.

        Args:
            tempo_simulacao: tempo limite de simulação (min)
            max_aleatorios: limita consumo de aleatórios (None = sem limite)
            tempo_primeira_chegada: instante da primeira chegada externa
        """
        self.tempo_final = tempo_simulacao
        self.gerador.definir_limite(max_aleatorios)
        self.eventos = []
        self.tempo_atual = 0.0
        
        # Agenda primeira chegada em cada fila com entrada externa
        for nome, fila in self.filas.items():
            if fila.tempo_chegada_min >=0:  # Tem entrada externa
                self.agendar_evento(tempo_primeira_chegada, "CHEGADA_EXTERNA", {"fila": nome})
        
        # Processa eventos
        while self.eventos and self.tempo_atual < self.tempo_final:
            tempo, tipo, dados = heapq.heappop(self.eventos)

            if tempo > self.tempo_final:
                self.tempo_atual = self.tempo_final
                break

            try:
                if tipo == "CHEGADA_EXTERNA":
                    self.processar_chegada_externa(tempo, dados["fila"])
                elif tipo == "CHEGADA_INTERNA":
                    self.processar_chegada_interna(tempo, dados["fila"])
                elif tipo == "SAIDA":
                    self.processar_saida(tempo, dados["fila"])
            except LimiteAleatoriosAtingido:
                break

        # Sincroniza estatísticas de todas as filas no tempo global final.
        for fila in self.filas.values():
            fila.atualizar_estatisticas(self.tempo_atual)
    
    def imprimir_relatorio(self, titulo: str = "Relatório de Simulação"):
        """Gera relatório da simulação."""
        linha = "=" * 70
        print(f"\n{linha}")
        print(f"  {titulo}")
        print(linha)
        print(f"  Tempo Final: {self.tempo_atual:.4f} minutos")
        print(f"  Números Aleatórios Consumidos: {self.gerador.aleatorios_consumidos}")
        print(linha)
        
        for nome in sorted(self.filas.keys()):
            fila = self.filas[nome]
            print(f"\n  FILA: {nome}")
            print(f"  Servidores: {fila.num_servidores}, Capacidade: {fila.capacidade}")
            print(f"  {'-' * 70}")
            print(f"    Clientes Processados: {fila.total_clientes_processados}")
            print(f"    Clientes Perdidos: {fila.total_clientes_perdidos}")
            
            print(f"\n    {'Estado':<10} {'Tempo (min)':>14} {'Probabilidade':>14}")
            print(f"    {'-' * 10} {'-' * 14} {'-' * 14}")
            
            for i in range(fila.capacidade + 1):
                tempo_estado = fila.tempo_no_estado[i]
                prob = (tempo_estado / self.tempo_atual * 100) if self.tempo_atual > 0 else 0
                print(f"    {i:<10} {tempo_estado:>14.4f} {prob:>13.2f}%")
        
        print(f"\n{linha}\n")


# ==========================================
# EXEMPLOS DE USO E CENÁRIOS
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  SIMULADOR DE REDE DE FILAS - VERSÃO 2.0 REFATORIZADA")
    print("  Arquitetura preparada para topologia genérica")
    print("=" * 70)
    
    # Cenário 1: Duas filas em tandem simples
    print("\n[CENÁRIO 1] Duas filas em tandem: G/G/1 -> G/G/1")
    rede1 = SimuladorRede()
    rede1.adicionar_fila("Fila1", servidores=1, capacidade=5, 
                        tempo_chegada_min=2.0, tempo_chegada_max=5.0,
                        tempo_atendimento_min=3.0, tempo_atendimento_max=5.0)
    rede1.adicionar_fila("Fila2", servidores=1, capacidade=5,
                        tempo_chegada_min=-1, tempo_chegada_max=-1,  # Sem entrada externa
                        tempo_atendimento_min=2.0, tempo_atendimento_max=4.0)
    rede1.adicionar_rota("Fila1", "Fila2", 1.0)
    
    rede1.executar(tempo_simulacao=1000.0)
    rede1.imprimir_relatorio("TANDEM: G/G/1/5 -> G/G/1/5")
    
    # Cenário 2: Fila2 com múltiplos servidores
    print("\n[CENÁRIO 2] Fila 2 com 2 servidores")
    rede2 = SimuladorRede()
    rede2.adicionar_fila("Fila1", servidores=1, capacidade=5,
                        tempo_chegada_min=2.0, tempo_chegada_max=5.0,
                        tempo_atendimento_min=3.0, tempo_atendimento_max=5.0)
    rede2.adicionar_fila("Fila2", servidores=2, capacidade=8,
                        tempo_chegada_min=-1, tempo_chegada_max=-1,
                        tempo_atendimento_min=1.0, tempo_atendimento_max=3.0)
    rede2.adicionar_rota("Fila1", "Fila2", 1.0)
    
    rede2.executar(tempo_simulacao=1000.0)
    rede2.imprimir_relatorio("TANDEM: G/G/1/5 -> G/G/2/8")
    
    # Cenário 3: Com três filas
    print("\n[CENÁRIO 3] Três filas com roteamento")
    rede3 = SimuladorRede()
    rede3.adicionar_fila("Fila1", servidores=1, capacidade=5,
                        tempo_chegada_min=2.0, tempo_chegada_max=5.0,
                        tempo_atendimento_min=3.0, tempo_atendimento_max=5.0)
    rede3.adicionar_fila("Fila2", servidores=1, capacidade=6,
                        tempo_chegada_min=-1, tempo_chegada_max=-1,
                        tempo_atendimento_min=2.0, tempo_atendimento_max=4.0)
    rede3.adicionar_fila("Fila3", servidores=1, capacidade=6,
                        tempo_chegada_min=-1, tempo_chegada_max=-1,
                        tempo_atendimento_min=1.5, tempo_atendimento_max=3.5)
    
    # Roteamento: 60% para Fila2, 40% para Fila3
    rede3.adicionar_rota("Fila1", "Fila2", 0.6)
    rede3.adicionar_rota("Fila1", "Fila3", 0.4)
    
    rede3.executar(tempo_simulacao=1000.0)
    rede3.imprimir_relatorio("REDE: Fila1 -> 60% Fila2, 40% Fila3")
    
    # DOCUMENTAÇÃO
    print("\n" + "=" * 70)
    print("  COMO USAR O SIMULADOR")
    print("=" * 70)
    print("""
  1. Criar uma rede:
     rede = SimuladorRede()
  
  2. Adicionar filas:
     rede.adicionar_fila(nome, servidores, capacidade,
                        tempo_chegada_min, tempo_chegada_max,
                        tempo_atendimento_min, tempo_atendimento_max)
     
     Para filas sem entrada externa (intermediárias):
     - Usar tempo_chegada_min = -1 e tempo_chegada_max = -1
  
  3. Definir roteamento:
     rede.adicionar_rota(fila_origem, fila_destino, probabilidade)
     
     Exemplo: roteamento probabilístico
     rede.adicionar_rota("Fila1", "Fila2", 0.7)  # 70%
     rede.adicionar_rota("Fila1", "Fila3", 0.3)  # 30%
  
  4. Executar simulação:
     rede.executar(tempo_simulacao=1000.0)
  
  5. Gerar relatório:
     rede.imprimir_relatorio("Título da Simulação")
    """)
    print("=" * 70)
