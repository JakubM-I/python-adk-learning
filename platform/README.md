# Lokalna platforma nauki

To jest aplikacja webowa do przerabiania modułów z katalogu `modules/` w przeglądarce.

Etap 4 zawiera:
- backend FastAPI,
- frontend React + Vite,
- endpoint zdrowia,
- endpoint listy modulow,
- endpoint czytania plikow Markdown modulu,
- widok listy modulow i zakladki czesci modulu,
- lokalny zapis postepu w `platform/data/progress.json`,
- oznaczanie czesci modulu jako ukonczonych,
- prywatne notatki per modul.
- parser `exercises.md`,
- tryb jednego cwiczenia na ekranie,
- zapis odpowiedzi i statusu cwiczenia.

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
http://127.0.0.1:8000/api/modules/module-01-python-foundations/exercises
```

Endpointy postepu:

```text
http://127.0.0.1:8000/api/progress
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

## Zakres etapu 4

Ten etap zawiera czytnik modulow z lokalnym postepem i trybem cwiczen:
- wykrywanie folderow `modules/module-*`,
- pobieranie metadanych modulu z `module.md`,
- przelaczanie plikow `module.md`, `exercises.md`, `mini_project.md`, `knowledge_check.md`, `summary.md`,
- renderowanie Markdown po stronie frontendu,
- zapis listy ukonczonych czesci modulu,
- pasek postepu i licznik ukonczonych czesci,
- pole prywatnych notatek zapisywane poza `modules/`.
- parsowanie cwiczen z naglowkow `### Cwiczenie N`,
- pokazywanie jednego cwiczenia naraz,
- zwijane wskazowki i ukryty oczekiwany efekt,
- zapis odpowiedzi w `answers`,
- statusy `W trakcie`, `Do sprawdzenia`, `Rozwiazane`,
- przechodzenie do poprzedniego i nastepnego cwiczenia.

Ten etap celowo nie zawiera jeszcze:
- uruchamiania kodu Pythona,
- automatycznego sprawdzania odpowiedzi,
- integracji z agentem.

Te elementy są opisane w `docs/platform/workflow.md` jako kolejne etapy.
