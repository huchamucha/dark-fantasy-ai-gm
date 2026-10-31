# Dark Fantasy AI GM — локальная AI RPG-платформа

Проект развивается от прототипа ведущего тёмного фэнтези к универсальной локальной платформе одиночных AI-RPG и визуальных новелл. Цель — поддерживать разные истории и сеттинги на общем движке, подключая контент отдельными Story Packs.

## Текущий основной контур

**Основной контур разработки:** FastAPI backend + React/Vite frontend + LM Studio.

- Backend: `backend/`, FastAPI, порт 8000.
- Frontend: `frontend/`, React + TypeScript + Vite, порт 5173.
- LLM: локальный OpenAI-compatible API LM Studio.
- Текущая модель в локальной конфигурации: `qwen2.5-7b-instruct`.
- Текущий адрес LM Studio: `http://localhost:1235/v1/chat/completions`.

В корне также сохранён ранний Flask-прототип (`app.py`, `game_engine.py`, `game_state.py`, `llm_client.py`, `prompts.py`). Он является исторической/legacy-реализацией и не является основным приложением для дальнейшего развития. Не удалять его без отдельного решения и проверки совместимости.

## Документация

- [Архитектура платформы](docs/ARCHITECTURE.md)
- [План разработки](docs/ROADMAP.md)
- [Технические решения](docs/TECHNICAL_DECISIONS.md)
- [Аудит текущего состояния](docs/CURRENT_STATE.md)
- [Промпты и правила ведущего](docs/PROMPTS.md)
- [Ручные настройки и история изменений](docs/DEVELOPMENT_NOTES.md)

## Локальный запуск (Windows PowerShell)

### 1. Подготовить окружение

Установить Python 3.11+, Node.js LTS и LM Studio. Скачать совместимую GGUF-модель Qwen2.5 7B Instruct Q4_K_M, загрузить её в LM Studio и включить Local Server на порту 1235.

В корне проекта создать `.env` на основе `.env.example` и указать точное имя модели, которое возвращает `GET http://localhost:1235/v1/models`.

Пример `.env`:

```dotenv
LLM_URL=http://localhost:1235/v1/chat/completions
LLM_MODEL=qwen2.5-7b-instruct
```

Не коммитить `.env`, ключи, локальные модели, кэши и виртуальные окружения.

### 2. Запустить backend

В первом окне PowerShell:

```powershell
cd "путь\к\dark-fantasy-ai-gm\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка: `http://localhost:8000/api/health` и Swagger `http://localhost:8000/docs`.

### 3. Запустить frontend

Во втором окне PowerShell:

```powershell
cd "путь\к\dark-fantasy-ai-gm\frontend"
npm install
npm run dev
```

Открыть `http://localhost:5173`. Vite проксирует `/api` на `http://localhost:8000`.

### Порядок запуска

1. LM Studio: модель загружена, Local Server включён на 1235.
2. FastAPI backend: порт 8000.
3. Vite frontend: порт 5173.

## Состояние реализации

Уже есть стартовый игровой цикл создания кампании, создания персонажа и отправки действия ведущему. Добавлены базовые правила повествования и защита от прямого применения LLM-изменений состояния. Хранилище пока in-memory: прогресс теряется при перезапуске backend. SQLite, полноценный Game Engine, Story Pack loader, NPC memory и media pipeline остаются задачами следующих этапов.

## Важные ограничения текущей версии

- LLM сейчас отвечает за повествование; механические исходы намеренно не рассчитываются.
- HP, характеристики, инвентарь, квесты и world flags не должны меняться по произвольному JSON от модели.
- Не считать наличие документации доказательством готовности функции.
- Перед крупным рефакторингом читать фактическую ветку и проверять запуск.
- Тесты и сборка должны выполняться в локальном окружении проекта; если они не запускались, не заявлять об успешной проверке.

## Цель ближайшего этапа

Стабилизировать игровой цикл, добавить тесты, затем вынести первую историю «Пепельная Корона» в Story Pack и перейти с in-memory состояния на SQLite. Главный критерий универсальности — две разные истории работают на одном движке и системе сохранений.