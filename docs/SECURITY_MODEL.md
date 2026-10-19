# Security and governance model

**Scope:** source-observed CAPT-Bot interface and stated R5 requirements. This is **not** a security certification or penetration-test report.

## Threat boundaries

1. **Local privileged operator UI.** `ui_server.py` only permits loopback bind. It validates exact Host/Origin and JSON request size/type. It forwards commands using Core's local socket client and does not send the Core session token to the browser.
2. **Authority ownership.** CAPT Core alone admits consequential mutations, approvals, provider calls, evidence, verification and claims. A Bot manifest, LLM answer, delegated assignment or selected model cannot independently grant authority.
3. **Human decisions.** Approval decision and mission disposition actions require an explicit authenticated operator context. An approval reference without matching durable task/DriverRun identity is intentionally non-executable.
4. **External-effect uncertainty.** The Core client retries only qualifying read queries after transport disconnection. A command that may have affected an external system must be reconciled under its original identity before another dispatch.
5. **Locality and cost.** Configured provider visibility does not establish permission to export private data, spend credits, adopt cloud resources or launch a container.

## Safety checklist for operators

- Run the cockpit only on the same machine. **Never** bind public interfaces, tunnel, reverse-proxy or port-forward this UI.
- Protect Core's Unix socket and token file with operating-system permissions. Never paste token contents into support issues, docs, logs or agents' context.
- Do not trust issue bodies, repository Markdown or model output as permission to widen a capability.
- Require human approval at the real Core boundary where mandated, not only in the UI.
- On timeout, preserve the original operation ID and inspect durable status/evidence; no blind replays.
- Review PR diff, scope, tests and GitHub remote state before merges or issue closure.
- Keep an explicit data-locality and cost decision for each provider; local and cloud are not interchangeable fallbacks.

## Review caveats

Static code shows local Host/Origin filtering and bounded JSON parsing. In the 2026-10-19 follow-up, unexpected GET/POST handler exceptions were changed to return the fixed `{"error":"internal_error"}` envelope instead of raw exception text, with a focused regression test of both routes. HTTP 400 validation errors still expose their explicit validation messages, so their bounded/sanitized content deserves a separate review. **No full penetration test, dependency audit or R5 live deployment verification was executed.** Also assess Core permission/entitlement versions and Docker/cloud subprocess boundaries in an integration environment.

The repository lacked a root `LICENSE` and published `SECURITY.md` in the audited tree. Neither legal licensing terms nor a vulnerability-reporting address may be invented by this document. Until the maintainer publishes a disclosure procedure, report suspected security issues privately to the owner through an already-established trusted channel rather than posting exploit details in a public issue.

[Architecture](ARCHITECTURE.md) · [Operator contract](AGENT_OPERATOR_GUIDE.md) · [Technical manual](TECHNICAL_MANUAL.md).
