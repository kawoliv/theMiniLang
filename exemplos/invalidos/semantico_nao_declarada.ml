# Erros semânticos: variável não declarada e 'leia' em identificador não declarado
programa nao_declarada
var
  soma: inteiro;
{
  leia(n);                 # 'n' não foi declarada
  soma = soma + total;     # 'total' não foi declarada (e aviso: 'soma' lida sem valor)
  escreva(soma);
}
fim.
