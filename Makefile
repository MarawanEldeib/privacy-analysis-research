# Makefile - orchestrate the 18-run capture and analysis cycle
#
# Quick reference (most-used commands):
#   make check          - verify dependencies are installed
#   make page           - open the test page in Firefox (use before every run)
#   make grammarly-1    - run Grammarly capture #1
#   make baseline-1     - run baseline #1 (no extension)
#   make analyze        - run analysis on whatever has been captured so far
#   make chart          - produce comparison_chart.png + .svg in results/
#   make clean          - delete all captures and results (CAREFUL)
#
# Per-run procedure (see docs/Capture-Protocol.md for full details):
#   1. Make sure the right Firefox profile is open and the test page is loaded
#      (run `make page-<tool>` to open the right profile).
#   2. Click into the textarea so it has focus.
#   3. In a separate terminal, run `make grammarly-1` (or whichever run).
#   4. The Makefile target loads the document into clipboard, pastes it,
#      waits 60s, and stops mitmproxy automatically.

PROJECT_ROOT := $(shell pwd)
TEST_DOC     := $(PROJECT_ROOT)/input-data/test-document.txt
TEST_PAGE    := file://$(PROJECT_ROOT)/input-data/test-page.html
RUN_SCRIPT   := $(PROJECT_ROOT)/scripts/capture/run_capture.sh
ANALYZE      := python3 $(PROJECT_ROOT)/scripts/analysis/analyze.py
WAIT_SECONDS := 60

.PHONY: help check page page-grammarly page-prowritingaid page-wordtune page-baseline \
        clean analyze analyze-lenient chart \
        grammarly-all prowritingaid-all wordtune-all baseline-all \
        $(foreach r,1 2 3 4 5,grammarly-$(r) prowritingaid-$(r) wordtune-$(r)) \
        $(foreach r,1 2 3,baseline-$(r))

help:
	@echo "Privacy analysis - Makefile targets"
	@echo ""
	@echo "Setup checks:"
	@echo "  make check                 - verify mitmproxy, xdotool, xclip, etc."
	@echo ""
	@echo "Open test page in the right Firefox profile (do this before each run):"
	@echo "  make page-grammarly"
	@echo "  make page-prowritingaid"
	@echo "  make page-wordtune"
	@echo "  make page-baseline"
	@echo ""
	@echo "Individual captures (run after the page is open + textarea focused):"
	@echo "  make grammarly-1 ... grammarly-5"
	@echo "  make prowritingaid-1 ... prowritingaid-5"
	@echo "  make wordtune-1 ... wordtune-5"
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
	@command -v xdotool  >/dev/null 2>&1 && echo "  xdotool:   OK" || echo "  MISSING: xdotool (sudo apt install xdotool)"
	@command -v firefox  >/dev/null 2>&1 && echo "  firefox:   OK" || echo "  MISSING: firefox (sudo apt install firefox-esr)"
	@command -v jq       >/dev/null 2>&1 && echo "  jq:        OK" || echo "  optional: jq (sudo apt install jq)"
	@python3 -c "import mitmproxy"     2>/dev/null && echo "  python mitmproxy: OK" || echo "  MISSING: python mitmproxy"
	@python3 -c "import ahocorasick"   2>/dev/null && echo "  pyahocorasick:    OK" || echo "  optional: pyahocorasick"
	@python3 -c "import brotli"        2>/dev/null && echo "  brotli:           OK" || echo "  optional: brotli"
	@python3 -c "import matplotlib"    2>/dev/null && echo "  matplotlib:       OK" || echo "  MISSING: matplotlib (needed for make chart)"
	@test -f "$(TEST_DOC)"             && echo "  test-document.txt: present" || echo "  MISSING: $(TEST_DOC)"
	@test -f "$(PROJECT_ROOT)/input-data/test-page.html" && echo "  test-page.html: present" || echo "  MISSING: test-page.html"

# Open test page in a specific Firefox profile
page-grammarly:
	firefox -P grammarly-test --no-remote "$(TEST_PAGE)" &
	@echo ""
	@echo "Firefox opened with profile grammarly-test."
	@echo "1. Wait ~5 seconds for Firefox to settle."
	@echo "2. CLICK INTO THE TEXTAREA so it has keyboard focus."
	@echo "3. Then in another terminal, run: make grammarly-1"

page-prowritingaid:
	firefox -P prowritingaid-test --no-remote "$(TEST_PAGE)" &
	@echo "Profile prowritingaid-test loaded. Click into textarea, then: make prowritingaid-1"

page-wordtune:
	firefox -P wordtune-test --no-remote "$(TEST_PAGE)" &
	@echo "Profile wordtune-test loaded. Click into textarea, then: make wordtune-1"

page-baseline:
	firefox -P baseline-test --no-remote "$(TEST_PAGE)" &
	@echo "Profile baseline-test loaded (no extension). Click into textarea, then: make baseline-1"

# Generic per-run target. Usage: $(call run_one,grammarly,1)
# It loads the document to clipboard, starts mitmproxy in background,
# pastes via xdotool, waits, then stops mitmproxy.
define run_one
	@echo "============================================================"
	@echo " $(1) run $(2)"
	@echo "============================================================"
	@echo "Step 1/4: loading test document into clipboard..."
	xclip -selection clipboard < "$(TEST_DOC)"
	@echo "Step 2/4: starting mitmproxy in background..."
	@mkdir -p data/raw/$(1)
	@TOOL_NAME=$(1) RUN_ID=$(2) mitmdump \
		--listen-host 127.0.0.1 --listen-port 8080 \
		--ssl-insecure \
		--save-stream-file "data/raw/$(1)/run_$(2).flow" \
		-s scripts/capture/capture_addon.py \
		> "data/raw/$(1)/run_$(2).log" 2>&1 & \
	echo $$! > /tmp/privacy_mitm.pid
	@sleep 3
	@echo "Step 3/4: pasting into Firefox..."
	xdotool key --window "$$(xdotool search --name 'Mozilla Firefox' | head -1)" ctrl+v
	@echo "Step 4/4: waiting $(WAIT_SECONDS)s for the extension to send..."
	@sleep $(WAIT_SECONDS)
	@echo "Stopping mitmproxy..."
	@kill -INT $$(cat /tmp/privacy_mitm.pid) 2>/dev/null || true
	@sleep 2
	@rm -f /tmp/privacy_mitm.pid
	@echo ""
	@echo "Capture complete. Results:"
	@echo "  data/raw/$(1)/run_$(2).json   (analyzed summary)"
	@echo "  data/raw/$(1)/run_$(2).flow   (raw archive)"
	@echo "  data/raw/$(1)/run_$(2).log    (mitmproxy console output)"
endef

# Per-tool, per-run targets
grammarly-1:      ; $(call run_one,grammarly,1)
grammarly-2:      ; $(call run_one,grammarly,2)
grammarly-3:      ; $(call run_one,grammarly,3)
grammarly-4:      ; $(call run_one,grammarly,4)
grammarly-5:      ; $(call run_one,grammarly,5)
prowritingaid-1:  ; $(call run_one,prowritingaid,1)
prowritingaid-2:  ; $(call run_one,prowritingaid,2)
prowritingaid-3:  ; $(call run_one,prowritingaid,3)
prowritingaid-4:  ; $(call run_one,prowritingaid,4)
prowritingaid-5:  ; $(call run_one,prowritingaid,5)
wordtune-1:       ; $(call run_one,wordtune,1)
wordtune-2:       ; $(call run_one,wordtune,2)
wordtune-3:       ; $(call run_one,wordtune,3)
wordtune-4:       ; $(call run_one,wordtune,4)
wordtune-5:       ; $(call run_one,wordtune,5)
baseline-1:       ; $(call run_one,baseline,1)
baseline-2:       ; $(call run_one,baseline,2)
baseline-3:       ; $(call run_one,baseline,3)

# "all" targets - reminders only; you still must reset Firefox between runs
grammarly-all:
	@echo "NOTE: you must reset the textarea between runs (refresh the page)."
	@echo "Run: make grammarly-1, then refresh, make grammarly-2, etc."

prowritingaid-all:
	@echo "Same as above for prowritingaid."

wordtune-all:
	@echo "Same as above for wordtune."

baseline-all:
	@echo "Run: make baseline-1, then refresh, make baseline-2, then make baseline-3"

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
