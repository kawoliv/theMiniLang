"""Analisador semântico da MiniLang.

Percorre a AST (padrão Visitor) e:
- monta a tabela de símbolos a partir das declarações;
- verifica declaração antes do uso, redeclaração, tipos de operadores,
  atribuições e condições (regras em docs/semantica.md);
- anota cada nó de expressão com o tipo inferido (campo `tipo`);
- avisa sobre variáveis lidas antes de serem inicializadas e variáveis
  nunca usadas.

Nos métodos visitar_* de expressão, o valor devolvido é o tipo da expressão.
"""

from __future__ import annotations

from typing import Optional

from minilang.arvore import (
    Atribuicao, Binaria, Bloco, Booleano, DeclVar, Enquanto, Escreva, Expressao,
    Identificador, Leia, No, Numero, Para, Programa, Repita, Se, Unaria, Visitante,
)
from minilang.errors import SemanticError
from minilang.simbolos import BOOLEANO, ERRO, INTEIRO, Simbolo, TabelaSimbolos

# Operador binário -> (tipo exigido dos dois operandos, tipo do resultado).
# '==' e '!=' ficam de fora: aceitam qualquer tipo, desde que igual dos dois lados.
REGRAS_BINARIAS = {
    "+": (INTEIRO, INTEIRO), "-": (INTEIRO, INTEIRO), "*": (INTEIRO, INTEIRO),
    "/": (INTEIRO, INTEIRO), "%": (INTEIRO, INTEIRO),
    "<": (INTEIRO, BOOLEANO), "<=": (INTEIRO, BOOLEANO),
    ">": (INTEIRO, BOOLEANO), ">=": (INTEIRO, BOOLEANO),
    "e": (BOOLEANO, BOOLEANO), "ou": (BOOLEANO, BOOLEANO),
}
IGUALDADE = {"==", "!="}
REGRAS_UNARIAS = {"-": INTEIRO, "não": BOOLEANO}


def _plural(tipo: str) -> str:
    return f"{tipo}s"


class AnalisadorSemantico(Visitante):
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros: list[str] = []                  # preenchidas no fim de analisar(),
        self.avisos: list[str] = []                 # em ordem de posição no código
        self._erros: list[SemanticError] = []
        self._avisos: list[SemanticError] = []
        # Variáveis certamente inicializadas no ponto atual do programa (docs/semantica.md, 4.1)
        self.inicializadas: set[str] = set()
        self._nao_declaradas: set[str] = set()       # já reportadas (reporta só o 1º uso)
        self._avisadas_inicializacao: set[str] = set()

    def analisar(self, programa: Programa) -> TabelaSimbolos:
        self.visitar(programa)
        posicao = lambda e: (e.linha, e.coluna)
        self.erros = [str(e) for e in sorted(self._erros, key=posicao)]
        self.avisos = [str(e) for e in sorted(self._avisos, key=posicao)]
        return self.tabela

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def _erro(self, no: No, mensagem: str) -> None:
        self._erros.append(SemanticError(no.linha, no.coluna, mensagem))

    def _aviso(self, no: No, mensagem: str) -> None:
        self._avisos.append(SemanticError(no.linha, no.coluna, f"aviso: {mensagem}"))

    def _tipo(self, expressao: Expressao) -> str:
        """Visita uma expressão, anota o tipo no nó e o devolve."""
        tipo = self.visitar(expressao)
        expressao.tipo = tipo
        return tipo

    def _resolver(self, ident: Identificador, leitura: bool, msg_nao_declarada: Optional[str] = None) -> Optional[Simbolo]:
        """Procura o identificador na tabela, anota o tipo e conta o uso.

        leitura=True quando o valor da variável é lido (para o aviso de
        variável não inicializada); False quando ela recebe um valor.
        """
        simbolo = self.tabela.buscar(ident.nome)
        if simbolo is None:
            ident.tipo = ERRO
            if ident.nome not in self._nao_declaradas:
                self._nao_declaradas.add(ident.nome)
                self._erro(ident, msg_nao_declarada or f"variável '{ident.nome}' não declarada")
            return None

        simbolo.usos += 1
        ident.tipo = simbolo.tipo
        if leitura and ident.nome not in self.inicializadas and ident.nome not in self._avisadas_inicializacao:
            self._avisadas_inicializacao.add(ident.nome)
            self._aviso(ident, f"variável '{ident.nome}' pode estar sendo lida antes de ser inicializada")
        return simbolo

    def _exige(self, expressao: Expressao, esperado: str, descricao: str) -> None:
        """Calcula o tipo de `expressao` e reporta erro se não for `esperado`."""
        tipo = self._tipo(expressao)
        if tipo not in (esperado, ERRO):
            self._erro(expressao, f"{descricao} deve ser do tipo {esperado}, mas é do tipo {tipo}")

    # ------------------------------------------------------------------
    # Programa e declarações
    # ------------------------------------------------------------------

    def visitar_Programa(self, no: Programa) -> None:
        self.tabela.entrar_escopo("global")
        for declaracao in no.declaracoes:
            self.visitar(declaracao)
        self.visitar(no.corpo)
        for simbolo in self.tabela.escopo_atual.simbolos.values():
            if simbolo.usos == 0:
                self._avisos.append(SemanticError(
                    simbolo.linha, simbolo.coluna, f"aviso: variável '{simbolo.nome}' declarada e nunca usada"
                ))
        self.tabela.sair_escopo()

    def visitar_DeclVar(self, no: DeclVar) -> None:
        anterior = self.tabela.buscar_local(no.nome)
        if anterior is not None:
            self._erro(no, f"variável '{no.nome}' já declarada na linha {anterior.linha}, coluna {anterior.coluna}")
            return
        self.tabela.declarar(no.nome, no.tipo, no.linha, no.coluna)

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def visitar_Bloco(self, no: Bloco) -> None:
        for comando in no.comandos:
            self.visitar(comando)

    def visitar_Atribuicao(self, no: Atribuicao) -> None:
        tipo_valor = self._tipo(no.valor)            # o lado direito é avaliado antes da atribuição
        simbolo = self._resolver(no.alvo, leitura=False)
        if simbolo is None:
            return
        if tipo_valor not in (simbolo.tipo, ERRO):
            self._erro(no, f"tipos incompatíveis: não é possível atribuir {tipo_valor} "
                           f"à variável '{simbolo.nome}' ({simbolo.tipo})")
        self.inicializadas.add(simbolo.nome)

    def visitar_Leia(self, no: Leia) -> None:
        simbolo = self._resolver(no.alvo, leitura=False,
                                 msg_nao_declarada=f"'leia' em identificador não declarado '{no.alvo.nome}'")
        if simbolo is not None:
            self.inicializadas.add(simbolo.nome)

    def visitar_Escreva(self, no: Escreva) -> None:
        for argumento in no.argumentos:
            self._tipo(argumento)

    def visitar_Se(self, no: Se) -> None:
        self._exige(no.condicao, BOOLEANO, "a condição do 'se'")
        antes = set(self.inicializadas)
        self.visitar(no.entao)
        depois_entao = self.inicializadas
        self.inicializadas = set(antes)
        if no.senao is not None:
            self.visitar(no.senao)
            # só está certamente inicializado o que os DOIS caminhos inicializam
            self.inicializadas = depois_entao & self.inicializadas
        # sem senão: o 'então' pode não executar, então vale o conjunto de antes

    def visitar_Enquanto(self, no: Enquanto) -> None:
        self._exige(no.condicao, BOOLEANO, "a condição do 'enquanto'")
        antes = set(self.inicializadas)
        self.visitar(no.corpo)
        self.inicializadas = antes                   # o corpo pode executar 0 vezes

    def visitar_Para(self, no: Para) -> None:
        self._exige(no.inicio, INTEIRO, "o valor inicial do 'para'")
        self._exige(no.limite, INTEIRO, "o limite do 'para'")
        if no.passo is not None:
            self._exige(no.passo, INTEIRO, "o passo do 'para'")
            if isinstance(no.passo, Numero) and no.passo.valor == 0:
                self._erro(no.passo, "o passo do 'para' não pode ser zero")

        simbolo = self._resolver(no.variavel, leitura=False)
        if simbolo is not None:
            if simbolo.tipo != INTEIRO:
                self._erro(no.variavel, f"a variável de controle do 'para' deve ser inteira, "
                                        f"mas '{simbolo.nome}' é {simbolo.tipo}")
            self.inicializadas.add(simbolo.nome)

        antes = set(self.inicializadas)
        self.visitar(no.corpo)
        self.inicializadas = antes                   # o corpo pode executar 0 vezes

    def visitar_Repita(self, no: Repita) -> None:
        self.visitar(no.corpo)                       # executa ao menos uma vez: mantém o que inicializou
        self._exige(no.condicao, BOOLEANO, "a condição do 'repita ... ate'")

    # ------------------------------------------------------------------
    # Expressões (devolvem o tipo)
    # ------------------------------------------------------------------

    def visitar_Numero(self, no: Numero) -> str:
        return INTEIRO

    def visitar_Booleano(self, no: Booleano) -> str:
        return BOOLEANO

    def visitar_Identificador(self, no: Identificador) -> str:
        simbolo = self._resolver(no, leitura=True)
        return simbolo.tipo if simbolo else ERRO

    def visitar_Unaria(self, no: Unaria) -> str:
        esperado = REGRAS_UNARIAS[no.op]
        tipo = self._tipo(no.operando)
        if tipo not in (esperado, ERRO):
            self._erro(no, f"operador '{no.op}' exige operando {esperado}, mas recebeu {tipo}")
        return esperado

    def visitar_Binaria(self, no: Binaria) -> str:
        tipo_esq = self._tipo(no.esq)
        tipo_dir = self._tipo(no.dir)

        if no.op in IGUALDADE:
            if ERRO not in (tipo_esq, tipo_dir) and tipo_esq != tipo_dir:
                self._erro(no, f"operador '{no.op}' compara {tipo_esq} com {tipo_dir}; "
                               f"os dois lados devem ter o mesmo tipo")
            return BOOLEANO

        esperado, resultado = REGRAS_BINARIAS[no.op]
        for lado, tipo in (("esquerdo", tipo_esq), ("direito", tipo_dir)):
            if tipo not in (esperado, ERRO):
                self._erro(no, f"operador '{no.op}' exige operandos {_plural(esperado)}, "
                               f"mas o operando {lado} é {tipo}")
                break

        if no.op in ("/", "%") and isinstance(no.dir, Numero) and no.dir.valor == 0:
            self._erro(no.dir, "divisão por zero")
        return resultado


def analisar_semantica(programa: Programa) -> tuple[TabelaSimbolos, list[str], list[str]]:
    """Atalho: roda o analisador e devolve (tabela de símbolos, erros, avisos)."""
    analisador = AnalisadorSemantico()
    tabela = analisador.analisar(programa)
    return tabela, analisador.erros, analisador.avisos
