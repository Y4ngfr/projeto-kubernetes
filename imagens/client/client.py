import socket
import time
import sys
import os
import csv
from datetime import datetime

class Metricas:
    def __init__(self, client_id, num_messages, total_time, server_ip, server_port, mensagens_enviadas, tempo_resposta_server):
        self.client_id = client_id
        self.num_messages = num_messages
        self.total_time = total_time
        self.server_ip = server_ip
        self.server_port = server_port
        self.mensagens_enviadas = mensagens_enviadas
        self.tempo_resposta_server = tempo_resposta_server    # tempo de resposta por mensagem

def main():
    if len(sys.argv) != 5:
       print("entre com 3 parâmetros (SERVER_IP SERVER_PORT NUM_MESSAGES)")
       exit(1)

    try:
        SERVER_IP = sys.argv[1]
        SERVER_PORT = int(sys.argv[2])
        NUM_MESSAGES = int(sys.argv[3])
        SIMULATION_FILENAME = sys.argv[4]
        # SERVER_IP = os.getenv('ipservice', '10.96.178.125')
        # SERVER_PORT = int(os.getenv('port', '8085'))
        # NUM_MESSAGES = int(os.getenv('num_messages', '10'))
    except ValueError:
        print("PORT, NUM_MESSAGES e SET_ARQUIVO devem ser números inteiros", flush=True)
        exit(1)
    
    CLIENT_ID = os.getpid()
    mensagens_enviadas = 0

    try:        
        start_time = time.time()
        server_response_time = 0

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # print("Cliente iniciado - Conectando ao servidor...", flush=True)
            s.connect((SERVER_IP, SERVER_PORT))

            # print("Conectado com sucesso - Enviando NUM_MESSAGES...", flush=True)
            s.sendall(f"{NUM_MESSAGES}".encode('utf-8'))

            data_recv = s.recv(1024)
            response = data_recv.decode('utf-8')

            if response == "Pronto para iniciar":
                # print("Mensagem de confirmação recebida", flush=True)

                for i in range(NUM_MESSAGES):
                    msg = f"menssagem para o servidor. Número [{i}]"
                    data = msg.encode('utf-8')
                    s.sendall(data)
                    start_server_response_time = time.time()
                    confirmacao = s.recv(1024).decode('utf-8')
                    end_server_response_time = time.time()
                    server_response_time += end_server_response_time - start_server_response_time
                    if(confirmacao == "ACK"):
                        mensagens_enviadas += 1
                        continue
                    else:
                        # print("Conexão com o servidor perdida", flush=True)
                        break
            
            end_time = time.time()
            total_time = end_time - start_time
            server_response_time_medio = server_response_time / i

            # print(f"Envio concluído. Total de {NUM_MESSAGES} mensagens em {total_time:.5f} segundos", flush=True)
            
    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor. Verifique se o servidor está em execução.", flush=True)
    except socket.error as e:
        print(f"Erro de socket: {str(e)}", flush=True)
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", flush=True)

    metricas = Metricas(CLIENT_ID, NUM_MESSAGES, total_time, SERVER_IP, SERVER_PORT, mensagens_enviadas, server_response_time_medio)
    write_to_csv(metricas, SIMULATION_FILENAME)

def write_to_csv(metricas:Metricas, SIMULATION_FILENAME):
    data_atual = datetime.now()

    if SIMULATION_FILENAME == '0':
        filename = f"/home/yangfr/workspace/Python/projeto_kubernetes/imagens/client/registros/registro_{data_atual.strftime('%d-%m-%Y')}.csv"
    else:
        filename = SIMULATION_FILENAME

    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='') as csvfile:
        fieldnames = [
            'end_time',
            'client_id',
            'server_ip',
            'server_port',
            'num_messages',
            'tempo_total_segundos',
            'tempo_medio_por_msg',
            'mensagens_enviadas',
            'Throughput',
            'tempo_medio_resposta_servidor'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'end_time': datetime.now().isoformat(),
            'client_id': metricas.client_id,
            'server_ip': metricas.server_ip,
            'server_port': metricas.server_port,
            'num_messages': metricas.num_messages,
            'tempo_total_segundos': metricas.total_time,
            'tempo_medio_por_msg': metricas.total_time / metricas.num_messages, # latência media por mensagem
            'mensagens_enviadas': metricas.mensagens_enviadas,
            'Throughput': metricas.num_messages / metricas.total_time, # mensagens / segundo
            'tempo_medio_resposta_servidor': metricas.tempo_resposta_server
        }) 

if __name__ == '__main__':
    main()