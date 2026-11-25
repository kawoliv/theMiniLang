# Nota do Marco M4 — Back-End, Otimização e Execução

**Projeto:** Compilador MiniLang  
**Disciplina:** Teoria da Computação e Compiladores (UNIFACS 2026.2)  
**Marco:** M4 — Back-End (Interpretador da AST), Otimização e Apresentação  
**Extensão escolhida:** D (`para ... ate ... passo` e `repita ... ate`)  
**Data:** Novembro de 2026

**Equipe:** Kawan Oliveira (`@kawoliv`), João Guilherme Perrone Hohlenwerger (`@joaohohlenwerger`),
Daniel Costa (`@Danncss`), João Spinola Falcão (`@Falc01`), Pedro Adaime Ribeiro (`@pedrobelane`),
Isabelle Maciel dos Santos (`@isabellesmaciel`)

---

## 1. O que foi entregue

| Item | Onde |
|---|---|
| Especificação técnica do Back-End, memória, `--trace` e erros de execução | [`docs/backend.md`](backend.md) |
| Interpretador direto da AST (`Interpretador(Visitante)`) | [`minilang/interpretador.py`](../minilang/interpretador.py) |
| Erro `[EXECUÇÃO] Linha L, Coluna C: ...` (`ExecutionError`) | [`minilang/errors.py`](../minilang/errors.py) |
| CLI: execução padrão, `--run`, `--trace`, prompt `[LEIA]` e tabela de memória | [`minilang/cli.py`](../minilang/cli.py) |
| 31 testes automatizados do Back-End | [`tests/test_interpretador.py`](../tests/test_interpretador.py) |
| Módulo de Otimização (`Otimizador(Visitante)` com Constant Folding e LICM, flag `--optimize`) | [`minilang/otimizador.py`](../minilang/otimizador.py) |
| 10 testes automatizados de Otimização (130 testes no total da suíte) | [`tests/test_otimizador.py`](../tests/test_otimizador.py) |

## 2. Cobertura da rubrica

| Critério | Como |
|---|---|
| Back-end funcional (4,0) | `Interpretador(Visitante)` executa toda a linguagem base e a Extensão D sobre a AST anotada |
| Otimização demonstrada (1,5) | Dobradura de Constantes (*Constant Folding*) e Movimentação de Invariantes de Laço (LICM) ativadas via `--optimize` |
| Relatório Técnico de 6 a 10 páginas (2,5) | Consolidado a partir de `afd.md`, `gramatica.md`, `semantica.md` e `backend.md` |
| Apresentação e arguição oral + domínio individual (2,0) | Modo interativo com `[LEIA]`, rastreamento `--trace` e tabela de estado final da memória |

## 3. Decisões de projeto

### 3.1 Back-End (Interpretador da AST)

- **Interpretação direta via Visitor:** `Interpretador` herda de `Visitante` (`minilang/arvore.py`),
  mantendo simetria direta com o `AnalisadorSemantico` (M3). Os métodos `visitar_<Expressao>`
  devolvem valores nativos (`int` ou `bool`) e os métodos `visitar_<Comando>` atualizam o dicionário
  `self.memoria`.
- **Inicialização padrão segura:** toda variável declarada em `DeclVar` é inicializada na memória
  com `0` (`inteiro`) ou `False` (`booleano`), permitindo a execução determinística mesmo em
  programas com avisos de variável potencialmente não inicializada (`avisos_inicializacao.ml`).
- **Curto-circuito e verificações dinâmicas:** `e` e `ou` aplicam curto-circuito lógico real; `/` e
  `%` verificam divisor `0` em tempo de execução; `para` verifica passo `0` dinâmico e suporta
  contagem crescente (`passo > 0`) e regressiva (`passo < 0`).
- **Formatação fiel à linguagem:** `formatar_valor` verifica `isinstance(valor, bool)` antes de
  `int` (já que `bool` é subclasse de `int` em Python), imprimindo sempre `verdadeiro` e `falso`.
- **Interatividade e rastreamento para apresentação:** em terminal interativo, `leia` exibe um
  prompt indicando o nome e o tipo esperado da variável, e o final da execução apresenta a tabela
  com o estado final da memória. A flag `--trace` detalha cada passo executado com linha e coluna.

### 3.2 Otimização (`--optimize`)

- **Dobradura de Constantes (*Constant Folding*):** percorre a AST *bottom-up* substituindo expressões constantes por nós `Numero` ou `Booleano` com `linha`, `coluna` e `tipo` preservados, utilizando `dividir_inteiro` e `modulo_inteiro` de `minilang/interpretador.py`. Expressões com divisão ou módulo por zero não são dobradas para preservar o erro `[EXECUÇÃO]` em runtime, e operadores `e`/`ou` aplicam curto-circuito constante.
- **Movimentação de Código Invariante de Laço (LICM):** analisa laços `enquanto`, `para` e `repita ... ate` do nível mais externo ao mais interno, movendo subexpressões compostas que não dependem de variáveis modificadas no laço (e sem divisão/módulo inseguros) para temporárias `_inv_k` calculadas uma única vez antes do laço.
- **Preservação da AST original e integração com a CLI:** `otimizar(programa)` atua sobre `copy.deepcopy(programa)` e é aplicada em `minilang/cli.py` antes de `--ast` e da execução no interpretador quando `--optimize` é utilizado.

## 4. Como verificar

```bash
# Execução interativa padrão (com prompt [LEIA] e tabela de memória final)
py minilang.py exemplos/validos/fatorial.ml

# Execução passo a passo (rastreamento completo de instruções e memória)
py minilang.py exemplos/validos/fatorial.ml --trace
py minilang.py exemplos/validos/exemplo_repita.ml --trace

# Execução sem entrada de teclado (laços aninhados e expressões)
py minilang.py exemplos/validos/lacos_aninhados.ml
py minilang.py exemplos/validos/expressoes.ml

# Exibição da AST anotada seguida de execução
py minilang.py exemplos/validos/exemplo_para.ml --ast --run

# Verificação da otimização antes/depois e execução otimizada
py minilang.py exemplos/validos/expressoes.ml --ast
py minilang.py exemplos/validos/expressoes.ml --ast --optimize --run

# Suíte completa de testes automatizados (M1 a M4)
py -m unittest discover -s tests -v
```

## 5. Limitações conhecidas

- Como a MiniLang base possui apenas escopo global de variáveis, `self.memoria` utiliza um único
  dicionário plano de execução.
- Operações de entrada via `leia` leem um valor por linha (`\n`).
- A dobradura de constantes e a movimentação de invariantes de laço operam sobre subexpressões individuais sem análise de fluxo de dados interblocos ou propagação de cópias entre comandos sequenciais.

---

## 6. Declaração de Uso de Ferramentas de Inteligência Artificial (IA)

Em conformidade com as diretrizes acadêmicas e de integridade do projeto:

- **Ferramentas utilizadas:** Google Antigravity.
- **Natureza do uso:** 
  - Auxílio na estruturação inicial dos esqueletos dos módulos e formatação dos modos de execução;
  - Apoio na elaboração de casos de testes unitários para cobertura de cenários de borda no interpretador;
  - Revisão e padronização da formatação das documentações do projeto.
- **Autoria e Validação:** Toda a lógica de execução do interpretador, o gerenciamento de memória e as regras do Back-End foram revisadas, testadas e validadas pela equipe do projeto, garantindo conformidade com a especificação da gramática da MiniLang e independência de bibliotecas externas.
