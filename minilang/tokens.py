from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):

    # --- Palavras reservadas (especificação mínima) ---
    PROGRAMA = auto()
    VAR = auto()
    INTEIRO = auto()
    BOOLEANO = auto()
    SE = auto()
    SENAO = auto()
    ENQUANTO = auto()
    ESCREVA = auto()
    LEIA = auto()
    VERDADEIRO = auto()
    FALSO = auto()
    E = auto()
    OU = auto()
    NAO = auto()
    FIM = auto()
    # --- Palavras reservadas da extensão D (para, repita/ate) ---
    PARA = auto()
    ATE = auto()
    PASSO = auto()
    REPITA = auto()
    # --- Identificadores e literais ---
    IDENT = auto()          
    NUM_INT = auto()
     # --- Operadores aritméticos ---
    MAIS = auto()           # +
    MENOS = auto()          # -
    MULT = auto()           # *
    DIV = auto()            # /
    MOD = auto()            # %
    # --- Operadores relacionais ---
    IGUAL = auto()          # ==
    DIFERENTE = auto()      # !=
    MENOR = auto()          # <
    MENOR_IGUAL = auto()    # <=
    MAIOR = auto()          # >
    MAIOR_IGUAL = auto()    # >=
    # --- Atribuição ---
    ATRIB = auto()          # =
    # --- Delimitadores ---
    ABRE_PAR = auto()       # (
    FECHA_PAR = auto()      # )
    ABRE_CHAVE = auto()     # {
    FECHA_CHAVE = auto()    # }
    PONTO_VIRGULA = auto()  # ;
    DOIS_PONTOS = auto()    # :
    VIRGULA = auto()        # ,
    PONTO = auto()          # .
    # --- Fim de arquivo ---
    EOF = auto()

   
PALAVRAS_RESERVADAS = {
    "programa": TokenType.PROGRAMA,
    "var": TokenType.VAR,
    "inteiro": TokenType.INTEIRO,
    "booleano": TokenType.BOOLEANO,
    "se": TokenType.SE,
    "senão": TokenType.SENAO,
    "senao": TokenType.SENAO,
    "enquanto": TokenType.ENQUANTO,
    "escreva": TokenType.ESCREVA,
    "leia": TokenType.LEIA,
    "verdadeiro": TokenType.VERDADEIRO,
    "falso": TokenType.FALSO,
    "e": TokenType.E,
    "ou": TokenType.OU,
    "não": TokenType.NAO,
    "nao": TokenType.NAO,
    "fim": TokenType.FIM,
    # Extensão D
    "para": TokenType.PARA,
    "ate": TokenType.ATE,
    "passo": TokenType.PASSO,
    "repita": TokenType.REPITA,
}

# Agrupamento das categorias, usado para exibir a tabela de tokens.
_PALAVRAS = set(PALAVRAS_RESERVADAS.values())
_OPERADORES = {
    TokenType.MAIS, TokenType.MENOS, TokenType.MULT, TokenType.DIV, TokenType.MOD,
    TokenType.IGUAL, TokenType.DIFERENTE, TokenType.MENOR, TokenType.MENOR_IGUAL,
    TokenType.MAIOR, TokenType.MAIOR_IGUAL, TokenType.ATRIB,
}
_DELIMITADORES = {
    TokenType.ABRE_PAR, TokenType.FECHA_PAR, TokenType.ABRE_CHAVE, TokenType.FECHA_CHAVE,
    TokenType.PONTO_VIRGULA, TokenType.DOIS_PONTOS, TokenType.VIRGULA, TokenType.PONTO,
}


def categoria(tipo: TokenType) -> str:
    """Devolve a categoria geral de um tipo de token (ex.: 'operador')."""
    if tipo in _PALAVRAS:
        return "palavra reservada"
    if tipo in _OPERADORES:
        return "operador"
    if tipo in _DELIMITADORES:
        return "delimitador"
    if tipo is TokenType.IDENT:
        return "identificador"
    if tipo is TokenType.NUM_INT:
        return "literal inteiro"
    return "fim de arquivo"


@dataclass(frozen=True)
class Token:
    """Unidade léxica: categoria, texto original e posição no código-fonte.

    linha e coluna começam em 1 e indicam o *primeiro* caractere do lexema.
    """

    tipo: TokenType
    lexema: str
    linha: int
    coluna: int

    def __str__(self) -> str:
        return f"{self.linha}:{self.coluna}\t{self.tipo.name}\t{self.lexema!r}"


