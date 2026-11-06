# Erro sintático: falta um '}'. O '}' da linha 11 fecha o 'enquanto' (linha 9),
# então o bloco principal (linha 7) fica aberto quando chega o 'fim'.
# Esperado: [SINTÁTICO] Linha 12, Coluna 1: esperado '}' para fechar o bloco aberto na linha 7, coluna 1, ...
programa bloco_aberto
var
  i: inteiro;
{
  i = 0;
  enquanto i < 10 {
    i = i + 1;
}
fim.
