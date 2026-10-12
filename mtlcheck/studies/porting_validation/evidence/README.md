# As medições, como saíram das máquinas

Cada arquivo aqui é a saída bruta de um experimento citado em `../PLAN.md` ou em `docs/`. Ficam
versionados porque a alternativa — "roda de novo para conferir" — é exatamente o que este projeto
está tentando eliminar. Todos vieram do A40 (`nespedgpu`), Alabama, salvo indicação.

| arquivo | o que mede | onde é citado |
|---|---|---|
| `build_compare.json` | referência × `mtlcheck`, 500 épocas, pesos transplantados | R16, PLAN §4 |
| `rerun_floor.json` | **referência × ela mesma, mesma seed** — o piso que dá escala ao resto | R16 |
| `seed_floor.json` | referência em três seeds — o teto do desacordo | R16 |
| `determinism.json` | `use_deterministic_algorithms` on/off: divergência e custo | R16 |
| `substrate_sensitivity.json` | três substratos meus × o bancado, macro-F1 da célula de categoria | PLAN §4 |
| `own_substrate_manifest.json` | o manifesto de um build meu, com a curva de loss inteira | — |
| `banked_v18_materialize.json` | a proveniência do substrato bancado, para saber o que ele **é** | PLAN §4 |

Duas leituras que valem mais que os números isolados:

- `rerun_floor.json` **antes** de `build_compare.json`. Sem o piso, a distância entre implementações
  não tem escala e admite tanto "sucesso" quanto "fracasso".
- `banked_v18_materialize.json` antes de comparar qualquer coisa com o v18: ele registra que aquele
  substrato veio do engine `check2hgi_dk_ovl` por um readout por janela, e **não** do mesmo caminho
  que o build novo. Os dois braços não são o mesmo procedimento.

| `trajectory_25.json` | paridade do treinador de substrato, 25 épocas, **CPU com determinismo pinado** (`use_deterministic_algorithms` + thread única). `max \|ref−porte\| = 5,96e-08`. ⚠ Ficou fora desta tabela até 19-08, e foi por isso que `fbbeb356` o sobrescreveu com a captura pré-pin em CUDA (5,05e-04, ~8 500× pior) sem ninguém notar — durante um dia a única evidência commitada da paridade a **contradizia**. Restaurado de `18736eec`. |
