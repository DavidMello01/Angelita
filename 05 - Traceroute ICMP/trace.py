import socket
import struct
import os
import time

ICMP_ECHO_REQUEST = 8  # Tipo de mensagem de eco ICMP
ICMP_TIME_EXCEEDED = 11  # Tipo de mensagem ICMP Time Exceeded

def checksum(source_string):
    """Calcula o checksum para os pacotes ICMP."""
    countTo = (len(source_string) // 2) * 2
    sum = 0
    for i in range(0, countTo, 2):
        sum += (source_string[i]) + (source_string[i + 1] << 8)
    if countTo < len(source_string):
        sum += source_string[-1]
    sum = (sum >> 16) + (sum & 0xFFFF)
    sum += (sum >> 16)
    return ~sum & 0xFFFF

def send_ping(sock, dest_addr, ttl):
    """Envia um pacote ICMP para o endereço de destino com TTL especificado."""
    #header
    icmp_packet = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, os.getpid() & 0xFFFF, 1) #o bbbHhh é 1-tipo icmp,2-codigo,3-checksum,4-identificacaoprocesso, 5-sequencia
    checksum_value = checksum(icmp_packet)
    icmp_packet = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, checksum_value, os.getpid() & 0xFFFF, 1)   
    # define ottl
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)    

    sock.sendto(icmp_packet, (dest_addr, 1))  #a porta 1 não é relevante pro icmp pq ele n precisa de é independete das portas, mas precisa de um valor p funfar

def receive_ping(sock, dest_addr, timeout):
    """Recebe um pacote ICMP e retorna o endereço do roteador, se disponível."""
    sock.settimeout(timeout)
    try:
        while True: #recebe os pacote icmp
            time_received = time.time()
            packet, addr = sock.recvfrom(1024)
            return addr[0], time_received 
    except socket.timeout:
        return None, None

def traceroute(dest_name, max_ttl=30):
    """Executa o Traceroute até o destino especificado."""
    dest_addr = socket.gethostbyname(dest_name) #obtem o ip do destino
    print(f'Traceroute para {dest_name} ({dest_addr}):')

    for ttl in range(1, max_ttl + 1): 
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock: #sock_raw é permite acesso na rede
            send_ping(sock, dest_addr, ttl)
            router_ip, time_received = receive_ping(sock, dest_addr, timeout=2) #envia o pacote com o ttl atual e tenta receber a resp
            #receive_ping tenta receber a resposta do roteador, ai o retorno dessa funcao tem o ip do roteador q respondeu e o tempo q levou p responder
            if router_ip is not None:
                rtt = (time.time() - time_received) * 1000  # calcula rtt qnd recebe uma resposta
                try:
                    router_name = socket.gethostbyaddr(router_ip)[0]
                except socket.herror: 
                    router_name = "Nome não resolvido" #aq e qnd tem resposta mas os malditos n tem um DNS q associe o IP  de volta a um nome de dominio
                print(f'{ttl}\t{router_ip} ({router_name})\t{rtt:.2f} ms')
            else:
                print(f'{ttl}\t*')

            if router_ip == dest_addr:
                print('Destino alcançado!')
                break

def ping_hosts(hosts):
    """Executa o Traceroute para uma lista de hosts."""
    for host in hosts:
        print(f"\nPinging {host}...")
        traceroute(host)

if __name__ == '__main__':
    destinations = [
        "google.com",        # baidu e bbc retoram como nome nao resolvido pq eles n tem um DNS q associe o IP  de volta a um nome de dominio
        "baidu.com",         # Ásia
        "bbc.co.uk",         # Eu
        "australianews.com.au"  # Oceania
    ]
    
    ping_hosts(destinations)
