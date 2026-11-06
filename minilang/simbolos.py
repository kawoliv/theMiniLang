"""Tabela de símbolos da MiniLang.

Guarda, para cada variável declarada: nome, tipo, escopo e posição de
declaração. É implementada como uma pilha de escopos: cada escopo é um
dicionário nome -> Simbolo. A busca vai do escopo mais interno para o mais
externo. Ver docs/semantica.md, seção 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

INTEIRO = "inteiro"
BOOLEANO = "booleano"
ERRO = "erro"   # tipo de uma expressão que já tem erro (evita mensagens em cascata)


@dataclass
class Simbolo:
    nome: str
    tipo: str
    escopo: str
    nivel: int
    linha: int
    coluna: int
    usos: int = 0


@dataclass
class Escopo:
    nome: str
    nivel: int
    simbolos: dict[str, Simbolo]


class TabelaSimbolos:
    def __init__(self):
        self.escopos: list[Escopo] = []      # pilha: o último é o escopo atual
        self.todos: list[Simbolo] = []       # histórico de todos os símbolos, em ordem de declaração

    # --- escopos ---

    def entrar_escopo(self, nome: str) -> None:
        self.escopos.append(Escopo(nome, len(self.escopos), {}))

    def sair_escopo(self) -> Escopo:
        return self.escopos.pop()

    @property
    def escopo_atual(self) -> Escopo:
        return self.escopos[-1]

    # --- símbolos ---

    def declarar(self, nome: str, tipo: str, linha: int, coluna: int) -> Simbolo:
        """Insere um símbolo no escopo atual. Quem chama deve checar redeclaração antes."""
        escopo = self.escopo_atual
        simbolo = Simbolo(nome, tipo, escopo.nome, escopo.nivel, linha, coluna)
        escopo.simbolos[nome] = simbolo
        self.todos.append(simbolo)
        return simbolo

    def buscar_local(self, nome: str) -> Optional[Simbolo]:
        """Procura só no escopo atual (usado para detectar redeclaração)."""
        return self.escopo_atual.simbolos.get(nome)

    def buscar(self, nome: str) -> Optional[Simbolo]:
        """Procura do escopo mais interno para o mais externo."""
        for escopo in reversed(self.escopos):
            if nome in escopo.simbolos:
                return escopo.simbolos[nome]
        return None

    # --- exibição (opção --symbols) ---

    def formatar(self) -> str:
        cabecalho = f"{'NOME':<16} | {'TIPO':<9} | {'ESCOPO':<8} | {'NÍVEL':>5} | {'DECLARADA EM':<13} | {'USOS':>4}"
        linhas = ["=" * len(cabecalho), "TABELA DE SÍMBOLOS (Marco 3 - Análise Semântica)",
                  "=" * len(cabecalho), cabecalho, "-" * len(cabecalho)]
        for s in self.todos:
            posicao = f"{s.linha}:{s.coluna}"
            linhas.append(f"{s.nome:<16} | {s.tipo:<9} | {s.escopo:<8} | {s.nivel:>5} | {posicao:<13} | {s.usos:>4}")
        linhas.append("-" * len(cabecalho))
        return "\n".join(linhas)
