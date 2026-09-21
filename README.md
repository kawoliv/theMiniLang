# MiniLang

Compilador da linguagem **MiniLang**, desenvolvido para a A3 de Teoria da Computação e Compiladores (UNIFACS 2026.2).

- **Linguagem de implementação:** Python 3 (sem bibliotecas externas)
- **Abordagem:** implementação manual (sem geradores de analisadores)
- **Extensão escolhida:** D — comandos `para` e `repita/ate`
- **Back-end:** geração de código de três endereços

## Marcos

| Marco | Conteúdo | Status |
|---|---|---|
| M1 | Analisador léxico | em desenvolvimento |
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

- Python 3.10 ou superior
