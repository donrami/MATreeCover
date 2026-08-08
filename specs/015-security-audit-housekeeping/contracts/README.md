# Contracts: Security Audit & Repo Housekeeping (feature 015)

Interface contracts produced by this feature. Each contract is the reviewed, committed statement of a security-relevant surface; changing one is a contract change and must be reflected in the implementation and the audit report together.

| Contract | Requirement | Subject |
|----------|-------------|---------|
| [secrets-scan.md](secrets-scan.md) | FR-001/002/003, SC-001/007 | Secret patterns (P1–P32), the shared pattern file, tracked + history scan semantics, exemptions ledger, dispositions |
| [security-headers.md](security-headers.md) | FR-004/005, US2 | Security headers and CSP on every Worker response, R2 data surface, regression constraints |
| [layout-gate.md](layout-gate.md) | FR-009/010/011, SC-003 | Layout manifest format, gate semantics, sync rule with DEVELOPMENT.md |
| [vendored-provenance.md](vendored-provenance.md) | FR-008 | Vendored library record, declared runtime dependencies, update rule |
| [endpoint-trust-model.md](endpoint-trust-model.md) | FR-007 | RunPod endpoint exposure path, input validation, privileges, accepted risks |

Cross-cutting rules that apply to every contract here:

- **Additive only**: no contract may alter map values, colors, labels, popups, interactions, caching semantics, or the static architecture (FR-013).
- **Change together**: gate/script changes, contract changes, and audit-report entries for the same surface land in the same commit (FR-003 pattern; OR-004 discipline).
- **Machine-checkable**: every rule a script can enforce is enforced by a committed gate, never by documentation alone (FR-011).
- **No new dependencies**: enforcement uses git, grep, and the shell only.
