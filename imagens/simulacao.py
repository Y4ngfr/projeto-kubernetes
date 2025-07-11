import subprocess
import time
import sys
from concurrent.futures import ThreadPoolExecutor

def run_client(client_id, server_ip, port, num_msgs, filename):
    """Função que executa um cliente como subprocesso"""
    # cmd = f"python3 client/client.py {server_ip} {port} {num_msgs} {filename}"
    cmd = f"./client/client {server_ip} {port} {num_msgs} {filename}"
    #print(f"[Cliente {client_id}] Iniciando...")
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Entre com parâmetros")
        exit(1)

    SERVER_IP = "127.0.0.1"
    PORT = 8085
    try:
        NUM_CLIENTS = int(sys.argv[1])      # Quantidade de clientes
        MSGS_PER_CLIENT = int(sys.argv[2])  # Mensagens por cliente
    except ValueError:
        print("NUM_CLIENTS e MSGS_PER_CLIENT devem ser inteiros")
        exit(1)

    SIMULATION_FILENAME = sys.argv[3]

    #print(f"🔥 Iniciando {NUM_CLIENTS} clientes SIMULTANEAMENTE...")
    start_time = time.time()

    # Usando ThreadPool para lançar todos os subprocessos de uma vez
    with ThreadPoolExecutor(max_workers=NUM_CLIENTS) as executor:
        futures = [
            executor.submit(
                run_client,
                i+1, SERVER_IP, PORT, MSGS_PER_CLIENT, SIMULATION_FILENAME
            )
            for i in range(NUM_CLIENTS)
        ]

    #print(f"✅ Todos os clientes terminaram em {time.time() - start_time:.5f}s")