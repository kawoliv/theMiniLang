# 🛠️ Fix 03: Conformidade de Identificadores e Literais no Lexer

**Módulo:** `minilang/lexer.py` e `tests/test_lexer.py`  
**Severidade:** 🟡 Média (Conformidade com a Seção 4 do Edital Oficial)  
**Responsável Sugerido:** Integrante responsável pelo Léxico (M1)  

---

## 1. Os Problemas

### Problema A: Identificador iniciado por sublinhado (`_`)
Na Seção 4 do documento oficial do professor Daniel Santana:
> *"Identificadores: **letra seguida** de letras, dígitos ou sublinhado; não pode coincidir com palavra reservada."*

No código atual de [`minilang/lexer.py`](../minilang/lexer.py):
```python
def _e_letra(self, c: str) -> bool:
    return c.isalpha() or c == "_"  # Aceita _var como identificador válido!
```
Pela especificação formal clássica, um identificador deve **obrigatoriamente iniciar com uma letra**. O caractere `_` só pode aparecer a partir do segundo caractere (ex: `minha_var` é válido; `_var` é inválido).

### Problema B: Número colado em identificador (`123abc`)
Se o código contiver `123abc` (sem espaço), a função `_ler_numero` consome `123` como `NUM_INT` e a iteração seguinte consome `abc` como `IDENT`.
Pela regra clássica do compilador (*Maximal Munch*), `123abc` não são dois tokens válidos colados, mas sim um **erro léxico** (identificador iniciado por dígito ou sufixo inválido em número).

---

## 2. Como Corrigir no Código

Abra [`minilang/lexer.py`](../minilang/lexer.py):

### Passo 1: Ajustar `_e_letra`

**Antes:**
```python
    def _e_letra(self, c: str) -> bool:
        """Letra ou sublinhado que pode INICIAR uma palavra ou identificador (inclui '_' e acentos)."""
        return c.isalpha() or c == "_"
```

**Depois:**
```python
    def _e_letra(self, c: str) -> bool:
        """Apenas letra que pode INICIAR uma palavra ou identificador (conforme edital Seção 4)."""
        return c.isalpha()
```
*(Nota: `_e_parte_palavra` continua aceitando `_`, permitindo `var_1` normalmente).*

### Passo 2: Validar fim do número em `_ler_numero`

**Antes:**
```python
    def _ler_numero(self, linha: int, coluna: int) -> None:
        """Lê dígitos consecutivos e gera um literal inteiro."""
        inicio = self.pos
        while self._e_digito(self._peek()):
            self._avancar()
        lexema = self.fonte[inicio:self.pos]
        valor = int(lexema)
        self.tokens.append(Token(TokenType.NUM_INT, lexema, linha, coluna, valor))
```

**Depois:**
```python
    def _ler_numero(self, linha: int, coluna: int) -> None:
        """Lê dígitos consecutivos e gera um literal inteiro, rejeitando sufixos como 123abc."""
        inicio = self.pos
        while self._e_digito(self._peek()):
            self._avancar()
        
        # Se após os dígitos vier imediatamente uma letra ou sublinhado, é erro léxico
        if self._e_parte_palavra(self._peek()):
            while self._e_parte_palavra(self._peek()):
                self._avancar()
            lexema_invalido = self.fonte[inicio:self.pos]
            self._adicionar_erro(linha, coluna, f"identificador ou número malformado '{lexema_invalido}'")
            return

        lexema = self.fonte[inicio:self.pos]
        valor = int(lexema)
        self.tokens.append(Token(TokenType.NUM_INT, lexema, linha, coluna, valor))
```

---

## 3. Teste Automatizado para Adicionar

Abra [`tests/test_lexer.py`](../tests/test_lexer.py):

```python
    def test_rejeita_identificador_iniciado_por_sublinhado_ou_numero(self):
        # Identificador iniciado por _ deve gerar erro léxico
        lexer1 = Lexer("_variavel = 10")
        lexer1.tokenizar()
        self.assertGreater(len(lexer1.erros), 0, "Deveria rejeitar identificador iniciado com '_'")

        # Número com letras coladas (123abc) deve gerar erro léxico
        lexer2 = Lexer("x = 123abc;")
        lexer2.tokenizar()
        self.assertGreater(len(lexer2.erros), 0, "Deveria rejeitar número seguido de letras sem espaço (123abc)")
```

---

## 4. Como Validar

Execute no terminal:

```bash
python -m unittest tests/test_lexer.py -v
```

Todos os testes devem passar com `OK`.
