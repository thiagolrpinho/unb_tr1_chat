# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

import socket
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
    print("Conectado por" + cliente)

    while True:
      bytes_recebidos, cliente = con.recvfrom(1024) # Retorna o buffer e o endereço IP de origem
      mensagem_recebida = bytes_recebidos.decode("utf8") 
      print(cliente, mensagem_recebida)
    print("Finalizando")
    con.close()

start_server_tcp()
#start_server_udp()
