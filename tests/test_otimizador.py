"""Suíte de testes automatizados para o Otimizador (M4) da MiniLang."""

import io
import subprocess
import sys
import unittest
from pathlib import Path

from minilang.arvore import Atribuicao, Binaria, Booleano, Enquanto, Numero, Para, Repita
from minilang.errors import ExecutionError
from minilang.interpretador import interpretar
from minilang.lexer import Lexer
from minilang.otimizador import Otimizador, otimizar
from minilang.parser import analisar_sintaxe
from minilang.semantico import analisar_semantica

RAIZ = Path(__file__).resolve().parent.parent
EXEMPLOS_VALIDOS = RAIZ / "exemplos" / "validos"


def compilar(fonte: str):
    tokens = Lexer(fonte).tokenizar()
    programa, erros_sint = analisar_sintaxe(tokens)
    assert not erros_sint, f"Erros sintáticos inesperados: {erros_sint}"
    _, erros_sem, _ = analisar_semantica(programa)
    assert not erros_sem, f"Erros semânticos inesperados: {erros_sem}"
    return programa


def executar_ambos(fonte: str, entrada=None, max_iteracoes: int = 10_000):
    """Executa `fonte` sem e com otimização e devolve (saida_orig, mem_orig, saida_otim, mem_otim, prog_otim)."""
    prog_orig = compilar(fonte)
    prog_otim = otimizar(prog_orig)

    buf1 = io.StringIO()
    interp1 = interpretar(prog_orig, entrada=list(entrada or []), saida=buf1, max_iteracoes=max_iteracoes)

    buf2 = io.StringIO()
    interp2 = interpretar(prog_otim, entrada=list(entrada or []), saida=buf2, max_iteracoes=max_iteracoes)

    return interp1.linhas_saida, interp1.memoria, interp2.linhas_saida, interp2.memoria, prog_otim


class TestDobraduraDeConstantes(unittest.TestCase):
    def test_dobradura_aritmetica_e_unaria(self):
        fonte = (
            "programa p\n"
            "var x, y, z, w: inteiro;\n"
            "{\n"
            "  x = 10 - 3 - 2;\n"
            "  y = 1 + 2 * 3;\n"
            "  z = (1 + 2) * 3 % 4;\n"
            "  w = - - 7;\n"
            "  escreva(x, y, z, w);\n"
            "}\n"
            "fim."
        )
        s1, m1, s2, m2, prog_otim = executar_ambos(fonte)
        self.assertEqual(s1, s2)
        self.assertEqual(s2, ["5 7 1 7"])
        for k in ("x", "y", "z", "w"):
            self.assertEqual(m1[k], m2[k])

        valores = [cmd.valor for cmd in prog_otim.corpo.comandos[:4]]
        self.assertTrue(all(isinstance(v, Numero) for v in valores))
        self.assertEqual([v.valor for v in valores], [5, 7, 1, 7])
        self.assertTrue(all(v.tipo == "inteiro" for v in valores))

    def test_dobradura_relacional_e_logica_com_curto_circuito(self):
        fonte = (
            "programa p\n"
            "var a, b, c: booleano; x: inteiro;\n"
            "{\n"
            "  x = 0;\n"
            "  a = 5 < 10 e (3 == 3);\n"
            "  b = falso e (10 / x > 1);\n"
            "  c = verdadeiro ou (10 / x > 1);\n"
            "  escreva(a, b, c);\n"
            "}\n"
            "fim."
        )
        s1, _, s2, _, prog_otim = executar_ambos(fonte)
        self.assertEqual(s1, s2)
        self.assertEqual(s2, ["verdadeiro falso verdadeiro"])

        cmds = prog_otim.corpo.comandos
        self.assertIsInstance(cmds[1].valor, Booleano)
        self.assertTrue(cmds[1].valor.valor)
        self.assertIsInstance(cmds[2].valor, Booleano)
        self.assertFalse(cmds[2].valor.valor)
        self.assertIsInstance(cmds[3].valor, Booleano)
        self.assertTrue(cmds[3].valor.valor)

    def test_nao_dobra_divisao_por_zero_e_nao_muta_ast_original(self):
        fonte = (
            "programa p\n"
            "var x: inteiro;\n"
            "{\n"
            "  x = 10 / (2 - 2);\n"
            "}\n"
            "fim."
        )
        prog_orig = compilar(fonte)
        prog_otim = otimizar(prog_orig)

        # Original continua intacto
        self.assertIsInstance(prog_orig.corpo.comandos[0].valor.dir, Binaria)
        # Otimizado dobrou (2 - 2) -> 0, mas preservou a divisão 10 / 0 para falhar em runtime
        atrib = prog_otim.corpo.comandos[0]
        self.assertIsInstance(atrib.valor, Binaria)
        self.assertIsInstance(atrib.valor.dir, Numero)
        self.assertEqual(atrib.valor.dir.valor, 0)

        with self.assertRaises(ExecutionError):
            interpretar(prog_otim, saida=None)


class TestMovimentacaoInvarianteDeLaco(unittest.TestCase):
    def test_move_calculo_fixo_para_antes_do_para(self):
        fonte = (
            "programa p\n"
            "var i, a, b, c, soma: inteiro;\n"
            "{\n"
            "  a = 3; b = 4; c = 2; soma = 0;\n"
            "  para i = 1 ate 5 {\n"
            "    soma = soma + (a * b + c);\n"
            "  }\n"
            "  escreva(soma);\n"
            "}\n"
            "fim."
        )
        otim = Otimizador()
        prog_orig = compilar(fonte)
        prog_otim = otim.otimizar(prog_orig)

        self.assertGreaterEqual(otim.movimentacoes, 1)
        # Deve haver atribuição de _inv_0 antes do comando Para
        nomes_decls = [d.nome for d in prog_otim.declaracoes]
        self.assertIn("_inv_0", nomes_decls)

        tipos_cmds = [type(c) for c in prog_otim.corpo.comandos]
        idx_para = tipos_cmds.index(Para)
        self.assertIsInstance(prog_otim.corpo.comandos[idx_para - 1], Atribuicao)
        self.assertEqual(prog_otim.corpo.comandos[idx_para - 1].alvo.nome, "_inv_0")

        s1, m1, s2, m2, _ = executar_ambos(fonte)
        self.assertEqual(s1, s2)
        self.assertEqual(s2, ["70"])
        self.assertEqual(m1["soma"], m2["soma"])

    def test_move_invariante_da_condicao_do_enquanto_e_do_repita(self):
        fonte = (
            "programa p\n"
            "var i, a, b, soma: inteiro;\n"
            "{\n"
            "  a = 2; b = 3; i = 0; soma = 0;\n"
            "  enquanto i < a * b + 4 {\n"
            "    soma = soma + (a + b);\n"
            "    i = i + 1;\n"
            "  }\n"
            "  repita\n"
            "    soma = soma + (a * 2);\n"
            "    i = i - 1;\n"
            "  ate i <= (a - a);\n"
            "  escreva(soma);\n"
            "}\n"
            "fim."
        )
        s1, m1, s2, m2, prog_otim = executar_ambos(fonte)
        self.assertEqual(s1, s2)
        self.assertEqual(m1["soma"], m2["soma"])

        # Tanto o enquanto quanto o repita devem ter recebido temporárias antes deles
        cmds = prog_otim.corpo.comandos
        idx_enq = next(i for i, c in enumerate(cmds) if isinstance(c, Enquanto))
        idx_rep = next(i for i, c in enumerate(cmds) if isinstance(c, Repita))
        self.assertIsInstance(cmds[idx_enq - 1], Atribuicao)
        self.assertIsInstance(cmds[idx_rep - 1], Atribuicao)

    def test_lacos_aninhados_move_para_o_nivel_mais_externo_possivel(self):
        fonte = (
            "programa p\n"
            "var i, j, a, b, soma: inteiro;\n"
            "{\n"
            "  a = 3; b = 4; soma = 0;\n"
            "  para i = 1 ate 3 {\n"
            "    para j = 1 ate 2 {\n"
            "      soma = soma + (a * b + 1) + (i * 10);\n"
            "    }\n"
            "  }\n"
            "  escreva(soma);\n"
            "}\n"
            "fim."
        )
        s1, m1, s2, m2, prog_otim = executar_ambos(fonte)
        self.assertEqual(s1, s2)
        self.assertEqual(m1["soma"], m2["soma"])

        # (a * b + 1) deve sair do laço externo; (i * 10) deve sair apenas do laço interno
        cmds = prog_otim.corpo.comandos
        idx_para_ext = next(i for i, c in enumerate(cmds) if isinstance(c, Para))
        self.assertIsInstance(cmds[idx_para_ext - 1], Atribuicao)
        self.assertTrue(cmds[idx_para_ext - 1].alvo.nome.startswith("_inv_"))

        para_ext = cmds[idx_para_ext]
        idx_para_int = next(i for i, c in enumerate(para_ext.corpo.comandos) if isinstance(c, Para))
        self.assertIsInstance(para_ext.corpo.comandos[idx_para_int - 1], Atribuicao)
        self.assertTrue(para_ext.corpo.comandos[idx_para_int - 1].alvo.nome.startswith("_inv_"))

    def test_nao_move_variavel_modificada_nem_divisao_insegura_em_laco_zero_vezes(self):
        fonte = (
            "programa p\n"
            "var i, x, y: inteiro;\n"
            "{\n"
            "  x = 0;\n"
            "  y = 10;\n"
            "  i = 5;\n"
            "  enquanto i < 3 {\n"
            "    y = 10 / x;\n"
            "    i = i + 1;\n"
            "  }\n"
            "  escreva(y);\n"
            "}\n"
            "fim."
        )
        s1, m1, s2, m2, _ = executar_ambos(fonte)
        self.assertEqual(s1, ["10"])
        self.assertEqual(s2, ["10"])
        self.assertEqual(m1["y"], m2["y"])

    def test_evita_colisao_com_nome_inv_existente(self):
        fonte = (
            "programa p\n"
            "var i, a, b, soma: inteiro;\n"
            "{\n"
            "  a = 2; b = 3; soma = 0;\n"
            "  para i = 1 ate 3 {\n"
            "    soma = soma + (a + b);\n"
            "  }\n"
            "  escreva(soma);\n"
            "}\n"
            "fim."
        )
        from minilang.arvore import DeclVar

        prog_orig = compilar(fonte)
        prog_orig.declaracoes.append(DeclVar(nome="_inv_0", tipo="inteiro", linha=1, coluna=1))
        prog_otim = otimizar(prog_orig)
        nomes = [d.nome for d in prog_otim.declaracoes]
        self.assertIn("_inv_0", nomes)
        self.assertIn("_inv_1", nomes)

        interp = interpretar(prog_otim, saida=None)
        self.assertEqual(interp.linhas_saida, ["15"])


class TestEquivalenciaExemplosECLI(unittest.TestCase):
    def test_equivalencia_nos_exemplos_validos(self):
        entradas_por_exemplo = {
            "avisos_inicializacao.ml": ["5"],
            "dangling_else.ml": ["1", "2"],
            "fatorial.ml": ["5"],
            "exemplo_basico.ml": ["10", "20"],
            "exemplo_repita.ml": ["5", "-1", "0"],
        }
        for arquivo in sorted(EXEMPLOS_VALIDOS.glob("*.ml")):
            with self.subTest(arquivo=arquivo.name):
                fonte = arquivo.read_text(encoding="utf-8")
                entrada = entradas_por_exemplo.get(arquivo.name, [])
                s1, _, s2, _, _ = executar_ambos(fonte, entrada=entrada)
                self.assertEqual(s1, s2)

    def test_cli_ast_optimize_e_execucao(self):
        resultado = subprocess.run(
            [sys.executable, str(RAIZ / "minilang.py"), str(EXEMPLOS_VALIDOS / "expressoes.ml"), "--ast", "--optimize", "--run"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertNotIn("ainda não está disponível", resultado.stderr)
        self.assertIn("Numero 5 : inteiro", resultado.stdout)
        self.assertIn("7 7 1", resultado.stdout)
        self.assertIn("falso falso falso", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
