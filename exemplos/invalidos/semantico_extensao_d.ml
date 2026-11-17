# Erros semânticos na extensão D
programa ext_d_semantico
var
  i: inteiro;
  b: booleano;
{
  para b = 1 ate 10 escreva(b);       # variável de controle booleana
  para i = 1 ate falso passo 0 {      # limite booleano e passo zero
    escreva(i);
  }
  repita
    i = i + 1;
  ate i;                              # condição não booleana
}
fim.
