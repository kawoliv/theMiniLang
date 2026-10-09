# Registro da Equipe e Guia de Contribuição — MiniLang

Este documento formaliza o registro da equipe e estabelece as diretrizes de desenvolvimento, versionamento e colaboração para a construção do compilador da **MiniLang** (Avaliação A3 da disciplina de Teoria da Computação e Compiladores — UNIFACS 2026.2).

O projeto é desenvolvido de forma cumulativa e colaborativa ao longo do semestre, com corresponsabilidade de todos os integrantes sobre as etapas do pipeline de compilação e preparação conjunta para a apresentação e arguição oral final.

---

## 👥 Registro Oficial da Equipe (6 Integrantes)

| # | Integrante | Matrícula / RA | GitHub |
| :-: | :--- | :---: | :---: |
| 1 | **João Spinola Falcão** | `12723116405` | [`@Falc01`](https://github.com/Falc01) |
| 2 | **Pedro Adaime Ribeiro** | `12723119338` | [`@pedrobelane`](https://github.com/pedrobelane) |
| 3 | **Isabelle Maciel** | `—` | `—` |
| 4 | **Kawan Oliveira** | `—` | [`@kawoliv`](https://github.com/kawoliv) |
| 5 | **João Guilherme Perrone Hohlenwerger** | `—` | [`@joaohohlenwerger`](https://github.com/joaohohlenwerger) |
| 6 | **Daniel Costa** | `—` | [`@Danncss`](https://github.com/Danncss) |

> *Nota: Os integrantes podem preencher e atualizar seus respectivos RAs e links de perfil diretamente nesta tabela.*

---

## 🤝 Modelo de Trabalho e Responsabilidade Coletiva

1. **Domínio Compartilhado do Código**:
   - Toda a equipe compartilha a responsabilidade sobre o compilador completo (M1 Léxico, M2 Sintático/AST, M3 Semântico e M4 Back-End/Otimização).
   - O desenvolvimento não é isolado por pessoa: todos participam da implementação, revisão de código (*code review*) e escrita de testes para garantir que todos dominem o projeto integralmente na arguição oral individual de 15 minutos com o professor.

2. **Acompanhamento Contínuo de Processo**:
   - Conforme exigido pelo edital (Seção 7), o histórico de commits do repositório é avaliado como evidência contínua de trabalho em equipe.
   - Commits devem ser regulares e distribuídos ao longo das semanas, evitando alterações volumosas de última hora.

---

## 🌿 Diretrizes de Git & Versionamento

Para assegurar transparência e organização no repositório:

### 1. Fluxo de Trabalho (Branch Principal: `main`)
* **Protocolo Pré-Push**: Antes de qualquer `git push`, execute sempre `git pull origin main` para sincronizar as contribuições recentes da equipe.
* **Commits Frequentes e Atômicos**: Commits devem refletir pequenas entregas bem testadas.

### 2. Padrão de Commits Semânticos (PT-BR)
Mensagens de commit devem ser redigidas em português e seguir o padrão convencional:
* `feat:` Nova funcionalidade no compilador (ex.: `feat(parser): implementa reconhecimento de comandos se/senao`).
* `fix:` Correção de bug ou ajuste de comportamento (ex.: `fix(lexer): ajusta lookahead em operadores relacionais`).
* `test:` Adição ou atualização de casos de teste (ex.: `test: adiciona programas validos e invalidos para M2`).
* `docs:` Melhorias na documentação, gramática ou notas de marco (ex.: `docs: atualiza especificacao da AST`).
* `refactor:` Reorganização de código sem alteração no comportamento externo.

### 3. Padrão Obrigatório de Mensagens de Erro
Todas as fases do compilador devem emitir mensagens formatadas no padrão canônico do edital:
```text
[FASE] Linha L, Coluna C: Descrição objetiva do erro.
```
*Exemplos:*
* `[LÉXICO] Linha 5, Coluna 12: Caractere inesperado '@'.`
* `[SINTÁTICO] Linha 14, Coluna 8: Era esperado ';' após o comando, mas foi encontrado 'fim'.`
* `[SEMÂNTICO] Linha 22, Coluna 4: Variável 'total' não declarada neste escopo.`

---

## 🔍 Preparação para a Arguição Oral (Seção 10 do Edital)

A avaliação final conta com uma arguição oral de 15 minutos com o professor Daniel Santana, onde perguntas técnicas individuais serão realizadas sobre qualquer módulo do compilador:
1. Realizar alinhamentos breves da equipe após a conclusão de cada marco para demonstrar a solução implementada;
2. Garantir que cada membro seja capaz de navegar na base de código, executar os testes e explicar as decisões teóricas (AFD, gramática EBNF, tabela de símbolos e geração de código intermediário).
