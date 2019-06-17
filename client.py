# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# Nesse módulo será desenvolvido o client udp
import socket

LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP    # ENDEREÇO IP SERVIDOR
PORT = 3300        # PORTA DO SERVIDOR(CLIENTE ENVIA)

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

start_cliente_tcp()
#start_cliente_udp()