# Nota do Marco M1 — Analisador Léxico

**Projeto:** Compilador MiniLang  
**Disciplina:** Teoria da Computação e Compiladores (UNIFACS 2026.2)  
**Marco:** M1 — Analisador Léxico (Scanner)  
**Extensão Escolhida:** D (`para`, `passo`, `ate`, `repita`)  
**Data:** Outubro de 2026  

---

## 1. Visão Geral e Escopo

O Marco M1 contemplou o desenvolvimento completo e autônomo do analisador léxico da linguagem **MiniLang**, implementado manualmente em Python 3 sem o auxílio de bibliotecas externas ou geradores automáticos de analisadores (como Lex ou Flex).

O módulo léxico é responsável por transformar o fluxo linear de caracteres do código-fonte em uma sequência de tokens tipados e localizados, descartando comentários e espaços irrelevantes e registrando erros léxicos sem abortar a leitura prematuramente.

## 2. Decisões de Projeto e Arquitetura

- **Implementação Manual Baseada em AFD:** O autômato finito determinístico opera através de métodos de varredura direta (`_peek`, `_avancar`), inspecionando prefixos e consumindo caracteres de forma eficiente com complexidade de tempo $O(N)$ relativo ao tamanho do código-fonte.
- **Rastreamento de Posição:** Cada token armazena o número exato da linha e coluna de seu primeiro caractere (`linha`, `coluna`), proporcionando mensagens de diagnóstico precisas tanto para o programador quanto para os módulos subsequentes (sintático e semântico).
- **Tratamento e Recuperação de Erros:** Caracteres inesperados (como `@`, `$`, ou exclamação solta `!` não seguida de `=`) não interrompem imediatamente a tokenização. O analisador registra o erro léxico em uma lista interna acompanhado de sua localização precisa e prossegue a análise para identificar possíveis erros adicionais ao longo do arquivo.
- **Suporte a Palavras-Chave e Extensão D:** A categorização entre identificadores gerais e palavras reservadas é feita através de consulta em tabela hash (`PALAVRAS_RESERVADAS`), cobrindo as palavras da linguagem base e os comandos da Extensão D (`para`, `passo`, `ate`, `repita`), aceitando ainda variações acentuadas (`não`/`nao`, `senão`/`senao`).

## 3. Estrutura de Arquivos e Código

- `minilang/tokens.py`: Enumeração `TokenType`, classe `Token` e mapeamento de palavras reservadas.
- `minilang/lexer.py`: Classe `Lexer` implementando o autômato finito determinístico e a lógica de tokenização.
- `minilang/errors.py`: Definição da exceção `LexicalError`.
- `minilang/__main__.py`: Interface de linha de comando (CLI) que recebe arquivos `.mlg` e a flag opcional `--tokens`.
- `docs/afd.md`: Documentação formal do AFD contendo as expressões regulares, diagrama Mermaid e tabela de transições.
- `tests/test_lexer.py`: Suíte de testes unitários automatizados com `unittest`.
- `exemplos/`: Programas de teste válidos e programas com erros léxicos intencionais.

## 4. Testes e Validação

A implementação foi submetida a baterias de testes automatizados e manuais cobrindo:
1. **Palavras reservadas da base e da Extensão D:** Validação de todos os termos-chave.
2. **Identificadores e literais inteiros:** Diferenciação correta de nomes de variáveis, dígitos e nomes iniciados por `_`.
3. **Operadores compostos e de um caractere:** Reconhecimento exato de `==`, `!=`, `<=`, `>=`, `=`, etc.
4. **Descarte de comentários e espaços:** Linhas comentadas com `#` e diferentes combinações de espaços/quebras de linha.
5. **Detecção precisa de erros:** Caracteres inválidos e operadores malformados (`!`).

Todos os 9 testes automatizados foram executados via `python -m unittest discover -s tests -v` com 100% de sucesso.

---

## 5. Declaração de Uso de Ferramentas de Inteligência Artificial (IA)

Em conformidade com as diretrizes acadêmicas e de integridade do projeto:

- **Ferramentas utilizadas:** Google Antigravity / Gemini CLI Assistant.
- **Natureza do uso:** 
  - Auxílio na estruturação inicial dos esqueletos dos módulos e diagramação formal em Mermaid;
  - Apoio na elaboração de casos de testes unitários para cobertura de cenários de borda no analisador léxico;
  - Revisão e padronização da formatação das documentações do projeto.
- **Autoria e Validação:** Toda a lógica do autômato, a tabela de transições e as regras léxicas foram revisadas, testadas e validadas pela equipe do projeto, garantindo conformidade com a especificação da gramática da MiniLang e independência de bibliotecas externas.
