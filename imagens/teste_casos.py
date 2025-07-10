import subprocess
import sys
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata  # Para interpolação e suavização
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.interpolate import Rbf  # Para interpolação radial
from scipy.ndimage import gaussian_filter  # Importação adicionada


def plot_ultra_smooth_surface(df, column, title):
    # Pré-processamento dos dados com remoção de outliers
    x = df['numero_clientes'].values
    y = df['numero_servidores'].values
    z = df[column].values
    
    # Método robusto para remoção de outliers usando IQR
    q1 = np.percentile(z, 25)
    q3 = np.percentile(z, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Criar máscara para valores dentro dos limites
    mask = (z >= lower_bound) & (z <= upper_bound)
    
    # Aplicar máscara a todos os arrays
    x_clean = x[mask]
    y_clean = y[mask]
    z_clean = z[mask]
    
    # Verificar se há dados suficientes
    if len(z_clean) < 10:
        raise ValueError("Dados insuficientes após remoção de outliers")
    
    # Grade regular para interpolação (aumentada para melhor suavização)
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.linspace(y.min(), y.max(), 300)
    xi, yi = np.meshgrid(xi, yi)
    
    # Interpolação radial com ajuste automático de suavidade
    smooth_factor = max(0.1, 0.5 * np.std(z_clean))  # Fator adaptativo
    rbf = Rbf(x_clean, y_clean, z_clean, 
              function='multiquadric', 
              smooth=smooth_factor,
              epsilon=2)
    
    # Interpolação e tratamento de bordas
    zi = rbf(xi, yi)
    zi = np.clip(zi, np.min(z_clean), np.max(z_clean))  # Limitar aos valores originais
    
    # Suavização em múltiplos níveis
    zi = gaussian_filter(zi, sigma=2.5, mode='mirror')
    
    # Criar superfície interativa
    fig = go.Figure(data=[go.Surface(
        x=xi,
        y=yi,
        z=zi,
        colorscale='Viridis',
        opacity=0.92,
        contours_z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="limegreen",
            project_z=True
        ),
        hoverinfo='x+y+z+text',
        hovertext=[f"Clientes: {x}<br>Servidores: {y}<br>{title}: {z:.2f}" 
                  for x, y, z in zip(xi.flatten(), yi.flatten(), zi.flatten())],
        connectgaps=True
    )])
    
    # Layout profissional
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b><br><sup>Superfície Ultra Suavizada</sup>',
            font=dict(size=24)
        ),
        scene=dict(
            xaxis_title='<b>Nº de Clientes</b>',
            yaxis_title='<b>Nº de Servidores</b>',
            zaxis_title=f'<b>{title}</b>',
            camera=dict(
                eye=dict(x=1.7, y=1.7, z=0.7),
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=-0.1)
            ),
            aspectratio=dict(x=1.2, y=1, z=0.6)
        ),
        margin=dict(l=80, r=80, b=80, t=100),
        font=dict(family="Arial", size=12)
    )
    
    # Salvar com metadados
    os.makedirs('superficies_otimizadas/Python', exist_ok=True)
    fig.write_html(
        f"superficies_otimizadas/Python/{column}_suavizada.html",
        include_plotlyjs='cdn',
        config={'responsive': True}
    )
    print(f"Gráfico otimizado salvo em: superficies_otimizadas/Python/{column}_suavizada.html")

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

    for j in range(1, 12):
        subprocess.run(['kubectl', 'scale', 'deployment', 'server-deployment', f"--replicas={str(j)}"])
        for i in range(1, 101):
            num_msgs = 5
            resultado = subprocess.run(['python3', 'simulacao.py', str(i), str(num_msgs), 'client/registros/output_data_1.csv'], 
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            df = pd.read_csv('client/registros/output_data_1.csv')
            tempo_total = df['tempo_total_segundos'].tail(i).sum()
            tempo_medio_por_msg = df['tempo_medio_por_msg'].tail(i).sum() / i
            throughput_medio = df['Throughput'].tail(i).sum() / i
            tempo_resposta_server_por_msg = df['tempo_medio_resposta_servidor'].tail(i).sum() / i
            
            writer.writerow({
                'numero_clientes': i,
                'numero_servidores': j,
                'msgs_por_cliente': num_msgs,
                'tempo_todos_clientes': tempo_total,
                'tempo_medio_por_cliente': tempo_total/i,
                'tempo_medio_por_msg': tempo_medio_por_msg,
                'Throughput_medio': throughput_medio,
                'tempo_resposta_servidor': tempo_resposta_server_por_msg,
            })

    # Carregar os dados
    df = pd.read_csv(filename)

    # Configuração do estilo dos gráficos 3D
    plt.style.use('seaborn-v0_8')
    sns.set_theme(style="whitegrid")

    # Função para criar gráficos 3D com múltiplas visualizações
    def plot_3d_views(x, y, z, xlabel, ylabel, zlabel, title, filename_prefix):
        # Configurações de visualização (elevação, azimute)
        views = [
            {'elev': 20, 'azim': 45, 'suffix': 'view1'},
            {'elev': 30, 'azim': 120, 'suffix': 'view2'}, 
            {'elev': 10, 'azim': 300, 'suffix': 'view3'}
        ]
        
        for view in views:
            fig = plt.figure(figsize=(14, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Criar scatter plot 3D
            sc = ax.scatter(x, y, z, c=z, cmap='viridis', s=50, alpha=0.8)
            
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_zlabel(zlabel, fontsize=12)
            ax.set_title(f"{title} (Ângulo {view['suffix']})", fontsize=16, pad=20)
            
            # Configurar ângulo de visualização
            ax.view_init(elev=view['elev'], azim=view['azim'])
            
            # Adicionar barra de cores
            fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5, label=zlabel)
            
            plt.tight_layout()
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(f"figuras/Python/{filename_prefix}"), exist_ok=True)
            plt.savefig(f"figuras/Python/{filename_prefix}_{view['suffix']}.png", dpi=300, bbox_inches='tight')
            plt.close()

    # Configurações de visualização
    plt.style.use('seaborn-v0_8')
    sns.set_theme(style="whitegrid")

    # Criar visualizações para cada métrica
    metrics = [
        ('tempo_todos_clientes', 'Tempo Total (segundos)'),
        ('tempo_medio_por_cliente', 'Tempo por Cliente (segundos)'),
        ('tempo_medio_por_msg', 'Tempo por Mensagem (segundos)'),
        ('Throughput_medio', 'Throughput (msg/seg)'),
        ('tempo_resposta_servidor', 'Tempo Resposta Servidor (segundos)')
    ]

    # Exemplo de uso:
    for column, title in metrics:
        plot_ultra_smooth_surface(df, column, title)

    # Criar gráficos 3D com múltiplas visualizações
    metrics = [
        ('tempo_todos_clientes', 'Tempo Total (segundos)', '3d_tempo_total'),
        ('tempo_medio_por_cliente', 'Tempo por Cliente (segundos)', '3d_tempo_medio_cliente'),
        ('tempo_medio_por_msg', 'Tempo por Mensagem (segundos)', '3d_tempo_medio_mensagem'),
        ('Throughput_medio', 'Throughput (msg/seg)', '3d_throughput_medio'),
        ('tempo_resposta_servidor', 'Tempo Resposta Servidor (segundos)', '3d_tempo_resposta_servidor')
    ]

    for column, zlabel, prefix in metrics:
        plot_3d_views(
            df['numero_clientes'],
            df['numero_servidores'],
            df[column],
            'Número de Clientes',
            'Número de Servidores',
            zlabel,
            f'{zlabel} vs Clientes e Servidores',
            f"{prefix}"
        )