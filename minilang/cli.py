"""Linha de comando do compilador MiniLang.

Usado tanto por `py minilang.py ...` (raiz do projeto) quanto por
`py -m minilang ...`. Executa as fases em sequência:

    código-fonte -> Lexer (M1) -> Parser + AST (M2) -> [M3, M4: a fazer]

As fases continuam mesmo depois de um erro, para que todos os problemas
apareçam em uma única execução; no fim, se houve erro, sai com código 1.
"""

import argparse
import sys
from pathlib import Path

from minilang.arvore import formatar_arvore
from minilang.lexer import Lexer
from minilang.parser import analisar_sintaxe
from minilang.tokens import TokenType, categoria

VERSAO = "MiniLang Compiler v0.3.0 (Marco 2 - Sintático + AST)"


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
        epilog="Exemplo: py minilang.py exemplos/validos/fatorial.mlg --ast",
    )
    parser.add_argument("arquivo", nargs="?", help="Caminho do código-fonte MiniLang (.mlg ou .ml)")
    parser.add_argument("--tokens", action="store_true", help="Exibe a tabela de tokens (M1)")
    parser.add_argument("--ast", action="store_true", help="Exibe a Árvore Sintática Abstrata (M2)")
    parser.add_argument("--symbols", action="store_true", help="Exibe a Tabela de Símbolos (M3, ainda não implementado)")
    parser.add_argument("--optimize", action="store_true", help="Aplica otimizações (M4, ainda não implementado)")
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
        print(f"Erros encontrados em {caminho.name}:", file=sys.stderr)
        for erro in erros:
            print(f"  {erro}", file=sys.stderr)
        print(
            f"\n[FALHA] Compilação interrompida: {len(lexer.erros)} erro(s) léxico(s) "
            f"e {len(erros_sintaticos)} erro(s) sintático(s).",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.ast:
        print(formatar_arvore(programa))

    for opcao, marco in (("symbols", "M3"), ("optimize", "M4")):
        if getattr(args, opcao):
            print(f"[AVISO] --{opcao} ainda não está disponível ({marco}).", file=sys.stderr)

    print(f"[SUCESSO] {caminho.name}: análise léxica e sintática concluídas sem erros "
          f"({len(tokens)} tokens).")
