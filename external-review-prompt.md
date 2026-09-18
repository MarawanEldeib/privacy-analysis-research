# External review prompt (for ChatGPT / DeepSeek / Claude Fable 5.1)

Attach **both** the approved project proposal and `report/main.pdf`, then paste the prompt below.

---

You are an experienced reviewer for a security-and-privacy venue. Attached is a
research-project report titled *"Measuring Data Exposure in LLM-Integrated Productivity
Tools"* (University of Stuttgart, IEEE two-column format, ~12 pages). It is a measurement
study: using an HTTPS man-in-the-middle proxy and a synthetic "confidential memo" seeded
with 12 unique planted secrets (including a UUID canary), it measures how much of a
document common writing/productivity tools transmit by default — across a browser phase
(Grammarly, LanguageTool, vs. a no-extension baseline) and a host phase (Word/Office AI,
DeepL desktop, Edge Copilot, plus passive/negative controls). All test data is synthetic.
I am about to submit it to my supervisor. I have also attached the **approved project
proposal** — the report must deliver what the proposal promised and stay within its scope.

Please review it thoroughly and give specific, actionable feedback, organized as follows:

1. **Proposal alignment** — compare the report against the approved proposal. Does it
   deliver every research question, objective, and deliverable the proposal promised? Flag
   (a) anything promised but missing or under-addressed, (b) anything in the report that
   drifts beyond the proposal's stated scope, and (c) any mismatch between the proposal's
   framing (question, method, expected outcomes) and what the report actually does. Be
   specific about which promise maps to which section.
2. **Add / remove / change** — anything that should be added, removed, or changed before
   submission. Be concrete: name the section, quote the text, and give the exact
   replacement or fix.
3. **Structure** — should any section be reorganized, merged, split, reordered, or
   retitled? Is the overall flow (Intro → Background/Threat Model → Related Work →
   Methodology → Results → Discussion → Limitations → Ethics → Conclusion) the right one?
4. **Figures & tables** — should any figure or table be added, removed, combined, or
   redesigned? Are the current ones necessary, clear, and well-placed? Do any results
   deserve a figure/table they don't have?
5. **Citations** — are any claims under-cited or missing a reference? Are any citations
   weak, unnecessary, or misused? Suggest specific additional references where they'd
   strengthen the work.
6. **Presentation** — for any idea, paragraph, section, figure, table, function/algorithm,
   formula, or the spacing/formatting, show where it could be presented more clearly or
   more professionally, with a concrete before/after where possible.
7. **Clarity questions** — if anything is vague, ambiguous, or unexplained, ask me the
   questions you need answered rather than guessing.
8. **Overall evaluation** — finish with an honest assessment of the research and the study
   as a whole: its contribution, rigor, strengths, weaknesses, and whether it is ready to
   submit (and if not, the top few things to fix first).

Be direct and critical — I want the weaknesses, not reassurance. Distinguish clearly
between (a) must-fix issues, (b) nice-to-have improvements, and (c) optional polish.
