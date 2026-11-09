# 🛠️ Fix 01: Suporte a Múltiplos Blocos e Linhas de `var` no Parser

**Módulo:** `minilang/parser.py` e `tests/test_parser.py`  
**Severidade:** 🔴 Crítica (Quebra o exemplo oficial do edital do Prof. Daniel Santana)  
**Responsável Sugerido:** Integrante responsável pelo Sintático (M2)  

---

## 1. O Problema

O método `_programa()` em [`minilang/parser.py`](../minilang/parser.py) consome a palavra-chave `var` apenas uma vez. Se o código MiniLang tiver declarações com `var` repetido:

```pascal
programa teste
var x: inteiro;
var y: inteiro;
{
    x = 1;
}
fim.
```

O parser rejeita na linha 3 com:
```
[SINTÁTICO] Linha 3, Coluna 1: esperado '{' para iniciar o corpo do programa, mas encontrado 'var'
```

No entanto, o **próprio edital oficial da UNIFACS** e o arquivo de instruções do professor contêm:
```pascal
programa fatorial
  var n: inteiro;
  var fat: inteiro;
  var i: inteiro;
{ ... }
```

Se o professor executar esse teste, o compilador zera a questão de validação de programas sintáticos válidos.

---

## 2. Como Corrigir no Código

### Passo 1: Modificar `minilang/parser.py`

Localize o método `_programa` (em torno da linha 189) e substitua a linha de leitura de declarações:

**Antes:**
```python
declaracoes = self._declaracoes() if self._verifica(T.VAR) else []
```

**Depois:**
```python
declaracoes: list[DeclVar] = []
while self._verifica(T.VAR):
    declaracoes.extend(self._declaracoes())
```

### Passo 2: Permitir múltiplos `var` sem quebrar o bloco `_declaracoes`

No método `_declaracoes` (em torno da linha 234):

**Antes:**
```python
    def _declaracoes(self) -> list[DeclVar]:
        self._espera(T.VAR)
        if not self._verifica(T.IDENT):
            self._registrar(self._erro(
                f"esperada ao menos uma declaração após 'var', mas encontrado {descrever(self._atual())}"
            ))
        declaracoes: list[DeclVar] = []
        while self._verifica(T.IDENT) and self._espiar().tipo is not T.ATRIB:
            try:
                declaracoes.extend(self._declaracao())
            except SyntacticError as erro:
                self._registrar(erro)
                self._sincronizar_declaracao()
        return declaracoes
```

Dessa forma, o parser aceita tanto a sintaxe estilo bloco:
```pascal
var
  a, b: inteiro;
  flag: booleano;
```
Quanto a sintaxe com `var` por linha:
```pascal
var a: inteiro;
var b: inteiro;
```

---

## 3. Teste Automatizado para Adicionar

Abra [`tests/test_parser.py`](../tests/test_parser.py) e adicione o seguinte teste dentro da classe `TestProgramasValidos`:

```python
    def test_multiplos_blocos_var(self):
        fonte = """programa teste
var a: inteiro;
var b: booleano;
var c, d: inteiro;
{
    a = 10;
}
fim."""
        programa, erros = analisar(fonte)
        self.assertEqual(len(erros), 0, f"Erros inesperados: {erros}")
        self.assertEqual(len(programa.declaracoes), 4)
        nomes = [d.nome for d in programa.declaracoes]
        self.assertEqual(nomes, ["a", "b", "c", "d"])
```

---

## 4. Como Validar

Execute no terminal:

```bash
python -m unittest tests/test_parser.py -v
```

Todos os testes devem passar com `OK`.
