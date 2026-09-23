from minilang.tokens import PALAVRAS_RESERVADAS, Token, TokenType

class Lexer:
    def __init__(self, fonte: str):
        self.fonte = fonte
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.tokens: list[Token] = []

    def _fim(self) -> bool:
        """True se já lemos todo o código-fonte."""
        return self.pos >= len(self.fonte)

    def _peek(self, k:int = 0) -> str:
        """Espia o caractere k posições à frente SEM consumi-lo."""
        i = self.pos + k
        return self.fonte[i] if i< len(self.fonte) else "\0"
        
    def _avancar(self) -> str:
        """Consome o caractere atual, atualiza linha/coluna e o devolve."""
        c = self.fonte[self.pos]
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c
    def _e_letra(self, c: str) -> bool:
        """Letra que pode INICIAR uma palavra (aceita acento, por causa de 'senão')."""
        return c.isalpha()

    def _e_digito(self, c: str) -> bool:
        """Dígito decimal. Não usamos c.isdigit() porque ele aceita '²' e outros."""
        return "0" <= c <= "9"

    def _e_parte_palavra(self, c: str) -> bool:
        """Caractere que pode CONTINUAR um identificador."""
        return self._e_letra(c) or self._e_digito(c) or c == "_"
    
    def _pular_espacos_e_comentarios(self) -> None:
        """Descarta espaços, tabulações, quebras de linha e comentários '#'."""
        while not self._fim():
            c = self._peek()
            if c in " \t\r\n":
                self._avancar()
            elif c == "#":
                while not self._fim() and self._peek() != "\n":
                    self._avancar()
            else:
                break

    # ------------------------------------------------------------------
    # Reconhecedores de token
    # ------------------------------------------------------------------

    def _ler_palavra(self, linha: int, coluna: int) -> None:
        """Lê letra (letra | dígito | _)* e decide: palavra reservada ou identificador."""
        inicio = self.pos
        while self._e_parte_palavra(self._peek()):
            self._avancar()
        lexema = self.fonte[inicio:self.pos]
        # consulta na tabela: se não estiver lá, é identificador
        tipo = PALAVRAS_RESERVADAS.get(lexema, TokenType.IDENT)
        self.tokens.append(Token(tipo, lexema, linha, coluna))

    def _ler_numero(self, linha: int, coluna: int) -> None:
        """Lê dígito+ e gera um literal inteiro."""
        inicio = self.pos
        while self._e_digito(self._peek()):
            self._avancar()
        lexema = self.fonte[inicio:self.pos]
        self.tokens.append(Token(TokenType.NUM_INT, lexema, linha, coluna))     

    # ------------------------------------------------------------------
    # Laço principal
    # ------------------------------------------------------------------

    

    def tokenizar(self) -> list[Token]:
        """Percorre todo o código-fonte e devolve a lista de tokens."""
        while True:
            self._pular_espacos_e_comentarios()
            if self._fim():
                break
            linha, coluna = self.linha, self.coluna
            self._proximo_token(linha,coluna)

        self.tokens.append(Token(TokenType.EOF,"", self.linha, self.coluna))
        return self.tokens

    def _proximo_token(self, linha: int, coluna: int) -> None:
        """Olha o primeiro caractere e decide qual token reconhecer."""
        c = self._peek()

        if self._e_letra(c):
            self._ler_palavra(linha, coluna)
        elif self._e_digito(c):
            self._ler_numero(linha, coluna)
        else:
            # PROVISÓRIO: operadores e delimitadores entram na etapa 4,
            # e os erros léxicos na etapa 5.
            self._avancar()
