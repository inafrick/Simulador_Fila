# Simulador de Rede de Filas (T1)

Simulador de eventos discretos para rede de filas com topologia genérica.

## Como executar

```bash
python simulador.py config_rede.yml
```

## Arquivos principais

- `simulador.py`: motor de simulação atualizado com cálculos automáticos de métricas e relatório formatado.
- `config_rede.yml`: configuração do modelo inicial (cenário de clínica médica com gargalo crítico na F2).
- `config_rede_otimizado.yml`: configuração do modelo futuro (otimização via rebalanceamento de servidores entre F2 e F3).

## O que o simulador reporta

O simulador gera um relatório detalhado no terminal contendo:

- tempo global da simulação
- números aleatórios consumidos (limite: 100000)
- perdas por fila
- tempos acumulados e probabilidade por estado de cada fila
- índices de desempenho: cálculos automáticos de L, λ, ρ e W.
