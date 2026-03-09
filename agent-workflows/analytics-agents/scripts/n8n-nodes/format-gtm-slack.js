// n8n Code node: Format GTM Slack Block Kit message bodies (Phase 5)
// Builds three message bodies for different GTM pipeline notification scenarios.
// Place after workspace preflight / resource creation nodes, before Slack HTTP Request nodes.
//
// Inputs:
//   $('Read Config').first().json  — client_name, slack.channel, gtm.account_id, gtm.container_id
//   $('Set Slack Token').first().json.slack_token
//   $input.first().json            — varies by context (route, workspace_id, resource creation results)
//
// Outputs (all in one json object):
//   slack_token            — passed through for downstream HTTP nodes
//   channel                — resolved from config
//   approval_request_body  — JSON string, use for pre-write approval gate
//   workspace_limit_body   — JSON string, use when workspace count >= 3
//   gtm_complete_body      — JSON string, use after resources are created

const input  = $input.first().json;
const config = $('Read Config').first().json;
const slackToken = $('Set Slack Token').first().json?.slack_token ?? '';

// ── Shared resolved values ────────────────────────────────────────────────────

const clientName  = config?.client_name    ?? 'Unknown Client';
const channel     = config?.slack?.channel ?? '#analytics';
const accountId   = config?.gtm?.account_id   ?? '';
const containerId = config?.gtm?.container_id ?? '';

// ── Helpers ───────────────────────────────────────────────────────────────────

function truncate(str, max) {
  if (!str) return '';
  const s = String(str);
  if (s.length <= max) return s;
  return s.slice(0, max).replace(/\s+\S*$/, '') + '…';
}

// ── 1. approval_request_body ─────────────────────────────────────────────────
// Sent before GTM writes; requests human approval.

const approvalInput     = input;
const eventCount        = approvalInput?.event_count          ?? approvalInput?.events?.length ?? 0;
const estimatedSeconds  = approvalInput?.estimated_seconds    ?? approvalInput?.estimated_time ?? 0;
const claudeSummary     = truncate(approvalInput?.claude_summary ?? approvalInput?.summary ?? '', 500);
const prdFilename       = approvalInput?.prd_filename         ?? approvalInput?.prd_path ?? '';

// Quick wins: array of strings or objects with name/description
const rawQuickWins = approvalInput?.quick_wins
  ?? approvalInput?.claude_analysis?.quick_wins
  ?? [];
const quickWinLines = (Array.isArray(rawQuickWins) ? rawQuickWins : [])
  .slice(0, 5)
  .map(w => `• ${typeof w === 'string' ? w : w.name ?? w.description ?? JSON.stringify(w)}`)
  .join('\n') || '• No quick wins identified';

const approvalMsg = {
  channel,
  text: `GTM Implementation Request — ${clientName}`,
  blocks: [
    {
      type: 'header',
      text: { type: 'plain_text', text: '🔧 GTM Implementation Request' },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: [
          `*Client:* ${clientName}`,
          `*Events to implement:* ${eventCount}`,
          `*Estimated time:* ${estimatedSeconds}s`,
          '',
          claudeSummary,
        ].filter(line => line !== null && line !== undefined).join('\n'),
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Quick Wins:*\n${quickWinLines}`,
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `📋 *PRD:* implementation/${prdFilename}`,
      },
    },
    {
      type: 'actions',
      elements: [
        {
          type: 'button',
          text: { type: 'plain_text', text: '✅ Approve' },
          style: 'primary',
          value: 'approve',
        },
        {
          type: 'button',
          text: { type: 'plain_text', text: '❌ Reject' },
          style: 'danger',
          value: 'reject',
        },
      ],
    },
  ],
};

// ── 2. workspace_limit_body ───────────────────────────────────────────────────
// Sent when GTM container already has 3/3 workspaces.

const limitMsg = {
  channel,
  text: `GTM Workspace Limit Reached — ${clientName}`,
  blocks: [
    {
      type: 'header',
      text: { type: 'plain_text', text: '⚠️ GTM Workspace Limit' },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `Cannot create workspace. ${clientName} GTM has 3/3 workspaces in use.\n\nFree a workspace and re-trigger the pipeline.`,
      },
    },
  ],
};

// ── 3. gtm_complete_body ──────────────────────────────────────────────────────
// Sent after workspace and GTM resources are successfully created.

const workspaceName   = input?.workspace_name   ?? input?.existing_agent_workspace?.name ?? 'claude-workspace';
const workspaceId     = input?.workspace_id     ?? input?.existing_agent_workspace?.workspaceId ?? '';
const varCount        = input?.variable_count   ?? input?.var_count     ?? input?.variables?.length   ?? 0;
const triggerCount    = input?.trigger_count    ?? input?.triggers?.length  ?? 0;
const tagCount        = input?.tag_count        ?? input?.tags?.length      ?? 0;
const docPath         = input?.doc_path         ?? input?.prd_path          ?? prdFilename ?? '';

// GTM workspace deep-link (falls back gracefully if IDs are missing)
const gtmWorkspaceUrl = accountId && containerId && workspaceId
  ? `https://tagmanager.google.com/#/container/accounts/${accountId}/containers/${containerId}/workspaces/${workspaceId}`
  : 'https://tagmanager.google.com';

const completeMsg = {
  channel,
  text: `GTM Workspace Ready — ${clientName}`,
  blocks: [
    {
      type: 'header',
      text: { type: 'plain_text', text: '✅ GTM Workspace Ready for Review' },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: [
          `*Client:* ${clientName}`,
          `*Workspace:* ${workspaceName}`,
          `*Resources created:* ${varCount} variables, ${triggerCount} triggers, ${tagCount} tags`,
        ].join('\n'),
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `🔗 <${gtmWorkspaceUrl}|Open in GTM>\n📋 Implementation doc: ${docPath}`,
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: [
          '*Review Checklist:*',
          '• Preview mode: verify each tag fires',
          '• Check dataLayer variables',
          '• Share with engineering',
          '• Engineering publishes workspace',
        ].join('\n'),
      },
    },
  ],
};

// ── Return ────────────────────────────────────────────────────────────────────

return [{
  json: {
    slack_token:            slackToken,
    channel,
    approval_request_body:  JSON.stringify(approvalMsg),
    workspace_limit_body:   JSON.stringify(limitMsg),
    gtm_complete_body:      JSON.stringify(completeMsg),
  },
}];
