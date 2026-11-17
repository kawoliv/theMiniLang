"""Permite executar o compilador como módulo: py -m minilang <arquivo.ml> [--tokens] [--ast]

A lógica da linha de comando fica em minilang/cli.py.
"""

from minilang.cli import main

main()
