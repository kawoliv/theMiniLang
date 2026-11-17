# Precedência e associatividade das expressões (use --ast para ver a árvore)
programa expressoes
var
  x, y, z: inteiro;
  p, q, r: booleano;
{
  x = 10 - 3 - 2;              # (10 - 3) - 2         esquerda
  y = 1 + 2 * 3;               # 1 + (2 * 3)          * antes de +
  z = (1 + 2) * 3 % 4;         # ((1 + 2) * 3) % 4    parênteses
  x = - - y;                   # -(-y)                unário à direita
  p = x + 1 > y * 2;           # (x + 1) > (y * 2)
  r = não (x < y) e y <= z;    # (não (x < y)) e (y <= z)
  q = p ou x == 1 e não r;     # p ou ((x == 1) e (não r))
  escreva(x, y, z);
  escreva(p, q, r);
}
fim.
