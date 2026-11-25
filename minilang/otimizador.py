"""Otimizador da Árvore Sintática Abstrata (AST) da MiniLang (Marco 4).

Aplica duas otimizações preservando a semântica do programa:
1. Dobradura de constantes (Constant Folding): avalia subexpressões constantes
   em tempo de compilação, respeitando curto-circuito lógico e evitando dobrar
   divisões/módulos por zero (que devem falhar em tempo de execução).
2. Movimentação de código invariante de laço (Loop-Invariant Code Motion - LICM):
   identifica subexpressões compostas cujo valor não muda dentro de um laço
   (`enquanto`, `para`, `repita`) e as move para variáveis temporárias calculadas
   uma única vez antes do início do laço.
"""

from __future__ import annotations

import copy

from minilang.arvore import (
    Atribuicao,
    Binaria,
    Bloco,
    Booleano,
    Comando,
    DeclVar,
    Enquanto,
    Escreva,
    Expressao,
    Identificador,
    Leia,
    No,
    Numero,
    Para,
    Programa,
    Repita,
    Se,
    Unaria,
    Visitante,
)
from minilang.interpretador import dividir_inteiro, modulo_inteiro
from minilang.simbolos import BOOLEANO, INTEIRO

_OPS_BOOLEANOS = {"não", "==", "!=", "<", "<=", ">", ">=", "e", "ou"}


def _inferir_tipo(expr: Expressao) -> str:
    """Devolve o tipo anotado da expressão ou infere um fallback seguro."""
    if expr.tipo in (INTEIRO, BOOLEANO):
        return expr.tipo
    if isinstance(expr, Booleano):
        return BOOLEANO
    if isinstance(expr, (Unaria, Binaria)) and expr.op in _OPS_BOOLEANOS:
        return BOOLEANO
    return INTEIRO


def _variaveis_modificadas(no: No) -> set[str]:
    """Coleta os nomes de todas as variáveis modificadas dentro de `no`."""
    modificadas: set[str] = set()
    if isinstance(no, Atribuicao):
        modificadas.add(no.alvo.nome)
    elif isinstance(no, Leia):
        modificadas.add(no.alvo.nome)
    elif isinstance(no, Para):
        modificadas.add(no.variavel.nome)

    for filho in no.filhos():
        modificadas.update(_variaveis_modificadas(filho))
    return modificadas


def _variaveis_lidas(expr: Expressao) -> set[str]:
    """Coleta os nomes de todos os identificadores lidos em `expr`."""
    if isinstance(expr, Identificador):
        return {expr.nome}
    lidas: set[str] = set()
    for filho in expr.filhos():
        if isinstance(filho, Expressao):
            lidas.update(_variaveis_lidas(filho))
    return lidas


def _eh_segura_para_mover(expr: Expressao) -> bool:
    """Garante que mover `expr` para antes de um laço não introduza divisão por zero."""
    if isinstance(expr, Binaria):
        if expr.op in ("/", "%"):
            if not (isinstance(expr.dir, Numero) and expr.dir.valor != 0):
                return False
        return _eh_segura_para_mover(expr.esq) and _eh_segura_para_mover(expr.dir)
    if isinstance(expr, Unaria):
        return _eh_segura_para_mover(expr.operando)
    return True


class Otimizador(Visitante):
    """Transforma a AST aplicando dobradura de constantes e LICM."""

    def __init__(self) -> None:
        self.dobraduras: int = 0
        self.movimentacoes: int = 0
        self._nomes_usados: set[str] = set()
        self._novas_declaracoes: list[DeclVar] = []
        self._contador_temp: int = 0

    def otimizar(self, programa: Programa) -> Programa:
        """Retorna uma nova AST otimizada sem mutar a árvore original."""
        self.dobraduras = 0
        self.movimentacoes = 0
        self._novas_declaracoes = []
        self._contador_temp = 0

        copia = copy.deepcopy(programa)
        self._nomes_usados = {decl.nome for decl in copia.declaracoes}

        # Passo 1: Dobradura de constantes (bottom-up)
        copia.corpo = self.visitar(copia.corpo)

        # Passo 2: Movimentação de invariantes de laço (do laço mais externo ao mais interno)
        copia.corpo = self._licm_bloco(copia.corpo)
        copia.declaracoes.extend(self._novas_declaracoes)
        return copia

    # ------------------------------------------------------------------
    # Passo 1: Dobradura de constantes (Constant Folding)
    # ------------------------------------------------------------------

    def visitar_Programa(self, no: Programa) -> Programa:
        return self.otimizar(no)

    def visitar_Bloco(self, no: Bloco) -> Bloco:
        no.comandos = [self.visitar(cmd) for cmd in no.comandos]
        return no

    def visitar_Atribuicao(self, no: Atribuicao) -> Atribuicao:
        no.valor = self.visitar(no.valor)
        return no

    def visitar_Leia(self, no: Leia) -> Leia:
        return no

    def visitar_Escreva(self, no: Escreva) -> Escreva:
        no.argumentos = [self.visitar(arg) for arg in no.argumentos]
        return no

    def visitar_Se(self, no: Se) -> Se:
        no.condicao = self.visitar(no.condicao)
        no.entao = self.visitar(no.entao)
        if no.senao is not None:
            no.senao = self.visitar(no.senao)
        return no

    def visitar_Enquanto(self, no: Enquanto) -> Enquanto:
        no.condicao = self.visitar(no.condicao)
        no.corpo = self.visitar(no.corpo)
        return no

    def visitar_Para(self, no: Para) -> Para:
        no.inicio = self.visitar(no.inicio)
        no.limite = self.visitar(no.limite)
        if no.passo is not None:
            no.passo = self.visitar(no.passo)
        no.corpo = self.visitar(no.corpo)
        return no

    def visitar_Repita(self, no: Repita) -> Repita:
        no.corpo = self.visitar(no.corpo)
        no.condicao = self.visitar(no.condicao)
        return no

    def visitar_Numero(self, no: Numero) -> Numero:
        return no

    def visitar_Booleano(self, no: Booleano) -> Booleano:
        return no

    def visitar_Identificador(self, no: Identificador) -> Identificador:
        return no

    def visitar_Unaria(self, no: Unaria) -> Expressao:
        operando = self.visitar(no.operando)
        if no.op == "-" and isinstance(operando, Numero):
            self.dobraduras += 1
            return Numero(-operando.valor, linha=no.linha, coluna=no.coluna, tipo=no.tipo or INTEIRO)
        if no.op == "não" and isinstance(operando, Booleano):
            self.dobraduras += 1
            return Booleano(not operando.valor, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)
        no.operando = operando
        return no

    def visitar_Binaria(self, no: Binaria) -> Expressao:
        esq = self.visitar(no.esq)
        dir_no = self.visitar(no.dir)

        # Curto-circuito constante para operadores lógicos
        if no.op == "e" and isinstance(esq, Booleano):
            if not esq.valor:
                self.dobraduras += 1
                return Booleano(False, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)
            if isinstance(dir_no, Booleano):
                self.dobraduras += 1
                return Booleano(dir_no.valor, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)

        if no.op == "ou" and isinstance(esq, Booleano):
            if esq.valor:
                self.dobraduras += 1
                return Booleano(True, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)
            if isinstance(dir_no, Booleano):
                self.dobraduras += 1
                return Booleano(dir_no.valor, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)

        if isinstance(esq, Numero) and isinstance(dir_no, Numero):
            a, b = esq.valor, dir_no.valor
            if no.op == "+":
                self.dobraduras += 1
                return Numero(a + b, linha=no.linha, coluna=no.coluna, tipo=no.tipo or INTEIRO)
            if no.op == "-":
                self.dobraduras += 1
                return Numero(a - b, linha=no.linha, coluna=no.coluna, tipo=no.tipo or INTEIRO)
            if no.op == "*":
                self.dobraduras += 1
                return Numero(a * b, linha=no.linha, coluna=no.coluna, tipo=no.tipo or INTEIRO)
            if no.op == "/" and b != 0:
                self.dobraduras += 1
                return Numero(dividir_inteiro(a, b), linha=no.linha, coluna=no.coluna, tipo=no.tipo or INTEIRO)
            if no.op == "%" and b != 0:
                self.dobraduras += 1
                return Numero(modulo_inteiro(a, b), linha=no.linha, coluna=no.coluna, tipo=no.tipo or INTEIRO)

            relacionais = {
                "<": a < b,
                "<=": a <= b,
                ">": a > b,
                ">=": a >= b,
                "==": a == b,
                "!=": a != b,
            }
            if no.op in relacionais:
                self.dobraduras += 1
                return Booleano(relacionais[no.op], linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)

        if isinstance(esq, Booleano) and isinstance(dir_no, Booleano):
            if no.op == "==":
                self.dobraduras += 1
                return Booleano(esq.valor == dir_no.valor, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)
            if no.op == "!=":
                self.dobraduras += 1
                return Booleano(esq.valor != dir_no.valor, linha=no.linha, coluna=no.coluna, tipo=no.tipo or BOOLEANO)

        no.esq = esq
        no.dir = dir_no
        return no

    # ------------------------------------------------------------------
    # Passo 2: Movimentação de Código Invariante de Laço (LICM)
    # ------------------------------------------------------------------

    def _novo_temp(self, tipo: str, linha: int, coluna: int) -> str:
        while True:
            nome = f"_inv_{self._contador_temp}"
            self._contador_temp += 1
            if nome not in self._nomes_usados:
                self._nomes_usados.add(nome)
                self._novas_declaracoes.append(DeclVar(nome=nome, tipo=tipo, linha=linha, coluna=coluna))
                return nome

    def _extrair_invariantes_expr(
        self,
        expr: Expressao,
        modificadas: set[str],
        hoisted: list[Comando],
    ) -> Expressao:
        if (
            isinstance(expr, (Binaria, Unaria))
            and _variaveis_lidas(expr).isdisjoint(modificadas)
            and _eh_segura_para_mover(expr)
        ):
            tipo = _inferir_tipo(expr)
            nome_temp = self._novo_temp(tipo, expr.linha, expr.coluna)
            hoisted.append(
                Atribuicao(
                    alvo=Identificador(nome_temp, linha=expr.linha, coluna=expr.coluna, tipo=tipo),
                    valor=expr,
                    linha=expr.linha,
                    coluna=expr.coluna,
                )
            )
            self.movimentacoes += 1
            return Identificador(nome_temp, linha=expr.linha, coluna=expr.coluna, tipo=tipo)

        if isinstance(expr, Unaria):
            expr.operando = self._extrair_invariantes_expr(expr.operando, modificadas, hoisted)
        elif isinstance(expr, Binaria):
            expr.esq = self._extrair_invariantes_expr(expr.esq, modificadas, hoisted)
            expr.dir = self._extrair_invariantes_expr(expr.dir, modificadas, hoisted)
        return expr

    def _extrair_invariantes_cmd(
        self,
        cmd: Comando,
        modificadas: set[str],
        hoisted: list[Comando],
    ) -> Comando:
        if isinstance(cmd, Bloco):
            cmd.comandos = [self._extrair_invariantes_cmd(c, modificadas, hoisted) for c in cmd.comandos]
        elif isinstance(cmd, Atribuicao):
            cmd.valor = self._extrair_invariantes_expr(cmd.valor, modificadas, hoisted)
        elif isinstance(cmd, Escreva):
            cmd.argumentos = [self._extrair_invariantes_expr(a, modificadas, hoisted) for a in cmd.argumentos]
        elif isinstance(cmd, Se):
            cmd.condicao = self._extrair_invariantes_expr(cmd.condicao, modificadas, hoisted)
            cmd.entao = self._extrair_invariantes_cmd(cmd.entao, modificadas, hoisted)
            if cmd.senao is not None:
                cmd.senao = self._extrair_invariantes_cmd(cmd.senao, modificadas, hoisted)
        elif isinstance(cmd, Enquanto):
            cmd.condicao = self._extrair_invariantes_expr(cmd.condicao, modificadas, hoisted)
            cmd.corpo = self._extrair_invariantes_cmd(cmd.corpo, modificadas, hoisted)
        elif isinstance(cmd, Para):
            cmd.inicio = self._extrair_invariantes_expr(cmd.inicio, modificadas, hoisted)
            cmd.limite = self._extrair_invariantes_expr(cmd.limite, modificadas, hoisted)
            if cmd.passo is not None:
                cmd.passo = self._extrair_invariantes_expr(cmd.passo, modificadas, hoisted)
            cmd.corpo = self._extrair_invariantes_cmd(cmd.corpo, modificadas, hoisted)
        elif isinstance(cmd, Repita):
            cmd.corpo = self._extrair_invariantes_cmd(cmd.corpo, modificadas, hoisted)
            cmd.condicao = self._extrair_invariantes_expr(cmd.condicao, modificadas, hoisted)
        return cmd

    def _licm_ramo(self, cmd: Comando) -> Comando:
        if isinstance(cmd, Bloco):
            return self._licm_bloco(cmd)
        cmds = self._licm_comando(cmd)
        if len(cmds) == 1:
            return cmds[0]
        return Bloco(comandos=cmds, linha=cmd.linha, coluna=cmd.coluna)

    def _licm_bloco(self, bloco: Bloco) -> Bloco:
        novos: list[Comando] = []
        for cmd in bloco.comandos:
            novos.extend(self._licm_comando(cmd))
        bloco.comandos = novos
        return bloco

    def _licm_comando(self, cmd: Comando) -> list[Comando]:
        if isinstance(cmd, Bloco):
            return [self._licm_bloco(cmd)]
        if isinstance(cmd, Se):
            cmd.entao = self._licm_ramo(cmd.entao)
            if cmd.senao is not None:
                cmd.senao = self._licm_ramo(cmd.senao)
            return [cmd]
        if isinstance(cmd, Enquanto):
            modificadas = _variaveis_modificadas(cmd.corpo)
            hoisted: list[Comando] = []
            cmd.condicao = self._extrair_invariantes_expr(cmd.condicao, modificadas, hoisted)
            cmd.corpo = self._extrair_invariantes_cmd(cmd.corpo, modificadas, hoisted)
            cmd.corpo = self._licm_ramo(cmd.corpo)
            return hoisted + [cmd]
        if isinstance(cmd, Para):
            modificadas = {cmd.variavel.nome} | _variaveis_modificadas(cmd.corpo)
            hoisted = []
            cmd.corpo = self._extrair_invariantes_cmd(cmd.corpo, modificadas, hoisted)
            cmd.corpo = self._licm_ramo(cmd.corpo)
            return hoisted + [cmd]
        if isinstance(cmd, Repita):
            modificadas = _variaveis_modificadas(cmd.corpo)
            hoisted = []
            cmd.corpo = self._extrair_invariantes_cmd(cmd.corpo, modificadas, hoisted)
            cmd.condicao = self._extrair_invariantes_expr(cmd.condicao, modificadas, hoisted)
            cmd.corpo = self._licm_bloco(cmd.corpo)
            return hoisted + [cmd]
        return [cmd]


def otimizar(programa: Programa) -> Programa:
    """Atalho: instancia o Otimizador, transforma a AST e devolve o Programa otimizado."""
    return Otimizador().otimizar(programa)
