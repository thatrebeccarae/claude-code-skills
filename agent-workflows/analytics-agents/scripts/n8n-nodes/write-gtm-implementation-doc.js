// n8n Code node: Generate GTM implementation doc after workspace resources are created
// Runs after Create GTM Resources. Outputs markdown + vault path for Save Report.

// ── 1. Pull inputs ────────────────────────────────────────────────────────────
const config       = $('Read Config').first().json;
const resourcePlan = $('Build GTM Resources').first().json;
const created      = $input.first().json;
const analysis     = $('Parse Gap Analysis').first().json.claude_analysis ?? {};

const client_name  = config.client_name ?? 'Unknown Client';
const account_id   = config.gtm?.account_id ?? '';
const container_id = config.gtm?.container_id ?? '';
const impl_dir     = config.vault?.implementation_dir
  ?? `10-Clients/${client_name.toLowerCase().replace(/\s+/g, '-')}/analytics/implementation`;

// ── 2. Resolve created vs. planned resources ─────────────────────────────────
// Prefer created_* arrays (have GTM resource IDs); fall back to planned
const variables = created.created_variables?.length
  ? created.created_variables
  : (resourcePlan.variables ?? []);

const triggers = created.created_triggers?.length
  ? created.created_triggers
  : (resourcePlan.triggers ?? []);

const tags = created.created_tags?.length
  ? created.created_tags
  : (resourcePlan.tags ?? []);

// Workspace info — may live on created output or resource plan
const workspace_id   = created.workspace_id   ?? resourcePlan.workspace_id   ?? '';
const workspace_name = created.workspace_name ?? resourcePlan.workspace_name ?? 'New Workspace';

// ── 3. Helpers ────────────────────────────────────────────────────────────────
const today   = new Date().toISOString().slice(0, 10);
const fence   = (lang, content) => '```' + lang + '\n' + content + '\n```';
const h2      = (t) => `## ${t}`;
const h3      = (t) => `### ${t}`;

const gtmWorkspaceUrl = workspace_id
  ? `https://tagmanager.google.com/#/container/accounts/${account_id}/containers/${container_id}/workspaces/${workspace_id}`
  : `https://tagmanager.google.com/#/container/accounts/${account_id}/containers/${container_id}/workspaces`;

// ── 4. Frontmatter ────────────────────────────────────────────────────────────
const frontmatter = [
  '---',
  `context: professional`,
  `type: gtm-implementation`,
  `client: ${client_name}`,
  `created: ${today}`,
  `gtm_account: "${account_id}"`,
  `gtm_container: "${container_id}"`,
  `workspace: ${workspace_name}`,
  `status: pending-review`,
  '---',
].join('\n');

// ── 5. Summary section ────────────────────────────────────────────────────────
const summaryText = analysis.summary ?? 'Review the created resources below before publishing the workspace.';

const summarySection = [
  h2('Summary'),
  '',
  summaryText,
  '',
  `Workspace: [${workspace_name}](${gtmWorkspaceUrl})`,
].join('\n');

// ── 6. Variables table ────────────────────────────────────────────────────────
let variablesSection;
if (variables.length === 0) {
  variablesSection = [h3(`Variables (0)`), '', 'No variables created.'].join('\n');
} else {
  const rows = variables.map(v => {
    const name    = v.name          ?? v.variable_name ?? '—';
    const dlKey   = v.parameter?.find?.(p => p.key === 'name')?.value
                 ?? v.data_layer_key
                 ?? v.dlKey
                 ?? '—';
    const type    = v.type ?? v.variable_type ?? 'Data Layer Variable';
    return `| ${name} | ${dlKey} | ${type} |`;
  });

  variablesSection = [
    h3(`Variables (${variables.length})`),
    '',
    '| Variable Name | Data Layer Key | Type |',
    '|---|---|---|',
    ...rows,
  ].join('\n');
}

// ── 7. Triggers table ─────────────────────────────────────────────────────────
let triggersSection;
if (triggers.length === 0) {
  triggersSection = [h3(`Triggers (0)`), '', 'No triggers created.'].join('\n');
} else {
  const rows = triggers.map(t => {
    const name   = t.name         ?? t.trigger_name ?? '—';
    const type   = t.type         ?? t.trigger_type ?? '—';
    // Custom event triggers store the event name in filter or customEventFilter
    const filter = t.customEventFilter?.[0]?.parameter?.find?.(p => p.key === 'arg1')?.value
                ?? t.filter?.[0]?.parameter?.find?.(p => p.key === 'arg1')?.value
                ?? t.event_name
                ?? t.filter
                ?? '—';
    return `| ${name} | ${type} | ${filter} |`;
  });

  triggersSection = [
    h3(`Triggers (${triggers.length})`),
    '',
    '| Trigger Name | Type | Event/Filter |',
    '|---|---|---|',
    ...rows,
  ].join('\n');
}

// ── 8. Tags table ─────────────────────────────────────────────────────────────
let tagsSection;
if (tags.length === 0) {
  tagsSection = [h3(`Tags (0)`), '', 'No tags created.'].join('\n');
} else {
  const rows = tags.map(t => {
    const name        = t.name     ?? t.tag_name ?? '—';
    // GA4 event name lives in the parameter list under key "eventName"
    const eventName   = t.parameter?.find?.(p => p.key === 'eventName')?.value
                     ?? t.event_name
                     ?? '—';
    // Firing trigger — use first linked trigger name if available
    const triggerName = t.firingTriggerId?.[0]
      ? (triggers.find(tr => tr.triggerId === t.firingTriggerId[0])?.name ?? t.firingTriggerId[0])
      : (t.trigger_name ?? '—');
    // Parameters are the GA4 event parameters (key/value list)
    const params      = t.parameter
      ?.filter?.(p => p.key === 'eventParameters')
      ?.[0]?.list
      ?.map?.(item => item.map?.find?.(m => m.key === 'name')?.value)
      ?.filter?.(Boolean)
      ?.join(', ')
      ?? t.parameters?.map?.(p => p.name ?? p.key)?.join(', ')
      ?? '—';
    return `| ${name} | ${eventName} | ${triggerName} | ${params} |`;
  });

  tagsSection = [
    h3(`Tags (${tags.length})`),
    '',
    '| Tag Name | Event | Trigger | Parameters |',
    '|---|---|---|---|',
    ...rows,
  ].join('\n');
}

// ── 9. Created Resources section ─────────────────────────────────────────────
const createdResourcesSection = [
  h2('Created Resources'),
  '',
  variablesSection,
  '',
  triggersSection,
  '',
  tagsSection,
].join('\n');

// ── 10. Review Checklist ──────────────────────────────────────────────────────
const reviewChecklist = [
  h2('Review Checklist'),
  '',
  `- [ ] Open workspace in GTM: [${workspace_name}](${gtmWorkspaceUrl})`,
  '- [ ] Verify each tag fires correctly in Preview mode',
  '- [ ] Check dataLayer variables are populated',
  '- [ ] Confirm event parameters match GA4 expected schema',
  '- [ ] Share workspace link with engineering team',
  '- [ ] Engineering team clicks "Submit" to publish',
].join('\n');

// ── 11. DataLayer Requirements ────────────────────────────────────────────────
const events = resourcePlan.events_to_implement ?? [];

let dataLayerSection;
if (events.length === 0) {
  dataLayerSection = [
    h2('DataLayer Requirements'),
    '',
    'No events listed — review the resource plan for dataLayer push requirements.',
  ].join('\n');
} else {
  const eventBlocks = events.map(ev => {
    const evName = ev.name ?? ev.event_name ?? 'unknown_event';
    const dlVars = ev.datalayer_requirements ?? ev.parameters ?? [];

    // Build the dataLayer.push snippet
    const paramLines = dlVars.length > 0
      ? dlVars.map(v => {
          const key = typeof v === 'string' ? v : (v.name ?? v.key ?? v);
          return `  ${key}: '<value>',`;
        }).join('\n')
      : '  // no custom parameters required';

    const snippet = `dataLayer.push({\n  event: '${evName}',\n${paramLines}\n});`;

    const lines = [
      `### \`${evName}\``,
      '',
    ];

    if (ev.trigger_config || ev.trigger_type) {
      lines.push(`**Trigger:** ${ev.trigger_config ?? ev.trigger_type}`);
      lines.push('');
    }

    if (dlVars.length > 0) {
      lines.push('**Required dataLayer variables:**');
      dlVars.forEach(v => {
        const key   = typeof v === 'string' ? v : (v.name ?? v.key ?? v);
        const notes = typeof v === 'object' ? (v.notes ?? v.description ?? '') : '';
        lines.push(`- \`${key}\`${notes ? ` — ${notes}` : ''}`);
      });
      lines.push('');
    }

    lines.push(fence('javascript', snippet));

    return lines.join('\n');
  });

  dataLayerSection = [
    h2('DataLayer Requirements'),
    '',
    'Events in this workspace require the following `dataLayer.push` calls from engineering:',
    '',
    ...eventBlocks,
  ].join('\n');
}

// ── 12. Next Steps ────────────────────────────────────────────────────────────
const clientSlug = client_name.replace(/\s+/g, ' ');

const nextStepsSection = [
  h2('Next Steps'),
  '',
  '1. Review workspace in GTM Preview mode',
  `2. Share with ${clientSlug} engineering for dataLayer implementation`,
  '3. Once dataLayer is live, publish the workspace',
].join('\n');

// ── 13. Quick Wins callout (from analysis) ───────────────────────────────────
const quickWins = analysis.quick_wins ?? [];
let quickWinsCallout = '';
if (quickWins.length > 0) {
  const items = quickWins.map(qw => `- **\`${qw.event_name ?? qw}\`**${qw.reason ? ` — ${qw.reason}` : ''}`);
  quickWinsCallout = [
    '',
    '> **Quick Wins identified by analysis:**',
    ...items.map(i => `> ${i}`),
    '',
  ].join('\n');
}

// ── 14. Assemble full document ────────────────────────────────────────────────
const timestamp = new Date().toISOString();

const doc_markdown = [
  frontmatter,
  '',
  `# GTM Implementation: ${client_name} — ${today}`,
  '',
  summarySection,
  quickWinsCallout,
  '',
  createdResourcesSection,
  '',
  reviewChecklist,
  '',
  dataLayerSection,
  '',
  nextStepsSection,
  '',
  '---',
  `*Generated by Analytics Agent pipeline at ${timestamp}*`,
  '',
].join('\n');

// ── 15. Output ────────────────────────────────────────────────────────────────
const doc_path = `${impl_dir}/gtm-${today}-workspace.md`;

return [{
  json: {
    doc_markdown,
    doc_path,
  },
}];
