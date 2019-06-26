# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# Nesse módulo será desenvolvido o client udp
import socket
import tkinter as tk
from threading import Thread

LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP    # ENDEREÇO IP SERVIDOR
PORT = 3300        # PORTA DO SERVIDOR(CLIENTE ENVIA)
BUFF_SIZE = 1024
CONEXAO = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
DESTINO = (HOST, PORT)
ROOT = tk.Tk()
CURRENT_FRAME = None
NOME = None
SALA = None
MENSAGEM = None
CHAT = None

def chat_gui():
  global CURRENT_FRAME
  global MENSAGEM
  global CHAT
  ROOT.title(NOME.get() + ' em: Sala ' + SALA.get())

  chatFrame = tk.Frame(ROOT, padx=10, pady=10)

  CHAT = tk.Text(chatFrame, state=tk.DISABLED)
  MENSAGEM = tk.Entry(chatFrame, width=55)
  sendButton = tk.Button(chatFrame, text='Enviar', command=send_message)
  exitButton = tk.Button(chatFrame, text='Sair', command=quit_chat)

  MENSAGEM.bind('<Return>', send_message)

  CHAT.pack()
  MENSAGEM.pack(side=tk.LEFT)
  sendButton.pack(side=tk.LEFT)
  exitButton.pack(side=tk.LEFT)

  CURRENT_FRAME.pack_forget()

  chatFrame.pack()

  CURRENT_FRAME = chatFrame

  CONEXAO.connect(DESTINO)
  receive_thread = Thread(target=receive_message, args=())
  receive_thread.start()


def start_gui():
  global CURRENT_FRAME
  global NOME
  global SALA
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
  nameLabel.grid(row=1, sticky=tk.E)
  NOME.grid(row=1, column=1)
  roomLabel.grid(row=2, sticky=tk.E)
  SALA.grid(row=2, column=1)
  spacer.grid(row=3)
  loginButton.grid(row=4, columnspan=2)
  exitButton.grid(row=4, columnspan=2, sticky=tk.E)

  loginFrame.pack()

  CURRENT_FRAME = loginFrame

def receive_message():
  global CHAT

  while True:
    try: mensagem = CONEXAO.recv(BUFF_SIZE).decode("utf8")
    except OSError: break
    CHAT.config(state=tk.NORMAL)
    CHAT.insert(tk.END, mensagem + '\n')
    CHAT.see('end')
    CHAT.config(state=tk.DISABLED)

def send_message(event = None):
  CONEXAO.send(bytes(MENSAGEM.get(), "utf8"))
  MENSAGEM.delete(0, 'end')

def quit_chat():
  CONEXAO.send(bytes("{quit}", "utf8"))
  CONEXAO.close()
  CURRENT_FRAME.destroy()
  ROOT.destroy()

def start_chat_user():
  start_gui()
  ROOT.mainloop()

start_chat_user()
