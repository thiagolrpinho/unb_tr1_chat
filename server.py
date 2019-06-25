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
      try : socket.send(bytes(autor  + " diz: ","utf8") + mensagem_a_transmitir )
      except BrokenPipeError: 
          socket.close()
      except OSError:
          socket.close()

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

def start_chat_multi_server():
  servidores = []
  enderecos_para_escutar = [ (HOST, PORT), (HOST, PORT + 1)]
  usuarios = dict()
  for endereco in enderecos_para_escutar:
    servidores.append(SERVIDOR(endereco, usuarios))
  
  servidores[0].set_primario(True)
  servidores[0].adiciona_servidor_auxiliar()
  servidores[1].auxilia_servidor_primario((HOST, PORT))

  print("Que porra")
  for servidor in servidores:
    servidor.set_servidor_online()

  servidores[1].espera_thread()
  


class SERVIDOR():
  ''' Essa classe descreve o comportamento e armazena as variáveis relacionados ao 
  servidor do chat, ele pode ser primário ou não. O sevidor primário recebe as mensagens
  dos usuários e transmite de volta. Os servidores não primários apenas recebem informação
  dos nicknames e suas respectivas salas do servidor primário. Quando um servidor não primário
  recebe uma mensagem de um usuário, isso significa que o primário caiu e agora ele passa a ser
  o primário. '''
  def __init__(self, endereco_da_porta, salas_de_usuarios, primario = False, numero_de_usuarios_maximo = 5 ):
    ''' Construtor precisa obrigatoriamente do endereco e das salas. Ele também pode ser configurado para ser ou não primário.
    E o número máximo de usuário desejado'''
    self.primario = primario # Somente o primário recebe mensagens e dá broadcast
    self.salas_de_usuarios = salas_de_usuarios # Uma lista de hashs com o nickname e o soquete de cada usuário
    self.servidores_auxiliares = []
    self.thread_com_usuarios = None

    self.soquete_da_porta = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria um objeto para encapsular o protocolo TCP
    self.soquete_de_transmissao = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Esse soquete será usado para se comunicar com outros servidores\
    PORTA_LIVRE = False
    while not PORTA_LIVRE:
      try: 
        self.soquete_da_porta.bind(endereco_da_porta)     # Esse soquete estará ligado a esse endereço
        PORTA_LIVRE = True
      except OSError as e:
        print(f"Porta em uso: {e}")   
    self.soquete_da_porta.listen(numero_de_usuarios_maximo)  ## escuta no máximo esse número de conexões


  def __del__(self):
    ''' Destrutor '''
    self.soquete_da_porta.close() 

  def espera_thread(self):
    ''' Faz com que o servidor em questão segure o andamento do código até essa 
    thread acabar '''
    self.thread_com_usuarios.join()
  
  def set_primario(self, primario = True):
    ''' Muda o estado para primário verdadeiro ou para o argumento passado no parâmetro'''
    if primario:
      self.contagem = 0
    self.primario = primario

  def is_primario(self):
    ''' Retorna se o servidor é ou não primário'''
    return self.primario

  def set_servidor_online(self):
  # Cria uma thread com a função recebe_usuario e essa fica em um loop infinito recebendo usuários
    self.thread_com_usuarios = Thread(target=self.servidor_online, args=(self.soquete_da_porta, self.salas_de_usuarios,))
    self.thread_com_usuarios.setDaemon(False) # Isso faz com que essa thread e as demais que ela chamar sejam fechadas quando o programa fechar
    self.thread_com_usuarios.start()

  def servidor_online(self, chat_server, usuarios):
    ''' Liga o servidor e fica escutando por novas conexões de usuários '''
    print(f"Servidor {self} online")
    enderecos = dict()
    if self.primario:
      self.contagem = 0
    else: 
      self.contagem = 3

    while self.contagem > 0:
      print(f"{self} Contagem: {self.contagem}")      
      usuario, endereco_usuario = chat_server.accept()
      if self.primario:
        print("Conectado como primário a " + str(endereco_usuario[0]) + ':' + str(endereco_usuario[1]))
        usuario.send(bytes("Bem-vindo! "+
                          "Escreva seu nome e aperte enter!", "utf8"))
        enderecos[usuario] = endereco_usuario
        nickname = usuario.recv(1024).decode("utf8")
        welcome = 'Para sair digite {quit} e aperte enter'
        usuario.send(bytes(welcome, "utf8"))
        mensagem = "%s se juntou ao chat" % nickname
        self.broadcast_servidores(endereco_usuario)
        broadcast(usuarios, bytes(mensagem, "utf8"))
        usuarios[usuario] = nickname
        Thread(target=self.conexao_usuario, args=(chat_server, usuarios, usuario)).start()
      else:
        print("Conectado como não primário a " + str(endereco_usuario[0]) + ':' + str(endereco_usuario[1]))
        Thread(target=self.conexao_usuario, args=(chat_server, usuarios, usuario)).start()

    self.set_primario(False)
    self.soquete_da_porta.close()
    print(f"Desligando servidor {self}")
  
  def conexao_usuario(self, chat_server, usuarios, usuario):
    ''' Conecta o servidor a um usuário, recebendo mensagens desses e dando broadcast para os demais membros da sala'''
    bytes_recebidos = usuario.recv(1024)
    while str(bytes_recebidos, encoding='utf8') != '{quit}':
      self.set_primario()
      print(str(bytes_recebidos, encoding='utf8'))
      try: 
        broadcast(usuarios, bytes_recebidos, usuarios[usuario])
        bytes_recebidos = usuario.recv(1024) # Retorna o buffer e o endereço IP de origem
      except OSError: 
        break
      except KeyError:
        break

    usuario.close()
    self.contagem = self.contagem -1
    try:  # CORRIGIR FATO DOS SERVIDORES ESTAREM COMPARTILHANDO VARIAVEL GLOBAL(NÃO POSSÍVEL EM SERVIDORES EM MÁQUINAS DIFERENTES)
      broadcast(usuarios, bytes("%s está sem tempo, irmão." % usuarios[usuario], "utf8"))
      del usuarios[usuario]
    except:
      pass
    
  def broadcast_servidores(self, mensagem_a_transmitir):
    '''Método para comunicação entre servidores '''
    mensagem_a_transmitir = str(mensagem_a_transmitir)
    if self.servidores_auxiliares:
      for soquete in self.servidores_auxiliares: 
        try : soquete.send(bytes(mensagem_a_transmitir, 'utf8') )
        except BrokenPipeError: 
            soquete.close()
        except OSError:
            soquete.close()

  def adiciona_servidor_auxiliar(self):
    '''Método que cria uma thread para receber a conexão de um servidor auxiliar e armazena na lista de servidores auxiliares '''
    Thread(target=self.recebe_servidor_auxiliar).start()

  def recebe_servidor_auxiliar(self):
    servidor, endereco_servidor = self.soquete_da_porta.accept()
    print("Auxiliar recebido com sucesso")
    self.servidores_auxiliares.append(servidor)

  
  def auxilia_servidor_primario(self, endereco_servidor_primario):
    ''' O servidor auxiliar pede para o primário para ser adicionado à sua lista de broadcast de servidores'''
    self.soquete_de_transmissao.connect(endereco_servidor_primario)
    print("Conectado ao primário")
    receive_thread = Thread(target=self.recebe_mensagem)
    receive_thread.start()
  
  def recebe_mensagem(self):
    ''' Método usado para receber os usuários conectados ao servidor primário'''
    while not self.primario:
      try: 
        mensagem = self.soquete_de_transmissao.recv(1024).decode("utf8")
        print(f"{mensagem}")
      except OSError: 
        return None

        
      


start_chat_multi_server()
#start_chat_server()
#start_server_tcp()
#start_server_udp()
