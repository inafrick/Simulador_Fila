class SimuladorFila:
    def __init__(self, servidores, capacidade, ch_min, ch_max, sa_min, sa_max):
        # Parâmetros da Fila
        self.servidores = servidores
        self.capacidade = capacidade
        self.ch_min = ch_min
        self.ch_max = ch_max
        self.sa_min = sa_min
        self.sa_max = sa_max
        
        # Variáveis de Estado
        self.status = 0
        self.tempo_global = 0.0
        self.tempos_acumulados = [0.0] * (capacidade + 1)
        self.perdas = 0
        
        # Escalonador de eventos: lista de tuplas (tempo, "CHEGADA" ou "SAIDA")
        self.escalonador = []
        
        # Parâmetros do Gerador de Números Pseudoaleatórios (LCG - glibc GCC)
        self.semente = 12345
        self.a = 1103515245
        self.c = 12345
        self.m = 2**31
        
        self.aleatorios_consumidos = 0
        self.limite_aleatorios = 100000
        self.simulacao_ativa = True

    def next_random(self):
        """Gera o próximo número pseudoaleatório entre 0 e 1."""
        if self.aleatorios_consumidos >= self.limite_aleatorios:
            self.simulacao_ativa = False
            return 0.0
            
        self.semente = (self.a * self.semente + self.c) % self.m
        self.aleatorios_consumidos += 1
        return self.semente / self.m

    def gerar_tempo(self, a, b):
        """Aplica a fórmula U(a, b) = a + [(b - a) * U(0,1)]"""
        u = self.next_random()
        if not self.simulacao_ativa:
            return 0.0
        return a + ((b - a) * u)

    def agendar_evento(self, tempo, tipo):
        self.escalonador.append((tempo, tipo))
        # Ordena para garantir que o evento com menor tempo seja o primeiro
        self.escalonador.sort(key=lambda x: x[0])

    def chegada(self, tempo_evento):
        # Atualiza acumulador de tempo
        delta_t = tempo_evento - self.tempo_global
        self.tempos_acumulados[self.status] += delta_t
        self.tempo_global = tempo_evento

        if self.status < self.capacidade:
            self.status += 1
            if self.status <= self.servidores:
                # Se há servidor livre, agenda a saída deste cliente
                tempo_saida = self.gerar_tempo(self.sa_min, self.sa_max)
                if self.simulacao_ativa:
                    self.agendar_evento(self.tempo_global + tempo_saida, "SAIDA")
        else:
            self.perdas += 1

        # Sempre agenda a próxima chegada
        tempo_chegada = self.gerar_tempo(self.ch_min, self.ch_max)
        if self.simulacao_ativa:
            self.agendar_evento(self.tempo_global + tempo_chegada, "CHEGADA")

    def saida(self, tempo_evento):
        # Atualiza acumulador de tempo
        delta_t = tempo_evento - self.tempo_global
        self.tempos_acumulados[self.status] += delta_t
        self.tempo_global = tempo_evento

        self.status -= 1

        # Se ainda há clientes na fila aguardando servidor, inicia novo atendimento
        if self.status >= self.servidores:
            tempo_saida = self.gerar_tempo(self.sa_min, self.sa_max)
            if self.simulacao_ativa:
                self.agendar_evento(self.tempo_global + tempo_saida, "SAIDA")

    def executar(self):
        # Condição inicial: Fila vazia, primeira chegada no tempo 2.0
        self.agendar_evento(2.0, "CHEGADA")

        # Laço principal do simulador
        while self.simulacao_ativa and len(self.escalonador) > 0:
            evento = self.escalonador.pop(0)
            tempo_evento = evento[0]
            tipo_evento = evento[1]

            if tipo_evento == "CHEGADA":
                self.chegada(tempo_evento)
            elif tipo_evento == "SAIDA":
                self.saida(tempo_evento)

    def imprimir_relatorio(self, nome_cenario):
        linha = "=" * 60
        print(f"\n{linha}")
        print(f"  RESULTADOS: {nome_cenario}")
        print(linha)
        print(f"  Tempo Global da Simulação: {self.tempo_global:.4f} minutos")
        print(f"  Números Aleatórios Consumidos: {self.aleatorios_consumidos}")
        print(f"  Clientes Perdidos: {self.perdas}")
        print(f"\n  {'Estado':<10} {'Tempo (min)':>14} {'Probabilidade':>14}")
        print(f"  {'-'*10} {'-'*14} {'-'*14}")

        for i in range(self.capacidade + 1):
            tempo_estado = self.tempos_acumulados[i]
            probabilidade = (tempo_estado / self.tempo_global) * 100 if self.tempo_global > 0 else 0
            print(f"  {i:<10} {tempo_estado:>14.4f} {probabilidade:>13.2f}%")

        print(linha)

# ==========================================
# EXECUÇÃO DOS CENÁRIOS
# ==========================================
if __name__ == "__main__":
    # Cenário 1: G/G/1/5
    sim_1 = SimuladorFila(servidores=1, capacidade=5, ch_min=2.0, ch_max=5.0, sa_min=3.0, sa_max=5.0)
    sim_1.executar()
    sim_1.imprimir_relatorio("G/G/1/5 , chegadas entre 2...5 , atendimento entre 3...5")

    # Cenário 2: G/G/2/5
    sim_2 = SimuladorFila(servidores=2, capacidade=5, ch_min=2.0, ch_max=5.0, sa_min=3.0, sa_max=5.0)
    sim_2.executar()
    sim_2.imprimir_relatorio("G/G/2/5 , chegadas entre 2...5 , atendimento entre 3...5")