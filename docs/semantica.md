# Análise Semântica da MiniLang — Marco M3

A gramática do M2 é livre de contexto e por isso não consegue expressar regras como "a variável
precisa ter sido declarada antes" ou "os dois lados de `+` devem ser inteiros". Essas regras
**sensíveis ao contexto** são verificadas pelo analisador semântico
(`minilang/semantico.py`), que percorre a AST com o padrão *Visitor*, consulta a **tabela de
símbolos** (`minilang/simbolos.py`) e **anota cada expressão com o seu tipo**.

---

## 1. Tabela de símbolos

Cada variável declarada vira um `Simbolo` com:

| Campo | Significado |
|---|---|
| `nome` | identificador |
| `tipo` | `inteiro` ou `booleano` |
| `escopo` / `nivel` | nome e profundidade do escopo onde foi declarada (`global`, nível 0) |
| `linha`, `coluna` | posição da declaração |
| `usos` | quantas vezes a variável aparece no corpo (leitura ou escrita) |

A tabela é uma **pilha de escopos**: `entrar_escopo()` empilha um dicionário `nome → Simbolo` e
`sair_escopo()` desempilha. A busca (`buscar`) vai do escopo mais interno para o mais externo, e
a redeclaração é verificada apenas no escopo atual (`buscar_local`).

Na MiniLang base todas as declarações ficam na seção `var` do programa, então na prática existe
um único escopo, o `global`. A estrutura em pilha foi mantida porque é a forma clássica de
implementar escopos aninhados e não custa nada a mais. Mesmo depois que um escopo é fechado, a
tabela mantém a lista de todos os símbolos, que é o que `--symbols` imprime.

---

## 2. Sistema de tipos

Os tipos são `inteiro` e `booleano`. Internamente existe também o tipo `erro`, dado a uma
expressão que já tem um problema (por exemplo, uma variável não declarada). Um operando do tipo
`erro` é aceito por qualquer operador sem gerar nova mensagem, o que evita **erros em cascata**.

### 2.1 Regras de tipo das expressões

| Expressão | Operandos exigidos | Tipo resultante |
|---|---|---|
| literal inteiro | — | `inteiro` |
| `verdadeiro`, `falso` | — | `booleano` |
| identificador | — | o tipo declarado |
| `-x` | `inteiro` | `inteiro` |
| `não x` | `booleano` | `booleano` |
| `a + b`, `a - b`, `a * b`, `a / b`, `a % b` | `inteiro`, `inteiro` | `inteiro` |
| `a < b`, `a <= b`, `a > b`, `a >= b` | `inteiro`, `inteiro` | `booleano` |
| `a == b`, `a != b` | mesmo tipo dos dois lados | `booleano` |
| `a e b`, `a ou b` | `booleano`, `booleano` | `booleano` |

Não há conversão implícita: `verdadeiro + 1` e `1 e 2` são erros.

### 2.2 Regras dos comandos

| Comando | Regra |
|---|---|
| `x = expr;` | `x` declarada; tipo de `expr` igual ao tipo de `x` |
| `leia(x);` | `x` declarada |
| `escreva(e1, ..., en);` | cada `ei` é uma expressão válida (qualquer tipo) |
| `se c ...` / `enquanto c ...` | `c` é `booleano` |
| `para i = a ate b passo p ...` | `i` declarada e `inteiro`; `a`, `b`, `p` são `inteiro`; `p` não é a constante `0` |
| `repita ... ate c;` | `c` é `booleano` |
| `var x: T;` | `x` não foi declarada antes no mesmo escopo |

---

## 3. Erros detectados

Todos seguem o padrão `[SEMÂNTICO] Linha L, Coluna C: descrição`.

| Situação | Exemplo de mensagem |
|---|---|
| variável não declarada | `variável 'total' não declarada` |
| `leia` em identificador não declarado | `'leia' em identificador não declarado 'k'` |
| redeclaração | `variável 'x' já declarada na linha 3, coluna 3` |
| atribuição com tipos incompatíveis | `tipos incompatíveis: não é possível atribuir booleano à variável 'x' (inteiro)` |
| condição não booleana | `a condição do 'se' deve ser booleana, mas é do tipo inteiro` |
| operador aritmético com booleano | `operador '+' exige operandos inteiros, mas o operando direito é booleano` |
| operador lógico com inteiro | `operador 'e' exige operandos booleanos, mas o operando esquerdo é inteiro` |
| comparação de tipos diferentes | `operador '==' compara inteiro com booleano; os dois lados devem ter o mesmo tipo` |
| unário com tipo errado | `operador 'não' exige operando booleano, mas recebeu inteiro` |
| divisão por zero constante | `divisão por zero` |
| `para` com variável/limites não inteiros ou passo `0` | `o passo do 'para' não pode ser zero` |

A posição reportada é a do nó relacionado ao erro: o identificador, o operador ou a condição.
Uma variável não declarada é reportada só no **primeiro uso**, para não repetir a mesma mensagem.

## 4. Avisos

Avisos aparecem na saída, mas **não impedem a compilação**:

- **Variável lida antes de ser inicializada** (bônus da rubrica):
  `aviso: variável 'x' pode estar sendo lida antes de ser inicializada`.
- **Variável declarada e nunca usada**: `aviso: variável 'temp' declarada e nunca usada`.

### 4.1 Análise de inicialização

O analisador mantém o conjunto de variáveis **certamente inicializadas** naquele ponto do programa,
seguindo o fluxo de controle de forma conservadora, como faz o Java com *definite assignment*:

| Construção | Efeito no conjunto |
|---|---|
| `x = expr;`, `leia(x);` | `x` entra no conjunto (depois de avaliar `expr`) |
| `se c A senão B` | ao final: interseção do que foi inicializado em `A` e em `B` |
| `se c A` (sem senão) | ao final: o mesmo conjunto de antes (`A` pode não executar) |
| `enquanto c A` | ao final: o mesmo de antes (`A` pode executar 0 vezes) |
| `para i = ... A` | `i` entra no conjunto; o que `A` inicializa é descartado no final |
| `repita A ate c;` | `A` executa pelo menos uma vez: o que ele inicializa é mantido, inclusive para `c` |

Como a análise é conservadora, ela pode avisar sobre um caso que, na prática, nunca acontece
(por exemplo, uma variável lida só a partir da segunda volta do laço). Por isso o resultado é um
**aviso** e não um erro.

---

## 5. Anotação da AST

Todo nó `Expressao` recebe no campo `tipo` o tipo inferido (`inteiro`, `booleano` ou `erro`).
A opção `--ast` mostra a árvore já anotada:

```
└── valor: Binaria '*' : inteiro  [11:15]
    ├── esq: Identificador 'fat' : inteiro  [11:11]
    └── dir: Identificador 'i' : inteiro  [11:17]
```

O back-end (M4) vai usar essas anotações e a tabela de símbolos para gerar o código de três
endereços.
