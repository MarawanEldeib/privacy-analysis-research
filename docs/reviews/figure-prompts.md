# ChatGPT prompts to generate the two merged figures

These replace the current four diagrams (old Figs 1–4). Ask ChatGPT to output each as a
downloadable high-resolution PNG (and SVG if it can). Style notes for both: clean, flat,
vector-style, restrained palette (blue = infrastructure, red = leak/vendor, grey = arrows),
generous whitespace, legible sans-serif, **no large title bar embedded in the image** (the
paper's caption provides the title), landscape, roughly 1600×700 px, suitable for a
two-column IEEE page (will be placed full width).

---

## PROMPT 1 — "Experimental setup (both phases)"

> Create a single clean, flat vector-style diagram (landscape, ~1600×700, transparent or
> white background, no big title text inside the image) showing two side-by-side panels that
> share the same interception core.
>
> **Left panel, labelled "Browser phase (Kali Linux VM)":**
> - A document icon labelled "Synthetic memo (12 planted secrets + UUID canary)".
> - An arrow "paste" into a browser window labelled "Firefox 140 ESR — bare localhost page".
> - Inside the browser, a small puzzle-piece labelled "Writing-assistant extension
>   (Grammarly / LanguageTool)".
> - An arrow labelled "HTTPS / WebSocket" from the browser to a central box.
>
> **Right panel, labelled "Host phase (Windows 11)":**
> - Four app tiles: "Microsoft Word (Office AI)", "DeepL desktop", "Edge / Copilot",
>   "Grammarly desktop".
> - An arrow from the apps to a box labelled "System proxy (WinINET + WinHTTP)", with a small
>   note "WinHTTP needed: native apps bypass a browser-only proxy".
> - An arrow from the system proxy to the same central box.
>
> **Central shared box (spanning both panels):** "mitmproxy (127.0.0.1:8080) — HTTPS/WebSocket
> interception". A small check-mark note beside it: "positive control (example.com) confirms
> interception is live". From this box, one arrow to the right labelled "per-host attribution"
> pointing to a stack of vendor-server icons labelled:
> capi.grammarly.com, api.languagetool.org, www2.deepl.com, augloop.svc.cloud.microsoft,
> copilot.microsoft.com.
>
> Keep it uncluttered and professional; no drop-shadow clip-art.

---

## PROMPT 2 — "Exposure-scoring pipeline"

> Create a single clean, flat vector-style horizontal flow diagram (landscape, ~1600×550,
> white/transparent background, no big title text inside the image) with five stages left to
> right, connected by arrows:
>
> 1. "Captured client→server flow" (small caption under it: "HTTP request bodies + client→server
>    WebSocket frames; server responses excluded").
> 2. "Decompress" (caption: "gzip / brotli / zstd").
> 3. "Decode variants" (caption: "plain, URL, JSON, HTML-entity, base64, UTF-16; case-folded,
>    Unicode NFC").
> 4. "Match" (caption: "20-character sliding windows + UUID canary + 12 planted secrets").
> 5. A highlighted result box (red accent): "Character-coverage exposure %  +  secrets x/12
>    +  per-host attribution" (small caption: "each document position counted once").
>
> Do NOT label the output "baseline-subtracted"; the metric is character coverage. Keep the
> style consistent with the setup figure (same fonts/colours). Uncluttered, professional.

---

---

## PROMPT 3 — "Burst timeline" (DATA plot — plot these exact values, do not invent)

> Create a clean, flat vector-style line chart (landscape, ~1500×550, white background, no
> big title inside the image), in the same visual style, fonts, and palette as my other two
> figures (blue = infrastructure, red = leak/vendor). It is a step chart of **cumulative
> outbound tool-host frames** (y) versus **seconds since the first outbound event** (x, from
> 0 to 60). Plot exactly these measured points and hold each line flat to 60 s; do not add,
> smooth, or invent any data:
>
> - **Grammarly (red):** step increments at t = 0.00 s → 1, 0.12 s → 2, 0.44 s → 3,
>   2.44 s → 4, 5.40 s → 5, then flat at 5 until 60 s.
> - **LanguageTool (blue):** two frames at t = 0.00 s → 2, then flat at 2 until 60 s.
>
> x-axis label: "Seconds since first outbound event (60 s capture)". y-axis label:
> "Cumulative outbound tool-host frames". Include a small legend. The point is to show a
> single burst in the first ~5 seconds and then silence for the rest of the 60 s window.
> Use a step (post) interpolation, integer y ticks. Keep it uncluttered and professional.

---

## PROMPT 4 — "Action spectrum" (DATA bar chart — plot these exact values, do not invent)

> Create a clean, flat vector-style horizontal bar chart (portrait-ish, ~1500×950, white
> background, **no title text inside the image** — the paper caption supplies it), in the
> same style/fonts/palette as my other figures. x-axis 0–100, label:
> "Document-content coverage in outbound traffic (%)". One bar per row, in this exact top-to-
> bottom order, with the exact value and run count labelled at the end of each bar as
> "VALUE%  (N=n)". Colour each bar by its interaction class (see legend). Do not add, round,
> or invent any values.
>
> | Row (top to bottom) | Value | N | Class |
> |---|---|---|---|
> | DeepL desktop (paste) | 99.6% | 3 | User-initiated |
> | Grammarly extension (paste) | 99.0% | 5 | Incidental / open-triggered |
> | Word: connected experiences on (open) | 96.8% | 3 | Incidental / open-triggered |
> | Word Protected View + Grammarly desktop | 94.2% | 2 | Incidental / open-triggered |
> | LanguageTool extension (paste) | 91.9% | 5 | Incidental / open-triggered |
> | Edge Copilot (invoked) | 76.9% | 3 | User-initiated |
> | Word: connected experiences off | 0.0% | 1 | Mitigation (setting off) |
> | Edge — PDF open, not invoked | 1.8% | 1 | No document content |
> | PDF in Chrome / Acrobat | 0.0% | 1 | No document content |
> | .txt / .md in Notepad | 0.0% | 1 | No document content |
> | iCloud Drive sync | 0.0% | 1 | No document content |
> | USB inserted, not opened | 0.0% | 1 | No document content |
>
> Legend (four classes, with these colours): Incidental / open-triggered (dark red),
> User-initiated (orange), Mitigation (setting off) (green), No document content (grey).
> Do NOT add a dagger or any lower-bound note in the image (the paper caption states the
> Edge/Copilot lower bound). Keep it uncluttered and professional; 0.0% rows will show as no
> visible bar, which is correct.

### After you generate them
Download both as PNG (SVG too if offered) and drop them into `report/figures/`, e.g.
`fig_setup.png` and `fig_pipeline.png`. Tell me the filenames and I'll wire them into the
LaTeX (replacing the four old figures) and update the captions.
