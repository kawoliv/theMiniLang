# Back-End e Execução da MiniLang — Marco M4

Após as fases de análise léxica (M1), sintática com construção da AST (M2) e semântica com checagem
de tipos (M3), o **back-end** (`minilang/interpretador.py`) recebe a Árvore Sintática Abstrata
validada e anotada e a **executa diretamente** por meio do padrão *Visitor* (`Interpretador(Visitante)`).

---

## 1. Arquitetura e modelo de memória

O interpretador mantém o estado de execução do programa em estruturas de dados em memória:

| Atributo | Tipo | Significado |
|---|---|---|
| `memoria` | `dict[str, int \| bool]` | Valor atual de cada variável declarada (`inteiro` ou `booleano`) |
| `tipos` | `dict[str, str]` | Tipo declarado de cada variável (`"inteiro"` ou `"booleano"`) |
| `linhas_saida` | `list[str]` | Histórico de todas as linhas emitidas pelo comando `escreva` |
| `historico_trace` | `list[str]` | Passo a passo das instruções executadas quando `--trace` está ativo |

### 1.1 Inicialização de variáveis (`DeclVar`)

Ao percorrer as declarações na seção `var`, cada variável é registrada no ambiente com um valor
padrão determinístico:
- `inteiro` $\to$ `0`
- `booleano` $\to$ `False` (`falso`)

Essa decisão garante que programas sintática e semanticamente válidos que possuam apenas **avisos**
de inicialização (como [`exemplos/validos/avisos_inicializacao.ml`](../exemplos/validos/avisos_inicializacao.ml))
possam ser executados com segurança sem lançar exceções internas do Python (`KeyError`).

### 1.2 Injeção de Entrada e Saída (Testabilidade)

O construtor `Interpretador(entrada=..., saida=..., max_iteracoes=..., prompt_interativo=..., trace=...)`
desacopla a execução do terminal físico:
- **`entrada`**: aceita `None` (`input` padrão), uma função `Callable[[], str]`, um fluxo com
  `.readline()` (como `sys.stdin` ou `io.StringIO`) ou qualquer iterável de valores (ex.: `["5"]`).
- **`saida`**: aceita qualquer fluxo de texto (padrão `sys.stdout`) ou `None` (modo silencioso para
  testes que inspecionam apenas `interpretador.linhas_saida`).

---

## 2. Semântica operacional das expressões

Cada método `visitar_<Expressao>` avalia recursivamente a subárvore e devolve um valor nativo
(`int` ou `bool`):

| Expressão | Operação em tempo de execução | Observações |
|---|---|---|
| `Numero(v)` | devolve `int(v)` | literal inteiro |
| `Booleano(v)` | devolve `bool(v)` | `True` (`verdadeiro`) ou `False` (`falso`) |
| `Identificador(nome)` | consulta `self.memoria[nome]` | erro `[EXECUÇÃO]` se não declarada |
| `-x` | `-valor` | negação aritmética |
| `não x` | `not valor` | negação lógica |
| `a + b`, `a - b`, `a * b` | `+`, `-`, `*` | aritmética inteira |
| `a / b`, `a % b` | `dividir_inteiro(a, b)`, `modulo_inteiro(a, b)` | verifica divisor `b == 0` em runtime |
| `a < b`, `a <= b`, `a > b`, `a >= b` | `<`, `<=`, `>`, `>=` | devolve `bool` |
| `a == b`, `a != b` | `==`, `!=` | compara valores do mesmo tipo |
| `a e b` | `bool(a) and bool(b)` | **curto-circuito**: não avalia `b` se `a` for `falso` |
| `a ou b` | `bool(a) or bool(b)` | **curto-circuito**: não avalia `b` se `a` for `verdadeiro` |

### 2.1 Curto-circuito lógico

Nos operadores lógicos `e` e `ou`, o operando direito só é avaliado quando o operando esquerdo não
determina sozinho o resultado. Por exemplo, em:

```pascal
se x != 0 e (10 / x > 1) { ... }
```

quando `x` vale `0`, o lado esquerdo (`x != 0`) resulta em `falso` e a divisão `10 / x` **não é
executada**, evitando divisão por zero.

### 2.2 Funções aritméticas compartilhadas com o Otimizador

As operações de divisão inteira e resto são isoladas nas funções de módulo `dividir_inteiro(esq, dir)`
e `modulo_inteiro(esq, dir)` em [`minilang/interpretador.py`](../minilang/interpretador.py). Isso
permite que o módulo de otimização (`--optimize`) utilize exatamente a mesma regra aritmética ao
dobrar constantes em tempo de compilação.

---

## 3. Semântica operacional dos comandos

| Comando | Comportamento na execução |
|---|---|
| `x = expr;` | avalia `expr` e atualiza `self.memoria["x"]` |
| `leia(x);` | lê uma linha da entrada e converte para o tipo de `x` (`inteiro` ou `booleano`) |
| `escreva(e1, ..., en);` | avalia os argumentos na ordem e imprime em uma linha separados por espaço |
| `se c A [senão B]` | avalia `c`; se `verdadeiro` executa `A`, caso contrário executa `B` (se existir) |
| `enquanto c A` | repete `A` enquanto `c` avaliar para `verdadeiro` |
| `para i = a ate b [passo p] A` | laço contado com passo positivo ou negativo e limite `b` inclusivo |
| `repita A ate c;` | executa `A` ao menos uma vez e encerra quando `c` avaliar para `verdadeiro` |

### 3.1 Formatação de saída no `escreva`

Em Python, a classe `bool` herda de `int` (`isinstance(True, int) == True`). Por isso, a função
`formatar_valor(valor)` testa `isinstance(valor, bool)` **antes** de `int`, garantindo que valores
booleanos sejam sempre impressos no vocabulário da MiniLang (`verdadeiro` e `falso`) e nunca como
`True`/`False` ou `1`/`0`.

### 3.2 Extensão D: `para` e `repita ... até`

- **Laço `para`**:
  1. Avalia `inicio`, `limite` e `passo` (quando omitido, `passo = 1`) uma única vez na entrada do laço.
  2. Verifica se `passo == 0` (caso o passo venha de uma variável ou expressão dinâmica); se for zero,
     lança `ExecutionError` para impedir laço infinito.
  3. Atribui `inicio` à variável de controle na memória (mesmo que o corpo execute 0 vezes).
  4. Se `passo > 0`, repete enquanto `memoria[var] <= limite`; se `passo < 0` (contagem regressiva,
     como em [`exemplos/validos/lacos_aninhados.ml`](../exemplos/validos/lacos_aninhados.ml)), repete
     enquanto `memoria[var] >= limite`.
  5. Ao final de cada iteração, incrementa `memoria[var] = memoria[var] + passo`.

- **Laço `repita ... até`**:
  Segue a semântica *repeat-until* (pós-condição de parada): executa o bloco do corpo e, ao final de
  cada volta, avalia a condição `ate`. Quando a condição resulta em `verdadeiro`, o laço termina.

---

## 4. Erros em tempo de execução

Embora o analisador semântico (M3) elimine erros de tipo e divisão por zero literal (`10 / 0`),
erros que dependem de valores dinâmicos (como entradas do usuário via `leia`) são capturados pelo
interpretador através da exceção `ExecutionError` ([`minilang/errors.py`](../minilang/errors.py)),
mantendo o padrão oficial do edital:

```text
[EXECUÇÃO] Linha L, Coluna C: descrição
```

| Situação | Exemplo de mensagem |
|---|---|
| divisão ou módulo por zero dinâmico (`x / y` com `y = 0`) | `[EXECUÇÃO] Linha 5, Coluna 19: divisão por zero` |
| passo zero dinâmico no `para` (`passo p` com `p = 0`) | `[EXECUÇÃO] Linha 5, Coluna 34: o passo do 'para' não pode ser zero` |
| texto inválido lido em `leia(n)` para variável `inteiro` | `[EXECUÇÃO] Linha 6, Coluna 3: valor inválido 'abc' para leitura de 'n' (esperado inteiro)` |
| texto inválido lido em `leia(b)` para variável `booleano` | `[EXECUÇÃO] Linha 6, Coluna 3: valor inválido 'talvez' para leitura de 'b' (esperado 'verdadeiro' ou 'falso')` |
| fim de arquivo (`EOF`) inesperado durante `leia(x)` | `[EXECUÇÃO] Linha 6, Coluna 3: fim de entrada inesperado ao ler 'x'` |
| limite de segurança de iterações excedido (em testes) | `[EXECUÇÃO] Linha 5, Coluna 1: limite máximo de 50 iterações excedido (possível laço infinito)` |

---

## 5. Interatividade na CLI, `--trace` e resumo de memória

A interface de linha de comando ([`minilang/cli.py`](../minilang/cli.py)) integra o interpretador
seguindo duas regras principais:

1. **Execução padrão**: ao rodar `py minilang.py programa.ml` (sem flags de inspeção estática
   `--tokens`, `--ast` ou `--symbols`), o programa é compilado e imediatamente executado.
2. **Inspeção combinada com execução (`--run` e `--trace`)**:
   - `--ast`, `--tokens` e `--symbols` sozinhos apenas inspecionam a estrutura da compilação.
   - Passando `--run` (ex.: `py minilang.py programa.ml --ast --run`), o compilador exibe a estrutura
     solicitada e em seguida executa o programa.
   - Passando `--trace` (ex.: `py minilang.py programa.ml --trace`), o interpretador exibe cada
     instrução executada com linha e coluna (`[TRACE L10:C5] fat = 20`) e imprime ao final a tabela
     **Estado Final da Memória**:

```text
[LEIA] Digite um valor (inteiro) para 'n': 5
120
==============================================
ESTADO FINAL DA MEMÓRIA (Marco 4 - Interpretador)
==============================================
VARIÁVEL         | TIPO      | VALOR FINAL    
----------------------------------------------
n                | inteiro   | 5              
i                | inteiro   | 1              
fat              | inteiro   | 120            
----------------------------------------------
```

Quando executado diretamente em um terminal interativo (`isatty()`), o comando `leia` exibe
automaticamente o prompt `[LEIA] Digite um valor (<tipo>) para '<var>': ` e apresenta o resumo
final da memória ao encerrar o programa.

---

## 6. Otimização de Código (`--optimize`) — *[A Preencher]*

> **[ESPAÇO RESERVADO — INTEGRANTE RESPONSÁVEL PELA OTIMIZAÇÃO]**
>
> Esta seção deve documentar a implementação da otimização do Marco 4:
> - **Técnica escolhida:** *Constant Folding* (dobradura de constantes) e/ou propagação de constantes sobre a AST.
> - **Módulo:** `minilang/otimizador.py` (sugestão: classe `Otimizador(Visitante)` recebendo e devolvendo `Programa`).
> - **Contrato com o Interpretador:**
>   - Importar `dividir_inteiro` e `modulo_inteiro` de `minilang.interpretador` para manter a mesma semântica aritmética.
>   - Preservar os campos `linha`, `coluna` e `tipo` nos nós `Numero` e `Booleano` gerados pela dobradura.
>   - Em `minilang/cli.py`, aplicar a transformação antes da impressão de `--ast` e antes da chamada a `interpretar(programa)`, permitindo comparar a árvore antes e depois com `--ast` vs. `--ast --optimize`.
> - **Exemplos de antes e depois (`--ast` vs. `--ast --optimize`):** *(inserir comparativo aqui)*.
