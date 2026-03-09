// n8n Code node: Parse Anthropic API response for gap analysis
// Runs after the HTTP Request node that calls POST https://api.anthropic.com/v1/messages
// Merges Claude's analysis back with Compare Events data.

// ── 1. Pull inputs ────────────────────────────────────────────────────────────
const apiResponse   = $input.first().json;
const compareData   = $('Compare Events').first().json;

// ── 2. Extract text content from Anthropic response ─────────────────────────
let rawText = '';

if (apiResponse.content && Array.isArray(apiResponse.content)) {
  // Standard Anthropic response shape: { content: [{ type: "text", text: "..." }] }
  const textBlock = apiResponse.content.find(b => b.type === 'text');
  rawText = textBlock?.text ?? '';
} else if (typeof apiResponse.content === 'string') {
  rawText = apiResponse.content;
} else if (apiResponse.error) {
  // API returned an error — pass it through gracefully
  return [{
    json: {
      ...compareData,
      claude_analysis: {
        summary: `Anthropic API error: ${apiResponse.error?.message ?? JSON.stringify(apiResponse.error)}`,
        quick_wins: [],
        phases: [],
        unexpected_event_analysis: [],
        _parse_error: true,
        _raw_error: apiResponse.error,
      },
      claude_gap_summary: `API error — manual review required`,
    },
  }];
}

// ── 3. Parse JSON from Claude's response ────────────────────────────────────
let parsedResponse;

try {
  // Strip markdown code fences if Claude wrapped the JSON despite instructions
  let cleaned = rawText.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\s*\n?/, '').replace(/\n?```\s*$/, '');
  }
  parsedResponse = JSON.parse(cleaned);
} catch (parseErr) {
  // JSON parse failed — wrap raw text in a structured fallback
  parsedResponse = {
    summary: rawText.slice(0, 500) || 'Analysis received but could not be parsed as JSON.',
    quick_wins: [],
    phases: [],
    unexpected_event_analysis: [],
    _parse_error: true,
    _raw_text: rawText,
  };
}

// ── 4. Validate expected keys exist (defensive) ─────────────────────────────
const analysis = {
  summary                    : parsedResponse.summary ?? 'No summary provided.',
  quick_wins                 : Array.isArray(parsedResponse.quick_wins) ? parsedResponse.quick_wins : [],
  phases                     : Array.isArray(parsedResponse.phases) ? parsedResponse.phases : [],
  unexpected_event_analysis  : Array.isArray(parsedResponse.unexpected_event_analysis) ? parsedResponse.unexpected_event_analysis : [],
};

// Preserve parse-error metadata if present
if (parsedResponse._parse_error) {
  analysis._parse_error = true;
  if (parsedResponse._raw_text) analysis._raw_text = parsedResponse._raw_text;
}

// ── 5. Build summary string for downstream Slack / reports ──────────────────
const summaryParts = [analysis.summary];
if (analysis.quick_wins.length > 0) {
  summaryParts.push(`${analysis.quick_wins.length} quick win(s) identified.`);
}
if (analysis.phases.length > 0) {
  const totalPhaseEvents = analysis.phases.reduce((acc, p) => acc + (p.events?.length ?? 0), 0);
  summaryParts.push(`${analysis.phases.length} implementation phase(s) covering ${totalPhaseEvents} events.`);
}
const claude_gap_summary = summaryParts.join(' ');

// ── 6. Merge and return ─────────────────────────────────────────────────────
return [{
  json: {
    ...compareData,
    claude_analysis    : analysis,
    claude_gap_summary : claude_gap_summary,
  },
}];
