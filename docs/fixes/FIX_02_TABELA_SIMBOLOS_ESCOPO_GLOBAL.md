# 🛠️ Fix 02: Preservação do Escopo Global na Tabela de Símbolos

**Módulo:** `minilang/semantico.py` e `tests/test_semantico.py`  
**Severidade:** 🔴 Crítica (Inutiliza a Tabela de Símbolos para o Marco 4 / Back-End)  
**Responsável Sugerido:** Integrante responsável pela Semântica (M3)  

---

## 1. O Problema

No arquivo [`minilang/semantico.py`](../minilang/semantico.py), ao final do método `visitar_Programa()`, é chamado:

```python
self.tabela.sair_escopo()
```

O método `sair_escopo()` faz um `pop()` no escopo `"global"` da pilha `self.escopos` da `TabelaSimbolos`.

Isso causa um efeito colateral grave:
1. A lista `tabela.escopos` fica com tamanho 0 (`len(tabela.escopos) == 0`).
2. Se o futuro Back-End (interpretador ou gerador de código no Marco 4) chamar `tabela.buscar("variavel")`, a busca sempre retorna `None`!
3. Se alguém acessar `tabela.escopo_atual`, o Python dispara:
   ```
   IndexError: list index out of range
   ```

Apesar da listagem para impressão (`tabela.todos`) continuar existindo, a estrutura de dados de consulta fica corrompida após a análise semântica.

---

## 2. Como Corrigir no Código

### Modificar `minilang/semantico.py`

Abra [`minilang/semantico.py`](../minilang/semantico.py) e localize o método `visitar_Programa` (em torno da linha 115):

**Antes:**
```python
    def visitar_Programa(self, no: Programa) -> None:
        self.tabela.entrar_escopo("global")
        for declaracao in no.declaracoes:
            self.visitar(declaracao)
        self.visitar(no.corpo)
        for simbolo in self.tabela.escopo_atual.simbolos.values():
            if simbolo.usos == 0:
                self._avisos.append(SemanticError(
                    simbolo.linha, simbolo.coluna, f"aviso: variável '{simbolo.nome}' declarada e nunca usada"
                ))
        self.tabela.sair_escopo()  # <--- REMOVER OU COMENTAR ESTA LINHA!
```

**Depois:**
```python
    def visitar_Programa(self, no: Programa) -> None:
        self.tabela.entrar_escopo("global")
        for declaracao in no.declaracoes:
            self.visitar(declaracao)
        self.visitar(no.corpo)
        for simbolo in self.tabela.escopo_atual.simbolos.values():
            if simbolo.usos == 0:
                self._avisos.append(SemanticError(
                    simbolo.linha, simbolo.coluna, f"aviso: variável '{simbolo.nome}' declarada e nunca usada"
                ))
        # O escopo 'global' NÃO é desempilhado aqui para que o M4 (Back-End)
        # e o CLI possam consultar tabela.buscar() e tabela.escopo_atual normalmente.
```

---

## 3. Teste Automatizado para Adicionar

Abra [`tests/test_semantico.py`](../tests/test_semantico.py) e adicione o teste na classe `TestTabelaDeSimbolos`:

```python
    def test_escopo_global_permanece_ativo_apos_analise(self):
        """Garante que o escopo global não seja descartado no fim da análise, permitindo uso no M4."""
        fonte = """programa teste
var x: inteiro;
{
    x = 10;
}
fim."""
        tokens = Lexer(fonte).tokenizar()
        programa, erros_sint = Parser(tokens).analisar()
        self.assertEqual(len(erros_sint), 0)

        analisador = AnalisadorSemantico()
        tabela = analisador.analisar(programa)

        self.assertEqual(len(analisador.erros), 0)
        self.assertGreater(len(tabela.escopos), 0, "A pilha de escopos não pode estar vazia")
        simbolo_x = tabela.buscar("x")
        self.assertIsNotNone(simbolo_x, "tabela.buscar('x') deve encontrar a variável declarada")
        self.assertEqual(simbolo_x.tipo, "inteiro")
```

---

## 4. Como Validar

Execute no terminal:

```bash
python -m unittest tests/test_semantico.py -v
```

Todos os testes devem passar com `OK`.
