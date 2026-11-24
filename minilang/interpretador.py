"""Interpretador da Árvore Sintática Abstrata (AST) da MiniLang (Marco 4 - Back-End).

Percorre a AST (padrão Visitor) e executa diretamente os comandos e expressões
do programa, mantendo o estado das variáveis em memória e interagindo com a
entrada e saída padrão (ou fluxos injetados nos testes).
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from typing import Any, Optional

from minilang.arvore import (
    Atribuicao, Binaria, Bloco, Booleano, DeclVar, Enquanto, Escreva,
    Identificador, Leia, No, Numero, Para, Programa, Repita, Se, Unaria, Visitante,
)
from minilang.errors import ExecutionError
from minilang.simbolos import BOOLEANO, INTEIRO


def dividir_inteiro(esq: int, dir_val: int) -> int:
    """Divisão inteira padrão da MiniLang (compartilhável com o otimizador do M4)."""
    return esq // dir_val


def modulo_inteiro(esq: int, dir_val: int) -> int:
    """Resto da divisão inteira padrão da MiniLang (compartilhável com o otimizador do M4)."""
    return esq % dir_val


def formatar_valor(valor: int | bool) -> str:
    """Converte um valor nativo do Python para o texto exibido por 'escreva'.

    Em Python `bool` é subclasse de `int` (`isinstance(True, int) == True`),
    portanto o teste de `bool` deve vir obrigatoriamente antes de `int`.
    """
    if isinstance(valor, bool):
        return "verdadeiro" if valor else "falso"
    return str(valor)


def _criar_leitor(entrada: Any) -> Callable[[], str]:
    """Normaliza a fonte de entrada (None/stdin, função, stream ou iterável) em um leitor de linha."""
    if entrada is None:
        return input
    if callable(entrada):
        return lambda: str(entrada())
    if hasattr(entrada, "readline"):
        def _ler_stream() -> str:
            linha = entrada.readline()
            if linha == "":
                raise EOFError
            return linha.rstrip("\r\n")
        return _ler_stream
    if isinstance(entrada, Iterable):
        iterador = iter(entrada)
        def _ler_iteravel() -> str:
            try:
                return str(next(iterador))
            except StopIteration as exc:
                raise EOFError from exc
        return _ler_iteravel
    raise TypeError(f"Fonte de entrada inválida para o interpretador: {type(entrada).__name__}")


class Interpretador(Visitante):
    """Executa um programa MiniLang percorrendo sua AST."""

    def __init__(
        self,
        entrada: Any = None,
        saida: Any = sys.stdout,
        max_iteracoes: Optional[int] = None,
        prompt_interativo: bool = False,
        trace: bool = False,
    ):
        self.memoria: dict[str, int | bool] = {}
        self.tipos: dict[str, str] = {}
        self.linhas_saida: list[str] = []
        self.historico_trace: list[str] = []
        self._ler = _criar_leitor(entrada)
        self._saida = saida
        self.max_iteracoes = max_iteracoes
        self.prompt_interativo = prompt_interativo
        self.trace = trace
        self._iteracoes = 0

    def executar(self, programa: Programa) -> list[str]:
        """Executa o programa completo e devolve a lista de linhas impressas por 'escreva'."""
        self.visitar(programa)
        return self.linhas_saida

    def formatar_memoria(self) -> str:
        """Devolve uma tabela formatada com o estado atual/final das variáveis na memória."""
        cabecalho = f"{'VARIÁVEL':<16} | {'TIPO':<9} | {'VALOR FINAL':<15}"
        largura = len(cabecalho)
        linhas = [
            "=" * largura,
            "ESTADO FINAL DA MEMÓRIA (Marco 4 - Interpretador)",
            "=" * largura,
            cabecalho,
            "-" * largura,
        ]
        if not self.memoria:
            linhas.append("(nenhuma variável declarada)")
        else:
            for nome, valor in self.memoria.items():
                tipo = self.tipos.get(nome, INTEIRO)
                linhas.append(f"{nome:<16} | {tipo:<9} | {formatar_valor(valor):<15}")
        linhas.append("-" * largura)
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Utilitários internos
    # ------------------------------------------------------------------

    def _registrar_trace(self, no: No, mensagem: str) -> None:
        """Registra e exibe (se `self.trace` estiver ativo) um passo da execução."""
        if not self.trace:
            return
        linha_trace = f"[TRACE L{no.linha}:C{no.coluna}] {mensagem}"
        self.historico_trace.append(linha_trace)
        if self._saida is not None:
            print(linha_trace, file=self._saida)

    def _contar_iteracao(self, no: No) -> None:
        """Incrementa contador de laços e aborta caso exceda `max_iteracoes` (proteção em testes)."""
        self._iteracoes += 1
        if self.max_iteracoes is not None and self._iteracoes > self.max_iteracoes:
            raise ExecutionError(
                no.linha,
                no.coluna,
                f"limite máximo de {self.max_iteracoes} iterações excedido (possível laço infinito)",
            )

    def _ler_linha(self, no: Leia, tipo: str) -> str:
        if self.prompt_interativo and self._saida is not None:
            dica_tipo = "inteiro" if tipo == INTEIRO else "booleano: verdadeiro/falso"
            print(f"[LEIA] Digite um valor ({dica_tipo}) para '{no.alvo.nome}': ", end="", file=self._saida, flush=True)
        try:
            return self._ler()
        except EOFError as exc:
            raise ExecutionError(
                no.linha,
                no.coluna,
                f"fim de entrada inesperado ao ler '{no.alvo.nome}'",
            ) from exc

    # ------------------------------------------------------------------
    # Programa e declarações
    # ------------------------------------------------------------------

    def visitar_Programa(self, no: Programa) -> None:
        for declaracao in no.declaracoes:
            self.visitar(declaracao)
        self.visitar(no.corpo)

    def visitar_DeclVar(self, no: DeclVar) -> None:
        self.tipos[no.nome] = no.tipo
        self.memoria[no.nome] = False if no.tipo == BOOLEANO else 0

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def visitar_Bloco(self, no: Bloco) -> None:
        for comando in no.comandos:
            self.visitar(comando)

    def visitar_Atribuicao(self, no: Atribuicao) -> None:
        valor = self.visitar(no.valor)
        self.memoria[no.alvo.nome] = valor
        self._registrar_trace(no, f"{no.alvo.nome} = {formatar_valor(valor)}")

    def visitar_Leia(self, no: Leia) -> None:
        nome = no.alvo.nome
        tipo = no.alvo.tipo or self.tipos.get(nome, INTEIRO)
        texto = self._ler_linha(no, tipo).strip()

        if tipo == INTEIRO:
            try:
                valor: int | bool = int(texto)
            except ValueError as exc:
                raise ExecutionError(
                    no.linha,
                    no.coluna,
                    f"valor inválido '{texto}' para leitura de '{nome}' (esperado inteiro)",
                ) from exc
        elif tipo == BOOLEANO:
            if texto in ("verdadeiro", "1"):
                valor = True
            elif texto in ("falso", "0"):
                valor = False
            else:
                raise ExecutionError(
                    no.linha,
                    no.coluna,
                    f"valor inválido '{texto}' para leitura de '{nome}' (esperado 'verdadeiro' ou 'falso')",
                )
        else:
            raise ExecutionError(no.linha, no.coluna, f"tipo desconhecido '{tipo}' para leitura de '{nome}'")

        self.memoria[nome] = valor
        self._registrar_trace(no, f"leia({nome}) <- {formatar_valor(valor)}")

    def visitar_Escreva(self, no: Escreva) -> None:
        valores = [formatar_valor(self.visitar(arg)) for arg in no.argumentos]
        linha = " ".join(valores)
        self.linhas_saida.append(linha)
        self._registrar_trace(no, f"escreva -> {linha}")
        if self._saida is not None:
            print(linha, file=self._saida)

    def visitar_Se(self, no: Se) -> None:
        cond = bool(self.visitar(no.condicao))
        self._registrar_trace(no, f"se ({formatar_valor(cond)})")
        if cond:
            self.visitar(no.entao)
        elif no.senao is not None:
            self.visitar(no.senao)

    def visitar_Enquanto(self, no: Enquanto) -> None:
        while self.visitar(no.condicao):
            self._contar_iteracao(no)
            self._registrar_trace(no, "enquanto (verdadeiro)")
            self.visitar(no.corpo)

    def visitar_Para(self, no: Para) -> None:
        inicio = self.visitar(no.inicio)
        limite = self.visitar(no.limite)
        passo = self.visitar(no.passo) if no.passo is not None else 1

        if passo == 0:
            alvo_erro = no.passo if no.passo is not None else no
            raise ExecutionError(alvo_erro.linha, alvo_erro.coluna, "o passo do 'para' não pode ser zero")

        nome = no.variavel.nome
        self.memoria[nome] = inicio
        while (self.memoria[nome] <= limite) if passo > 0 else (self.memoria[nome] >= limite):
            self._contar_iteracao(no)
            self._registrar_trace(
                no,
                f"para {nome} = {formatar_valor(self.memoria[nome])} (ate {formatar_valor(limite)}, passo {formatar_valor(passo)})",
            )
            self.visitar(no.corpo)
            self.memoria[nome] = self.memoria[nome] + passo

    def visitar_Repita(self, no: Repita) -> None:
        while True:
            self._contar_iteracao(no)
            self._registrar_trace(no, "repita (início da iteração)")
            self.visitar(no.corpo)
            cond = bool(self.visitar(no.condicao))
            self._registrar_trace(no, f"ate ({formatar_valor(cond)})")
            if cond:
                break

    # ------------------------------------------------------------------
    # Expressões
    # ------------------------------------------------------------------

    def visitar_Numero(self, no: Numero) -> int:
        return no.valor

    def visitar_Booleano(self, no: Booleano) -> bool:
        return no.valor

    def visitar_Identificador(self, no: Identificador) -> int | bool:
        if no.nome not in self.memoria:
            raise ExecutionError(no.linha, no.coluna, f"variável '{no.nome}' não declarada")
        return self.memoria[no.nome]

    def visitar_Unaria(self, no: Unaria) -> int | bool:
        operando = self.visitar(no.operando)
        if no.op == "-":
            return -operando
        if no.op == "não":
            return not operando
        raise ExecutionError(no.linha, no.coluna, f"operador unário desconhecido '{no.op}'")

    def visitar_Binaria(self, no: Binaria) -> int | bool:
        # Curto-circuito lógico: só avalia o lado direito se necessário
        if no.op == "e":
            return bool(self.visitar(no.esq)) and bool(self.visitar(no.dir))
        if no.op == "ou":
            return bool(self.visitar(no.esq)) or bool(self.visitar(no.dir))

        esq = self.visitar(no.esq)
        dir_val = self.visitar(no.dir)

        if no.op in ("/", "%") and dir_val == 0:
            raise ExecutionError(no.dir.linha, no.dir.coluna, "divisão por zero")

        if no.op == "+":
            return esq + dir_val
        if no.op == "-":
            return esq - dir_val
        if no.op == "*":
            return esq * dir_val
        if no.op == "/":
            return dividir_inteiro(esq, dir_val)
        if no.op == "%":
            return modulo_inteiro(esq, dir_val)
        if no.op == "==":
            return esq == dir_val
        if no.op == "!=":
            return esq != dir_val
        if no.op == "<":
            return esq < dir_val
        if no.op == "<=":
            return esq <= dir_val
        if no.op == ">":
            return esq > dir_val
        if no.op == ">=":
            return esq >= dir_val
        raise ExecutionError(no.linha, no.coluna, f"operador binário desconhecido '{no.op}'")


def interpretar(
    programa: Programa,
    entrada: Any = None,
    saida: Any = sys.stdout,
    max_iteracoes: Optional[int] = None,
    prompt_interativo: bool = False,
    trace: bool = False,
) -> Interpretador:
    """Atalho: instancia o Interpretador, executa a AST e devolve a instância."""
    interpretador = Interpretador(
        entrada=entrada,
        saida=saida,
        max_iteracoes=max_iteracoes,
        prompt_interativo=prompt_interativo,
        trace=trace,
    )
    interpretador.executar(programa)
    return interpretador
