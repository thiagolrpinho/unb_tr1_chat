# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

import socket
# É uma biblioteca python voltada para a interface de soquetes(TCP/UDP).
LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP # ENDEREÇO IP DO HOST
PORT = 3300        # PORTA DO SERVIDOR(SERVIDOR ESCUTA)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
orig = (HOST, PORT)
udp.bind(orig)     # Bind the socket to address

while True:
  msg, cliente = udp.recvfrom(1024)
  print(cliente, msg)
udp.close()
