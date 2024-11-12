import socket
import urllib.parse
import hashlib
import os

# Cria a pasta de cache caso ela não exista
cache_dir = "cache"
if not os.path.exists(cache_dir): 
    os.makedirs(cache_dir)

def get_cache_filename(url):
    """Gera o nome do arquivo de cache com base no hash MD5 da URL."""
    cache_key = hashlib.md5(url.encode()).hexdigest() #gera um hash MD5 da URL -> md5 converte URL numa string
    return os.path.join(cache_dir, cache_key)

def handle_client_request(client_socket):
    """Função que recebe a requisição do cliente, redireciona ao servidor e responde ao cliente."""
    try:
        # Recebe a solicitação do cliente
        request = client_socket.recv(4096).decode() 
        first_line = request.split('\n')[0] #separa a primeira linha p ver se e get post ou outro e tbm separa a propria url dembaixo
        method, url, _ = first_line.split() #tipo garçom, o cliente fez um pedido e tem que separar pro cozinheiro -> quero carne, o /carne vai ser o get
        
        # Trata os métodos GET e POST
        if method not in ['GET', 'POST']:
            client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n") #so aceita pra receber e enviar, se n for um desses get ou post, n aceita
            client_socket.close() 
            return

        # Converte a URL para garantir que ela seja bem formada -- separa ela entre host e caminho
        parsed_url = urllib.parse.urlparse(url if url.startswith('http') else 'http://' + url.lstrip('/')) #se n tiver http, coloca, se tiver, n faz nada 
        host = parsed_url.hostname #pega o host da url 
        path = parsed_url.path or '/' #pega o caminho da url e se n tiver coloca uma barra
        
        if not host:
            client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            client_socket.close()
            return

        # Verifica se a resposta está no cache
        cache_filename = get_cache_filename(url) # vai ver se existe a resposta, se encontrar ele envia diretamente ao cliente sem precisar do servidor
        if method == 'GET' and os.path.exists(cache_filename):
            print(f"Resposta encontrada no cache para: {url}")
            with open(cache_filename, 'rb') as cache_file:
                cached_response = cache_file.read()
            client_socket.sendall(cached_response)
            client_socket.close()
            return

        # Tenta conectar ao servidor de destino
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # se n tiver a resposta no cache paizao, vai ter que pedir pro servidor
            server_socket.connect((host, 80))
            print(f"Conectado ao servidor {host}")

            # Para GET, cria o pedido padrão
            if method == 'GET':
                full_request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode() #pede pro servidor a resposta
            # Para POST, inclui o corpo da requisição
            elif method == 'POST':
                content_length = 0
                headers = request.split('\n')[1:]
                for header in headers:
                    if 'Content-Length' in header:
                        content_length = int(header.split(':')[1].strip())

                # Extrai o corpo da requisição POST
                body = request.split('\r\n\r\n')[1] if content_length > 0 else ''

                full_request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{body}".encode()

            # Envia a solicitação para o servidor de destino
            server_socket.sendall(full_request) #e aq manda tudo que foi tratado antes do post e get

            # Recebe a resposta do servidor
            response = b""
            while True:
                data = server_socket.recv(4096)
                if not data:
                    break
                response += data

            # Checa o código de status da resposta
            if b"404 Not Found" in response:
                print("Erro 404 - Página não encontrada.")
                client_socket.sendall(response)
            elif b"403 Forbidden" in response:
                print("Erro 403 - Acesso proibido.")
                client_socket.sendall(response)
            elif b"500 Internal Server Error" in response:
                print("Erro 500 - Problema no servidor.")
                client_socket.sendall(response)
            else:
                # Caso não seja um erro, envia a resposta normalmente
                print(f"Armazenando a resposta no cache para: {url}")
                with open(cache_filename, 'wb') as cache_file:
                    cache_file.write(response)  # Armazena a resposta no arquivo de cache
                client_socket.sendall(response) #envia resposta ao cliente

            server_socket.close()

        except socket.error as e:
            print(f"Erro ao conectar ao servidor: {e}")
            client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
    
    client_socket.close()

def start_proxy_server(port):
    """Inicia o servidor proxy."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(5)
    print(f"Servidor proxy em execução em localhost:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexão recebida de {client_address}")
        handle_client_request(client_socket)

# Porta do servidor proxy
start_proxy_server(8888)
#http://localhost:8888/www.google.com/404notfound