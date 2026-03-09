// n8n Code node: Generate implementation PRD from Claude gap analysis
// Runs after Parse Gap Analysis. Outputs markdown + vault path for Save Report.

// ── 1. Pull inputs ────────────────────────────────────────────────────────────
const data   = $input.first().json;
const config = $('Read Config').first().json;

const {
  client,
  ga4_property,
  run_date,
  coverage_pct,
  total_spec_events,
  implemented,
  missing_events       = [],
  unexpected_events    = [],
  claude_analysis      = {},
} = data;

const client_name = config.client_name ?? client;
const impl_dir    = config.vault?.implementation_dir
  ?? `10-Clients/${client}/analytics/implementation`;

// ── 2. Helpers ──────────────────────────────────────────────────────────────
const fmt   = (n) => n == null ? '—' : Number(n).toLocaleString('en-US');
const fence = (lang, content) => '```' + lang + '\n' + content + '\n```';
const h2    = (t) => `## ${t}`;
const h3    = (t) => `### ${t}`;
const h4    = (t) => `#### ${t}`;

// ── 3. Frontmatter ──────────────────────────────────────────────────────────
const frontmatter = [
  '---',
  `type: prd`,
  `context: ${client_name}`,
  `ga4_property: "${ga4_property}"`,
  `coverage_pct: ${coverage_pct}`,
  `created: ${run_date}`,
  `parent: "[[${client}/analytics/_index|${client_name} Analytics]]"`,
  `generated_by: analytics-agent-pipeline`,
  '---',
].join('\n');

// ── 4. Executive summary ────────────────────────────────────────────────────
const summaryText = claude_analysis.summary ?? 'No AI summary available — review raw gap data below.';

const executiveSummary = [
  h2('Executive Summary'),
  '',
  summaryText,
].join('\n');

// ── 5. Current state ────────────────────────────────────────────────────────
const currentState = [
  h2('Current State'),
  '',
  `| Metric | Value |`,
  `|--------|-------|`,
  `| GA4 Property | ${ga4_property} |`,
  `| Spec Coverage | ${coverage_pct}% |`,
  `| Events Implemented | ${implemented} of ${total_spec_events} |`,
  `| Missing Events | ${missing_events.length} |`,
  `| Unexpected Events | ${unexpected_events.length} |`,
  `| Report Date | ${run_date} |`,
].join('\n');

// ── 6. Quick wins ───────────────────────────────────────────────────────────
const quickWins = claude_analysis.quick_wins ?? [];
let quickWinsSection;

if (quickWins.length === 0) {
  quickWinsSection = [h2('Quick Wins'), '', 'No quick wins identified.'].join('\n');
} else {
  const items = quickWins.map(qw => {
    const lines = [
      `- **\`${qw.event_name}\`**${qw.reason ? ` — ${qw.reason}` : ''}`,
    ];
    if (qw.gtm_config) {
      lines.push(`  - Tag type: \`${qw.gtm_config.tag_type ?? '—'}\``);
      lines.push(`  - Trigger: \`${qw.gtm_config.trigger_type ?? '—'}\``);
      if (qw.gtm_config.trigger_config) {
        lines.push(`  - Config: ${qw.gtm_config.trigger_config}`);
      }
    }
    return lines.join('\n');
  });

  quickWinsSection = [
    h2(`Quick Wins (${quickWins.length})`),
    '',
    'These events can be implemented without dataLayer or engineering changes.',
    '',
    ...items,
  ].join('\n');
}

// ── 7. Phased implementation plan ───────────────────────────────────────────
const phases = claude_analysis.phases ?? [];
let phasesSection;

if (phases.length === 0) {
  phasesSection = [h2('Implementation Plan'), '', 'No phased plan available.'].join('\n');
} else {
  const phaseBlocks = phases.map(phase => {
    const events = phase.events ?? [];
    const lines  = [
      h3(`Phase ${phase.phase_number ?? '?'}: ${phase.group_name ?? 'Unnamed'}`),
      '',
    ];

    if (phase.description) {
      lines.push(`> ${phase.description}`);
      lines.push('');
    }

    if (phase.engineering_effort) {
      lines.push(`**Estimated effort:** ${phase.engineering_effort}`);
      lines.push('');
    }

    if (events.length === 0) {
      lines.push('No events listed for this phase.');
    } else {
      for (const ev of events) {
        lines.push(h4(`\`${ev.name}\` (${ev.priority ?? '—'})`));
        lines.push('');
        lines.push('| Config | Value |');
        lines.push('|--------|-------|');
        lines.push(`| GTM Tag Type | \`${ev.gtm_tag_type ?? '—'}\` |`);
        lines.push(`| Trigger Type | \`${ev.trigger_type ?? '—'}\` |`);
        lines.push(`| Trigger Config | ${ev.trigger_config ?? '—'} |`);

        const dlReqs = ev.datalayer_requirements ?? [];
        if (dlReqs.length > 0) {
          lines.push(`| dataLayer Variables | ${dlReqs.map(v => '`' + v + '`').join(', ')} |`);
        } else {
          lines.push(`| dataLayer Variables | None |`);
        }

        lines.push('');

        if (ev.engineering_notes) {
          lines.push(`**Engineering notes:** ${ev.engineering_notes}`);
          lines.push('');
        }
      }
    }

    return lines.join('\n');
  });

  phasesSection = [
    h2('Implementation Plan'),
    '',
    ...phaseBlocks,
  ].join('\n');
}

// ── 8. Unexpected events analysis ───────────────────────────────────────────
const unexpectedAnalysis = claude_analysis.unexpected_event_analysis ?? [];
let unexpectedSection;

if (unexpectedAnalysis.length === 0 && unexpected_events.length === 0) {
  unexpectedSection = [h2('Unexpected Events'), '', 'No unexpected events detected.'].join('\n');
} else {
  const lines = [
    h2('Unexpected Events Analysis'),
    '',
    'These events are firing in GA4 but are not in the event spec.',
    '',
  ];

  if (unexpectedAnalysis.length > 0) {
    lines.push('| GA4 Event | Likely Spec Match | Recommendation | Confidence |');
    lines.push('|-----------|-------------------|----------------|------------|');
    for (const ua of unexpectedAnalysis) {
      lines.push(
        `| \`${ua.unexpected_event}\` | ${ua.likely_spec_match ? '`' + ua.likely_spec_match + '`' : '—'} | ${ua.recommendation ?? '—'} | ${ua.confidence ?? '—'} |`
      );
    }
    lines.push('');
  }

  // Also list raw unexpected events not covered by Claude's analysis
  const analyzedNames = new Set(unexpectedAnalysis.map(ua => ua.unexpected_event));
  const unanalyzed    = unexpected_events.filter(ue => !analyzedNames.has(ue.name));

  if (unanalyzed.length > 0) {
    lines.push(h3('Other Unexpected Events (not analyzed)'));
    lines.push('');
    lines.push('| Event | Count (7d) | Users (7d) |');
    lines.push('|-------|------------|------------|');
    for (const ue of unanalyzed) {
      lines.push(`| \`${ue.name}\` | ${fmt(ue.count)} | ${fmt(ue.users)} |`);
    }
    lines.push('');
  }

  unexpectedSection = lines.join('\n');
}

// ── 9. Next steps ───────────────────────────────────────────────────────────
const nextSteps = [
  h2('Next Steps'),
  '',
  '1. **Review quick wins** — implement GTM-only events first for immediate coverage gains.',
  '2. **Scope engineering work** — share Phase 1 dataLayer requirements with dev team.',
  '3. **Validate unexpected events** — confirm whether any map to spec events (rename vs. remove).',
  '4. **Re-run pipeline** after implementation to measure coverage improvement.',
  `5. **Target:** Move from ${coverage_pct}% to ≥80% coverage within 2 sprints.`,
].join('\n');

// ── 10. Parse-error notice (if Claude response was malformed) ───────────────
let parseNotice = '';
if (claude_analysis._parse_error) {
  parseNotice = [
    '',
    '> **Note:** The AI analysis response could not be fully parsed.',
    '> Some sections above may be incomplete. Review the raw pipeline output for full details.',
    '',
  ].join('\n');
}

// ── 11. Assemble full PRD ───────────────────────────────────────────────────
const timestamp = new Date().toISOString();

const prd_markdown = [
  frontmatter,
  '',
  `# ${client_name} — GA4 Implementation PRD`,
  '',
  executiveSummary,
  '',
  currentState,
  '',
  quickWinsSection,
  '',
  phasesSection,
  '',
  unexpectedSection,
  '',
  nextSteps,
  parseNotice,
  '',
  '---',
  `*Generated by Analytics Agent pipeline at ${timestamp}*`,
  '',
].join('\n');

// ── 12. Output ──────────────────────────────────────────────────────────────
const prd_path = `${impl_dir}/${run_date}-gap-analysis-prd.md`;

return [{
  json: {
    prd_markdown,
    prd_path,
  },
}];
