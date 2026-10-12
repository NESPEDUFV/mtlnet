# _fixtures/check_register

Two tiny hand-written trees proving `check_register.py` fires on the register defects and stays
silent on their American equivalents. Not copies of the real tree (failure class T6).

`dirty/src/chapters/fixture_target.tex` carries one hit of each mechanical class the gate must
catch: the British `need`+gerund construction ("needs saying plainly", the author's own instance
from PENDENCIAS_RESOLVIDOS 2.22 (arquivado 2026-07-30) point 8), three British spellings (`neighbour`, `behaviour`, `centre`), and a
Class B delayed-subject shape ("Several differences between the two configurations emerge").
`clean/` is the same tree with each rewritten in American English and with the subject named first.

Two shapes of the fixture are load-bearing and will look arbitrary otherwise:

- **Twenty filler chapters.** The gate refuses to report on a scope below 20 `.tex` files, because
  two other prose gates on this project silently swept almost nothing after a file move. A fixture
  under the floor would exit 2 on both sides.
- **A stub at the real OPEN_REGISTER path** (`chapters/3_cbic/conclusion.tex`), holding the needle
  its register entry names. The open register is self-retiring: an entry whose needle is absent makes
  the gate FAIL and demand the entry's deletion. Without this stub the clean side would fail, and it
  would be the gate working correctly rather than a fixture bug. `chapters/apx_f_cosine.tex` is a
  stub too, but it holds ordinary prose: it carried four needles until the parallel Appendix F track
  landed its rewrite on 2026-07-30 and those four entries retired. Leaving them here would have made
  the clean side fail on the delayed-subject and idiom shapes, with nothing holding them open.

`references.bib` carries `towards`, `Behaviour` and `Colour` inside `title` and `journal`, which are
attributes of record under AGENT_GUARDRAILS §1 R2. **Both sides must stay silent on them.** That is
the point of including them: the real bibliography's only British form is inside a published title
(Xu2023, `towards`, confirmed at Crossref 10.1145/3582553), and a gate that "corrected" it would
corrupt a citation attribute.
