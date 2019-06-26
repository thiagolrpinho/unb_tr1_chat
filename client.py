# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# Nesse módulo será desenvolvido o client udp
import socket
from threading import Thread

LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP    # ENDEREÇO IP SERVIDOR
PORT = 3300        # PORTA DO SERVIDOR(CLIENTE ENVIA)
BUFF_SIZE = 1024

def start_cliente_udp():
  socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  endereco_de_destino = (HOST, PORT)
  print("Para sair envie uma mensagem com um espaço em branco")
  mensagem_a_enviar = input()
  while mensagem_a_enviar != ' ':
    socket_udp.sendto(bytes(mensagem_a_enviar, 'utf8'), endereco_de_destino)
    mensagem_a_enviar = input()
  socket_udp.close

def start_cliente_tcp():
  socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  endereco_de_destino = (HOST, PORT)
  socket_tcp.connect(endereco_de_destino)
  print("Para sair envie uma mensagem com um espaço em branco")
  mensagem_a_enviar = input()
  while mensagem_a_enviar != ' ':
    socket_tcp.send(bytes(mensagem_a_enviar, 'utf8'))
    mensagem_a_enviar = input()
  socket_tcp.close()

def receive_message(conexao_chat_server):
  ligado = True
  while ligado:
    try: 
      mensagem = conexao_chat_server.recv(BUFF_SIZE).decode("utf8")
    except:
      ligado = False

    if ligado:
      print(mensagem)
    

def send_message(mensagem_a_enviar, conexoes_chat_servers, evento = None):
  if conexoes_chat_servers:
    for conexao_chat_server in conexoes_chat_servers:
      try:
        conexao_chat_server.send(bytes(mensagem_a_enviar, "utf8"))
        print(f"Mensagem: {mensagem_a_enviar} enviada para {conexao_chat_server}")
        break
      except BrokenPipeError:
        conexoes_chat_servers.remove(conexao_chat_server)
        continue
      except OSError:
        break

def start_chat_user():
  conexao_chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Soquete TCP
  endereco_de_destino = (HOST, PORT)
  # Tenta criar uma conexão com o servidor de destino
  conexao_chat_server.connect(endereco_de_destino)
  receive_thread = Thread(target=receive_message, args=(conexao_chat_server,))
  receive_thread.start()
  mensagem_a_enviar = input()
  while mensagem_a_enviar != '{quit}':
    send_message(mensagem_a_enviar, conexao_chat_server)
    mensagem_a_enviar = input()
  # Manda uma informando para o server que irá fechar a conexão
  send_message(mensagem_a_enviar, conexao_chat_server)
  conexao_chat_server.close()

def start_chat_user_with_multi_servers():
  conexoes_chat_servers = []
  # Soquetes TCP
  enderecos_de_destino = [('127.0.0.1', 3602), ('127.0.0.1', 4141)]

  # Tenta criar uma conexão com os servidores de destino
  for i,endereco_de_destino in enumerate(enderecos_de_destino):  
    conexoes_falharam = True
    conexao_chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
      conexao_chat_server.connect(endereco_de_destino)
      conexoes_falharam = False
    except ConnectionRefusedError: 
      print(f'Problema ao se conectar ao {endereco_de_destino}')

    if not conexoes_falharam:
      conexoes_chat_servers.append(conexao_chat_server)
      receive_thread = Thread(target=receive_message, args=(conexao_chat_server,))
      receive_thread.start()
        

  if conexoes_falharam:
    return None

  # Comunica-se com os servidores e consequentemente os outros usuários
  mensagem_a_enviar = input()
  while mensagem_a_enviar != '{quit}':
    send_message( mensagem_a_enviar, conexoes_chat_servers )
    mensagem_a_enviar = input()
  
  # Informando para os servidores que irá fechar a conexão
  send_message( mensagem_a_enviar, conexoes_chat_servers )
  conexao_chat_server.close()
  print(f'Desconectado com sucesso')

start_chat_user_with_multi_servers()
#start_chat_user()
#start_cliente_udp()
