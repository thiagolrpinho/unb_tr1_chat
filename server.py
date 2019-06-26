# Código desenvolvido para a matéria de Teleinformática e Redes I de 2019.1
# da Universidade de Brasília
# O Objetivo do projeto é criar um chat multi-servidores com diversos usuários

# É uma biblioteca python voltada para a interface de soquetes(TCP/UDP).
import socket
from threading import Thread
import random

LOCAL_IP = '127.0.0.1'
HOST = LOCAL_IP  # ENDEREÇO IP DO HOST
PORT = 3300        # PORTA DO SERVIDOR(SERVIDOR ESCUTA)
BUFF_SIZE = 1024
MAX_USERS = 5

def start_chat_multi_server():
  servidores = []
  endereco_para_escutar = (HOST, PORT + random.randint(0,500))
  print(endereco_para_escutar)
  servidor = SERVIDOR(endereco_para_escutar)

  # Depois disso, ligamos o servidor
  servidor.set_servidor_online()

  # Depois pedimos ao servidores auxiliares para se conectarem ao primário
  servidor.espera_thread()
  


class SERVIDOR():
  ''' Essa classe descreve o comportamento e armazena as variáveis relacionados ao 
  servidor do chat, ele pode ser primário ou não. O sevidor primário recebe as mensagens
  dos usuários e transmite de volta. Os servidores não primários apenas recebem informação
  dos nicknames e suas respectivas salas do servidor primário. Quando um servidor não primário
  recebe uma mensagem de um usuário, isso significa que o primário caiu e agora ele passa a ser
  o primário. '''
  def __init__(self, endereco_da_porta, numero_de_usuarios_maximo = 5 ):
    ''' Construtor precisa obrigatoriamente do endereco e das salas. Ele também pode ser configurado para ser ou não primário.
    E o número máximo de usuário desejado'''
    self.salas_de_usuarios = dict() # Uma lista de hashs com o nickname e o soquete de cada usuário
    self.servidores_auxiliares = [] # Aqui serão listados quais servidores auxiliares devem ser informados sobre os novos usuários
    self.buffer_nicknames_salas = [] # Aqui serão armazenadas por ordem de chegada os usuários do chat que o servidor primário informou
    self.thread_com_usuarios = None # Para melhor controlar a comunicação com os usuários, vamos armazenar a thread
    self.is_online = False # Flag para controlar as threads do servidor
    self.soquete_da_porta = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria um objeto para encapsular o protocolo TCP
    self.soquete_de_transmissao = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Esse soquete será usado para se comunicar com outros servidores\
    
    PORTA_LIVRE = False
    while not PORTA_LIVRE:
      try: 
        self.soquete_da_porta.bind(endereco_da_porta)     # Esse soquete estará ligado a esse endereço
        PORTA_LIVRE = True
      except OSError as e:
        print("Porta em uso: " + e)   
    self.soquete_da_porta.listen(numero_de_usuarios_maximo)  ## escuta no máximo esse número de conexões


  def __del__(self):
    ''' Destrutor '''
    self.soquete_da_porta.close() 
    self.soquete_de_transmissao.close()

  def espera_thread(self):
    ''' Faz com que o servidor em questão segure o andamento do código até essa 
    thread acabar '''
    self.thread_com_usuarios.join()
  
  def set_servidor_online(self):
    '''Cria uma thread com a função recebe_usuario e essa fica em um loop infinito recebendo usuários'''
    self.is_online = True
    self.thread_com_usuarios = Thread(target=self.servidor_online, args=())
    self.thread_com_usuarios.setDaemon(False) # Isso faz com que essa thread e as demais que ela chamar sejam fechadas
    # quando a thread ou programa acima dele fechar
    self.thread_com_usuarios.start() # Começa a thread

  def servidor_online(self):
    ''' Liga o servidor e fica escutando por novas conexões de usuários '''
    soquete_do_servidor = self.soquete_da_porta
    threads_conexoes_usuarios = []

    while self.is_online: # O servidor deve fechar quando a contagem acabar para podermos simularmos a queda
      usuario, endereco_usuario = soquete_do_servidor.accept()
      print("Conectado como primário a " + str(endereco_usuario[0]) + ':' + str(endereco_usuario[1]))
      usuario.send(bytes("Bem-vindo! "+
                        "Escreva seu nome e aperte enter!", "utf8"))
      nickname = usuario.recv(1024).decode("utf8")
      welcome = 'Para sair digite {quit} e aperte enter'
      usuario.send(bytes(welcome, "utf8"))
      mensagem = "%s se juntou ao chat" % nickname
      self.broadcast_servidores(endereco_usuario)
      self.salas_de_usuarios[usuario] = nickname
      self.broadcast(bytes(mensagem, "utf8"))
      threads_conexoes_usuarios.append(Thread(target=self.conexao_usuario, args=(usuario,)))
      threads_conexoes_usuarios[-1].start()

    self.soquete_da_porta.close()
    self.is_online = False
    print("Desligando servidor {}".format(self))
  
  def conexao_usuario(self, usuario):
    ''' Conecta o servidor a um usuário, recebendo mensagens desses e dando broadcast para os demais membros da sala'''
    try: 
      bytes_recebidos = usuario.recv(1024)
    except OSError:
      del self.salas_de_usuarios[usuario]
      usuario.close()
    while str(bytes_recebidos, encoding='utf8') != '{quit}' and self.is_online:
      print("recebeu {}".format(self) + str(bytes_recebidos, encoding='utf8') + "de {}".format(usuario))
      try: 
        self.broadcast(bytes_recebidos, self.salas_de_usuarios[usuario])
        bytes_recebidos = usuario.recv(1024)
      except OSError: 
        break
      except KeyError:
        break

    usuario.close()
    self.broadcast(bytes("%s está sem tempo, irmão." % self.salas_de_usuarios[usuario], "utf8"))
    del self.salas_de_usuarios[usuario]

  def broadcast(self, mensagem_a_transmitir, autor = "Servidor "):
    if self.salas_de_usuarios:
      for socket in self.salas_de_usuarios: 
        try : 
          socket.send(bytes(autor  + " diz: ","utf8") + mensagem_a_transmitir )
          #print("Broadcast de {}".format(self) + "para {}".format(socket) + "do seguinte: {}".format(mensagem_a_transmitir))
        except BrokenPipeError: 
            socket.close()
        except OSError:
            socket.close()


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
    ''' Método usado para receber mensagens do servidor primário com os nicknames e salas dos usuários recém conectados'''

    while self.is_online:
      try: 
        mensagem = self.soquete_de_transmissao.recv(1024).decode("utf8")
      except OSError: 
        break
      self.buffer_nicknames_salas.append(mensagem)

        
      


start_chat_multi_server()
#start_chat_server()
#start_server_tcp()
#start_server_udp()
