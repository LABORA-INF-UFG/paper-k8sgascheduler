# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 10:57:55 2023

@author: Thiago Guimarães

Fluxo do algoritmo genético:
    
    1 - Definição da representação dos cromossomos
        - Cada cromossomo representa uma solução candidata que é a alocação de PODs em Nós (Gene: 1 sim; 0 não)
    2 - Iníciar a população
        - Cada cromossomo é uma "pessoa" que carrega uma possível solução.
    3 - Avaliação da aptidão (fitness)
        - A aptidão calcula o quão boa é aquela alocação com base no peso do relacionamento entre os PODs
    4 - Seleção dos pais
        - Seleciona os cromossomos pais (roleta)
    5 - Cruzamento (crossover)
        - Realizar o cruzamento entre os pais selecionados para gerar novos cromossomos (filhos)
    6 - Mutação
        - Aplica a mutação (troca aleatória de gene). Permitindo que o algoritmo continue buscando novas soluções.
    7 - Avaliação da aptidão dos filhos
        - Calcula a aptidão de solução de cada filho gerado
    8 - Seleção dos sobreviventes
        - Exclui parte da população gerada e seleciona os cromossomos sobreviventes para gerar uma nova população
    9 - Repete os passos de 4 a 8
        - Cada vez que o algoritmo se repetir será uma nova geração criada
    10 - Retorna com a melhor solução encontrada
"""

# Dados para receber:
#   Quantas vezes deseja executar o GA?
#   Salvar em arquivo o resultado dos testes


import random
import matplotlib.pyplot as plt
import numpy as np

# --------------- Variáveis para o GA --------------- #"
tam_populacao = 100          # Tamaho da população do GA
num_geracoes = 100            # Numero de gerações do GA
prob_cruzamento = 0.8       # Probabilidade de cruzamento (80%)
prob_mutacao = 0.2          # Probabilidade de mutação (20%)
qt_teste = 1                # Qt de vezes que o teste será executado por padrão
numero_nos = 3              # Qt padrão de nós
cpu_no = 2000               # Qt de CPU de cada Nó
mem_no = 2048               # Qt de Memória de cada Nó
numero_pods = 20            # Qt de PODs a serem alocados
cpu_pod = 50               # Qt de CPU de cada POD
mem_pod = 64               # Qt de Memória de cada POD
taxa_rel = 0               # Porcentagem de preenchimento da matriz de relacionamentos
alocacao = [0,1,1,1,0,2,0,2,2,1,1,2,0,0,1,0,0,2,2,2]

def gerar_matriz_nos(numero_nos, cpu_no, mem_no):
    matriz_nos = [
        {"id": i, "cpu_no": cpu_no, "memoria_no": mem_no}
        for i in range(numero_nos)
    ]
    return matriz_nos

# Função para gerar matrizes de PODs e de Relacionamentos
def gerar_matrizes(numero_pods, cpu_pod, mem_pod, taxa_rel):
    # Criar matriz_pod
    matriz_pods = [
        {"id": i, "cpu_pod": cpu_pod, "memoria_pod": mem_pod}
        for i in range(numero_pods)
    ]

    # Criar matriz_relacionamentos
    matriz_relacionamentos = [
        [round(random.uniform(0, 1), 2) if random.uniform(0, 100) < taxa_rel else 0 for _ in range(numero_pods)]
        for _ in range(numero_pods)
    ]

    # Tornar a matriz_relacionamentos simétrica
    for i in range(numero_pods):
        for j in range(i + 1, numero_pods):
            matriz_relacionamentos[i][j] = matriz_relacionamentos[j][i]

    return matriz_pods, matriz_relacionamentos

matriz_pods, matriz_relacionamentos = gerar_matrizes(numero_pods, cpu_pod, mem_pod, taxa_rel)
matriz_nos = gerar_matriz_nos(numero_nos, cpu_no, mem_no)
# --------------- B(x) Função de Alocação
# Descrição:
# Retorna a quantidade de Nós utilizados em cada alocação
# A função set cria um conjunto de itens únicos e a função len conta esses itens
# B(x) = a quantidade de nós utilizados para alocar os pods.
def func_alocacao(alocacao):
    nos_utilizados = set(alocacao)
    num_nos_utilizados = len(nos_utilizados)
    return num_nos_utilizados

# --------------- S(x) - Função de Consumo
# Descrição:
# Calcula o percentual de consumo de CPU e Memória dos PODs nos Nós
# S(x) = capacidade total do Nó (em memória ou cpu) dividido pelo somatório da
# quantidade de recursos (em memória ou cpu) demandados pelos PODs a serem alocados
# naquele Nó.
# 1. Itera sobre cada Nó da matriz de nós
# 2. Itera sobre o vetor de alocação verificando se cada pod está alocado no Nó da iteração anterior.
# 3. Caso o POD esteja alocado realiza o somatório da quantidade de memória e cpu demandada
# 4. Retorna o somatório 
def func_consumo(alocacao, matriz_nos, matriz_pods, peso):
    soma_porc_mem = 0
    soma_porc_cpu = 0

    # Itera sobre cada nó utilizado na alocação
    for node in range(len(matriz_nos)):
        # Inicializar somatórios para cada nó
        somatorio_mem = 0
        somatorio_cpu = 0

        # Itera sobre cada POD alocado e verificar se pertence ao nó atual
        # enumerate() retorna uma tupla onde a variável 'POD' armazena o índice
        # que representa o POD e a variavel 'alocado_no' armazena o conteúdo
        # que representa o Nó.
        for pod, alocado_no in enumerate(alocacao):
            if alocado_no == node:
                # Soma a quantidade de memória e CPU consumida pelo POD no nó atual
                somatorio_mem += matriz_pods[pod]['memoria_pod']
                somatorio_cpu += matriz_pods[pod]['cpu_pod']

        # Calcula a porcentagem de utilização de memória e CPU para o nó atual
        media_mem = somatorio_mem / matriz_nos[node]['memoria_no']
        media_cpu = somatorio_cpu / matriz_nos[node]['cpu_no']

        # Soma as porcentagens calculadas aos somatórios gerais
        soma_porc_mem += media_mem ** peso
        soma_porc_cpu += media_cpu ** peso
        
        #print(f"Consumo de recursos do nó {matriz_nos[node]['id']}")
        #print(f"Porcentagem de uso da memória: {media_mem}%")
        #print(f"Porcentagem de uso da CPU: {media_cpu}%")
        #print("---")

    #print(f"Somatório total de consumo de memória: {soma_porc_mem}")
    #print(f"Somatório total de consumo de CPU: {soma_porc_cpu}")

    return soma_porc_mem, soma_porc_cpu

# --------------- I(x) - Função de Infactibilidade
# Descrição:
# Calcula a infactibilidade na alocação (se a alocação é viável ou não)
# É uma medida do quão próximo o Nó está de ficar sem recursos.
# I(x) = -1 ou 0 
# -1 -> se i(x) > 1 a alocação não é viável (pois excede a capacidade do nó 0.99%)
# 0 -> Caso Contrário
# 1. Itera sobre cada Nó da matriz de nós
# 2. Itera sobre o vetor de alocação verificando se cada pod está alocado no Nó da iteração anterior.
# 3. Caso o POD esteja alocado realiza o somatório da quantidade de memória e cpu demandada
# 4. Calcula a proporção de utilização do Nó (em memória e cpu)
#   a. Retorna 0 se a alocação for factivel
#   b. Retorna -1 se a alocação for infactível
# 5. Retorna o somatório da infactibilidade da alocação
def func_infactibilidade(alocacao, matriz_nos, matriz_pods):
    somatorio_inf_mem = 0
    somatorio_inf_cpu = 0
    
    # Itera sobre cada nó utilizado na alocação
    for node in range(len(matriz_nos)):
        infactibilidade_mem = 0
        infactibilidade_cpu = 0
        somatorio_mem = 0
        somatorio_cpu = 0

        # Itera sobre cada POD alocado e verificar se pertence ao nó atual
        for pod, alocado_no in enumerate(alocacao):
            
            if alocado_no == node:
                somatorio_mem += matriz_pods[pod]['memoria_pod']
                somatorio_cpu += matriz_pods[pod]['cpu_pod']

        if (somatorio_mem / matriz_nos[node]['memoria_no']) <= 1:
            infactibilidade_mem += 0
        else:
            infactibilidade_mem += (somatorio_mem / matriz_nos[node]['memoria_no'])
            
        if (somatorio_cpu / matriz_nos[node]['cpu_no']) <= 1:
            infactibilidade_cpu += 0
        else:
            infactibilidade_cpu += (somatorio_cpu / matriz_nos[node]['cpu_no'])
        
        # if (somatorio_mem /  matriz_nos[node]['memoria_no']) <= 1:
        #     infactibilidade_mem += 0
        # else:
        #     infactibilidade_mem += -1
            
        # if (somatorio_cpu /  matriz_nos[node]['cpu_no']) <= 1:
        #     infactibilidade_cpu += 0
        # else:
        #     infactibilidade_cpu += -1
        
        # Imprimir informações de infactibilidade para o nó atual
        #print(f"Infactibilidade do nó {matriz_nos[node]['id']}")
        #print(f"Infactibilidade Memória: {infactibilidade_mem}")
        #print(f"Infactibilidade CPU: {infactibilidade_cpu}")
        
        # Acumular infactibilidade total para o nó
        somatorio_inf_mem += infactibilidade_mem
        somatorio_inf_cpu += infactibilidade_cpu
        
    # Retornar a infactibilidade total
    return somatorio_inf_mem, somatorio_inf_cpu

# --------------- T(x) - Calcula a taxa de relacionamento dentre os PODs
def taxa_relacionamento(alocacao, matriz_nos, matriz_pods, matriz_relacionamentos):
    pesos_comunicacao = [0] * len(matriz_nos)
    for i, node in enumerate(alocacao):
            for j in range(i + 1, len(alocacao)):
                if alocacao[j] == node:
                    pod1 = i
                    pod2 = j
                    peso = matriz_relacionamentos[pod1][pod2]
                    pesos_comunicacao[node] += peso
    soma_pesos = sum(pesos_comunicacao)
    return soma_pesos

# --------------- F(x) Função de Aptidão
# Descrição:
# Avalia cada alocação e retorna sua aptidão.
# f(x) = O somatório da porcentagem de ocupação da memória de todos os nós dividido 
# pela quantidade de nós utilizados na alocação somado ao somatório da porcentagem 
# de ocupação da cpu de todos os nós dividido pela quantidade de nós utilizados 
# na alocação somado a taxa de relacionamento entre os nós subtraido a infactibilidade 
# de alocação de memória subtraido a infactibilidade de alocação de cpu.
def calcular_aptidao(alocacao, matriz_nos, matriz_pods, matriz_relacionamentos):
    
    somatorio_mem, somatorio_cpu = func_consumo(alocacao, matriz_nos, matriz_pods, 2)
    num_nos = func_alocacao(alocacao)
    somatorio_inf_mem, somatorio_inf_cpu = func_infactibilidade(alocacao, matriz_nos, matriz_pods)
    taxa_rel = taxa_relacionamento(alocacao, matriz_nos, matriz_pods, matriz_relacionamentos)
    
    aptidao = (somatorio_mem / num_nos + somatorio_cpu / num_nos) - (somatorio_inf_mem + somatorio_inf_cpu) + taxa_rel
    
    # print("# --------------------------------------------- #")
    # print (alocacao)
    # print (f"Numero de Nós utilizados: {num_nos}")
    # print(f"Penalidade = {somatorio_inf_cpu+somatorio_inf_mem}")
    # print(f"Relacionamento = {taxa_rel}")
    
    # print(f"Aptidão: {aptidao}")
    
    return aptidao

print("Alocação informada:", alocacao)
aptidao = calcular_aptidao(alocacao, matriz_nos, matriz_pods, matriz_relacionamentos)
print("Aptidão da alocação:", aptidao)