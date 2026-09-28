import sys
import os
from minilang.lexer import Lexer

def main():
    if len(sys.argv) < 2:
        print("Uso: python -m minilang <arquivo.mlg> [--tokens]")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    mostrar_tokens = "--tokens" in sys.argv

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O ficheiro '{caminho_arquivo}' não foi encontrado.")
        sys.exit(1)

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        codigo_fonte = f.read()

    lexer = Lexer(codigo_fonte)
    tokens = lexer.tokenizar()

    if lexer.erros:
        print("Erros léxicos encontrados:")
        for erro in lexer.erros:
            print(erro)
        sys.exit(1)

    if mostrar_tokens:
        for token in tokens:
            print(token)

if __name__ == "__main__":
    main()
