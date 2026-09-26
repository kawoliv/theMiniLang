import sys
import os
from minilang.lexer import Lexer

def main():
    # Verifica se o utilizador passou os argumentos corretos
    if len(sys.argv) < 2:
        print("Uso: py -m minilang <arquivo.mlg> [--tokens]")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    mostrar_tokens = "--tokens" in sys.argv

    # Verifica se o ficheiro existe antes de tentar abrir
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O ficheiro '{caminho_arquivo}' não foi encontrado.")
        sys.exit(1)

    # Lê o conteúdo do ficheiro-fonte
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        codigo_fonte = f.read()

    # Inicia a análise léxica
    lexer = Lexer(codigo_fonte)
    tokens = lexer.tokenizar()

    # Se existirem erros léxicos, exibe-os e interrompe a execução
    if lexer.erros:
        print("Erros léxicos encontrados:")
        for erro in lexer.erros:
            print(erro)
        sys.exit(1)

    # Se não houver erros e a flag --tokens foi passada, imprime os tokens
    if mostrar_tokens:
        for token in tokens:
            print(token)

if __name__ == "__main__":
    main()