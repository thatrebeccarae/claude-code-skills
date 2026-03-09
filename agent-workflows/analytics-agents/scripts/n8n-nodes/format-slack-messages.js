// n8n Code node: Format Slack messages from comparison results
// Produces pre-formatted text fields needed by the Slack Block Kit templates.
// Place after the Compare Events node, before Slack HTTP Request nodes.

const data = $input.first().json;

// ── Missing events preview (for Gaps Found message) ──────────────────────────
const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
const MAX_INLINE = 5;

const sortedMissing = [...(data.missing_events || [])].sort((a, b) => {
  const pa = priorityOrder[a.priority] ?? 99;
  const pb = priorityOrder[b.priority] ?? 99;
  return pa - pb;
});

const shown = sortedMissing.slice(0, MAX_INLINE);
const remainder = sortedMissing.length - shown.length;

const missingLines = shown.map(e => {
  const badge = e.priority === 'critical' ? ' :red_circle:'
              : e.priority === 'high'     ? ' :large_orange_circle:'
              : '';
  return `• *${e.name}*${badge}  [${e.group} / Phase ${e.phase}]`;
});

if (remainder > 0) {
  missingLines.push(`_+${remainder} more — see vault report_`);
}

const missing_preview_text = missingLines.join('\n') || 'None';

// ── Anomaly lines (for Urgent Anomaly message) ──────────────────────────────
const anomalyLines = (data.anomalies || []).map(a => {
  const prev = Number(a.previous_count).toLocaleString('en-US');
  const curr = Number(a.current_count).toLocaleString('en-US');
  return `• *${a.event}* — :chart_with_downwards_trend: dropped to ${curr} (was ${prev}/7d)`;
});

const anomaly_lines_text = anomalyLines.join('\n') || 'None';

// ── Claude gap analysis summary (for Gaps Found message) ─────────────────────
const MAX_CLAUDE_TEXT = 500;

function truncate(str, max) {
  if (!str) return '';
  if (str.length <= max) return str;
  return str.slice(0, max).replace(/\s+\S*$/, '') + '…';
}

const claude_gap_text = data.claude_gap_summary
  ? truncate(data.claude_gap_summary, MAX_CLAUDE_TEXT)
  : '';

// ── Claude anomaly analysis summary (for Anomaly Alert message) ──────────────
const claude_anomaly_text = data.claude_anomaly_summary
  ? truncate(data.claude_anomaly_summary, MAX_CLAUDE_TEXT)
  : '';

// ── PRD link (for Gaps Found message) ────────────────────────────────────────
const prd_link_text = data.prd_path
  ? `:clipboard: PRD: \`${data.prd_path}\``
  : '';

// ── Quick wins from Claude analysis (for Gaps Found message) ─────────────────
const MAX_QUICK_WINS = 3;
const quickWins = (data.claude_analysis && Array.isArray(data.claude_analysis.quick_wins))
  ? data.claude_analysis.quick_wins.slice(0, MAX_QUICK_WINS)
  : [];

const quick_wins_text = quickWins.length > 0
  ? quickWins.map((w, i) => `${i + 1}. ${typeof w === 'string' ? w : w.name || w.description || JSON.stringify(w)}`).join('\n')
  : '';

// ── Pass through all fields + add formatted text ─────────────────────────────
return [{
  json: {
    ...data,
    missing_preview_text,
    anomaly_lines_text,
    claude_gap_text,
    claude_anomaly_text,
    prd_link_text,
    quick_wins_text,
  }
}];
