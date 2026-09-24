Apply the following fixes to the attached `main.tex` and `refs.bib` of this PoPETs paper. Apply each edit exactly as written and change nothing else. Each "Find" text appears once in the file. When done, return the full updated `main.tex` and `refs.bib`.

## 1. Author block — add ORCID and email, remove the two TODO comments

**Find:**
```
\author{Marawan Eldeib}
%TODO: get an ORCID number, if you don't already have one
\affiliation{%
  \institution{Master INFOTECH, University of Stuttgart}
  \city{Stuttgart}
  \country{Germany}}
\email{marawan.eldeib@example.org}% TODO: email, better if official like uni-stuttgart.de
```
**Replace with:**
```
\author{Marawan Eldeib}
\orcid{0009-0008-5285-424X}
\affiliation{%
  \institution{Master INFOTECH, University of Stuttgart}
  \city{Stuttgart}
  \country{Germany}}
\email{marawandeep13@gmail.com}
```

## 2. Document class — add `balance=false` (as in the official PoPETs template)

**Find:** `\documentclass[sigconf,anonymous,review]{acmart}`
**Replace with:** `\documentclass[sigconf,anonymous,review,balance=false]{acmart}`

## 3. Fix a broken cross-reference — uncomment `\label{sec:modes}`

Two `\ref{sec:modes}` uses currently point to a commented-out label, so they show as "??".

**Find:**
```
%\subsection{Modes of exposure}
%\label{sec:modes}
```
**Replace with:**
```
%\subsection{Modes of exposure}
\label{sec:modes}
```

## 4. Results — fix the awkward USB/iCloud sentence

**Find:** `It is not. Inserting the USB without opening the file (Process Monitor showed only the Windows indexer and shell probing volume metadata, not the file being read) and dropping the file into iCloud~Drive to sync each transmitted \textbf{no} document content to the writing tools' servers (0/12), even though Grammarly and the other clients were running throughout: the file never entered a surface they watch.`
**Replace with:** `It is not. Inserting the USB without opening the file transmitted \textbf{no} document content (Process Monitor showed only the Windows indexer and shell probing volume metadata, not the file being read), and dropping the file into iCloud~Drive to sync transmitted none either (0/12), even though Grammarly and the other clients were running throughout: the file never entered a surface they watch.`

## 5. Disclosure table — remove the TODO, tighten the caption, use verified vendor paraphrases

Delete this comment line entirely:
```
% TODO: fill Table~\ref{tab:disclosure} with verbatim quotations from the current privacy policy / Web Store disclosure of each vendor, with access dates, before submission.
```

Then **replace the whole `\begin{table} ... \end{table}` block for `tab:disclosure`** with:
```
\begin{table}
\caption{Documented versus measured behaviour per channel. The ``Documented'' column
paraphrases each vendor's cited privacy documentation (access dates in the references); the
``Measured'' column reports this study's findings.}
\label{tab:disclosure}
\small
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{1.9cm}>{\raggedright\arraybackslash}p{2.7cm}>{\raggedright\arraybackslash}p{3.3cm}@{}}
\toprule
\textbf{Channel} & \textbf{Documented} & \textbf{Measured} \\
\midrule
Grammarly ext. & processes the user's text on its servers to provide writing suggestions~\cite{grammarly2025privacy} & whole field (99.0\%) on paste, before any suggestion; account token attached \\
LanguageTool ext. & by default sends text to its servers to be checked and states it is not stored~\cite{languagetool2025privacy} & whole field (91.9\%) on paste, before any suggestion; no account identifier \\
Word connected exp. & experiences that analyse content process it in the cloud and can be turned off in Account Privacy settings~\cite{microsoft2026connectedexp} & 96.8\% on open, no edit or submission; 0\% with the setting off \\
Grammarly desktop & offers suggestions in supported desktop applications~\cite{grammarly2025privacy} & 94.2\% from a Protected View window, no user action \\
Edge Copilot & processes page content the user provides when Copilot is invoked~\cite{microsoft2026copilotprivacy} & $\geq$76.9\% and all secrets, before the model's reply declined to reveal them \\
\bottomrule
\end{tabular}
\end{table}
```

## 6. Add two missing citations to `refs.bib`

The draft cites `nih2023genai` and `incogni2026ranking` but they are not in `refs.bib`. Add:
```
@misc{nih2023genai,
  author       = {{National Institutes of Health}},
  title        = {The Use of Generative Artificial Intelligence Technologies is Prohibited for the {NIH} Peer Review Process},
  howpublished = {NIH Guide Notice NOT-OD-23-149},
  year         = {2023},
  note         = {Accessed 2026-09-22},
  url          = {https://grants.nih.gov/grants/guide/notice-files/NOT-OD-23-149.html}
}

@misc{incogni2026ranking,
  author       = {{Incogni}},
  title        = {Ranking {AI}-Powered {Chrome} Extensions by Privacy Risk in 2026},
  howpublished = {Incogni Research Report},
  year         = {2026},
  note         = {Accessed 2026-09-22},
  url          = {https://blog.incogni.com/chrome-extensions-privacy-2026/}
}
```
