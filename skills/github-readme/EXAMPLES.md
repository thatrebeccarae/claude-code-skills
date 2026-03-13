# GitHub README — Examples

## Example 1: Generate README for a Node.js Library

**Prompt:**
> Generate a README for this repo. It's a TypeScript utility library for parsing and validating email addresses.

**Expected output:** A complete README with:
- Title + npm version badge + build badge + TypeScript badge + license badge
- One-line description
- Features list (parsing, validation, MX lookup, etc.)
- Installation (npm/yarn/pnpm)
- Quick start code example in TypeScript
- API reference for main exported functions
- Configuration options
- Contributing section
- MIT license

---

## Example 2: Audit an Existing README

**Prompt:**
> Audit the README for this repo. Check for completeness, broken badges, and stale content.

**Expected output:** A scored report (e.g., 72/100) with findings:
- "Missing: Environment Variables section (detected .env.example in repo)"
- "Stale: npm badge shows v1.2.0 but package.json is at v2.0.1"
- "Broken: Coverage badge URL returns 404 (no Codecov config found)"
- "Good: Install instructions are correct and tested"
- "Good: Code examples are syntactically valid"
- Prioritized fix recommendations

---

## Example 3: Update README After Major Release

**Prompt:**
> Update the README. We just released v3.0 with a new plugin system and dropped Node 16 support.

**Expected output:** Diff-style preview showing:
- Badge version bump (v2.x → v3.x)
- Node.js badge update (>=16 → >=18)
- New "Plugins" section added after Configuration
- Breaking changes note added to top
- Updated install command if package name changed
- User approves → changes applied

---

## Example 4: Generate README for a Monorepo

**Prompt:**
> Generate a README for this monorepo. It has packages/core, packages/cli, and packages/web.

**Expected output:** A README with:
- Title + badges
- Monorepo overview explaining the package structure
- Table listing each package with description and npm link
- Getting started with workspace setup (pnpm/yarn workspaces)
- Development workflow (how to run, test, build across packages)
- Contributing guidelines
- License
