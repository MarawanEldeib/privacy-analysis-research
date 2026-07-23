// Progress-review deck for Prof. Marco Aiello — built with pptxgenjs
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE"; // 13.333 x 7.5

// ---- palette ----
const NAVY = "16233D";   // dark background
const NAVY2 = "22335A";  // dark card
const INK  = "1A2438";   // dark text on light
const RED  = "B23A48";   // "leak" accent
const TEAL = "1C7293";   // method
const SAFE = "2A9D8F";   // baseline / safe
const ICE  = "CADCFC";
const MUTE = "6B7280";
const CARD = "F4F6FA";
const LINE = "E3E8F0";
const WHITE = "FFFFFF";
const GOLD = "E0A800";

const HFONT = "Cambria";     // serif headers
const BFONT = "Calibri";     // sans body
const MONO = "Consolas";

const W = 13.333, H = 7.5;
let N = 0;

function pageNum(s, dark) {
  N++;
  s.addText(String(N), { x: W - 0.7, y: H - 0.45, w: 0.4, h: 0.3, fontSize: 10,
    color: dark ? "8EA0C0" : MUTE, align: "right", fontFace: BFONT, margin: 0 });
  s.addText("Data Exposure in LLM-Integrated Tools", { x: 0.5, y: H - 0.45, w: 6, h: 0.3,
    fontSize: 9, color: dark ? "8EA0C0" : MUTE, align: "left", fontFace: BFONT, margin: 0 });
}

// number-in-circle
function circle(s, x, y, d, fill, label, tcol) {
  s.addShape(p.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill } });
  s.addText(label, { x, y, w: d, h: d, align: "center", valign: "middle", fontSize: d > 0.7 ? 18 : 13,
    bold: true, color: tcol || WHITE, fontFace: BFONT, margin: 0 });
}

function title(s, t, col) {
  s.addText(t, { x: 0.6, y: 0.45, w: W - 1.2, h: 0.9, fontSize: 32, bold: true,
    color: col || INK, fontFace: HFONT, align: "left", margin: 0 });
}

function card(s, x, y, w, h, fill) {
  s.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08,
    fill: { color: fill || CARD }, line: { color: LINE, width: 1 },
    shadow: { type: "outer", color: "9AA5B5", blur: 6, offset: 2, angle: 90, opacity: 0.35 } });
}

// ============ SLIDE 1 — TITLE (dark) ============
let s = p.addSlide(); s.background = { color: NAVY };
s.addText("PROGRESS REVIEW  ·  JULY 2026", { x: 0.8, y: 1.5, w: 11, h: 0.4, fontSize: 15,
  color: ICE, bold: true, charSpacing: 3, fontFace: BFONT, margin: 0 });
s.addText("Measuring Data Exposure in LLM-Integrated Productivity Tools", { x: 0.8, y: 2.0, w: 11.7, h: 1.6,
  fontSize: 32, bold: true, color: WHITE, fontFace: HFONT, lineSpacingMultiple: 1.05, margin: 0 });
s.addText("How much of a confidential document do writing-assistant browser extensions silently send to their servers?",
  { x: 0.8, y: 4.15, w: 11.2, h: 0.8, fontSize: 17, italic: true, color: ICE, fontFace: BFONT, margin: 0 });
s.addText([{ text: "Marawan Eldeib", options: { bold: true, color: WHITE } },
           { text: "   ·   Matrikelnummer 3764796   ·   Supervisor: Prof. Marco Aiello", options: { color: "8EA0C0" } }],
  { x: 0.8, y: 6.5, w: 11.5, h: 0.5, fontSize: 14, fontFace: BFONT, margin: 0 });
s.addNotes("Progress review with Prof. Aiello. Goal: show what I built and found in ~3 months and get guidance on scope and next steps.");

// ============ SLIDE 2 — WHY IT MATTERS (light, big stats) ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "Why this matters");
const stats = [
  ["40M+", "daily Grammarly users", RED],
  ["96%", "of the Fortune 500 use it", TEAL],
  ["99%", "of enterprise users run ≥1 browser extension", NAVY2],
];
let sx = 0.6;
stats.forEach(([big, lab, col], i) => {
  const x = 0.6 + i * 4.15;
  card(s, x, 1.7, 3.75, 2.5);
  s.addText(big, { x: x, y: 1.95, w: 3.75, h: 1.2, align: "center", fontSize: 60, bold: true, color: col, fontFace: HFONT, margin: 0 });
  s.addText(lab, { x: x + 0.2, y: 3.15, w: 3.35, h: 1.0, align: "center", fontSize: 15, color: INK, fontFace: BFONT, margin: 0 });
});
s.addText("These tools work by sending the text you type or paste to their own servers for analysis. The processing is server-side — so the content must leave your machine. Most users never see it happen.",
  { x: 0.6, y: 4.45, w: 12.1, h: 0.95, fontSize: 16, color: INK, fontFace: BFONT, margin: 0 });
s.addShape(p.ShapeType.roundRect, { x: 0.6, y: 5.5, w: 12.1, h: 0.9, rectRadius: 0.08, fill: { color: "FBEDED" } });
s.addText([{ text: "And by their own policies:  ", options: { bold: true, color: RED } },
  { text: "Grammarly keeps your text and, for individual accounts, trains its models on it by default. LanguageTool does neither.", options: { color: INK } }],
  { x: 0.95, y: 5.5, w: 11.4, h: 0.9, valign: "middle", fontSize: 14.5, fontFace: BFONT, margin: 0 });
s.addText("Sources: Grammarly & LanguageTool privacy policies (read July 2026); LayerX 2026.",
  { x: 0.6, y: 6.62, w: 12, h: 0.3, fontSize: 10, italic: true, color: MUTE, fontFace: BFONT, margin: 0 });
s.addNotes("Set the stakes: these tools are everywhere, they work by sending your text to their servers, and by their own policies some keep it and train on it.");

pageNum(s);

// ============ SLIDE 3 — QUESTION & OBJECTIVES ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "The question");
card(s, 0.6, 1.6, 12.1, 1.4, "EEF3FB");
s.addText("How does user data exposure differ across LLM-integrated productivity tools during controlled use?",
  { x: 0.95, y: 1.6, w: 11.4, h: 1.4, valign: "middle", fontSize: 22, italic: true, bold: true, color: NAVY2, fontFace: HFONT, margin: 0 });
const objs = [
  ["1", "Define a controlled setup for evaluating these tools"],
  ["2", "Measure user data exposure during tool use"],
  ["3", "Compare exposure across tools under identical conditions"],
  ["4", "Summarise each tool with a clear exposure + confidence assessment"],
];
objs.forEach(([n, t], i) => {
  const y = 3.4 + i * 0.92;
  circle(s, 0.7, y, 0.6, TEAL, n);
  s.addText(t, { x: 1.5, y: y, w: 10.9, h: 0.6, valign: "middle", fontSize: 17, color: INK, fontFace: BFONT, margin: 0 });
});
s.addText("From the project proposal", { x: 0.6, y: 6.7, w: 6, h: 0.3, fontSize: 10, italic: true, color: MUTE, fontFace: BFONT, margin: 0 });
s.addNotes("State the research question and the four objectives from my proposal. Stress differ across tools and controlled use.");

pageNum(s);

// ============ SLIDE 5 — PIPELINE ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "How the measurement works");
const steps = [
  ["1", "Plant", "12 unique secrets +\na UUID canary in a\nsynthetic memo", RED],
  ["2", "Paste", "into a controlled\nfield with one tool's\nextension active", TEAL],
  ["3", "Intercept", "mitmproxy decrypts\nthe outbound HTTPS/\nWebSocket traffic", NAVY2],
  ["4", "Measure", "search traffic for the\ncanary + how much of\nthe document appears", GOLD],
  ["5", "Compare", "against a no-extension\nbaseline to subtract\nbrowser noise", SAFE],
];
steps.forEach(([n, h, d, col], i) => {
  const x = 0.55 + i * 2.5;
  card(s, x, 1.9, 2.3, 3.6);
  circle(s, x + 0.85, 2.15, 0.6, col, n);
  s.addText(h, { x: x, y: 2.95, w: 2.3, h: 0.5, align: "center", fontSize: 18, bold: true, color: col, fontFace: HFONT, margin: 0 });
  s.addText(d, { x: x + 0.12, y: 3.5, w: 2.06, h: 1.9, align: "center", fontSize: 12.5, color: INK, fontFace: BFONT, lineSpacingMultiple: 1.05, margin: 0 });
});
s.addText([{ text: "The canary is the key idea: ", options: { bold: true, color: INK } },
  { text: "a string that exists nowhere else, so finding it in the traffic is undeniable proof the document left the machine.", options: { color: INK } }],
  { x: 0.6, y: 5.9, w: 12.1, h: 0.9, fontSize: 16, fontFace: BFONT, margin: 0 });
s.addNotes("Walk the five steps: plant secrets plus a canary, paste into a clean field, mitmproxy decrypts the traffic, search for the canary and measure coverage, compare against a no-extension baseline.");

pageNum(s);

// ============ SLIDE 6b — TOOLS / MITMPROXY ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "The tools — mitmproxy & the CA certificate");
const boxes = [
  ["Firefox", "test profile —\ntrusts the mitmproxy CA", CARD, INK, LINE],
  ["mitmproxy 12.2.3", "decrypts HTTPS / WebSocket\n+ runs the capture add-on", "EAF1F5", TEAL, TEAL],
  ["Tool servers", "Grammarly /\nLanguageTool", CARD, INK, LINE],
];
boxes.forEach(([h,d,bg,tc,ln],i)=>{
  const x=0.6+i*4.2;
  s.addShape(p.ShapeType.roundRect,{ x, y:1.85, w:3.7, h:1.85, rectRadius:0.08, fill:{ color:bg }, line:{ color:ln, width:1.2 } });
  s.addText(h,{ x, y:2.05, w:3.7, h:0.5, align:"center", fontSize:17, bold:true, color:tc, fontFace:HFONT, margin:0 });
  s.addText(d,{ x:x+0.2, y:2.62, w:3.3, h:1.0, align:"center", fontSize:12.5, color:INK, fontFace:BFONT, lineSpacingMultiple:1.05, margin:0 });
});
s.addText("→",{ x:4.3, y:1.85, w:0.5, h:1.85, align:"center", valign:"middle", fontSize:30, bold:true, color:MUTE, fontFace:BFONT, margin:0 });
s.addText("→",{ x:8.5, y:1.85, w:0.5, h:1.85, align:"center", valign:"middle", fontSize:30, bold:true, color:MUTE, fontFace:BFONT, margin:0 });
s.addShape(p.ShapeType.roundRect,{ x:0.6, y:4.1, w:12.1, h:1.15, rectRadius:0.08, fill:{ color:"EEF3FB" } });
s.addText([{ text:"The CA (certificate authority):  ", options:{ bold:true, color:NAVY2 } },{ text:"mitmproxy makes its own certificate, and we trust it only inside the test profile — so the browser lets us read its own encrypted traffic. Legitimate because it is our machine, our browser, our certificate.", options:{ color:INK } }],
  { x:0.95, y:4.1, w:11.4, h:1.15, valign:"middle", fontSize:14.5, fontFace:BFONT, lineSpacingMultiple:1.1, margin:0 });
const chips=["Kali Linux VM","Isolated Firefox profiles","mitmproxy 12.2.3","Python (stdlib) analyzer"];
let cx=0.6;
chips.forEach((c)=>{
  const w=0.4+c.length*0.115;
  s.addShape(p.ShapeType.roundRect,{ x:cx, y:5.65, w, h:0.55, rectRadius:0.25, fill:{ color:"F0F2F6" }, line:{ color:LINE, width:1 } });
  s.addText(c,{ x:cx, y:5.65, w, h:0.55, align:"center", valign:"middle", fontSize:12.5, color:INK, fontFace:BFONT, margin:0 });
  cx+=w+0.3;
});
s.addNotes("mitmproxy is an open-source HTTPS proxy that decrypts the traffic. Its certificate is trusted only inside my test Firefox profile, so I can read the browser's own encrypted traffic on my own machine. Supporting tools: Kali Linux, isolated profiles, a Python analyzer.");
pageNum(s);


// ============ SLIDE 6 — SETUP / RIGOR ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "A controlled, reproducible setup");
const rig = [
  ["Isolated", "Kali Linux VM; a separate Firefox profile per tool, only that tool's extension active"],
  ["Unambiguous", "a synthetic “confidential memo” (2,065 chars) with 12 planted identifiers + a UUID canary"],
  ["Repeatable", "5 runs per tool + 3 baseline runs, an identical locked protocol every time"],
  ["Honest", "a real manual Ctrl+V (a scripted paste doesn’t trigger the tool); un-decryptable traffic is counted, not hidden"],
];
rig.forEach(([hh, d], i) => {
  const y = 1.75 + i * 1.02;
  circle(s, 0.7, y + 0.08, 0.5, TEAL, "✓");
  s.addText([{ text: hh + ":  ", options: { bold: true, color: TEAL } }, { text: d, options: { color: INK } }],
    { x: 1.45, y: y, w: 11.2, h: 0.85, valign: "middle", fontSize: 16.5, fontFace: BFONT, margin: 0 });
});
s.addNotes("Stress the rigour: isolated Kali VM, one tool per profile, decryption trusted only in the test profile, five runs each, and a real manual paste.");

pageNum(s);

// ============ SLIDE 8 — RESULTS + CHART ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "Result: both tools sent the whole document");
const axisY = 5.7, maxH = 3.2;
s.addShape(p.ShapeType.line, { x: 0.7, y: axisY, w: 6.6, h: 0, line: { color: "C7CFDA", width: 1.5 } });
const bars = [["Grammarly", 99.0, RED, "12/12"], ["LanguageTool", 91.9, RED, "12/12"], ["Baseline", 0.0, SAFE, "0/12"]];
bars.forEach(([nm, val, col, sec], i) => {
  const cx = 1.9 + i * 2.05, bw = 1.4;
  const h = maxH * val / 100, by = axisY - h;
  if (val > 0) s.addShape(p.ShapeType.roundRect, { x: cx - bw / 2, y: by, w: bw, h, rectRadius: 0.03, fill: { color: col } });
  s.addText(val.toFixed(1) + "%", { x: cx - 1.1, y: (val > 0 ? by - 0.42 : axisY - 0.5), w: 2.2, h: 0.38, align: "center", fontSize: 16, bold: true, color: INK, fontFace: HFONT, margin: 0 });
  s.addText(sec + " secrets", { x: cx - 1.1, y: (val > 0 ? by + 0.16 : axisY + 0.06), w: 2.2, h: 0.3, align: "center", fontSize: 11.5, bold: true, color: (val > 0 ? WHITE : MUTE), fontFace: BFONT, margin: 0 });
  s.addText(nm, { x: cx - 1.15, y: axisY + 0.42, w: 2.3, h: 0.35, align: "center", fontSize: 13, bold: true, color: INK, fontFace: BFONT, margin: 0 });
});
s.addText([{ text: "Both tools sent 100% of the content and all 12 secrets — ", options: { bold: true, color: INK } }, { text: "the 99 vs 92 gap is whitespace only.", options: { color: MUTE } }],
  { x: 0.5, y: 6.62, w: 7.1, h: 0.35, align: "center", fontSize: 11.5, italic: true, fontFace: BFONT, margin: 0 });
// callouts right
const calls = [
  ["12 / 12", "planted secrets sent — including the canary", RED],
  ["100%", "of traffic was HTTPS; 0 handshakes hidden from us", TEAL],
  ["0.0 pp", "std. deviation — identical on every single run", NAVY2],
];
calls.forEach(([big, lab, col], i) => {
  const y = 1.8 + i * 1.6;
  card(s, 7.5, y, 5.2, 1.4);
  s.addText(big, { x: 7.7, y: y + 0.12, w: 2.0, h: 1.15, valign: "middle", fontSize: 34, bold: true, color: col, fontFace: HFONT, margin: 0 });
  s.addText(lab, { x: 9.7, y: y, w: 2.85, h: 1.4, valign: "middle", fontSize: 14, color: INK, fontFace: BFONT, margin: 0 });
});
s.addNotes("Lead with 12 of 12 secrets, not the percentage. Both tools sent essentially the whole document; 100 percent HTTPS, zero hidden handshakes, identical every run.");

pageNum(s);

// ============ SLIDE 9b — 12 PLANTED SECRETS ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "The 12 planted secrets — all transmitted");
const secrets = [
  ["Helena Voss","name"],
  ["HV-2026-391847","employee ID"],
  ["Theodora Baumgartner-Klein","name"],
  ["theodora.baumgartner@priv-research-demo.invalid","email"],
  ["+49 30 4827-9153","phone number"],
  ["Project Nighthawk-3","project codename"],
  ["XREF-291-ALPHA","document reference"],
  ["NHK3-RES-7741","reserve fund code"],
  ["AC-2026-00293-DELTA","approval code"],
  ["2026-LGL-00847","contract ID"],
  ["DE-291-847-3309","tax registration"],
  ["CANARY-BC267061-67DC-485B-8E51-6F5494765CAB","UUID canary"],
];
secrets.forEach(([val,typ],i)=>{
  const cc=Math.floor(i/6), rr=i%6;
  const x=0.6+cc*6.15, y=1.65+rr*0.82;
  const isC = i===11;
  s.addShape(p.ShapeType.roundRect,{ x, y, w:5.95, h:0.72, rectRadius:0.06, fill:{ color: isC?"FBEDED":CARD }, line:{ color: isC?RED:LINE, width: isC?1.3:1 } });
  s.addText(String(i+1),{ x:x+0.1, y, w:0.5, h:0.72, align:"center", valign:"middle", fontSize:13, bold:true, color: isC?RED:MUTE, fontFace:BFONT, margin:0 });
  s.addText(val,{ x:x+0.65, y:y+0.06, w:5.2, h:0.36, valign:"middle", fontSize: isC?10:11.5, bold:true, color: isC?RED:INK, fontFace:MONO, margin:0 });
  s.addText(typ,{ x:x+0.65, y:y+0.42, w:5.2, h:0.26, valign:"middle", fontSize:10, color:MUTE, fontFace:BFONT, margin:0 });
});
s.addText([{ text:"12 / 12 transmitted", options:{ bold:true, color:RED } },{ text:"  by both Grammarly and LanguageTool — including the canary.", options:{ color:INK } }],
  { x:0.6, y:6.75, w:12.1, h:0.3, fontSize:13, fontFace:BFONT, margin:0 });
s.addNotes("Show what was planted and that all twelve were transmitted by both tools. Makes 12 of 12 concrete.");
pageNum(s);


// ============ SLIDE 9 — THE CANARY (dark) ============
s = p.addSlide(); s.background = { color: NAVY };
title(s, "The proof: one unforgeable token", WHITE);
s.addShape(p.ShapeType.roundRect, { x: 0.9, y: 2.2, w: 11.5, h: 1.15, rectRadius: 0.08, fill: { color: "0C1526" }, line: { color: RED, width: 1.5 } });
s.addText("CANARY-BC267061-67DC-485B-8E51-6F5494765CAB", { x: 0.9, y: 2.2, w: 11.5, h: 1.15,
  align: "center", valign: "middle", fontSize: 22, bold: true, color: "6FD3B8", fontFace: MONO, margin: 0 });
s.addText("This string exists nowhere else on the internet.", { x: 0.9, y: 3.7, w: 11.5, h: 0.6, align: "center",
  fontSize: 20, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
s.addText("It appeared in the traffic bound for the tool’s servers, seconds after an ordinary paste. There is no innocent explanation — it could only have come from the confidential document. This is the headline result: not a percentage, but undeniable, per-secret proof.",
  { x: 1.4, y: 4.5, w: 10.5, h: 1.8, align: "center", fontSize: 17, color: ICE, fontFace: BFONT, lineSpacingMultiple: 1.2, margin: 0 });
s.addNotes("The proof. This unique string exists nowhere else, yet it appeared in the traffic seconds after a paste. Undeniable evidence the document left the machine.");

pageNum(s, true);

// ============ SLIDE 11 — RELATED WORK / NOVELTY ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "Where this sits in the research");
card(s, 0.6, 1.7, 12.1, 2.2, CARD);
s.addText("PRIOR WORK", { x: 0.9, y: 1.85, w: 5, h: 0.35, fontSize: 13, bold: true, color: MUTE, charSpacing: 2, fontFace: BFONT, margin: 0 });
s.addText([
  { text: "How MANY extensions leak: ", options: { bold: true, color: INK } },
  { text: "Starov (WWW’17), Mystique (CCS’18, 181k extensions), Arcanum (USENIX’24 — 3,028 extensions, up to 144M users). ", options: { color: INK } },
  { text: "Auditing AI assistants: ", options: { bold: true, color: INK } },
  { text: "Vekaria “Big Help or Big Brother?” (USENIX’25) used the same MITM-decryption method on GenAI assistants.", options: { color: INK } },
], { x: 0.9, y: 2.25, w: 11.5, h: 1.55, fontSize: 15.5, fontFace: BFONT, lineSpacingMultiple: 1.15, margin: 0 });
card(s, 0.6, 4.1, 12.1, 2.3, "EAF6F1");
s.addText("MY CONTRIBUTION", { x: 0.9, y: 4.25, w: 6, h: 0.35, fontSize: 13, bold: true, color: SAFE, charSpacing: 2, fontFace: BFONT, margin: 0 });
s.addText([
  { text: "No one has measured HOW MUCH of a specific confidential document writing assistants transmit, with per-secret canary proof. ", options: { bold: true, color: INK } },
  { text: "This is the writing-assistant, canary-proven complement to Vekaria — the same interception principle, narrowed to one reproducible threat model and strengthened so every individual leak is provable, not just observed in aggregate.", options: { color: INK } },
], { x: 0.9, y: 4.65, w: 11.5, h: 1.65, fontSize: 15.5, fontFace: BFONT, lineSpacingMultiple: 1.15, margin: 0 });
s.addNotes("Prior work measured how many extensions leak or audited AI assistants with the same method. My contribution is how much of a specific document, with canary proof.");

pageNum(s);

// ============ SLIDE 12 — 3 MONTHS OF WORK (timeline) ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "Three months of work");
const tl = [
  ["Apr 13", "Project kickoff: proposal, background reading, threat model & scope"],
  ["May", "Environment: Kali Linux + mitmproxy; synthetic test document with planted secrets"],
  ["May–Jun", "Built the capture add-on + analyzer; three internal review passes fixing the instrument"],
  ["Jun–Jul", "Data collection: Grammarly, LanguageTool, baseline (13 runs); analysis + dashboard"],
  ["Jul", "Full LaTeX report, cited related-work research, and a managed reference library"],
];
tl.forEach(([m, d], i) => {
  const y = 1.62 + i * 0.9;
  circle(s, 0.75, y, 0.58, i === 4 ? SAFE : TEAL, String(i + 1));
  if (i < 4) s.addShape(p.ShapeType.line, { x: 1.04, y: y + 0.58, w: 0, h: 0.32, line: { color: LINE, width: 2 } });
  s.addText(m, { x: 1.55, y: y, w: 1.75, h: 0.58, valign: "middle", fontSize: 15, bold: true, color: TEAL, fontFace: HFONT, margin: 0 });
  s.addText(d, { x: 3.35, y: y, w: 9.4, h: 0.58, valign: "middle", fontSize: 14.5, color: INK, fontFace: BFONT, margin: 0 });
});
card(s, 0.6, 6.05, 12.1, 0.95, "EEF3FB");
s.addText([{ text: "Artifacts produced:  ", options: { bold: true, color: NAVY2 } },
  { text: "~2,000 lines of Python  ·  13 timestamped capture runs  ·  15+ documents  ·  a compiled research report  ·  a cited literature digest", options: { color: INK } }],
  { x: 0.9, y: 6.05, w: 11.5, h: 0.95, valign: "middle", fontSize: 14.5, fontFace: BFONT, margin: 0 });
s.addNotes("Show sustained work from 13 April: proposal, environment, building the pipeline, data collection, report and research. I have also started drafting the written report and will expand it once I have your feedback.");

pageNum(s);

// ============ SLIDE 13 — PROPOSAL ALIGNMENT ============
s = p.addSlide(); s.background = { color: WHITE };
title(s, "Against the proposal: delivered");
card(s, 0.6, 1.75, 12.1, 4.7, "EAF6F1");
s.addText("DELIVERED", { x: 0.9, y: 1.95, w: 5, h: 0.4, fontSize: 14, bold: true, color: SAFE, charSpacing: 2, fontFace: BFONT, margin: 0 });
const done = ["Controlled setup + identical input", "Exposure measured (content, bytes, requests, domains)", "No-extension baseline for comparison", "Per-tool result + confidence (consistency & completeness)", "mitmproxy + Python + JSON, as proposed"];
done.forEach((t, i) => {
  s.addText(t, { x: 1.0, y: 2.6 + i * 0.8, w: 11.5, h: 0.7, valign: "middle", fontSize: 15, color: INK, fontFace: BFONT, bullet: { characterCode: "2713", indent: 18 }, margin: 0 });
});
s.addText("Verdict: the method fully meets the proposal as specified.",
  { x: 0.6, y: 6.65, w: 12, h: 0.3, fontSize: 11.5, italic: true, color: MUTE, fontFace: BFONT, margin: 0 });
s.addNotes("Map what I built to each proposal requirement. All met. Breadth of scope is the discussion for today.");

pageNum(s);

// ============ SLIDE 15 — QUESTIONS FOR PROFESSOR (dark) ============
s = p.addSlide(); s.background = { color: NAVY };
title(s, "Where I’d value your guidance", WHITE);
const q = [
  "Is the methodology sound as it stands — anything you'd add or change in how I measured it?",
  "Is this the scope you expected — or did you have other tools or directions in mind (e.g. a desktop app or an AI-assistant extension)?",
  "Is there a required report template or format — length, structure, citation style — and do you need the standard declaration of originality?",
];
q.forEach((t, i) => {
  const y = 1.95 + i * 1.5;
  circle(s, 0.8, y, 0.55, TEAL, "?");
  s.addText(t, { x: 1.65, y: y - 0.1, w: 11.0, h: 1.1, valign: "middle", fontSize: 18, color: WHITE, fontFace: BFONT, lineSpacingMultiple: 1.08, margin: 0 });
});
s.addNotes("My main ask: narrow to browser grammar checkers, or broaden to a different integration type such as a desktop app or an AI assistant.");

pageNum(s, true);

// ============ SLIDE 16 — THANK YOU (dark) ============
s = p.addSlide(); s.background = { color: NAVY };
s.addText("Thank you", { x: 0.8, y: 2.6, w: 11.7, h: 1.2, fontSize: 48, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
s.addText("Questions & discussion", { x: 0.85, y: 3.9, w: 11, h: 0.6, fontSize: 22, italic: true, color: ICE, fontFace: BFONT, margin: 0 });
s.addText([{ text: "Marawan Eldeib", options: { bold: true, color: WHITE } },
  { text: "   ·   marawandeep13@gmail.com   ·   Matrikelnummer 3764796", options: { color: "8EA0C0" } }],
  { x: 0.85, y: 5.0, w: 11.5, h: 0.5, fontSize: 14, fontFace: BFONT, margin: 0 });

s.addNotes("Thank him and invite questions. If there is time, propose a standing bi-weekly slot.");

p.writeFile({ fileName: "/sessions/kind-jolly-planck/mnt/Research Project - Privacy analysis/presentation/Progress-Review.pptx" })
  .then(f => console.log("WROTE", f))
  .catch(e => { console.error("ERR", e); process.exit(1); });
