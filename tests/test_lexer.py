"""Suíte de testes automatizados para o Analisador Léxico da MiniLang."""

import unittest
from minilang.lexer import Lexer
from minilang.tokens import TokenType, categoria


class TestLexer(unittest.TestCase):
    def test_palavras_reservadas_e_extensao_d(self):
        fonte = (
            "programa var inteiro booleano se senão senao enquanto escreva leia "
            "verdadeiro falso e ou não nao fim para ate passo repita"
        )
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 0)

        tipos = [t.tipo for t in tokens[:-1]] # exclui EOF
        self.assertIn(TokenType.PROGRAMA, tipos)
        self.assertIn(TokenType.VAR, tipos)
        self.assertIn(TokenType.INTEIRO, tipos)
        self.assertIn(TokenType.BOOLEANO, tipos)
        self.assertIn(TokenType.SE, tipos)
        self.assertIn(TokenType.SENAO, tipos)
        self.assertIn(TokenType.ENQUANTO, tipos)
        self.assertIn(TokenType.ESCREVA, tipos)
        self.assertIn(TokenType.LEIA, tipos)
        self.assertIn(TokenType.VERDADEIRO, tipos)
        self.assertIn(TokenType.FALSO, tipos)
        self.assertIn(TokenType.E, tipos)
        self.assertIn(TokenType.OU, tipos)
        self.assertIn(TokenType.NAO, tipos)
        self.assertIn(TokenType.FIM, tipos)
        # Extensão D
        self.assertIn(TokenType.PARA, tipos)
        self.assertIn(TokenType.ATE, tipos)
        self.assertIn(TokenType.PASSO, tipos)
        self.assertIn(TokenType.REPITA, tipos)

    def test_identificadores_e_numeros(self):
        fonte = "x1 = 42 + _var2"
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 0)
        self.assertEqual(tokens[0].tipo, TokenType.IDENT)
        self.assertEqual(tokens[0].lexema, "x1")
        self.assertEqual(tokens[1].tipo, TokenType.ATRIB)
        self.assertEqual(tokens[2].tipo, TokenType.NUM_INT)
        self.assertEqual(tokens[2].lexema, "42")
        self.assertEqual(tokens[3].tipo, TokenType.MAIS)
        self.assertEqual(tokens[4].tipo, TokenType.IDENT)
        self.assertEqual(tokens[4].lexema, "_var2")

    def test_operadores_relacionais_e_atribuicao(self):
        fonte = "== != <= >= = < >"
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 0)
        tipos = [t.tipo for t in tokens[:-1]]
        esperados = [
            TokenType.IGUAL,
            TokenType.DIFERENTE,
            TokenType.MENOR_IGUAL,
            TokenType.MAIOR_IGUAL,
            TokenType.ATRIB,
            TokenType.MENOR,
            TokenType.MAIOR,
        ]
        self.assertEqual(tipos, esperados)

    def test_operadores_aritmeticos_e_delimitadores(self):
        fonte = "+ - * / % ( ) { } ; : , ."
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 0)
        tipos = [t.tipo for t in tokens[:-1]]
        esperados = [
            TokenType.MAIS, TokenType.MENOS, TokenType.MULT, TokenType.DIV, TokenType.MOD,
            TokenType.ABRE_PAR, TokenType.FECHA_PAR, TokenType.ABRE_CHAVE, TokenType.FECHA_CHAVE,
            TokenType.PONTO_VIRGULA, TokenType.DOIS_PONTOS, TokenType.VIRGULA, TokenType.PONTO
        ]
        self.assertEqual(tipos, esperados)

    def test_posicao_linha_coluna(self):
        fonte = "var a;\n  b = 10;"
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 0)

        # 'a' na linha 1, coluna 5
        token_a = tokens[1]
        self.assertEqual(token_a.lexema, "a")
        self.assertEqual(token_a.linha, 1)
        self.assertEqual(token_a.coluna, 5)

        # 'b' na linha 2, coluna 3
        token_b = tokens[3]
        self.assertEqual(token_b.lexema, "b")
        self.assertEqual(token_b.linha, 2)
        self.assertEqual(token_b.coluna, 3)

    def test_descarte_de_espacos_e_comentarios(self):
        fonte = "a = 1; # isto e um comentario\nb = 2; # outro comentario"
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 0)
        lexemas = [t.lexema for t in tokens if t.tipo != TokenType.EOF]
        self.assertEqual(lexemas, ["a", "=", "1", ";", "b", "=", "2", ";"])

    def test_erros_lexicos_caracteres_invalidos(self):
        fonte = "var a @ 10;"
        lexer = Lexer(fonte)
        tokens = lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 1)
        self.assertIn("caractere inesperado '@'", lexer.erros[0])

    def test_erro_exclamacao_solta(self):
        fonte = "se a ! b"
        lexer = Lexer(fonte)
        lexer.tokenizar()
        self.assertEqual(len(lexer.erros), 1)
        self.assertIn("caractere inesperado '!'", lexer.erros[0])

    def test_funcao_helper_categoria(self):
        self.assertEqual(categoria(TokenType.PROGRAMA), "palavra reservada")
        self.assertEqual(categoria(TokenType.MAIS), "operador")
        self.assertEqual(categoria(TokenType.PONTO_VIRGULA), "delimitador")
        self.assertEqual(categoria(TokenType.IDENT), "identificador")
        self.assertEqual(categoria(TokenType.NUM_INT), "literal inteiro")
        self.assertEqual(categoria(TokenType.EOF), "fim de arquivo")


if __name__ == "__main__":
    unittest.main()
