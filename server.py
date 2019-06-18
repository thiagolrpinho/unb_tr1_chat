# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

import socket
from threading import Thread

# É uma biblioteca python voltada para a interface de soquetes(TCP/UDP).
LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP # ENDEREÇO IP DO HOST
PORT = 3300        # PORTA DO SERVIDOR(SERVIDOR ESCUTA)

def start_server_udp():
  socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  endereco_para_escutar = (HOST, PORT)
  socket_udp.bind(endereco_para_escutar)     # Esse socket estará ligado a esse endereço
  print("Servidor online: Escutando mensagens")

  while True:
    bytes_recebidos, cliente = socket_udp.recvfrom(1024) # Retorna o buffer e o endereço IP de origem
    mensagem_recebida = bytes_recebidos.decode("utf8") 
    print(cliente, mensagem_recebida)
  socket_udp.close()

def start_server_tcp():
  socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  endereco_para_escutar = (HOST, PORT)
  socket_tcp.bind(endereco_para_escutar)     # Esse socket estará ligado a esse endereço
  print("Servidor online: Escutando mensagens")
  socket_tcp.listen(1)

  while True:
    con, cliente = socket_tcp.accept()
    print("Conectado a " + str(cliente[0]) + ':' + str(cliente[1]))

    while True:
      bytes_recebidos = con.recv(1024) # Retorna o buffer e o endereço IP de origem
      mensagem_recebida = bytes_recebidos.decode("utf8") 
      print(mensagem_recebida)
    print("Finalizando")
    con.close()
  socket_tcp.close()

def conexao_usuario(chat_server, usuarios, usuario):
  
  nickname = usuario.recv(1024).decode("utf8")
  welcome = 'Para sair digite espaço em branco e aperte enter'
  usuario.send(bytes(welcome, "utf8"))
  mensagem = "%s se juntou ao chat" % nickname
  broadcast(usuarios, bytes(mensagem, "utf8"))
  usuarios[usuario] = nickname

  while mensagem != ' ':
    bytes_recebidos = usuario.recv(1024) # Retorna o buffer e o endereço IP de origem
    broadcast(usuarios, bytes_recebidos, usuarios[usuario])

  usuario.send(bytes("{quit}", "utf8"))
  usuario.close()
  del usuarios[usuario]
  broadcast(usuarios, bytes("%s arregou." % nickname, "utf8"))

def recebe_usuario(chat_server, usuarios):
  enderecos = dict()
  while True:
    usuario, endereco_usuario = chat_server.accept()
    print("Conectado a " + str(endereco_usuario[0]) + ':' + str(endereco_usuario[1]))
    usuario.send(bytes("Bem-vindo! "+
                      "Escreva seu nome e aperte enter!", "utf8"))
    enderecos[usuario] = endereco_usuario
    Thread(target=conexao_usuario, args=(chat_server, usuarios, usuario)).start()

def broadcast(usuarios, mensagem_a_transmitir, autor = "Servidor:"):
  if usuarios:
    for socket in usuarios: 
      socket.send(bytes(autor  + " diz: ","utf8") + mensagem_a_transmitir )

def start_chat_server():
  chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  endereco_para_escutar = (HOST, PORT)
  chat_server.bind(endereco_para_escutar)     # Esse socket estará ligado a esse endereço
  print("Servidor online: Escutando mensagens")
  chat_server.listen(5)
  usuarios = dict()

  ACCEPT_THREAD = Thread(target=recebe_usuario, args=(chat_server, usuarios,))
  ACCEPT_THREAD.start()
  ACCEPT_THREAD.join()
  chat_server.close()


start_chat_server()
#start_server_tcp()
#start_server_udp()
