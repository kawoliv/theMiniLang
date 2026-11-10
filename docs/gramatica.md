# Gramática da MiniLang — Marco M2

Este documento define a **gramática livre de contexto** da MiniLang em EBNF, explica como ela
foi transformada no parser descendente recursivo (`minilang/parser.py`) e documenta as decisões de
precedência, associatividade, *dangling else* e recuperação de erros.

---

## 1. Notação

| Símbolo | Significado |
|---|---|
| `::=` | definição de um não-terminal |
| `\|` | alternativa |
| `[ x ]` | `x` é opcional (0 ou 1 vez) |
| `{ x }` | `x` se repete 0 ou mais vezes |
| `"se"` | terminal (palavra reservada ou símbolo) |
| `IDENT`, `NUM_INT` | terminais produzidos pelo léxico (ver [afd.md](afd.md)) |

---

## 2. Gramática em EBNF

```ebnf
(* ---------- Estrutura do programa ---------- *)
programa        ::= "programa" IDENT { declaracoes } bloco "fim" "." ;

declaracoes     ::= "var" declaracao { declaracao } ;
declaracao      ::= lista_ids ":" tipo ";" ;
lista_ids       ::= IDENT { "," IDENT } ;
tipo            ::= "inteiro" | "booleano" ;

(* ---------- Comandos ---------- *)
bloco           ::= "{" { comando } "}" ;

comando         ::= atribuicao
                  | leitura
                  | escrita
                  | condicional
                  | enquanto
                  | para                       (* extensão D *)
                  | repita                     (* extensão D *)
                  | bloco ;

atribuicao      ::= IDENT "=" expressao ";" ;
leitura         ::= "leia" "(" IDENT ")" ";" ;
escrita         ::= "escreva" "(" expressao { "," expressao } ")" ";" ;
condicional     ::= "se" expressao comando [ "senão" comando ] ;
enquanto        ::= "enquanto" expressao comando ;

(* ---------- Extensão D ---------- *)
para            ::= "para" IDENT "=" expressao "ate" expressao [ "passo" expressao ] comando ;
repita          ::= "repita" { comando } "ate" expressao ";" ;

(* ---------- Expressões (da menor para a maior precedência) ---------- *)
expressao       ::= expr_ou ;
expr_ou         ::= expr_e { "ou" expr_e } ;
expr_e          ::= expr_relacional { "e" expr_relacional } ;
expr_relacional ::= expr_aditiva [ op_relacional expr_aditiva ] ;
expr_aditiva    ::= expr_multiplicativa { ( "+" | "-" ) expr_multiplicativa } ;
expr_multiplicativa ::= expr_unaria { ( "*" | "/" | "%" ) expr_unaria } ;
expr_unaria     ::= ( "-" | "não" ) expr_unaria
                  | primaria ;
primaria        ::= NUM_INT
                  | "verdadeiro" | "falso"
                  | IDENT
                  | "(" expressao ")" ;

op_relacional   ::= "==" | "!=" | "<" | "<=" | ">" | ">=" ;
```

Observações:

- `senão`/`senao`, `não`/`nao` e `ate`/`até` são o mesmo terminal (o léxico já os unifica).
- A condição de `se`/`enquanto` **não exige parênteses**: `se x > 0 { ... }`. Isso não gera
  ambiguidade porque nenhum comando começa com um operador ou com `(`; a expressão termina assim
  que aparece um token que não pode continuá-la.
- Exemplos completos de programas válidos estão em [`exemplos/validos/`](../exemplos/validos/).

---

## 3. Classificação na Hierarquia de Chomsky

- A gramática acima é **livre de contexto (tipo 2)**: todo lado esquerdo é um único não-terminal.
- Ela **não é regular (tipo 3)**: blocos `{ ... }` e parênteses podem ser aninhados sem limite,
  e um AFD não consegue "contar" aberturas e fechamentos. Por isso o M2 precisa de um
  **autômato de pilha**, que no nosso parser é a **pilha de chamadas do Python**: cada método
  `_nome()` corresponde a um não-terminal, e entrar/sair do método equivale a empilhar/desempilhar.
- Regras que dependem de contexto (variável declarada antes do uso, tipos compatíveis) **não** são
  expressas pela gramática; elas ficam para o analisador semântico (M3).

---

## 4. Do EBNF ao parser descendente recursivo (LL(1))

O parser é **preditivo**: olhando só o token atual (1 token de *lookahead*) ele decide qual regra
aplicar. Para isso a gramática foi escrita sem recursão à esquerda (as repetições `{ ... }` viram
laços `while`) e cada alternativa de `comando` começa com um token diferente:

| Alternativa de `comando` | FIRST (token que a inicia) |
|---|---|
| `atribuicao` | `IDENT` |
| `leitura` | `leia` |
| `escrita` | `escreva` |
| `condicional` | `se` |
| `enquanto` | `enquanto` |
| `para` | `para` |
| `repita` | `repita` |
| `bloco` | `{` |

Como os conjuntos FIRST são disjuntos, um único `if/elif` sobre o token atual escolhe a regra
(`Parser._comando`). O único conflito LL(1) da gramática é o *dangling else* (seção 6).

---

## 5. Precedência e associatividade

A precedência é codificada pela **ordem dos níveis da gramática**: quanto mais "fundo" o
não-terminal, maior a precedência. Operadores do mesmo nível são processados por um laço que vai
montando a árvore para a esquerda, o que dá **associatividade à esquerda**.

| Precedência | Operadores | Associatividade | Não-terminal |
|---|---|---|---|
| 1 (menor) | `ou` | esquerda | `expr_ou` |
| 2 | `e` | esquerda | `expr_e` |
| 3 | `==` `!=` `<` `<=` `>` `>=` | **não associativos** | `expr_relacional` |
| 4 | `+` `-` (binários) | esquerda | `expr_aditiva` |
| 5 | `*` `/` `%` | esquerda | `expr_multiplicativa` |
| 6 (maior) | `-` `não` (unários) | direita | `expr_unaria` |

Exemplos de árvores construídas:

```
10 - 3 - 2        →  (10 - 3) - 2              associatividade à esquerda
1 + 2 * 3         →  1 + (2 * 3)               * tem precedência sobre +
a ou b e c        →  a ou (b e c)              e tem precedência sobre ou
x + 1 > y * 2     →  (x + 1) > (y * 2)         aritmética antes da relação
- - x             →  -(-x)                     unários associam à direita
não a e b         →  (não a) e b               unário tem a maior precedência
```

**Relacionais não associativos.** A regra `expr_relacional ::= expr_aditiva [ op expr_aditiva ]`
permite **no máximo um** operador relacional por nível. `a < b < c` é rejeitado com uma mensagem
explicativa, porque `(a < b) < c` compararia um booleano com um inteiro. O programador deve
escrever `a < b e b < c`.

**`não` com maior precedência.** Assim como `!` em C e `not` em Pascal, `não` se liga ao operando
mais próximo: `não x > 0` é lido como `(não x) > 0`. Para negar a comparação inteira, usa-se
`não (x > 0)`. A verificação de que o operando de `não` é booleano fica para o M3.

---

## 6. *Dangling else*

### O problema

Com as regras

```ebnf
condicional ::= "se" expressao comando [ "senão" comando ] ;
comando     ::= condicional | ... ;
```

o programa

```
se a > 0
  se b > 0
    escreva(1);
senão
  escreva(2);
```

tem **duas árvores sintáticas** possíveis, logo a gramática é **ambígua**:

```
Interpretação 1 (adotada)              Interpretação 2
Se (a > 0)                             Se (a > 0)
└── então: Se (b > 0)                  ├── então: Se (b > 0)
    ├── então: escreva(1)              │   └── então: escreva(1)
    └── senão: escreva(2)              └── senão: escreva(2)
```

Em termos LL(1): depois de reconhecer `se b > 0 escreva(1);`, o token `senão` está tanto em
FIRST(`[ "senão" comando ]`) quanto em FOLLOW(`condicional`), então a tabela preditiva teria duas
ações para a mesma célula.

### A resolução

O `senão` é associado ao **`se` mais próximo que ainda não tem `senão`** (interpretação 1), a mesma
convenção de C, Java e Pascal. No parser isso é obtido de forma natural: `Parser._condicional`,
logo após ler o comando do `então`, **consome o `senão` se ele for o próximo token** (escolha
"gulosa"). Como o `se` interno é analisado dentro do externo, é ele que encontra o `senão` primeiro.

```python
entao = self._comando()
senao = None
if self._aceita(TokenType.SENAO):   # o 'se' mais interno fica com o 'senão'
    senao = self._comando()
```

**Por que não mudar a gramática?** Daria para eliminar a ambiguidade com não-terminais
`comando_casado`/`comando_aberto`, mas a gramática fica bem menos legível e a árvore resultante é
idêntica. Também seria possível exigir `{ }` no corpo do `se` (como Go e Rust), o que tornaria a
ambiguidade impossível; preferimos manter a forma clássica e documentar a regra. Para obter a
interpretação 2, o programador usa chaves:

```
se a > 0 {
  se b > 0 escreva(1);
} senão
  escreva(2);
```

Os dois casos estão em [`exemplos/validos/dangling_else.mlg`](../exemplos/validos/dangling_else.mlg)
e no teste `test_dangling_else_associa_ao_se_mais_proximo`.

---

## 7. Árvore Sintática Abstrata (AST)

A AST é definida em [`minilang/arvore.py`](../minilang/arvore.py). Ela guarda apenas o que importa
para as próximas fases: pontuação (`;`, `(`, `{`, `fim.`) **não** vira nó. Todo nó registra a
`linha` e a `coluna` do token que o originou, e todo nó de expressão tem o campo `tipo`, que fica
vazio no M2 e será preenchido pelo analisador semântico no M3.

| Nó | Campos | Origem na gramática |
|---|---|---|
| `Programa` | `nome`, `declaracoes`, `corpo` | `programa` |
| `DeclVar` | `nome`, `tipo` | um nó por identificador de `declaracao` |
| `Bloco` | `comandos` | `bloco` |
| `Atribuicao` | `alvo`, `valor` | `atribuicao` |
| `Leia` | `alvo` | `leitura` |
| `Escreva` | `argumentos` | `escrita` |
| `Se` | `condicao`, `entao`, `senao` (opcional) | `condicional` |
| `Enquanto` | `condicao`, `corpo` | `enquanto` |
| `Para` | `variavel`, `inicio`, `limite`, `passo` (opcional), `corpo` | `para` |
| `Repita` | `corpo` (um `Bloco`), `condicao` | `repita` |
| `Binaria` | `op`, `esq`, `dir` | operadores binários |
| `Unaria` | `op`, `operando` | `-` e `não` unários |
| `Numero` | `valor` | `NUM_INT` |
| `Booleano` | `valor` | `verdadeiro` / `falso` |
| `Identificador` | `nome` | `IDENT` em expressões e como alvo |

A AST é **navegável**: `No.filhos()` devolve os filhos de qualquer nó, a classe `Visitante`
implementa o padrão *Visitor* (que será usado no M3 e no M4) e `formatar_arvore()` imprime a árvore,
o que pode ser feito pela linha de comando com `--ast`.

---

## 8. Erros sintáticos e recuperação

Mensagens seguem o padrão do edital:

```
[SINTÁTICO] Linha L, Coluna C: esperado ')' para fechar '(' aberto na linha 7, coluna 12, mas encontrado ';'
```

O parser **não para no primeiro erro**. Ele usa duas estratégias:

1. **Modo pânico (nível de comando e de declaração).** Quando um comando falha, o erro é registrado
   e o parser descarta tokens até um **ponto de sincronização**: um `;` (que é consumido) ou um
   token que inicia ou encerra um comando (`se`, `enquanto`, `para`, `repita`, `leia`, `escreva`,
   `{`, `}`, `senão`, `ate`, `fim`). Em seguida retoma a análise normalmente. Nas declarações, a
   sincronização é feita no `;`, em um novo `var` ou no `{` que abre o corpo do programa. Um `;`
   esquecido antes de `var` ou `{` é tratado em nível de frase, sem descartar a declaração.
2. **Nível de frase para `;` esquecido.** Se falta o `;` e o próximo token já começa um novo comando
   **em outra linha** (ou é `}`/`fim`), o parser registra o erro e age como se o `;` estivesse lá,
   sem descartar nada. Assim, um `;` esquecido gera **um** erro e não esconde o comando seguinte.

Para evitar erros em cascata, um segundo erro na mesma posição do anterior é descartado, e a
condição de `se`/`enquanto` tem recuperação local, ressincronizando no início do corpo.
