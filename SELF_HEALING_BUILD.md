# AZIZ AI — Autonomous React/React+TypeScript Self-Healing Build

The React builder now follows a bounded autonomous loop:

Plan → Generate → Imports → Build/Vite → TypeScript (TSX) → Run → Browser Runtime → Diagnose → Targeted Repair → Rebuild → Retest → Verify → Done

## Supported diagnostics

- JavaScript / JSX syntax and Vite/esbuild errors
- React runtime/render errors
- TypeScript / TSX compiler errors
- Missing imports/components and local path mismatches
- Prop contract mismatches
- Missing shared dependencies (template dependency bootstrap is automatic)
- Browser `window.onerror`, `unhandledrejection`, and actionable `console.error`
- Runtime error localization to a generated component where the browser stack identifies it

## Repair policy

- Plain React: up to 5 targeted runtime/build repair rounds.
- React+TypeScript: up to 5 targeted repair rounds plus the existing multi-error tsc repair passes.
- Repairs are scoped to the failing component whenever the diagnostic can be mapped safely.
- The build cannot report success without a clean browser runtime ready signal.
- If the limit is reached, the task is marked error and the final diagnostics are shown in the chat sidebar.

## Live sidebar activity

The web UI receives real build milestones such as planning, writing files, import checking, build verification, bug discovery, repair, rebuild, TypeScript validation, runtime verification, and final success/failure.

## LM Studio resilience

LM Studio 400 responses preserve the server's actionable error body. If a 400 is caused by a stale/invalid model id, the gateway can discover loaded non-embedding models and retry once with an available model.
