// n8n Code node: Compare GA4 events against event spec
// Detects gaps, unexpected events, and anomalies.

// ── 1. Pull inputs ────────────────────────────────────────────────────────────
const ga4Raw     = $('GA4 Fetch').first().json;
const specRaw    = $('Read Event Spec').first().json.data;
const prevRaw    = (() => {
  try { return $('Read Previous Counts').first().json.data; } catch { return null; }
})();

// ── 2. Parse event spec ───────────────────────────────────────────────────────
const spec = typeof specRaw === 'string' ? JSON.parse(specRaw) : specRaw;

// ── 3. Parse previous counts (optional) ──────────────────────────────────────
let prevCounts = {};
if (prevRaw) {
  try {
    const parsed = typeof prevRaw === 'string' ? JSON.parse(prevRaw) : prevRaw;
    // Handle both { event_counts: {...} } and flat { event: count } formats
    prevCounts = parsed.event_counts ?? parsed;
  } catch { /* ignore malformed */ }
}

// ── 4. GA4 auto-collected events to exclude from "unexpected" ─────────────────
const GA4_AUTO = new Set([
  'page_view', 'session_start', 'user_engagement',
  'first_visit', 'scroll', 'click',
]);

// ── 5. Parse GA4 rows → { name, count, users } ───────────────────────────────
const ga4Events = {};

if (ga4Raw && Array.isArray(ga4Raw.rows)) {
  const dimHeaders    = (ga4Raw.dimensionHeaders || []).map(h => h.name);
  const metricHeaders = (ga4Raw.metricHeaders   || []).map(h => h.name);

  const eventNameIdx  = dimHeaders.findIndex(n => n === 'eventName');
  const eventCountIdx = metricHeaders.findIndex(n => n === 'eventCount');
  const totalUsersIdx = metricHeaders.findIndex(n => n === 'totalUsers');

  for (const row of ga4Raw.rows) {
    const dimVals    = row.dimensionValues || [];
    const metricVals = row.metricValues   || [];

    const name  = eventNameIdx  >= 0 ? (dimVals[eventNameIdx]?.value   ?? '') : '';
    const count = eventCountIdx >= 0 ? parseInt(metricVals[eventCountIdx]?.value ?? '0', 10) : 0;
    const users = totalUsersIdx >= 0 ? parseInt(metricVals[totalUsersIdx]?.value ?? '0', 10) : 0;

    if (name) {
      ga4Events[name] = { count, users };
    }
  }
}

// ── 6. Build spec event map ───────────────────────────────────────────────────
const specEventMap = {};

for (const group of (spec.event_groups || [])) {
  for (const ev of (group.events || [])) {
    specEventMap[ev.name] = {
      group_name : group.group_name ?? null,
      phase      : group.phase      ?? null,
      priority   : ev.priority      ?? null,
      replaces   : ev.replaces      ?? null,
      status     : ev.status        ?? null,
    };
  }
}

const specNames = new Set(Object.keys(specEventMap));
const ga4Names  = new Set(Object.keys(ga4Events));

// ── 7. Missing events ────────────────────────────────────────────────────────
const missing_events = [];
for (const name of specNames) {
  if (!ga4Names.has(name)) {
    const meta = specEventMap[name];
    missing_events.push({
      name,
      group    : meta.group_name,
      phase    : meta.phase,
      priority : meta.priority,
      replaces : meta.replaces,
      status   : meta.status,
    });
  }
}

const PRIORITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };
missing_events.sort((a, b) => {
  const pa = PRIORITY_ORDER[a.priority] ?? 99;
  const pb = PRIORITY_ORDER[b.priority] ?? 99;
  if (pa !== pb) return pa - pb;
  if (a.phase !== b.phase) return (a.phase ?? 99) - (b.phase ?? 99);
  return a.name.localeCompare(b.name);
});

// ── 8. Unexpected events ──────────────────────────────────────────────────────
const unexpected_events = [];
for (const name of ga4Names) {
  if (!specNames.has(name) && !GA4_AUTO.has(name)) {
    unexpected_events.push({
      name,
      count : ga4Events[name].count,
      users : ga4Events[name].users,
    });
  }
}
unexpected_events.sort((a, b) => b.count - a.count);

// ── 9. Anomalies: previously >100 count, now 0 ───────────────────────────────
const anomalies = [];
for (const [name, prevCount] of Object.entries(prevCounts)) {
  if (prevCount > 100) {
    const current = ga4Events[name]?.count ?? 0;
    if (current === 0) {
      anomalies.push({
        event          : name,
        previous_count : prevCount,
        current_count  : 0,
        in_spec        : specNames.has(name),
      });
    }
  }
}
anomalies.sort((a, b) => b.previous_count - a.previous_count);

// ── 10. Coverage stats ────────────────────────────────────────────────────────
const total_spec_events = specNames.size;
const implemented       = total_spec_events - missing_events.length;
const coverage_pct      = total_spec_events > 0
  ? Math.round((implemented / total_spec_events) * 100)
  : 0;

// ── 11. Flat lookup maps ──────────────────────────────────────────────────────
const event_counts = {};
const event_users  = {};
for (const [name, vals] of Object.entries(ga4Events)) {
  event_counts[name] = vals.count;
  event_users[name]  = vals.users;
}

// ── 12. Summary flags ─────────────────────────────────────────────────────────
const gaps_found       = missing_events.length > 0;
const anomalies_found  = anomalies.length > 0;
const all_clear        = !gaps_found && !anomalies_found;

// ── 13. Return ────────────────────────────────────────────────────────────────
return [{
  json: {
    client          : spec.client        ?? null,
    ga4_property    : spec.ga4_property  ?? null,
    run_date        : new Date().toISOString().slice(0, 10),
    coverage_pct,
    total_spec_events,
    implemented,
    missing_events,
    unexpected_events,
    anomalies,
    gaps_found,
    anomalies_found,
    all_clear,
    event_counts,
    event_users,
  }
}];
