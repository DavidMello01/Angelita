import socket
import ssl
import base64 #preicsa pro smtp, converte binario em texto ascii
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText #imports pro Mime, q estrutura o email em diferentes tipos de conteudo
from email.mime.base import MIMEBase
from email import encoders

# Configurações do servidor SMTP e credenciais
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # Porta para conexões TLS
username = 'pessoal.david2307@gmail.com'  
password = 'wine cixb tbkg bhal'  # lembrar de apagar essa senha dps de apresentar
recipient = 'pessoal.david2307@gmail.com'  

# Função para enviar comandos e receber respostas do servidor SMTP
def send_command(sock, command):
    sock.sendall(command.encode()) 
    response = sock.recv(1024).decode()
    print(f"SERVIDOR: {response}") #envia e espera resposta do servdir
    return response

# Estabelece a conexão segura com TLS (versao moderna do SSL)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #sock_stream pro tcp
client_socket.connect((smtp_server, smtp_port))
print("Conectado ao servidor SMTP")

# Inicia a comunicação com o servidor
response = client_socket.recv(1024).decode()
print(f"SERVIDOR: {response}")

# Envia comando EHLO
send_command(client_socket, "EHLO cliente.com\n") #EHLO é tipo um guia turistico, apresenta o server

# Inicia a camada de segurança TLS
send_command(client_socket, "STARTTLS\n")
client_socket = ssl.wrap_socket(client_socket) # o start é tipo qnd vc migra de pais, e precisa de um visto novo, ele solicita uma conexao TLS(segura)
#wrap socket converte pra um socket mais seguro q criptografa os dados

# Reenvia EHLO para iniciar uma sessão segura
send_command(client_socket, "EHLO cliente.com\n")

# Autenticação Base64
send_command(client_socket, "AUTH LOGIN\n")
send_command(client_socket, base64.b64encode(username.encode()).decode() + "\n") #pede user e senha em baixo. Isso aq faz a autenticação com o email
send_command(client_socket, base64.b64encode(password.encode()).decode() + "\n") #b64 codifica o user e a senha p evitar

# Comando MAIL FROM
send_command(client_socket, f"MAIL FROM:<{username}>\n")

# Comando RCPT TO
send_command(client_socket, f"RCPT TO:<{recipient}>\n")

# Comando DATA
send_command(client_socket, "DATA\n")

# Criação da mensagem MIME
msg = MIMEMultipart() #objeto q permite anexar diferentes tipos de conteudo no emial
msg['From'] = username
msg['To'] = recipient
msg['Subject'] = "Feliz natal, receba esse presente"

# Corpo do texto
texto = "ho ho ho"
msg.attach(MIMEText(texto, 'plain'))

# Anexando a imagem
filename = "gatonatalino.jpg"  # Nome do arquivo da imagem
with open(filename, "rb") as attachment:
    part = MIMEBase("application", "octet-stream") #octect é um tipo de binário genérico (?) MimeBase mostra q o arquivo é binário -> tem algo a ver com o deciframento de imagens la?
    part.set_payload(attachment.read()) #coloca o conteudo da img no part

encoders.encode_base64(part) # criptografa o part
part.add_header("Content-Disposition", f"attachment; filename= {filename}")
msg.attach(part) #anexa o part no email - q no caso é uma img

# Envio do corpo do e-mail
client_socket.sendall(msg.as_string().encode() + b"\r\n.\r\n")  #sendall faz manda tudo como string no corpo do email
response = client_socket.recv(1024).decode()
print(f"SERVIDOR: {response}")

# Finaliza a conexão com o servidor SMTP
send_command(client_socket, "QUIT\n")
client_socket.close()
print("E-mail enviado e conexão encerrada.")
