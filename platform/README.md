# Lokalna platforma nauki

To jest aplikacja webowa do przerabiania modułów z katalogu `modules/` w przeglądarce.

Etap 6 zawiera:
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
- parser `knowledge_check.md`,
- tryb jednego pytania lub scenariusza na ekranie,
- zapis odpowiedzi i statusu pytania sprawdzenia wiedzy.
- endpointy przygotowania paczki kontekstu dla agenta,
- panel agentowy w trybie cwiczen i sprawdzenia wiedzy,
- zapis feedbacku agenta przy konkretnej odpowiedzi.
- pole odpowiedzi na pytanie sprawdzajace w Materiale,
- pole odpowiedzi na pytanie sprawdzajace i miejsce na rozwiazanie w Mini-projekcie.

## Backend

Domyślny port backendu to `8000`. Przed startem sprawdź, czy nie działa już poprzednia instancja:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

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
http://127.0.0.1:8000/api/modules/module-01-python-foundations/knowledge-check
http://127.0.0.1:8000/api/modules/module-01-python-foundations/exercises/exercise-1/agent-context
http://127.0.0.1:8000/api/modules/module-01-python-foundations/knowledge-check/knowledge-check-1/agent-context
```

Endpointy postepu:

```text
http://127.0.0.1:8000/api/progress
```

Endpointy feedbacku agenta:

```text
PUT http://127.0.0.1:8000/api/modules/module-01-python-foundations/exercises/exercise-1/feedback
PUT http://127.0.0.1:8000/api/modules/module-01-python-foundations/knowledge-check/knowledge-check-1/feedback
```

## Frontend

Domyślny port frontendu to `5173`. Przed startem sprawdź, czy nie działa już poprzednia instancja:

```bash
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

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

Nie uruchamiaj frontendu na kolejnych portach zastępczych, jeśli `5173` jest zajęty. Najpierw zamknij poprzedni proces Vite, a potem uruchom frontend ponownie.

Jeśli wyjątkowo backend działa na innym porcie, ustaw:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

Po zakończeniu pracy zamknij oba serwery i sprawdź, czy porty są wolne:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

## Zakres etapu 6

Ten etap zawiera czytnik modulow z lokalnym postepem, trybem cwiczen, trybem sprawdzenia wiedzy i punktem integracji z agentem:
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
- parsowanie pytan z `knowledge_check.md` wedlug sekcji,
- pokazywanie jednego pytania albo scenariusza naraz,
- zapis odpowiedzi w `knowledge_check_answers`,
- statusy `W trakcie`, `Do omowienia`, `Przerobione`,
- licznik przerobionych pytan i przechodzenie poprzednie/nastepne.
- przygotowanie paczki `agent-context` dla wybranego cwiczenia albo pytania,
- rozdzielenie tresci zadania, odpowiedzi uzytkownika, oczekiwanego efektu i feedbacku,
- zapis feedbacku w `exercise_feedback` albo `knowledge_check_feedback` w lokalnym `platform/data/progress.json`.
- zapis odpowiedzi z konca Materialu i Mini-projektu w `part_answers`,
- zapis rozwiazania Mini-projektu do sprawdzenia w `mini_project_submission`.

Ten etap celowo nie zawiera jeszcze:
- uruchamiania kodu Pythona,
- automatycznego wywolania zewnetrznego modelu,
- przechowywania sekretow w kodzie albo w plikach sledzonych przez git.

## Sekrety i dane lokalne

Aplikacja nie potrzebuje klucza API do przygotowania paczki dla agenta. Jesli w przyszlosci pojawi sie bezposrednie wywolanie modelu, sekret powinien byc czytany tylko po stronie backendu z lokalnego `.env` albo zmiennych srodowiskowych.

Repo ignoruje:
- `.env` i `.env.*`,
- pliki kluczy `*.pem` i `*.key`,
- lokalny postep `platform/data/*.json`,
- `node_modules/`, `dist/` i `.venv/`.

Nie zapisuj sekretow w `platform/frontend/src/`, w `vite.config.js`, w Markdownach modulow ani w `platform/data/progress.json`. Frontend powinien komunikowac sie z backendem, a backend powinien trzymac integracje wymagajace sekretow po swojej stronie.
