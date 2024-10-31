import os
import sys
import struct
import time
import socket
import select
import statistics

ICMP_ECHO_REQUEST = 8

# Códigos de erro ICMP
ICMP_ERROR_MESSAGES = {
    0: "Rede de Destino Inalcançável", #tipo 3 é do 0 ao 3
    1: "Host de Destino Inalcançável",
    2: "Protocolo Inalcançável",
    3: "Porta Inalcançável",
    4: "Fragmentação Necessária e o DF foi Definido",
    5: "Rede Desconhecida",
    6: "Host Desconhecido",
    7: "Rede é Atingível, mas Atingida por um Outro Protocolo",
    8: "Host é Atingível, mas Atingido por Outro Protocolo", #tipo 11 é o 0 e o 1
    9: "Rede de Destino Desconhecida",
    10: "Host de Destino Desconhecido",
}

def checksum(source_string):
    csum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count += 2
    if countTo < len(source_string):
        csum = csum + source_string[len(source_string) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receive_one_ping(my_socket, ID, timeout):
    time_left = timeout
    while True:
        started_select = time.time()
        what_ready = select.select([my_socket], [], [], time_left) 
        how_long_in_select = (time.time() - started_select)
        if what_ready[0] == []:  # Timeout
            return "Request timed out."

        time_received = time.time()
        rec_packet, addr = my_socket.recvfrom(1024)
        
        # Fetch the ICMP header from the IP packet
        icmp_header = rec_packet[20:28]
        type_, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)

        # Verifica o tipo de resposta ICMP
        if type_ == 0:  # Echo Reply
            rtt = time_received - struct.unpack("d", rec_packet[28:])[0] #cabecalho do 20 a 28 pq antes disso é do IP
            return rtt * 1000  # converter para milissegundos
        elif type_ == 3:  # Destination Unreachable
            return f"Destination Unreachable: {ICMP_ERROR_MESSAGES.get(code, 'Unknown code')}"
        elif type_ == 11:  # Time Exceeded
            return "Time Exceeded"
        else:
            return f"Received unknown ICMP type: {type_}"
     
def send_one_ping(my_socket, dest_addr, ID):
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    data = struct.pack("d", time.time()) 
    my_checksum = checksum(header + data)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)

    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))  # AF_INET address must be tuple, not str

def do_one_ping(dest_addr, timeout):
    icmp = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) #cria o socket - raw = placa de rede
    my_id = os.getpid() & 0xFFFF  # Retorna o id do processo

    send_one_ping(my_socket, dest_addr, my_id)
    delay = receive_one_ping(my_socket, my_id, timeout)

    my_socket.close()
    return delay

def ping(host, timeout=1, count=4):
    dest = socket.gethostbyname(host)
    print(f"Pinging {dest} using Python:")
    print("")

    total_time = 0
    received = 0
    delays = []

    for i in range(count):
        delay = do_one_ping(dest, timeout)
        if isinstance(delay, str):  # se delay for string, ele retornou msg de erro, ou request ou um codigo de erro
            print(f"Attempt {i + 1}: {delay}")
        else:  
            print(f"Reply from {dest}: time={delay:.2f} ms")
            delays.append(delay) #adiciona o valor de delay numa lista p calcular os rtt
            total_time += delay
            received += 1
        time.sleep(1)

    # Estatísticas finais
    print("\n--- Ping statistics ---")
    print(f"{count} packets transmitted, {received} received, {count - received} lost, {100 * (count - received) / count:.2f}% loss")
    if received > 0:
        print(f"RTT Min -> {min(delays):.2f} ms \nRTT Méd -> {statistics.mean(delays):.2f} ms \nRTT Max -> {max(delays):.2f} ms")

# Testando com hosts diferentes
if __name__ == "__main__":
    ping("8.8.8.8", timeout=1, count=4)  
    ping("192.168.100.100", timeout=1, count=4)  #network
    ping("192.0.2.1", timeout=1, count=4) #network tbm, ngc so pra doc
    
