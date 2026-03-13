---
name: safe-push
description: "Pre-push hygiene check for GitHub repositories. Scans for PII, secrets, and sensitive data before pushing. Audits commit messages, enforces repo-specific blocklists, and rate-limits pushes to avoid GitHub abuse detection. Use before any git push, especially to public repos."
license: MIT
origin: custom
author: Rebecca Rae Barton
author_url: https://github.com/thatrebeccarae
metadata:
  version: 1.0.0
  category: dev-tools
  domain: git
  updated: 2026-03-13
---

# Safe Push

Pre-push hygiene checker for GitHub repositories. Prevents accidental exposure of secrets, PII, and sensitive infrastructure details.

## When to Use

- Before any `git push` to a remote repository
- Especially before pushing to public repos
- When onboarding a new repo to ensure clean push habits
- After bulk commits or rebases before pushing

## Procedure

### Step 1: Classify the Repo

```bash
# Check remote URL
git remote -v

# Check for public repo marker
test -f .public-repo && echo "PUBLIC" || echo "private or unmarked"
```

**Public repos** (`.public-repo` marker or public remote): apply ALL checks below.
**Private repos**: apply PII/secrets scan only (Step 2).

When in doubt, treat a repo as public.

### Step 2: PII and Secrets Scan

Scan the full diff against the target branch:

```bash
git diff origin/main...HEAD
```

**Always blocked:**
- Email addresses (personal or client)
- Phone numbers
- API keys, tokens, secrets (AWS, GitHub, Slack, generic patterns)
- Private IP addresses (RFC 1918 ranges)
- Internal hostnames and infrastructure details
- Private key material (RSA, SSH, PGP headers)
- Hardcoded credentials or passwords
- Client names configured in `.commit-msg-blocklist`

**Allowlist:** Patterns matching repo-local `.pii-allowlist` (one regex per line) are excluded from the scan.

If anything is found:
- List each finding with file, line number, and what was detected
- Do NOT push until all findings are resolved or allowlisted

### Step 3: Commit Message Audit

Review all commit messages in the push range:

```bash
git log origin/main..HEAD --format="%h %s"
```

For public repos, flag:
- Client names or internal project codenames (per `.commit-msg-blocklist`)
- Internal URLs, private IPs, hostnames
- Infrastructure details (service names, device IDs, network names)
- Personal information
- Vague messages ("fix", "update", "wip") — suggest descriptive rewrites

### Step 4: Staggered Push (Rate Limiting)

To avoid triggering GitHub bulk action / automation abuse detection:

| Scenario | Strategy |
|----------|----------|
| Single branch, < 50 commits | Push normally |
| Multiple branches | One branch at a time, 5s gap between pushes |
| > 50 commits on one branch | Batch into groups of 50, 10s gap between batches |
| New repo, initial push | Push default branch first, wait 10s, then remaining branches with 5s gaps |

Never use `git push --all` or `git push --mirror` to a public remote without staggering.

### Step 5: Final Confirmation

Present a summary before executing:
- Repository name and public/private classification
- Branch(es) being pushed
- Number of commits
- Any warnings from Steps 2-4
- Push strategy (direct or staggered)

Wait for explicit user confirmation.

### Step 6: Push and Verify

```bash
git push origin <branch>
git log origin/<branch> --oneline -5
```

Report success and the remote URL.

## Configuration Files

### `.pii-allowlist`

Place in repo root. One regex per line. Matches are excluded from the PII scan.

```
# Allow example.com emails in docs
example\.com
# Allow documentation IP ranges
192\.0\.2\.\d+
198\.51\.100\.\d+
```

### `.commit-msg-blocklist`

Place in repo root. Terms that must never appear in public commit messages.

```
# Client names
acme-corp
bigco
# Internal project codenames
project-phoenix
# Infrastructure
staging\.internal
```

## Key Principles

1. **Default to caution.** If unsure whether a repo is public, treat it as public.
2. **Never bypass.** This skill complements pre-commit hooks — they work together.
3. **Fix, don't suppress.** Remove the sensitive data rather than allowlisting it, when possible.
4. **Audit the full range.** Always scan from the divergence point, not just the latest commit.

For regex patterns and detection details, see [REFERENCE.md](REFERENCE.md).
