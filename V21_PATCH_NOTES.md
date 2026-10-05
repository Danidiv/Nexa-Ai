# AZIZ AI v21 — Mistral 3B UI-resource hardening

## Root cause addressed
Mistral 3B generated an unnecessary `@/components/ui/avatar` import. The v20 resource resolver asked the model to generate `avatar.jsx`; the generated JSX was malformed, then export-contract repair repeatedly tried to repair the same file.

## Fixes
- Added deterministic `avatar.jsx` scaffold with `Avatar`, `AvatarImage`, and `AvatarFallback` exports.
- Added deterministic `accordion.jsx` scaffold with `Accordion`, `AccordionItem`, `AccordionTrigger`, and `AccordionContent` exports.
- UI scaffold copying now includes `.jsx`/`.js` resources as well as `.tsx`.
- Alias/local-resource resolver recognizes the deterministic UI resources, so Mistral is not called to invent them.
- `@/components/ui/` barrel now exports Avatar and Accordion as well as the existing primitives.
- Existing Mistral model configuration remains `AZIZ_MODEL=mistralai-3-3b`.

## Verification
- `python -m compileall -q services core web_ui load_env.py` — PASS
- `pytest -q tests/test_self_healing_react.py tests/test_runtime_repair.py tests/test_model.py` — 13 passed
- ZIP integrity — generated after patch

## Note
The uploaded ZIP's Linux node_modules snapshot is missing Rollup's platform optional dependency, so a Linux-local Vite build from this extracted artifact cannot be used as a clean browser E2E proof. On the target Windows/LM Studio environment, AZIZ's existing automatic dependency bootstrap should recreate the dependency tree.
