# Fase 1 · fatorial A2 × A3 — resultado

**Medido 2026-08-21.** Alabama, **uma semente** (`model_seed=0`, `split_seed=0`), protocolo aninhado
(`inner_validation=true`), 5 folds. Braços em [`../waves/`](../waves/); base = `final_al`.

⚠ **Validação INTERNA.** Não gasta leitura de teste, não produz número citável. Responde a uma
pergunta só: *estas duas correções entram na v20?*

## Os números

| braço | região Acc@10 | Δ região | categoria macro-F1 | Δ categoria |
|---|---:|---:|---:|---:|
| base (A2 off, A3 off) | 74,5119 | — | 30,0751 | — |
| **A2** · unidades do Delaunay | 74,3341 | −0,178 (ep 0,163) | 30,2164 | **+0,141** (ep 0,059) |
| **A3** · simetriza o POI2Vec | 74,6739 | +0,162 (ep 0,134) | 30,2447 | **+0,170** (ep 0,057) |
| **A2 × A3** | 74,5851 | +0,073 (ep 0,182) | 30,1911 | +0,116 (ep 0,108) |

Δ pareados por fold; `ep` = erro-padrão do delta pareado sobre os 5 folds.

Em desvios: A2 região 1,09 ep · categoria 2,39 ep ▪ A3 região 1,21 ep · categoria 2,98 ep ▪
A2×A3 região 0,40 ep · categoria 1,07 ep. (Conferido independentemente pelo mtlcheck-2.)

## Leitura

**Região: nenhum dos três efeitos é resolvido.** Todos abaixo de 1,25 erro-padrão.

**Categoria: A2 e A3 sozinhos são reais** (2,4 e 3,0 ep). **A combinação não é** (1,07 ep) — e é
**menor que qualquer um sozinho**. Os dois não compõem; interferem. Faz sentido mecanicamente: o A2
redefine os pesos de aresta que o POI2Vec caminha e o A3 redefine a direção do caminho, então operam
sobre a mesma estrutura.

**Candidato limpo: A3 sozinho.** Melhora categoria com a maior margem em erro-padrão da tabela, não
machuca região, e é o comportamento defensável de um node2vec — o grafo de Delaunay é intrinsecamente
não-dirigido, e caminhá-lo num sentido só era artefato de o `edges.csv` guardar cada par uma vez.

**A2 não se sustenta sozinho** e **a combinação é pior que as partes**: levar os dois seria escolher
o braço de menor ganho medido.

## ⚠ Correção registrada — um erro de grandeza que passou por dois revisores

Uma leitura anterior deste mesmo dado afirmava que os dois efeitos do A2 estavam *"acima do piso de
ruído (0,034) e em direções opostas"*, e daí que o A2 era um **trade-off entre as duas tarefas** —
formulação que chegou a entrar no [`v19_defence/STUDY.md`](../../v19_defence/STUDY.md).

**Não se sustenta.** O piso de 0,034 pp é dispersão entre **sorteios de substrato**; a grandeza certa
para um delta pareado é o **erro-padrão do próprio delta**. São coisas diferentes. −0,178 ± 0,163 é
1,09 desvio.

O mecanismo de como passou vale mais que o erro: a formulação original era vaga ("não é melhoria
limpa"); o revisor a **melhorou** para "trade-off entre as duas tarefas, e num modelo multi-tarefa
isso é substantivo"; e o revisado aceitou a versão afiada **por ser mais afiada**. Ela era mais
afiada e mais errada. Nenhum dos dois perguntou se o teste conseguia falhar.

**Regra que fica:** um delta pareado se compara ao erro-padrão dele, nunca a um piso medido sobre
outra fonte de variação. E uma reformulação mais nítida vinda do revisor **não é evidência** —
precisa da mesma verificação que a original.

## Limite

**Uma semente, um estado.** Com erros-padrão de 0,06 a 0,18, quatro sementes mudariam a leitura de
qualquer um dos três braços. **Nada aqui congela a v20**; o passo 2 do [`STATE.md`](../STATE.md)
pedia ≥2 sorteios de substrato por braço e isso **não foi feito**.
