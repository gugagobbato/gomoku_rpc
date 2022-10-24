class Tabuleiro :
    def __init__(self) :
        self.board = [[0] * 15 for _ in range(15)]
        self.utils = TabuleiroUtils()
    def set_tabuleiro(self, board):
        self.board = board
    def get_tabuleiro(self):
        return self.board

    def verificar_tabuleiro(self, i, j, nro_jogador):
        verificacao_linha = verificacao_coluna = verificacao_diagonal = False

        if self.utils.verificar_linha(i, nro_jogador, board=self.board):
            verificacao_linha = True
        if self.utils.verificar_coluna(j, nro_jogador, board=self.board):
            verificacao_coluna = True
        if self.utils.verificar_diagonal(nro_jogador, board=self.board):
            verificacao_diagonal = True

        return verificacao_linha and verificacao_coluna and verificacao_diagonal

class TabuleiroUtils :
    def verificar_linha(i, nro_jogador, board):
        b = 0
        count = 0
        total = 14
        while b <= total:
            if board[i][b] == nro_jogador:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0
            b += 1

        return False

    def verificar_coluna(j, nro_jogador, board):
        b = 0
        count = 0
        total = 14
        while b <= total:
            if board[b][j] == nro_jogador:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0
            b += 1
        return False

    def verificar_diagonal(nro_jogador, board):
        max_col = len(board[0])
        max_row = len(board)
        fdiag = [[] for _ in range(max_row + max_col - 1)]
        bdiag = [[] for _ in range(len(fdiag))]
        min_bdiag = -max_row + 1

        for x in range(max_col):
            for y in range(max_row):
                fdiag[x + y].append(board[y][x])
                bdiag[x - y - min_bdiag].append(board[y][x])

        count = 0
        for vetor in bdiag:
            for item in vetor:
                if item == nro_jogador:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0

        for vetor in fdiag:
            for item in vetor:
                if item == nro_jogador:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0

        return False