# CAPT-Bot, explained without the jargon

Imagine you have a workshop. CAPT Core is the workshop's **key cabinet, safety rules, logbook, and inspector**. CAPT-Bot is the system for describing specialized workers and giving a human a cockpit to request, follow, and review their work.

A Bot **name and job description** are like an employee badge. They are not keys to the building. Registering a Bot does not let it edit files, call services, spend money or hire other Bots.

## What can I do today?

The source contains a local cockpit. With a properly configured and compatible CAPT Core running, you can attempt to view its operator state, create a Bot *identity*, prepare a governed prompt, review a proposal, and see which separate approval/review steps Core requires.

## What should I not expect yet?

Do not assume CAPT-Bot can independently wake up, repair every GitHub issue, activate skills, safely delegate, or deploy across Cloudflare by itself. The larger R5 integration work is documented but **not demonstrated as a fully released system**.

## Six words to remember

**Identity** = who a Bot says it is. **Authority** = what CAPT permits it to do. **Approval** = an explicit decision at a gate. **Evidence** = the recorded observations. **Verification** = checked evidence against criteria. **Claim** = what can responsibly be stated about the outcome.

A returned model answer is not automatically proof.

## First five minutes

Start at [Installation](INSTALLATION.md), then [Quickstart](QUICKSTART.md). For the human-operated flows, read [Human operator guide](PUBLIC_USER_GUIDE.md). If anything mentions paying for a model run, granting shell access, or making a public change, those are **separate decisions**—not a consequence of signing into the cockpit.
