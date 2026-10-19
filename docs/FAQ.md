# Frequently asked questions

### Can CAPT-Bot run independently of CAPT Core?
Not as the supported design. `capt_bot/ui_server.py` imports the Core desktop runtime client and connects to Core's authorized Unix socket. Core remains the single authoritative runtime.

### Does Create Bot start an autonomous agent?
No. Registration creates identity/policy only. Activation and grants are distinct future governed states.

### Are Cloudflare, Docker and workflow modules implemented?
Source and tests exist for several related adapters/backends. This does **not** establish production credentials, adopted resources, entitlement, a working Docker daemon, or R5 release certification.

### Why can I see an approval but not start a run?
An informational approval reference is not executable authority. The selected session, request, mission, task, DriverRun, expiry, remaining uses and provider/model/workspace binding must match.

### Will CAPT-Bot fix all my GitHub issues without supervision?
The complete unattended issue-to-PR-to-merge loop is not release-proven. Human approval and per-effect reconciliation remain mandatory where policy requires them.

### The provider appears in a dropdown. Is it live?
No. The catalog is sanitized configured metadata with `availabilityVerified: false`. Provider health, balance and tool/model access require separate verification.

### Can I use an old compatibility pass as a current release certificate?
No. It was a test-only overlay against a pinned historical Core SHA, not R5 production composition.

### Does the public repository include reuse permission?
Public GitHub visibility is not a license grant. No root license file was present in this audited tree; obtain a maintainer-published license before assuming redistribution rights.

### How do I request help?
Include CAPT-Bot/Core SHAs, local setup and sanitized error category. Never post session tokens, API keys or private receipts. See [Troubleshooting](TROUBLESHOOTING.md).

[Glossary](GLOSSARY.md) · [Compatibility](COMPATIBILITY.md) · [Agent contract](AGENT_OPERATOR_GUIDE.md).
