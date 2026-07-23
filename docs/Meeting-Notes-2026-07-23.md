# Supervisor Meeting Notes — 23 July 2026

**Supervisor:** Prof. Marco Aiello · **Format:** in person · **Duration:** ~20 min (12:57–13:17)

## Outcome in one line
Methodology **approved**. Encouraged to **broaden the study where feasible** — including testing tools on the **desktop, not only in Firefox** — with partial additions welcome (not everything required). Report format is **free**.

## Confirmed / decided
- **Methodology — approved.** He is fine with the current approach as it stands.
- **Report format — any format.** IEEE double-column is acceptable if I want it; he has no preference at all. *(This resolves our open "report template" question.)*

## New directions to investigate *(do what's feasible; not all required)*
1. **Not Firefox-only — test on the desktop too.** He wants the tools evaluated **beyond the browser**: their **desktop applications / at the system level** (e.g. Grammarly desktop, the DeepL app, Avast), not only as Firefox extensions. This needs a **system-wide proxy** instead of just the Firefox profile, and possibly **Frida** to handle certificate pinning.
2. **More tools** — add **DeepL** (translator), an **LLM-based tool**, and **Avast** (the "alvast sec" note — Avast has free browser *and* desktop products).
3. **Background behaviour & permissions** — measure **all** traffic a tool generates *on its own*:
   - Does it request or use device permissions (microphone, etc.)?
   - With **no user action**, does it still transmit anything in the background?
4. **USB auto-read test** — plug in a USB stick containing PDFs; does the tool **automatically read them** once connected, and does it transmit? Watch the traffic.
5. **Cloud sync** — briefly investigate whether files saved to **iCloud (Apple)** are exposed.

## Literature
- Read **~20 more related papers** to deepen the related-work grounding.

## Future / thesis
- Potential to **expand this into a Master's thesis next semester** — the department is busy, but he was open to it ("why not").
- Possible direction he floated: **classify the *types* of information** leaked (e.g. names, contact details, financial, IDs), etc.

## My own additions to consider
- A **traffic-over-time graph** (bytes / events per second) to visualise the paste-spike vs any background transmission — pairs naturally with direction #2.

## Action items
- [ ] **Set up desktop / system-level testing** (system-wide proxy; Frida for certificate pinning) — tools must be tested on desktop, **not Firefox-only**.
- [ ] Add **DeepL**, an **LLM tool**, and **Avast** — on both browser and desktop.
- [ ] Design a **background / idle** capture (no user action) + a **permissions** check (mic, etc.).
- [ ] **USB-with-PDFs** auto-read test, with traffic capture.
- [ ] Quick **iCloud** exposure check.
- [ ] Read **~20 related papers** → feed the related-work section.
- [ ] Add an **information-type breakdown** (start from the 12 planted-secret types; optionally add a general PII classifier).
- [ ] Add a **traffic-over-time graph** to the report/dashboard.
- [ ] Continue the **report** in current LaTeX (format is free — IEEE optional).
- [ ] (Optional) Confirm with him whether "alvast sec" meant something other than Avast.
