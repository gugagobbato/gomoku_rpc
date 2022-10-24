import os
import json
import time
import uuid
import xmlrpc.client
import tkinter as tk
from tkinter.messagebox import showinfo
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')
sys.path.insert(1, '../../')

from tabuleiro import Tabuleiro
from refresh_status import RefreshInterval

class StartGame:
    def __init__(self):
        super(StartGame, self).__init__()

#### ROTAS GLOBAIS - CLIENTE
root = tk.Tk()
nro_jogador = 0
nro_jogadores = 0
StartTime=time.time()
#### ROTAS GLOBAIS - CLIENTE

clientId = uuid.uuid4().hex
aguardando_oponente = True

srv_proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

ROOT_LOG = "\033[1;33mROOT: \033[0;0m"
ERROR_LOG = "\033[1;31mERROR: \033[0;0m"
RUNTIME_LOG = "\033[0;32mRUNTIME: \033[0;0m"
FUNCTION_LOG = "\033[0;35mFUNCTION: \033[0;0m"
FUNCTION_ARGS_LOG = "\033[0;35mFUNCTION_ARGS: \033[0;0m"

def iniciar_cliente():
    dados_rcv = json.loads(srv_proxy.conectar_cliente(clientId))
    global aguardando_oponente, nro_jogador
    
    try:
        nro_jogador = dados_rcv.get("nro_jogador")

        if (nro_jogador > 0):
            print(ROOT_LOG, "Conectado ao servidor com sucesso!")

            if nro_jogador == 1:
                print(RUNTIME_LOG, "Você é o primeiro a jogar.")
                aguardando_oponente = False
                #refreshInterval.cancel()
            else:
                print(RUNTIME_LOG, "Você é o segundo a jogar.")
        else:
            showinfo("Aviso!", "Ocorreu um erro ao tentar obter dados do servidor.")
            fechar_janela()
    except:
        showinfo("Aviso!", "Ocorreu um erro ao tentar obter dados do servidor.")
        fechar_janela()

def inserir_grid():
    global gameframe
    global i, j

    gameframe = tk.Frame(root)
    gameframe.pack()

    renderizar_grid()

def renderizar_grid(board_in = None):
    board_temp = tabuleiro.get_tabuleiro()
    if board_in != None: board_temp = board_in

    linhas = len(board_temp)
    colunas = len(board_temp[0])

    for i in range(linhas):
        for j in range(colunas):
            labels_grid = tk.Label(gameframe, text="      ", bg= "white" if board_temp[i][j] == 0 else "gray" if board_temp[i][j] == 1 else "black")
            labels_grid.grid(row=i, column=j, padx='6', pady='6')
            labels_grid.bind('<Button-1>', lambda e, i=i, j=j: on_click_grid(i, j, e))

def obter_status_servidor(i = None, j = None):
    global aguardando_oponente, nro_jogadores, nro_jogador

    dados_rcv = json.loads(srv_proxy.obter_status_servidor(clientId, i, j))
    nro_jogadores_recv = dados_rcv.get("nro_jogadores")
    fim_jogo_recv = bool(dados_rcv.get("fim_jogo"))
    i_recv = dados_rcv.get("i")
    j_recv = dados_rcv.get("j")

    if (i != None):
        if nro_jogadores > nro_jogadores_recv:
            showinfo("Aviso!", "O outro jogador deixou a partida. O jogo será encerrado. :/")
            fechar_janela(False)

        if nro_jogadores_recv != None and nro_jogadores_recv > 1:
            aguardando_oponente = not bool(dados_rcv.get("pode_jogar"))

        if fim_jogo_recv:
            if aguardando_oponente:
                showinfo("FIM DE JOGO!", "Seu oponente venceu! :/")
            else:
                showinfo("FIM DE JOGO!", "Você venceu! :)")

            fechar_janela()
    else:
        if i_recv != None:
            tabuleiro_temp = tabuleiro.get_tabuleiro()
            tabuleiro_temp[i_recv][j_recv] = 2 if nro_jogador != 1 else 1
            tabuleiro.set_tabuleiro(tabuleiro_temp)
            aguardando_oponente = False
            renderizar_grid()

def on_click_grid(i, j, event):
    global nro_jogador

    if not aguardando_oponente:
        if tabuleiro[i][j] == 0:
            color = "gray" if nro_jogador % 2 else "black"  # Famoso ternário do PYTHON :)
            event.widget.config(bg=color)
        elif tabuleiro[i][j] != nro_jogador:
             showinfo("Aviso!", "Essa posição já foi selecionada!")
             return

        dados_rcv = obter_status_servidor(i, j)

        if not bool(dados_rcv.get("sucesso")):
            showinfo("Aviso!", "Erro ao registrar jogada no servidor.")
            fechar_janela()
    else:
        showinfo("Aviso!", "Aguardando oponente.")

def configurar_janela():
    if os.path.isdir("themes/icons/"):
        root.iconbitmap(bitmap='../../themes/icons/Gomoku.ico')

    root.winfo_toplevel().title("Socket's Gomoku")

def fechar_janela(mostrar_msg_saida = True, confirmar_saida = True, call_destroy = True):
    if refreshInterval.getStatus():
         refreshInterval.cancel()

    if mostrar_msg_saida:
        showinfo("Aviso!", "O jogo (cliente) será encerrado.")

    if confirmar_saida:
        srv_proxy.desconectar_cliente(clientId)

    if call_destroy:
        root.destroy()

def monitorar_fechamento_janela():
    fechar_janela(False, True, False)

def configurar_mainloop_calls():
    root.geometry("700x700")
    root.mainloop()

    monitorar_fechamento_janela()

def action() :
    obter_status_servidor()

tabuleiro = Tabuleiro()

configurar_janela()
iniciar_cliente()
refreshInterval = RefreshInterval(0.5, action)

inserir_grid()