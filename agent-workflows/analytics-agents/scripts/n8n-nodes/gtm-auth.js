// n8n Code node: GTM JWT Builder
// Reads a Google Service Account JSON key file, builds a signed JWT,
// and returns it as { jwt_assertion } for the downstream GTM Token Exchange
// HTTP Request node (POST https://oauth2.googleapis.com/token).

const fs = require('fs');
const crypto = require('crypto');

// --- 1. Load the service account JSON path from client config ---
// Expects "Read Config" node upstream with structure: config.gtm.credentials_file
const saKeyPath = $('Read Config').first().json.gtm.credentials_file;

if (!saKeyPath) {
  throw new Error(
    'Client config is missing "gtm.credentials_file". ' +
    'Ensure the Read Config node provides this field.'
  );
}

const saJson = JSON.parse(fs.readFileSync(saKeyPath, 'utf8'));

const {
  client_email: clientEmail,
  private_key: privateKey,
  private_key_id: privateKeyId,
} = saJson;

if (!clientEmail || !privateKey) {
  throw new Error(
    `Service account file at "${saKeyPath}" is missing "client_email" or "private_key".`
  );
}

// --- 2. Build JWT header and claim set ---
// Scope grants read/write access to GTM containers.
const scope = 'https://www.googleapis.com/auth/tagmanager.edit.containers';
const tokenUri = 'https://oauth2.googleapis.com/token';
const now = Math.floor(Date.now() / 1000);
const expiry = now + 3600; // JWT valid for 1 hour

const header = {
  alg: 'RS256',
  typ: 'JWT',
  kid: privateKeyId, // Key ID ties the JWT to the SA key pair
};

const claimSet = {
  iss: clientEmail,  // Issuer: the service account email
  scope: scope,      // Requested OAuth2 scope
  aud: tokenUri,     // Audience: Google's token endpoint
  iat: now,          // Issued at (Unix seconds)
  exp: expiry,       // Expiry (Unix seconds)
};

// --- 3. Base64url-encode helper (no padding, URL-safe characters) ---
function base64url(str) {
  return Buffer.from(str)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

const encodedHeader = base64url(JSON.stringify(header));
const encodedClaims = base64url(JSON.stringify(claimSet));

// The signing input is the two base64url segments joined by a dot
const signingInput = `${encodedHeader}.${encodedClaims}`;

// --- 4. Sign the JWT with RS256 ---
// Normalize escaped newlines that may appear when the key is stored in JSON
const normalizedKey = privateKey.replace(/\\n/g, '\n');

const sign = crypto.createSign('RSA-SHA256');
sign.update(signingInput);
sign.end();

const signature = sign.sign(normalizedKey);
const encodedSignature = signature
  .toString('base64')
  .replace(/\+/g, '-')
  .replace(/\//g, '_')
  .replace(/=/g, '');

// Assemble the final JWT: header.claims.signature
const jwt_assertion = `${signingInput}.${encodedSignature}`;

// --- 5. Return JWT for the downstream GTM Token Exchange HTTP Request node ---
// That node POSTs to https://oauth2.googleapis.com/token with:
//   grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
//   assertion={{ $json.jwt_assertion }}
return [
  {
    json: {
      jwt_assertion,
    },
  },
];
