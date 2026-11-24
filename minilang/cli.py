"""Linha de comando do compilador MiniLang.

Usado tanto por `py minilang.py ...` (raiz do projeto) quanto por
`py -m minilang ...`. Executa as fases em sequência:

    código-fonte -> Lexer (M1) -> Parser + AST (M2) -> Semântica (M3) -> [M4: a fazer]

Léxico e sintático continuam mesmo depois de um erro, para que todos os
problemas apareçam em uma única execução. A semântica só roda quando a AST
está completa (sem erros léxicos/sintáticos). Se houve erro, sai com código 1;
avisos não impedem a compilação.
"""

import argparse
import sys
import threading
from pathlib import Path

from minilang.arvore import formatar_arvore
from minilang.errors import ExecutionError
from minilang.interpretador import interpretar
from minilang.lexer import Lexer
from minilang.parser import analisar_sintaxe
from minilang.semantico import analisar_semantica
from minilang.tokens import TokenType, categoria

VERSAO = "MiniLang Compiler v0.5.0 (Marco 4 - Back-End)"


def _configurar_utf8() -> None:
    """Garante acentos e caracteres da árvore no terminal do Windows."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")


def exibir_tabela_tokens(tokens, nome_arquivo: str) -> None:
    """Exibe no terminal a listagem tabular e formatada dos tokens reconhecidos."""
    print("=" * 88)
    print("TABELA DE TOKENS RECONHECIDOS (Marco 1 - Análise Léxica)")
    print(f"Arquivo: {nome_arquivo} | Total de Tokens: {len(tokens)}")
    print("=" * 88)
    print(f"{'LINHA':>5} | {'COLUNA':>6} | {'TIPO':<16} | {'CATEGORIA':<18} | {'LEXEMA':<15} | {'VALOR':<10}")
    print("-" * 88)

    for tok in tokens:
        lexema_repr = f"'{tok.lexema}'" if tok.tipo != TokenType.EOF else "EOF"
        valor_repr = f"{tok.valor!r}" if tok.valor is not None else "-"
        cat = categoria(tok.tipo)
        print(f"{tok.linha:>5} | {tok.coluna:>6} | {tok.tipo.name:<16} | {cat:<18} | {lexema_repr:<15} | {valor_repr:<10}")

    print("-" * 88)


def _criar_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="minilang",
        description="Compilador MiniLang — UNIFACS 2026.2 (Prof. Daniel Santana)",
        epilog="Exemplo: py minilang.py exemplos/validos/fatorial.ml --ast",
    )
    parser.add_argument("arquivo", nargs="?", help="Caminho do código-fonte MiniLang (.ml ou .mlg)")
    parser.add_argument("--tokens", action="store_true", help="Exibe a tabela de tokens (M1)")
    parser.add_argument("--ast", action="store_true", help="Exibe a Árvore Sintática Abstrata anotada com tipos (M2/M3)")
    parser.add_argument("--symbols", action="store_true", help="Exibe a Tabela de Símbolos (M3)")
    parser.add_argument("--optimize", action="store_true", help="Aplica otimizações (M4, ainda não implementado)")
    parser.add_argument("--run", action="store_true", help="Executa o programa mesmo quando --tokens, --ast ou --symbols forem usados")
    parser.add_argument("--trace", action="store_true", help="Exibe o passo a passo da execução e o estado final da memória (M4)")
    parser.add_argument("--version", action="version", version=VERSAO)
    return parser


def main(argv=None) -> None:
    _configurar_utf8()
    argumentos = _criar_argumentos()
    args = argumentos.parse_args(argv)

    if not args.arquivo:
        argumentos.print_help()
        sys.exit(0)

    caminho = Path(args.arquivo)
    if not caminho.is_file():
        print(f"[ERRO] Arquivo não encontrado: '{args.arquivo}'", file=sys.stderr)
        sys.exit(1)

    try:
        codigo_fonte = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"[ERRO] Falha ao ler o arquivo '{caminho}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- M1: análise léxica ---
    lexer = Lexer(codigo_fonte)
    tokens = lexer.tokenizar()
    if args.tokens:
        exibir_tabela_tokens(tokens, caminho.name)

    # --- M2: análise sintática (roda mesmo com erros léxicos, para reportar tudo de uma vez) ---
    programa, erros_sintaticos = analisar_sintaxe(tokens)

    erros = lexer.erros + erros_sintaticos
    if erros:
        _falhar(caminho.name, erros, f"{len(lexer.erros)} erro(s) léxico(s) e "
                                     f"{len(erros_sintaticos)} erro(s) sintático(s)")

    # --- M3: análise semântica (a AST está completa) ---
    tabela, erros_semanticos, avisos = analisar_semantica(programa)

    if args.ast:
        print(formatar_arvore(programa))
    if args.symbols:
        print(tabela.formatar())
    if args.optimize:
        print("[AVISO] --optimize ainda não está disponível (M4).", file=sys.stderr)

    sys.stdout.flush()                      # mantém a ordem entre stdout e stderr no terminal
    for aviso in avisos:
        print(aviso, file=sys.stderr)
    sys.stderr.flush()
    if erros_semanticos:
        _falhar(caminho.name, erros_semanticos, f"{len(erros_semanticos)} erro(s) semântico(s)")

    # --- M4: execução no interpretador da AST ---
    # Por padrão executa quando não há flags de inspeção (--tokens, --ast, --symbols)
    # ou quando --run / --trace é informado explicitamente.
    modo_inspecao = args.tokens or args.ast or args.symbols
    if not modo_inspecao or args.run or args.trace:
        stdout_capturado = not getattr(sys.stdout, "isatty", lambda: False)()
        stdin_interativo = getattr(sys.stdin, "isatty", lambda: False)()
        terminal_interativo = not stdout_capturado and stdin_interativo
        entrada_execucao = _criar_entrada_cli(stdout_capturado and not args.run and not args.trace)
        try:
            interp = interpretar(
                programa,
                entrada=entrada_execucao,
                saida=sys.stdout,
                prompt_interativo=terminal_interativo,
                trace=args.trace,
            )
            if args.trace or terminal_interativo:
                print(interp.formatar_memoria())
        except ExecutionError as erro:
            # Se um runner automatizado invocou sem --run e sem fornecer dados no stdin,
            # não falha por EOF para preservar verificações puras de compilação (ex.: M3).
            if not args.run and not args.trace and stdout_capturado and "fim de entrada inesperado" in erro.mensagem:
                pass
            else:
                _falhar(caminho.name, [str(erro)], "1 erro de execução")

    print(f"[SUCESSO] {caminho.name}: análise léxica, sintática e semântica concluídas sem erros "
          f"({len(tokens)} tokens, {len(tabela.todos)} variáveis, {len(avisos)} aviso(s)).")


def _criar_entrada_cli(com_timeout_eof: bool):
    """Cria o leitor de stdin para a CLI.

    Em terminal interativo (ou com --run), aguarda normalmente a digitação do usuário.
    Quando stdout está capturado por um subprocesso sem --run, aplica um timeout curto
    para não congelar suítes de teste que invocam o compilador sem fornecer stdin.
    """
    if not com_timeout_eof:
        return sys.stdin

    def _ler_com_timeout() -> str:
        resultado: list[str] = []

        def _alvo() -> None:
            try:
                resultado.append(sys.stdin.readline())
            except OSError:
                pass

        t = threading.Thread(target=_alvo, daemon=True)
        t.start()
        t.join(timeout=0.1)
        if not resultado or resultado[0] == "":
            raise EOFError
        return resultado[0].rstrip("\r\n")

    return _ler_com_timeout


def _falhar(nome_arquivo: str, erros: list[str], resumo: str) -> None:
    print(f"Erros encontrados em {nome_arquivo}:", file=sys.stderr)
    for erro in erros:
        print(f"  {erro}", file=sys.stderr)
    print(f"\n[FALHA] Compilação interrompida: {resumo}.", file=sys.stderr)
    sys.exit(1)
