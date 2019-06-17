# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# Nesse módulo será desenvolvido o client udp
import socket

LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP    # ENDEREÇO IP SERVIDOR
PORT = 3300        # PORTA DO SERVIDOR(CLIENTE ENVIA)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)
print("Para sair aperte CTRL+X")
msg = input()
while msg != ' ':
  udp.sendto(bytes(msg, 'utf8'), dest)
  msg = input()
udp.close