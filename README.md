# Simulador de Rede de Filas (T1)

Simulador de eventos discretos para rede de filas com topologia genérica.

## Como executar

```bash
python simulador.py config_rede.yml
```

## Arquivos principais

- `simulador.py`: código do simulador.
- `config_rede.yml`: configuração da rede usada na validação do T1.

## O que o simulador reporta

- tempo global da simulação
- números aleatórios consumidos (limite: 100000)
- perdas por fila
- tempos acumulados e probabilidade por estado de cada fila
