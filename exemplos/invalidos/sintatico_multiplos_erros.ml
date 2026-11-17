# Vários erros sintáticos: o parser se recupera (modo pânico) e reporta todos
programa varios_erros
var
  x, y: inteiro;
  ok booleano;
{
  x = ;
  y = (x + 2;
  se x > { escreva(x); }
  leia(10);
  x = 1 < 2 < 3;
  senão escreva(y);
  escreva(x, y);
}
fim.
