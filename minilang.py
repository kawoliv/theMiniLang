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

Uso:
    py minilang.py <arquivo.mlg> [--tokens] [--ast]

A lógica da linha de comando fica em minilang/cli.py.
"""

from minilang.cli import main

if __name__ == "__main__":
    main()
