# Aziz AI — Plan Compression Patch (v19)

## Problem fixed
Local models can ignore the planner's small-plan instruction and return more than 10 files. Previously the React builders rejected the response with:

`plan too large (11 files) - keep it small`

That stopped generation before any files were created.

## New behavior
- Planner accepts plans up to 10 files.
- If the model returns more than 10 files, Aziz AI automatically asks the model to compress/replan the oversized plan.
- Compression preserves requested features and interactions and merges related sections into richer components instead of simply deleting files.
- Up to 3 compression attempts are made.
- The same recovery is applied to React JS, React TS/TSX, and the generic multi-file planner.
- The old `plan too large` hard failure is removed.
- Domain-specific validation still runs after compression, so unsafe paths, duplicate files, missing App entry, and invalid extensions remain protected.

## Verification
- Python `compileall`: PASS
- Oversized React plan recovery test: PASS
- Oversized React compression retry test: PASS
- Relevant self-healing/runtime tests excluding two pre-existing import-repair assertions: 8 passed, 2 deselected
- Full repository pytest was also run: 259 passed, 2 failed, 2 collection errors. The failures/errors are pre-existing unrelated tests (`test_self_healing_react` import-repair assertions and two malformed pytest-collection targets), not caused by this planner patch.

## Important
This patch was not tested against the user's Windows LM Studio process from this container. The local-model/browser end-to-end test must still be run on the user's machine.
