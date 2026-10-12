# O Capítulo 5 contra a v19 — o que reproduz, o que não, e o que discorda

**Escrito em 2026-08-27**, depois da leitura confirmatória dos seis conjuntos.

Este documento existe porque a pergunta *"os números novos contradizem a dissertação?"* tem três
respostas diferentes conforme o eixo, e a resposta errada já esteve prestes a entrar num slide.

## ⚠ A regra que vale antes de qualquer comparação

**As células não se subtraem.** São estimandos diferentes:

| | Capítulo 5 (v18) | v19 |
|---|---|---|
| onde o número é lido | o fold de validação, **que também escolhe a época** | **teste selado**, lido uma vez |
| agregação | por fold | **OOF agrupado** |
| partição | uma, congelada | **sorteada por execução**, e o Δ é a média |
| margem | δ = 2 pp | **δ = 0,4 pp** |

A frase que fecha isso está no volume entregue, `05_setup.tex:30`:

> *"The held-out fold provides the validation data, and **we do not reserve a third split**."*

E a incomparabilidade está medida no projeto: a diferença entre protocolos em Alabama/região é de
**3,66 pp** ([`../../docs/QUAL_CONJUNTO_USAR.md`](../../docs/QUAL_CONJUNTO_USAR.md) §, nove vezes a
margem nova), e a macro-F1 média-por-fold é estimador enviesado sob desbalanceamento, medido em
**−0,24 pp** na estrutura do Alabama ([`../../docs/plans/EVALUATION_PROTOCOL.md`](../../docs/plans/EVALUATION_PROTOCOL.md) §1).

**O que se compara é o padrão e o veredito — nunca a diferença entre dois números.**

## 1 · Região: reproduz nos seis, sinal por sinal

Fonte do Capítulo 5: `articles/dissertacao/src/chapters/5_mobiwac/06_results.tex:223-228`.

| conjunto | usuários | Cap. 5 | v19 | sinal |
|---|---:|---:|---:|:---:|
| Alabama | 1 101 | −0,87 | −0,925 | ✔ |
| Arizona | 2 136 | −0,44 | −0,572 | ✔ |
| Florida | 10 622 | −0,16 | −0,219 | ✔ |
| Istambul | 14 530 | −0,08 | −0,122 | ✔ |
| California | 20 667 | **+1,06** | **+0,961** | ✔ |
| Texas | 22 592 | **+1,21** | **+0,893** | ✔ |

**Seis de seis com o mesmo sinal, e a ordenação é a mesma** — California e Texas trocam entre si, e
estão a dois mil usuários um do outro.

**O gradiente não é achado da v19.** Ele está no Capítulo 5, e a v19 o reproduz sob teste selado,
partição sorteada e margem cinco vezes mais estrita. É reprodução independente, não contradição.

**O que muda são dois vereditos, e por causa da margem:** Alabama e Arizona ficavam dentro de
δ = 2 pp e ficam fora de δ = 0,4 pp. O número praticamente não se moveu; a régua encolheu.

## 2 · Categoria: os dois concordam que o efeito é pequeno — e só isso

Fonte: `06_results.tex:208-214`.

| conjunto | usuários | Cap. 5 | v19 | concorda? |
|---|---:|---|---|:---:|
| Alabama | 1 101 | −0,19 [−0,33, −0,04] | −0,377 [−0,584, −0,177] | ✔ |
| Arizona | 2 136 | **−0,00** [−0,04, +0,03] | −0,115 [−0,224, −0,012] | sem sinal |
| Florida | 10 622 | +0,19 [+0,14, +0,25] | +0,136 [+0,097, +0,176] | ✔ |
| Istambul | 14 530 | +0,08 [+0,01, +0,15] | +0,155 [+0,076, +0,232] | ✔ |
| California | 20 667 | **−0,00** [−0,03, +0,02] | +0,035 [+0,015, +0,058] | sem sinal |
| Texas | 22 592 | −0,13 [−0,19, −0,08] | **−0,007** [−0,030, +0,017] | **discorda** |

**Três de seis com sinal e magnitude não-triviais.** Em dois, um dos lados é `−0,00` — não há sinal
para reproduzir. Um discorda (abaixo).

⚠ **A afirmação de reprodução tem de ficar ancorada em REGIÃO.** Estendê-la a categoria é falso, e a
tentação é real porque a frase honesta é mais fraca e soa como hedge:

> Os dois protocolos concordam em que o efeito de categoria é **pequeno nos seis** — nenhuma
> medição, em nenhum dos dois, passa de 0,4 pp em módulo.

Escreva o número ao lado (3 de 6 · 2 sem sinal · 1 discordância) e a frase fraca deixa de parecer
timidez: ela é precisão.

## 3 · Texas · categoria: a única discordância real

```
Cap. 5:  −0,13 [−0,19, −0,08]     → exclui zero: déficit pequeno, mas resolvido
v19:     −0,007 [−0,030, +0,017]  → inclui zero: indistinguível de zero
```

Os intervalos mal se tocam. Não é efeito da margem nem de poder — é o que se espera quando um número
deixa de ser lido no conjunto que o selecionou. **É a demonstração mais limpa do que o teste selado
faz**, mais concreta que qualquer explicação abstrata do protocolo.

⚠ **E o cuidado que ela exige.** É **uma** célula, e a direção do viés de seleção não é garantida a
priori. A leitura defensável é *"consistente com o que a remoção do viés de seleção produz"*. A
leitura indefensável é *"prova que o número entregue estava inflado"* — que é o mesmo exagero que
este projeto já corrigiu no sentido oposto (afirmar de dois estados o que só um sustenta), só que a
favor em vez de contra.

## O que isto NÃO resolve

**O eixo do gradiente continua confundido.** Neste corpus, `corr(log(classes de região),
log(janelas)) = +0,85` — estados maiores têm mais setores censitários. Com seis pontos, *"o conjunto
ganha porque há mais dados"* e *"ganha porque a tarefa é mais difícil"* não são separáveis. O
experimento que os separaria está pré-registrado (§4c, dose–resposta dentro de uma geografia) e
**não foi executado**. Ver [`../../docs/future_works/escada_mede_o_ruido_do_medidor.md`](../../docs/future_works/escada_mede_o_ruido_do_medidor.md)
para o outro item aberto do mesmo ciclo.

## Procedência

- v19: `studies/v19_defence/leitura/<estado>.json`, commit `a6639c0a`; receita
  `recipes/analysis/v19_ladder.toml` (δ = 0,4 congelado, linha 20).
- Capítulo 5: `articles/dissertacao/src/chapters/5_mobiwac/06_results.tex`, linhas 208-214
  (categoria) e 223-228 (região); `05_setup.tex:30` (ausência do terceiro bloco).
- ⚠ Alabama, Arizona e Istambul são **segunda leitura** — a campanha arquivada já os leu em
  2026-08-24. Florida, California e Texas são primeira leitura.
