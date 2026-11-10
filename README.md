# 💻 MiniLang — Compilador e Interpretador

Projeto prático de avaliação semestral (**A3**) da disciplina de **Teoria da Computação e Compiladores (0006964)**.  
**Universidade Salvador (UNIFACS)** — Período Letivo: **2026.2**  
**Docente**: Prof. Daniel Santana  
**Valor da Avaliação**: 40 Pontos | **Carga Horária**: 160h  

---

## 📖 Sobre o Projeto

O objetivo deste projeto é projetar e implementar um **compilador completo** para a linguagem imperativa **MiniLang**, percorrendo todas as etapas clássicas de compilação: **análise léxica (M1)**, **análise sintática com construção de Árvore Sintática Abstrata - AST (M2)**, **análise semântica com tabela de símbolos e checagem de tipos (M3)**, e **back-end com otimização demonstrada (M4)**.

O compilador é implementado em **Python 3** puro (sem bibliotecas externas e sem geradores automáticos de analisadores), com execução unificada via linha de comando e suíte com **84 testes automatizados**.

---

## 🚀 Como Executar o Compilador (Linha Única)

Conforme exigido pelo **Item 1 do Checklist Oficial da Disciplina**, o compilador executa através de uma **linha de comando única**:

```bash
# Execução padrão (análise léxica, sintática e semântica com código de saída 0 ou 1)
python minilang.py exemplos/validos/fatorial.mlg

# Inspeção Léxica (M1 - Exibe a tabela detalhada de tokens reconhecidos)
python minilang.py exemplos/validos/fatorial.mlg --tokens

# Inspeção Sintática (M2 - Exibe a Árvore Sintática Abstrata - AST navegável)
python minilang.py exemplos/validos/fatorial.mlg --ast

# Inspeção Semântica (M3 - Exibe a Tabela de Símbolos completa com escopos e tipos)
python minilang.py exemplos/validos/fatorial.mlg --symbols

# Inspeção Combinada (M3 - Exibe a AST anotada com tipos inferidos e a Tabela de Símbolos)
python minilang.py exemplos/validos/fatorial.mlg --ast --symbols

# Otimização demonstrada (M4 - Constant Folding / Propagação de Constantes)
python minilang.py exemplos/validos/fatorial.mlg --optimize
```

> **Dica (Windows):** Você também pode executar utilizando `py` em vez de `python`. O compilador suporta extensões `.mlg` e `.ml`.

### Execução Alternativa via Módulo Python

```bash
python -m minilang exemplos/validos/fatorial.mlg --ast
```

---

## 🧪 Suíte de Testes Automatizados

O repositório conta com uma bateria rigorosa de testes cobrindo casos válidos, casos inválidos e recuperação de erros em todas as fases:

```bash
python -m unittest discover -s tests -v
```

* **Marco 1 (Léxico)**: 12 testes ([`tests/test_lexer.py`](tests/test_lexer.py))
* **Marco 2 (Sintático)**: 36 testes ([`tests/test_parser.py`](tests/test_parser.py))
* **Marco 3 (Semântico)**: 36 testes ([`tests/test_semantico.py`](tests/test_semantico.py))
* **Total:** **84/84 testes passando com sucesso**.

---

## 📜 Especificação Oficial da Linguagem MiniLang

A **MiniLang** é uma linguagem imperativa estruturada com tipagem estática e suporte a comandos de entrada/saída, condicionais, repetições e expressões:

| Categoria | Especificação Oficial do Edital |
| :--- | :--- |
| **Palavras Reservadas (18)** | • **Base (15)**: `programa`, `var`, `inteiro`, `booleano`, `se`, `senão`, `enquanto`, `escreva`, `leia`, `verdadeiro`, `falso`, `e`, `ou`, `não`, `fim`<br>• **Extensão Oficial (Opção D - 3)**: `para`, `repita`, `até` (e `passo`) |
| **Identificadores** | Inicia obrigatoriamente com uma letra, seguida de letras, dígitos ou sublinhado `_`. Não pode coincidir com palavras reservadas. |
| **Tipos Primitivos** | `inteiro` (ex: `0`, `42`, `-10`) e `booleano` (`verdadeiro`, `falso`). |
| **Operadores** | • **Aritméticos**: `+`, `-`, `*`, `/`, `%`<br>• **Relacionais**: `==`, `!=`, `<`, `<=`, `>`, `>=`<br>• **Lógicos**: `e`, `ou`, `não`<br>• **Atribuição**: `=` |
| **Delimitadores** | Parênteses `( )`, Chaves `{ }`, Ponto e vírgula `;`, Dois-pontos `:`, Vírgula `,` e Ponto final `.` |
| **Comentários** | Caractere `#` até o final da linha (comentário de linha única, descartado pelo analisador léxico). |
| **Padrão de Erros** | Todas as fases reportam: **`[FASE] Linha L, Coluna C: Descrição objetiva`**. |

### Exemplo de Código MiniLang Válido (`.mlg` / `.ml`)
```pascal
# Calculo de Fatorial em MiniLang
programa fatorial
var
  n, i, fat: inteiro;
{
  leia(n);
  fat = 1;
  i = n;
  enquanto i > 1 {
    fat = fat * i;
    i = i - 1;
  }
  escreva(fat);
}
fim.
```

---

## ✅ Checklist Oficial de Avaliação (Seção 11 do Edital)

Este checklist espelha as exigências formais de conformidade estabelecidas pelo professor Daniel Santana:

- [x] **1. Execução em linha de comando única documentada no README**: O compilador executa diretamente por `python minilang.py <arquivo>`.
- [x] **2. Repositório Git oficial disponibilizado ao professor**: Repositório [`kawoliv/theMiniLang`](https://github.com/kawoliv/theMiniLang.git) configurado com governança, commits frequentes e histórico transparente.
- [x] **3. Bateria de testes válidos e inválidos**: Suíte de 84 testes automatizados em `tests/` cobrindo casos válidos e programas inválidos provocados em `exemplos/invalidos/`.
- [x] **4. Mensagens de erro padronizadas com fase, linha e coluna**: Padrão canônico `[LÉXICO]`, `[SINTÁTICO]` e `[SEMÂNTICO]` rigorosamente implementado.
- [x] **5. AST navegável e inspecionável**: Construção de Árvore Sintática Abstrata completa e imprimível via flag `--ast`.
- [x] **6. Tabela de Símbolos completa**: Registra identificador, tipo, escopo, nível, posição de declaração e contagem de usos via flag `--symbols`.
- [x] **7. Extensão obrigatória implementada (Opção D: `para` e `repita ... até`)**: Integrada no léxico, na gramática EBNF, na AST e na análise semântica.
- [ ] **8. Relatório técnico final de 6 a 10 páginas (M4)**: Em elaboração para a entrega final, declarando decisões, EBNF, AFD, ferramentas e uso de IA.
- [ ] **9. Domínio individual do código na arguição oral (M4)**: Preparação de todos os integrantes para a apresentação de 15 minutos com demo ao vivo.

---

## 📅 Marcos Cumulativos e Pontuação (Total: 40 Pontos)

| Marco | Prazo Estimado | Pontos | Status | Conteúdo / Entregáveis Principais |
| :---: | :---: | :---: | :---: | :--- |
| **M1** | Semana 7 (~21/09) | **8 pts** | **Concluído** ✅ | **Analisador Léxico**: Reconhecimento de todos os tokens, lookahead de 2 caracteres (`==`, `!=`, `<=`, `>=`), rastreamento de linha/coluna, descarte de comentários `#`, diagrama Mermaid e tabela AFD ([`docs/afd.md`](docs/afd.md)), e Nota M1 ([`docs/nota_M1.md`](docs/nota_M1.md)). |
| **M2** | Semana 10 (~12/10) | **12 pts** | **Concluído** ✅ | **Analisador Sintático + AST**: Gramática EBNF ([`docs/gramatica.md`](docs/gramatica.md)), parser descendente recursivo LL(1) manual, nós da AST com padrão Visitor ([`minilang/arvore.py`](minilang/arvore.py)), resolução do *dangling else*, recuperação de erros em modo pânico e nível de frase, e Nota M2 ([`docs/nota_M2.md`](docs/nota_M2.md)). |
| **M3** | Semana 14 (~09/11) | **10 pts** | **Concluído** ✅ | **Analisador Semântico**: Tabela de símbolos com pilha de escopos ([`minilang/simbolos.py`](minilang/simbolos.py)), verificação de declaração prévia, detecção de redeclaração, checagem estrita de tipos, AST anotada ([`docs/semantica.md`](docs/semantica.md)), bônus de análise de inicialização e Nota M3 ([`docs/nota_M3.md`](docs/nota_M3.md)). |
| **M4** | Semana 17 (~30/11) | **10 pts** | **Em Planejamento** ⏳ | **Back-End, Otimização e Apresentação**: Interpretador da AST (ou TAC), otimização com comparativo antes/depois (*Constant Folding* via `--optimize`), relatório técnico final de 6 a 10 páginas e apresentação de 15 min com arguição oral individual. |

---

## 🧩 Extensão Obrigatória: Opção D — Comandos `para` e `repita ... até`

A equipe escolheu e implementou formalmente a **Opção D (Comandos `para` e `repita ... até`)**, expandindo a linguagem base com duas estruturas de repetição consolidadas:

### 1. Comando `para` (Laço Contado com Limites e Passo Opcional)
```pascal
para i = 1 ate 10 passo 2 {
  escreva(i);
}
```
* **Gramática EBNF**: `para ::= "para" IDENT "=" expressao "ate" expressao [ "passo" expressao ] comando ;`
* **Semântica**: A variável de controle, a expressão inicial, o limite e o passo devem ser obrigatoriamente do tipo `inteiro`. Passo estático igual a zero é rejeitado como erro semântico.

### 2. Comando `repita ... até` (Laço com Pós-Condição)
```pascal
repita {
  leia(num);
} ate num > 0;
```
* **Gramática EBNF**: `repita ::= "repita" { comando } "ate" expressao ";" ;`
* **Semântica**: O corpo é executado ao menos uma vez e a condição pós-teste deve ser do tipo `booleano`.

---

## 🛠️ Stack Tecnológica & Declaração de Ferramentas (Seção 8 do Edital)

* **Linguagem Principal**: **Python 3.10+** puro (sem dependências externas).
* **Abordagem de Parsing**: **Descendente Recursivo Manual (LL(1))**, sem uso de geradores automáticos de analisadores (ANTLR, Flex/Bison ou PLY) para assegurar total domínio acadêmico sobre os autômatos.
* **Padrões de Projeto**: Padrão **Visitor** adotado em [`minilang/arvore.py`](minilang/arvore.py) para navegação na AST, anotação de tipos semânticos e suporte ao interpretador do M4.
* **Declaração de Uso de IA Generativa**: Conforme a Seção 8 do edital, o uso de ferramentas de IA generativa (Claude Code / Anthropic Claude Opus) nas fases do projeto está formalmente declarado e detalhado nas notas técnicas de entrega ([`docs/nota_M1.md`](docs/nota_M1.md), [`docs/nota_M2.md`](docs/nota_M2.md) e [`docs/nota_M3.md`](docs/nota_M3.md)). Todos os integrantes dominam a base de código e estão capacitados para explicar qualquer trecho na arguição oral.

---

## 📂 Arquitetura de Diretórios do Projeto

```text
theMiniLang/
├── minilang/                     # Núcleo do Compilador MiniLang
│   ├── __init__.py
│   ├── __main__.py               # Ponto de entrada para execução via módulo
│   ├── tokens.py                 # [M1] Categorias de tokens e palavras reservadas
│   ├── lexer.py                  # [M1] Analisador Léxico (Scanner / AFD manual)
│   ├── arvore.py                 # [M2] Nós da AST, formatador e padrão Visitor
│   ├── parser.py                 # [M2] Parser Descendente Recursivo LL(1)
│   ├── simbolos.py               # [M3] Tabela de Símbolos e pilha de escopos
│   ├── semantico.py              # [M3] Analisador Semântico e checagem de tipos
│   ├── errors.py                 # Classes canônicas de erro ([FASE] Linha L, Coluna C)
│   └── cli.py                    # Interface unificada de linha de comando
├── tests/                        # Bateria de Testes Unitários Automatizados
│   ├── test_lexer.py             # 12 testes léxicos (M1)
│   ├── test_parser.py            # 36 testes sintáticos e AST (M2)
│   └── test_semantico.py         # 36 testes semânticos e tipos (M3)
├── exemplos/                     # Programas MiniLang Válidos e Inválidos
│   ├── validos/                  # Fatorial, laços aninhados, expressões, dangling else
│   └── invalidos/                # Erros léxicos, sintáticos e semânticos provocados
├── docs/                         # Documentação Acadêmica Completa
│   ├── afd.md                    # [M1] Especificação formal do AFD e Mermaid
│   ├── gramatica.md              # [M2] Gramática EBNF e análise LL(1)
│   ├── semantica.md              # [M3] Regras semânticas, tipos e inicialização
│   ├── fixes/                    # Guias de correção e alinhamento da equipe
│   │   ├── README.md             # Índice dos fixes para a equipe
│   │   ├── FIX_01_PARSER_MULTIPLOS_VAR.md
│   │   ├── FIX_02_TABELA_SIMBOLOS_ESCOPO_GLOBAL.md
│   │   ├── FIX_03_LEXER_IDENTIFICADORES_E_NUMEROS.md
│   │   └── FIX_04_PADRONIZACAO_EXTENSAO_ML.md
│   ├── nota_M1.md                # Relatório formal de entrega do Marco 1
│   ├── nota_M2.md                # Relatório formal de entrega do Marco 2
│   └── nota_M3.md                # Relatório formal de entrega do Marco 3
├── CONTRIBUTING.md               # Registro oficial dos 6 integrantes e regras de Git
├── README.md                     # Documentação central do projeto
└── minilang.py                   # Ponto de entrada CLI na raiz (linha única)
```

---

## 👥 Registro Oficial da Equipe & Governança

Para consultar as diretrizes de versionamento e a governança do repositório, acesse o [`CONTRIBUTING.md`](./CONTRIBUTING.md):

| # | Integrante | Matrícula / RA | GitHub |
| :-: | :--- | :---: | :---: |
| 1 | **João Spinola Falcão** | `12723116405` | [`@Falc01`](https://github.com/Falc01) |
| 2 | **Pedro Adaime Ribeiro** | `12723119338` | [`@pedrobelane`](https://github.com/pedrobelane) |
| 3 | **Isabelle Maciel dos Santos** | `12723118051` | [`@isabellesmaciel`](https://github.com/isabellesmaciel) |
| 4 | **Kawan Oliveira Carneiro** | `12724119606` | [`@kawoliv`](https://github.com/kawoliv) |
| 5 | **João Guilherme Perrone Hohlenwerger** | `1272328057` | [`@joaohohlenwerger`](https://github.com/joaohohlenwerger) |
| 6 | **Daniel Costa Santos** | `1272323654` | [`@Danncss`](https://github.com/Danncss) |

---

## 📚 Referências Bibliográficas

* AHO, Alfred V. et al. **Compiladores: princípios, técnicas e ferramentas**. 2. ed. Pearson Addison Wesley, 2008.
* MENEZES, Paulo Blauth. **Linguagens formais e autômatos**. 6. ed. Bookman, 2011.
* SANTOS, Pedro Reis; LANGLOIS, Thibault. **Compiladores: da teoria à prática**. LTC, 2018.
* UNIFACS. **Plano de Ensino 2026.2 — Teoria da Computação e Compiladores (0006964)**.
* SANTANA, Daniel. **Projeto A3 MiniLang — Compilador da MiniLang**. UNIFACS, 2026.
