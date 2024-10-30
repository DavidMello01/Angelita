import socket
import ssl
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Configurações do servidor SMTP e credenciais
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # Porta para conexões TLS
username = 'pessoal.david2307@gmail.com'  # Substitua pelo seu e-mail
password = 'wine cixb tbkg bhal'  # Substitua pela sua senha
recipient = 'pessoal.david2307@gmail.com'  # Substitua pelo e-mail do destinatário

# Função para enviar comandos e receber respostas do servidor SMTP
def send_command(sock, command):
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print(f"SERVIDOR: {response}")
    return response

# Estabelece a conexão segura com TLS
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((smtp_server, smtp_port))
print("Conectado ao servidor SMTP")

# Inicia a comunicação com o servidor
response = client_socket.recv(1024).decode()
print(f"SERVIDOR: {response}")

# Envia comando EHLO
send_command(client_socket, "EHLO cliente.com\n") #EHLO é tipo um guia turistico

# Inicia a camada de segurança TLS
send_command(client_socket, "STARTTLS\n")
client_socket = ssl.wrap_socket(client_socket) # o start é tipo qnd vc migra de pais

# Reenvia EHLO para iniciar uma sessão segura
send_command(client_socket, "EHLO cliente.com\n")

# Autenticação Base64
send_command(client_socket, "AUTH LOGIN\n")
send_command(client_socket, base64.b64encode(username.encode()).decode() + "\n")
send_command(client_socket, base64.b64encode(password.encode()).decode() + "\n")

# Comando MAIL FROM
send_command(client_socket, f"MAIL FROM:<{username}>\n")

# Comando RCPT TO
send_command(client_socket, f"RCPT TO:<{recipient}>\n")

# Comando DATA
send_command(client_socket, "DATA\n")

# Criação da mensagem MIME
msg = MIMEMultipart()
msg['From'] = username
msg['To'] = recipient
msg['Subject'] = "Feliz natal, receba esse presente"

# Corpo do texto
texto = "Olá, este é um teste de e-mail com texto e imagem usando sockets e SMTP."
msg.attach(MIMEText(texto, 'plain'))

# Anexando a imagem
filename = "gatonatalino.jpg"  # Nome do arquivo da imagem
with open(filename, "rb") as attachment:
    part = MIMEBase("application", "octet-stream") #octect é um tipo de binário genérico (?)
    part.set_payload(attachment.read())

encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename= {filename}")
msg.attach(part)

# Envio do corpo do e-mail
client_socket.sendall(msg.as_string().encode() + b"\r\n.\r\n") 
response = client_socket.recv(1024).decode()
print(f"SERVIDOR: {response}")

# Finaliza a conexão com o servidor SMTP
send_command(client_socket, "QUIT\n")
client_socket.close()
print("E-mail enviado e conexão encerrada.")
