# Setup Guide — RETIRED

> **This guide has been retired.** It described an earlier scope (ProWritingAid /
> Wordtune profiles) and an earlier capture method (automated `xdotool` paste)
> that the study moved away from — the paste is now a manual **Ctrl+V**, because an
> automated paste doesn't fire the DOM input event the extensions listen for.
>
> Use **[`Reproduction-Guide.md`](Reproduction-Guide.md)** instead. It is the
> current, corrected, from-scratch tutorial and covers everything this file used
> to, including:
>
> - dependency install, mitmproxy CA setup, and per-profile configuration;
> - installing the extensions from **verified** official listings;
> - the interception-verification check before collecting data;
> - the capture and analysis commands;
> - VirtualBox shared-folder setup (Appendix A) and `jq` inspection recipes
>   (Appendix B).
>
> Related reference docs: [`Capture-Protocol.md`](Capture-Protocol.md) (locked
> per-run steps), [`ENVIRONMENT.md`](ENVIRONMENT.md) (pinned versions),
> [`Metrics-Definition.md`](Metrics-Definition.md) (metric formulas).
