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
ligado = False

def receive_message(conexao_chat_server):
  global ligado 
  ligado = True
  
  while ligado:
    try: 
      mensagem = conexao_chat_server.recv(BUFF_SIZE).decode("utf8")
    except:
      ligado = False

    if ligado and not mensagem == ' ':
      print(mensagem)
    

def send_message(mensagem_a_enviar, conexoes_chat_servers, evento = None):
  if conexoes_chat_servers:
    for conexao_chat_server in conexoes_chat_servers:
      try:
        conexao_chat_server.send(bytes(mensagem_a_enviar, "utf8"))
        break
      except BrokenPipeError:
        conexoes_chat_servers.remove(conexao_chat_server)
        continue
      except OSError:
        break

def start_chat_user_with_multi_servers():
  global ligado

  conexoes_chat_servers = []
  # Soquetes TCP
  enderecos_de_destino = [('127.0.0.1', 3301)]

  # Tenta criar uma conexão com os servidores de destino
  for i,endereco_de_destino in enumerate(enderecos_de_destino):  
    conexao_chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
      conexao_chat_server.connect(endereco_de_destino)
      conexoes_chat_servers.append(conexao_chat_server)
      receive_thread = Thread(target=receive_message, args=(conexao_chat_server,))
      receive_thread.start()

      # Comunica-se com os servidores e consequentemente os outros usuários
      mensagem_a_enviar = input()
      while mensagem_a_enviar != '{quit}':
        send_message( mensagem_a_enviar, conexoes_chat_servers )
        mensagem_a_enviar = input()
        
      # Informando para os servidores que irá fechar a conexão
      send_message( mensagem_a_enviar, conexoes_chat_servers )
      ligado = False
      conexao_chat_server.close()
      receive_thread._stop
    except ConnectionRefusedError: 
      print('Problema ao se conectar ao {}'.format(endereco_de_destino))

      

  print('Desconectado com sucesso')

start_chat_user_with_multi_servers()
#start_chat_user()
#start_cliente_udp()
