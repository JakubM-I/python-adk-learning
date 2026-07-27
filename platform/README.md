# Lokalna platforma nauki

To jest aplikacja webowa do przerabiania modułów z katalogu `modules/` w przeglądarce.

Etap 2 zawiera:
- backend FastAPI,
- frontend React + Vite,
- endpoint zdrowia,
- endpoint listy modulow,
- endpoint czytania plikow Markdown modulu,
- widok listy modulow i zakladki czesci modulu.

## Backend

```bash
cd platform/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend będzie dostępny pod adresem:

```text
http://127.0.0.1:8000
```

Endpoint testowy:

```text
http://127.0.0.1:8000/api/health
```

Endpointy czytnika:

```text
http://127.0.0.1:8000/api/modules
http://127.0.0.1:8000/api/modules/module-01-python-foundations/content/material
```

## Frontend

W drugim terminalu:

```bash
cd platform/frontend
npm install
npm run dev
```

Frontend będzie dostępny pod adresem pokazanym przez Vite, domyślnie:

```text
http://127.0.0.1:5173
```

Jeśli backend działa na innym porcie, ustaw:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

## Zakres etapu 2

Ten etap zawiera pierwszy czytnik modulow:
- wykrywanie folderow `modules/module-*`,
- pobieranie metadanych modulu z `module.md`,
- przelaczanie plikow `module.md`, `exercises.md`, `mini_project.md`, `knowledge_check.md`, `summary.md`,
- renderowanie Markdown po stronie frontendu.

Ten etap celowo nie zawiera jeszcze:
- zapisu postępu,
- trybu ćwiczeń,
- integracji z agentem.

Te elementy są opisane w `docs/platform/workflow.md` jako kolejne etapy.
