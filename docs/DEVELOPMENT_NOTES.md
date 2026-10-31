# История наработок и ручные настройки разработчика

Документ объединяет договорённости из предыдущих рабочих сессий, изменения, которые пользователь выполнял вручную, и текущие локальные настройки. Секреты и содержимое реального `.env` сюда не помещаются.

## 1. Локальная среда

- ОС разработки: Windows.
- GPU: NVIDIA RTX 3070, 8 GB VRAM.
- RAM: 32 GB.
- CPU: AMD Ryzen 5 9600X.
- Свободное место на диске: ориентировочно 100–300 GB.
- LM Studio: Bionic 1.1.10.
- LM Studio OpenAI-compatible server: `http://localhost:1235/v1`.
- Модель: `qwen2.5-7b-instruct` (Qwen2.5 7B Instruct GGUF Q4_K_M, около 4.68 GB).
- Проверка модели: `GET http://localhost:1235/v1/models`.
- Backend: FastAPI, `http://localhost:8000`.
- Frontend: Vite, `http://localhost:5173`.

## 2. Ручная настройка `.env`

В корне проекта создать локальный `.env` (он не должен попадать в Git):

```dotenv
LLM_URL=http://localhost:1235/v1/chat/completions
LLM_MODEL=qwen2.5-7b-instruct
```

Проверять точный ID модели по `/v1/models`: имя должно совпадать с тем, что сообщает LM Studio.

## 3. Ручная настройка `backend/app/config.py`

Ранее пользователь вручную добавлял загрузку `.env` из корня проекта. В актуальной ветке это изменение уже внесено в `backend/app/config.py`:

```python
from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)

LLM_URL = os.getenv("LLM_URL", "http://localhost:1235/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-7b-instruct")
```

Это устраняет прежнее расхождение: репозиторий по умолчанию указывал Ollama на 11434 и `gpt-4o-mini`, а реальная локальная среда использует LM Studio на 1235 и Qwen.

## 4. Запуск в PowerShell

Окно 1 — backend:

```powershell
cd "C:\Users\ave maria\Desktop\dark-fantasy-ai-gm-main\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Окно 2 — frontend:

```powershell
cd "C:\Users\ave maria\Desktop\dark-fantasy-ai-gm-main\frontend"
npm run dev
```

Порядок: сначала LM Studio и загруженная модель, затем backend, затем frontend.

## 5. Русский JSON в PowerShell

При отправке тестовых JSON-запросов с русским текстом из Windows PowerShell ранее возникала проблема кодировки. Надёжный подход — явно преобразовать JSON в UTF-8 байты перед отправкой, а не полагаться на кодировку консоли.

## 6. Ручные изменения промпта из предыдущих сессий

Ранее пользователь добавлял в системный промпт следующие логические блоки:

1. `ПРАВИЛО КОНКРЕТИКИ` — отвечать на вопросы прямо, не заменять ответ загадкой, давать новую информацию.
2. `ПРАВИЛО КОНТРОЛЯ ИГРОКА` — не совершать действия за игрока, не придумывать его мысли и не объявлять успех до действия.
3. `ПРАВИЛО РАЗВИТИЯ ИГРОВОЙ СЦЕНЫ` — не повторяться, продвигать сцену, учитывать повторное исследование и действия игрока.

Эти правила собраны в единый актуальный промпт `backend/app/prompts/game_master_ru.py` и описаны в `docs/PROMPTS.md`.

## 7. Ручное изменение журнала событий

Ранее обсуждалось, что действие игрока нужно сохранять в recent_events. В актуальной ветке:

- `GameService.process_turn` передаёт `turn.action_text` в `update_after_turn`;
- `world_service.update_after_turn` принимает исходный текст действия;
- `GameWorldStore` записывает `player_action`, narrative, summary и уникальный event_id.

## 8. Известные проблемы и уроки

- Не вставлять большой кодовый блок до проверки фактического файла и его текущей версии.
- Ошибки отступов Python уже приводили к `IndentationError` и `NameError`; при правках сохранять отступы метода/класса и запускать проверки.
- Не использовать фиксированный `turn_0001`; теперь ID генерируется через UUID.
- Не позволять LLM изменять HP/инвентарь/характеристики без движка.
- Не коммитить `.env`, модели, node_modules, виртуальные окружения и кэши.

## 9. Ограничение текущей синхронизации

GitHub-ветка отражает согласованные настройки и изменения, но локальная папка пользователя может содержать дополнительные незакоммиченные правки. Перед переключением на ветку следует сделать резервную копию локальной папки или отдельный commit/stash и затем сравнить локальную версию с GitHub.