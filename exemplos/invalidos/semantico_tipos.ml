# Erros semânticos de tipo: atribuição, condições e operadores
programa tipos
var
  n, i: inteiro;
  ok: booleano;
{
  n = verdadeiro;          # booleano atribuído a inteiro
  ok = 10;                 # inteiro atribuído a booleano
  se n escreva(n);         # condição não booleana
  enquanto n - 1 n = 0;    # condição não booleana
  i = n + ok;              # '+' com operando booleano
  ok = ok e n;             # 'e' com operando inteiro
  ok = não n;              # 'não' com operando inteiro
  ok = n == ok;            # comparação entre tipos diferentes
  i = n / 0;               # divisão por zero
}
fim.
