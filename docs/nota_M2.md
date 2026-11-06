# Nota do Marco M2 — Analisador Sintático + AST

**Projeto:** Compilador MiniLang  
**Disciplina:** Teoria da Computação e Compiladores (UNIFACS 2026.2)  
**Marco:** M2 — Analisador Sintático e Árvore Sintática Abstrata  
**Extensão escolhida:** D (`para ... ate ... passo` e `repita ... ate`)  
**Data:** Novembro de 2026

**Equipe:** Kawan Oliveira (`@kawoliv`), João Guilherme Perrone Hohlenwerger (`@joaohohlenwerger`),
Daniel Costa (`@Danncss`), João Spinola Falcão (`@Falc01`), Pedro Adaime Ribeiro (`@pedrobelane`),
Isabelle Maciel dos Santos (`@isabellesmaciel`)

---

## 1. O que foi entregue

| Item | Onde |
|---|---|
| Gramática EBNF, precedência, *dangling else*, recuperação de erros | [`docs/gramatica.md`](gramatica.md) |
| Parser descendente recursivo (LL(1), manual) | [`minilang/parser.py`](../minilang/parser.py) |
| Nós da AST, `Visitante` e impressão em árvore | [`minilang/arvore.py`](../minilang/arvore.py) |
| Erro `[SINTÁTICO] Linha L, Coluna C: ...` | [`minilang/errors.py`](../minilang/errors.py) |
| CLI com `--ast` (léxico + sintático numa execução) | [`minilang/cli.py`](../minilang/cli.py) |
| 36 testes do parser (48 no total) | [`tests/test_parser.py`](../tests/test_parser.py) |
| 3 novos programas válidos, 4 inválidos sintáticos | [`exemplos/`](../exemplos/) |

## 2. Decisões de projeto

- **Descendente recursivo manual.** Um método por não-terminal; a pilha de chamadas do Python faz o
  papel da pilha do autômato de pilha. Os FIRST das alternativas de `comando` são disjuntos, então
  1 token de *lookahead* basta.
- **Precedência pela estrutura da gramática** (6 níveis: `ou` < `e` < relacionais < `+ -` <
  `* / %` < unários). Os laços `while` de cada nível montam a árvore à esquerda, o que dá
  associatividade à esquerda. Os unários são recursivos à direita.
- **Relacionais não associativos:** `a < b < c` é rejeitado com uma mensagem que sugere `e`.
- **Dangling else:** o `senão` fica com o `se` mais próximo, porque `_condicional` consome o `senão`
  logo após o `então` (escolha gulosa). Isso está documentado com as duas árvores possíveis em
  `gramatica.md` §6 e coberto por teste e por `exemplos/validos/dangling_else.mlg`.
- **AST enxuta e anotável:** sem nós de pontuação; todo nó guarda linha e coluna; expressões têm o
  campo `tipo`, reservado para o M3. `var a, b: inteiro;` gera um `DeclVar` por variável, o que
  prepara a tabela de símbolos.
- **Extensão D na AST:** `Para` e `Repita` são nós próprios. Por enquanto não são traduzidos para
  `enquanto`, já que essa tradução (açúcar sintático) fica para o back-end no M4.

## 3. Recuperação de erros

- **Modo pânico:** um comando ou declaração com erro é descartado até um `;` ou até um token que
  inicia ou encerra um comando, e a análise continua.
- **Nível de frase:** um `;` esquecido antes de um comando na linha seguinte gera **um** erro, e
  nada mais é descartado.
- **Anti-cascata:** erros repetidos na mesma posição são suprimidos, e as condições de `se` e
  `enquanto` se recuperam localmente.
- **Erros léxicos não interrompem o parser:** os dois tipos de erro aparecem juntos. Exemplo:
  `exemplos/invalidos/sintatico_multiplos_erros.mlg` gera 7 erros em uma execução.

## 4. Como verificar

```bash
py minilang.py exemplos/validos/dangling_else.mlg --ast
py minilang.py exemplos/invalidos/sintatico_multiplos_erros.mlg
py -m unittest discover -s tests -v
```

## 5. Limitações conhecidas

- A condição sem parênteses obriga `não` a ter a maior precedência: `não x > 0` é `(não x) > 0`.
  O M3 vai acusar o erro de tipo nesse caso.
- Erros em sequência muito próximos ainda podem gerar uma mensagem em cascata (por exemplo, um
  `senão` cujo `se` teve a condição descartada).

## 6. Declaração de uso de IA

- **Ferramenta:** Claude Code (Anthropic, modelo Claude Opus).
- **Uso:** implementação do parser, da AST, da integração no CLI, dos testes e exemplos do M2 e
  redação de `gramatica.md` e desta nota, a pedido da equipe.
- **Responsabilidade:** a equipe revisou e executou o código e os testes, e cada integrante deve
  ser capaz de explicar qualquer trecho (edital, seção 8).
