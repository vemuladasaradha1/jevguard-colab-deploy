# JevGuard — Production FastAPI Edition

A deployable version of the Colab prototype:

**Jev decision layer → deterministic validation → LangGraph orchestration → calculator/web tools → Groq generation → Jev guardian → risk policy → FastAPI → space UI**

## Features

- Jev 1.13 decision layer
- Deterministic fallback if Jev fails
- Deterministic validator for obvious arithmetic/current-info requests
- LangGraph orchestration
- Safe arithmetic calculator (AST allowlist; no `eval`)
- DuckDuckGo web search via `ddgs`
- Parallel calculator + web execution when both are selected
- Groq generation
- Jev guardian: quality + groundedness + safety
- Composite risk score
- API-friendly human-review status
- LangSmith-compatible tracing through environment variables
- Space-themed responsive frontend
- Dockerfile
- PythonAnywhere ASGI deployment path

## Important model note

The default Groq model is `openai/gpt-oss-20b`. Groq's model catalog should be checked before deployment because model IDs can change over time.

## 1. Local setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Create `.env`:

```bash
copy .env.example .env
```

PowerShell alternative:

```powershell
Copy-Item .env.example .env
```

Put your keys into `.env`.

Run:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## 2. Docker

Build:

```bash
docker build -t jevguard .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env jevguard
```

Open:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

## 3. Docker Compose

```bash
docker compose up --build
```

The included compose file publishes port 8000.

## 4. PythonAnywhere

PythonAnywhere currently documents FastAPI deployment through its ASGI/uvicorn path. Their ASGI support is described as experimental, and the current docs show a Uvicorn command using the provided `DOMAIN_SOCKET`.

Create a Python virtual environment in a Bash console:

```bash
mkvirtualenv jevguard --python=python3.13
workon jevguard
```

Clone/upload the project:

```bash
cd ~
git clone YOUR_REPOSITORY_URL jevguard
cd jevguard
pip install -r requirements.txt
```

Create `.env` with your API keys.

For an ASGI site, the command is conceptually:

```bash
/home/YOURUSERNAME/.virtualenvs/jevguard/bin/uvicorn \
  --app-dir /home/YOURUSERNAME/jevguard \
  --uds ${DOMAIN_SOCKET} \
  app.main:app
```

If using PythonAnywhere's `pa` command:

```bash
pip install --upgrade pythonanywhere

pa website create \
  --domain YOURUSERNAME.pythonanywhere.com \
  --command '/home/YOURUSERNAME/.virtualenvs/jevguard/bin/uvicorn --app-dir /home/YOURUSERNAME/jevguard --uds ${DOMAIN_SOCKET} app.main:app'
```

Reload after changes:

```bash
pa website reload --domain YOURUSERNAME.pythonanywhere.com
```

### PythonAnywhere note

The ASGI path is experimental according to PythonAnywhere's current documentation. This project serves its own frontend through FastAPI rather than relying on PythonAnywhere static-file mappings.

## 5. Antigravity workflow

Open the project folder in Antigravity.

Recommended terminal commands:

```bash
python -m venv .venv
```

Activate the environment and:

```bash
pip install -r requirements.txt
```

Then:

```bash
uvicorn app.main:app --reload
```

For Docker:

```bash
docker build -t jevguard .
docker run --rm -p 8000:8000 --env-file .env jevguard
```

## 6. API

POST `/api/chat`

```json
{
  "query": "What is LangGraph?"
}
```

Response:

```json
{
  "answer": "...",
  "status": "approved",
  "tools_used": [],
  "risk": 0.12,
  "quality": 3.7,
  "grounded": 0.92,
  "safe": 0.98,
  "latency_ms": 1200,
  "request_id": "..."
}
```

## 7. Architecture

```text
Browser
   |
   v
FastAPI /api/chat
   |
   v
JevGuard LangGraph
   |
   +--> Security
   |
   +--> Jev Planner
   |       |
   |       +--> direct
   |       +--> calculator
   |       +--> web_search
   |       +--> calculator_and_web
   |
   +--> Deterministic validation
   |
   +--> Calculator / Web Search
   |
   +--> Evidence aggregation
   |
   +--> Groq
   |
   +--> Jev Guardian
   |
   +--> Composite Risk
   |
   +--> Final Policy
   |
   v
JSON response
```

## Security notes

- Never commit `.env`.
- Do not put API keys in frontend JavaScript.
- Calculator input is parsed with an AST allowlist; it does not use Python `eval`.
- The security classifier is a screening layer, not a complete prompt-injection defense.
- Production deployments should add authentication, rate limiting, structured logging, and persistent state if human review is required.
