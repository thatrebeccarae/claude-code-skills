# Tech Diagram — Examples

## Example 1: Data Pipeline Architecture

**Prompt:**
> Create a diagram showing our ETL pipeline: S3 ingestion → Spark transform → Snowflake warehouse → dbt models → Looker dashboards

**Expected output:** A standalone HTML file with a 5-stage horizontal pipeline flow, each stage colored with a different accent, connecting arrows between stages, and a brief description under each stage label.

---

## Example 2: Tech Stack Layers

**Prompt:**
> Show our tech stack as a layer diagram: Infrastructure (AWS), Platform (Kubernetes), Services (Go microservices), API Gateway (Kong), Frontend (Next.js)

**Expected output:** A vertical stack diagram with 5 layers, bottom to top from infrastructure to frontend. Each layer has a distinct background tint and lists the key technologies.

---

## Example 3: Microservices Component Map

**Prompt:**
> Map out our microservices: Auth Service (Go), User Service (Go), Payment Service (Java), Notification Service (Python), API Gateway (Kong). Auth talks to User and Payment. Gateway routes to all.

**Expected output:** A grid of 5 component boxes with the service name, language tag, and status indicator. Connection lines or arrows showing the communication paths described.

---

## Example 4: Migration Timeline

**Prompt:**
> Create a timeline for our database migration: Phase 1 (Jan) — Schema design, Phase 2 (Feb) — Dual-write setup, Phase 3 (Mar) — Shadow reads, Phase 4 (Apr) — Cutover, Phase 5 (May) — Decommission legacy

**Expected output:** A vertical timeline with 5 milestones, each showing the phase name, month, and a one-line description. Completed phases in green, current in blue, future in muted gray.

---

## Example 5: Before/After Architecture

**Prompt:**
> Show before/after: Before — monolith Rails app with MySQL, single server. After — microservices with API gateway, Redis cache, PostgreSQL, deployed on Kubernetes.

**Expected output:** A side-by-side split diagram. Left side shows a single box (monolith) connected to MySQL. Right side shows multiple service boxes connected through an API gateway, with Redis and PostgreSQL as separate data stores.

---

## Example 6: KPI Dashboard Header

**Prompt:**
> Create a metrics row showing: Uptime 99.97%, P95 Latency 142ms (down 12%), Error Rate 0.03%, Deployments 47/month (up 8%)

**Expected output:** A horizontal row of 4 metric cards with large monospace numbers, labels, and trend indicators (green up arrows, red down arrows as appropriate).
