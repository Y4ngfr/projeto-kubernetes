import subprocess
import sys
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

if len(sys.argv) != 2:
    print("Entre com filename")
    exit(1)

filename = sys.argv[1]

file_exists = os.path.isfile(filename)

with open(filename, 'a', newline='') as csvfile:
    fieldnames = [
        'numero_clientes',
        'numero_servidores',
        'msgs_por_cliente',
        'tempo_todos_clientes',
        'tempo_medio_por_cliente',
        'tempo_medio_por_msg',
        'Throughput_medio',
        'tempo_resposta_servidor'
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()

    # for j in range(1, 11):
        # subprocess.run(['kubectl', 'scale', 'deployment', 'server-deployment', f"--replicas={str(j)}"])
    for i in range(1, 101):
        num_msgs = 5
        resultado = subprocess.run(['python3', 'simulacao.py', str(i), str(num_msgs), 'client/registros/output_data_1.csv'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        df = pd.read_csv('client/registros/output_data_1.csv')
        tempo_total = df['tempo_total_segundos'].tail(i).sum()
        tempo_medio_por_msg = df['tempo_medio_por_msg'].tail(i).sum() / i
        throughput_medio = df['Throughput'].tail(i).sum() / i
        tempo_resposta_server_por_msg = df['tempo_medio_resposta_servidor'].tail(i).sum() / i
        
        writer.writerow({
            'numero_clientes': i,
            'numero_servidores': 10,
            'msgs_por_cliente': 5,
            'tempo_todos_clientes': tempo_total,
            'tempo_medio_por_cliente': tempo_total/i,
            'tempo_medio_por_msg': tempo_medio_por_msg, # latência media (de mensagens)
            'Throughput_medio': throughput_medio,
            'tempo_resposta_servidor': tempo_resposta_server_por_msg,   # tempo de resposta por mensagem
            # 'uso_de_cpu': ,
            # 'uso_de_memoria': ,
            # 'uso_de_rede'
        })

        # print(resultado.stdout)

    # Configuração do estilo dos gráficos
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = [12, 6]

    # Carregar os dados
    df = pd.read_csv(filename)

    # 1. Gráfico de Tempo Total vs Número de Clientes
    plt.figure(figsize=(14, 7))
    sns.regplot(x='numero_clientes', y='tempo_todos_clientes', data=df,
            scatter_kws={'s':60,'alpha':0.6}, 
            line_kws={'color':'blue', 'linestyle':'--'})
    plt.title('Tempo Total de Processamento vs Número de Clientes', fontsize=16)
    plt.xlabel('Número de Clientes', fontsize=14)
    plt.ylabel('Tempo Total (segundos)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(np.arange(0, 101, 10))
    plt.tight_layout()
    plt.savefig(f"figuras/tempo_total_vs_clientes.png", dpi=300)
    plt.show()

    # 2. Gráfico de Tempo Médio por Cliente
    plt.figure(figsize=(14, 7))
    sns.regplot(x='numero_clientes', y='tempo_medio_por_cliente', data=df, 
                scatter_kws={'s': 60, 'alpha': 0.6}, 
                line_kws={'color': 'blue', 'linestyle': '--'})
    plt.title('Tempo Médio por Cliente vs Número de Clientes', fontsize=16)
    plt.xlabel('Número de Clientes', fontsize=14)
    plt.ylabel('Tempo por Cliente (segundos)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(np.arange(0, 101, 10))
    plt.tight_layout()
    plt.savefig(f"figuras/tempo_medio_cliente.png", dpi=300)
    plt.show()

    # 3. Gráfico de Tempo Médio por Mensagem
    plt.figure(figsize=(14, 7))
    sns.regplot(x='numero_clientes', y='tempo_medio_por_msg', data=df, 
                scatter_kws={'s': 60, 'alpha': 0.6}, 
                line_kws={'color': 'blue', 'linestyle': '--'})
    plt.title('Tempo Médio por Mensagem vs Número de Clientes', fontsize=16)
    plt.xlabel('Número de Clientes', fontsize=14)
    plt.ylabel('Tempo por Mensagem (segundos)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(np.arange(0, 101, 10))
    plt.tight_layout()
    plt.savefig(f"figuras/tempo_medio_mensagem.png", dpi=300)
    plt.show()

    # 4. Gráfico Throughput médio
    plt.figure(figsize=(14, 7))
    sns.regplot(x='numero_clientes', y='Throughput_medio', data=df, 
                scatter_kws={'s': 60, 'alpha': 0.6}, 
                line_kws={'color': 'blue', 'linestyle': '--'})
    plt.title('Throughput Médio vs Número de Clientes', fontsize=16)
    plt.xlabel('Número de Clientes', fontsize=14)
    plt.ylabel('Throughput Médio (mensagens/segundo)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(np.arange(0, 101, 10))
    plt.tight_layout()
    plt.savefig(f"figuras/throughput_medio.png", dpi=300)
    plt.show()

    # 5. Gráfico Throughput médio
    plt.figure(figsize=(14, 7))
    sns.regplot(x='numero_clientes', y='tempo_resposta_servidor', data=df, 
                scatter_kws={'s': 60, 'alpha': 0.6}, 
                line_kws={'color': 'blue', 'linestyle': '--'})
    plt.title('Tempo de Resposta do Servidor (por mensagem) vs Número de Clientes', fontsize=16)
    plt.xlabel('Número de Clientes', fontsize=14)
    plt.ylabel('Tempo de Resposta Médio', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(np.arange(0, 101, 10))
    plt.tight_layout()
    plt.savefig(f"figuras/tempo_resposta_servidor.png", dpi=300)
    plt.show()
