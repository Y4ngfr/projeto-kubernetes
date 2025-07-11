# projeto-kubernetes

Este projeto fornece a implementação e os resultados de uma série de experimentos em uma simulação de rede distribuída.

Foi utilizado o Kubernetes para criar a estrutura de rede que irá "receber" a carga e o Docker como software de containers.

![Estrutura da Rede](./infra-rede.drawio.png)

# Experimentos de Carga

Todos os experimentos foram realizados variando o número de clientes de 1 a 100 e o número de servidores de 1 a 10. 

Para cada uma dessas configurações foi escolhida uma métrica para visualizar em um gráfico tri-dimensional.

Foram escolhidas as seguintes métricas:

- Tempo Médio Por Cliente
- Tempo Médio Por Mensagem
- Throughput Médio
- Tempo de Resposta do Servidor

# Resultados

## Dados Brutos

### Métrica: Tempo Médio Por Cliente

<div style="display: flex; justify-content: space-between;">
  <figure>
    <img src="imagens/figuras/Python/3d_tempo_medio_cliente_view1.png" alt="Descrição 1"/>
    <figcaption>Python</figcaption>
  </figure>
  <figure>
    <img src="imagens/figuras/Go/3d_tempo_medio_cliente_view1.png" alt="Descrição 2"/>
    <figcaption>Go</figcaption>
  </figure>
</div>

#### Python

![py tempo medio por cliente view 1](./imagens/figuras/Python/3d_tempo_medio_cliente_view1.png)
![py tempo medio por cliente view 2](./imagens/figuras/Python/3d_tempo_medio_cliente_view2.png)
![py tempo medio por cliente view 3](./imagens/figuras/Python/3d_tempo_medio_cliente_view3.png)

#### Go

![go tempo medio por cliente view 1](./imagens/figuras/Go/3d_tempo_medio_cliente_view1.png)
![go tempo medio por cliente view 2](./imagens/figuras/Go/3d_tempo_medio_cliente_view2.png)
![go tempo medio por cliente view 3](./imagens/figuras/Go/3d_tempo_medio_cliente_view3.png)

### Métrica: Tempo Médio Por Mensagem

#### Python

![py tempo medio por mensagem view 1](./imagens/figuras/Python/3d_tempo_medio_mensagem_view1.png)
![py tempo medio por mensagem view 2](./imagens/figuras/Python/3d_tempo_medio_mensagem_view2.png)
![py tempo medio por mensagem view 3](./imagens/figuras/Python/3d_tempo_medio_mensagem_view3.png)

#### Go

![go tempo medio por mensagem view 1](./imagens/figuras/Go/3d_tempo_medio_mensagem_view1.png)
![go tempo medio por mensagem view 2](./imagens/figuras/Go/3d_tempo_medio_mensagem_view2.png)
![go tempo medio por mensagem view 3](./imagens/figuras/Go/3d_tempo_medio_mensagem_view3.png)

### Métrica: Throughput Médio

#### Python

![py throughput medio view 1](./imagens/figuras/Python/3d_throughput_medio_view1.png)
![py throughput medio view 2](./imagens/figuras/Python/3d_throughput_medio_view2.png)
![py throughput medio view 3](./imagens/figuras/Python/3d_throughput_medio_view3.png)

#### Go

![go throughput medio view 1](./imagens/figuras/Go/3d_throughput_medio_view1.png)
![go throughput medio view 2](./imagens/figuras/Go/3d_throughput_medio_view2.png)
![go throughput medio view 3](./imagens/figuras/Go/3d_throughput_medio_view3.png)

### Métrica: Tempo de Resposta do Servidor

#### Python

![py tempo resposta view 1](./imagens/figuras/Python/3d_tempo_resposta_servidor_view1.png)
![py tempo resposta view 2](./imagens/figuras/Python/3d_tempo_resposta_servidor_view2.png)
![py tempo resposta view 3](./imagens/figuras/Python/3d_tempo_resposta_servidor_view3.png)

#### Go

![go tempo resposta view 1](./imagens/figuras/Go/3d_tempo_resposta_servidor_view1.png)
![go tempo resposta view 2](./imagens/figuras/Go/3d_tempo_resposta_servidor_view2.png)
![go tempo resposta view 3](./imagens/figuras/Go/3d_tempo_resposta_servidor_view3.png)

## Dados Tratados

---------------------------

Justificar os resultados (faz sentido a diferença de tempo que o python está tendo?)
Colocar a média de 5 execuções
Por que o python está caindo o tempo?

10 min e 5 min