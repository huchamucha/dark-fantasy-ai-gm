export async function sendTurn(campaignId: string, characterId: string, actionText: string) {
  const response = await fetch(`/api/campaigns/${campaignId}/turns`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      character_id: characterId,
      action_text: actionText,
    }),
  });

  return response.json();
}
