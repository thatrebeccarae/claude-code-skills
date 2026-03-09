// Build Anomaly Prompt — n8n Code node
// Runs after Compare Events when anomalies_found === true
// Builds Anthropic Messages API request body for anomaly analysis

const compareData = $('Compare Events').first().json;

const { client, ga4_property, run_date, anomalies } = compareData;

if (!anomalies || anomalies.length === 0) {
  return [{ json: { error: 'No anomalies found in Compare Events output', skip: true } }];
}

const anomalyLines = anomalies.map((a) => {
  const specLabel = a.in_spec ? 'IN event spec' : 'NOT in event spec';
  return `- ${a.event}: previous 7-day count = ${a.previous_count}, current count = ${a.current_count} (${specLabel})`;
});

const userMessage = `Client: ${client}
GA4 Property ID: ${ga4_property}
Run Date: ${run_date}
Total anomalies detected: ${anomalies.length}

The following GA4 events previously had significant volume (>100 in the prior 7-day window) but dropped to exactly 0 in the current period:

${anomalyLines.join('\n')}

Analyze these drops and respond with a JSON object (no markdown fencing) containing:
{
  "urgency": "critical | high | medium | low",
  "summary": "2-3 sentence overview of the situation",
  "likely_causes": [
    { "cause": "description", "probability": "high | medium | low", "affected_events": ["event_name"] }
  ],
  "diagnostic_steps": ["step 1", "step 2"],
  "immediate_actions": ["action 1", "action 2"]
}

Consider: number of affected events, whether they are in the event spec, their previous volume, and common root causes (GTM changes, tag removal, site deployments, data processing delays, traffic shifts).`;

const systemPrompt =
  'You are a GA4 analytics expert specializing in tracking diagnostics. ' +
  'Analyze event anomalies (events that dropped to zero) and provide root cause analysis. ' +
  'Consider common causes: GTM container changes, tag removal/modification, site code deployment, ' +
  'traffic pattern changes, data processing delays. Always respond with valid JSON only.';

const anthropic_request_body = {
  model: 'claude-haiku-4-5-20251001',
  max_tokens: 2048,
  system: systemPrompt,
  messages: [
    {
      role: 'user',
      content: userMessage,
    },
  ],
};

return [{ json: { anthropic_request_body } }];
