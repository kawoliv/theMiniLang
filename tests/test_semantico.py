"""Suíte de testes automatizados para o Analisador Semântico (M3) da MiniLang."""

import subprocess
import sys
import unittest
from pathlib import Path

from minilang.arvore import Binaria, Expressao, Visitante
from minilang.lexer import Lexer
from minilang.parser import analisar_sintaxe
from minilang.semantico import analisar_semantica

RAIZ = Path(__file__).resolve().parent.parent
EXEMPLOS = RAIZ / "exemplos"

# Linha 5 é onde o corpo de teste começa.
MODELO = (
    "programa teste\n"
    "var x, y: inteiro;\n"
    "    a, b: booleano;\n"
    "{\n"
    "%s\n"
    "  escreva(x, y, a, b);\n"
    "}\n"
    "fim."
)


def analisar(fonte: str):
    """Léxico + sintático (que devem passar) + semântico: (AST, tabela, erros, avisos)."""
    programa, erros_sintaticos = analisar_sintaxe(Lexer(fonte).tokenizar())
    assert not erros_sintaticos, erros_sintaticos
    tabela, erros, avisos = analisar_semantica(programa)
    return programa, tabela, erros, avisos


def erros_de(corpo: str) -> list[str]:
    """Erros semânticos de `corpo` dentro do programa padrão (variáveis já inicializadas)."""
    inicio = "x = 1; y = 2; a = verdadeiro; b = falso;\n"
    _, _, erros, _ = analisar(MODELO % (inicio + corpo))
    return erros


def avisos_de(corpo: str) -> list[str]:
    _, _, _, avisos = analisar(MODELO % corpo)
    return avisos


class TestTabelaDeSimbolos(unittest.TestCase):
    def test_registra_nome_tipo_escopo_e_posicao(self):
        _, tabela, erros, _ = analisar(MODELO % "leia(x); y = x; a = x > y; b = a;")
        self.assertEqual(erros, [])
        registros = [(s.nome, s.tipo, s.escopo, s.nivel, s.linha, s.coluna) for s in tabela.todos]
        self.assertEqual(registros, [
            ("x", "inteiro", "global", 0, 2, 5),
            ("y", "inteiro", "global", 0, 2, 8),
            ("a", "booleano", "global", 0, 3, 5),
            ("b", "booleano", "global", 0, 3, 8),
        ])

    def test_conta_usos(self):
        _, tabela, _, _ = analisar(MODELO % "leia(x); y = x + x; a = falso; b = a;")
        usos = {s.nome: s.usos for s in tabela.todos}
        self.assertEqual(usos, {"x": 4, "y": 2, "a": 3, "b": 2})

    def test_pilha_de_escopos(self):
        from minilang.simbolos import TabelaSimbolos
        tabela = TabelaSimbolos()
        tabela.entrar_escopo("global")
        tabela.declarar("x", "inteiro", 1, 1)
        tabela.entrar_escopo("interno")
        tabela.declarar("x", "booleano", 2, 1)
        self.assertEqual(tabela.buscar("x").tipo, "booleano")     # o mais interno esconde o externo
        self.assertEqual(tabela.buscar("x").nivel, 1)
        tabela.sair_escopo()
        self.assertEqual(tabela.buscar("x").tipo, "inteiro")
        self.assertIsNone(tabela.buscar_local("y"))
        self.assertEqual(len(tabela.todos), 2)                   # o histórico guarda os dois

    def test_formatar_tabela(self):
        _, tabela, _, _ = analisar(MODELO % "leia(x); leia(y); a = verdadeiro; b = a;")
        texto = tabela.formatar()
        self.assertIn("TABELA DE SÍMBOLOS", texto)
        self.assertRegex(texto, r"a\s+\| booleano\s+\| global\s+\|\s+0 \| 3:5")


class TestErrosObrigatorios(unittest.TestCase):
    def test_variavel_nao_declarada(self):
        self.assertEqual(erros_de("y = z + 1;"),
                         ["[SEMÂNTICO] Linha 6, Coluna 5: variável 'z' não declarada"])

    def test_nao_declarada_reportada_uma_vez(self):
        self.assertEqual(len(erros_de("y = z + z;\nz = 3;")), 1)

    def test_leia_em_identificador_nao_declarado(self):
        self.assertEqual(erros_de("leia(k);"),
                         ["[SEMÂNTICO] Linha 6, Coluna 6: 'leia' em identificador não declarado 'k'"])

    def test_redeclaracao(self):
        _, _, erros, _ = analisar("programa p var x: inteiro; y, x: booleano; { leia(x); escreva(x, y); } fim.")
        self.assertEqual(erros, ["[SEMÂNTICO] Linha 1, Coluna 31: variável 'x' já declarada na linha 1, coluna 16"])

    def test_redeclaracao_mantem_o_primeiro_tipo(self):
        _, tabela, erros, _ = analisar("programa p var x: inteiro; x: booleano; { x = 1; escreva(x); } fim.")
        self.assertEqual(len(erros), 1)                  # só a redeclaração; 'x = 1' é válido
        self.assertEqual([s.tipo for s in tabela.todos], ["inteiro"])

    def test_atribuicao_com_tipos_incompativeis(self):
        erros = erros_de("x = verdadeiro;\na = 1 + 2;")
        self.assertEqual(erros, [
            "[SEMÂNTICO] Linha 6, Coluna 1: tipos incompatíveis: não é possível atribuir booleano à variável 'x' (inteiro)",
            "[SEMÂNTICO] Linha 7, Coluna 1: tipos incompatíveis: não é possível atribuir inteiro à variável 'a' (booleano)",
        ])

    def test_condicoes_nao_booleanas(self):
        erros = erros_de("se x escreva(x);\nenquanto x + 1 x = 0;\nrepita x = 1; ate y;")
        self.assertEqual(len(erros), 3)
        self.assertIn("Linha 6, Coluna 4: a condição do 'se' deve ser do tipo booleano, mas é do tipo inteiro", erros[0])
        self.assertIn("Linha 7, Coluna 12: a condição do 'enquanto'", erros[1])
        self.assertIn("Linha 8, Coluna 19: a condição do 'repita ... ate'", erros[2])

    def test_condicao_booleana_valida(self):
        self.assertEqual(erros_de("se x > 0 e não a ou b escreva(x);\nenquanto a a = falso;"), [])


class TestOperadores(unittest.TestCase):
    def test_aritmetico_com_booleano(self):
        erros = erros_de("x = y + a;\ny = b * 2;\nx = x % verdadeiro;")
        self.assertEqual(len(erros), 3)
        self.assertIn("Linha 6, Coluna 7: operador '+' exige operandos inteiros, mas o operando direito é booleano", erros[0])
        self.assertIn("operador '*' exige operandos inteiros, mas o operando esquerdo é booleano", erros[1])

    def test_logico_com_inteiro(self):
        erros = erros_de("a = a e x;\nb = 1 ou b;")
        self.assertIn("operador 'e' exige operandos booleanos, mas o operando direito é inteiro", erros[0])
        self.assertIn("operador 'ou' exige operandos booleanos, mas o operando esquerdo é inteiro", erros[1])

    def test_relacional_com_booleano(self):
        erros = erros_de("a = a < b;")
        self.assertEqual(len(erros), 1)            # um erro por operador, não um por operando
        self.assertIn("operador '<' exige operandos inteiros", erros[0])

    def test_unarios(self):
        erros = erros_de("a = não x;\nx = -a;")
        self.assertIn("operador 'não' exige operando booleano, mas recebeu inteiro", erros[0])
        self.assertIn("operador '-' exige operando inteiro, mas recebeu booleano", erros[1])

    def test_igualdade_exige_mesmo_tipo(self):
        self.assertEqual(erros_de("a = x == y;\nb = a != falso;"), [])
        erros = erros_de("a = x == a;")
        self.assertIn("operador '==' compara inteiro com booleano", erros[0])

    def test_divisao_por_zero_constante(self):
        erros = erros_de("x = y / 0;\ny = x % 0;")
        self.assertEqual([e.split(": ", 1)[1] for e in erros], ["divisão por zero", "divisão por zero"])

    def test_sem_cascata_apos_nao_declarada(self):
        # 'z' não declarada vira tipo 'erro', que não gera erros novos em '+', '>' nem na atribuição
        self.assertEqual(len(erros_de("a = z + 1 > 2;")), 1)


class TestExtensaoD(unittest.TestCase):
    def test_para_valido(self):
        self.assertEqual(erros_de("para x = 1 ate y passo 2 escreva(x);"), [])

    def test_para_com_tipos_errados(self):
        erros = erros_de("para a = 1 ate 10 escreva(a);\npara x = verdadeiro ate b passo a escreva(x);")
        self.assertEqual(len(erros), 4)
        self.assertIn("a variável de controle do 'para' deve ser inteira, mas 'a' é booleano", erros[0])
        self.assertIn("o valor inicial do 'para' deve ser do tipo inteiro", erros[1])
        self.assertIn("o limite do 'para' deve ser do tipo inteiro", erros[2])
        self.assertIn("o passo do 'para' deve ser do tipo inteiro", erros[3])

    def test_passo_zero(self):
        self.assertEqual(erros_de("para x = 1 ate 5 passo 0 escreva(x);"),
                         ["[SEMÂNTICO] Linha 6, Coluna 24: o passo do 'para' não pode ser zero"])

    def test_para_com_variavel_nao_declarada(self):
        self.assertIn("variável 'k' não declarada", erros_de("para k = 1 ate 3 escreva(k);")[0])


class TestAnotacaoDeTipos(unittest.TestCase):
    def test_todas_as_expressoes_recebem_tipo(self):
        programa, _, erros, _ = analisar(MODELO % "leia(x); y = -x * 2; a = não (x > y) ou x == 3; b = a e verdadeiro;")
        self.assertEqual(erros, [])
        sem_tipo = []

        class Verifica(Visitante):
            def visitar_generico(self, no):
                if isinstance(no, Expressao) and no.tipo is None:
                    sem_tipo.append(no)
                super().visitar_generico(no)

        Verifica().visitar(programa)
        self.assertEqual(sem_tipo, [])

    def test_tipos_inferidos(self):
        programa, _, _, _ = analisar(MODELO % "leia(x); y = 1; a = x + 1 > y; b = a;")
        atrib = programa.corpo.comandos[2]           # a = x + 1 > y;
        self.assertEqual(atrib.valor.tipo, "booleano")
        self.assertIsInstance(atrib.valor.esq, Binaria)
        self.assertEqual(atrib.valor.esq.tipo, "inteiro")
        self.assertEqual(atrib.alvo.tipo, "booleano")

    def test_identificador_nao_declarado_tem_tipo_erro(self):
        programa, _, _, _ = analisar(MODELO % "x = 1; y = 1; a = falso; b = falso; x = z;")
        self.assertEqual(programa.corpo.comandos[-2].valor.tipo, "erro")   # [-1] é o escreva do MODELO


class TestInicializacao(unittest.TestCase):
    """Bônus da rubrica: variável lida antes de ser inicializada (é um aviso)."""

    def _variaveis_avisadas(self, corpo: str) -> list[str]:
        return [a.split("'")[1] for a in avisos_de(corpo) if "inicializada" in a]

    def test_leitura_sem_inicializar(self):
        avisos = avisos_de("y = x + 1; a = falso; b = a;")
        self.assertIn("[SEMÂNTICO] Linha 5, Coluna 5: aviso: variável 'x' pode estar sendo lida antes de ser inicializada", avisos)

    def test_leia_e_atribuicao_inicializam(self):
        self.assertEqual(self._variaveis_avisadas("leia(x); y = x; a = y > 0; b = a;"), [])

    def test_se_sem_senao_nao_garante(self):
        self.assertEqual(self._variaveis_avisadas("leia(x); se x > 0 y = 1; a = falso; b = a;"), ["y"])

    def test_se_com_senao_garante_quando_os_dois_inicializam(self):
        self.assertEqual(self._variaveis_avisadas("leia(x); se x > 0 y = 1; senao y = 2; a = falso; b = a;"), [])

    def test_enquanto_e_para_podem_nao_executar(self):
        self.assertEqual(self._variaveis_avisadas("a = falso; enquanto a y = 1; x = y; b = a;"), ["y"])
        self.assertEqual(self._variaveis_avisadas("para x = 1 ate 0 y = x; a = y > 0; b = a;"), ["y"])

    def test_repita_executa_ao_menos_uma_vez(self):
        self.assertEqual(self._variaveis_avisadas("repita leia(x); ate x > 0; y = x; a = falso; b = a;"), [])

    def test_variavel_nunca_usada(self):
        _, _, _, avisos = analisar("programa p var x, sobra: inteiro; { leia(x); escreva(x); } fim.")
        self.assertEqual(avisos, ["[SEMÂNTICO] Linha 1, Coluna 19: aviso: variável 'sobra' declarada e nunca usada"])


class TestExemplos(unittest.TestCase):
    def test_exemplos_validos_sem_erros_semanticos(self):
        for arquivo in sorted((EXEMPLOS / "validos").glob("*.mlg")):
            with self.subTest(arquivo=arquivo.name):
                _, _, erros, avisos = analisar(arquivo.read_text(encoding="utf-8"))
                self.assertEqual(erros, [])
                if arquivo.name != "avisos_inicializacao.mlg":
                    self.assertEqual(avisos, [])

    def test_exemplos_invalidos_semanticos(self):
        arquivos = sorted((EXEMPLOS / "invalidos").glob("semantico_*.mlg"))
        self.assertGreaterEqual(len(arquivos), 4)
        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                _, _, erros, _ = analisar(arquivo.read_text(encoding="utf-8"))
                self.assertGreater(len(erros), 0)
                for erro in erros:
                    self.assertRegex(erro, r"^\[SEMÂNTICO\] Linha \d+, Coluna \d+: .+")
                # erros saem em ordem de posição no código
                posicoes = [tuple(map(int, e.split("Linha ")[1].split(":")[0].split(", Coluna "))) for e in erros]
                self.assertEqual(posicoes, sorted(posicoes))

    def test_cli_symbols_e_falha_semantica(self):
        def rodar(*args):
            return subprocess.run([sys.executable, str(RAIZ / "minilang.py"), *args],
                                  capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)

        ok = rodar(str(EXEMPLOS / "validos" / "fatorial.mlg"), "--symbols", "--ast")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("TABELA DE SÍMBOLOS", ok.stdout)
        self.assertIn("Identificador 'fat' : inteiro", ok.stdout)

        falha = rodar(str(EXEMPLOS / "invalidos" / "semantico_tipos.mlg"))
        self.assertEqual(falha.returncode, 1)
        self.assertEqual(falha.stderr.count("[SEMÂNTICO]"), 9)

        avisos = rodar(str(EXEMPLOS / "validos" / "avisos_inicializacao.mlg"))
        self.assertEqual(avisos.returncode, 0)          # avisos não impedem a compilação
        self.assertIn("aviso:", avisos.stderr)


if __name__ == "__main__":
    unittest.main()
