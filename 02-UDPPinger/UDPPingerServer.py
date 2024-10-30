import random
import time
from socket import *


server_port_pinger = 12000
server_port_heartbeat = 12001

pinger_socket = socket(AF_INET, SOCK_DGRAM)
heartbeat_socket = socket(AF_INET, SOCK_DGRAM)


pinger_socket.bind(('', server_port_pinger))
heartbeat_socket.bind(('', server_port_heartbeat))

# Armazena informações de última sequência e tempo no Heartbeat
last_sequence_number = 0
last_receive_time = None
lost_packets = 0
report_interval = 8

print("Servidor pronto para receber pings e heartbeats.")

def pinger_server():
    while True:
        message, client_address = pinger_socket.recvfrom(1024) #1024 é o tamanho da msg q pode receber
        if random.randint(0, 10) >= 2:
            modified_message = message.decode().upper()
            pinger_socket.sendto(modified_message.encode(), client_address) #manda de vorta pro cliente
            print(f"Ping recebido e respondido: {modified_message}")

            time.sleep(0.005)

        else:
            print("Ping recebido e ignorado (simulação de perda de pacote).")

# Variáveis globais para controle de pacotes perdidos e contagem de heartbeats
heartbeat_counter = 0  # Contador de heartbeats recebidos
report_interval = 10  # Defina o valor X (intervalo para exibir o relatório)

def heartbeat_server():
    global last_sequence_number, last_receive_time, lost_packets, heartbeat_counter
    
    while True:
        # Recebe mensagens de heartbeat
        message, client_address = heartbeat_socket.recvfrom(1024)
        sequence_number, send_time = message.decode().split()
        sequence_number = int(sequence_number)
        send_time = float(send_time)
        
        receive_time = time.time()
        rtt = receive_time - send_time

        # Detecta e conta pacotes perdidos
        if last_sequence_number and sequence_number != last_sequence_number + 1:
            lost_packets += sequence_number - last_sequence_number - 1
            print(f"Pacotes perdidos detectados: {sequence_number - last_sequence_number - 1}")
        
        # Contabiliza o tempo desde o último heartbeat
        if last_receive_time is not None:
            time_since_last_heartbeat = receive_time - last_receive_time
            print(f"Heartbeat recebido - Seq: {sequence_number}, RTT: {rtt:.6f} segundos, Tempo desde o último heartbeat: {time_since_last_heartbeat:.6f} segundos")
        else:
            print(f"Primeiro heartbeat recebido - Seq: {sequence_number}, RTT: {rtt:.6f} segundos")

        # Incrementa o contador de heartbeats
        heartbeat_counter += 1

        # Exibe relatório a cada X heartbeats e reseta o contador
        if heartbeat_counter >= report_interval:
            print("\n*** Relatório de Pacotes Perdidos ***")
            print(f"Pacotes perdidos até agora: {lost_packets}")
            print(f"Total de heartbeats recebidos: {heartbeat_counter}\n")
            heartbeat_counter = 0  # Reseta o contador para o próximo intervalo

        # Atualiza o último número de sequência e tempo de recepção
        last_sequence_number = sequence_number
        last_receive_time = receive_time


       

# Executa os servidores de Pinger e Heartbeat simultaneamente
from threading import Thread

# Inicia os servidores Pinger e Heartbeat
Thread(target=pinger_server).start()
Thread(target=heartbeat_server).start()
