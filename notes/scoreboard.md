# Scoreboard

| Version                                                         | Practice (answers)             | Held-out | Guards | Hard (answers) | Hard (retrieval, hybrid)   |
| --------------------------------------------------------------- | ------------------------------ | -------- | ------ | -------------- | -------------------------- |
| Before glossary and CGST fix                                    | 22/22                          | 10/10    | 6/6    | 11/16          | 10/14                      |
| After glossary and CGST fix                                     | fill in after the clean re-run | fill in  | 6/6    | 16/16          | 14/14                      |
| After glossary and CGST fix (clean re-run)                      | 22/22                          | 10/10    | 6/6    | 16/16          | 14/14                      |
| First fair test: everyday words outside the glossary (hard_own) | n/a                            | n/a      | n/a    | n/a            | retrieval 1/8, answers 1/8 |
| Fresh set, glossary only                                        |                                |          |        |                | 0/10                       |
| Fresh set, rewrite                                              |                                |          |        |                | 10/10                      |
| Fresh set, both                                                 |                                |          |        |                | 10/10                      |
| hard_own, rewrite                                               |                                |          |        |                | 6/8                        |
| Version | Set | Result |
|---|---|---|
| Full system (rewrite + glossary, stemming, 8 cards) | practice (tuned on) | 22/22 |
| Full system | hard (tuned on) | 15/15 scored, 1 error (503) |
| Full system | hard_own (tuned on) | 8/8 |
| Full system | fresh2 (frozen, run once) | fill in |
| Stability, fresh set, top 5 | 5 repeats per question | 44/50 retrieval |
| Stability, fresh set, top 8 | 5 repeats per question | 50/50 retrieval |
| Full system, top 8 (before the two fixes) | fresh2 (frozen, run once) | 8/10 (failed: g02 seb, g10 makhan) |
| Full system after SEARCH TERMS and no typo fix after rewrite | fresh2 (now development) | 10/10 |
| same | hard (development) | 15/16 (k11 papad regressed) |
| same | practice | 22/22 |
