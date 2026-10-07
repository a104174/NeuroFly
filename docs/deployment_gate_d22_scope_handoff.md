# Deployment Gate D2.2 resume — release ownership confirmation

Decision: `STORAGE_PROVIDER_OPERATOR_ACTION_REQUIRED`.
Status: `READY_FOR_OPERATOR_ACTION`. No remote release is verified.

This resumes the committed authentication handoff, rather than restarting D2.2.
Initial clean `main == origin/main`:
`af63e08a245172288cfb4bc7ce394c617763cbe5`.
The authentication handoff, D2 and D2.1 are committed; diff check passed.

## Completed resumed checks

- Vercel CLI **62.7.0**, Node.js **24.11.1**.
- `whoami` succeeds as **hcruz**. No authentication token was inspected or printed.
- Installed `blob --help` and help for store listing/creation/upload/retrieval
  were inspected. Private access, explicit pathname, no-random-suffix and
  no-overwrite options are supported; both upload booleans default to false.
- The inventory, manifest and existing archive passed committed D2 verification.
  No rebuild or scientific artifact regeneration occurred.

Frozen inventory ID:
`cf85d5fb1b688857e0af44d7cfe934382cdc9e3588185c87a754f6fa5f24a98b`.
Frozen manifest ID:
`e0dd15da7a1dd27456f7c1d9ecebc5a6ec8f2b11e07c8e3065b047c22ad9c882`.
Archive bytes: **3,674,299**. Archive SHA-256:
`12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5`.
All 74 original inventory files retain exact sizes/hashes.

## New stopping boundary: scope ownership

The committed authentication handoff names team
`team_lqFdMyuSy0bBP4cAMU8az64v`, slug
`andrepintos-projects-24230ca3`, discovered through the connected MCP account.

The newly authenticated CLI account instead lists only:

| CLI scope | Team name | Plan |
| --- | --- | --- |
| `hd-dev` | HC | Hobby |

The explicit read-only command targeting the handoff's scope:

```sh
npx --yes vercel@latest blob list-stores --all --json \
  --scope andrepintos-projects-24230ca3
```

failed with `The specified scope does not exist` (exit 1). Thus the current CLI
identity cannot resolve the documented release-owner scope. This does **not**
establish that the team/store is globally absent. It does not authorize moving
the release into `hd-dev` merely because that team is accessible.

## Required operator direction

Confirm one ownership path before store creation:

1. Explicitly authorize **`hd-dev` / HC** as the NeuroFly runtime-release owner;
   then resume read-only store enumeration there and create a dedicated private
   store only if no suitable NeuroFly store exists.
2. Retain **`andrepintos-projects-24230ca3`** as release owner and authenticate a
   CLI account that can resolve that team.

No personal/team destination was guessed. No store was created, selected,
modified or deleted. No object was checked, uploaded or retrieved. No frontend
project or backend deployment occurred. The original authentication handoff
remains unchanged; its missing-authentication observation is historical, not
the current blocker.

The frozen object key and complete resumed transfer/provisioning sequence remain
in `deployment_gate_d22_storage_handoff.md`. After scope confirmation, continue
from **store enumeration**, not from artifact generation. Store-specific Blob
credentials may still need separate configuration; account login is not proof
that object-transfer credentials are available. Never expose them in chat/logs.

No remote release JSON was created because cloud round-trip verification has not
occurred. Cloud-derived provisioning, `/health`, `/ready`, all five playback
identities, eight historical replays and post-run hashes are NOT_RUN. Full
repository quality gates are pending successful round-trip; no PASS is claimed.

Current official private-storage/CLI documentation was checked alongside the
installed CLI help:
[private storage](https://vercel.com/docs/vercel-blob/private-storage),
[Blob CLI](https://vercel.com/docs/cli/blob).
The Vercel CLI/storage skills informed the explicit-scope and secret-handling
checks. No provider credential was read, logged or committed.

Only this non-secret handoff document was added. No scientific/application code,
frozen authority, archive, scenario payload or prior record was modified.
No Git staging, commit or push occurred.
