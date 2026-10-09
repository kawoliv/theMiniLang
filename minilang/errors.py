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
