"""Árvore Sintática Abstrata (AST) da MiniLang.

Cada construção da linguagem vira um nó (uma dataclass). A AST guarda só o
que importa para as próximas fases: a pontuação (';', '(', '{', 'fim.') não
vira nó.

- Todo nó tem `linha` e `coluna` do token que o originou, para que o M3 e o
  M4 possam reportar erros com posição.
- Todo nó de expressão tem o campo `tipo` (None no M2), que o analisador
  semântico (M3) vai preencher ao anotar a AST com os tipos inferidos.
- `linha`, `coluna` e `tipo` são campos só-por-nome (kw_only), por isso os
  nós são criados assim: Numero(5, linha=3, coluna=10).

A especificação completa está em docs/gramatica.md, seção 7.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Iterator, Optional


# ----------------------------------------------------------------------
# Classes base
# ----------------------------------------------------------------------

@dataclass
class No:
    """Base de todos os nós da AST."""

    linha: int = field(kw_only=True)
    coluna: int = field(kw_only=True)

    def filhos(self) -> Iterator[No]:
        """Devolve os nós filhos diretos, na ordem em que aparecem no código."""
        for campo in fields(self):
            valor = getattr(self, campo.name)
            if isinstance(valor, No):
                yield valor
            elif isinstance(valor, list):
                for item in valor:
                    if isinstance(item, No):
                        yield item


@dataclass
class Comando(No):
    """Base dos nós de comando."""


@dataclass
class Expressao(No):
    """Base dos nós de expressão. `tipo` será preenchido no M3."""

    tipo: Optional[str] = field(default=None, kw_only=True)


# ----------------------------------------------------------------------
# Expressões
# ----------------------------------------------------------------------

@dataclass
class Numero(Expressao):
    valor: int


@dataclass
class Booleano(Expressao):
    valor: bool


@dataclass
class Identificador(Expressao):
    nome: str


@dataclass
class Unaria(Expressao):
    op: str            # "-" ou "não"
    operando: Expressao


@dataclass
class Binaria(Expressao):
    op: str            # "+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "e", "ou"
    esq: Expressao
    dir: Expressao


# ----------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------

@dataclass
class Bloco(Comando):
    comandos: list[Comando]


@dataclass
class Atribuicao(Comando):
    alvo: Identificador
    valor: Expressao


@dataclass
class Leia(Comando):
    alvo: Identificador


@dataclass
class Escreva(Comando):
    argumentos: list[Expressao]


@dataclass
class Se(Comando):
    condicao: Expressao
    entao: Comando
    senao: Optional[Comando] = None


@dataclass
class Enquanto(Comando):
    condicao: Expressao
    corpo: Comando


@dataclass
class Para(Comando):
    """Extensão D: para <variavel> = <inicio> ate <limite> [passo <passo>] <corpo>."""

    variavel: Identificador
    inicio: Expressao
    limite: Expressao
    passo: Optional[Expressao]
    corpo: Comando


@dataclass
class Repita(Comando):
    """Extensão D: repita <comandos> ate <condicao>; (o corpo executa ao menos uma vez)."""

    corpo: Bloco
    condicao: Expressao


# ----------------------------------------------------------------------
# Declarações e programa
# ----------------------------------------------------------------------

@dataclass
class DeclVar(No):
    """Uma variável declarada. 'var a, b: inteiro;' gera dois DeclVar."""

    nome: str
    tipo: str          # "inteiro" ou "booleano"


@dataclass
class Programa(No):
    nome: str
    declaracoes: list[DeclVar]
    corpo: Bloco


# ----------------------------------------------------------------------
# Navegação: padrão Visitor
# ----------------------------------------------------------------------

class Visitante:
    """Base para percorrer a AST (padrão Visitor).

    Para tratar um tipo de nó, a subclasse define um método
    visitar_<NomeDaClasse>. Os nós sem método próprio caem em
    visitar_generico, que apenas visita os filhos. O M3 (semântica) e o M4
    (back-end) serão escritos como subclasses desta classe.
    """

    def visitar(self, no: No):
        metodo = getattr(self, f"visitar_{type(no).__name__}", self.visitar_generico)
        return metodo(no)

    def visitar_generico(self, no: No):
        for filho in no.filhos():
            self.visitar(filho)


# ----------------------------------------------------------------------
# Impressão da árvore (usada pela opção --ast do CLI)
# ----------------------------------------------------------------------

def _rotulo(no: No) -> str:
    """Texto de uma linha que descreve o nó (sem os filhos)."""
    if isinstance(no, Programa):
        texto = f"Programa '{no.nome}'"
    elif isinstance(no, DeclVar):
        texto = f"DeclVar {no.nome}: {no.tipo}"
    elif isinstance(no, Identificador):
        texto = f"Identificador '{no.nome}'"
    elif isinstance(no, Numero):
        texto = f"Numero {no.valor}"
    elif isinstance(no, Booleano):
        texto = f"Booleano {'verdadeiro' if no.valor else 'falso'}"
    elif isinstance(no, (Unaria, Binaria)):
        texto = f"{type(no).__name__} '{no.op}'"
    else:
        texto = type(no).__name__

    if isinstance(no, Expressao) and no.tipo is not None:
        texto += f" : {no.tipo}"
    return f"{texto}  [{no.linha}:{no.coluna}]"


def _entradas(no: No) -> list[tuple[str, object]]:
    """Campos de um nó que contêm filhos: (nome do campo, nó ou lista de nós)."""
    entradas = []
    for campo in fields(no):
        valor = getattr(no, campo.name)
        if isinstance(valor, No) or (isinstance(valor, list) and valor and isinstance(valor[0], No)):
            entradas.append((campo.name, valor))
    return entradas


def _formatar(no: No, prefixo: str, saida: list[str]) -> None:
    entradas = _entradas(no)
    for i, (papel, valor) in enumerate(entradas):
        ultimo = i == len(entradas) - 1
        ramo = "└── " if ultimo else "├── "
        recuo = prefixo + ("    " if ultimo else "│   ")
        if isinstance(valor, list):
            saida.append(f"{prefixo}{ramo}{papel} ({len(valor)})")
            for j, item in enumerate(valor):
                ultimo_item = j == len(valor) - 1
                saida.append(f"{recuo}{'└── ' if ultimo_item else '├── '}{_rotulo(item)}")
                _formatar(item, recuo + ("    " if ultimo_item else "│   "), saida)
        else:
            saida.append(f"{prefixo}{ramo}{papel}: {_rotulo(valor)}")
            _formatar(valor, recuo, saida)


def formatar_arvore(raiz: No) -> str:
    """Devolve a AST como texto em forma de árvore, com [linha:coluna] de cada nó."""
    saida = [_rotulo(raiz)]
    _formatar(raiz, "", saida)
    return "\n".join(saida)
