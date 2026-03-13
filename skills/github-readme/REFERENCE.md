# GitHub README — Reference

## Badge URL Patterns

### Shields.io Badges

```markdown
<!-- Build status (GitHub Actions) -->
![Build](https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow}.yml?branch=main)

<!-- npm version -->
![npm](https://img.shields.io/npm/v/{package-name})

<!-- PyPI version -->
![PyPI](https://img.shields.io/pypi/v/{package-name})

<!-- License -->
![License](https://img.shields.io/github/license/{owner}/{repo})

<!-- TypeScript -->
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript&logoColor=white)

<!-- Node.js -->
![Node](https://img.shields.io/badge/Node.js-%3E%3D18-green?logo=node.js&logoColor=white)

<!-- Python -->
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)

<!-- Coverage (Codecov) -->
![Coverage](https://img.shields.io/codecov/c/github/{owner}/{repo})

<!-- Docker -->
![Docker](https://img.shields.io/docker/v/{owner}/{repo}?sort=semver&logo=docker)

<!-- Downloads (npm) -->
![Downloads](https://img.shields.io/npm/dm/{package-name})

<!-- Stars -->
![Stars](https://img.shields.io/github/stars/{owner}/{repo}?style=social)
```

## Section Templates

### Title Block

```markdown
# Project Name

[![Build](badge-url)](link) [![License](badge-url)](link)

> One-line description of what this project does and who it's for.
```

### Features

```markdown
## Features

- **Feature name** — What it does and why it matters
- **Feature name** — What it does and why it matters
- **Feature name** — What it does and why it matters
```

### Installation

```markdown
## Installation

```bash
npm install package-name
# or
yarn add package-name
# or
pnpm add package-name
```
```

### Quick Start

```markdown
## Quick Start

```typescript
import { thing } from "package-name";

const result = thing.doSomething({
  option: "value",
});

console.log(result);
```
```

### Environment Variables

```markdown
## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | — | Your API key from the dashboard |
| `PORT` | No | `3000` | Server port |
| `LOG_LEVEL` | No | `info` | Logging verbosity |

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```
```

### CLI Commands

```markdown
## Commands

| Command | Description |
|---------|-------------|
| `tool init` | Initialize a new project |
| `tool build` | Build for production |
| `tool dev` | Start development server |
| `tool test` | Run test suite |

### `tool init`

```bash
tool init [project-name] [--template <name>]
```

Options:
- `--template` — Starter template (default: `basic`)
- `--no-git` — Skip git initialization
```

### API Endpoints

```markdown
## API Reference

### Authentication

All requests require an API key in the `Authorization` header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/v1/resource
```

### Endpoints

#### `GET /v1/resources`

List all resources.

**Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `limit` | integer | No | Max results (default: 20) |
| `offset` | integer | No | Pagination offset |

**Response:**

```json
{
  "data": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```
```

### Contributing

```markdown
## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
```

### License

```markdown
## License

[MIT](LICENSE) &copy; [Your Name](https://github.com/yourusername)
```

## Audit Scoring Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| Description | 15% | Clear one-liner, explains what + who |
| Installation | 20% | Working install command, prerequisites listed |
| Usage/Examples | 20% | Code examples that work, cover main use case |
| Badges | 10% | Relevant badges, all URLs resolve |
| Structure | 15% | Logical section order, appropriate for repo type |
| Completeness | 10% | All required sections present |
| Freshness | 10% | Version numbers current, no stale references |

## PII/Infrastructure Scrub Checklist

Before publishing, verify the README contains none of:

- [ ] Email addresses (personal or team)
- [ ] Internal IP addresses or hostnames
- [ ] API keys, tokens, or passwords (even example ones that look real)
- [ ] Internal URLs (intranet, staging, VPN)
- [ ] Client names or project codenames
- [ ] Employee names (unless public maintainers)
- [ ] File paths containing usernames
- [ ] Internal tool references (Slack channels, Jira projects)
