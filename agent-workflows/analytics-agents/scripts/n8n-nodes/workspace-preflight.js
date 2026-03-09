// n8n Code node: GTM Workspace Preflight Check
// Receives GTM List Workspaces API response and determines routing for workspace operations.
//
// Inputs:
//   $input.first().json         — HTTP response from GTM List Workspaces API
//                                 Shape: { workspace: [ { workspaceId, name, path, ... } ] }
//   $('Read Config').first().json — Client config with gtm.workspace_name_prefix (default "claude")

const apiResponse = $input.first().json;
const config = $('Read Config').first().json;

// --- 1. Parse workspace list ---
const workspaces = apiResponse.workspace || [];

// --- 2. Count total workspaces ---
const workspace_count = workspaces.length;

// --- 3. Resolve the prefix to match against ---
const prefix = (config?.gtm?.workspace_name_prefix ?? 'claude') + '-';

// --- 4. Check for an existing agent workspace ---
const found = workspaces.find(ws => ws.name && ws.name.startsWith(prefix)) || null;

const existing_agent_workspace = found
  ? {
      workspaceId: found.workspaceId,
      name: found.name,
      path: found.path,
    }
  : null;

// --- 5. Determine route ---
// GTM allows a maximum of 3 workspaces per container.
let route;
if (workspace_count >= 3) {
  route = 'workspace_limit';
} else if (existing_agent_workspace !== null) {
  route = 'existing_workspace';
} else {
  route = 'available';
}

// --- 6. Return result ---
// can_proceed: true if we have a workspace to use (new or existing)
const can_proceed = route === 'available' || route === 'existing_workspace';

return [
  {
    json: {
      route,                    // "available" | "workspace_limit" | "existing_workspace"
      workspace_count,          // number
      existing_agent_workspace, // null or { workspaceId, name, path }
      can_create: route === 'available',
      can_proceed,              // true if we can continue to GTM writes
      // If reusing existing workspace, pass its ID so downstream nodes can use it
      reuse_workspace_id: existing_agent_workspace?.workspaceId ?? null,
    },
  },
];
