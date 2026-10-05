# AZIZ AI Cross-Prompt Regression Matrix

Date: 2026-10-05
Base: v17

## Requested prompts

1. Dashboard — `build a dashboard with sidebar, analytics cards, charts, recent activity table, responsive mobile layout and interactive filters`
2. E-commerce — `build an e-commerce storefront with product grid, product cards, filters, cart summary and responsive mobile layout`
3. Business/Corporate — `build a corporate business website with hero, services, company stats, testimonials, team and contact section`
4. Portfolio — `build a developer portfolio with hero, skills, projects, experience and contact section`
5. Blog/News — `build a blog/news homepage with featured story, article cards, categories, search and responsive layout`
6. Educational — `build an educational platform homepage with courses, instructors, categories, progress cards and responsive layout`
7. Event — `build an event website with hero, schedule, speakers, tickets, venue information and responsive layout`
8. Landing Page — `build a modern SaaS landing page with hero, features, pricing, testimonials, FAQ and call to action`

## Execution status in this build environment

The cross-prompt **real LM Studio generation run could not be executed here** because the user's local LM Studio server is not exposed to this execution environment (`127.0.0.1:1234` refused the connection). Therefore no fabricated per-prompt first-failure file/runtime error is reported.

The project was instead statically/runtime-hardened against the shared failure classes already observed in the v17 dashboard run, and the targeted regression suite was executed.

## Shared root causes fixed in this revision

### 1. Runtime reporter could abort before parent transport
The reporter previously returned immediately when `document.referrer` did not produce a direct API endpoint. That could suppress the parent `postMessage` channel and produce a false `no clean ready signal` timeout.

Fix: parent `postMessage` remains available even without a referrer/direct endpoint.

### 2. Runtime retry-limit diagnostic was hard-coded
The failure message said `after 3 targeted repairs` even though the builder is configured for 5 repairs.

Fix: diagnostic now reports the actual configured `max_repairs`.

### 3. Partial node_modules cache was treated as healthy
A packaged/deployed template can contain a `node_modules` directory without usable `.bin/vite` shims. The old bootstrap check only tested whether the directory existed.

Fix: dependency readiness now requires both React and the Vite executable shim; otherwise automatic npm bootstrap is triggered.

### 4. Stale completion-contract imports
Two older completion tests referenced missing compatibility contracts (`RuntimeVerificationPlan` / `build_verification_plan` and `CommandPreflight`). Additive compatibility implementations were restored without changing the newer runtime builder API.

## Verification performed

- Python compileall: PASS
- Targeted runtime repair tests: PASS (4 passed)
- Compatibility/runtime integration test collection: PASS for the previously failing modules
- Builder source AST parse: PASS

A full repository pytest run still contains unrelated legacy/generated setup tests outside the self-healing React path; those were not silently treated as product prompt failures.
