"""Analisador sintático (parser) da MiniLang.

Parser descendente recursivo preditivo, LL(1): cada não-terminal da
gramática (docs/gramatica.md) vira um método _nome(), e o token atual
(1 token de lookahead) decide qual regra aplicar. A pilha de chamadas do
Python faz o papel da pilha do autômato de pilha.

Entrada: lista de tokens do Lexer (terminada em EOF).
Saída:   a AST (minilang/arvore.py) e a lista de erros sintáticos.

Recuperação de erros (docs/gramatica.md, seção 8):
- modo pânico: um comando ou declaração com erro é descartado até um ponto
  de sincronização (';' ou um token que inicia/encerra um comando);
- nível de frase: um ';' esquecido antes de um comando na linha seguinte é
  registrado como erro e "inserido" sem descartar nada.
"""

from __future__ import annotations

from typing import Optional

from minilang.arvore import (
    Atribuicao, Binaria, Bloco, Booleano, Comando, DeclVar, Enquanto, Escreva,
    Expressao, Identificador, Leia, Numero, Para, Programa, Repita, Se, Unaria,
)
from minilang.errors import SyntacticError
from minilang.tokens import PALAVRAS_RESERVADAS, Token, TokenType as T


# ----------------------------------------------------------------------
# Conjuntos de tokens usados nas decisões e na recuperação
# ----------------------------------------------------------------------

# FIRST(comando): tokens que podem iniciar um comando.
INICIO_COMANDO = {T.IDENT, T.LEIA, T.ESCREVA, T.SE, T.ENQUANTO, T.PARA, T.REPITA, T.ABRE_CHAVE}

# Tokens onde uma lista de comandos termina (o chamador decide o que fazer com eles).
FIM_LISTA = {T.FECHA_CHAVE, T.FIM, T.EOF}

# Pontos de sincronização do modo pânico. IDENT fica de fora de propósito: um
# identificador no meio de uma expressão quebrada não é um bom recomeço.
SINCRONIZA_COMANDO = (INICIO_COMANDO - {T.IDENT}) | FIM_LISTA | {T.SENAO, T.ATE}

# Tokens que podem vir logo depois de um comando quando o ';' foi esquecido.
DEPOIS_DE_COMANDO = {T.FECHA_CHAVE, T.FIM, T.EOF, T.SENAO, T.ATE}

OPS_RELACIONAIS = {T.IGUAL, T.DIFERENTE, T.MENOR, T.MENOR_IGUAL, T.MAIOR, T.MAIOR_IGUAL}
OPS_ADITIVOS = {T.MAIS, T.MENOS}
OPS_MULTIPLICATIVOS = {T.MULT, T.DIV, T.MOD}

# Como cada tipo de token aparece nas mensagens de erro.
_SIMBOLOS = {
    T.MAIS: "+", T.MENOS: "-", T.MULT: "*", T.DIV: "/", T.MOD: "%",
    T.IGUAL: "==", T.DIFERENTE: "!=", T.MENOR: "<", T.MENOR_IGUAL: "<=",
    T.MAIOR: ">", T.MAIOR_IGUAL: ">=", T.ATRIB: "=",
    T.ABRE_PAR: "(", T.FECHA_PAR: ")", T.ABRE_CHAVE: "{", T.FECHA_CHAVE: "}",
    T.PONTO_VIRGULA: ";", T.DOIS_PONTOS: ":", T.VIRGULA: ",", T.PONTO: ".",
}
NOME_TOKEN = {tipo: f"'{lexema}'" for lexema, tipo in reversed(list(PALAVRAS_RESERVADAS.items()))}
NOME_TOKEN.update({tipo: f"'{s}'" for tipo, s in _SIMBOLOS.items()})
NOME_TOKEN.update({T.IDENT: "um identificador", T.NUM_INT: "um número inteiro", T.EOF: "o fim do arquivo"})


def descrever(token: Token) -> str:
    """Como um token encontrado aparece na mensagem de erro."""
    if token.tipo is T.EOF:
        return "o fim do arquivo"
    return f"'{token.lexema}'"


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.erros: list[str] = []
        self._ultima_posicao_erro: Optional[tuple[int, int]] = None

    # ------------------------------------------------------------------
    # Ponto de entrada
    # ------------------------------------------------------------------

    def analisar(self) -> Programa:
        """Analisa o programa inteiro e devolve a AST.

        Mesmo com erros devolve uma AST (parcial); quem chama deve olhar
        self.erros antes de usá-la.
        """
        return self._programa()

    # ------------------------------------------------------------------
    # Utilitários de leitura de tokens
    # ------------------------------------------------------------------

    def _atual(self) -> Token:
        return self.tokens[self.pos]

    def _espiar(self, k: int = 1) -> Token:
        """Token k posições à frente do atual, sem consumir (o último é sempre EOF)."""
        return self.tokens[min(self.pos + k, len(self.tokens) - 1)]

    def _anterior(self) -> Token:
        return self.tokens[self.pos - 1] if self.pos > 0 else self.tokens[0]

    def _verifica(self, *tipos: T) -> bool:
        """True se o token atual é de um dos tipos dados (não consome)."""
        return self._atual().tipo in tipos

    def _avancar(self) -> Token:
        """Consome e devolve o token atual. Nunca passa do EOF."""
        token = self._atual()
        if token.tipo is not T.EOF:
            self.pos += 1
        return token

    def _aceita(self, tipo: T) -> Optional[Token]:
        """Consome o token atual se for do tipo dado; senão não faz nada."""
        if self._verifica(tipo):
            return self._avancar()
        return None

    def _espera(self, tipo: T, contexto: str = "") -> Token:
        """Consome um token obrigatório ou lança SyntacticError."""
        if self._verifica(tipo):
            return self._avancar()
        raise self._erro(f"esperado {NOME_TOKEN[tipo]}{contexto}, mas encontrado {descrever(self._atual())}")

    # ------------------------------------------------------------------
    # Erros e recuperação
    # ------------------------------------------------------------------

    def _erro(self, mensagem: str, token: Optional[Token] = None) -> SyntacticError:
        token = token or self._atual()
        return SyntacticError(token.linha, token.coluna, mensagem)

    def _registrar(self, erro: SyntacticError) -> None:
        """Guarda o erro, ignorando um segundo erro na mesma posição (cascata)."""
        posicao = (erro.linha, erro.coluna)
        if posicao == self._ultima_posicao_erro:
            return
        self._ultima_posicao_erro = posicao
        self.erros.append(str(erro))

    def _sincronizar_comando(self, inicio: int) -> None:
        """Modo pânico: descarta tokens até um ponto seguro para recomeçar.

        Para no ';' (consumindo-o) ou antes de um token de SINCRONIZA_COMANDO.
        Se o comando falhou sem consumir nada, descarta ao menos o token
        atual, para garantir que o parser sempre avança.
        """
        if self.pos == inicio:
            self._avancar()
        while not self._verifica(T.EOF):
            if self._aceita(T.PONTO_VIRGULA):
                return
            if self._verifica(*SINCRONIZA_COMANDO):
                return
            self._avancar()

    def _sincronizar_declaracao(self) -> None:
        """Modo pânico nas declarações: vai até o ';' (consome) ou o '{' do corpo."""
        while not self._verifica(T.EOF, T.ABRE_CHAVE, T.FIM):
            if self._aceita(T.PONTO_VIRGULA):
                return
            self._avancar()

    def _espera_ponto_virgula(self, contexto: str, depois: set[T], inicio_na_linha_seguinte: set[T]) -> None:
        """Exige ';'. Se ele foi esquecido, tenta a recuperação em nível de frase.

        O ';' é considerado "esquecido" (erro registrado, nada descartado)
        quando o próximo token é um de `depois`, ou é um de
        `inicio_na_linha_seguinte` numa linha abaixo do token anterior. Nos
        demais casos lança SyntacticError, e o chamador entra em modo pânico.
        """
        if self._aceita(T.PONTO_VIRGULA):
            return
        atual, anterior = self._atual(), self._anterior()
        if atual.tipo in depois or (atual.tipo in inicio_na_linha_seguinte and atual.linha > anterior.linha):
            self._registrar(SyntacticError(
                anterior.linha, anterior.coluna + len(anterior.lexema),
                f"esperado ';' {contexto}",
            ))
            return
        raise self._erro(f"esperado ';' {contexto}, mas encontrado {descrever(atual)}")

    # ------------------------------------------------------------------
    # programa ::= "programa" IDENT [ declaracoes ] bloco "fim" "."
    # ------------------------------------------------------------------

    def _programa(self) -> Programa:
        inicio = self._atual()
        nome = "?"
        try:
            self._espera(T.PROGRAMA, " no início do arquivo")
            nome = self._espera(T.IDENT, " como nome do programa").lexema
        except SyntacticError as erro:
            self._registrar(erro)
            while not self._verifica(T.VAR, T.ABRE_CHAVE, T.FIM, T.EOF):
                self._avancar()

        declaracoes = self._declaracoes() if self._verifica(T.VAR) else []
        corpo = self._corpo_programa()
        self._final_programa()
        return Programa(nome, declaracoes, corpo, linha=inicio.linha, coluna=inicio.coluna)

    def _corpo_programa(self) -> Bloco:
        """O bloco principal. Sem o '{', registra o erro e analisa os comandos mesmo assim."""
        if self._verifica(T.ABRE_CHAVE):
            return self._bloco()
        atual = self._atual()
        self._registrar(self._erro(
            f"esperado '{{' para iniciar o corpo do programa, mas encontrado {descrever(atual)}"
        ))
        comandos = self._lista_comandos()
        self._aceita(T.FECHA_CHAVE)
        return Bloco(comandos, linha=atual.linha, coluna=atual.coluna)

    def _final_programa(self) -> None:
        try:
            self._espera(T.FIM, " para encerrar o programa")
            self._espera(T.PONTO, " após 'fim'")
        except SyntacticError as erro:
            self._registrar(erro)
            return
        if not self._verifica(T.EOF):
            self._registrar(self._erro(
                f"conteúdo inesperado após 'fim.': encontrado {descrever(self._atual())}"
            ))

    # ------------------------------------------------------------------
    # declaracoes ::= "var" declaracao { declaracao }
    # declaracao  ::= IDENT { "," IDENT } ":" tipo ";"
    # ------------------------------------------------------------------

    def _declaracoes(self) -> list[DeclVar]:
        self._espera(T.VAR)
        if not self._verifica(T.IDENT):
            self._registrar(self._erro(
                f"esperada ao menos uma declaração após 'var', mas encontrado {descrever(self._atual())}"
            ))
        declaracoes: list[DeclVar] = []
        # 'IDENT =' já é uma atribuição: o programador esqueceu o '{' do corpo.
        # Único ponto onde o parser olha 2 tokens à frente, só para dar uma
        # mensagem de erro melhor.
        while self._verifica(T.IDENT) and self._espiar().tipo is not T.ATRIB:
            try:
                declaracoes.extend(self._declaracao())
            except SyntacticError as erro:
                self._registrar(erro)
                self._sincronizar_declaracao()
        return declaracoes

    def _declaracao(self) -> list[DeclVar]:
        nomes = [self._espera(T.IDENT)]
        while self._aceita(T.VIRGULA):
            nomes.append(self._espera(T.IDENT, " após ','"))
        self._espera(T.DOIS_PONTOS, " antes do tipo da variável")
        if not self._verifica(T.INTEIRO, T.BOOLEANO):
            raise self._erro(f"esperado um tipo ('inteiro' ou 'booleano'), mas encontrado {descrever(self._atual())}")
        tipo = self._avancar().lexema
        self._espera_ponto_virgula("ao final da declaração", {T.ABRE_CHAVE}, {T.IDENT})
        return [DeclVar(n.lexema, tipo, linha=n.linha, coluna=n.coluna) for n in nomes]

    # ------------------------------------------------------------------
    # bloco ::= "{" { comando } "}"
    # ------------------------------------------------------------------

    def _bloco(self) -> Bloco:
        abre = self._espera(T.ABRE_CHAVE)
        comandos = self._lista_comandos()
        if not self._aceita(T.FECHA_CHAVE):
            self._registrar(self._erro(
                f"esperado '}}' para fechar o bloco aberto na linha {abre.linha}, coluna {abre.coluna}, "
                f"mas encontrado {descrever(self._atual())}"
            ))
        return Bloco(comandos, linha=abre.linha, coluna=abre.coluna)

    def _lista_comandos(self, terminadores: frozenset[T] = frozenset()) -> list[Comando]:
        """Lê comandos até um token de FIM_LISTA ou de `terminadores`.

        É aqui que fica a recuperação em modo pânico: um comando com erro é
        registrado, descartado, e a análise continua no próximo comando.
        """
        parada = FIM_LISTA | terminadores
        comandos: list[Comando] = []
        while not self._verifica(*parada):
            inicio = self.pos
            try:
                comandos.append(self._comando())
            except SyntacticError as erro:
                self._registrar(erro)
                self._sincronizar_comando(inicio)
        return comandos

    # ------------------------------------------------------------------
    # comando: escolhido pelo token atual (FIRST disjuntos, LL(1))
    # ------------------------------------------------------------------

    def _comando(self) -> Comando:
        tipo = self._atual().tipo
        if tipo is T.IDENT:
            return self._atribuicao()
        if tipo is T.LEIA:
            return self._leitura()
        if tipo is T.ESCREVA:
            return self._escrita()
        if tipo is T.SE:
            return self._condicional()
        if tipo is T.ENQUANTO:
            return self._enquanto()
        if tipo is T.PARA:
            return self._para()
        if tipo is T.REPITA:
            return self._repita()
        if tipo is T.ABRE_CHAVE:
            return self._bloco()
        if tipo is T.SENAO:
            raise self._erro("'senão' sem 'se' correspondente")
        if tipo is T.ATE:
            raise self._erro("'ate' sem 'repita' correspondente")
        raise self._erro(f"esperado um comando, mas encontrado {descrever(self._atual())}")

    def _fim_comando(self) -> None:
        self._espera_ponto_virgula("ao final do comando", DEPOIS_DE_COMANDO, INICIO_COMANDO)

    def _identificador(self, contexto: str = "") -> Identificador:
        token = self._espera(T.IDENT, contexto)
        return Identificador(token.lexema, linha=token.linha, coluna=token.coluna)

    # atribuicao ::= IDENT "=" expressao ";"
    def _atribuicao(self) -> Atribuicao:
        alvo = self._identificador()
        self._espera(T.ATRIB, f" após '{alvo.nome}' na atribuição")
        valor = self._expressao()
        self._fim_comando()
        return Atribuicao(alvo, valor, linha=alvo.linha, coluna=alvo.coluna)

    # leitura ::= "leia" "(" IDENT ")" ";"
    def _leitura(self) -> Leia:
        leia = self._avancar()
        self._espera(T.ABRE_PAR, " após 'leia'")
        alvo = self._identificador(" dentro de 'leia(...)'")
        self._espera(T.FECHA_PAR, " após a variável de 'leia'")
        self._fim_comando()
        return Leia(alvo, linha=leia.linha, coluna=leia.coluna)

    # escrita ::= "escreva" "(" expressao { "," expressao } ")" ";"
    def _escrita(self) -> Escreva:
        escreva = self._avancar()
        self._espera(T.ABRE_PAR, " após 'escreva'")
        argumentos = [self._expressao()]
        while self._aceita(T.VIRGULA):
            argumentos.append(self._expressao())
        self._espera(T.FECHA_PAR, " para fechar 'escreva('")
        self._fim_comando()
        return Escreva(argumentos, linha=escreva.linha, coluna=escreva.coluna)

    # condicional ::= "se" expressao comando [ "senão" comando ]
    def _condicional(self) -> Se:
        se = self._avancar()
        condicao = self._condicao("'se'")
        entao = self._comando()
        senao = None
        # Dangling else: o 'senão' é consumido aqui, pelo 'se' mais interno
        # que ainda está sendo analisado (docs/gramatica.md, seção 6).
        if self._aceita(T.SENAO):
            senao = self._comando()
        return Se(condicao, entao, senao, linha=se.linha, coluna=se.coluna)

    # enquanto ::= "enquanto" expressao comando
    def _enquanto(self) -> Enquanto:
        enquanto = self._avancar()
        condicao = self._condicao("'enquanto'")
        corpo = self._comando()
        return Enquanto(condicao, corpo, linha=enquanto.linha, coluna=enquanto.coluna)

    def _condicao(self, comando: str) -> Optional[Expressao]:
        """Condição de se/enquanto com recuperação local.

        Se a expressão tiver erro, registra-o e pula até o início do corpo
        (um token que inicia um comando), para não perder o corpo inteiro.
        Nesse caso devolve None, já que a AST não será usada.
        """
        try:
            return self._expressao()
        except SyntacticError as erro:
            self._registrar(SyntacticError(erro.linha, erro.coluna, f"{erro.mensagem} (na condição de {comando})"))
            while not self._verifica(*SINCRONIZA_COMANDO):
                self._avancar()
            return None

    # para ::= "para" IDENT "=" expressao "ate" expressao [ "passo" expressao ] comando
    def _para(self) -> Para:
        para = self._avancar()
        variavel = self._identificador(" após 'para'")
        self._espera(T.ATRIB, f" após '{variavel.nome}' no 'para'")
        inicio = self._expressao()
        self._espera(T.ATE, " para indicar o limite do 'para'")
        limite = self._expressao()
        passo = self._expressao() if self._aceita(T.PASSO) else None
        corpo = self._comando()
        return Para(variavel, inicio, limite, passo, corpo, linha=para.linha, coluna=para.coluna)

    # repita ::= "repita" { comando } "ate" expressao ";"
    def _repita(self) -> Repita:
        repita = self._avancar()
        comandos = self._lista_comandos(frozenset({T.ATE}))
        if len(comandos) == 1 and isinstance(comandos[0], Bloco):
            corpo = comandos[0]          # forma 'repita { ... } ate': evita Bloco dentro de Bloco
        else:
            corpo = Bloco(comandos, linha=repita.linha, coluna=repita.coluna)
        self._espera(T.ATE, f" para encerrar o 'repita' da linha {repita.linha}")
        condicao = self._expressao()
        self._fim_comando()
        return Repita(corpo, condicao, linha=repita.linha, coluna=repita.coluna)

    # ------------------------------------------------------------------
    # Expressões: um método por nível de precedência (menor -> maior).
    # Os laços 'while' montam a árvore para a esquerda, o que dá
    # associatividade à esquerda (docs/gramatica.md, seção 5).
    # ------------------------------------------------------------------

    def _expressao(self) -> Expressao:
        return self._expr_ou()

    def _binaria(self, op: Token, esq: Expressao, dir: Expressao) -> Binaria:
        nome = {T.E: "e", T.OU: "ou"}.get(op.tipo, op.lexema)
        return Binaria(nome, esq, dir, linha=op.linha, coluna=op.coluna)

    # expr_ou ::= expr_e { "ou" expr_e }
    def _expr_ou(self) -> Expressao:
        esq = self._expr_e()
        while self._verifica(T.OU):
            op = self._avancar()
            esq = self._binaria(op, esq, self._expr_e())
        return esq

    # expr_e ::= expr_relacional { "e" expr_relacional }
    def _expr_e(self) -> Expressao:
        esq = self._expr_relacional()
        while self._verifica(T.E):
            op = self._avancar()
            esq = self._binaria(op, esq, self._expr_relacional())
        return esq

    # expr_relacional ::= expr_aditiva [ op_relacional expr_aditiva ]   (não associativo)
    def _expr_relacional(self) -> Expressao:
        esq = self._expr_aditiva()
        if self._verifica(*OPS_RELACIONAIS):
            op = self._avancar()
            esq = self._binaria(op, esq, self._expr_aditiva())
            if self._verifica(*OPS_RELACIONAIS):
                raise self._erro(
                    f"operadores relacionais não podem ser encadeados ('{op.lexema}' seguido de "
                    f"'{self._atual().lexema}'); use parênteses ou 'e'"
                )
        return esq

    # expr_aditiva ::= expr_multiplicativa { ( "+" | "-" ) expr_multiplicativa }
    def _expr_aditiva(self) -> Expressao:
        esq = self._expr_multiplicativa()
        while self._verifica(*OPS_ADITIVOS):
            op = self._avancar()
            esq = self._binaria(op, esq, self._expr_multiplicativa())
        return esq

    # expr_multiplicativa ::= expr_unaria { ( "*" | "/" | "%" ) expr_unaria }
    def _expr_multiplicativa(self) -> Expressao:
        esq = self._expr_unaria()
        while self._verifica(*OPS_MULTIPLICATIVOS):
            op = self._avancar()
            esq = self._binaria(op, esq, self._expr_unaria())
        return esq

    # expr_unaria ::= ( "-" | "não" ) expr_unaria | primaria   (recursão à direita)
    def _expr_unaria(self) -> Expressao:
        if self._verifica(T.MENOS, T.NAO):
            op = self._avancar()
            nome = "não" if op.tipo is T.NAO else "-"
            return Unaria(nome, self._expr_unaria(), linha=op.linha, coluna=op.coluna)
        return self._primaria()

    # primaria ::= NUM_INT | "verdadeiro" | "falso" | IDENT | "(" expressao ")"
    def _primaria(self) -> Expressao:
        token = self._atual()
        if token.tipo is T.NUM_INT:
            self._avancar()
            return Numero(token.valor, linha=token.linha, coluna=token.coluna)
        if token.tipo in (T.VERDADEIRO, T.FALSO):
            self._avancar()
            return Booleano(token.valor, linha=token.linha, coluna=token.coluna)
        if token.tipo is T.IDENT:
            self._avancar()
            return Identificador(token.lexema, linha=token.linha, coluna=token.coluna)
        if token.tipo is T.ABRE_PAR:
            self._avancar()
            expressao = self._expressao()
            self._espera(T.FECHA_PAR, f" para fechar '(' aberto na linha {token.linha}, coluna {token.coluna}")
            return expressao
        raise self._erro(f"esperada uma expressão, mas encontrado {descrever(token)}")


def analisar_sintaxe(tokens: list[Token]) -> tuple[Programa, list[str]]:
    """Atalho: roda o parser e devolve (AST, erros sintáticos)."""
    parser = Parser(tokens)
    programa = parser.analisar()
    return programa, parser.erros
