# MiniLang

Compilador da linguagem **MiniLang**, desenvolvido para a A3 de Teoria da Computação e Compiladores (UNIFACS 2026.2).

- **Linguagem de implementação:** Python 3 (sem bibliotecas externas)
- **Abordagem:** implementação manual (sem geradores de analisadores)
- **Extensão escolhida:** D — comandos `para` e `repita/ate`
- **Back-end:** geração de código de três endereços

## Marcos

| Marco | Conteúdo | Status |
|---|---|---|
| M1 | Analisador léxico | concluído |
| M2 | Analisador sintático + AST | concluído |
| M3 | Analisador semântico | concluído |
| M4 | Back-end, otimização e relatório | — |

## Estrutura

```
minilang/    código-fonte do compilador
tests/       testes automatizados
exemplos/    programas MiniLang válidos e inválidos
docs/        documentação (AFD, gramática, semântica, notas de marco)
```

## Requisitos

- Python 3.10 ou superior (sem dependências externas)

## Como Executar o Compilador (CLI)

O compilador MiniLang oferece execução direta via script unificado na raiz (`minilang.py`) e também via módulo (`minilang`):

### 1. Execução direta (Padrão Oficial do Edital)

```bash
# Exibir a tabela detalhada de tokens (Marco 1)
python minilang.py exemplos/validos/fatorial.mlg --tokens

# Validar programas com a Extensão D
python minilang.py exemplos/validos/exemplo_para.mlg --tokens
python minilang.py exemplos/validos/exemplo_repita.mlg --tokens

# Testar detecção de erros com posição precisa [LÉXICO] Linha L, Coluna C
python minilang.py exemplos/invalidos/caractere_invalido.mlg

# Exibir a Árvore Sintática Abstrata (Marco 2)
python minilang.py exemplos/validos/fatorial.mlg --ast
python minilang.py exemplos/validos/dangling_else.mlg --ast

# Erros sintáticos com recuperação: vários erros [SINTÁTICO] em uma execução
python minilang.py exemplos/invalidos/sintatico_multiplos_erros.mlg

# Tabela de símbolos e AST anotada com tipos (Marco 3)
python minilang.py exemplos/validos/fatorial.mlg --symbols --ast

# Erros semânticos [SEMÂNTICO] e avisos (variável não inicializada / não usada)
python minilang.py exemplos/invalidos/semantico_tipos.mlg
python minilang.py exemplos/validos/avisos_inicializacao.mlg
```

Sem opções, o compilador roda as fases implementadas (léxica, sintática e semântica) e informa
sucesso (código de saída 0) ou lista todos os erros encontrados (código de saída 1). Avisos são
exibidos, mas não impedem a compilação.

### 2. Execução alternativa via módulo Python

```bash
python -m minilang exemplos/validos/fatorial.mlg --ast
```

> **Dica (Windows):** Você também pode substituir `python` por `py`. Suporta extensões `.mlg` e `.ml`.

## Execução dos Testes Automatizados

Para rodar todos os testes unitários da suíte de testes com relatório detalhado:

```bash
python -m unittest discover -s tests -v
```

## Documentação do Marco M1

- [docs/afd.md](docs/afd.md): Especificação formal das Expressões Regulares, Diagrama Mermaid e Tabela de Transições do AFD.
- [docs/nota_M1.md](docs/nota_M1.md): Nota descritiva do Marco M1 contendo decisões de projeto, estrutura, testes e declaração de uso de IA.

## Documentação do Marco M2

- [docs/gramatica.md](docs/gramatica.md): Gramática EBNF, classificação na Hierarquia de Chomsky, precedência e associatividade, *dangling else*, nós da AST e estratégia de recuperação de erros.
- [docs/nota_M2.md](docs/nota_M2.md): Nota do Marco M2 com decisões de projeto, testes, limitações e declaração de uso de IA.

## Documentação do Marco M3

- [docs/semantica.md](docs/semantica.md): Tabela de símbolos, sistema de tipos, regras dos comandos, erros e avisos detectados, análise de inicialização e anotação da AST.
- [docs/nota_M3.md](docs/nota_M3.md): Nota do Marco M3 com cobertura da rubrica, decisões de projeto, limitações e declaração de uso de IA.
