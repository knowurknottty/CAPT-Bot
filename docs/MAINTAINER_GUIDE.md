# Maintainer guide — release and documentation ownership

This is an operational **checklist**, not a release certificate. The added `.github/workflows/docs-integrity.yml` is scoped to documentation QA, not production acceptance.

**Canonical public front door:** root [README](../README.md) and [documentation index](START_HERE.md). Human workflow truth belongs in [PUBLIC_USER_GUIDE](PUBLIC_USER_GUIDE.md), agent contract in [AGENT_OPERATOR_GUIDE](AGENT_OPERATOR_GUIDE.md); architecture remains owned by [R5 spec](architecture/CAPT_BOT_CONVERGENCE_R5.md) and source anchors.

For each meaningful change:

1. Freeze Bot/Core SHAs; inventory source, contracts, executable surfaces and affected reader journeys.
2. Update canonical guide(s), compatibility ledger and affected cross-links. Do not add parallel, contradictory 'complete guides'.
3. Run `python3 scripts/check_docs.py` and `python3 -m unittest discover -s tests -p test_docs_integrity.py` for public-doc changes. Record `PASS/FAIL/NOT RUN`; archive proof without leaking tokens.
4. Audit authority effects, secret exposure, licensing, release language and historical-vs-current claims.
5. Require human review before changing license/security policy, publishing releases, widening external authority or merging consequential PRs.
6. Preserve old architecture plans as historical evidence; mark superseded assertions rather than rewriting old receipts.

**Known maintainer decisions needed:** publish licensing terms and coordinated disclosure channel; define packaging/version support and product readiness; approve actual R5 migration and release gates. See [OMEGA audit](audit/OMEGA_2026-10-19.md) and [Release notes](RELEASES_AND_MIGRATIONS.md).
