"""
Exemplos Avançados de Uso do Simulador de Rede de Filas
Demonstra diferentes configurações e topologias
"""

from simulador import SimuladorRede


def exemplo_basico_tandem():
    """Exemplo básico: duas filas em tandem."""
    print("\n" + "="*70)
    print("EXEMPLO 1: Duas Filas em Tandem Básico")
    print("="*70)
    
    rede = SimuladorRede()
    
    # Fila de entrada
    rede.adicionar_fila("Entrada", servidores=1, capacidade=5,
                       tempo_chegada_min=2.0, tempo_chegada_max=5.0,
                       tempo_atendimento_min=1.0, tempo_atendimento_max=2.0)
    
    # Fila de processamento
    rede.adicionar_fila("Processamento", servidores=1, capacidade=5,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    
    # Roteamento
    rede.adicionar_rota("Entrada", "Processamento", 1.0)
    
    rede.executar(tempo_simulacao=500.0)
    rede.imprimir_relatorio("Tandem: Entrada -> Processamento")


def exemplo_multiple_servidores():
    """Exemplo com múltiplos servidores em paralelo."""
    print("\n" + "="*70)
    print("EXEMPLO 2: Filas com Múltiplos Servidores")
    print("="*70)
    
    rede = SimuladorRede()
    
    # Fila de entrada
    rede.adicionar_fila("Recepção", servidores=2, capacidade=10,
                       tempo_chegada_min=1.5, tempo_chegada_max=3.0,
                       tempo_atendimento_min=0.5, tempo_atendimento_max=1.5)
    
    # Fila de processamento com 3 servidores
    rede.adicionar_fila("Centro_Processamento", servidores=3, capacidade=15,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=1.0, tempo_atendimento_max=2.5)
    
    rede.adicionar_rota("Recepção", "Centro_Processamento", 1.0)
    
    rede.executar(tempo_simulacao=500.0)
    rede.imprimir_relatorio("Múltiplos Servidores: 2 -> 3 servidores")


def exemplo_roteamento_probabilistico():
    """Exemplo com roteamento probabilístico para múltiplas filas."""
    print("\n" + "="*70)
    print("EXEMPLO 3: Roteamento Probabilístico")
    print("="*70)
    
    rede = SimuladorRede()
    
    # Fila inicial
    rede.adicionar_fila("Entrada", servidores=1, capacidade=10,
                       tempo_chegada_min=2.0, tempo_chegada_max=4.0,
                       tempo_atendimento_min=1.0, tempo_atendimento_max=2.0)
    
    # Duas filas paralelas
    rede.adicionar_fila("Rota_A", servidores=1, capacidade=8,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=1.5, tempo_atendimento_max=3.0)
    
    rede.adicionar_fila("Rota_B", servidores=1, capacidade=8,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=1.0, tempo_atendimento_max=2.0)
    
    # Roteamento: 70% para Rota_A, 30% para Rota_B
    rede.adicionar_rota("Entrada", "Rota_A", 0.7)
    rede.adicionar_rota("Entrada", "Rota_B", 0.3)
    
    rede.executar(tempo_simulacao=500.0)
    rede.imprimir_relatorio("Roteamento: 70% Rota_A, 30% Rota_B")


def exemplo_rede_complexa():
    """Exemplo com rede mais complexa (3 estágios)."""
    print("\n" + "="*70)
    print("EXEMPLO 4: Rede Complexa (3 Estágios)")
    print("="*70)
    
    rede = SimuladorRede()
    
    # Estágio 1: Entrada
    rede.adicionar_fila("Estag1_Entrada", servidores=1, capacidade=8,
                       tempo_chegada_min=2.0, tempo_chegada_max=4.0,
                       tempo_atendimento_min=1.0, tempo_atendimento_max=1.5)
    
    # Estágio 2: Processamento duplo
    rede.adicionar_fila("Estag2_Caminho1", servidores=1, capacidade=6,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=1.5, tempo_atendimento_max=2.5)
    
    rede.adicionar_fila("Estag2_Caminho2", servidores=1, capacidade=6,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    
    # Estágio 3: Consolidação
    rede.adicionar_fila("Estag3_Saida", servidores=2, capacidade=10,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=0.5, tempo_atendimento_max=1.0)
    
    # Roteamento
    rede.adicionar_rota("Estag1_Entrada", "Estag2_Caminho1", 0.6)
    rede.adicionar_rota("Estag1_Entrada", "Estag2_Caminho2", 0.4)
    rede.adicionar_rota("Estag2_Caminho1", "Estag3_Saida", 1.0)
    rede.adicionar_rota("Estag2_Caminho2", "Estag3_Saida", 1.0)
    
    rede.executar(tempo_simulacao=500.0)
    rede.imprimir_relatorio("Rede 3 Estágios: Entrada -> Caminho Duplo -> Saída")


def exemplo_testes_carga():
    """Exemplo: teste de carga com diferentes velocidades de chegada."""
    print("\n" + "="*70)
    print("EXEMPLO 5: Teste de Carga - Comparação")
    print("="*70)
    
    # Carga Baixa
    print("\n[Teste 1] Carga Baixa")
    rede_baixa = SimuladorRede()
    rede_baixa.adicionar_fila("Fila", servidores=1, capacidade=5,
                             tempo_chegada_min=5.0, tempo_chegada_max=8.0,
                             tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    rede_baixa.executar(tempo_simulacao=500.0)
    rede_baixa.imprimir_relatorio("Carga Baixa: Chegadas de 5-8 min")
    
    # Carga Média
    print("\n[Teste 2] Carga Média")
    rede_media = SimuladorRede()
    rede_media.adicionar_fila("Fila", servidores=1, capacidade=5,
                             tempo_chegada_min=2.0, tempo_chegada_max=4.0,
                             tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    rede_media.executar(tempo_simulacao=500.0)
    rede_media.imprimir_relatorio("Carga Média: Chegadas de 2-4 min")
    
    # Carga Alta
    print("\n[Teste 3] Carga Alta")
    rede_alta = SimuladorRede()
    rede_alta.adicionar_fila("Fila", servidores=1, capacidade=5,
                            tempo_chegada_min=1.0, tempo_chegada_max=2.0,
                            tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    rede_alta.executar(tempo_simulacao=500.0)
    rede_alta.imprimir_relatorio("Carga Alta: Chegadas de 1-2 min")


def exemplo_impacto_capacidade():
    """Exemplo: teste do impacto de diferentes capacidades."""
    print("\n" + "="*70)
    print("EXEMPLO 6: Impacto da Capacidade")
    print("="*70)
    
    capacidades = [3, 5, 10, 20]
    
    for cap in capacidades:
        print(f"\n[Teste com Capacidade {cap}]")
        rede = SimuladorRede()
        rede.adicionar_fila("Fila", servidores=1, capacidade=cap,
                           tempo_chegada_min=2.0, tempo_chegada_max=4.0,
                           tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
        rede.executar(tempo_simulacao=300.0)
        
        fila = rede.filas["Fila"]
        taxa_perda = (fila.total_clientes_perdidos / 
                     (fila.total_clientes_processados + fila.total_clientes_perdidos) * 100) \
                     if (fila.total_clientes_processados + fila.total_clientes_perdidos) > 0 else 0
        
        print(f"  Processados: {fila.total_clientes_processados}")
        print(f"  Perdidos: {fila.total_clientes_perdidos}")
        print(f"  Taxa de Perda: {taxa_perda:.2f}%")


def exemplo_impacto_servidores():
    """Exemplo: teste do impacto de número de servidores."""
    print("\n" + "="*70)
    print("EXEMPLO 7: Impacto do Número de Servidores")
    print("="*70)
    
    num_servidores = [1, 2, 3, 4]
    
    for servers in num_servidores:
        print(f"\n[Teste com {servers} Servidor(es)]")
        rede = SimuladorRede()
        rede.adicionar_fila("Fila", servidores=servers, capacidade=10,
                           tempo_chegada_min=2.0, tempo_chegada_max=4.0,
                           tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
        rede.executar(tempo_simulacao=300.0)
        
        fila = rede.filas["Fila"]
        print(f"  Processados: {fila.total_clientes_processados}")
        print(f"  Perdidos: {fila.total_clientes_perdidos}")
        print(f"  % Tempo Ocioso: {fila.tempo_no_estado[0] / rede.tempo_atual * 100:.2f}%")


def exemplo_validacao_tandem_100k_aleatorios():
    """Validação solicitada: tandem G/G/2/3 -> G/G/1/5 com 100.000 aleatórios."""
    print("\n" + "="*70)
    print("EXEMPLO 8: Validação Tandem com 100.000 Aleatórios")
    print("="*70)

    rede = SimuladorRede()

    # Fila 1: G/G/2/3 com chegada externa entre 1 e 4.
    rede.adicionar_fila("Fila1", servidores=2, capacidade=3,
                       tempo_chegada_min=1.0, tempo_chegada_max=4.0,
                       tempo_atendimento_min=3.0, tempo_atendimento_max=4.0)

    # Fila 2: G/G/1/5 sem chegada externa (apenas fluxo interno da Fila1).
    rede.adicionar_fila("Fila2", servidores=1, capacidade=5,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)

    # Tandem: 100% dos clientes que saem da Fila1 seguem para a Fila2.
    rede.adicionar_rota("Fila1", "Fila2", 1.0)

    rede.executar(
        tempo_simulacao=10**9,
        max_aleatorios=100000,
        tempo_primeira_chegada=1.5,
    )
    rede.imprimir_relatorio(
        "VALIDACAO: Fila1 G/G/2/3 -> Fila2 G/G/1/5 (100.000 aleatorios)"
    )


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  EXEMPLOS AVANÇADOS - SIMULADOR DE REDE DE FILAS")
    print("="*70)
    
    exemplo_basico_tandem()
    exemplo_multiple_servidores()
    exemplo_roteamento_probabilistico()
    exemplo_rede_complexa()
    exemplo_testes_carga()
    exemplo_impacto_capacidade()
    exemplo_impacto_servidores()
    exemplo_validacao_tandem_100k_aleatorios()
    
    print("\n" + "="*70)
    print("  FIM DOS EXEMPLOS")
    print("="*70)
