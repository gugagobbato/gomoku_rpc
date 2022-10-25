from glob import glob
import json
import os
import sys
import time
import tkinter as tk
import uuid
import xmlrpc.client
from tkinter.messagebox import showinfo

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')
sys.path.insert(2, '../../')

from tabuleiro import Tabuleiro

from refresh_status import RefreshInterval

#### ROTAS GLOBAIS - CLIENTE
root = tk.Tk()
nro_jogador = 0
nro_jogadores = 0
#### ROTAS GLOBAIS - CLIENTE

clientId = uuid.uuid4().hex
aguardando_oponente = True
status_cliente = tk.StringVar()
status_cliente.set('')

srv_proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

ROOT_LOG = "\033[1;33mROOT: \033[0;0m"
ERROR_LOG = "\033[1;31mERROR: \033[0;0m"
RUNTIME_LOG = "\033[0;32mRUNTIME: \033[0;0m"
FUNCTION_LOG = "\033[0;35mFUNCTION: \033[0;0m"
FUNCTION_ARGS_LOG = "\033[0;35mFUNCTION_ARGS: \033[0;0m"

def iniciar_cliente():
    dados_rcv = json.loads(srv_proxy.conectar_cliente(clientId))
    global nro_jogador, refreshInterval
    
    try:
        nro_jogador = dados_rcv.get("nro_jogador")

        if (nro_jogador > 0):
            print(ROOT_LOG, "Conectado ao servidor com sucesso!")
            refreshInterval = RefreshInterval(0.01, action)

            if nro_jogador == 1:
                print(RUNTIME_LOG, "Você é o primeiro a jogar.")
                atualizar_situacao_cliente(False)
                refreshInterval.cancel_interval()
            else:
                print(RUNTIME_LOG, "Você é o segundo a jogar.")
                atualizar_situacao_cliente(True)
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

    tabuleiro_temp = tabuleiro.get_tabuleiro()

    linhas = len(tabuleiro_temp)
    colunas = len(tabuleiro_temp[0])

    for i in range(linhas):
        for j in range(colunas):
            atualizar_posicao_grid(i, j, tabuleiro_temp)

def atualizar_situacao_cliente(aguardando):
    global aguardando_oponente

    aguardando_oponente = aguardando
    status_cliente.set("STATUS CLIENTE: sua vez de jogar." if not aguardando else "STATUS CLIENTE: aguardando oponente.")

def atualizar_posicao_grid(i, j, board_in = None):
    tabuleiro_temp = board_in if board_in != None else tabuleiro.get_tabuleiro()

    labels_grid = tk.Label(gameframe, text="      ", bg= "white" if tabuleiro_temp[i][j] == 0 else "gray" if tabuleiro_temp[i][j] == 2 else "black")
    labels_grid.grid(row=i, column=j, padx='6', pady='6')
    labels_grid.bind('<Button-1>', lambda e, i=i, j=j: on_click_grid(i, j, e))

def obter_status_servidor(i = None, j = None):
    global nro_jogadores, nro_jogador

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
            atualizar_situacao_cliente(not bool(dados_rcv.get("pode_jogar")))

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
            atualizar_posicao_grid(i_recv, j_recv)
            atualizar_situacao_cliente(False)

            if refreshInterval.get_status():
                refreshInterval.cancel_interval()
            
    return dados_rcv

def on_click_grid(i, j, event):
    global nro_jogador
    tabuleiro_temp = tabuleiro.get_tabuleiro()
    backup_jogada = tabuleiro_temp[i][j]

    if not aguardando_oponente:
        if tabuleiro_temp[i][j] == 0:
            color = "gray" if nro_jogador == 1 else "black"  # Famoso ternário do PYTHON :)
            event.widget.config(bg=color)
            tabuleiro_temp[i][j] = nro_jogador
        elif tabuleiro_temp[i][j] != nro_jogador:
             showinfo("Aviso!", "Essa posição já foi selecionada!")
             return

        dados_rcv = obter_status_servidor(i, j)
        sucesso = dados_rcv.get("sucesso")

        if not bool(sucesso):
            showinfo("Aviso!", "Erro ao registrar jogada no servidor.")
            tabuleiro_temp[i][j] = backup_jogada
            atualizar_posicao_grid(i, j)
            #fechar_janela()
        else:
            tabuleiro.set_tabuleiro(tabuleiro_temp)
            if not refreshInterval.get_status():
                refreshInterval.restart_interval()
    else:
        showinfo("Aviso!", "Aguardando oponente.")

def configurar_janela():
    global status_cliente

    if os.path.isdir("../../../themes/icons/"):
        root.iconbitmap(bitmap='../../../themes/icons/Gomoku.ico')

    root.winfo_toplevel().title("RPC's Gomoku")

    tk.Label(root, 
		 text="RPC's Gomoku",
		 fg = "blue",
         bg = "light green",
		 font = "Verdana 25 bold").pack(pady="20")
    tk.Label(root, 
		 text="JOGADOR nº: " + str(nro_jogador),
		 fg = "green",
		 font = "Verdana 10 bold").pack(side="bottom", pady="15")
    tk.Label(root, 
		 textvariable = status_cliente,
		 fg = "green",
		 font = "Verdana 10 bold").pack(side="bottom", pady="15")

def fechar_janela(mostrar_msg_saida = True, confirmar_saida = True, call_destroy = True):
    if refreshInterval.get_status():
         refreshInterval.cancel_interval()

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

iniciar_cliente()
configurar_janela()

inserir_grid()
configurar_mainloop_calls()
