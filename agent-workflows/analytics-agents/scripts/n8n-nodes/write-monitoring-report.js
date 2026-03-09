// n8n Code node: Generate daily monitoring markdown report
// Outputs report_markdown, report_path, event_counts_json, event_counts_path

const comparison = $('Compare Events').first().json;
const config     = $('Read Config').first().json;
const specData   = JSON.parse($('Read Event Spec').first().json.data);

// ── Destructure ───────────────────────────────────────────────────────────────
const {
  client,
  ga4_property,
  run_date,
  coverage_pct,
  total_spec_events,
  implemented,
  missing_events    = [],
  unexpected_events = [],
  anomalies         = [],
  gaps_found,
  anomalies_found,
  all_clear,
  event_counts      = {},
  event_users       = {},
} = comparison;

const client_name    = config.client_name ?? client;
const monitoring_dir = config.vault?.monitoring_dir ?? `10-Clients/${client}/analytics/monitoring`;
const slack_channel  = config.slack?.channel ?? `#${client}-analytics`;

// ── Helpers ───────────────────────────────────────────────────────────────────
const fmt = (n) => n == null ? '—' : Number(n).toLocaleString('en-US');
const PRIORITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

// ── Build spec lookup: event_name → { group_name, phase, priority } ──────────
const specByName = {};
for (const group of (specData.event_groups || [])) {
  for (const ev of (group.events || [])) {
    specByName[ev.name] = {
      group_name: group.group_name,
      phase: group.phase,
      priority: ev.priority,
    };
  }
}

// ── Status label ──────────────────────────────────────────────────────────────
let status_label;
if (all_clear)                        status_label = 'All Clear';
else if (gaps_found && anomalies_found) status_label = 'Gaps + Anomalies Detected';
else if (gaps_found)                  status_label = 'Gaps Detected';
else if (anomalies_found)             status_label = 'Anomalies Detected';
else                                  status_label = 'Review Required';

// ── Build coverage table rows ─────────────────────────────────────────────────
const missingNames = new Set(missing_events.map(e => e.name));

// Missing rows (sorted by priority)
const missingRows = missing_events.map(e => ({
  name: e.name,
  group: e.group ?? specByName[e.name]?.group_name ?? '',
  status: 'missing',
  count: null,
  users: null,
  priority: e.priority ?? 'low',
}));
missingRows.sort((a, b) => {
  const pa = PRIORITY_ORDER[a.priority] ?? 99;
  const pb = PRIORITY_ORDER[b.priority] ?? 99;
  return pa !== pb ? pa - pb : a.name.localeCompare(b.name);
});

// Live spec events
const liveRows = [];
for (const group of (specData.event_groups || [])) {
  for (const ev of (group.events || [])) {
    if (!missingNames.has(ev.name) && event_counts[ev.name] != null) {
      liveRows.push({
        name: ev.name,
        group: group.group_name,
        status: 'live',
        count: event_counts[ev.name],
        users: event_users[ev.name] ?? null,
        priority: ev.priority,
      });
    }
  }
}
liveRows.sort((a, b) => a.name.localeCompare(b.name));

// Unexpected events
const unexpectedRows = (unexpected_events || []).map(e => {
  const name = typeof e === 'string' ? e : e.name;
  return {
    name,
    group: 'N/A (not in spec)',
    status: 'unexpected',
    count: event_counts[name] ?? null,
    users: event_users[name] ?? null,
    priority: '',
  };
});

const allRows = [...missingRows, ...liveRows, ...unexpectedRows];

const tableLines = [
  '| Event | Group | Status | Count (7d) | Users (7d) |',
  '|-------|-------|--------|------------|------------|',
];
for (const r of allRows) {
  tableLines.push(
    `| \`${r.name}\` | ${r.group} | ${r.status} | ${fmt(r.count)} | ${fmt(r.users)} |`
  );
}

// ── Gaps section (grouped by priority) ────────────────────────────────────────
let gapsSection;
if (missing_events.length === 0) {
  gapsSection = '## Gaps (0)\n\nNo missing events.';
} else {
  const byPriority = {};
  for (const e of missingRows) {
    const p = e.priority || 'low';
    if (!byPriority[p]) byPriority[p] = [];
    byPriority[p].push(e);
  }

  const labels = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' };
  const lines = [`## Gaps (${missing_events.length})`, ''];

  for (const p of ['critical', 'high', 'medium', 'low']) {
    if (!byPriority[p]?.length) continue;
    lines.push(`### ${labels[p]}`);
    lines.push('');
    for (const e of byPriority[p]) {
      const meta = specByName[e.name] ?? {};
      const phaseStr = meta.phase ? `, Phase ${meta.phase}` : '';
      lines.push(`- \`${e.name}\` — ${e.group}${phaseStr}`);
    }
    lines.push('');
  }

  gapsSection = lines.join('\n').trimEnd();
}

// ── Anomalies section ─────────────────────────────────────────────────────────
let anomaliesSection;
if (anomalies.length === 0) {
  anomaliesSection = '## Anomalies (0)\n\nNo anomalies detected.';
} else {
  const lines = [`## Anomalies (${anomalies.length})`, ''];
  for (const a of anomalies) {
    lines.push(`- \`${a.event}\` — was ${fmt(a.previous_count)}/7d, now ${fmt(a.current_count)}/7d`);
  }
  anomaliesSection = lines.join('\n');
}

// ── Actions taken ─────────────────────────────────────────────────────────────
const actions = [];
if (!all_clear) actions.push(`Slack notification sent to ${slack_channel}`);
if (anomalies_found) actions.push(`Anomaly alert sent to ${config.slack?.alert_channel ?? '#analytics-agent-alerts'}`);
if (all_clear) actions.push('All-clear status logged');

// ── Assemble report ───────────────────────────────────────────────────────────
const timestamp = new Date().toISOString();

const report_markdown = `# ${client_name} GA4 Status - ${run_date}

**Property:** ${ga4_property}
**Coverage:** ${coverage_pct}% (${implemented}/${total_spec_events} spec events)
**Status:** ${status_label}

## Event Coverage

${tableLines.join('\n')}

${gapsSection}

${anomaliesSection}

## Actions Taken

${actions.map(a => `- ${a}`).join('\n')}

---
*Generated by Analytics Agent pipeline at ${timestamp}*
`;

// ── Output ────────────────────────────────────────────────────────────────────
const report_path       = `${monitoring_dir}/${run_date}-status.md`;
const event_counts_path = `${monitoring_dir}/latest-event-counts.json`;
const event_counts_json = JSON.stringify({ date: run_date, event_counts, event_users }, null, 2);

return [{
  json: {
    report_markdown,
    report_path,
    event_counts_json,
    event_counts_path,
  }
}];
