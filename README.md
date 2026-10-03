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

O analisador léxico da MiniLang pode ser executado diretamente via terminal utilizando o módulo Python `minilang`:

### Sintaxe básica

```bash
python -m minilang <caminho_do_arquivo.mlg> [--tokens]
```

> **Dica (Windows):** Você também pode utilizar o executável `py`:
> ```cmd
> py -m minilang <caminho_do_arquivo.mlg> [--tokens]
> ```

### Exemplos de uso

1. **Exibir a lista de tokens reconhecidos:**
   ```bash
   python -m minilang exemplos/validos/fatorial.mlg --tokens
   ```
   *Saída formatada contendo `LINHA:COLUNA  TIPO_TOKEN  'LEXEMA'`.*

2. **Validar programa com suporte à Extensão D (`para`, `repita/ate`):**
   ```bash
   python -m minilang exemplos/validos/exemplo_para.mlg --tokens
   python -m minilang exemplos/validos/exemplo_repita.mlg --tokens
   ```

3. **Verificar detecção e tratamento de erros léxicos:**
   ```bash
   python -m minilang exemplos/invalidos/caractere_invalido.mlg --tokens
   ```
   *Exibirá as mensagens de erro detalhadas com linha e coluna exatas.*

## Execução dos Testes Automatizados

Para rodar todos os testes unitários da suíte de testes com relatório detalhado:

```bash
python -m unittest discover -s tests -v
```

## Documentação do Marco M1

- [docs/afd.md](docs/afd.md): Especificação formal das Expressões Regulares, Diagrama Mermaid e Tabela de Transições do AFD.
- [docs/nota_M1.md](docs/nota_M1.md): Nota descritiva do Marco M1 contendo decisões de projeto, estrutura, testes e declaração de uso de IA.
