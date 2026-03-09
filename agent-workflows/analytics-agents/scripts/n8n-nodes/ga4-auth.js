// n8n Code node: Google Service Account OAuth2 Token
// Reads a SA JSON key file, builds a JWT, and exchanges it for an access token.

const fs = require('fs');
const crypto = require('crypto');

// --- 1. Load the service account JSON ---
const saKeyPath = $input.first().json.saKeyPath;

if (!saKeyPath) {
  throw new Error('Input must include "saKeyPath" field pointing to the service account JSON file.');
}

const saJson = JSON.parse(fs.readFileSync(saKeyPath, 'utf8'));

const {
  client_email: clientEmail,
  private_key: privateKey,
  private_key_id: privateKeyId,
} = saJson;

if (!clientEmail || !privateKey) {
  throw new Error('Service account JSON is missing "client_email" or "private_key".');
}

// --- 2. Build the JWT header and claim set ---
const scope = 'https://www.googleapis.com/auth/analytics.readonly';
const tokenUri = 'https://oauth2.googleapis.com/token';
const now = Math.floor(Date.now() / 1000);
const expiry = now + 3600; // Token valid for 1 hour

const header = {
  alg: 'RS256',
  typ: 'JWT',
  kid: privateKeyId,
};

const claimSet = {
  iss: clientEmail,
  scope: scope,
  aud: tokenUri,
  iat: now,
  exp: expiry,
};

// --- 3. Base64url-encode (no padding, URL-safe) ---
function base64url(str) {
  return Buffer.from(str)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

const encodedHeader = base64url(JSON.stringify(header));
const encodedClaims = base64url(JSON.stringify(claimSet));
const signingInput = `${encodedHeader}.${encodedClaims}`;

// --- 4. Sign the JWT with RS256 ---
const sign = crypto.createSign('RSA-SHA256');
sign.update(signingInput);
sign.end();

const normalizedKey = privateKey.replace(/\\n/g, '\n');
const signature = sign.sign(normalizedKey);
const encodedSignature = signature
  .toString('base64')
  .replace(/\+/g, '-')
  .replace(/\//g, '_')
  .replace(/=/g, '');

const jwt = `${signingInput}.${encodedSignature}`;

// --- 5. Exchange JWT for access token ---
const response = await fetch(tokenUri, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    assertion: jwt,
  }),
});

if (!response.ok) {
  const errorBody = await response.text();
  throw new Error(`Token exchange failed (${response.status}): ${errorBody}`);
}

const tokenData = await response.json();

if (!tokenData.access_token) {
  throw new Error(`No access_token in response: ${JSON.stringify(tokenData)}`);
}

// --- 6. Return token for downstream HTTP Request nodes ---
// Use: Bearer {{ $json.access_token }}
return [
  {
    json: {
      access_token: tokenData.access_token,
      token_type: tokenData.token_type,
      expires_in: tokenData.expires_in,
      issued_at: now,
    },
  },
];
