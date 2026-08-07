# Contracts: Popup Comparative Context

Feature 013 contracts. These documents define the behavior the implementation must
satisfy; they are validated by `tests/acceptance/test_rank.py`, `tests/acceptance/test_style.py`
(extended), and `tests/frontend/smoke_us7.md` (see [quickstart.md](../quickstart.md)).

| Contract | Scope |
|----------|-------|
| [popup-content.md](popup-content.md) | Popup hierarchy, exact German copy, delta rules, badge, footnote, degradation, mobile fit |
| [rank-quartile.md](rank-quartile.md) | Rank/quartile algorithm, tie-break, band formula, reference table, SC-003 test harness |

Cross-references: [data-model.md](../data-model.md) (entities), [research.md](../research.md)
(R-1..R-12 decisions), feature spec (FR-001..FR-017, SC-001..SC-007).
