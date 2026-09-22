from minilang.tokens import Token, TokenType

class Lexer:
    def __init__(self, fonte:str):
        self.fonte = fonte
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.tokens: list[Token] = []

    def _fim(self) -> bool:
        return self.pos >= len(self.fonte)

    def _peek(self, k:int = 0) -> str:
        i = self.pos + k
        return self.fonte[i] if i< len(self.fonte) else "\0"
        
    def _avancar(self) -> str:
        c = self.fonte[self.pos]
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    def _pular_espacos_e_comentarios(self) -> None:
        while not self._fim():
            c = self._peek()
            if c in " \t\r\n":
                self._avancar()
            elif c == "#":
                while not self._fim() and self._peek() != "\n":
                    self._avancar()
            else:
                break
    def tokenizar(self) -> list[Token]:
        while True:
            self._pular_espacos_e_comentarios()
            if self._fim():
                break
            linha, coluna = self.linha, self.coluna
            self._proximo_token(linha,coluna)

        self.tokens.append(Token(TokenType.EOF,"", self.linha, self.coluna))
        return self.tokens

    def _proximo_token(self,linha:int, coluna:int) -> None:
        self._avancar()
