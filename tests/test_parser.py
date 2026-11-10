"""Suíte de testes automatizados para o Analisador Sintático (M2) da MiniLang."""

import subprocess
import sys
import unittest
from pathlib import Path

from minilang.arvore import (
    Atribuicao, Binaria, Bloco, Booleano, DeclVar, Enquanto, Escreva, Identificador,
    Leia, Numero, Para, Programa, Repita, Se, Unaria, Visitante, formatar_arvore,
)
from minilang.lexer import Lexer
from minilang.parser import analisar_sintaxe

RAIZ = Path(__file__).resolve().parent.parent
EXEMPLOS = RAIZ / "exemplos"

MODELO = (
    "programa teste\n"
    "var x, y, z: inteiro;\n"
    "    a, b: booleano;\n"
    "{\n"
    "%s\n"
    "}\n"
    "fim."
)


def analisar(fonte: str):
    """Roda léxico + parser e devolve (AST, erros sintáticos)."""
    tokens = Lexer(fonte).tokenizar()
    return analisar_sintaxe(tokens)


def comandos(corpo: str):
    """Analisa `corpo` dentro de um programa padrão e devolve a lista de comandos."""
    programa, erros = analisar(MODELO % corpo)
    assert not erros, erros
    return programa.corpo.comandos


def expressao(texto: str):
    """Analisa uma expressão (como valor de uma atribuição) e devolve o nó."""
    return comandos(f"x = {texto};")[0].valor


def forma(no) -> str:
    """Representação compacta e totalmente parentesada de uma expressão."""
    if isinstance(no, Numero):
        return str(no.valor)
    if isinstance(no, Booleano):
        return "verdadeiro" if no.valor else "falso"
    if isinstance(no, Identificador):
        return no.nome
    if isinstance(no, Unaria):
        return f"({no.op} {forma(no.operando)})"
    if isinstance(no, Binaria):
        return f"({forma(no.esq)} {no.op} {forma(no.dir)})"
    raise TypeError(no)


class TestProgramasValidos(unittest.TestCase):
    def test_aceita_todos_os_exemplos_validos(self):
        arquivos = sorted((EXEMPLOS / "validos").glob("*.mlg"))
        self.assertGreaterEqual(len(arquivos), 7)
        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                lexer = Lexer(arquivo.read_text(encoding="utf-8"))
                programa, erros = analisar_sintaxe(lexer.tokenizar())
                self.assertEqual(lexer.erros, [])
                self.assertEqual(erros, [])
                self.assertIsInstance(programa, Programa)

    def test_estrutura_do_programa_e_declaracoes(self):
        programa, erros = analisar(MODELO % "leia(x);")
        self.assertEqual(erros, [])
        self.assertEqual(programa.nome, "teste")
        self.assertEqual(
            [(d.nome, d.tipo) for d in programa.declaracoes],
            [("x", "inteiro"), ("y", "inteiro"), ("z", "inteiro"), ("a", "booleano"), ("b", "booleano")],
        )
        # Posição de declaração (será usada na tabela de símbolos do M3)
        self.assertEqual((programa.declaracoes[1].linha, programa.declaracoes[1].coluna), (2, 8))
        self.assertIsInstance(programa.corpo, Bloco)

    def test_programa_sem_var(self):
        programa, erros = analisar("programa p { escreva(1); } fim.")
        self.assertEqual(erros, [])
        self.assertEqual(programa.declaracoes, [])

    def test_multiplos_blocos_var(self):
        fonte = (
            "programa teste\n"
            "var a: inteiro;\n"
            "var b: booleano;\n"
            "var c, d: inteiro;\n"
            "{\n"
            "    a = 10;\n"
            "}\n"
            "fim."
        )
        programa, erros = analisar(fonte)
        self.assertEqual(erros, [])
        self.assertEqual(
            [(d.nome, d.tipo) for d in programa.declaracoes],
            [("a", "inteiro"), ("b", "booleano"), ("c", "inteiro"), ("d", "inteiro")],
        )

    def test_comandos_basicos(self):
        cmds = comandos("leia(x);\nx = x + 1;\nescreva(x, a);\n{ y = 2; }")
        self.assertEqual([type(c) for c in cmds], [Leia, Atribuicao, Escreva, Bloco])
        self.assertEqual(cmds[0].alvo.nome, "x")
        self.assertEqual(len(cmds[2].argumentos), 2)
        self.assertEqual((cmds[1].linha, cmds[1].coluna), (6, 1))

    def test_enquanto(self):
        laco = comandos("enquanto x > 0 x = x - 1;")[0]
        self.assertIsInstance(laco, Enquanto)
        self.assertEqual(forma(laco.condicao), "(x > 0)")
        self.assertIsInstance(laco.corpo, Atribuicao)


class TestExtensaoD(unittest.TestCase):
    def test_para_com_passo(self):
        laco = comandos("para x = 10 até 1 passo -1 { escreva(x); }")[0]
        self.assertIsInstance(laco, Para)
        self.assertEqual(laco.variavel.nome, "x")
        self.assertEqual(forma(laco.inicio), "10")
        self.assertEqual(forma(laco.limite), "1")
        self.assertEqual(forma(laco.passo), "(- 1)")
        self.assertIsInstance(laco.corpo, Bloco)

    def test_para_sem_passo(self):
        laco = comandos("para x = 1 ate y + 1 escreva(x);")[0]
        self.assertIsNone(laco.passo)
        self.assertEqual(forma(laco.limite), "(y + 1)")
        self.assertIsInstance(laco.corpo, Escreva)

    def test_repita_com_bloco(self):
        laco = comandos("repita { x = x + 1; escreva(x); } ate x >= 5;")[0]
        self.assertIsInstance(laco, Repita)
        self.assertEqual(len(laco.corpo.comandos), 2)
        self.assertEqual(forma(laco.condicao), "(x >= 5)")

    def test_repita_com_lista_de_comandos(self):
        laco = comandos("repita x = x + 1; escreva(x); ate x == 3;")[0]
        self.assertEqual([type(c) for c in laco.corpo.comandos], [Atribuicao, Escreva])


class TestPrecedenciaEAssociatividade(unittest.TestCase):
    def test_multiplicacao_antes_da_soma(self):
        self.assertEqual(forma(expressao("1 + 2 * 3")), "(1 + (2 * 3))")
        self.assertEqual(forma(expressao("1 * 2 + 3")), "((1 * 2) + 3)")

    def test_associatividade_a_esquerda(self):
        self.assertEqual(forma(expressao("10 - 3 - 2")), "((10 - 3) - 2)")
        self.assertEqual(forma(expressao("100 / 10 / 2")), "((100 / 10) / 2)")
        self.assertEqual(forma(expressao("a ou b ou a")), "((a ou b) ou a)")

    def test_parenteses_mudam_a_arvore(self):
        self.assertEqual(forma(expressao("(1 + 2) * 3")), "((1 + 2) * 3)")
        self.assertEqual(forma(expressao("10 - (3 - 2)")), "(10 - (3 - 2))")

    def test_relacional_entre_aritmeticas(self):
        self.assertEqual(forma(expressao("x + 1 > y * 2")), "((x + 1) > (y * 2))")

    def test_niveis_logicos(self):
        self.assertEqual(forma(expressao("a ou b e x == 1")), "(a ou (b e (x == 1)))")

    def test_unarios(self):
        self.assertEqual(forma(expressao("- - x")), "(- (- x))")
        self.assertEqual(forma(expressao("-x * 2")), "((- x) * 2)")
        self.assertEqual(forma(expressao("não a e b")), "((não a) e b)")
        self.assertEqual(forma(expressao("nao (x < y)")), "(não (x < y))")

    def test_literais_booleanos_e_posicao_do_operador(self):
        no = expressao("verdadeiro ou falso")
        self.assertEqual(forma(no), "(verdadeiro ou falso)")
        self.assertEqual((no.linha, no.coluna), (5, 16))   # posição do 'ou'

    def test_relacionais_nao_sao_associativos(self):
        _, erros = analisar(MODELO % "a = 1 < 2 < 3;")
        self.assertEqual(len(erros), 1)
        self.assertIn("Linha 5, Coluna 11", erros[0])     # o segundo '<'
        self.assertIn("não podem ser encadeados", erros[0])


class TestDanglingElse(unittest.TestCase):
    def test_dangling_else_associa_ao_se_mais_proximo(self):
        externo = comandos("se a se b x = 1; senão x = 2;")[0]
        self.assertIsInstance(externo, Se)
        self.assertIsNone(externo.senao)               # o externo NÃO tem senão
        interno = externo.entao
        self.assertIsInstance(interno, Se)
        self.assertIsInstance(interno.senao, Atribuicao)
        self.assertEqual(interno.senao.valor.valor, 2)

    def test_chaves_mudam_o_dono_do_senao(self):
        externo = comandos("se a { se b x = 1; } senao x = 2;")[0]
        self.assertIsInstance(externo.senao, Atribuicao)
        self.assertIsNone(externo.entao.comandos[0].senao)

    def test_cadeia_senao_se(self):
        se = comandos("se x == 0 y = 0; senao se x == 1 y = 1; senao y = 2;")[0]
        self.assertIsInstance(se.senao, Se)
        self.assertIsInstance(se.senao.senao, Atribuicao)


class TestErrosSintaticos(unittest.TestCase):
    def test_rejeita_exemplos_invalidos_sintaticos(self):
        arquivos = sorted((EXEMPLOS / "invalidos").glob("sintatico_*.mlg"))
        self.assertGreaterEqual(len(arquivos), 4)
        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                _, erros = analisar(arquivo.read_text(encoding="utf-8"))
                self.assertGreater(len(erros), 0)
                for erro in erros:
                    self.assertRegex(erro, r"^\[SINTÁTICO\] Linha \d+, Coluna \d+: .+")

    def test_falta_ponto_virgula_posicao_e_recuperacao(self):
        programa, erros = analisar(MODELO % "x = 10\ny = x * 2;")
        self.assertEqual(erros, ["[SINTÁTICO] Linha 5, Coluna 7: esperado ';' ao final do comando"])
        # O comando seguinte não foi perdido
        self.assertEqual(len(programa.corpo.comandos), 2)

    def test_erro_em_declaracao_nao_engole_var_seguinte(self):
        fonte = "programa t\nvar x inteiro\nvar y: inteiro;\n{ y = 1; }\nfim."
        programa, erros = analisar(fonte)
        self.assertEqual(len(erros), 1)
        # O modo pânico para no 'var' e 'y' continua declarado
        self.assertEqual([d.nome for d in programa.declaracoes], ["y"])

    def test_ponto_virgula_esquecido_antes_de_var(self):
        fonte = "programa t\nvar x: inteiro\nvar y: inteiro;\n{ x = 1; }\nfim."
        programa, erros = analisar(fonte)
        self.assertEqual(erros, ["[SINTÁTICO] Linha 2, Coluna 15: esperado ';' ao final da declaração"])
        # Recuperação em nível de frase: nenhuma declaração é perdida
        self.assertEqual([d.nome for d in programa.declaracoes], ["x", "y"])

    def test_parentese_nao_fechado(self):
        _, erros = analisar(MODELO % "x = (1 + 2;")
        self.assertEqual(len(erros), 1)
        self.assertIn("Linha 5, Coluna 11", erros[0])
        self.assertIn("para fechar '(' aberto na linha 5, coluna 5", erros[0])

    def test_expressao_incompleta(self):
        _, erros = analisar(MODELO % "x = 1 + ;")
        self.assertEqual(erros, ["[SINTÁTICO] Linha 5, Coluna 9: esperada uma expressão, mas encontrado ';'"])

    def test_reporta_multiplos_erros_em_uma_execucao(self):
        corpo = "x = ;\nescreva(x, y;\nse x > { y = 1; }\nleia(1);\nsenão y = 2;\nescreva(x);"
        programa, erros = analisar(MODELO % corpo)
        linhas = [int(e.split("Linha ")[1].split(",")[0]) for e in erros]
        self.assertEqual(linhas, [5, 6, 7, 8, 9])
        # Depois de todos os erros, o último comando ainda foi reconhecido
        self.assertIsInstance(programa.corpo.comandos[-1], Escreva)

    def test_erros_em_declaracoes(self):
        _, erros = analisar("programa p var x inteiro; y: real; z: inteiro;\n{ } fim.")
        self.assertEqual(len(erros), 2)
        self.assertIn("esperado ':'", erros[0])
        self.assertIn("esperado um tipo", erros[1])

    def test_senao_sem_se(self):
        _, erros = analisar(MODELO % "senão x = 1;")
        self.assertEqual(erros, ["[SINTÁTICO] Linha 5, Coluna 1: 'senão' sem 'se' correspondente"])

    def test_falta_abre_chave_do_corpo(self):
        programa, erros = analisar("programa p var x: inteiro; x = 1; } fim.")
        self.assertEqual(len(erros), 1)
        self.assertIn("esperado '{' para iniciar o corpo do programa", erros[0])
        self.assertIsInstance(programa.corpo.comandos[0], Atribuicao)

    def test_bloco_nao_fechado(self):
        _, erros = analisar("programa p {\n  enquanto verdadeiro {\n    escreva(1);\n}\nfim.")
        self.assertEqual(len(erros), 1)
        self.assertIn("Linha 5, Coluna 1", erros[0])
        self.assertIn("bloco aberto na linha 1, coluna 12", erros[0])

    def test_falta_fim_e_lixo_depois_do_fim(self):
        _, erros = analisar("programa p { }")
        self.assertIn("esperado 'fim'", erros[0])
        _, erros = analisar("programa p { } fim. x")
        self.assertIn("conteúdo inesperado após 'fim.'", erros[0])

    def test_arquivo_vazio(self):
        _, erros = analisar("")
        self.assertEqual(len(erros), 1)
        self.assertIn("esperado 'programa'", erros[0])

    def test_erros_da_extensao_d(self):
        _, erros = analisar(MODELO % "para x = 1 10 escreva(x);\nrepita x = 1;")
        self.assertEqual(len(erros), 2)
        self.assertIn("esperado 'ate' para indicar o limite do 'para'", erros[0])
        self.assertIn("para encerrar o 'repita'", erros[1])


class TestNavegacaoDaAST(unittest.TestCase):
    def test_filhos_e_visitante(self):
        programa, _ = analisar((EXEMPLOS / "validos" / "fatorial.mlg").read_text(encoding="utf-8"))

        class ContaIdentificadores(Visitante):
            def __init__(self):
                self.nomes = []

            def visitar_Identificador(self, no):
                self.nomes.append(no.nome)

        visitante = ContaIdentificadores()
        visitante.visitar(programa)
        self.assertEqual(visitante.nomes, ["n", "fat", "i", "n", "i", "fat", "fat", "i", "i", "i", "fat"])
        self.assertEqual(len(list(programa.filhos())), 4)   # 3 DeclVar + corpo
        self.assertIsInstance(next(programa.filhos()), DeclVar)

    def test_formatar_arvore(self):
        programa, _ = analisar(MODELO % "x = 1 + 2;")
        texto = formatar_arvore(programa)
        self.assertTrue(texto.startswith("Programa 'teste'  [1:1]"))
        self.assertIn("valor: Binaria '+'  [5:7]", texto)
        self.assertIn("DeclVar a: booleano  [3:5]", texto)

    def test_cli_imprime_ast(self):
        resultado = subprocess.run(
            [sys.executable, str(RAIZ / "minilang.py"), str(EXEMPLOS / "validos" / "fatorial.mlg"), "--ast"],
            capture_output=True, text=True, encoding="utf-8", cwd=RAIZ,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Programa 'fatorial'", resultado.stdout)
        self.assertIn("Enquanto", resultado.stdout)

    def test_cli_falha_com_erro_sintatico(self):
        resultado = subprocess.run(
            [sys.executable, str(RAIZ / "minilang.py"), str(EXEMPLOS / "invalidos" / "sintatico_multiplos_erros.mlg")],
            capture_output=True, text=True, encoding="utf-8", cwd=RAIZ,
        )
        self.assertEqual(resultado.returncode, 1)
        self.assertGreaterEqual(resultado.stderr.count("[SINTÁTICO]"), 5)


if __name__ == "__main__":
    unittest.main()
