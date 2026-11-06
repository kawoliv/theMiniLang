"""Especificação de erros léxicos e de compilação da MiniLang."""

from dataclasses import dataclass


@dataclass
class LexicalError:
    """Representa um erro léxico com linha, coluna e mensagem detalhada."""

    linha: int
    coluna: int
    mensagem: str

    def __str__(self) -> str:
        return f"[LÉXICO] Linha {self.linha}, Coluna {self.coluna}: {self.mensagem}"


class SyntacticError(Exception):
    """Erro sintático com linha, coluna e mensagem.

    É uma exceção porque o parser a lança no ponto do erro e a captura mais
    acima, onde registra a mensagem e faz a recuperação em modo pânico.
    """

    def __init__(self, linha: int, coluna: int, mensagem: str):
        super().__init__(mensagem)
        self.linha = linha
        self.coluna = coluna
        self.mensagem = mensagem

    def __str__(self) -> str:
        return f"[SINTÁTICO] Linha {self.linha}, Coluna {self.coluna}: {self.mensagem}"
