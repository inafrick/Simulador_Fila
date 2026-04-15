"""
Exemplos Avançados de Uso do Simulador de Rede de Filas
Demonstra diferentes configurações e topologias
"""

import sys

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


def exemplo_professor_itens_2_e_3():
    """Exemplo dedicado para os itens 2 e 3 da validação."""
    print("\n" + "="*70)
    print("EXEMPLO PROFESSOR: ITENS 2 E 3")
    print("="*70)
    print("2. G/G/2/3, chegadas entre 1..4, atendimento entre 3..4")
    print("3. G/G/1/5, atendimento entre 2..3 (sem chegadas externas)")

    rede = SimuladorRede()
    rede.adicionar_fila("Fila1", servidores=2, capacidade=3,
                       tempo_chegada_min=1.0, tempo_chegada_max=4.0,
                       tempo_atendimento_min=3.0, tempo_atendimento_max=4.0)
    rede.adicionar_fila("Fila2", servidores=1, capacidade=5,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    rede.adicionar_rota("Fila1", "Fila2", 1.0)

    rede.executar(
        tempo_simulacao=10**9,
        max_aleatorios=100000,
        tempo_primeira_chegada=1.5,
    )

    rede.imprimir_relatorio("RESULTADO DOS ITENS 2 E 3 (100.000 ALEATORIOS)")

    print("Resumo objetivo para entrega:")
    print(f"  Tempo global da simulacao: {rede.tempo_atual:.4f} minutos")
    print(f"  Aleatorios consumidos: {rede.gerador.aleatorios_consumidos}")
    print(f"  Perdas Fila1 (item 2): {rede.filas['Fila1'].total_clientes_perdidos}")
    print(f"  Perdas Fila2 (item 3): {rede.filas['Fila2'].total_clientes_perdidos}")


def _executar_cenario_itens_2_e_3():
    """Executa o cenario base usado nos itens 2 e 3 e retorna a rede simulada."""
    rede = SimuladorRede()
    rede.adicionar_fila("Fila1", servidores=2, capacidade=3,
                       tempo_chegada_min=1.0, tempo_chegada_max=4.0,
                       tempo_atendimento_min=3.0, tempo_atendimento_max=4.0)
    rede.adicionar_fila("Fila2", servidores=1, capacidade=5,
                       tempo_chegada_min=-1, tempo_chegada_max=-1,
                       tempo_atendimento_min=2.0, tempo_atendimento_max=3.0)
    rede.adicionar_rota("Fila1", "Fila2", 1.0)

    rede.executar(
        tempo_simulacao=10**9,
        max_aleatorios=100000,
        tempo_primeira_chegada=1.5,
    )
    return rede


def _imprimir_somente_fila(rede: SimuladorRede, nome_fila: str, titulo: str):
    """Imprime apenas os dados da fila solicitada para facilitar preenchimento."""
    fila = rede.filas[nome_fila]

    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)
    print(f"  Tempo Global da Simulacao: {rede.tempo_atual:.4f} minutos")
    print(f"  Numeros Aleatorios Consumidos: {rede.gerador.aleatorios_consumidos}")
    print("=" * 70)
    print(f"  FILA: {nome_fila}")
    print(f"  Servidores: {fila.num_servidores}, Capacidade: {fila.capacidade}")
    print(f"  {'-' * 70}")
    print(f"    Clientes Processados: {fila.total_clientes_processados}")
    print(f"    Clientes Perdidos: {fila.total_clientes_perdidos}")

    print(f"\n    {'Estado':<10} {'Tempo (min)':>14} {'Probabilidade':>14}")
    print(f"    {'-' * 10} {'-' * 14} {'-' * 14}")
    for i in range(fila.capacidade + 1):
        tempo_estado = fila.tempo_no_estado[i]
        prob = (tempo_estado / rede.tempo_atual * 100) if rede.tempo_atual > 0 else 0
        print(f"    {i:<10} {tempo_estado:>14.4f} {prob:>13.2f}%")
    print("=" * 70)


def exemplo_para_fila_3_4():
    """Campo do professor: G/G/2/3 com atendimento entre 3..4 (Fila1)."""
    rede = _executar_cenario_itens_2_e_3()
    _imprimir_somente_fila(
        rede,
        "Fila1",
        "ITEM 2: G/G/2/3, chegadas 1..4, atendimento 3..4",
    )


def exemplo_para_fila_2_3():
    """Campo do professor: G/G/1/5 com atendimento entre 2..3 (Fila2)."""
    rede = _executar_cenario_itens_2_e_3()
    _imprimir_somente_fila(
        rede,
        "Fila2",
        "ITEM 3: G/G/1/5, atendimento 2..3 (sem chegadas externas)",
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in {"professor", "itens23", "validacao"}:
        exemplo_professor_itens_2_e_3()
        raise SystemExit(0)

    if len(sys.argv) > 1 and sys.argv[1].lower() in {"fila_3_4", "item2", "exemplo_para_fila_3_4"}:
        exemplo_para_fila_3_4()
        raise SystemExit(0)

    if len(sys.argv) > 1 and sys.argv[1].lower() in {"fila_2_3", "item3", "exemplo_para_fila_2_3"}:
        exemplo_para_fila_2_3()
        raise SystemExit(0)

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
    exemplo_professor_itens_2_e_3()
    
    print("\n" + "="*70)
    print("  FIM DOS EXEMPLOS")
    print("="*70)
