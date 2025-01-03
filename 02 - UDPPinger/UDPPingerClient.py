import time
from socket import *
import random

# Configurações do servidor e do cliente
server_name = '127.0.0.1'
server_port_pinger = 12000
server_port_heartbeat = 12001

# Cria sockets para Pinger e Heartbeat
pinger_socket = socket(AF_INET, SOCK_DGRAM)
heartbeat_socket = socket(AF_INET, SOCK_DGRAM)

# Define timeout para o cliente Pinger
pinger_socket.settimeout(1)

# Função para cliente Pinger
def udp_pinger_client():
    num_pings = 10
    rtt_values = []
    lost_packets = 0

    for sequence_number in range(1, num_pings + 1):
        send_time = time.time()
        message = f"Ping {sequence_number} {send_time}"
        
        try:
            # Envia mensagem de ping
            pinger_socket.sendto(message.encode(), (server_name, server_port_pinger))
            
            # Captura o tempo logo após o envio
            start_time = time.time()

            # Espera resposta do servidor
            response, server_address = pinger_socket.recvfrom(1024)

            recv_time = time.time()
            # Calcula RTT logo após receber a resposta
            
            rtt =  recv_time - start_time# Usando tempo entre envio e resposta
            rtt_values.append(rtt)

            print(f"Resposta do servidor: {response.decode()}")
            print(f"RTT: {rtt:.6f} segundos")
        
        except timeout:
            print("Request timed out")
            lost_packets += 1

    # Estatísticas de RTT e perda de pacotes
    if rtt_values:
        min_rtt = min(rtt_values)
        max_rtt = max(rtt_values)
        avg_rtt = sum(rtt_values) / len(rtt_values) # soma / quantia burro
    else:
        min_rtt = max_rtt = avg_rtt = 0
    
    packet_loss_rate = (lost_packets / num_pings) * 100
    print("\nEstatísticas de Ping:")
    print(f"RTT Mínimo: {min_rtt:.6f} segundos")
    print(f"RTT Máximo: {max_rtt:.6f} segundos")
    print(f"RTT Médio: {avg_rtt:.6f} segundos")
    print(f"Taxa de Perda de Pacotes: {packet_loss_rate:.2f}%")

# Função para cliente Heartbeat
def udp_heartbeat_client():
    sequence_number = 1
    
    try:
        while True:
            send_time = time.time()
            message = f"{sequence_number} {send_time}"
            
            # 20% chance de n mandar
            if random.randint(0, 10) >= 2:
                heartbeat_socket.sendto(message.encode(), (server_name, server_port_heartbeat))
                print(f"Heartbeat enviado - Seq: {sequence_number}")
            else:
                print(f"Heartbeat Seq {sequence_number} foi perdido (simulação)")

            sequence_number += 1
            time.sleep(1)  
            
    except KeyboardInterrupt:
        print("Cliente Heartbeat interrompido.")
    finally:
        heartbeat_socket.close()


# Executa os clientes de Pinger e Heartbeat simultaneamente
from threading import Thread

# Inicia os clientes Pinger e Heartbeat
Thread(target=udp_pinger_client).start()
Thread(target=udp_heartbeat_client).start()
