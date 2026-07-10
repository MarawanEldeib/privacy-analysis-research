# Narrative Walkthrough — The Story of the Project

A documented case study: what this project set out to measure, how the method was
designed, what actually happened along the way (including the dead ends), and what
the evidence finally showed. Where the [Reproduction Guide](Reproduction-Guide.md)
tells you *what to do* and the [Technical Walkthrough](Technical-Walkthrough.md)
explains *how the machinery works*, this document tells you *why the study looks
the way it does*.

---

## 1. The question

It starts with an ordinary situation. A colleague sends you a confidential file
and says, plainly, "don't share this with any AI tools." You wouldn't paste it
into ChatGPT. But you might have a grammar-checker extension installed — the kind
millions of people run and forget about — quietly watching every text field in
your browser. You paste a paragraph of that document into an email reply. Did
anything just leave your machine?

That is the whole project. Not an exploit, not a hack — just a measurement of
what *default-configuration* writing assistants do with text you never
consciously "sent" anywhere. The research question was framed as:

> *How does user data exposure differ across LLM-integrated productivity tools
> during controlled use?*

The expected shape of an answer, per tool, was simple: "Tool X transmitted Y % of
the document, and here is how confident we are in that number."

---

## 2. Designing a measurement you can trust

The hard part of a study like this is not catching a tool in the act — it's being
able to *prove* what you caught, and to prove it wasn't an accident of your setup.
Several design decisions came out of that concern.

**Synthetic bait, not real data.** The test document is a fabricated
"confidential memo" — 2,065 characters, 245 words — seeded with **12 unique
fictional identifiers**: names (Helena Voss, Theodora Baumgartner-Klein), a fake
email and phone number, project and reference codes, and, most importantly, a
**UUID canary**: `CANARY-BC267061-67DC-485B-8E51-6F5494765CAB`. None of these
strings exist anywhere on the internet. So if the canary shows up in intercepted
traffic, there is no innocent explanation — it came from our document. This turns
a fuzzy question ("did some of the text leak?") into a binary one you can put in a
report.

**A control, so the number means something.** Every tool is measured against a
**no-extension baseline**: the exact same browser, the exact same page, the exact
same paste — just no writing assistant installed. Whatever the baseline transmits
is ordinary browser background noise, and it gets subtracted. When the baseline
reads 0 % and a tool reads 99 %, the extension is unambiguously the cause.

**A noise-free stage.** Rather than test inside Gmail or Google Docs — full of
third-party scripts and analytics — the document is pasted into a bare local HTML
page with a single text box and nothing else. The extension behaves the same way
it would on any site (its manifest says it attaches to every text field), but
there is no other traffic to disentangle.

**Paste, not typing.** The scenario is "you received a document," which is
paste-shaped, not "you're writing something fresh." Pasting also avoids the
keystroke-timing randomness that would make repeated runs inconsistent. Five runs
per tool, identical each time, so the spread across runs becomes a measure of how
reproducible the result is.

**See inside HTTPS, honestly.** Everything modern is encrypted, so the study uses
mitmproxy as a man-in-the-middle with its certificate trusted inside each test
profile. Crucially, when a connection *can't* be intercepted (certificate
pinning), that is counted and reported rather than hidden — so any exposure figure
is an honest lower bound, never an inflated one.

---

## 3. What the tool list went through

The scope did not arrive fully formed. It moved, and the movement is part of the
story.

The professor's original illustrative example was **Grammarly** — the archetypal
"always-on" assistant. To make the finding more than an anecdote about one
product, the plan grew into a **2×2 design**: two grammar checkers (Grammarly,
ProWritingAid) and two paraphrasers (Wordtune, QuillBot), so the study could say
"*both* checkers and *both* paraphrasers behaved this way" — replication, not a
single data point. That was a deliberate scoping choice, not a requirement handed
down.

Then reality pushed back on three of the four candidates.

---

## 4. The dead ends (and why they matter)

Documenting what *didn't* work is not filler — it's what separates a measurement
from a lucky screenshot. Three tools were investigated and dropped, each for a
different, instructive reason.

**ProWritingAid — the tool that wouldn't bite.** Its extension is genuine and
installed cleanly, and it connected to `api.prowritingaid.com`. But on the
controlled test field it only ever sent tiny 11–32 byte heartbeats — never the
document. It turned out not to attach to a plain `<textarea>` the way Grammarly
does; it wants a rich editor. A `contenteditable` box was added to the test page
to give it one, and it still didn't transmit the document. Rather than bend the
protocol tool-by-tool (which would wreck comparability), ProWritingAid was
recorded as a limitation and set aside.

**QuillBot — no door to knock on.** The intended paraphraser replication partner
simply has **no official Firefox extension** — it ships on Chrome only. Since the
entire method depends on one identical Firefox-based capture protocol for every
tool, QuillBot couldn't be tested without breaking that uniformity. Dropped.

**Wordtune — the impostor.** This is the cautionary tale of the project. The
obvious Firefox listing at the `/wordtune/` slug *looked* right, but the publisher
was "Akajan Burno," with a support link pointing to a scam domain. Testing showed
it echoed the typed text back locally and never contacted a server at all — a
**clone**, not the real product. The genuine Wordtune lives at
`/wordtune-ai-writing-assistant/`, published by AI21 Labs. But even the real one
didn't fit: it is an **on-demand** tool. It transmits only when the user actively
selects text and clicks "Rewrite" — nothing leaves on a background paste. On top
of that, its backend threw repeated `403`s at an entitlement wall and the sidebar
never finished loading, so a rewrite couldn't even be driven. Dropped — but with a
lesson attached: **always verify an extension's publisher before installing it.**

Two corrections belong in this section honestly. Early on, the browser *appeared*
to show Wordtune reflecting the document, which looked like a catch — but the
authoritative capture (0 %, no server traffic) was what mattered, and it said
nothing had left. And the "auto-paste" approach was briefly blamed for a missed
capture before the real cause was found: the paste had landed, but without a DOM
input event the extension never ingested it. Trusting the capture over the
appearance, and the event model over the assumption, is what kept the results
clean.

---

## 5. What the dropping left behind — a cleaner result

Losing three candidates could have looked like a setback. Instead it sharpened the
finding into something more precise: tools fall into **two exposure classes**.

- **Automatic / background transmitters** send the document to their servers with
  no user action beyond pasting. This is the pure silent-exposure threat the study
  is about. Grammarly and LanguageTool are both here.
- **On-demand transmitters** only send text the user actively submits. Under this
  study's exact threat model — extension running in the background, user pastes a
  document they were told not to share — this class *doesn't* leak. Wordtune is
  here.

So the final design is two independent **automatic** grammar checkers versus a
control — and the interesting nuance that not every "AI writing tool" behaves the
same way. That distinction is a genuine result to report, not a gap.

---

## 6. What happened when the captures ran

With Grammarly active, pasting the memo produced an immediate `[! EXPOSURE]` line
in the recorder. Across five runs it transmitted a **median ~99 %** of the
document's characters and **all 12 planted secrets, including the canary**, to its
servers — over WebSocket, automatically, seconds after the paste, with no click.

LanguageTool — a completely independent product, and one that needs **no account
at all** — did the same thing: **~92 %** of the document and **all 12 secrets**
across its five runs. Two unrelated vendors, the same behavior, which is exactly
the replication the 2×2 design was chasing (just within one class instead of two).

The baseline, run three times with no extension, transmitted **0 %** and **0
secrets** — confirming both that the browser itself is innocent and that the
interception was genuinely working.

---

## 7. What it means

The number that matters isn't really the percentage — it's the canary. A single
unique token that existed only inside a document marked "DO NOT FORWARD" was found
sitting in traffic bound for two companies' servers, put there by software the
user installed once and forgot. The tools are doing exactly what they were
designed to do; nothing here is a vulnerability. The finding is about the gap
between that design and what a user, told "don't share this with AI," would
reasonably expect to have happened when they simply pasted a paragraph.

The methodology is deliberately transparent and conservative: synthetic data, a
subtracted baseline, an honest accounting of traffic that couldn't be decrypted, a
headline built on an unforgeable canary rather than a fuzzy percentage, and a
documented trail of every tool that was tried and set aside. That trail — the
impostor extension, the tool that wouldn't attach, the paraphraser with no Firefox
door — is not the mess around the result. It *is* the result: a careful account of
what these tools do by default, and of how easy it is to be misled if you don't
check.

---

*Companion documents: [`Reproduction-Guide.md`](Reproduction-Guide.md) to run it
yourself, [`Technical-Walkthrough.md`](Technical-Walkthrough.md) for how the
capture and analysis code works, and [`QA-Professor.md`](QA-Professor.md) for the
decision log behind the scope.*
