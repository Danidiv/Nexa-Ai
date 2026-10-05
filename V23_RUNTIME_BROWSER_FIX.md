# AZIZ AI v23 — Browser Runtime Verification Fix

## Problem observed
The React build reached Vite validation successfully, but the worker ended with:

`Browser runtime verification timed out: no clean ready signal was received.`

## Fixes
- Browser runtime reporter now writes `data-aziz-runtime="loading|ready|error"` on the document.
- Runtime errors also write `data-aziz-runtime-message` for deterministic browser diagnostics.
- The parent preview iframe now sends `AZIZ_RUNTIME_PING` after iframe load and at short intervals to avoid a ready-message timing race.
- The child reporter responds to the parent handshake once it has reached ready/error state.
- If the authenticated parent `postMessage` transport is unavailable, the builder can use a local Chromium smoke verifier when Chromium is available. It checks the same reporter marker instead of blindly treating a timeout as an app failure.
- Existing build/import/dependency/self-healing behavior is unchanged.

## Model
`.env` remains configured for `AZIZ_MODEL=mistralai-3-3b`.

## Verification actually performed in the sandbox
- Targeted runtime/self-healing tests: **13 passed**.
- Full pytest collection: **267 passed, 2 unrelated collection errors** from pre-existing helper-style functions that pytest attempts to collect (`services/completion_responsive_testing.py` and `tests/test_validator.py`).
- Python compile of modified builder: **PASS**.
- The sandbox Chromium executable was present but could not complete a headless page load in this container (it hung until timeout). Therefore no false claim of a successful sandbox browser E2E is made.
- The sandbox also has no access to the user's LM Studio process, so an actual Mistral 3B generation cannot be claimed here.
