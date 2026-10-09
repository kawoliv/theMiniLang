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
| M2 | Analisador sintático + AST | — |
| M3 | Analisador semântico | — |
| M4 | Back-end, otimização e relatório | — |

## Estrutura

```
minilang/    código-fonte do compilador
tests/       testes automatizados
exemplos/    programas MiniLang válidos e inválidos
docs/        documentação (AFD, notas de marco)
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
```

### 2. Execução alternativa via módulo Python

```bash
python -m minilang exemplos/validos/fatorial.mlg --tokens
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
