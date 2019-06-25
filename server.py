# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# É uma biblioteca python voltada para a interface de soquetes(TCP/UDP).
import socket
from threading import Thread

LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP  # ENDEREÇO IP DO HOST
PORT = 3300        # PORTA DO SERVIDOR(SERVIDOR ESCUTA)
BUFF_SIZE = 1024
MAX_USERS = 5

def start_server_udp():
  ## Envelopa todo o protocolo de rede
  socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp
  endereco_para_escutar = (HOST, PORT)
  socket_udp.bind(endereco_para_escutar)     # Esse socket estará ligado a esse endereço
  print("Servidor online: Escutando mensagens")

  while True:
    bytes_recebidos, cliente = socket_udp.recvfrom(BUFF_SIZE) # Retorna o buffer e o endereço IP de origem
    mensagem_recebida = bytes_recebidos.decode("utf8")
    print(cliente, mensagem_recebida)
  socket_udp.close()

def start_server_tcp():
  socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # tcp
  endereco_para_escutar = (HOST, PORT)
  socket_tcp.bind(endereco_para_escutar)     # Esse socket estará ligado a esse endereço
  print("Servidor online: Escutando mensagens")
  socket_tcp.listen(1)

  while True:
    con, cliente = socket_tcp.accept()
    print("Conectado a " + str(cliente[0]) + ':' + str(cliente[1]))

    while True:
      bytes_recebidos = con.recv(BUFF_SIZE) # Retorna o buffer e o endereço IP de origem
      mensagem_recebida = bytes_recebidos.decode("utf8")
      # print(mensagem_recebida)
    print("Finalizando")
    con.close()
  socket_tcp.close()

def conexao_usuario(chat_server, usuarios, usuario):

  usuario.send(bytes("Bem-vindo! " + "Escreva a sala", "utf8"))
  room = int(usuario.recv(BUFF_SIZE).decode("utf8"))
  usuario.send(bytes("Bem-vindo! " + "Escreva seu nome e aperte enter!", "utf8"))
  nickname = usuario.recv(BUFF_SIZE).decode("utf8")
  welcome = 'Para sair digite {quit} e aperte enter'
  usuario.send(bytes(welcome, "utf8"))
  mensagem = "%s se juntou ao chat" % nickname
  broadcast(usuarios[room], bytes(mensagem, "utf8"))
  usuarios[room][usuario] = nickname
  bytes_recebidos = usuario.recv(BUFF_SIZE)
  while str(bytes_recebidos, encoding='utf8') != '{quit}':
    # print(str(bytes_recebidos, encoding='utf8'))
    broadcast(usuarios[room], bytes_recebidos, usuarios[room][usuario])
    bytes_recebidos = usuario.recv(BUFF_SIZE) # Retorna o buffer e o endereço IP de origem

  usuario.close()
  del usuarios[room][usuario]
  broadcast(usuarios[room], bytes("%s está sem tempo, irmão." % nickname, "utf8"))

def recebe_usuario(chat_server, usuarios):
  enderecos = dict()
  try:
    while True:
      usuario, endereco_usuario = chat_server.accept()
      print("Conectado a " + str(endereco_usuario[0]) + ':' + str(endereco_usuario[1]))
      enderecos[usuario] = endereco_usuario
      Thread(target=conexao_usuario, args=(chat_server, usuarios, usuario)).start()
  except KeyboardInterrupt:
    pass

def broadcast(usuarios, mensagem_a_transmitir, autor = "Servidor "):
  if usuarios:
    for socket in usuarios:
      socket.send(bytes(autor  + " diz: ","utf8") + mensagem_a_transmitir )

def start_chat_server():
  try:
    chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    endereco_para_escutar = (HOST, PORT)
    chat_server.bind(endereco_para_escutar)     # Esse socket estará ligado a esse endereço
    print("Servidor online: Escutando mensagens")
    chat_server.listen(MAX_USERS)  ## escuta no máximo 5 conexões
    usuarios = [dict() for i in range(MAX_USERS)]

    ACCEPT_THREAD = Thread(target=recebe_usuario, args=(chat_server, usuarios,))
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
  except KeyboardInterrupt:
    chat_server.close()
    pass


start_chat_server()
#start_server_tcp()
#start_server_udp()
