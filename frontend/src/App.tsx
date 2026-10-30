import React, { useState } from 'react';

const sampleNarrative = 'Колокола вдалеке звенят, и город будто затаил дыхание. Пепельная тьма кружится у ваших ног, как будто кто-то шепчет из-под земли.';

export default function App() {
  const [input, setInput] = useState('');
  const [narrative, setNarrative] = useState(sampleNarrative);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/campaigns/campaign_1/turns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: 'char_1',
          action_text: input || 'Исследую город и ищу следы тени.',
        }),
      });

      const data = await response.json();
      setNarrative(data.narrative || sampleNarrative);
    } catch (error) {
      setNarrative(sampleNarrative);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f172a',
      color: '#e2e8f0',
      fontFamily: 'Segoe UI, sans-serif',
      padding: '32px',
    }}>
      <div style={{ maxWidth: 980, margin: '0 auto' }}>
        <h1 style={{ fontSize: 36, marginBottom: 12 }}>Пепельная Корона</h1>
        <p style={{ color: '#a5b4fc', marginBottom: 20 }}>Тёмное фэнтези AI GM</p>

        <div style={{
          background: '#111827',
          border: '1px solid #374151',
          borderRadius: 12,
          padding: 20,
          boxShadow: '0 10px 15px rgba(0,0,0,0.2)',
        }}>
          <p>{narrative}</p>
        </div>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={5}
          placeholder="Что вы делаете?"
          style={{
            width: '100%',
            marginTop: 20,
            padding: 14,
            borderRadius: 10,
            border: '1px solid #475569',
            background: '#0b1120',
            color: '#e2e8f0',
            resize: 'vertical',
          }}
        />

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            marginTop: 16,
            background: '#7c3aed',
            color: '#fff',
            border: 'none',
            borderRadius: 10,
            padding: '12px 20px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? 'Рассуждаю...' : 'Совершить действие'}
        </button>
      </div>
    </div>
  );
}
