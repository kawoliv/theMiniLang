# Nota do Marco M3 — Analisador Semântico

**Projeto:** Compilador MiniLang  
**Disciplina:** Teoria da Computação e Compiladores (UNIFACS 2026.2)  
**Marco:** M3 — Análise Semântica, Tabela de Símbolos e AST anotada  
**Extensão escolhida:** D (`para ... ate ... passo` e `repita ... ate`)  
**Data:** Novembro de 2026

**Equipe:** Kawan Oliveira (`@kawoliv`), João Guilherme Perrone Hohlenwerger (`@joaohohlenwerger`),
Daniel Costa (`@Danncss`), João Spinola Falcão (`@Falc01`), Pedro Adaime Ribeiro (`@pedrobelane`),
Isabelle Maciel dos Santos (`@isabellesmaciel`)

---

## 1. O que foi entregue

| Item | Onde |
|---|---|
| Regras semânticas, sistema de tipos, análise de inicialização | [`docs/semantica.md`](semantica.md) |
| Tabela de símbolos (pilha de escopos) | [`minilang/simbolos.py`](../minilang/simbolos.py) |
| Analisador semântico (Visitor sobre a AST) | [`minilang/semantico.py`](../minilang/semantico.py) |
| Erro `[SEMÂNTICO] Linha L, Coluna C: ...` | [`minilang/errors.py`](../minilang/errors.py) |
| CLI: `--symbols` e `--ast` com tipos | [`minilang/cli.py`](../minilang/cli.py) |
| 36 testes semânticos (84 no total) | [`tests/test_semantico.py`](../tests/test_semantico.py) |
| 4 programas inválidos semânticos e 1 válido com avisos | [`exemplos/`](../exemplos/) |

## 2. Cobertura da rubrica

| Critério | Como |
|---|---|
| Tabela com escopo, tipo e posição (3,0) | `Simbolo(nome, tipo, escopo, nivel, linha, coluna, usos)`; `--symbols` imprime |
| Não declarada, redeclaração, tipos incompatíveis, condição não booleana (3,0) | `_resolver`, `visitar_DeclVar`, `visitar_Atribuicao`, `_exige(..., BOOLEANO, ...)` |
| Mau uso de operadores e `leia` não declarado (2,0) | tabela `REGRAS_BINARIAS`/`REGRAS_UNARIAS`; mensagem específica em `visitar_Leia` |
| AST anotada com tipos (1,5) | todo `Expressao.tipo` preenchido; visível com `--ast` |
| Bônus: lida antes de inicializar (0,5) | análise de fluxo conservadora (*definite assignment*), emitida como aviso |

## 3. Decisões de projeto

- **Visitor:** `AnalisadorSemantico` herda de `Visitante` (M2). Os métodos de expressão devolvem o
  tipo, e `_tipo()` grava esse tipo no nó. Isso é a anotação da AST.
- **Regras de operador em tabela:** um dicionário `operador → (tipo dos operandos, tipo do
  resultado)` substitui uma cadeia de `if`s. `==` e `!=` são tratados à parte, porque exigem apenas
  tipos iguais dos dois lados.
- **Tipo `erro` contra cascata:** uma variável não declarada vira o tipo `erro`, que todo operador
  aceita em silêncio. O resultado é uma mensagem por problema real, e a variável não declarada é
  reportada só no primeiro uso.
- **Sem coerção:** a MiniLang não converte `booleano` em `inteiro` nem o contrário.
- **Inicialização como aviso:** a análise é conservadora (interseção nos ramos do `se`; `enquanto`
  e `para` podem executar 0 vezes; `repita` executa ao menos uma vez). Como pode haver falso
  positivo, ela não bloqueia a compilação.
- **Extensão D:** a variável de controle e as expressões do `para` precisam ser `inteiro`, e um passo
  constante `0` é rejeitado porque geraria laço infinito.
- **Ordem das fases:** a semântica só roda com a AST completa, isto é, sem erros léxicos ou
  sintáticos. Os erros saem ordenados por posição.

## 4. Como verificar

```bash
py minilang.py exemplos/validos/fatorial.mlg --symbols --ast
py minilang.py exemplos/invalidos/semantico_tipos.mlg          # 9 erros em uma execução
py minilang.py exemplos/validos/avisos_inicializacao.mlg        # compila, com 2 avisos
py -m unittest discover -s tests -v
```

## 5. Limitações conhecidas

- Há um único escopo (`global`), porque a MiniLang base só declara variáveis na seção `var`. A
  tabela já suporta escopos aninhados.
- Divisão por zero só é detectada quando o divisor é a constante `0`. Expressões como `x / (y - y)`
  ficam para a execução no M4.
- Atribuir à variável de controle dentro do corpo do `para` não é proibido.

## 6. Declaração de uso de IA

- **Ferramenta:** Claude Code (Anthropic, modelo Claude Opus).
- **Uso:** implementação da tabela de símbolos, do analisador semântico, da integração no CLI, dos
  testes e exemplos do M3 e redação de `semantica.md` e desta nota, a pedido da equipe.
- **Responsabilidade:** a equipe revisou e executou o código e os testes, e cada integrante deve
  ser capaz de explicar qualquer trecho (edital, seção 8).
