import React, { useEffect, useMemo, useState } from 'react';

const DEFAULT_ACTION = 'Иду к монастырю и хочу понять, кто зазывает тень из-под города.';

export default function App() {
  const [campaignId, setCampaignId] = useState('');
  const [characterId, setCharacterId] = useState('');
  const [campaignName, setCampaignName] = useState('Пепельная Корона');
  const [name, setName] = useState('Эдрик');
  const [className, setClassName] = useState('Рыцарь Пепельного Ордена');
  const [action, setAction] = useState(DEFAULT_ACTION);
  const [narrative, setNarrative] = useState('Колокола Серебряного Логова звонят без причины. Тьма под городом шевелится, и вы слышите зов из-под земли.');
  const [loading, setLoading] = useState(false);

  const classOptions = useMemo(() => [
    'Рыцарь Пепельного Ордена',
    'Алхимик-отшельник',
    'Охотник на чудовищ',
    'Монах-оккультист',
    'Посланник тени',
  ], []);

  useEffect(() => {
    setCampaignId('campaign_1');
  }, []);

  const createCampaign = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: campaignName, setting: 'dark_fantasy', tone: 'dark_fantasy' }),
      });
      const data = await response.json();
      setCampaignId(data.id);
      setNarrative(`Кампания "${data.title}" создана. В Серебряном Логове начинается тёмный рассвет.`);
    } catch (error) {
      setNarrative('Не удалось создать кампанию. Проверьте, запущен ли backend.');
    } finally {
      setLoading(false);
    }
  };

  const createCharacter = async () => {
    if (!campaignId) {
      setNarrative('Сначала создайте кампанию.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/campaigns/${campaignId}/characters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: 'player_1',
          name,
          class_name: className,
          strength: 12,
          agility: 9,
          intellect: 10,
          will: 11,
        }),
      });
      const data = await response.json();
      setCharacterId(data.id);
      setNarrative(`Персонаж ${data.name} создан. Он вступает в Серебряный Логов.`);
    } catch (error) {
      setNarrative('Не удалось создать персонажа.');
    } finally {
      setLoading(false);
    }
  };

  const sendAction = async () => {
    if (!campaignId || !characterId) {
      setNarrative('Сначала создайте кампанию и персонажа.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/campaigns/${campaignId}/turns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: characterId,
          action_text: action,
        }),
      });
      const data = await response.json();
      setNarrative(data.narrative || 'Ничего не произошло, но тьма усилилась.');
    } catch (error) {
      setNarrative('Ошибка при обработке хода. Проверьте backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', color: '#e2e8f0', fontFamily: 'Segoe UI, sans-serif', padding: 28 }}>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <h1 style={{ fontSize: 36, marginBottom: 12 }}>Пепельная Корона</h1>
        <p style={{ color: '#a5b4fc', marginBottom: 30 }}>Тёмное фэнтези AI GM</p>

        <div style={{ display: 'grid', gap: 16, gridTemplateColumns: '1fr 1fr', marginBottom: 16 }}>
          <div style={{ background: '#111827', border: '1px solid #374151', borderRadius: 12, padding: 16 }}>
            <label style={{ display: 'block', marginBottom: 8 }}>Название кампании</label>
            <input value={campaignName} onChange={(e) => setCampaignName(e.target.value)} style={{ width: '100%', padding: 10, borderRadius: 8, border: '1px solid #475569', background: '#0b1120', color: '#fff' }} />
            <button onClick={createCampaign} style={{ marginTop: 12, width: '100%', background: '#7c3aed', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 16px', cursor: 'pointer' }}>
              {loading ? 'Создаём...' : 'Создать кампанию'}
            </button>
          </div>

          <div style={{ background: '#111827', border: '1px solid #374151', borderRadius: 12, padding: 16 }}>
            <label style={{ display: 'block', marginBottom: 8 }}>Имя персонажа</label>
            <input value={name} onChange={(e) => setName(e.target.value)} style={{ width: '100%', padding: 10, borderRadius: 8, border: '1px solid #475569', background: '#0b1120', color: '#fff', marginBottom: 12 }} />

            <label style={{ display: 'block', marginBottom: 8 }}>Класс</label>
            <select value={className} onChange={(e) => setClassName(e.target.value)} style={{ width: '100%', padding: 10, borderRadius: 8, border: '1px solid #475569', background: '#0b1120', color: '#fff' }}>
              {classOptions.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>

            <button onClick={createCharacter} style={{ marginTop: 12, width: '100%', background: '#0ea5e9', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 16px', cursor: 'pointer' }}>
              Создать персонажа
            </button>
          </div>
        </div>

        <div style={{ background: '#111827', border: '1px solid #374151', borderRadius: 12, padding: 20, marginBottom: 16 }}>
          <h3 style={{ marginTop: 0, marginBottom: 12 }}>История</h3>
          <p style={{ lineHeight: 1.6 }}>{narrative}</p>
        </div>

        <div style={{ background: '#111827', border: '1px solid #374151', borderRadius: 12, padding: 20 }}>
          <label style={{ display: 'block', marginBottom: 8 }}>Ваше действие</label>
          <textarea value={action} onChange={(e) => setAction(e.target.value)} rows={5} style={{ width: '100%', resize: 'vertical', padding: 12, borderRadius: 8, border: '1px solid #475569', background: '#0b1120', color: '#fff' }} />
          <button onClick={sendAction} disabled={loading} style={{ marginTop: 12, background: '#22c55e', color: '#fff', border: 'none', borderRadius: 8, padding: '12px 18px', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Рассуждаю...' : 'Сделать ход'}
          </button>
        </div>
      </div>
    </div>
  );
}
