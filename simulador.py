"""
Simulador de Rede de Filas — Métodos Analíticos
================================================
Suporta topologia genérica de rede de filas com roteamento probabilístico.

Uso:
  python simulador.py                     # Executa cenários programados
  python simulador.py config_tandem.yml   # Carrega rede a partir de arquivo YAML

Formato do arquivo YAML:
  aleatorios: 100000
  semente: 12345
  primeira_chegada:
    fila: Fila1
    tempo: 1.5
  filas:
    Fila1:
      servidores: 2
      capacidade: 3
      chegada: [1, 4]
      atendimento: [3, 4]
    Fila2:
      servidores: 1
      capacidade: 5
      atendimento: [2, 3]
  roteamento:
    Fila1:
      Fila2: 1.0
"""

import heapq
import sys


class Fila:
    """Representa uma fila individual dentro da rede."""

    def __init__(self, nome, servidores, capacidade, sa_min, sa_max,
                 ch_min=None, ch_max=None):
        self.nome = nome
        self.servidores = servidores
        self.capacidade = capacidade
        self.sa_min = sa_min
        self.sa_max = sa_max
        self.ch_min = ch_min   # None → sem chegadas externas
        self.ch_max = ch_max

        # Estado
        self.status = 0
        self.tempos_acumulados = [0.0] * (capacidade + 1)
        self.perdas = 0


class SimuladorRede:
    """Simulador de rede de filas com topologia e roteamento configuráveis."""

    def __init__(self, semente=12345, limite_aleatorios=100000):
        self.filas = {}
        self.roteamento = {}
        self.escalonador = []
        self._seq = 0
        self.tempo_global = 0.0

        # LCG (glibc / GCC)
        self.semente = semente
        self.a = 1103515245
        self.c = 12345
        self.m = 2 ** 31
        self.aleatorios_consumidos = 0
        self.limite_aleatorios = limite_aleatorios
        self.simulacao_ativa = True

    # ── Configuração ─────────────────────────────────────────

    def adicionar_fila(self, nome, servidores, capacidade, sa_min, sa_max,
                       ch_min=None, ch_max=None):
        """Adiciona uma fila à rede."""
        self.filas[nome] = Fila(nome, servidores, capacidade,
                                sa_min, sa_max, ch_min, ch_max)

    def definir_roteamento(self, origem, destinos):
        """
        Define o roteamento de saída de uma fila.
        destinos: lista de tuplas (fila_destino, probabilidade).
        Ex.: [("F2", 1.0)]          → 100% para F2
             [("F2", 0.8), ("F3", 0.2)] → 80% F2, 20% F3
        Se soma das probabilidades < 1.0, o restante sai do sistema.
        """
        self.roteamento[origem] = destinos

    # ── Gerador de Números Pseudoaleatórios ──────────────────

    def next_random(self):
        if self.aleatorios_consumidos >= self.limite_aleatorios:
            self.simulacao_ativa = False
            return 0.0
        self.semente = (self.a * self.semente + self.c) % self.m
        self.aleatorios_consumidos += 1
        return self.semente / self.m

    def gerar_tempo(self, a, b):
        """U(a, b) = a + (b − a) × U(0,1)"""
        u = self.next_random()
        if not self.simulacao_ativa:
            return 0.0
        return a + ((b - a) * u)

    # ── Escalonador de Eventos ───────────────────────────────

    def agendar_evento(self, tempo, tipo, fila_nome):
        heapq.heappush(self.escalonador,
                       (tempo, self._seq, tipo, fila_nome))
        self._seq += 1

    # ── Atualização de Tempos ────────────────────────────────

    def _atualizar_tempos(self, tempo_evento):
        """Acumula tempo de TODAS as filas no estado atual."""
        delta = tempo_evento - self.tempo_global
        if delta > 0:
            for fila in self.filas.values():
                fila.tempos_acumulados[fila.status] += delta
            self.tempo_global = tempo_evento

    # ── Eventos ──────────────────────────────────────────────

    def chegada(self, fila_nome, tempo_evento):
        """Chegada externa de um cliente na fila."""
        fila = self.filas[fila_nome]
        self._atualizar_tempos(tempo_evento)

        if fila.status < fila.capacidade:
            fila.status += 1
            if fila.status <= fila.servidores:
                ts = self.gerar_tempo(fila.sa_min, fila.sa_max)
                if self.simulacao_ativa:
                    self.agendar_evento(self.tempo_global + ts,
                                       "SAIDA", fila_nome)
        else:
            fila.perdas += 1

        # Próxima chegada externa (somente se a fila recebe do exterior)
        if fila.ch_min is not None:
            tc = self.gerar_tempo(fila.ch_min, fila.ch_max)
            if self.simulacao_ativa:
                self.agendar_evento(self.tempo_global + tc,
                                   "CHEGADA", fila_nome)

    def saida(self, fila_nome, tempo_evento):
        """Fim de atendimento — cliente sai da fila."""
        fila = self.filas[fila_nome]
        self._atualizar_tempos(tempo_evento)

        fila.status -= 1

        if fila.status >= fila.servidores:
            ts = self.gerar_tempo(fila.sa_min, fila.sa_max)
            if self.simulacao_ativa:
                self.agendar_evento(self.tempo_global + ts,
                                   "SAIDA", fila_nome)

        self._rotear_cliente(fila_nome)

    def _chegada_interna(self, fila_nome):
        """Chegada de cliente vindo de outra fila (mesmo instante)."""
        fila = self.filas[fila_nome]
        if fila.status < fila.capacidade:
            fila.status += 1
            if fila.status <= fila.servidores:
                ts = self.gerar_tempo(fila.sa_min, fila.sa_max)
                if self.simulacao_ativa:
                    self.agendar_evento(self.tempo_global + ts,
                                       "SAIDA", fila_nome)
        else:
            fila.perdas += 1

    def _rotear_cliente(self, fila_origem):
        """Encaminha o cliente conforme tabela de roteamento."""
        if fila_origem not in self.roteamento:
            return  # cliente sai do sistema

        destinos = self.roteamento[fila_origem]
        if not destinos:
            return

        # Determinístico (destino único com probabilidade = 1.0)
        if len(destinos) == 1 and destinos[0][1] >= 1.0:
            self._chegada_interna(destinos[0][0])
            return

        # Probabilístico — consome um número aleatório
        r = self.next_random()
        if not self.simulacao_ativa:
            return
        acum = 0.0
        for destino, prob in destinos:
            acum += prob
            if r < acum:
                self._chegada_interna(destino)
                return
        # r >= acum → cliente sai do sistema

    # ── Execução ─────────────────────────────────────────────

    def executar(self, chegadas_iniciais):
        """
        chegadas_iniciais: lista de tuplas (tempo, fila_nome).
        Ex.: [(1.5, "Fila1")]
        """
        for tempo, fila_nome in chegadas_iniciais:
            self.agendar_evento(tempo, "CHEGADA", fila_nome)

        while self.simulacao_ativa and self.escalonador:
            tempo_ev, _, tipo_ev, fila_nome = heapq.heappop(self.escalonador)
            if tipo_ev == "CHEGADA":
                self.chegada(fila_nome, tempo_ev)
            elif tipo_ev == "SAIDA":
                self.saida(fila_nome, tempo_ev)

    # ── Relatório ────────────────────────────────────────────

    def imprimir_relatorio(self, titulo=None):
        linha = "=" * 65
        print(f"\n{linha}")
        print(f"  {titulo or 'RESULTADOS DA SIMULAÇÃO'}")
        print(linha)
        print(f"  Tempo Global: {self.tempo_global:.4f}")
        print(f"  Aleatórios Consumidos: {self.aleatorios_consumidos}")

        for fila in self.filas.values():
            ch_info = (f"chegadas [{fila.ch_min}..{fila.ch_max}]"
                       if fila.ch_min is not None else "sem chegada externa")
            print(f"\n  --- {fila.nome}: G/G/{fila.servidores}/{fila.capacidade}"
                  f" | {ch_info}"
                  f" | atend [{fila.sa_min}..{fila.sa_max}] ---")
            print(f"  Perdas: {fila.perdas}")
            print(f"\n  {'Estado':<10} {'Tempo':>14} {'Probabilidade':>14}")
            print(f"  {'-'*10} {'-'*14} {'-'*14}")
            for i in range(fila.capacidade + 1):
                t = fila.tempos_acumulados[i]
                p = (t / self.tempo_global * 100) if self.tempo_global > 0 else 0
                print(f"  {i:<10} {t:>14.4f} {p:>13.2f}%")

        print(f"\n{linha}")

    # ── Carregamento YAML ────────────────────────────────────

    @classmethod
    def carregar_yaml(cls, arquivo):
        """Carrega configuração da rede a partir de arquivo YAML."""
        try:
            import yaml
        except ImportError:
            print("Erro: módulo 'pyyaml' necessário. Instale com:  pip install pyyaml")
            sys.exit(1)

        with open(arquivo, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        sim = cls(semente=cfg.get("semente", 12345),
                  limite_aleatorios=cfg.get("aleatorios", 100000))

        for nome, p in cfg["filas"].items():
            ch = p.get("chegada")
            sim.adicionar_fila(
                nome=nome,
                servidores=p["servidores"],
                capacidade=p["capacidade"],
                sa_min=p["atendimento"][0],
                sa_max=p["atendimento"][1],
                ch_min=ch[0] if ch else None,
                ch_max=ch[1] if ch else None,
            )

        for orig, dests in cfg.get("roteamento", {}).items():
            sim.definir_roteamento(
                orig, [(d, pr) for d, pr in dests.items()])

        pc = cfg["primeira_chegada"]
        return sim, [(pc["tempo"], pc["fila"])]


# ==========================================
# EXECUÇÃO DOS CENÁRIOS
# ==========================================

if __name__ == "__main__":

    # ── Modo arquivo YAML ──
    if len(sys.argv) > 1 and sys.argv[1].endswith((".yml", ".yaml")):
        sim, chegadas = SimuladorRede.carregar_yaml(sys.argv[1])
        sim.executar(chegadas)
        sim.imprimir_relatorio()
        sys.exit(0)

    # ── Cenário 1: Fila única G/G/1/5 ──
    sim1 = SimuladorRede()
    sim1.adicionar_fila("F1", servidores=1, capacidade=5,
                        ch_min=2.0, ch_max=5.0, sa_min=3.0, sa_max=5.0)
    sim1.executar([(2.0, "F1")])
    sim1.imprimir_relatorio("G/G/1/5 — chegadas [2..5], atendimento [3..5]")

    # ── Cenário 2: Fila única G/G/2/5 ──
    sim2 = SimuladorRede()
    sim2.adicionar_fila("F1", servidores=2, capacidade=5,
                        ch_min=2.0, ch_max=5.0, sa_min=3.0, sa_max=5.0)
    sim2.executar([(2.0, "F1")])
    sim2.imprimir_relatorio("G/G/2/5 — chegadas [2..5], atendimento [3..5]")

    # ── Cenário 3: Rede Tandem (Validação) ──
    # Fila 1 — G/G/2/3, chegadas 1..4, atendimento 3..4
    # Fila 2 — G/G/1/5, atendimento 2..3 (sem chegada externa)
    # Roteamento: 100% Fila1 → Fila2
    # Primeiro cliente chega em t = 1.5, filas inicialmente vazias
    sim3 = SimuladorRede()
    sim3.adicionar_fila("Fila1", servidores=2, capacidade=3,
                        ch_min=1.0, ch_max=4.0, sa_min=3.0, sa_max=4.0)
    sim3.adicionar_fila("Fila2", servidores=1, capacidade=5,
                        sa_min=2.0, sa_max=3.0)
    sim3.definir_roteamento("Fila1", [("Fila2", 1.0)])
    sim3.executar([(1.5, "Fila1")])
    sim3.imprimir_relatorio("Rede Tandem: Fila1 (G/G/2/3) → Fila2 (G/G/1/5)")
