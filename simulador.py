"""
Simulador de Rede de Filas — Métodos Analíticos
================================================
Suporta topologia genérica de rede de filas com roteamento probabilístico,
incluindo feedback (ciclos) entre filas e capacidade infinita.
"""

import heapq
import sys
from collections import defaultdict


class Fila:
    """Representa uma fila individual dentro da rede."""

    def __init__(self, nome, servidores, capacidade, sa_min, sa_max,
                 ch_min=None, ch_max=None):
        self.nome = nome
        self.servidores = servidores
        self.capacidade = capacidade  # None → capacidade infinita
        self.sa_min = sa_min
        self.sa_max = sa_max
        self.ch_min = ch_min   # None → sem chegadas externas
        self.ch_max = ch_max

        # Estado
        self.status = 0
        self.tempos_acumulados = defaultdict(float)
        self.perdas = 0
        self.max_status = 0    # maior estado observado (para relatório)


class SimuladorRede:
    """Simulador de rede de filas com topologia e roteamento configuráveis."""

    def __init__(self, semente=12345, limite_aleatorios=100000,
                 rng_a=1103515245, rng_c=12345, rng_m=2**31):
        self.filas = {}
        self.roteamento = {}
        self.escalonador = []
        self._seq = 0
        self.tempo_global = 0.0

        # Gerador Congruencial Linear (configurável)
        self.semente = semente
        self.a = rng_a
        self.c = rng_c
        self.m = rng_m
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
        """Define o roteamento de saída de uma fila."""
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

    def _tem_vaga(self, fila):
        if fila.capacidade is None:
            return True
        return fila.status < fila.capacidade

    def _registrar_status(self, fila):
        if fila.status > fila.max_status:
            fila.max_status = fila.status

    def chegada(self, fila_nome, tempo_evento):
        fila = self.filas[fila_nome]
        self._atualizar_tempos(tempo_evento)

        if self._tem_vaga(fila):
            fila.status += 1
            self._registrar_status(fila)
            if fila.status <= fila.servidores:
                ts = self.gerar_tempo(fila.sa_min, fila.sa_max)
                if self.simulacao_ativa:
                    self.agendar_evento(self.tempo_global + ts,
                                       "SAIDA", fila_nome)
        else:
            fila.perdas += 1

        if fila.ch_min is not None:
            tc = self.gerar_tempo(fila.ch_min, fila.ch_max)
            if self.simulacao_ativa:
                self.agendar_evento(self.tempo_global + tc,
                                   "CHEGADA", fila_nome)

    def saida(self, fila_nome, tempo_evento):
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
        fila = self.filas[fila_nome]
        if self._tem_vaga(fila):
            fila.status += 1
            self._registrar_status(fila)
            if fila.status <= fila.servidores:
                ts = self.gerar_tempo(fila.sa_min, fila.sa_max)
                if self.simulacao_ativa:
                    self.agendar_evento(self.tempo_global + ts,
                                       "SAIDA", fila_nome)
        else:
            fila.perdas += 1

    def _rotear_cliente(self, fila_origem):
        if fila_origem not in self.roteamento:
            return

        destinos = self.roteamento[fila_origem]
        if not destinos:
            return

        r = self.next_random()
        if not self.simulacao_ativa:
            return
        acum = 0.0
        for destino, prob in destinos:
            acum += prob
            if r < acum:
                self._chegada_interna(destino)
                return

    # ── Execução ─────────────────────────────────────────────

    def executar(self, chegadas_iniciais):
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
            cap_str = fila.capacidade if fila.capacidade is not None else "∞"
            print(f"\n  --- {fila.nome}: G/G/{fila.servidores}/{cap_str}"
                  f" | {ch_info}"
                  f" | atend [{fila.sa_min}..{fila.sa_max}] ---")
            print(f"  Perdas de clientes: {fila.perdas}")
            
            # Cabeçalho da tabela ajustado para ficar parecido com seu exemplo
            max_estado = fila.max_status if fila.capacidade is None else fila.max_status
            
            L = 0.0
            servidores_ocupados = 0.0

            for i in range(max_estado + 1):
                t = fila.tempos_acumulados[i]
                p_prob = (t / self.tempo_global) if self.tempo_global > 0 else 0
                print(f"  Estado {i}: tempo = {t:<12.4f} probabilidade = {p_prob*100:>7.4f}%")
                
                # Cálculos matemáticos dos índices
                L += i * p_prob
                servidores_ocupados += min(i, fila.servidores) * p_prob

            # Cálculo de Vazão (Lambda/X) e Tempo de Resposta (W)
            e_s = (fila.sa_min + fila.sa_max) / 2.0
            mu = 1.0 / e_s if e_s > 0 else 0
            
            utilizacao = (servidores_ocupados / fila.servidores) if fila.servidores > 0 else 0
            vazao = servidores_ocupados * mu
            tempo_resposta = L / vazao if vazao > 0 else 0

            # Imprime os cálculos
            print(f"\n  • População (L): {L:.6f}")
            print(f"  • Vazão (λ): {vazao:.6f}")
            print(f"  • Utilização (ρ): {utilizacao:.6f}")
            print(f"  • Tempo de Resposta (W): {tempo_resposta:.6f}")

        print(f"\n{linha}")

    # ── Carregamento YAML ────────────────────────────────────

    @classmethod
    def carregar_yaml(cls, arquivo):
        try:
            import yaml
        except ImportError:
            print("Erro: módulo 'pyyaml' necessário. Instale com:  pip install pyyaml")
            sys.exit(1)

        with open(arquivo, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        sim = cls(semente=cfg.get("semente", 12345),
                  limite_aleatorios=cfg.get("aleatorios", 100000),
                  rng_a=cfg.get("a", 1103515245),
                  rng_c=cfg.get("c", 12345),
                  rng_m=cfg.get("M", 2**31))

        for nome, p in cfg["filas"].items():
            ch = p.get("chegada")
            sim.adicionar_fila(
                nome=nome,
                servidores=p["servidores"],
                capacidade=p.get("capacidade"),
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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith((".yml", ".yaml")):
        sim, chegadas = SimuladorRede.carregar_yaml(sys.argv[1])
        sim.executar(chegadas)
        sim.imprimir_relatorio()
        sys.exit(0)
    else:
        print("Uso: python simulador.py arquivo.yml")