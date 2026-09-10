# Idle / background transmission test — Grammarly (VALID run)

**Date:** 2026-09-10 · **Capture:** `data/raw/grammarly_idle/run_1.json` (+ `.log`)
**Window:** 20 min (2026-09-10 13:00 → 13:19 local / 17:00–17:19 UTC), Firefox `grammarly-test`
profile, Grammarly extension active on the test page, **routed through mitmproxy, NO user
action** (no paste, no typing, no clicks). Screen was allowed to lock — still "no user action".

## Validity — positive control passed
The first attempt recorded zero of anything (browser wasn't proxied) and was discarded. This
run was preceded by a routing control (11 captured requests) and **contains Firefox's own
background traffic** (`ads.mozilla.org`, `push.services.mozilla.com`) as a built-in positive
control — proving the capture path was live. `tls_handshake_failures = 0`, so nothing slipped
past encrypted-but-uncaught.

## Result — Grammarly is NOT silent while idle, but sends no document content
Totals: **27 events, 6 external domains, 0 % document exposure, 0/12 secrets, 0 events
carrying document content.**

Destination hosts (event counts):
| Host | Events | Grammarly? | Role |
|---|---|---|---|
| capi.grammarly.com | 7 | ✔ | client API / session |
| gateway.grammarly.com | 6 | ✔ | API gateway |
| config.extension.grammarly.com | 5 | ✔ | config polling |
| f-log-extension.grammarly.io | 3 | ✔ | telemetry/logging (`POST /logv2`) |
| auth.grammarly.com | 2 | ✔ | authentication / session |
| ads.mozilla.org | 4 | — | Firefox background (positive control) |

**23 of 27 events (all five Grammarly hosts) occurred with no user action**, but **none
carried the test document or any planted secret** (`exposed_events = 0`,
`sensitive_token_count = 0`, `carries_doc = 0`).

## Interpretation
Two distinct privacy facts, both true:
1. **Always connected.** The extension maintains a persistent live relationship with
   Grammarly's servers even when completely unused — authenticating, polling configuration,
   keeping a gateway/session, and sending telemetry/logs. Merely having it installed and
   loaded means continuous background contact with Grammarly, independent of any typing.
2. **Content exposure is input-triggered.** The *document itself* is only transmitted once
   the user supplies text; while idle, no document content or secret left the machine.

This refines the headline finding: the near-total document exposure documented elsewhere is
triggered by user input, but the tool is not dormant between uses — it is in constant,
low-level background communication with the vendor.

*Reproduce:* proven-proxied profile, `TOOL_NAME=grammarly_idle mitmdump -s ...capture_addon.py`,
open the test page, leave untouched 20 min. Require Firefox background hosts in the capture as
a positive control before trusting any "no content" conclusion.
