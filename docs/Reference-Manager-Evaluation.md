# Reference Manager Evaluation — Mendeley vs. the current Zotero workflow

**Question (from a friend's suggestion):** should this project use **Mendeley** for
reference management and citations?

**Short answer: No — keep the current setup.** For *this* project's LaTeX pipeline,
Mendeley is a downgrade, and there's a privacy irony worth noting. Details below.

Reviewed 2026-09-06.

## What we already use
Zotero + the **Better BibTeX** plugin, auto-exporting to `report/refs.bib` with pinned
citation keys, which `report/main.tex` cites directly. This was set up deliberately
(commit 2026-07-14, "switch refs.bib to Zotero/Better BibTeX auto-export (keys
preserved)"). The `.bib` file stays in sync automatically whenever the library changes.

## What Mendeley is in 2026
- **Mendeley Reference Manager** is the current app; the old **Mendeley Desktop was
  retired in September 2022**.
- Owned by **Elsevier**; cloud-first, with newer AI-assisted reading/summary features, a
  polished built-in PDF reader, watched-folder sync, and Notebook annotation synthesis.
- **2 GB** free web storage.
- Exports BibTeX (auto-generated `AuthorYear` keys), and has a browser Web Importer.

## The decisive point for a LaTeX project
The new Mendeley Reference Manager **removed automatic BibTeX file syncing** — the very
feature that made Mendeley Desktop usable with LaTeX. In the current version you must
**manually re-export** a standalone `.bib` every time your library changes, and it does
**not** stay in sync. Our Zotero + Better BibTeX setup does exactly the opposite: it keeps
`refs.bib` continuously up to date with stable keys, with no manual step. Switching to
Mendeley would replace an automated pipeline with a manual, error-prone one.

## Head-to-head (for this project's needs)

| Dimension | Zotero + Better BibTeX (current) | Mendeley Reference Manager |
|---|---|---|
| **Auto `.bib` sync for LaTeX** | **Yes** — continuous, pinned keys | **No** — manual re-export, standalone file |
| Cost / storage | Free; unlimited **local** storage | Free; **2 GB** cloud cap |
| Open source / auditable | **Yes** (GitHub) | No — closed, Elsevier-owned |
| Citation styles | 9,000+ CSL styles | More limited |
| Ownership / data use | Non-profit; not Elsevier | **Elsevier; uses Mendeley data for analytics** |
| PDF reader / annotation | Good (getting better) | **Nicer built-in reader**, smooth annotation sync |
| AI reading features | Fewer built-in | Newer AI summaries / Notebook synthesis |
| Migration cost now | Zero (already set up, 22 refs in `refs.bib`) | Re-import library, rewire the LaTeX export |

## The privacy irony
This is a project **about data exposure by productivity tools**. Mendeley is owned by
Elsevier and **uses library/usage data for analytics products**. Adopting a
telemetry-heavy, closed tool as the backbone of a privacy-exposure study is a poor look
and a small but real "do as I say, not as I do." Zotero (open-source, offline-first,
auditable) is the on-message choice.

## Verdict
- **Keep Zotero + Better BibTeX** as the citation source of truth. It is strictly better
  for a LaTeX/BibTeX workflow, free with unlimited local storage, open-source, and already
  wired into `refs.bib`. Switching would add manual work and lose auto-sync.
- **If you like Mendeley's PDF reader**, it's fine to use it *only* as a reader/annotator
  for papers — but do **not** make it the citation manager, and don't route `refs.bib`
  through it. Keeping two sources of truth for references is how bibliographies drift.
- Net: your friend's advice is reasonable in general (Mendeley is a fine tool), but for
  *this* project and workflow it doesn't beat what you already have.

## Sources
- Mendeley → BibTeX/LaTeX export (standalone, no auto-update) — https://libguides.usask.ca/c.php?g=218034&p=1446316 · https://subjectguides.lib.neu.edu/mendeley/latex
- No BibTeX sync in Reference Manager; Desktop retired Sept 2022 — https://researchguides.uoregon.edu/Mendeley/desktop · https://sarahlawrence.libguides.com/Mendeley/Changes
- Zotero vs Mendeley 2026 (open-source, storage, Elsevier data-use, styles) — https://researchgold.org/blog/zotero-vs-mendeley · https://paperguide.ai/blog/zotero-vs-mendeley/
- Best reference managers for LaTeX/BibTeX 2026 — https://tesify.app/best-reference-managers-latex-bibtex-2026/
