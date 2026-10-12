# Por que o conjunto de teste espera — a estatística, sem jargão

> Escrito porque a pergunta foi feita várias vezes e as respostas anteriores explicaram **a regra**
> em vez de **o motivo**. Aqui o objetivo é que a regra fique óbvia, não obedecida.

---

## 1 · O problema em uma frase

**Um número medido sobre dados que você já usou para tomar decisões não estima o que você quer que
ele estime.**

Não é que o número fique "sujo" ou "contaminado" — essas palavras não explicam nada. É que ele para
de responder a pergunta *"quanto este modelo acertaria em dados novos?"* e passa a responder *"quanto
este modelo acerta nos dados que eu usei para escolhê-lo?"*, que é sempre mais.

O resto deste documento é isso, com números.

---

## 2 · A primeira forma: escolher a época

Você treina 50 épocas. Ao fim de cada uma, mede o desempenho num conjunto. Pega a melhor.

Suponha — e isto é o pior caso pedagógico, não o real — que o modelo **não melhora nada** ao longo do
treino: as 50 medições são o mesmo desempenho verdadeiro, digamos 70,0, mais ruído de medição.

Se cada medição tem ruído com desvio 1,0, as 50 medições ficam espalhadas em torno de 70,0. Você pega
a maior. **A maior de 50 amostras não fica em 70,0 — fica perto de 72,5.**

    verdadeiro:  70,0
    o que você reporta ao pegar o máximo de 50:  ≈ 72,5

Ganhou 2,5 pontos sem que o modelo tenha aprendido nada. Só de olhar 50 vezes e escolher.

Isto tem nome — **viés de seleção** — e a intuição é a que você já tem em outro contexto: se você
joga 50 moedas e reporta a que mais deu cara, não está medindo a moeda, está medindo o seu
procedimento de escolha.

**Por isso a época é escolhida num conjunto e o número é reportado em outro.** O conjunto que escolhe
paga o viés; o conjunto que reporta não olhou nada e por isso ainda estima o que interessa.

⚠ **Isto não é hipotético neste projeto.** Está medido: em Alabama, região, a diferença entre
escolher-e-reportar no mesmo conjunto e escolher num e reportar noutro é de **~1 ponto percentual**.
E a margem de equivalência que a dissertação usa é **0,4 pp**. O viés é **duas vezes e meia maior que
o efeito que queremos detectar.**

---

## 3 · A segunda forma, que é a que se esquece: escolher o *modelo*

O §2 é sobre escolher a época. Mas você escolhe muito mais que isso ao longo de meses:

- a arquitetura da cabeça;
- a taxa de aprendizado, por estado;
- o tamanho do lote;
- se usa ajuste de logit, e com qual τ;
- qual substrato, qual grafo, qual objetivo;
- quantas camadas, qual dropout.

**Cada uma dessas decisões foi tomada olhando um número.** E cada número olhado era de Alabama,
Arizona ou Istambul.

Isso significa que a receita final é, matematicamente, **um parâmetro ajustado a esses três
estados** — do mesmo jeito que os pesos da rede são parâmetros ajustados ao conjunto de treino. A
diferença é só que o ajuste passou pela sua cabeça em vez de por um gradiente.

E aí vem a consequência que costuma escapar:

> **Um fold de validação protege contra ajustar os PESOS demais. Ele não protege contra ajustar as
> DECISÕES demais.** Para isso é preciso um conjunto sobre o qual nenhuma decisão foi tomada.

É exatamente por isso que existem estados de reserva. Não é ritual — é o único jeito de medir se as
decisões tomadas em AL/AZ/IST valem em outro lugar, ou se elas eram só as que funcionavam ali.

---

## 4 · Por que "uma vez" e não "poucas vezes"

A pergunta natural: e se eu olhar só duas ou três vezes?

Cada olhada degrada um pouco. Se você olha, não gosta, muda alguma coisa e olha de novo, você fez
seleção — com n = 2 em vez de n = 50, mas fez. O viés é menor, não é zero, e **não é mensurável
depois**, porque depende de quantas alternativas você considerou e descartou, inclusive as que
descartou mentalmente sem rodar.

Esse é o ponto incômodo: o viés de seleção **não deixa rastro nos dados**. Não dá para corrigi-lo
estatisticamente a posteriori, porque a informação necessária — quantas coisas você olhou antes de
parar — não está em lugar nenhum. Só dá para **evitá-lo por procedimento**.

Por isso a contabilidade é fraca e o mecanismo é forte: registrar que você olhou não desfaz ter
olhado.

---

## 5 · Por que um ESTADO inteiro, e não um pedaço a mais de cada estado

Poderia-se guardar 10 % a mais de cada estado em vez de dois estados inteiros. Não é a mesma coisa.

Guardar um pedaço de Alabama mede: *"a receita generaliza para outros usuários de Alabama?"*

Guardar a Califórnia mede: *"a receita generaliza para outro lugar?"* — outro tamanho, outra
densidade de POIs, outra distribuição de categorias, outro número de regiões.

A segunda pergunta é a que a dissertação faz, porque a alegação é sobre o método e não sobre
Alabama. E é a mais difícil das duas: uma receita pode generalizar perfeitamente entre usuários do
mesmo estado e falhar ao mudar de escala. **Este projeto já viu isso acontecer** — o gate do negativo
duro (R15) muda o objetivo do treino acima de 50 000 lugares, o que só existe nos estados grandes.

---

## 6 · O que isto custa, e quando NÃO vale a pena

Reservar tem um preço real: você não sabe como o modelo se comporta lá até o fim. Durante o
desenvolvimento você fica cego para dois dos seis conjuntos.

**A reserva só vale se você pretende fazer a alegação que ela sustenta.** A alegação é:

> "Este resultado vale em dois conjuntos que nunca foram usados para tomar nenhuma decisão."

Se você **não** vai fazer essa alegação, a reserva não tem valor — e mantê-la é só custo. Essa é uma
decisão de escopo, não de estatística, e é do autor.

⚠ **A confusão que motivou este documento.** "CA e TX ainda não passaram por sweep de
hiperparâmetros, então são estados de desenvolvimento" — isto está **invertido**. Nunca terem sido
tunados é precisamente o que os torna reserva. O valor deles **é** não terem sido olhados; olhá-los
para "ver o comportamento do modelo" não os prepara para serem reserva, **gasta** a reserva.

Não há um estado intermediário. Um conjunto é reserva enquanto ninguém o viu, e deixa de ser no
instante em que alguém vê. Não é uma regra que se pode relaxar — é o que a palavra significa.

---

## 7 · O que isto significa para a dissertação, concretamente

**Os números de CA e TX da dissertação já estão publicados**, e vieram do pipeline v18 anterior
(`tables/mobiwac/results.tex`: CA 35,63 / 63,48 / 64,54; TX 36,33 / 64,94 / 66,15). A dissertação
**não depende** da reserva do mtlcheck.

A reserva do mtlcheck protege a **próxima** alegação — a de um artigo que queira dizer "validado em
dois conjuntos nunca usados para decisão". Gastá-la agora não fere a dissertação; fecha essa porta
para depois.

---

## 8 · O resumo, para não precisar reler

| | |
|---|---|
| **o que o viés é** | o máximo de N medições ruidosas fica acima do valor verdadeiro |
| **o tamanho aqui** | ~1 pp medido, contra uma margem de 0,4 pp |
| **por que não se corrige depois** | depende de quantas alternativas você descartou, e isso não está nos dados |
| **o que o fold protege** | os pesos |
| **o que só o estado reservado protege** | as decisões — receita, arquitetura, hiperparâmetros |
| **quando a reserva não vale nada** | quando você não vai fazer a alegação que ela sustenta |
| **o que a dissertação depende** | nada disto: os números de CA/TX dela já saíram do v18 |
