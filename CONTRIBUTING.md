# Guia de Contribuição e Alocação da Equipe - MiniLang

Este documento estabelece a alocação de tarefas, responsabilidades e as diretrizes de desenvolvimento da equipe para a construção do compilador da **MiniLang** (Avaliação A3 de Teoria da Computação e Compiladores — UNIFACS 2026.2).

Como o professor exige acompanhamento contínuo de processo e histórico de versionamento, adotamos um fluxo de trabalho colaborativo, transparente e com divisão de escopo bem delineada para assegurar o domínio individual de cada integrante na apresentação final.

---

## 👥 Quadro Geral de Integrantes da Equipe

| Integrante | RA | GitHub | Foco Principal / Marcos |
| :--- | :---: | :---: | :--- |
| **João Spinola Falcão** | `12723116405` | `@Falc01` | Marco 1 (Léxico) & Marco 4 (Back-End / Integração) |
| **Pedro Adaime Ribeiro** | `12723119338` | `@pedrobelane` | Marco 3 (Analisador Semântico & Tabela de Símbolos) |
| *[Integrante 3 - A Definir]* | `—` | `@` | Marco 2 (Analisador Sintático & AST) |
| *[Integrante 4 - A Definir]* | `—` | `@` | Suporte M1/M2 & Testes de Integração |
| *[Integrante 5 - A Definir]* | `—` | `@` | Suporte M3/M4 & Otimização de Código |

---

## 📋 Alocação de Tarefas por Marco Avaliativo

Abaixo está a divisão de tarefas baseada no planejamento técnico dos quatro marcos cumulativos da MiniLang:

### 1. 🔍 Analisador Léxico & Autômatos (Marco 1)
* **Foco e Responsabilidades:**
  * Implementar o scanner manual da linguagem no módulo `minilang/lexer.py` e `minilang/tokens.py`.
  * Mapear e reconhecer todas as palavras reservadas da base e da Extensão Opção D (`para`, `repita`, `até`/`ate`, `passo`), literais inteiros/booleanos, delimitadores e operadores.
  * Implementar o tratamento de *lookahead* de 1 caractere para operadores relacionais e atribuição (`=`, `==`, `<`, `<=`, `>`, `>=`, `!=`).
  * Descartar comentários de linha única iniciados por `#` e caracteres de espaço em branco (`\t`, `\r`, ` `).
  * Rastrear estritamente o número de **linha** e **coluna** de cada token processado e emitir mensagens de erro léxico no padrão oficial `[LÉXICO] Linha L, Coluna C: Descrição`.
  * Especificar e documentar formalmente o Autômato Finito Determinístico (AFD) com diagrama de estados e tabela de transições (`docs/afd.md`).
  * Criar a bateria de testes automatizados unitários em `tests/test_lexer.py` e programas de exemplo em `exemplos/`.
* **Arquivos e Diretórios:** `minilang/lexer.py`, `minilang/tokens.py`, `minilang/errors.py`, `tests/`, `exemplos/`, `docs/afd.md`, `docs/nota_M1.md`.
* **Responsáveis:**
  * 👤 **João Spinola Falcão** (RA: `12723116405` | GitHub: `@Falc01`)
  * 👤 *`[Integrante 4 - A Definir]`*

---

### 2. 🌲 Analisador Sintático & AST (Marco 2)
* **Foco e Responsabilidades:**
  * Formalizar a Gramática Livre de Contexto (GLC) da MiniLang em notação EBNF.
  * Implementar o analisador sintático preditivo descendente recursivo (*Recursive Descent Parser*).
  * Modelar e instanciar os nós da Árvore Sintática Abstrata (AST) estruturada e navegável.
  * Implementar o mecanismo de recuperação de erros em **Modo Pânico** (sincronização por tokens de parada como `;`, `}`, `fim`) para permitir a identificação de múltiplos erros sintáticos em uma única execução.
  * Garantir a correta precedência e associatividade de operadores aritméticos, relacionais e lógicos.
  * Identificar, resolver e documentar a ambiguidade clássica do *dangling else* (senão pendente).
* **Arquivos e Diretórios:** `minilang/parser/`, `tests/`, `exemplos/`, `docs/M2_SINTATICO.md`.
* **Responsáveis:**
  * 👤 *`[Integrante 3 - A Definir]`*
  * 👤 *`[Integrante 4 - A Definir]`*

---

### 3. 🛡️ Analisador Semântico & Tabela de Símbolos (Marco 3)
* **Foco e Responsabilidades:**
  * Implementar a estrutura de dados da Tabela de Símbolos, suportando escopos estáticos aninhados (global e blocos locais).
  * Registrar metadados essenciais de cada símbolo: identificador, tipo (`inteiro`, `booleano`), escopo e posição (linha/coluna) da declaração.
  * Implementar o verificador de tipos (*Type Checker*), validando regras de atribuição, operações aritméticas/lógicas e condições de comandos de controle (`se`, `enquanto`).
  * Identificar e emitir erros semânticos precisos: variável não declarada, redeclaração no mesmo escopo, incompatibilidade de tipo e `leia` em identificadores não declarados no padrão `[SEMÂNTICO] Linha L, Coluna C: Descrição`.
  * Anotar os nós da AST com seus respectivos tipos inferidos.
  * Implementar o bônus avaliativo (+0,5 pt): detecção em tempo de compilação de variáveis lidas antes de serem inicializadas.
* **Arquivos e Diretórios:** `minilang/semantic/`, `tests/`, `docs/M3_SEMANTICO.md`.
* **Responsáveis:**
  * 👤 **Pedro Adaime Ribeiro** (RA: `12723119338` | GitHub: `@pedrobelane`)
  * 👤 *`[Integrante 5 - A Definir]`*

---

### 4. ⚙️ Back-End, Otimização e Apresentação (Marco 4)
* **Foco e Responsabilidades:**
  * Implementar o interpretador direto da AST (*Tree-walking Interpreter*) via padrão *Visitor* ou gerador de Código de Três Endereços (TAC).
  * Implementar a extensão obrigatória do edital (Opção D: comandos `para` e `repita ... até` via desaçucaramento sintático na própria AST).
  * Desenvolver e demonstrar ao menos uma técnica de otimização de código (*Constant Folding* / propagação estática de constantes), exibindo métricas de "antes e depois".
  * Integrar o pipeline completo no comando unificado `minilang.py`.
  * Redigir o Relatório Técnico acadêmico final de 6 a 10 páginas (decisões, gramática, AFD, ferramentas e uso de IA).
  * Preparar a apresentação de 15 minutos com demonstração prática ao vivo e treinamento mútuo para a arguição individual.
* **Arquivos e Diretórios:** `minilang/backend/`, `minilang.py`, `docs/relatorio_final.pdf`.
* **Responsáveis:**
  * 👥 **Toda a Equipe** (João Spinola Falcão, Pedro Adaime Ribeiro e Integrantes 3, 4 e 5 em conjunto)

---

## 🌿 Diretrizes de Git & Versionamento

Para garantir transparência, histórico contínuo e nota máxima no critério de processo da A3:

### 1. Fluxo Simplificado de Versionamento (Branch Única: `main`)
Para maximizar a agilidade da equipe e evitar atritos de mesclagem complexos, todo o desenvolvimento é centralizado diretamente na branch principal (`main`):
* **Protocolo Pré-Push Obrigatório**: Antes de qualquer `git push`, execute obrigatoriamente `git pull origin main` para integrar eventuais commits recentes dos seus colegas de equipe.
* **Commits Atômicos & Individuais**: Cada membro commita diretamente a partir de seu usuário Git configurado, registrando a autoria de cada marco de forma incremental.

### 2. Padrão de Commits Semânticos (PT-BR)
Todos os commits devem ser frequentes, atômicos e redigidos em português com os prefixos:
* `feat:` Nova funcionalidade (ex: `feat: implementa scanner com lookahead para relacionais`).
* `fix:` Correção de bug (ex: `fix: corrige contagem de coluna ao pular comentarios com hashtag`).
* `test:` Adição/atualização de casos de teste (ex: `test: adiciona programas com erros lexicos`).
* `docs:` Documentação e diagramas (ex: `docs: adiciona tabela de transicoes de estados do AFD`).
* `refactor:` Melhoria de código sem alterar regra de negócio.

### 3. Padrão Obrigatório de Mensagens de Erro
Todas as fases do compilador devem emitir mensagens formatadas no padrão do edital:
```text
[FASE] Linha L, Coluna C: Descrição objetiva do erro.
```
*Exemplos:*
* `[LÉXICO] Linha 5, Coluna 12: Caractere inválido '@' não reconhecido.`
* `[SINTÁTICO] Linha 14, Coluna 8: Era esperado ';' após o comando, mas foi encontrado 'fim'.`
* `[SEMÂNTICO] Linha 22, Coluna 4: Variável 'total' não declarada neste escopo.`

---

## 🔍 Revisão e Preparação para Arguição Oral

Lembre-se: no Marco 4, o professor realizará perguntas individuais sobre qualquer parte do código. Para proteger a nota de todos:
1. Faça leitura e *Code Review* das alterações dos colegas conforme o código for integrado na `main`.
2. Realize reuniões rápidas de alinhamento para que cada desenvolvedor demonstre como sua fase foi implementada.
