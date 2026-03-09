// Parse Anomaly Response — n8n Code node
// Runs after HTTP Request node that calls Anthropic Messages API
// Extracts and parses Claude's analysis, merges with Compare Events data

const compareData = $('Compare Events').first().json;
const apiResponse = $input.first().json;

let rawText = '';

try {
  if (apiResponse.content && Array.isArray(apiResponse.content) && apiResponse.content.length > 0) {
    rawText = apiResponse.content[0].text || '';
  } else if (typeof apiResponse.content === 'string') {
    rawText = apiResponse.content;
  } else {
    rawText = JSON.stringify(apiResponse);
  }
} catch (e) {
  return [
    {
      json: {
        ...compareData,
        claude_anomaly_analysis: { error: 'Failed to extract text from API response', raw: apiResponse },
        claude_anomaly_summary: 'Anomaly analysis complete — review recommended',
      },
    },
  ];
}

let parsedResponse;

try {
  // Strip markdown code fences if present
  const cleaned = rawText.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '').trim();
  parsedResponse = JSON.parse(cleaned);
} catch (e) {
  // Fall back to wrapping raw text
  parsedResponse = {
    urgency: 'unknown',
    summary: rawText.slice(0, 500),
    likely_causes: [],
    diagnostic_steps: [],
    immediate_actions: [],
    _parse_error: 'Claude response was not valid JSON — raw text preserved in summary',
  };
}

const claude_anomaly_summary = parsedResponse.summary || 'Anomaly analysis complete — review recommended';

return [
  {
    json: {
      ...compareData,
      claude_anomaly_analysis: parsedResponse,
      claude_anomaly_summary,
    },
  },
];
