package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"net"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"
)

type Metricas struct {
	ClientID         int
	NumMessages      int
	TotalTime        float64
	ServerIP         string
	ServerPort       int
	MensagensEnviadas int
}

func main() {
	if len(os.Args) != 5 {
		fmt.Println("Entre com 4 parâmetros (SERVER_IP SERVER_PORT NUM_MESSAGES SIMULATION_FILENAME)")
		os.Exit(1)
	}

	serverIP := os.Args[1]
	serverPort, err := strconv.Atoi(os.Args[2])
	if err != nil {
		fmt.Println("PORT deve ser um número inteiro")
		os.Exit(1)
	}

	numMessages, err := strconv.Atoi(os.Args[3])
	if err != nil {
		fmt.Println("NUM_MESSAGES deve ser um número inteiro")
		os.Exit(1)
	}

	simulationFilename := os.Args[4]
	clientID := os.Getpid()
	mensagensEnviadas := 0
	var totalTime float64

	// Configurar tratamento de sinais para encerramento limpo
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Canal para comunicação entre goroutines
	done := make(chan bool)

	go func() {
		startTime := time.Now()

		conn, err := net.Dial("tcp", fmt.Sprintf("%s:%d", serverIP, serverPort))
		if err != nil {
			fmt.Printf("Erro ao conectar ao servidor: %v\n", err)
			done <- true
			return
		}
		defer conn.Close()

		fmt.Println("Cliente iniciado - Conectando ao servidor...")

		// Enviar número de mensagens
		_, err = conn.Write([]byte(fmt.Sprintf("%d\n", numMessages)))
		if err != nil {
			fmt.Printf("Erro ao enviar número de mensagens: %v\n", err)
			done <- true
			return
		}

		fmt.Println("Conectado com sucesso - Enviando NUM_MESSAGES...")

		// Ler confirmação do servidor
		reader := bufio.NewReader(conn)
		response, err := reader.ReadString('\n')
		if err != nil {
			fmt.Printf("Erro ao ler resposta do servidor: %v\n", err)
			done <- true
			return
		}

		if response == "Pronto para iniciar\n" {
			fmt.Println("Mensagem de confirmação recebida")

			for i := 0; i < numMessages; i++ {
				msg := fmt.Sprintf("mensagem para o servidor. Número [%d]\n", i)
				_, err := conn.Write([]byte(msg))
				if err != nil {
					fmt.Printf("Conexão com o servidor perdida: %v\n", err)
					break
				}

				// Esperar ACK
				ack, err := reader.ReadString('\n')
				if err != nil || ack != "ACK\n" {
					fmt.Printf("Erro na confirmação: %v\n", err)
					break
				}
				mensagensEnviadas++
			}
		}

		totalTime = time.Since(startTime).Seconds()
		fmt.Printf("Envio concluído. Total de %d mensagens em %.5f segundos\n", numMessages, totalTime)
		done <- true
	}()

	select {
	case <-sigChan:
		fmt.Println("\nRecebido sinal de encerramento, finalizando...")
	case <-done:
		// Continua normalmente
	}

	metricas := Metricas{
		ClientID:         clientID,
		NumMessages:      numMessages,
		TotalTime:        totalTime,
		ServerIP:         serverIP,
		ServerPort:       serverPort,
		MensagensEnviadas: mensagensEnviadas,
	}

	writeToCSV(metricas, simulationFilename)
}

func writeToCSV(metricas Metricas, simulationFilename string) {
	var filename string
	currentTime := time.Now()

	if simulationFilename == "0" {
		filename = fmt.Sprintf("registro_%s.csv", currentTime.Format("02-01-2006"))
	} else {
		filename = simulationFilename
	}

	file, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Printf("Erro ao abrir arquivo CSV: %v\n", err)
		return
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	fileInfo, err := file.Stat()
	if err != nil {
		fmt.Printf("Erro ao obter informações do arquivo: %v\n", err)
		return
	}

	if fileInfo.Size() == 0 {
		headers := []string{
			"end_time",
			"client_id",
			"server_ip",
			"server_port",
			"num_messages",
			"tempo_total_segundos",
			"tempo_medio_por_msg",
			"mensagens_enviadas",
		}
		writer.Write(headers)
	}

	tempoMedio := 0.0
	if metricas.NumMessages > 0 {
		tempoMedio = metricas.TotalTime / float64(metricas.NumMessages)
	}

	record := []string{
		time.Now().Format(time.RFC3339),
		strconv.Itoa(metricas.ClientID),
		metricas.ServerIP,
		strconv.Itoa(metricas.ServerPort),
		strconv.Itoa(metricas.NumMessages),
		strconv.FormatFloat(metricas.TotalTime, 'f', 5, 64),
		strconv.FormatFloat(tempoMedio, 'f', 5, 64),
		strconv.Itoa(metricas.MensagensEnviadas),
	}

	writer.Write(record)
}
