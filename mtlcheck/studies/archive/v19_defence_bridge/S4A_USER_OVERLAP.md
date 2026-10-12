# §4a — a sobreposição de usuários entre os conjuntos, medida em 2026-08-23

O §4a impõe esta auditoria como **precondição** de qualquer reivindicação entre estados:

> Precondition (one-hour pandas job): intersect user IDs across the six parquets — Gowalla users
> travel; if overlap is non-trivial, assign each traveller to one state or report the overlap and
> switch to the Bonferroni combining variant. Istanbul is clean by construction.

Nunca tinha rodado. Rodou agora, sobre os corpora de **entrada** — nenhuma predição tocada.

## ⚠ Primeiro, a armadilha que quase virou número errado

Uma contagem ingênua de interseção acusa 1 952 usuários "em comum" entre Istambul e a Califórnia. É
**falso**. Istambul vem do Massive-STEPS (HuggingFace) e os cinco estados vêm do Gowalla (SNAP) —
**espaços de identificador independentes**. Um inteiro repetido ali é coincidência, não a mesma
pessoa. A frase do §4a, "Istanbul is clean by construction", está **certa**, e uma auditoria que a
contradiga está medindo colisão de inteiro.

O que segue é restrito aos cinco estados dos EUA, onde o id significa a mesma pessoa.

## A medição

| estado | usuários | compartilhados com outro estado | |
|---|---:|---:|---:|
| alabama | 3 858 | 2 743 | **71,1 %** |
| arizona | 7 869 | 6 328 | **80,4 %** |
| florida | 21 052 | 9 503 | 45,1 % |
| california | 37 090 | 14 481 | 39,0 % |
| texas | 38 644 | 14 391 | 37,2 % |

União dos cinco: **80 875 usuários distintos** contra 108 513 somando os estados. **19 808 pessoas
(24,5 %) aparecem em mais de um estado**; 265 aparecem nos cinco.

Pares mais fortes: arizona×california 64,5 % do menor, alabama×florida 50,4 %, alabama×texas 46,3 %.

## ⚠ Segunda armadilha: viajante real ou artefato do ETL?

A medição acima só intersecta identificadores, e isso **não distingue** "a mesma pessoa viajou" de
"o ETL duplicou linhas entre os recortes". O autor levantou a dúvida; ela foi testada contra o dado,
não respondida por argumento.

| teste | resultado |
|---|---|
| lugares compartilhados entre estados | **zero** — o recorte é pela geografia do lugar |
| check-ins `(usuário, instante)` em dois estados | **5**, em ~9 milhões |
| um usuário compartilhado, de perto | 182 check-ins na Flórida entre 19–27/03/2011, **1** no Alabama em 27/03 às 17:25 |

Os cinco pares repetidos são coisas como o mesmo usuário às 14:36:19 e 14:36:21 em dois estados —
esquisitice do Gowalla bruto perto de fronteira, não duplicação sistemática. E o caso de perto é
inequívoco: é uma pessoa que passou uma semana na Flórida e cruzou o Alabama na volta.

**Veredito: viajante real. O ETL não duplica.**

## E o peso, que a contagem de usuários escondia

O exemplo acima mostra por que contar usuários não basta: aquele viajante vale 182 linhas na Flórida
e 1 no Alabama. Medindo por volume de check-ins:

| estado | % usuários compartilhados | % check-ins vindos deles |
|---|---:|---:|
| alabama | 71,1 % | 64,5 % |
| arizona | 80,4 % | 76,9 % |
| florida | 45,1 % | 44,9 % |
| california | 39,0 % | 46,5 % |
| texas | 37,2 % | **50,8 %** |

No Texas os viajantes são 37 % das pessoas e **51 % dos check-ins** — são mais ativos que a média. A
contagem por usuário **subestimava** a dependência nos estados grandes.

## O que isto decide

**A precondição do §4a falha, e com folga.** A remediação está pré-registrada e é uma escolha do
autor entre duas:

1. **atribuir cada viajante a um estado** — muda os corpora e obrigaria a re-treinar tudo; ou
2. **reportar a sobreposição e trocar para a variante de Bonferroni** na conjunção parcial — custo
   zero de GPU, só de poder estatístico.

A (2) é a que o protocolo antecipa como saída barata, e é a única compatível com o calendário.

## A consequência que é maior que a escolha de teste

Não é só o combinador. É a **força da frase**.

"Replicado em seis conjuntos" soa como seis observações independentes. Os cinco estados dos EUA são
recortes geográficos de **uma** população do Gowalla, com 24,5 % das pessoas em mais de um recorte —
e nos dois estados pequenos, que são estados-ponte, a fração passa de 70 %. **Alabama e Arizona são,
em maioria, gente que também aparece nos grandes.**

O conjunto genuinamente independente é **Istambul**, e é o único.

Isto não invalida nada: cada leitura intra-estado é condicional aos usuários daquele estado, e o
bootstrap por usuário é feito dentro dele. O que muda é o que se pode dizer ao juntar os seis — e a
dissertação precisa dizer isso antes que alguém pergunte.
