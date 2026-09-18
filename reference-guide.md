# Reference guide — what each citation is for

Numbered in the order they appear in the report (IEEE numbering, `unsrtnat`). "Role" = why it's cited here.

1. **starov2017extended — "Extended Tracking Powers" (WWW 2017).** Early systematic measurement of how browser extensions leak identifying data beyond their function. *Role:* opens Related Work; establishes extension privacy leakage as a long-studied problem.

2. **weissbacher2017exray — "Ex-Ray" (ACSAC 2017).** A system to detect history-leaking extensions. *Role:* example of prior extension-leak detection.

3. **aggarwal2018ispy — "I Spy with My Little Eye" (EuroS&P 2018).** Analyses and detects "spying" extensions that exfiltrate browsing behaviour. *Role:* prior work on malicious/spying extensions.

4. **chen2018mystique — "Mystique" (CCS 2018).** Scales dynamic taint-tracking to ~182k extensions, flagging thousands that leak sensitive data. *Role:* large-scale precedent and a detection-method lineage.

5. **fass2021doublex — "DoubleX" (CCS 2021).** Static data-flow analysis of extensions at scale. *Role:* the code-analysis complement to runtime measurement.

6. **carlini2012chrome — Chrome extension security architecture (USENIX Sec 2012).** Shows over-broad host permissions undercut Chrome's isolation guarantees. *Role:* explains why "all-sites" permission is the real risk.

7. **pantelaios2020changed — "You've Changed" (CCS 2020).** Benign extensions can turn malicious via later updates. *Role:* justifies runtime measurement over trusting one reviewed snapshot.

8. **nayak2024experimental — sensitive-data access by extensions (WWW 2024).** Experimentally measures extension access to page content and credentials. *Role:* recent shift from metadata to page content.

9. **xie2024arcanum — "Arcanum" (USENIX Sec 2024).** Dynamic taint-tracking of extension privacy risks on real pages. *Role:* recent content-exfiltration measurement (research tool, not a consumer product).

10. **bui2023extpriva — inconsistencies in extension privacy practices (S&P 2023).** Intercepts ~47k extensions' traffic and compares it to their stated privacy practices. *Role:* closest methodological cousin (traffic vs. claims).

11. **dambra2022sally — "When Sally Met Trackers" (USENIX Sec 2022).** Web tracking from the user's perspective. *Role:* tracking-side context.

12. **englehardt2016openwpm — "Online Tracking / OpenWPM" (CCS 2016).** The standard open-source web-privacy measurement platform. *Role:* method lineage for instrumented measurement.

13. **senol2022leakyforms — "Leaky Forms" (USENIX Sec 2022).** Emails/passwords sent to third parties as the user types, before submitting. *Role:* the closest behavioural precedent (read-before-submit).

14. **munir2025keystroke — "Every Keystroke You Make" (arXiv 2025).** Widespread third-party keystroke interception across top sites, with a wiretap-law framing. *Role:* recent generalisation of read-before-submit.

15. **starov2016contactforms — PII leakage via contact forms (PoPETs 2016).** Quantifies PII leaking from website contact forms. *Role:* earlier read-before-submit precedent.

16. **enck2010taintdroid — "TaintDroid" (OSDI 2010).** Foundational taint-tracking for realtime privacy monitoring. *Role:* roots of the PII-in-traffic method.

17. **ren2016recon — "ReCon" (MobiSys 2016).** Reveals/controls PII leaks in decrypted mobile traffic. *Role:* network-level PII-measurement lineage.

18. **continella2017agrigento — "AGRIGENTO" (NDSS 2017).** Black-box differential leak detection resilient to obfuscation. *Role:* precedent for our canary/differential logic.

19. **vekaria2025bighelp — "Big Help or Big Brother?" (USENIX Sec 2025).** Audits generative-AI browser assistants; several forward full page content to their servers and trackers. *Role:* closest work; we position ours as the narrow, canary-proven complement.

20. **carlini2021extracting — extracting training data from LLMs (USENIX Sec 2021).** LLMs memorise and can regurgitate verbatim personal data. *Role:* why the transmitted content matters downstream.

21. **nasr2025scalable — scalable extraction from aligned models (ICLR 2025).** Extends extraction to production models (e.g. ChatGPT). *Role:* current LLM-memorisation risk.

22. **lukas2023pii — analyzing PII leakage in LLMs (S&P 2023).** Quantifies model PII leakage; scrubbing/DP leave residual exposure. *Role:* LLM PII risk.

23. **staab2024beyond — "Beyond Memorization" (ICLR 2024).** LLMs infer sensitive attributes (location, age, income) from ordinary prose. *Role:* profiling risk; cited in Related Work and Broader Impact.

24. **mireshghallah2024cansecret — "Can LLMs Keep a Secret?" (ICLR 2024).** LLM apps disclose info to contextually inappropriate recipients. *Role:* LLM-integration privacy risk.

25. **privacyparadox2026 — "The Privacy Paradox of LLMs" (CHI 2026).** Gap between user perception and reality of PII leakage. *Role:* motivates our quantified measurement.

26. **anthropic2026threats — Anthropic threat-intelligence report (2026).** Deployed AI services/proxies observed silently saving and relaying user inputs. *Role:* downstream retention/reuse; cited in Related Work and Broader Impact.

27. **unit42genai2026 — Palo Alto Unit 42 report (2026).** High-risk generative-AI browser extensions that read email as it is composed. *Role:* industry corroboration for our tool class.

28. **csa2026extensions — Cloud Security Alliance note (2026).** AI browser extensions read page content invisibly to standard DLP controls. *Role:* enterprise-risk corroboration.

29. **cyberhaven2026 — Cyberhaven AI adoption & risk report (2026).** Much data entered into AI tools comes from personal, unmonitored accounts. *Role:* enterprise-risk corroboration.

30. **mitmproxy — the interception proxy (software).** The HTTPS/WebSocket MITM proxy used for all captures. *Role:* core tool citation.

31. **microsoft2026connectedexp — Microsoft "Connected experiences in Office" (Microsoft Learn, 2026).** States that connected experiences analyse Office content in the cloud and are available unless the control is disabled. *Role:* primary source for the connected-experiences default and disable control (Word/augloop finding).

32. **microsoft2026copilotprivacy — Microsoft Copilot privacy docs (2026).** Documents cloud processing of Office content and the disable control. *Role:* supports the Word/augloop finding and the one-setting mitigation.

33. **apple2024platformsec — Apple Platform Security guide (2024).** iCloud encrypts file content in transit and (with Advanced Data Protection) end-to-end. *Role:* explains why iCloud sync showed no cleartext to the writing tools (ADP was off in our setup).

34. **mozilla2024permissions — Mozilla extension-permissions support page (2024).** "Access your data for all websites" lets an extension read and change page content. *Role:* backs the all-sites host-permission claim in the Permissions subsection.

35. **grammarly2025privacy — Grammarly privacy documentation (2025).** Grammarly analyses the text users write while the product is active. *Role:* vendor confirmation that processing user text is by design (Discussion).

36. **languagetool2025privacy — LanguageTool privacy policy (2025).** Describes browser-session/webpage content handled by the extension. *Role:* vendor confirmation for the second tool (Discussion).

37. **nissenbaum2004contextual — "Privacy as Contextual Integrity" (Washington Law Review, 2004).** Privacy as appropriate information flow within a context. *Role:* theoretical frame for the default-vs-expectation gap (Discussion).

38. **ieee2020ethics — IEEE Code of Ethics (2020).** Commits members to hold paramount the public's safety, welfare, and privacy. *Role:* grounds the Broader Impact discussion in professional/engineering responsibility.

39. **durumeric2017https — "The Security Impact of HTTPS Interception" (NDSS 2017).** Interception can weaken the connection it observes. *Role:* limitation/methodology caveat.

40. **razaghpanah2017tls — "Studying TLS Usage in Android Apps" (ACM CoNEXT 2017).** Measures certificate pinning and TLS practices in production apps. *Role:* supports the Limitations point that pinning is common and makes some channels a lower bound.

41. **microsoft2018presidio — Microsoft Presidio (software).** Open-source PII detection/de-identification SDK. *Role:* used to surface account identifiers alongside the document; basis for the labelling future work.

*(Removed from the citation set in this revision: the persistent-memory, unreleased-model, and Lavender/defence references, dropped when Broader Impact was condensed to measured, in-scope claims.)*
