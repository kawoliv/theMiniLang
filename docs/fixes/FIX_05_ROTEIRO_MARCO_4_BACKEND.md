# 🚀 Roteiro do Marco 4 (Back-End, Otimização, Relatório e Arguição)

**Módulo:** `minilang/interpretador.py`, `minilang/otimizador.py` e Relatório Técnico  
**Valor na Avaliação:** 10,0 pontos (de 40 pontos da A3)  
**Prazo Sugerido no Edital:** 17ª semana (30/11)  

---

## 1. O que Falta para Concluir o Compilador MiniLang?

Ao contrário do que alguns colegas podem pensar, **o projeto ainda não está concluído**. O compilador atual apenas valida léxico, sintático e semântico, mas **não executa os programas**.

Conforme o edital oficial (Seção 6, Rubrica M4), a entrega final exige:

| Critério Oficial | Pontos | O que deve ser feito |
| :--- | :--- | :--- |
| **Back-end funcional** | **4,0 pts** | Interpretar a AST diretamente ou gerar código de 3 endereços. Recomendado: criar um `Interpretador(Visitante)` que percorre a AST e executa comandos (`leia`, `escreva`, `atribuicao`, `se`, `enquanto`, `para`, `repita`). |
| **Otimização demonstrada** | **1,5 pts** | Implementar *Constant Folding* (dobradura de constantes) na AST. Exemplo: pré-calcular `2 + 3 * 4` como `14` antes da execução. Ativada pela flag `--optimize`. |
| **Relatório Técnico** | **2,5 pts** | Documento em PDF de **6 a 10 páginas** contendo: especificação da linguagem, diagramas do AFD, gramática EBNF, árvore sintática, tabela de símbolos, decisões de projeto, limitações e declaração de ferramentas/IA (Seção 8). |
| **Apresentação e Arguição Oral** | **1,5 pts** | Apresentação de 15 minutos com demo ao vivo perante o Prof. Daniel Santana. |
| **Domínio do código (Individual)** | **0,5 pt** | Perguntas individuais feitas pelo professor para cada integrante. |

---

## 2. Arquitetura Recomendada para o Back-End (Interpretador)

Como o projeto já implementou o padrão **Visitor** em [`minilang/arvore.py`](../minilang/arvore.py) e usou no semântico, a forma mais limpa, robusta e rápida de fazer o Back-End é criar:

```
minilang/interpretador.py  -> Classe Interpretador(Visitante)
```

### Como funciona:
1. Mantém um dicionário de ambiente de memória em execução: `self.memoria: dict[str, int | bool] = {}`.
2. `visitar_Atribuicao`: avalia o valor da expressão e grava `self.memoria[alvo] = valor`.
3. `visitar_Leia`: lê do teclado com `input()` e converte para `int` ou `bool`.
4. `visitar_Escreva`: imprime no terminal com `print()`.
5. `visitar_Se`: avalia condição booleana e executa ramo `então` ou `senão`.
6. `visitar_Enquanto`: executa laço `while self.visitar(no.condicao): self.visitar(no.corpo)`.
7. `visitar_Para`: executa laço `for valor in range(inicio, limite + 1, passo): ...`.
8. `visitar_Repita`: executa corpo ao menos uma vez e repete até a condição ser verdadeira.

---

## 3. Otimização Obrigatória: Constant Folding (Dobradura de Constantes)

Criar [`minilang/otimizador.py`](../minilang/otimizador.py) contendo a classe `Otimizador(Visitante)`:
* Quando encontra um nó `Binaria("+", Numero(2), Binaria("*", Numero(3), Numero(4)))`:
  * Detecta que ambos os lados são números conhecidos em tempo de compilação.
  * Substitui o nó binário por um único nó `Numero(14)`.
* Mostrar na demo do professor o comparativo com `--ast` e `--ast --optimize` (o professor exige ver o antes e o depois da otimização).

---

## 4. Roteiro da Arguição Oral (15 minutos com o Professor)

O edital oficial estabelece que o professor fará perguntas individuais:
1. **Léxico:** Explicar o funcionamento do AFD e como foi tratado o *lookahead* (`=`, `==`, `<`, `<=`, `>`, `>=`).
2. **Sintático:** Explicar por que a gramática é LL(1) e como o *dangling else* foi resolvido (associação gulosa ao `se` mais próximo).
3. **Semântico:** Explicar a estrutura da tabela de símbolos, a inferência de tipos e como foi implementada a detecção de variáveis não declaradas sem gerar erros em cascata.
4. **Back-end:** Mostrar um programa rodando ao vivo (ex: cálculo de fatorial) e demonstrar a árvore antes e depois da otimização.
