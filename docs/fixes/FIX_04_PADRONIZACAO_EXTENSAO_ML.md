# 🛠️ Fix 04: Padronização da Extensão de Arquivos para `.ml`

**Módulo:** Pasta `exemplos/`, `README.md` e `minilang/cli.py`  
**Severidade:** 🟢 Baixa / Organizacional (Conformidade com a Seção 11 do Edital)  
**Responsável Sugerido:** Integrante responsável por Documentação e CLI  

---

## 1. O Problema

O edital oficial da disciplina (Prof. Daniel Santana, UNIFACS 2026.2) especifica repetidamente:
> *"Exemplo de Código MiniLang Válido (`.ml`)"*  
> *"Linha de comando documentada no README: `python minilang.py tests/valid/exemplo_basico.ml`"*

No entanto, no repositório `theMiniLang`, todos os exemplos foram salvos com a extensão `.mlg` (ex: `fatorial.mlg`, `expressoes.mlg`).

Embora o compilador aceite qualquer arquivo fornecido por parâmetro, é uma boa prática e evita ruído com o professor manter os arquivos com a extensão `.ml` conforme o checklist oficial.

---

## 2. Ações Práticas

1. **Criar ou renomear arquivos de exemplo na pasta `exemplos/validos/` e `exemplos/invalidos/`:**
   * Garantir que cada arquivo `.mlg` tenha sua versão correspondente `.ml` ou seja renomeado.
   * Exemplo: `exemplos/validos/fatorial.ml`, `exemplos/validos/exemplo_basico.ml`.

2. **Garantir que o exemplo básico do edital esteja presente:**
   Criar `exemplos/validos/exemplo_basico.ml` com o código fornecido no edital:
   ```pascal
   programa exemplo_basico
   var n: inteiro;
   var fat: inteiro;
   var i: inteiro;
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

3. **Atualizar os comandos no `README.md`:**
   Substituir referências como `py minilang.py exemplos/validos/fatorial.mlg --symbols` por `.ml`.

---

## 3. Como Validar

Execute no terminal:

```bash
python minilang.py exemplos/validos/exemplo_basico.ml --ast
python minilang.py exemplos/validos/exemplo_basico.ml --symbols
```

A saída deve ser:
`[SUCESSO] exemplo_basico.ml: análise léxica, sintática e semântica concluídas sem erros`
