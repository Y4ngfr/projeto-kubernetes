package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"sync"
	"strconv"
	"syscall"
)

var serverRunning = true
var wg sync.WaitGroup

func handleClient(conn net.Conn, addr net.Addr) {
	defer conn.Close()
	defer wg.Done()

	fmt.Printf("Conexão estabelecida com %s\n", addr)

	reader := bufio.NewReader(conn)
	numMessagesStr, err := reader.ReadString('\n')
	if err != nil {
		fmt.Printf("Erro ao ler número de mensagens: %v\n", err)
		return
	}

	numMessages, err := strconv.Atoi(numMessagesStr[:len(numMessagesStr)-1])
	if err != nil {
		fmt.Printf("Erro ao converter número de mensagens: %v\n", err)
		return
	}

	_, err = conn.Write([]byte("Pronto para iniciar\n"))
	if err != nil {
		fmt.Printf("Erro ao enviar confirmação: %v\n", err)
		return
	}

	for i := 0; i < numMessages; i++ {
		msg, err := reader.ReadString('\n')
		if err != nil {
			fmt.Printf("Erro na comunicação com %s: %v\n", addr, err)
			break
		}

		fmt.Printf("Recebido de %s: %s", addr, msg)
		_, err = conn.Write([]byte("ACK\n"))
		if err != nil {
			fmt.Printf("Erro ao enviar ACK: %v\n", err)
			break
		}
	}

	fmt.Printf("Conexão com %s fechada\n", addr)
}

func startServer(host string, port int) {
	listener, err := net.Listen("tcp", fmt.Sprintf("%s:%d", host, port))
	if err != nil {
		fmt.Printf("Erro ao iniciar servidor: %v\n", err)
		return
	}
	defer listener.Close()

	fmt.Printf("Servidor ouvindo em %s:%d\n", host, port)

	// Configurar tratamento de sinais
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		fmt.Println("\nRecebido sinal de encerramento, finalizando...")
		serverRunning = false
		listener.Close()
	}()

	for serverRunning {
		conn, err := listener.Accept()
		if err != nil {
			if !serverRunning {
				break
			}
			fmt.Printf("Erro ao aceitar conexão: %v\n", err)
			continue
		}

		wg.Add(1)
		go handleClient(conn, conn.RemoteAddr())
	}

	wg.Wait()
	fmt.Println("Servidor encerrado corretamente")
}

func main() {
	startServer("0.0.0.0", 8080)
}
