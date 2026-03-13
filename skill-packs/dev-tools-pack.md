<div align="center">

# Developer Tools Pack

**2 skills for pre-push security scanning and README generation.**

[![GitHub stars](https://img.shields.io/github/stars/thatrebeccarae/dgtldept?style=for-the-badge&logo=github&color=181717)](https://github.com/thatrebeccarae/dgtldept/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](../LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rebecca%20Rae%20Barton-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rebeccaraebarton)
[![Substack](https://img.shields.io/badge/Substack-dgtl%20dept*-FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://dgtldept.substack.com/welcome)

Ship clean. Ship safe.

[**Back to Repo**](../README.md)

</div>

---

## Who This Is For

- **Developers and marketers shipping code** — anyone maintaining a public repo who doesn't want to accidentally commit a client name, API key, or Slack webhook
- **Solo consultants and small agencies** who are one careless commit away from exposing client data to a public repository
- **Teams that want consistent README quality** across multiple repos without manually enforcing structure

## What's Included

| Skill | What It Does | Includes |
|-------|-------------|----------|
| **[safe-push](../skills/safe-push/)** | Claude-powered pre-push review: scans staged commits for PII patterns, exposed API keys, and sensitive client references. Audits commit messages against a configurable blocklist. Rate-limits pushes to avoid bulk action triggers. Configurable via `.pii-allowlist` and `.commit-msg-blocklist` files. | SKILL + REFERENCE + EXAMPLES |
| **[github-readme](../skills/github-readme/)** | Generate, audit, or update GitHub READMEs. Three modes: generate (new repos), audit (check existing against best practices), update (patch with new content). Detects repo type and selects appropriate badges, sections, and structure. | SKILL + REFERENCE + EXAMPLES |

## How the Skills Connect

Together they form a publish workflow: update the **README** before a release, then run **Safe Push** to verify nothing sensitive leaks in the push. Both enforce standards that protect a public-facing repository.

## Quick Start

```bash
cd dgtldept
for skill in safe-push github-readme; do
  cp -r "skills/$skill" ~/.claude/skills/
done
```

No API keys required. Safe Push uses configurable allowlist files in the repo root.

### Optional Configuration

**Safe Push** reads two optional files from the repo root:

| File | Purpose |
|------|---------|
| `.pii-allowlist` | One regex per line — matches are exempt from PII scanning |
| `.commit-msg-blocklist` | Terms that must never appear in public commit messages |

## Example Prompts

### Safe Push
- "Safe push this branch to origin"
- "Scan the last 5 commits for PII before pushing"
- "Audit my commit messages for anything that shouldn't be in a public repo"

### GitHub README
- "Generate a README for this repo"
- "Audit my existing README against best practices"
- "Update the README to reflect the new features we added this sprint"

## FAQ

<details>
<summary><strong>Does Safe Push work with GitHub Actions?</strong></summary>

No — it's a Claude Code skill that runs locally before you push, not a CI/CD step. It complements tools like git-secrets or trufflehog (which are regex-based) with Claude-based semantic analysis that can catch things pattern matching misses, like a client name in a commit message or a hardcoded IP address in a config comment.

</details>

<details>
<summary><strong>Is Safe Push a replacement for git-secrets or trufflehog?</strong></summary>

Complementary, not a replacement. Git-secrets and trufflehog are fast, regex-based scanners that run in CI. Safe Push adds a semantic review layer — Claude understands context, so it can flag a client name that isn't in any regex pattern or catch a sensitive reference that's technically not a "secret" but shouldn't be public.

</details>

<details>
<summary><strong>Can GitHub README work with monorepos or non-standard structures?</strong></summary>

Yes. The skill detects repo type (library, application, CLI tool, monorepo) and adapts its badge selection, section structure, and content suggestions accordingly. For monorepos, it generates a root README with package links and individual package READMEs.

</details>

## License

MIT — see [LICENSE](../LICENSE) for details.
