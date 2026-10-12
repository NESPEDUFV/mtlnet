# Achados da leitura — o gradiente com o tamanho, e o que ele não separa

**Escrito em 2026-08-27**, depois da leitura confirmatória dos seis conjuntos. Nada aqui é
exploratório: os números vêm dos payloads em [`leitura/`](leitura/), a telemetria de gradiente vem
dos `result.json` das células conjuntas, e a leitura foi gasta uma vez.

## O resultado

| conjunto | usuários | janelas | classes reg | P | co-primária | cat Δ (IC90) | reg Δ (IC90) |
|---|---:|---:|---:|---:|---|---|---|
| alabama | 1 101 | 0,58 M | 1 109 | 6 | não vale | −0,377 [−0,584, −0,177] · inconclusivo | −0,925 [−1,099, −0,767] · **inferior** |
| arizona | 2 136 | 0,80 M | 1 547 | 4 | não vale | −0,115 [−0,224, −0,012] · não-inferior | −0,572 [−0,719, −0,430] · **inferior** |
| istanbul | 14 530 | 1,63 M | 520 | 6 | **VALE** | +0,156 [+0,076, +0,232] · **superior** | −0,122 [−0,181, −0,074] · não-inferior |
| florida | 10 622 | 5,10 M | 4 703 | 4 | **VALE** | +0,136 [+0,097, +0,176] · **superior** | −0,219 [−0,257, −0,179] · não-inferior |
| california | 20 667 | 11,70 M | 8 501 | 4 | **VALE** | +0,035 [+0,015, +0,058] · não-inferior | +0,961 [+0,908, +1,029] · **superior** |
| texas | 22 592 | 11,49 M | 6 553 | 3 | **VALE** | −0,007 [−0,030, +0,017] · não-inferior | +0,893 [+0,853, +0,934] · **superior** |

⚠ Alabama, Arizona e Istambul foram lidos antes pela campanha da ponte — **segunda olhada nos mesmos
usuários**, e isso acompanha o número onde ele for reportado. Florida, California e Texas eram
virgens.

## Os dois fenômenos

**Em região, o sinal inverte.** De −0,93 no menor conjunto a +0,96 no maior — quase 2 pp de
amplitude, e o modelo conjunto passa de claramente pior a claramente melhor.

**Em categoria, o ganho tem pico e desaparece.** −0,38 → −0,12 → **+0,16** → **+0,14** → +0,04 →
−0,01. Não é monotônico: sobe até o meio da escala e volta a zero.

### E não é artefato

Todas as execuções concordam em sinal, em todos os conjuntos e nas duas tarefas onde o efeito existe.
Em California o Δ de região vai de +0,90 a +1,10 nas quatro execuções; em Texas, +0,85 a +0,95 nas
três. É o resultado mais consistente da campanha.

**Nem é OOD.** A fração de rótulos de região ausentes do treino é ≤0,83 % em toda parte e **idêntica
entre os braços**; o Δ em `top10_raw` bate com o `indist` até a terceira casa.

## O mecanismo — e são DOIS, não um

A telemetria de gradiente estava ligada em todas as células (`grad_geometry = true`). Ela mede, sobre
os parâmetros COMPARTILHADOS do modelo conjunto, o cosseno entre os gradientes das duas tarefas e a
norma de cada um, por grupo do tronco.

### 1 · As tarefas não conflitam — são ortogonais

| conjunto | cosseno geral | % épocas negativas | cross_ab | cross_ba | ffn_a | ffn_b |
|---|---:|---:|---:|---:|---:|---:|
| istanbul | +0,00089 | 48,3 % | +0,00127 | +0,00142 | +0,00045 | +0,00176 |
| alabama | +0,00059 | 49,6 % | +0,00128 | +0,00013 | +0,00104 | +0,00101 |
| arizona | +0,00134 | 44,3 % | +0,00230 | +0,00133 | +0,00189 | +0,00122 |
| florida | +0,00039 | 46,0 % | +0,00094 | −0,00031 | +0,00176 | −0,00011 |
| texas | +0,00130 | 43,3 % | +0,00031 | +0,00193 | +0,00089 | +0,00098 |
| california | +0,00107 | 42,8 % | +0,00096 | +0,00167 | +0,00147 | +0,00035 |

**O maior cosseno medido é 746× menor que 1**, e 45,7 % das épocas têm cosseno negativo — sob
ortogonalidade pura o esperado é 50 %. Em nenhum conjunto, em nenhum grupo do tronco, há
interferência destrutiva.

**Consequência prática:** a família de métodos de manipulação de gradiente — PCGrad, CAGrad,
Aligned-MTL — **não tem o que fazer neste problema**. Eles projetam gradientes que apontam em
direções opostas; aqui eles apontam em direções independentes. Isto é uma medição em seis conjuntos,
não uma suposição.

### 2 · Região: ALOCAÇÃO do tronco, ordenada pela cardinalidade

| conjunto | classes reg | \|g\| cat | \|g\| reg | **razão reg/cat** | Δ reg |
|---|---:|---:|---:|---:|---:|
| istanbul | 520 | 0,1061 | 0,0884 | **0,83** | −0,122 |
| alabama | 1 109 | 0,1294 | 0,1154 | **0,89** | −0,925 |
| arizona | 1 547 | 0,1139 | 0,1438 | **1,26** | −0,572 |
| florida | 4 703 | 0,0874 | 0,1299 | **1,49** | −0,219 |
| texas | 6 553 | 0,0765 | 0,1261 | **1,65** | +0,893 |
| california | 8 501 | 0,0775 | 0,1477 | **1,91** | +0,961 |

A razão cresce **monotonicamente com o número de classes, sem uma inversão**. O gradiente de região
passa de mais fraco que o de categoria a quase o dobro dela: o tronco é progressivamente governado
pela tarefa de região.

`corr(razão, log classes) = +0,97` contra `+0,86` com log(janelas). E o caso que separa os dois:
**Alabama tem o MENOR volume de todos (0,58 M janelas) e ainda assim razão maior que Istambul, que
tem o triplo** — porque tem o dobro de classes. A razão segue cardinalidade, não volume.

Na desagregação por grupo, o efeito é mais nítido ainda nos blocos do lado de região: em `ffn_b` a
razão vai de 3,41 (Istambul) a 10,28 (California), e em `cross_ba` de 2,28 a 8,06.

### 3 · Categoria: SATURAÇÃO, e ela NÃO é o mesmo mecanismo

O ganho em categoria é um **U invertido em volume de dados**, não um gradiente:

```
  < 1 M janelas    o conjunto PREJUDICA   (AL −0,377 · AZ −0,115)
  1,6–5,1 M        o conjunto AJUDA       (IST +0,155 · FL +0,136)
  > 11 M           efeito NULO            (CA +0,035 · TX −0,007)
```

⚠ **E ele não segue a razão de normas.** O contra-exemplo é limpo e mata a hipótese de um mecanismo
único: **Istambul tem razão 0,83 e Δ +0,155; Alabama tem razão 0,89 e Δ −0,377.** Razões
praticamente iguais, efeitos opostos.

O que a telemetria mostra para categoria é **saturação**: `|g|cat` cai **41 %** do menor ao maior
conjunto (0,1294 → 0,0765), monotonicamente, em todos os grupos do tronco. Gradiente menor é menos
sinal residual — a tarefa foi aprendida. A base do braço dedicado confirma: sobe de 30,3 até ~35–37 e
estaciona.

**A leitura:** com pouco dado o tronco compartilhado é passivo e as duas tarefas perdem; com dado
intermediário há transferência real e a categoria ganha; com muito dado a categoria satura e não
sobra o que o compartilhamento acrescente.

### E a não-superioridade em CA/TX não é falta de poder

| conjunto | Δ cat | meia-largura IC90 |
|---|---:|---:|
| istanbul | +0,155 | ±0,078 |
| florida | +0,136 | ±0,039 |
| california | +0,035 | **±0,021** |
| texas | −0,007 | **±0,024** |

O intervalo em CA e TX é **três vezes mais estreito** que no Istambul. Um efeito de +0,15 teria sido
detectado com folga. É efeito ausente, medido com precisão.

## ⚠ O que estes dados NÃO permitem afirmar

**Cardinalidade e volume são confundidos neste corpus.** Estados maiores têm mais setores censitários:
`corr(log classes, log janelas) = +0,85`. E os dois predizem o efeito:

```
Δ reg × log(janelas)      = +0,93
Δ reg × razão de normas   = +0,80
Δ reg × log(classes)      = +0,73
```

Com **seis pontos** e essa colinearidade, *"o conjunto ganha porque há mais dados"* e *"o conjunto
ganha porque a tarefa é mais difícil"* **não são separáveis**. A telemetria dá um mediador plausível
para o segundo braço — a alocação do tronco — mas não exclui o primeiro.

**Não escreva o mecanismo como conclusão.** Escreva o gradiente como fenômeno, a ortogonalidade e a
alocação como medição, e o confundimento como limite declarado.

## O experimento que separaria, e ele já está pré-registrado

O **§4c** do protocolo: dose–resposta na Florida, subamostrando usuários de desenvolvimento a
25/50/75 %, retreinando os braços pareados e avaliando **nos mesmos folds externos selados**. Varia o
volume **dentro de uma geografia**, com a cardinalidade de região **fixa** — que é exatamente o corte
que este confundimento pede.

Custo: 90 fits, ≈1,2 dia de GPU (§7). **Não foi comprado.** Sob o desenho de partição sorteada ele
exige nomear a execução que o ancora — ver §4c, emendado em 25-08.

Uma curva plana em volume, com a cardinalidade fixa, atribuiria o efeito à dificuldade da tarefa. Uma
curva que sobe o atribuiria ao volume. Hoje as duas leituras cabem.

## Leia também

- [`LEITURA.md`](LEITURA.md) — o procedimento, e o que a leitura não autoriza
- [`STATE.md`](STATE.md) — o estado da campanha
- [`../../docs/plans/EVALUATION_PROTOCOL.md`](../../docs/plans/EVALUATION_PROTOCOL.md) §1, §2a, §4c
- [`../../docs/future_works/escada_mede_o_ruido_do_medidor.md`](../../docs/future_works/escada_mede_o_ruido_do_medidor.md)
