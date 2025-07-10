import socket
import os
from threading import Thread, Event
import signal
import sys

server_running = Event()
server_running.set()

def handle_client(conn: socket.socket, addr):
    """Lida com a conexão de um cliente"""
    try:
        # print(f"Conexão estabelecida com {addr}", flush=True)
        
        # Receber número de mensagens esperadas
        num_messages = int(conn.recv(1024).decode('utf-8'))
        conn.sendall(b"Pronto para iniciar")

        for _ in range(num_messages):
            try:
                data = conn.recv(1024)
                if not data:  # Conexão fechada pelo cliente
                    break

                # msg = data.decode('utf-8')
                # print(f"Recebido de {addr}: {msg}", flush=True)
                conn.sendall(b"ACK")
                
            except (ConnectionResetError, UnicodeDecodeError) as e:
                print(f"Erro na comunicação com {addr}: {str(e)}", flush=True)
                break
                
    except Exception as e:
        print(f"Erro no handler do cliente {addr}: {str(e)}", flush=True)
    finally:
        conn.close()
        # print(f"Conexão com {addr} fechada", flush=True)

def shutdown_server(signum, frame):
    """Encerra o servidor de forma limpa"""
    # print(f"\nRecebido sinal {signum}, encerrando servidor...", flush=True)
    server_running.clear()

def start_server(host='0.0.0.0', port=8080):
    """Inicia o servidor TCP"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        # print(f"Servidor ouvindo em {host}:{port}", flush=True)
        
        # Configurar timeout menor para resposta mais rápida a sinais
        s.settimeout(0.1)
        
        signal.signal(signal.SIGINT, shutdown_server)
        signal.signal(signal.SIGTERM, shutdown_server)
        
        try:
            while server_running.is_set():
                try:
                    conn, addr = s.accept()
                    thread = Thread(target=handle_client, args=(conn, addr))
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Erro ao aceitar conexão: {str(e)}", flush=True)
                    if not server_running.is_set():
                        break
        
        finally:
            print("Servidor encerrado corretamente", flush=True)

if __name__ == '__main__':
    start_server()