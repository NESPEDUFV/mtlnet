# Respostas orais das erratas

Uma pagina por errata. A frase e para ser dita em pe, sem consultar nada, e cada numero que ela
carrega esta verificado contra os artefatos (ver `VERIFICACAO.md`).

---

## Q13 -- o controle de concatenacao

**A pergunta que vem.** "O senhor afirma que o ganho vem da estrutura hierarquica e nao das
features. Como sabe?"

**A resposta, dita em pe.**

> Nao sabemos, e a afirmacao no texto esta errada. Refizemos o controle na escala da propria
> Tabela 9, em tres datasets. Concatenar as features por visita ao place embedding fecha o intervalo
> inteiro em Alabama, 68 por cento em Arizona, e em Florida vai muito alem dele. Sao as features que
> carregam a maior parte do ganho de categoria. Ha errata escrita.
>
> O que a tabela estabelece continua de pe: a representacao de entrada domina a arquitetura.
> Injetar informacao por visita move o resultado muito mais do que qualquer diferenca de
> arquitetura que medimos. O que cai e a afirmacao mais fina sobre qual parte da representacao
> carrega o ganho.

**Se insistirem: entao a representacao por check-in nao serve para nada?**

> Em um dos tres datasets ela ainda lidera. Em Arizona fica 0,8 ponto acima da concatenacao,
> unanime nas cinco dobras. Em Alabama as duas empatam, e em Florida a concatenacao e que fica
> 0,8 acima. Com tres datasets nao da para dizer em que condicao ela lidera, e nao vou inventar
> uma.

**Se perguntarem pela procedencia.** O braco de fidelidade de Alabama reproduz a tabela exatamente,
fold a fold. Os de Arizona e Florida reproduzem a media, dentro de 0,07 e 0,03, mas nao os folds
individuais. Verifiquei que o treino e determinista, rodando a mesma configuracao duas vezes com
diferenca zero, entao essa discrepancia tem causa que ainda nao identifiquei, e digo isso em vez de
explicar. Ela e da ordem de 0,1 ponto; o efeito medido e de 1,7.


## Q14 · "O artigo lista o confundimento de capacidade como um dos cinco limites do resultado de
regiao. A lista da dissertacao nao o carrega. Por que ele saiu?"

**Ele nao deveria ter saido, entra como errata, e agora vem com a medicao que o artigo dizia faltar.**

> O artigo declara que o controle pareado por capacidade nao havia sido rodado. Eu o rodei, na
> California. Dando ao modelo dedicado de regiao noventa e sete por cento do orcamento de parametros
> do modelo conjunto, contado nos logs de treino, ele passa o conjunto por quatro decimos de Acc@10,
> com as cinco dobras na mesma direcao e um teste pareado que separa a diferenca de zero. Alargar
> alem da paridade nao acrescenta nada. No Texas nao ha controle pareado: o unico braco que correu
> la tem cerca de setenta por cento a mais que o conjunto, e a diferenca dele nao se separa de zero.
> Ou seja: na California, a vantagem de regiao que eu reporto mede capacidade, nao troca entre as
> tarefas. O que sobrevive e a afirmacao operacional, um modelo produz as duas predicoes em uma
> passada sem custo mensuravel em nenhuma das duas tarefas, e essa continua de pe.

*Corrigido a 2026-10-02 com os numeros de 2026-09-02 (`VERIFICACAO.md`, seccao do denominador; e o
texto atual de `errata_Q14_capacity_region.tex`). A versao anterior desta resposta tratava o braco de
528 como o "orcamento inteiro", dizia que o conjunto era igualado em Texas, e dispensava o braco de
352 como "cinquenta e sete por cento". Contra a contagem medida nos logs (5.151.189 parametros), o de
352 e o pareado (97,4 %, +0,41, p = 0,010, 5/5), o de 528 tem 174,8 %, e o unico braco do Texas tem
170,5 % (+0,21, p = 0,12).*

**Se perguntarem se isso derruba a tese.** Nao, e por uma razao que o documento ja declara: a tese
e sobre representacao, e vive no eixo de categoria. La o controle de capacidade aponta na direcao
oposta, multiplicar por quase sete (6,7; era "seis e meio" antes da recontagem de 2026-09-02) os
parametros do dedicado **baixa** o macro-F1 dele. Os dois
ganhos de regiao sao resultados secundarios, fora do plano de analise registrado, e a p. 76 e a
p. 88 ja dizem isso.

**Se perguntarem por que reportar um resultado que enfraquece o proprio texto.** Porque a
alternativa e deixar a banca descobrir. O limite estava no artigo; retirá-lo da dissertacao sem
medi-lo seria a unica versao indefensavel dos tres caminhos.

---

## Q15 · o quarto fundamento de integridade descrito na errata do suplemento

**Nao e errata a escrever. E errata a corrigir, e a correcao e retirar.**

> Aquela linha da tabela de errata descreve uma auditoria de desenvolvimento feita sobre uma
> construcao anterior da representacao, e a propria linha declara os tres limites dela: uma sonda
> linear, Florida numa unica inicializacao aleatoria, e construcoes anteriores da representacao. O
> texto que eu depositei nao carrega esse fundamento, e nao deveria: ele mediria uma preparacao que
> nao e a que os resultados usam. A linha de errata e que esta sobredeclarando, e ela sai.

**A verificacao.** As expressoes "on three grounds", "fourth ground", "linear probe" e
"forward-edge" tem zero ocorrencias em prosa viva do volume principal; "linear probe" aparece uma
vez, dentro da propria tabela de errata. Medido em 2026-08-13.
