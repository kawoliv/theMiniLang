# Calculo de Fatorial em MiniLang
programa fatorial
var
  n, i, fat: inteiro;
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
