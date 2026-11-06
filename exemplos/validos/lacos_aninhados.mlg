# Todos os comandos de repetição (base + extensão D), aninhados
programa lacos
var
  i, j, soma: inteiro;
  achou: booleano;
{
  soma = 0;
  achou = falso;

  para i = 10 até 1 passo -1 {
    para j = 1 ate i
      soma = soma + j;
  }

  enquanto soma > 100 e não achou {
    soma = soma - 7;
    se soma % 5 == 0 achou = verdadeiro;
  }

  # repita sem chaves: a lista de comandos vai até o 'ate'
  repita
    soma = soma + 1;
    escreva(soma);
  ate soma >= 50;
}
fim.
