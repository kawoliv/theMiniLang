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
