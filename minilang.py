#!/usr/bin/env python3
"""Compilador MiniLang - Projeto de Avaliação A3
Teoria da Computação e Compiladores (0006964) - UNIFACS 2026.2
Docente: Prof. Daniel Santana

Equipe:
    - Kawan Oliveira
    - João Guilherme Perrone Hohlenwerger
    - Daniel Costa
    - João Spinola Falcão
    - Pedro Adaime Ribeiro
    - Isabelle Maciel dos Santos
"""

import argparse
import os
import sys
from pathlib import Path

# Garante saída UTF-8 no terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from minilang.lexer import Lexer
from minilang.tokens import TokenType, categoria


def exibir_tabela_tokens(tokens, nome_arquivo: str) -> None:
    """Exibe no terminal a listagem tabular e formatada dos tokens reconhecidos."""
    print("=" * 88)
    print(f"TABELA DE TOKENS RECONHECIDOS (Marco 1 - Análise Léxica)")
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


def main():
    parser = argparse.ArgumentParser(
        description="Compilador MiniLang — UNIFACS 2026.2 (Prof. Daniel Santana)",
        epilog="Exemplo: python minilang.py exemplos/validos/fatorial.mlg --tokens"
    )
    parser.add_argument("arquivo", nargs="?", help="Caminho do código-fonte MiniLang (.mlg ou .ml)")
    parser.add_argument("--tokens", action="store_true", help="Executa a análise léxica e exibe a tabela de tokens (M1)")
    parser.add_argument("--ast", action="store_true", help="Exibe a Árvore Sintática Abstrata (M2)")
    parser.add_argument("--symbols", action="store_true", help="Exibe a Tabela de Símbolos (M3)")
    parser.add_argument("--optimize", action="store_true", help="Aplica otimizações de código intermediário (M4)")
    parser.add_argument("--version", action="version", version="MiniLang Compiler v0.2.0 (Marco 1 - Léxico Concluído)")

    args = parser.parse_args()

    if not args.arquivo:
        parser.print_help()
        sys.exit(0)

    caminho = Path(args.arquivo)
    if not caminho.is_file():
        print(f"[ERRO] Arquivo não encontrado: '{args.arquivo}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            codigo_fonte = f.read()
    except Exception as e:
        print(f"[ERRO] Falha ao ler o arquivo '{caminho}': {e}", file=sys.stderr)
        sys.exit(1)

    lexer = Lexer(codigo_fonte)
    tokens = lexer.tokenizar()

    if lexer.erros:
        print("Erros léxicos detectados:", file=sys.stderr)
        for erro in lexer.erros:
            print(f"  {erro}", file=sys.stderr)
        print(f"\n[FALHA] Compilação interrompida com {len(lexer.erros)} erro(s) léxico(s).", file=sys.stderr)
        sys.exit(1)

    if args.tokens:
        exibir_tabela_tokens(tokens, caminho.name)
        print(f"[SUCESSO] Análise léxica concluída com 0 erros ({len(tokens)} tokens gerados).")
        sys.exit(0)

    # Modo padrão provisório até a integração do M2
    print(f"=== Compilador MiniLang (UNIFACS 2026.2) ===")
    print(f"Arquivo processado: {caminho.name}")
    print(f"Análise léxica (M1): OK ({len(tokens)} tokens gerados sem erros).")
    print("Dica: Use '--tokens' para inspecionar a tabela detalhada de tokens.")


if __name__ == "__main__":
    main()
