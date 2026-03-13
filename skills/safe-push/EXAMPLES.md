# Safe Push — Examples

## Example 1: Standard Push to Public Repo

**Prompt:**
> Push my changes to the public repo.

**Expected behavior:**
1. Detects `.public-repo` marker → applies all checks
2. Scans diff: finds no secrets or PII
3. Audits commit messages: all descriptive, no blocked terms
4. Summary: "Public repo, 3 commits on main, no issues found. Push directly?"
5. User confirms → pushes → verifies with `git log`

---

## Example 2: PII Detected in Diff

**Prompt:**
> Push this branch to origin.

**Expected behavior:**
1. Scans diff → finds issues:
   - `config.py:12` — email address `john.doe@company.com`
   - `settings.json:8` — private IP `192.168.1.50`
   - `.env.example:3` — looks like a real API key `sk-live-abc123...`
2. Reports all findings with file and line number
3. Blocks push: "3 issues found. Fix these before pushing."
4. Does NOT push until resolved

---

## Example 3: Vague Commit Messages

**Prompt:**
> Safe push to the public repo.

**Expected behavior:**
1. PII scan passes
2. Commit message audit flags:
   - `a1b2c3d fix` — too vague, suggest: "fix: [describe what was fixed]"
   - `e4f5g6h update` — too vague, suggest: "update: [describe what changed]"
3. Suggests interactive rebase to clean messages (with user approval)
4. Does not push until messages are acceptable

---

## Example 4: Large Push with Staggering

**Prompt:**
> Push all branches to the new public remote.

**Expected behavior:**
1. Detects multiple branches: main (120 commits), develop (45 commits), feature/auth (8 commits)
2. PII scan on all branches — clean
3. Proposes staggered strategy:
   - Push `main` first (in batches of 50: 3 batches, 10s gaps)
   - Wait 10s
   - Push `develop` (single push, < 50 commits)
   - Wait 5s
   - Push `feature/auth` (single push)
4. User confirms → executes with progress updates
