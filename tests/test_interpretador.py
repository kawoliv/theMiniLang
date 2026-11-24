"""Suíte de testes automatizados para o Interpretador / Back-End (M4) da MiniLang."""

import io
import subprocess
import sys
import unittest
from pathlib import Path

from minilang.errors import ExecutionError
from minilang.interpretador import (
    Interpretador,
    dividir_inteiro,
    formatar_valor,
    interpretar,
    modulo_inteiro,
)
from minilang.lexer import Lexer
from minilang.parser import analisar_sintaxe
from minilang.semantico import analisar_semantica

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


def executar_codigo(fonte: str, entrada=None, max_iteracoes: int = 10_000) -> tuple[list[str], dict[str, int | bool]]:
    """Compila (M1..M3) e executa (M4) `fonte`, devolvendo (linhas_saida, memoria)."""
    tokens = Lexer(fonte).tokenizar()
    assert not tokens or True
    programa, erros_sint = analisar_sintaxe(tokens)
    assert not erros_sint, f"Erros sintáticos inesperados: {erros_sint}"
    _, erros_sem, _ = analisar_semantica(programa)
    assert not erros_sem, f"Erros semânticos inesperados: {erros_sem}"

    buffer_saida = io.StringIO()
    interp = interpretar(programa, entrada=entrada or [], saida=buffer_saida, max_iteracoes=max_iteracoes)
    return interp.linhas_saida, interp.memoria


def executar_corpo(corpo: str, entrada=None, max_iteracoes: int = 10_000) -> tuple[list[str], dict[str, int | bool]]:
    """Executa `corpo` dentro do programa MODELO."""
    return executar_codigo(MODELO % corpo, entrada=entrada, max_iteracoes=max_iteracoes)


class TestInterpretadorBasico(unittest.TestCase):
    def test_inicializacao_padrao_de_variaveis(self):
        saida, mem = executar_corpo("escreva(x, y, z, a, b);")
        self.assertEqual(saida, ["0 0 0 falso falso"])
        self.assertEqual(mem["x"], 0)
        self.assertIs(mem["a"], False)

    def test_escreva_formata_booleano_e_inteiro(self):
        # Garante que bool não seja tratado como int (isinstance(True, int) == True em Python)
        self.assertEqual(formatar_valor(True), "verdadeiro")
        self.assertEqual(formatar_valor(False), "falso")
        self.assertEqual(formatar_valor(1), "1")
        self.assertEqual(formatar_valor(0), "0")

        saida, _ = executar_corpo("x = 1; y = 0; a = verdadeiro; b = falso; escreva(a, b, x, y);")
        self.assertEqual(saida, ["verdadeiro falso 1 0"])

    def test_aritmetica_e_unarios(self):
        saida, mem = executar_corpo(
            "x = 10 - 3 - 2;\n"
            "y = 1 + 2 * 3;\n"
            "z = (1 + 2) * 3 % 4;\n"
            "x = - - y;\n"
            "escreva(x, y, z);"
        )
        self.assertEqual(saida, ["7 7 1"])
        self.assertEqual((mem["x"], mem["y"], mem["z"]), (7, 7, 1))

    def test_divisao_e_modulo_inteiros(self):
        self.assertEqual(dividir_inteiro(17, 5), 3)
        self.assertEqual(modulo_inteiro(17, 5), 2)
        saida, _ = executar_corpo("x = 17 / 5; y = 17 % 5; escreva(x, y);")
        self.assertEqual(saida, ["3 2"])

    def test_relacionais_e_logicos(self):
        saida, _ = executar_corpo(
            "x = 5; y = 10;\n"
            "a = x < y e y >= 10;\n"
            "b = x == y ou não (x > y);\n"
            "escreva(a, b, x != y, x <= 5);"
        )
        self.assertEqual(saida, ["verdadeiro verdadeiro verdadeiro verdadeiro"])

    def test_curto_circuito_evita_divisao_por_zero(self):
        # Quando x == 0:
        # 1) 'x != 0 e (10 / x > 1)' não deve avaliar o lado direito;
        # 2) 'x == 0 ou (10 / x > 1)' não deve avaliar o lado direito.
        saida, _ = executar_corpo(
            "x = 0;\n"
            "a = x != 0 e (10 / x > 1);\n"
            "b = x == 0 ou (10 / x > 1);\n"
            "escreva(a, b);"
        )
        self.assertEqual(saida, ["falso verdadeiro"])

    def test_leia_inteiro_e_booleano(self):
        saida, mem = executar_corpo(
            "leia(x); leia(y); leia(a); leia(b);\n"
            "escreva(x + y, a, b);",
            entrada=["15", "-3", "verdadeiro", "falso"],
        )
        self.assertEqual(saida, ["12 verdadeiro falso"])
        self.assertIs(mem["a"], True)
        self.assertIs(mem["b"], False)

    def test_funciona_mesmo_sem_passar_pelo_semantico(self):
        # Verifica independência do interpretador caso seja chamado direto após o Parser
        fonte = "programa p var n: inteiro; flag: booleano; { leia(n); leia(flag); escreva(n, flag); } fim."
        programa, erros = analisar_sintaxe(Lexer(fonte).tokenizar())
        self.assertEqual(erros, [])
        interp = interpretar(programa, entrada=["42", "verdadeiro"], saida=None)
        self.assertEqual(interp.linhas_saida, ["42 verdadeiro"])


class TestEstruturasDeControleEExtensaoD(unittest.TestCase):
    def test_se_e_senao(self):
        corpo = "leia(x); se x > 0 y = 1; senão y = -1; escreva(y);"
        self.assertEqual(executar_corpo(corpo, entrada=["10"])[0], ["1"])
        self.assertEqual(executar_corpo(corpo, entrada=["0"])[0], ["-1"])

    def test_enquanto(self):
        saida, _ = executar_corpo(
            "x = 1; y = 0;\n"
            "enquanto x <= 4 {\n"
            "  y = y + x;\n"
            "  x = x + 1;\n"
            "}\n"
            "escreva(y);"
        )
        self.assertEqual(saida, ["10"])

    def test_para_crescente_sem_e_com_passo(self):
        saida1, _ = executar_corpo("y = 0; para x = 1 ate 5 y = y + x; escreva(y);")
        self.assertEqual(saida1, ["15"])

        saida2, _ = executar_corpo("y = 0; para x = 1 ate 6 passo 2 y = y + x; escreva(y);")
        self.assertEqual(saida2, ["9"])  # 1 + 3 + 5

    def test_para_decrescente_passo_negativo(self):
        saida, _ = executar_corpo(
            "para x = 4 até 1 passo -1 {\n"
            "  escreva(x);\n"
            "}"
        )
        self.assertEqual(saida, ["4", "3", "2", "1"])

    def test_para_zero_iteracoes_inicializa_variavel_controle(self):
        saida, mem = executar_corpo("para x = 5 ate 1 y = 99; escreva(x, y);")
        self.assertEqual(saida, ["5 0"])
        self.assertEqual(mem["x"], 5)

    def test_repita_executa_ao_menos_uma_vez(self):
        # Mesmo com a condição já verdadeira na 1ª verificação, o corpo roda 1 vez
        saida, _ = executar_corpo(
            "x = 10;\n"
            "repita\n"
            "  x = x + 1;\n"
            "  escreva(x);\n"
            "ate x > 5;"
        )
        self.assertEqual(saida, ["11"])


class TestExemplosValidos(unittest.TestCase):
    def _rodar_exemplo(self, nome: str, entrada=None) -> list[str]:
        caminho = EXEMPLOS / "validos" / nome
        fonte = caminho.read_text(encoding="utf-8")
        saida, _ = executar_codigo(fonte, entrada=entrada)
        return saida

    def test_fatorial_e_exemplo_basico(self):
        self.assertEqual(self._rodar_exemplo("fatorial.ml", entrada=["5"]), ["120"])
        self.assertEqual(self._rodar_exemplo("fatorial.ml", entrada=["0"]), ["1"])
        self.assertEqual(self._rodar_exemplo("exemplo_basico.ml", entrada=["6"]), ["720"])

    def test_exemplo_para(self):
        self.assertEqual(self._rodar_exemplo("exemplo_para.ml"), ["55"])

    def test_exemplo_repita(self):
        self.assertEqual(self._rodar_exemplo("exemplo_repita.ml"), ["1", "2", "3", "4", "5"])

    def test_expressoes(self):
        self.assertEqual(self._rodar_exemplo("expressoes.ml"), ["7 7 1", "falso falso falso"])

    def test_lacos_aninhados(self):
        self.assertEqual(self._rodar_exemplo("lacos_aninhados.ml"), ["186"])

    def test_dangling_else(self):
        # a=1 (>0), b=-1 (<=0) -> 1º se entra no senão interno (2); 2º se não tem senão interno; 3º se cai em a==1 (11)
        self.assertEqual(self._rodar_exemplo("dangling_else.ml", entrada=["1", "-1"]), ["2", "11"])
        # a=0 (<=0), b=5 -> 1º se não entra; 2º se entra no senão externo (4); 3º se cai em a==0 (10)
        self.assertEqual(self._rodar_exemplo("dangling_else.ml", entrada=["0", "5"]), ["4", "10"])

    def test_avisos_inicializacao_ambos_os_caminhos(self):
        # Caminho onde 'maior' é inicializada (x > 0)
        self.assertEqual(self._rodar_exemplo("avisos_inicializacao.ml", entrada=["8"]), ["8"])
        # Caminho onde 'maior' não é atribuída (x <= 0): usa valor padrão seguro (0) sem KeyError
        self.assertEqual(self._rodar_exemplo("avisos_inicializacao.ml", entrada=["-5"]), ["0"])


class TestErrosDeExecucao(unittest.TestCase):
    def test_divisao_e_modulo_por_zero_dinamicos(self):
        with self.assertRaises(ExecutionError) as ctx_div:
            executar_corpo("leia(y); x = 10 / y;", entrada=["0"])
        self.assertEqual(str(ctx_div.exception), "[EXECUÇÃO] Linha 5, Coluna 19: divisão por zero")

        with self.assertRaises(ExecutionError) as ctx_mod:
            executar_corpo("leia(y); x = 10 % y;", entrada=["0"])
        self.assertEqual(str(ctx_mod.exception), "[EXECUÇÃO] Linha 5, Coluna 19: divisão por zero")

    def test_passo_zero_dinamico_no_para(self):
        with self.assertRaises(ExecutionError) as ctx:
            executar_corpo("leia(y); para x = 1 ate 10 passo y escreva(x);", entrada=["0"])
        self.assertEqual(str(ctx.exception), "[EXECUÇÃO] Linha 5, Coluna 34: o passo do 'para' não pode ser zero")

    def test_entrada_invalida_no_leia(self):
        with self.assertRaises(ExecutionError) as ctx_int:
            executar_corpo("leia(x);", entrada=["abc"])
        self.assertIn("[EXECUÇÃO] Linha 5, Coluna 1: valor inválido 'abc' para leitura de 'x'", str(ctx_int.exception))

        with self.assertRaises(ExecutionError) as ctx_bool:
            executar_corpo("leia(a);", entrada=["talvez"])
        self.assertIn("[EXECUÇÃO] Linha 5, Coluna 1: valor inválido 'talvez' para leitura de 'a'", str(ctx_bool.exception))

    def test_erro_eof_no_leia(self):
        with self.assertRaises(ExecutionError) as ctx:
            executar_corpo("leia(x);", entrada=[])
        self.assertEqual(str(ctx.exception), "[EXECUÇÃO] Linha 5, Coluna 1: fim de entrada inesperado ao ler 'x'")

    def test_protecao_contra_laco_infinito(self):
        with self.assertRaises(ExecutionError) as ctx:
            executar_corpo("enquanto verdadeiro x = x + 1;", max_iteracoes=50)
        self.assertIn("limite máximo de 50 iterações excedido", str(ctx.exception))


class TestCLIBackEnd(unittest.TestCase):
    def _rodar_cli(self, *args: str, entrada: str = "") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(RAIZ / "minilang.py"), *args],
            input=entrada,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=RAIZ,
        )

    def test_cli_executa_programa_por_padrao(self):
        res = self._rodar_cli(str(EXEMPLOS / "validos" / "fatorial.ml"), entrada="5\n")
        self.assertEqual(res.returncode, 0, res.stderr)
        linhas = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        self.assertEqual(linhas[0], "120")
        self.assertIn("[SUCESSO]", linhas[-1])

    def test_cli_modo_inspecao_nao_executa_sem_flag_run(self):
        # Sem stdin, --ast não deve tentar ler 'leia(n)' de fatorial.ml
        res = self._rodar_cli(str(EXEMPLOS / "validos" / "fatorial.ml"), "--ast")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Programa 'fatorial'", res.stdout)

        # Com --ast e --run juntos, exibe a AST e executa o programa
        res_run = self._rodar_cli(str(EXEMPLOS / "validos" / "fatorial.ml"), "--ast", "--run", entrada="4\n")
        self.assertEqual(res_run.returncode, 0, res_run.stderr)
        self.assertIn("Programa 'fatorial'", res_run.stdout)
        self.assertIn("\n24\n", res_run.stdout)

    def test_cli_reporta_erro_de_execucao_com_codigo_1(self):
        res = self._rodar_cli(str(EXEMPLOS / "validos" / "fatorial.ml"), entrada="invalido\n")
        self.assertEqual(res.returncode, 1)
        self.assertIn("[EXECUÇÃO]", res.stderr)
        self.assertIn("[FALHA] Compilação interrompida: 1 erro de execução.", res.stderr)

    def test_cli_trace_exibe_passo_a_passo_e_memoria_final(self):
        res = self._rodar_cli(str(EXEMPLOS / "validos" / "fatorial.ml"), "--trace", entrada="4\n")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("[TRACE L6:C3] leia(n) <- 4", res.stdout)
        self.assertIn("[TRACE L7:C3] fat = 1", res.stdout)
        self.assertIn("ESTADO FINAL DA MEMÓRIA", res.stdout)
        self.assertRegex(res.stdout, r"fat\s+\| inteiro\s+\| 24")

    def test_prompt_interativo_no_leia_e_formatar_memoria(self):
        fonte = "programa p var n: inteiro; ok: booleano; { leia(n); leia(ok); escreva(n, ok); } fim."
        programa, _ = analisar_sintaxe(Lexer(fonte).tokenizar())
        analisar_semantica(programa)
        saida_buf = io.StringIO()
        interp = interpretar(
            programa,
            entrada=["7", "verdadeiro"],
            saida=saida_buf,
            prompt_interativo=True,
            trace=True,
        )
        texto_saida = saida_buf.getvalue()
        self.assertIn("[LEIA] Digite um valor (inteiro) para 'n': ", texto_saida)
        self.assertIn("[LEIA] Digite um valor (booleano: verdadeiro/falso) para 'ok': ", texto_saida)
        self.assertEqual(interp.linhas_saida, ["7 verdadeiro"])
        tabela_mem = interp.formatar_memoria()
        self.assertIn("ESTADO FINAL DA MEMÓRIA", tabela_mem)
        self.assertIn("verdadeiro", tabela_mem)


if __name__ == "__main__":
    unittest.main()
