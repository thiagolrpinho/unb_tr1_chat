# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# Nesse módulo será desenvolvido o client udp
import socket
from threading import Thread

MAX_SERVERS = 50
LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP    # ENDEREÇO IP SERVIDOR
PORT = 3300        # PORTA DO SERVIDOR(CLIENTE ENVIA)
BUFF_SIZE = 1024
DESTINO = (HOST, PORT)

NOME = None
SALA = None

CONEXAO = None
EXIT = False

def connect_to_server():
  global CONEXAO, EXIT, DESTINO

  try:
    CONEXAO.close()
  except:
    pass
  finally:
    CONEXAO = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    EXIT = True
    for i in range(MAX_SERVERS):
      DESTINO = (HOST, PORT + i)
      try:
        CONEXAO.connect(DESTINO)
      except:
        pass
      else:
        EXIT = False
        break

  if not EXIT:
    CONEXAO.send(bytes(SALA, "utf8"))
    mensagem = CONEXAO.recv(BUFF_SIZE).decode("utf8")
    if mensagem != '':
      print(mensagem)
    CONEXAO.send(bytes(NOME, "utf8"))

  print('Servidor diz: Conectado!\n')

def receive_message():
  global EXIT, DESTINO

  while not EXIT:
    mensagem = CONEXAO.recv(BUFF_SIZE).decode("utf8")
    if mensagem != '':
      print(mensagem)
    else:
      connect_to_server()

  print('Servidor diz: Desconectado!\n')

def send_message(mensagem):
  if mensagem == '{quit}':
    quit_chat()
  else:
    try:
      CONEXAO.send(bytes(mensagem, "utf8"))
    except:
      if EXIT:
        raise SystemExit

def quit_chat():
  global EXIT

  try:
    CONEXAO.send(bytes("{quit}", "utf8"))
    CONEXAO.close()
  except:
    pass

  EXIT = True
  raise SystemExit

def main():
  global NOME, SALA
  print('Digite seu nome:')
  NOME = input()
  print('Digite o número da sala:')
  SALA = input()
  connect_to_server()
  receive_thread = Thread(target=receive_message, args=())
  receive_thread.start()
  print('Bem-Vindo! Para sair digite {quit}')
  while True:
    send_message(input())

if __name__ == '__main__':
  main()
