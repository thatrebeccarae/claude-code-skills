// n8n Code node: Build Anthropic API request for gap analysis
// Runs after Compare Events (only when gaps_found === true).
// Output feeds an HTTP Request node calling POST https://api.anthropic.com/v1/messages

// ── 1. Pull inputs ────────────────────────────────────────────────────────────
const comparison = $('Compare Events').first().json;
const specRaw    = $('Read Event Spec').first().json.data;

// ── 2. Parse event spec ───────────────────────────────────────────────────────
const spec = typeof specRaw === 'string' ? JSON.parse(specRaw) : specRaw;

// ── 3. Build spec lookup: event_name → full event object (incl. GTM config) ──
const specByName = {};
for (const group of (spec.event_groups || [])) {
  for (const ev of (group.events || [])) {
    specByName[ev.name] = {
      ...ev,
      group_name : group.group_name ?? null,
      phase      : group.phase      ?? null,
    };
  }
}

// ── 4. Enrich missing events with full GTM config from spec ──────────────────
const enrichedMissing = (comparison.missing_events || []).map(me => {
  const full = specByName[me.name] || {};
  return {
    name             : me.name,
    group            : me.group ?? full.group_name,
    phase            : me.phase ?? full.phase,
    priority         : me.priority ?? full.priority,
    replaces         : me.replaces ?? full.replaces ?? null,
    description      : full.description ?? null,
    fires_on         : full.fires_on ?? null,
    required_params  : full.required_params ?? [],
    gtm              : full.gtm ?? null,
  };
});

// ── 5. Build compact user message ────────────────────────────────────────────
// Summarize missing events by group to reduce token usage
const byGroup = {};
for (const e of enrichedMissing) {
  const g = e.group || 'Other';
  if (!byGroup[g]) byGroup[g] = { phase: e.phase, events: [] };
  byGroup[g].events.push({
    name: e.name,
    priority: e.priority,
    trigger_type: e.gtm?.trigger_type ?? 'unknown',
    requires_datalayer: e.gtm?.requires_datalayer ?? false,
    datalayer_vars: e.gtm?.datalayer_variables ?? [],
  });
}

// Top 10 unexpected events only (by volume)
const topUnexpected = (comparison.unexpected_events || [])
  .sort((a, b) => (b.count || 0) - (a.count || 0))
  .slice(0, 10)
  .map(e => `${e.name} (${e.count} events, ${e.users} users)`);

const userContent = [
  `Client: ${comparison.client} | Property: ${comparison.ga4_property} | Date: ${comparison.run_date}`,
  `Coverage: ${comparison.coverage_pct}% (${comparison.implemented}/${comparison.total_spec_events})`,
  '',
  '## Missing Events by Group',
  ...Object.entries(byGroup).map(([group, data]) => {
    const events = data.events.map(e => {
      const dl = e.datalayer_vars.length > 0 ? ` [dataLayer: ${e.datalayer_vars.join(', ')}]` : '';
      return `  - ${e.name} (${e.priority}, ${e.trigger_type}${dl})`;
    }).join('\n');
    return `\n### ${group} (Phase ${data.phase})\n${events}`;
  }),
  '',
  '## Top Unexpected Events (not in spec)',
  topUnexpected.map(e => `- ${e}`).join('\n'),
].join('\n');

// ── 6. Build Anthropic messages API request body ─────────────────────────────
const systemPrompt = [
  'You are a GA4/GTM analytics expert.',
  'Analyze missing events and provide implementation recommendations.',
  'Focus on practical, actionable GTM configurations.',
  'Group recommendations by implementation phase.',
  'For each event, specify the exact GTM tag type, trigger configuration, and any dataLayer requirements.',
  '',
  'CRITICAL: Respond with ONLY valid JSON. No markdown fences (```), no commentary outside the JSON.',
  'Be concise — max 3 events per quick_wins, max 4 phases, max 5 unexpected_event_analysis entries.',
  'Use this exact schema:',
  '',
  '{"summary":"2-3 sentences","quick_wins":[{"event_name":"str","reason":"str","gtm_config":{"tag_type":"str","trigger_type":"str","trigger_config":"str"}}],"phases":[{"phase_number":1,"group_name":"str","description":"str","events":[{"name":"str","priority":"str","trigger_type":"str","datalayer_requirements":["var"],"engineering_notes":"str"}],"engineering_effort":"str"}],"unexpected_event_analysis":[{"unexpected_event":"str","likely_spec_match":"str|null","recommendation":"str"}]}',
].join('\n');

const anthropic_request_body = {
  model      : 'claude-sonnet-4-6',
  max_tokens : 8192,
  system     : systemPrompt,
  messages   : [
    { role: 'user', content: userContent },
  ],
};

// ── 7. Return ────────────────────────────────────────────────────────────────
return [{ json: { anthropic_request_body } }];
