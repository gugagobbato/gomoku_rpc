import json
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../../')

from xmlrpc.server import SimpleXMLRPCServer

from tabuleiro import Tabuleiro

ROOT_LOG = "\033[1;33mROOT: \033[0;0m"
ERROR_LOG = "\033[1;31mERROR: \033[0;0m"
RUNTIME_LOG = "\033[0;32mRUNTIME: \033[0;0m"
FUNCTION_LOG = "\033[0;35mFUNCTION: \033[0;0m"
FUNCTION_ARGS_LOG = "\033[0;35mFUNCTION_ARGS: \033[0;0m"

nr_clientes = 0
id_clientes = []

end_game = False
fim_jogo = False
jogo_iniciado = False
tabuleiro = Tabuleiro()
cliente_desconectado = False
primeiro_jogador_aguardando = False

iTemp = jTemp = None

def conectar_cliente(clientId):
    global jogo_iniciado, nr_clientes

    if not clientId in id_clientes:
        nr_clientes+=1
        id_clientes.append(clientId)
        if nr_clientes > 1: jogo_iniciado = True
        print(ROOT_LOG, f"Cliente {clientId} conectado.")
        print(ROOT_LOG, "Clientes conectados:", nr_clientes)

        if nr_clientes > 2:
            print(ERROR_LOG, "Número máximo de jogadores atingido para este servidor. O mesmo está sendo encerrado agora.")
            print(">>>>>>  Por favor, pressione 'CTRL + BREAK' para sair.")
            server.server_close()
            server.shutdown()
            exit(1)

        return json.dumps({"nro_jogador": nr_clientes})

def desconectar_cliente(clientId):
    global jogo_iniciado, nr_clientes, cliente_desconectado, primeiro_jogador_aguardando, fim_jogo

    nr_clientes = nr_clientes - 1 if nr_clientes > 0 else 0

    print(ROOT_LOG, f"Cliente {clientId} desconectado.")
    print(ROOT_LOG, "Clientes conectados:", nr_clientes)

    if nr_clientes < 1:
        fim_jogo = False
        id_clientes.clear()

    if nr_clientes < 2:
        if jogo_iniciado:
            if id_clientes.index(clientId):
                id_clientes.remove(clientId)
            
            resetGame()
            jogo_iniciado = False
            cliente_desconectado = True
            primeiro_jogador_aguardando = False
            print(RUNTIME_LOG, "Reiniciando partida...")

def resetGame():
    tabuleiro.reset_tabuleiro()

def obter_status_servidor(clientId, i, j):
    index_jogador = id_clientes.index(clientId) + 1
    global iTemp, jTemp, cliente_desconectado, primeiro_jogador_aguardando, fim_jogo

    if fim_jogo:
        return json.dumps({"nro_jogadores": nr_clientes, "sucesso": True, "pode_jogar": False, "fim_jogo": fim_jogo})

    if cliente_desconectado:
        cliente_desconectado = False
        return json.dumps({"nro_jogadores": nr_clientes, "sucesso": True, "pode_jogar": False, "fim_jogo": fim_jogo})

    if jogo_iniciado:
        if (i != None):
            verificacao_tabuleiro = tabuleiro.verificar_tabuleiro(i, j, index_jogador)
            if verificacao_tabuleiro:
                fim_jogo = True
                return json.dumps({"nro_jogadores": nr_clientes, "sucesso": True, "pode_jogar": False, "fim_jogo": fim_jogo})

            if primeiro_jogador_aguardando and index_jogador == 2 or not primeiro_jogador_aguardando and index_jogador == 1:
                tabuleiro_temp = tabuleiro.get_tabuleiro()
                
                if tabuleiro_temp[i][j] == 0:                    

                    tabuleiro_temp[i][j] = index_jogador
                    iTemp = i
                    jTemp = j

                    if index_jogador == 1: 
                        primeiro_jogador_aguardando = True
                    else: 
                        primeiro_jogador_aguardando = False

                    return json.dumps({"nro_jogadores": nr_clientes, "sucesso": True, "pode_jogar": False, "fim_jogo": False})
                else:
                    return json.dumps({"nro_jogadores": nr_clientes, "sucesso": False, "pode_jogar": True, "fim_jogo": False})
    
    retorno = json.dumps({"i": iTemp, "j": jTemp, "nro_jogadores": len(id_clientes), "sucesso": False, "pode_jogar": False, "fim_jogo": False})
    if iTemp != None: iTemp = jTemp = None

    return retorno

# INÍCIO - LÓGICA RPC SERVIDOR

server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)

server.register_function(conectar_cliente, "conectar_cliente")
server.register_function(desconectar_cliente, "desconectar_cliente")
server.register_function(obter_status_servidor, "obter_status_servidor")

server.serve_forever()

# FIM - LÓGICA RPC SERVIDOR
