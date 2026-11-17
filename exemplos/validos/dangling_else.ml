# Dangling else: o 'senão' pertence ao 'se' mais próximo (docs/gramatica.md, seção 6)
programa dangling
var
  a, b: inteiro;
{
  leia(a);
  leia(b);

  # Sem chaves: o senão é do 'se b > 0' (o mais interno)
  se a > 0
    se b > 0
      escreva(1);
    senão
      escreva(2);

  # Com chaves: o senão passa a ser do 'se a > 0'
  se a > 0 {
    se b > 0
      escreva(3);
  } senão
    escreva(4);

  # Cadeia senão-se
  se a == 0 escreva(10);
  senao se a == 1 escreva(11);
  senao escreva(12);
}
fim.
