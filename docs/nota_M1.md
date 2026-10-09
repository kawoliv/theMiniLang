# Nota do Marco M1 — Analisador Léxico

**Projeto:** Compilador MiniLang  
**Disciplina:** Teoria da Computação e Compiladores (UNIFACS 2026.2)  
**Marco:** M1 — Analisador Léxico (Scanner)  
**Extensão Escolhida:** D (`para`, `passo`, `ate`/`até`, `repita`)  
**Data:** Outubro de 2026  

**Equipe de Desenvolvimento:**
- Kawan Oliveira (`@kawoliv`)
- João Guilherme Perrone Hohlenwerger (`@joaohohlenwerger`)
- Daniel Costa (`@Danncss`)
- João Spinola Falcão (RA: `12723116405` | `@Falc01`)
- Pedro Adaime Ribeiro (RA: `12723119338` | `@pedrobelane`)
- Isabelle Maciel dos Santos (RA: `12723118051` | `@isabellesmaciel`)

---

## 1. Visão Geral e Escopo

O Marco M1 contemplou o desenvolvimento completo e autônomo do analisador léxico da linguagem **MiniLang**, implementado manualmente em Python 3 sem o auxílio de bibliotecas externas ou geradores automáticos de analisadores (como Lex ou Flex).

O módulo léxico é responsável por transformar o fluxo linear de caracteres do código-fonte em uma sequência de tokens tipados e localizados, descartando comentários e espaços irrelevantes e registrando erros léxicos sem abortar a leitura prematuramente.

## 2. Decisões de Projeto e Arquitetura

- **Implementação Manual Baseada em AFD:** O autômato finito determinístico opera através de métodos de varredura direta (`_peek`, `_avancar`), inspecionando prefixos e consumindo caracteres de forma eficiente com complexidade de tempo $O(N)$ relativo ao tamanho do código-fonte.
- **Rastreamento de Posição & Atributo Semântico:** Cada token armazena o número exato da linha e coluna de seu primeiro caractere (`linha`, `coluna`) e o valor de atributo computado (`valor`, ex.: `int` para inteiros e `bool` para booleanos), preparando a base canônica para a AST (M2) e a verificação de tipos (M3).
- **Tratamento e Recuperação de Erros Padronizados:** Caracteres inesperados (como `@`, `$`, ou exclamação solta `!` não seguida de `=`) não interrompem imediatamente a tokenização. O analisador registra o erro no padrão oficial exigido pela minuta: `[LÉXICO] Linha L, Coluna C: Descrição`, prosseguindo a análise para identificar possíveis erros adicionais ao longo do arquivo.
- **Suporte a Palavras-Chave e Extensão D:** A categorização entre identificadores gerais e palavras reservadas é feita através de consulta em tabela hash (`PALAVRAS_RESERVADAS`), cobrindo as palavras da linguagem base e os comandos da Extensão D (`para`, `passo`, `ate`/`até`, `repita`), aceitando ainda variações acentuadas (`não`/`nao`, `senão`/`senao`, `até`/`ate`).

## 3. Estrutura de Arquivos e Código

- `minilang.py`: Ponto de entrada CLI principal na raiz com suporte a flags de todos os marcos (`--tokens`, `--ast`, `--symbols`, `--optimize`).
- `minilang/tokens.py`: Enumeração `TokenType`, classe `Token` com atributos de valor e mapeamento de palavras reservadas.
- `minilang/lexer.py`: Classe `Lexer` implementando o autômato finito determinístico e a lógica de tokenização.
- `minilang/errors.py`: Definição da exceção `LexicalError` formatada no padrão oficial `[LÉXICO]`.
- `minilang/__main__.py`: Interface de linha de comando alternativa via módulo (`python -m minilang`).
- `docs/afd.md`: Documentação formal do AFD contendo as expressões regulares, diagrama Mermaid e tabela de transições.
- `tests/test_lexer.py`: Suíte de testes unitários automatizados com `unittest` (12 testes).
- `exemplos/`: Programas de teste válidos e programas com erros léxicos intencionais.

## 4. Testes e Validação

A implementação foi submetida a baterias de testes automatizados e manuais cobrindo:
1. **Palavras reservadas da base e da Extensão D:** Validação de todos os termos-chave (incluindo variações acentuadas `até`, `senão`, `não`).
2. **Identificadores e literais inteiros:** Diferenciação correta de nomes de variáveis, dígitos e nomes iniciados por `_`, com cálculo de valor nativo.
3. **Operadores compostos e de um caractere:** Reconhecimento exato de `==`, `!=`, `<=`, `>=`, `=`, etc.
4. **Descarte de comentários e espaços:** Linhas comentadas com `#` e diferentes combinações de espaços/quebras de linha.
5. **Detecção e formatação de erros:** Padrão `[LÉXICO] Linha L, Coluna C:` para caracteres inválidos e operadores malformados (`!`).

Todos os 12 testes automatizados foram executados via `python -m unittest discover -s tests -v` com 100% de sucesso.

---

## 5. Declaração de Uso de Ferramentas de Inteligência Artificial (IA)

Em conformidade com as diretrizes acadêmicas e de integridade do projeto:

- **Ferramentas utilizadas:** Google Antigravity / Gemini CLI Assistant.
- **Natureza do uso:** 
  - Auxílio na estruturação inicial dos esqueletos dos módulos e diagramação formal em Mermaid;
  - Apoio na elaboração de casos de testes unitários para cobertura de cenários de borda no analisador léxico;
  - Revisão e padronização da formatação das documentações do projeto.
- **Autoria e Validação:** Toda a lógica do autômato, a tabela de transições e as regras léxicas foram revisadas, testadas e validadas pela equipe do projeto, garantindo conformidade com a especificação da gramática da MiniLang e independência de bibliotecas externas.
