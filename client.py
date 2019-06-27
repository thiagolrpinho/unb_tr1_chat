# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# Nesse módulo será desenvolvido o client udp
import time
import socket
import tkinter as tk
from threading import Thread

MAX_SERVERS = 50
LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP    # ENDEREÇO IP SERVIDOR
PORT = 3300        # PORTA DO SERVIDOR(CLIENTE ENVIA)
BUFF_SIZE = 1024
DESTINO = (HOST, PORT)

ROOT = tk.Tk()
CURRENT_FRAME = None
NOME = None
SALA = None
MENSAGEM = None
CHAT = None

CONEXAO = None
EXIT = False

def connect_to_server():
  global CONEXAO, EXIT

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
    CONEXAO.send(bytes(SALA.get(), "utf8"))
    time.sleep(.1)
    mensagem = CONEXAO.recv(BUFF_SIZE).decode("utf8")
    if mensagem != '':
      CHAT.config(state='normal')
      CHAT.insert('end', mensagem + '\n')
      CHAT.see('end')
      CHAT.config(state='disabled')
    CONEXAO.send(bytes(NOME.get(), "utf8"))
    time.sleep(.1)

  CHAT.config(state='normal')
  CHAT.insert('end', 'Servidor diz: Conectado!\n')
  CHAT.see('end')
  CHAT.config(state='disabled')

def chat_gui():
  global CURRENT_FRAME, MENSAGEM, CHAT, PORT, DESTINO, EXIT
  ROOT.title(NOME.get() + ' em: Sala ' + SALA.get())

  chatFrame = tk.Frame(ROOT, padx=10, pady=10)

  CHAT = tk.Text(chatFrame, state='disabled')
  MENSAGEM = tk.Entry(chatFrame, width=55)
  sendButton = tk.Button(chatFrame, text='Enviar', command=send_message)
  exitButton = tk.Button(chatFrame, text='Sair', command=quit_chat)

  MENSAGEM.bind('<Return>', send_message)

  CHAT.pack()
  MENSAGEM.pack(side='left')
  sendButton.pack(side='left')
  exitButton.pack(side='left')

  CURRENT_FRAME.pack_forget()

  chatFrame.pack()

  CURRENT_FRAME = chatFrame

  connect_to_server()

  receive_thread = Thread(target=receive_message, args=())
  receive_thread.start()

def start_gui():
  global CURRENT_FRAME, NOME, SALA
  ROOT.title('Login')

  loginFrame = tk.Frame(ROOT, padx=10, pady=10)

  loginLabel = tk.Label(loginFrame, text='Bem-Vindo!\n\nInsira seu nome de usuário\n e sua sala nos campos\na seguir:\n')
  nameLabel = tk.Label(loginFrame, text='Nome')
  NOME = tk.Entry(loginFrame)
  roomLabel = tk.Label(loginFrame, text='Sala')
  SALA = tk.Entry(loginFrame)
  spacer = tk.Label(loginFrame, text='')
  loginButton = tk.Button(loginFrame, text='Entrar', command=chat_gui)
  exitButton = tk.Button(loginFrame, text='Sair', command=tk._exit)

  loginLabel.grid(row=0, columnspan=2)
  nameLabel.grid(row=1, sticky='e')
  NOME.grid(row=1, column=1)
  roomLabel.grid(row=2, sticky='e')
  SALA.grid(row=2, column=1)
  spacer.grid(row=3)
  loginButton.grid(row=4, columnspan=2)
  exitButton.grid(row=4, columnspan=2, sticky='e')

  loginFrame.pack()

  CURRENT_FRAME = loginFrame

def receive_message():
  global CHAT, EXIT, DESTINO

  while not EXIT:
    mensagem = CONEXAO.recv(BUFF_SIZE).decode("utf8")
    if mensagem != '':
      print(mensagem)
      CHAT.config(state='normal')
      CHAT.insert('end', mensagem + '\n')
      CHAT.see('end')
      CHAT.config(state='disabled')
    else:
      connect_to_server()

  CHAT.config(state='normal')
  CHAT.insert('end', 'Servidor diz: Desconectado!\n')
  CHAT.see('end')
  CHAT.config(state='disabled')

def send_message(event = None):
  if MENSAGEM.get() == '{quit}':
    quit_chat()
  else:
    try:
      CONEXAO.send(bytes(MENSAGEM.get(), "utf8"))
    except:
      if EXIT:
        ROOT.quit()
    else:
      MENSAGEM.delete(0, 'end')

def quit_chat():
  global EXIT

  try:
    CONEXAO.send(bytes("{quit}", "utf8"))
    CONEXAO.close()
  except:
    pass

  EXIT = True
  ROOT.quit()

def main():
  start_gui()
  ROOT.mainloop()

if __name__ == '__main__':
  main()
