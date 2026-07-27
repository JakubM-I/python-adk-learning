# Lokalna platforma nauki

To jest aplikacja webowa do przerabiania modułów z katalogu `modules/` w przeglądarce.

Etap 1 zawiera tylko szkielet:
- backend FastAPI,
- frontend React + Vite,
- prosty endpoint zdrowia,
- roboczy ekran, który pobiera status backendu.

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

## Zakres etapu 1

Ten etap celowo nie zawiera jeszcze:
- czytnika modułów,
- renderowania Markdown,
- zapisu postępu,
- trybu ćwiczeń,
- integracji z agentem.

Te elementy są opisane w `docs/platform/workflow.md` jako kolejne etapy.
