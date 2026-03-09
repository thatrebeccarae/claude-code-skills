// execute-gtm-writes.js
// n8n Code node — creates GTM variables, triggers, and tags sequentially
// with 4-second delays between API calls to respect rate limits.
// Deduplicates by listing existing resources before creating.
//
// Input node: "Build GTM Resources"
// Auth node:  "GTM Token Exchange"

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// ---------------------------------------------------------------------------
// Pull inputs
// ---------------------------------------------------------------------------
const buildOutput = $('Build GTM Resources').first().json;

const {
  workspace_id,
  account_id,
  container_id,
  variables = [],
  triggers  = [],
  tags      = [],
} = buildOutput;

const accessToken = $('GTM Token Exchange').first().json.access_token;

if (!accessToken) {
  throw new Error('No access_token found from GTM Token Exchange node.');
}
if (!workspace_id || !account_id || !container_id) {
  throw new Error('Missing workspace_id, account_id, or container_id in Build GTM Resources output.');
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const BASE_URL      = 'https://tagmanager.googleapis.com/tagmanager/v2';
const WORKSPACE_PATH = `accounts/${account_id}/containers/${container_id}/workspaces/${workspace_id}`;

const authHeaders = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type':  'application/json',
};

// ---------------------------------------------------------------------------
// HTTP helper
// ---------------------------------------------------------------------------
async function gtmRequest(method, path, body) {
  const url = `${BASE_URL}/${path}`;

  try {
    const opts = {
      method,
      url,
      headers: authHeaders,
      json: true,
      returnFullResponse: false,
    };
    if (body !== undefined) {
      opts.body = body;
    }
    const response = await this.helpers.httpRequest(opts);
    return response;
  } catch (err) {
    const detail = err.cause?.response?.body
      || err.response?.body
      || err.description
      || err.message
      || String(err);
    const msg = typeof detail === 'object' ? JSON.stringify(detail) : String(detail);
    throw new Error(`GTM API error: ${msg}`);
  }
}

const httpCall = gtmRequest.bind(this);

// ---------------------------------------------------------------------------
// Payload sanitiser — strips fields whose names start with "_"
// ---------------------------------------------------------------------------
function sanitisePayload(payload) {
  const clean = {};
  for (const [key, value] of Object.entries(payload)) {
    if (!key.startsWith('_')) {
      clean[key] = value;
    }
  }
  return clean;
}

// ---------------------------------------------------------------------------
// Deduplication: list existing resources in workspace
// ---------------------------------------------------------------------------
const existingVarNames = new Set();
const existingTriggerNames = new Set();
const existingTagNames = new Set();

// Also build trigger name → ID map from existing triggers (for tag resolution)
const triggerMap = {};

try {
  const varResp = await httpCall('GET', `${WORKSPACE_PATH}/variables`);
  for (const v of (varResp.variable || [])) {
    if (v.name) existingVarNames.add(v.name);
  }
} catch (err) {
  // 404 means no variables exist yet — that's fine
}
await delay(4000);

try {
  const trigResp = await httpCall('GET', `${WORKSPACE_PATH}/triggers`);
  for (const t of (trigResp.trigger || [])) {
    if (t.name) {
      existingTriggerNames.add(t.name);
      triggerMap[t.name] = t.triggerId;
    }
  }
} catch (err) {
  // 404 means no triggers exist yet
}
await delay(4000);

try {
  const tagResp = await httpCall('GET', `${WORKSPACE_PATH}/tags`);
  for (const t of (tagResp.tag || [])) {
    if (t.name) existingTagNames.add(t.name);
  }
} catch (err) {
  // 404 means no tags exist yet
}
await delay(4000);

// ---------------------------------------------------------------------------
// Accumulators
// ---------------------------------------------------------------------------
const created_variables = [];
const created_triggers  = [];
const created_tags      = [];
const skipped           = [];
const errors            = [];

// ---------------------------------------------------------------------------
// 1. Create variables (skip existing)
// ---------------------------------------------------------------------------
for (const variable of variables) {
  const name = variable.name || '(unnamed variable)';
  if (existingVarNames.has(name)) {
    skipped.push({ resource_type: 'variable', name, reason: 'already exists' });
    continue;
  }
  try {
    const payload  = sanitisePayload(variable);
    const response = await httpCall('POST', `${WORKSPACE_PATH}/variables`, payload);
    created_variables.push({ name: response.name, variableId: response.variableId });
  } catch (err) {
    errors.push({
      resource_type: 'variable',
      name,
      error_message: err.message || String(err),
    });
  }
  await delay(4000);
}

// ---------------------------------------------------------------------------
// 2. Create triggers (skip existing, populate triggerMap)
// ---------------------------------------------------------------------------
for (const trigger of triggers) {
  const name = trigger.name || '(unnamed trigger)';
  if (existingTriggerNames.has(name)) {
    skipped.push({ resource_type: 'trigger', name, reason: 'already exists' });
    continue; // triggerMap already populated from GET above
  }
  try {
    const payload  = sanitisePayload(trigger);
    const response = await httpCall('POST', `${WORKSPACE_PATH}/triggers`, payload);
    const created  = { name: response.name, triggerId: response.triggerId };
    created_triggers.push(created);
    triggerMap[response.name] = response.triggerId;
  } catch (err) {
    errors.push({
      resource_type: 'trigger',
      name,
      error_message: err.message || String(err),
    });
  }
  await delay(4000);
}

// ---------------------------------------------------------------------------
// 3. Create tags (skip existing, resolve trigger references first)
// ---------------------------------------------------------------------------
for (const tag of tags) {
  const name         = tag.name || '(unnamed tag)';
  const triggerName  = tag._trigger_name;

  if (existingTagNames.has(name)) {
    skipped.push({ resource_type: 'tag', name, reason: 'already exists' });
    continue;
  }

  try {
    const payload = sanitisePayload(tag);

    // Resolve the firing trigger
    if (triggerName) {
      const triggerId = triggerMap[triggerName];
      if (triggerId) {
        payload.firingTriggerId = [triggerId];
      } else {
        errors.push({
          resource_type: 'tag_trigger_lookup',
          name,
          error_message: `Could not resolve trigger "${triggerName}" for tag "${name}" — trigger may not have been created successfully.`,
        });
      }
    }

    const response = await httpCall('POST', `${WORKSPACE_PATH}/tags`, payload);
    created_tags.push({
      name:            response.name,
      tagId:           response.tagId,
      firingTriggerId: response.firingTriggerId || payload.firingTriggerId || [],
    });
  } catch (err) {
    errors.push({
      resource_type: 'tag',
      name,
      error_message: err.message || String(err),
    });
  }
  await delay(4000);
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------
const total_created =
  created_variables.length + created_triggers.length + created_tags.length;
const total_skipped = skipped.length;
const total_errors = errors.length;

return [{
  json: {
    created_variables,
    created_triggers,
    created_tags,
    skipped,
    errors,
    total_created,
    total_skipped,
    total_errors,
    workspace_id,
    workspace_url: `https://tagmanager.google.com/#/container/accounts/${account_id}/containers/${container_id}/workspaces/${workspace_id}`,
  },
}];
