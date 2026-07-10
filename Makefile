# Makefile - orchestrate the capture and analysis cycle
# Final tool set: Grammarly + LanguageTool (automatic grammar checkers) + baseline.
#   (ProWritingAid / QuillBot / Wordtune were dropped — see docs/QA-Professor.md.)
#
# Quick reference (most-used commands):
#   make check           - verify dependencies are installed
#   make page-grammarly  - start the page server + open the tool's Firefox profile
#   make grammarly-1     - run Grammarly capture #1 (you do the Ctrl+V when prompted)
#   make languagetool-1  - run LanguageTool capture #1
#   make baseline-1      - run baseline #1 (no extension)
#   make smoke           - test the Makefile without touching real data
#   make analyze         - run analysis on whatever has been captured so far
#   make chart           - produce comparison_chart.png + .svg in results/
#   make clean           - delete all captures and results (CAREFUL)
#
# Per-run procedure (see docs/Capture-Protocol.md for full details):
#   1. `make page-<tool>`  -> starts the localhost page server and opens the
#      right Firefox profile at http://localhost:8000/test-page.html
#   2. Click into the textarea so it has keyboard focus (cursor blinking).
#   3. `make <tool>-<n>`   -> loads the doc to the clipboard and starts the
#      recorder, then PAUSES and asks you to paste.
#   4. Switch to Firefox, empty the box, Ctrl+V to paste, come back, press ENTER.
#   5. The target records for 60s, stops the recorder, and prints the summary.
#
# NOTE: the paste is deliberately MANUAL. Auto-paste (xdotool) fills the box
# visually but the extension registers no input event and sends nothing (a
# fake-clean 0%). A real Ctrl+V is what makes the tool ingest the text. An
# opt-in `AUTO=1` exists but is not recommended.

PROJECT_ROOT := $(shell pwd)
TEST_DOC     := $(PROJECT_ROOT)/input-data/test-document.txt
PAGE_DIR     := $(PROJECT_ROOT)/input-data
PAGE_PORT    := 8000
TEST_PAGE    := http://localhost:$(PAGE_PORT)/test-page.html
ANALYZE      := python3 $(PROJECT_ROOT)/scripts/analysis/analyze.py
WAIT_SECONDS := 60

.PHONY: help check serve smoke \
        page-grammarly page-languagetool page-baseline \
        clean analyze analyze-lenient chart \
        grammarly-all languagetool-all baseline-all \
        $(foreach r,1 2 3 4 5,grammarly-$(r) languagetool-$(r)) \
        $(foreach r,1 2 3,baseline-$(r))

help:
	@echo "Privacy analysis - Makefile targets"
	@echo ""
	@echo "Setup checks:"
	@echo "  make check                 - verify mitmproxy, xclip, firefox, etc."
	@echo "  make smoke                 - dry-run the capture flow into a throwaway dir"
	@echo ""
	@echo "Open the page in the right Firefox profile (does 'serve' for you):"
	@echo "  make page-grammarly / page-languagetool / page-baseline"
	@echo ""
	@echo "Individual captures (page open + textarea focused first):"
	@echo "  make grammarly-1 ... grammarly-5"
	@echo "  make languagetool-1 ... languagetool-5"
	@echo "  make baseline-1 ... baseline-3"
	@echo ""
	@echo "Analyze:"
	@echo "  make analyze               - default strict analysis"
	@echo "  make analyze-lenient       - lenient view (window=12, threshold=0.5, no baseline)"
	@echo "  make chart                 - produce comparison chart PNG + SVG"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                 - delete data/raw/ and results/ (CAREFUL)"

check:
	@echo "Checking required tools..."
	@command -v mitmdump >/dev/null 2>&1 && echo "  mitmproxy: OK" || echo "  MISSING: mitmproxy (pip install --break-system-packages mitmproxy)"
	@command -v xclip    >/dev/null 2>&1 && echo "  xclip:     OK" || echo "  MISSING: xclip (sudo apt install xclip)"
	@command -v firefox  >/dev/null 2>&1 && echo "  firefox:   OK" || echo "  MISSING: firefox (sudo apt install firefox-esr)"
	@command -v python3  >/dev/null 2>&1 && echo "  python3:   OK" || echo "  MISSING: python3"
	@python3 -c "import mitmproxy"     2>/dev/null && echo "  python mitmproxy: OK" || echo "  MISSING: python mitmproxy"
	@python3 -c "import ahocorasick"   2>/dev/null && echo "  pyahocorasick:    OK" || echo "  optional: pyahocorasick"
	@python3 -c "import brotli"        2>/dev/null && echo "  brotli:           OK" || echo "  optional: brotli"
	@python3 -c "import matplotlib"    2>/dev/null && echo "  matplotlib:       OK" || echo "  MISSING: matplotlib (needed for make chart)"
	@test -f "$(TEST_DOC)"             && echo "  test-document.txt: present" || echo "  MISSING: $(TEST_DOC)"
	@test -f "$(PAGE_DIR)/test-page.html" && echo "  test-page.html: present" || echo "  MISSING: test-page.html"

# Start the localhost page server if it is not already running.
serve:
	@if pgrep -f "http.server $(PAGE_PORT)" >/dev/null 2>&1; then \
		echo "Page server already running on :$(PAGE_PORT)."; \
	else \
		echo "Starting page server on :$(PAGE_PORT) (serving $(PAGE_DIR))..."; \
		cd "$(PAGE_DIR)" && nohup python3 -m http.server $(PAGE_PORT) >/dev/null 2>&1 & \
		sleep 1; \
		echo "Started."; \
	fi

# Open the test page in a specific Firefox profile (starts the server first).
page-grammarly: serve
	@firefox -P grammarly-test --no-remote "$(TEST_PAGE)" &
	@echo ""
	@echo "Firefox opened: profile grammarly-test at $(TEST_PAGE)"
	@echo "1. Wait ~5s for it to load."
	@echo "2. CLICK INTO THE TEXTAREA so the cursor is blinking inside it."
	@echo "3. Then run:  make grammarly-1"

page-languagetool: serve
	@firefox -P languagetool-test --no-remote "$(TEST_PAGE)" &
	@echo "Profile languagetool-test at $(TEST_PAGE). Click the textarea, then: make languagetool-1"

page-baseline: serve
	@firefox -P baseline-test --no-remote "$(TEST_PAGE)" &
	@echo "Profile baseline-test (no extension) at $(TEST_PAGE). Click the textarea, then: make baseline-1"

# Generic per-run target. Usage: $(call run_one,grammarly,1)
# Loads the doc to the clipboard, starts the recorder, PAUSES for you to paste
# manually, records for $(WAIT_SECONDS)s, then stops and prints the summary.
define run_one
	@echo "============================================================"
	@echo " $(1) - run $(2)"
	@echo "============================================================"
	@mkdir -p data/raw/$(1)
	@echo "[1/4] Loading test document into clipboard..."
	@xclip -selection clipboard < "$(TEST_DOC)"
	@echo "[2/4] Starting recorder (mitmproxy)..."
	@TOOL_NAME=$(1) RUN_ID=$(2) mitmdump \
		--listen-host 127.0.0.1 --listen-port 8080 \
		--save-stream-file "data/raw/$(1)/run_$(2).flow" \
		-s scripts/capture/capture_addon.py \
		> "data/raw/$(1)/run_$(2).log" 2>&1 & \
	echo $$! > /tmp/privacy_mitm.pid
	@sleep 2
	@if [ -n "$(AUTO)" ]; then \
		echo "[3/4] AUTO paste via xdotool (experimental - verify the % below!)..."; \
		win=$$(xdotool search --name 'Mozilla Firefox' | head -1); \
		xdotool windowactivate --sync $$win; sleep 1; \
		xdotool key --clearmodifiers ctrl+a; xdotool key --clearmodifiers Delete; sleep 0.3; \
		xdotool key --clearmodifiers ctrl+v; \
	else \
		echo ""; \
		echo ">>> PASTE NOW:"; \
		echo ">>>   1. Switch to Firefox."; \
		echo ">>>   2. Empty the text box (Ctrl+A, then Backspace)."; \
		echo ">>>   3. Click the box and press Ctrl+V - watch the document appear."; \
		echo ">>>   4. Come back to THIS terminal and press ENTER."; \
		read _paste; \
	fi
	@echo "[3/4] Recording $(WAIT_SECONDS)s for the tool to send..."
	@sleep $(WAIT_SECONDS)
	@echo "[4/4] Stopping recorder..."
	@kill -INT $$(cat /tmp/privacy_mitm.pid) 2>/dev/null || true
	@sleep 2
	@rm -f /tmp/privacy_mitm.pid
	@echo ""
	@echo "------------------------- RESULT ---------------------------"
	@sed -n '/SESSION COMPLETE/,$$p' "data/raw/$(1)/run_$(2).log" 2>/dev/null || true
	@echo "------------------------------------------------------------"
	@echo "Saved: data/raw/$(1)/run_$(2).json   (.flow + .log alongside)"
endef

# Smoke test: exercises the whole Makefile flow but writes to a throwaway dir
# so it never touches real tool/baseline data. Use any open profile+page.
smoke: serve
	@echo "SMOKE TEST -> data/raw/_smoketest (throwaway; gitignored)."
	@echo "Open ANY profile+page first (grammarly-test ~= 99%, baseline-test = 0%)."
	$(call run_one,_smoketest,1)
	@echo ""
	@echo "If a SESSION COMPLETE summary printed above, the Makefile works."
	@echo "Remove the throwaway data with:  rm -rf data/raw/_smoketest"

# Per-tool, per-run targets
grammarly-1:      ; $(call run_one,grammarly,1)
grammarly-2:      ; $(call run_one,grammarly,2)
grammarly-3:      ; $(call run_one,grammarly,3)
grammarly-4:      ; $(call run_one,grammarly,4)
grammarly-5:      ; $(call run_one,grammarly,5)
languagetool-1:   ; $(call run_one,languagetool,1)
languagetool-2:   ; $(call run_one,languagetool,2)
languagetool-3:   ; $(call run_one,languagetool,3)
languagetool-4:   ; $(call run_one,languagetool,4)
languagetool-5:   ; $(call run_one,languagetool,5)
baseline-1:       ; $(call run_one,baseline,1)
baseline-2:       ; $(call run_one,baseline,2)
baseline-3:       ; $(call run_one,baseline,3)

# "all" targets - reminders only; you still must reset Firefox between runs
grammarly-all:
	@echo "Run: make grammarly-1, empty the box, make grammarly-2, ... through 5."

languagetool-all:
	@echo "Run: make languagetool-1 ... languagetool-5 (empty the box between each)."

baseline-all:
	@echo "Run: make baseline-1, make baseline-2, make baseline-3."

# Analysis targets
analyze:
	$(ANALYZE) --all

analyze-lenient:
	$(ANALYZE) --all --no-baseline --window 12 --sentence-threshold 0.5

chart:
	$(ANALYZE) --all --chart

# Cleanup
clean:
	@echo "About to delete data/raw/ and results/."
	@echo "Press Ctrl+C to cancel, or Enter to proceed."
	@read _confirm
	rm -rf data/raw/ results/
	mkdir -p data/raw results
	@echo "Cleaned."
