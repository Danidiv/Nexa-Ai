# v25 Security Cleanup and History Purge

## Current-tree cleanup

Removed from the repository snapshot:
- .env
- aziz_users.db
- database/aziz_memory.db
- workspace/ and its generated runtime/test projects

Kept:
- .env.example as the safe configuration template.
- Source code and deterministic test fixtures that are not runtime state.

## Before rewriting Git history

1. Inspect the full Git history for secrets and private data.
2. Treat every credential that ever appeared in Git history as compromised, even if later deleted.
3. Rotate/revoke API keys, tokens, passwords, signing keys, or other credentials that may have been exposed.
4. Make a local backup/clone before rewriting history.
5. Coordinate the rewrite with anyone else who has cloned the repository.

## Recommended history purge

Use git-filter-repo locally from a fresh mirror clone:

    git clone --mirror https://github.com/Danidiv/Nexa-Ai.git Nexa-Ai.git
    cd Nexa-Ai.git
    git filter-repo --force --path .env --path aziz_users.db --path database/aziz_memory.db --path-glob 'workspace/**' --invert-paths

Then verify rewritten history:

    git log --all -- .env aziz_users.db database/aziz_memory.db workspace/
    git rev-list --objects --all | grep -E '(^|/)(\.env|aziz_users\.db|aziz_memory\.db|workspace/)'

Those commands should return no matching historical paths. Also search the rewritten repository for credential-like material before publishing it again.

## Publish the rewritten history

After verification:

    git push --force --all origin
    git push --force --tags origin

If GitHub or another service cached a secret, deleting the file from Git history does not revoke that secret. Rotate/revoke it first.

## After the purge

- Never commit .env; use .env.example.
- Never commit user/session databases.
- Never commit generated workspace projects.
- Keep runtime state outside the Git working tree where practical.
- Add CI secret scanning before merging future changes.
- Review pull requests for accidental credentials and generated runtime data.

## Important

This document defines the purge procedure. The history rewrite is intentionally NOT performed by the repository snapshot cleanup itself because rewriting public history is a destructive operation that should be run and verified from the owner's local clone.
