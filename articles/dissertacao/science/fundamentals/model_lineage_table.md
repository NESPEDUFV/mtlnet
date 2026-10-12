# Model-lineage table (for Ch. 2)

<!-- Source of the names: GLOSSARY.md. This is the DGI -> ... -> joint-model spine the chapter threads.
     Each row: the name as the GLOSSARY gives it, what it added, and the citation key. -->

| # | Model / method | What it added (one line) | Cite |
|---|---|---|---|
| 1 | **DGI** (Deep Graph Infomax) | Unsupervised node/place embeddings by maximizing mutual information between local patches and a global graph summary. | `velickovic2019deep` |
| 2 | **HGI** (Hierarchical Graph Infomax) | Extends graph infomax hierarchically over the POI-region-city hierarchy to yield urban-region (place) embeddings. | `huang2023hgi` |
| 3 | **MTLnet** | The project's first joint model: place embedding + FiLM conditioning + hard parameter sharing (+ Nash-MTL). Honest null: MTL ~ single-task at higher cost. | `silva2025mtlnet` |
| 4 | **ST-MTLNet** | Keeps MTLnet but replaces the monolithic place-embedding input with decomposed spatial + temporal + categorical encoders; category F1 rises sharply. | (CoUrb record, DOI 10.5753/courb.2026.22960) |
| 5 | **Check2HGI** | The check-in-level representation: graph infomax extended to the check-in itself (Check-in -> POI -> Region -> City), so each visit carries the representation, not each place. | (MobiWac, submitted / under review) |
| 6 | **The joint model** | Cross-attention joint model on Check2HGI: one model beats both dedicated single-task models -- category everywhere, region at four of six datasets with TOST non-inferiority at the other two. | (MobiWac, submitted / under review) |

<!-- Verb discipline: row 6 wins are bound to the paper's paired tests; "matches" at the two non-inferior datasets
     is TOST within the two-point margin, never upgraded to a win. Status wording for rows 5-6 is
     "submitted, under review" -- never "published/accepted". -->
