# 📌 Índice dos Guias de Fix e Roteiro da MiniLang

Este diretório reúne as instruções passo a passo para corrigir os bugs encontrados na auditoria e preparar a equipe para o Marco 4 e a arguição oral com o Prof. Daniel Santana:

| Arquivo | Descrição | Módulo | Severidade |
| :--- | :--- | :--- | :--- |
| [`FIX_01_PARSER_MULTIPLOS_VAR.md`](FIX_01_PARSER_MULTIPLOS_VAR.md) | Permite múltiplas linhas e blocos com `var` (corrige exemplo oficial do edital) | `minilang/parser.py` | 🔴 Alta |
| [`FIX_02_TABELA_SIMBOLOS_ESCOPO_GLOBAL.md`](FIX_02_TABELA_SIMBOLOS_ESCOPO_GLOBAL.md) | Mantém escopo global ativo para o Back-End / Interpretador | `minilang/semantico.py` | 🔴 Alta |
| [`FIX_03_LEXER_IDENTIFICADORES_E_NUMEROS.md`](FIX_03_LEXER_IDENTIFICADORES_E_NUMEROS.md) | Rejeita identificador iniciado por `_` e tokens colados `123abc` | `minilang/lexer.py` | 🟡 Média |
| [`FIX_04_PADRONIZACAO_EXTENSAO_ML.md`](FIX_04_PADRONIZACAO_EXTENSAO_ML.md) | Padroniza exemplos com extensão `.ml` conforme o edital | `exemplos/` e `README.md` | 🟢 Baixa |
| [`FIX_05_ROTEIRO_MARCO_4_BACKEND.md`](FIX_05_ROTEIRO_MARCO_4_BACKEND.md) | Planejamento completo do M4 (Interpretador, Constant Folding, Relatório e Arguição) | `minilang/` e Docs | 🚀 Estratégico |
