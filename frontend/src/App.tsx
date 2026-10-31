
import React, { useMemo, useState } from 'react';

const DEFAULT_ACTION =
  'Иду к монастырю и хочу понять, кто зазывает тень из-под города.';

type Character = {
  id: string;
  name: string;
  class_name: string;
  level: number;
  hp: number;
  max_hp: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  gold: number;
  location_id: string;
  inventory: string[];
  status_flags: Record<string, unknown>;
};

const attributes = [
  { key: 'strength', label: 'Сила', short: 'СИЛ' },
  { key: 'dexterity', label: 'Ловкость', short: 'ЛОВ' },
  { key: 'constitution', label: 'Телосложение', short: 'ТЕЛ' },
  { key: 'intelligence', label: 'Интеллект', short: 'ИНТ' },
  { key: 'wisdom', label: 'Мудрость', short: 'МДР' },
  { key: 'charisma', label: 'Харизма', short: 'ХАР' },
] as const;

function modifier(score: number) {
  const value = Math.floor((score - 10) / 2);
  return value >= 0 ? `+${value}` : `${value}`;
}

export default function App() {
  const [campaignId, setCampaignId] = useState('');
  const [character, setCharacter] = useState<Character | null>(null);

  const [campaignName, setCampaignName] = useState('Пепельная Корона');
  const [name, setName] = useState('Эдрик');
  const [className, setClassName] = useState('Рыцарь Пепельного Ордена');

  const [action, setAction] = useState(DEFAULT_ACTION);
  const [history, setHistory] = useState<string[]>([
    'Колокола Серебряного Логова звонят без причины. Тьма под городом шевелится, и вы слышите зов из-под земли.',
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const classOptions = useMemo(() => [
    'Рыцарь Пепельного Ордена',
    'Алхимик-отшельник',
    'Охотник на чудовищ',
    'Монах-оккультист',
    'Посланник тени',
  ], []);

  const addHistory = (text: string) => {
    setHistory((previous) => [...previous, text]);
  };

  const createCampaign = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: campaignName,
          setting: 'dark_fantasy',
          tone: 'dark_fantasy',
        }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка создания кампании: ${response.status}`);
      }

      const data = await response.json();
      setCampaignId(data.id);
      addHistory(`Кампания «${data.title}» создана.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось создать кампанию.');
    } finally {
      setLoading(false);
    }
  };

  const createCharacter = async () => {
    if (!campaignId) {
      setError('Сначала создай кампанию.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`/api/campaigns/${campaignId}/characters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: 'player_1',
          name,
          class_name: className,
          strength: 12,
          dexterity: 9,
          constitution: 11,
          intelligence: 10,
          wisdom: 11,
          charisma: 10,
        }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка создания персонажа: ${response.status}`);
      }

      const data = await response.json();

      setCharacter({
        id: data.id,
        name: data.name,
        class_name: data.class_name,
        level: data.level ?? 1,
        hp: data.hp ?? 18,
        max_hp: data.max_hp ?? 18,
        strength: data.strength ?? 12,
        dexterity: data.dexterity ?? 9,
        constitution: data.constitution ?? 11,
        intelligence: data.intelligence ?? 10,
        wisdom: data.wisdom ?? 11,
        charisma: data.charisma ?? 10,
        gold: data.gold ?? 0,
        location_id: data.location_id ?? 'unknown',
        inventory: data.inventory ?? [],
        status_flags: data.status_flags ?? {},
      });

      addHistory(
        `${data.name} вступает в Серебряное Логово. Его история начинается.`
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось создать персонажа.');
    } finally {
      setLoading(false);
    }
  };

  const sendAction = async () => {
    if (!campaignId || !character) {
      setError('Сначала создай персонажа.');
      return;
    }

    if (!action.trim()) {
      setError('Опиши, что собирается сделать персонаж.');
      return;
    }

    setLoading(true);
    setError('');

    const playerAction = action.trim();
    addHistory(`Вы: ${playerAction}`);

    try {
      const response = await fetch(`/api/campaigns/${campaignId}/turns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: character.id,
          action_text: playerAction,
        }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка обработки хода: ${response.status}`);
      }

      const data = await response.json();

      if (data.summary) {
       addHistory(`🎲 ${data.summary}`);
      }

      addHistory(data.narrative || 'В мире ничего не произошло.');
      setAction('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось обработать ход.');
    } finally {
      setLoading(false);
    }
  };

  const resetGame = () => {
    setCharacter(null);
    setCampaignId('');
    setHistory([
      'Колокола Серебряного Логова звонят без причины. Тьма под городом шевелится.',
    ]);
    setError('');
  };

  const panelStyle: React.CSSProperties = {
    background: '#171923',
    border: '1px solid #343746',
    borderRadius: 12,
    padding: 18,
  };

  const mutedStyle: React.CSSProperties = {
    color: '#9ca3af',
    fontSize: 13,
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    boxSizing: 'border-box',
    padding: 12,
    borderRadius: 8,
    border: '1px solid #45495b',
    background: '#10121b',
    color: '#f3f4f6',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '12px 18px',
    border: 'none',
    borderRadius: 8,
    background: '#8b5cf6',
    color: 'white',
    fontWeight: 600,
    cursor: 'pointer',
  };

  // Экран создания кампании и персонажа
  if (!character) {
    return (
      <main style={{
        minHeight: '100vh',
        background: '#0c0d12',
        color: '#e5e7eb',
        padding: 28,
        fontFamily: 'Segoe UI, sans-serif',
      }}>
        <div style={{ maxWidth: 850, margin: '40px auto' }}>
          <h1 style={{ fontSize: 38, color: '#d6c2a1' }}>Пепельная Корона</h1>
          <p style={{ color: '#a78bfa' }}>Тёмное фэнтези · AI Game Master</p>

          <section style={{ ...panelStyle, marginTop: 30 }}>
            <h2>Новая кампания</h2>
            <input
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              style={inputStyle}
              placeholder="Название кампании"
            />
            <button
              onClick={createCampaign}
              disabled={loading || !!campaignId}
              style={{ ...buttonStyle, marginTop: 12, opacity: campaignId ? 0.5 : 1 }}
            >
              {campaignId ? 'Кампания создана' : 'Создать кампанию'}
            </button>
          </section>

          <section style={{ ...panelStyle, marginTop: 16 }}>
            <h2>Создание персонажа</h2>

            <label>Имя</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ ...inputStyle, marginTop: 8, marginBottom: 16 }}
            />

            <label>Класс</label>
            <select
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              style={{ ...inputStyle, marginTop: 8 }}
            >
              {classOptions.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>

            <button
              onClick={createCharacter}
              disabled={loading || !campaignId}
              style={{ ...buttonStyle, marginTop: 16, opacity: !campaignId ? 0.5 : 1 }}
            >
              {loading ? 'Создаём...' : 'Создать персонажа и начать игру'}
            </button>
          </section>

          {error && (
            <p style={{ color: '#f87171', marginTop: 16 }}>{error}</p>
          )}
        </div>
      </main>
    );
  }

  // Игровой экран
  return (
    <main style={{
      minHeight: '100vh',
      background: '#0c0d12',
      color: '#e5e7eb',
      padding: 20,
      fontFamily: 'Segoe UI, sans-serif',
    }}>
      <div style={{ maxWidth: 1450, margin: '0 auto' }}>

        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 16,
          flexWrap: 'wrap',
          borderBottom: '1px solid #343746',
          paddingBottom: 18,
          marginBottom: 20,
        }}>
          <div>
            <h1 style={{ color: '#d6c2a1', margin: 0 }}>Пепельная Корона</h1>
            <span style={mutedStyle}>Серебряное Логово · Тёмное фэнтези</span>
          </div>
          <button onClick={resetGame} style={{ ...buttonStyle, background: '#343746' }}>
            В меню
          </button>
        </header>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(230px, 280px) minmax(300px, 1fr) minmax(210px, 260px)',
          gap: 16,
          alignItems: 'start',
        }}>

          {/* Левая панель — персонаж */}
          <aside style={panelStyle}>
            <h2 style={{ marginTop: 0, color: '#d6c2a1' }}>Персонаж</h2>
            <h3 style={{ marginBottom: 4 }}>{character.name}</h3>
            <div style={mutedStyle}>{character.class_name}</div>
            <div style={{ marginTop: 12, color: '#c4b5fd' }}>
              Уровень {character.level}
            </div>

            <div style={{ marginTop: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <b>Здоровье</b>
                <span>{character.hp} / {character.max_hp}</span>
              </div>
              <div style={{
                height: 10,
                background: '#343746',
                borderRadius: 20,
                marginTop: 8,
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${Math.max(0, Math.min(100, character.hp / Math.max(1, character.max_hp) * 100))}%`,
                  background: '#b91c1c',
                }} />
              </div>
            </div>

            <h3 style={{ marginTop: 24 }}>Характеристики</h3>
            <div style={{ display: 'grid', gap: 8 }}>
              {attributes.map((attribute) => {
                const score = character[attribute.key];
                return (
                  <div key={attribute.key} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#10121b',
                    borderRadius: 8,
                    padding: 10,
                  }}>
                    <div>
                      <b>{attribute.short}</b>
                      <div style={mutedStyle}>{attribute.label}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <b style={{ fontSize: 19 }}>{score}</b>
                      <div style={{ color: '#a78bfa', fontSize: 13 }}>
                        {modifier(score)}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ marginTop: 20, borderTop: '1px solid #343746', paddingTop: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Золото</span>
                <b>{character.gold}</b>
              </div>
            </div>
          </aside>

          {/* Центральная панель — история */}
          <section style={{ ...panelStyle, minHeight: 580 }}>
            <h2 style={{ marginTop: 0, color: '#d6c2a1' }}>История</h2>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 16,
              minHeight: 400,
            }}>
              {history.map((entry, index) => (
                <div key={index} style={{
                  padding: 14,
                  background: '#10121b',
                  borderRadius: 8,
                  borderLeft: `3px solid ${entry.startsWith('Вы:') ? '#8b5cf6' : '#a78bfa'}`,
                  lineHeight: 1.7,
                  whiteSpace: 'pre-wrap',
                }}>
                  {entry}
                </div>
              ))}
            </div>

            {error && (
              <p style={{ color: '#f87171' }}>{error}</p>
            )}

            <div style={{ marginTop: 24 }}>
              <label style={{ display: 'block', marginBottom: 8 }}>
                Что делает {character.name}?
              </label>
              <textarea
                value={action}
                onChange={(e) => setAction(e.target.value)}
                rows={4}
                style={{ ...inputStyle, resize: 'vertical' }}
                placeholder="Опиши своё действие..."
              />
              <button
                onClick={sendAction}
                disabled={loading}
                style={{
                  ...buttonStyle,
                  marginTop: 12,
                  background: '#6d28d9',
                  opacity: loading ? 0.6 : 1,
                }}
              >
                {loading ? 'Мир отвечает...' : 'Совершить действие'}
              </button>
            </div>
          </section>

          {/* Правая панель — инвентарь и задания */}
          <aside style={{ display: 'grid', gap: 16 }}>
            <section style={panelStyle}>
              <h2 style={{ marginTop: 0, color: '#d6c2a1' }}>Инвентарь</h2>
              {character.inventory.length === 0 ? (
                <p style={mutedStyle}>Инвентарь пока пуст.</p>
              ) : (
                character.inventory.map((item, index) => (
                  <div key={index} style={{
                    padding: 9,
                    background: '#10121b',
                    borderRadius: 6,
                    marginBottom: 6,
                  }}>
                    {item}
                  </div>
                ))
              )}
            </section>

            <section style={panelStyle}>
              <h2 style={{ marginTop: 0, color: '#d6c2a1' }}>Задания</h2>
              <p style={{ lineHeight: 1.6 }}>
                <b>Главная тайна</b>
              </p>
              <p style={mutedStyle}>
                Узнать, кто зазывает тень из-под города.
              </p>
              <div style={{
                display: 'inline-block',
                padding: '5px 9px',
                background: '#422006',
                color: '#fbbf24',
                borderRadius: 6,
                fontSize: 12,
              }}>
                Активное
              </div>
            </section>

            <section style={panelStyle}>
              <h2 style={{ marginTop: 0, color: '#d6c2a1' }}>Состояние</h2>
              {Object.keys(character.status_flags).length === 0 ? (
                <p style={mutedStyle}>Нет активных эффектов.</p>
              ) : (
                Object.entries(character.status_flags).map(([key, value]) => (
                  <div key={key}>{key}: {String(value)}</div>
                ))
              )}
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}
