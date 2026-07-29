# Lokalna platforma nauki

To jest aplikacja webowa do przerabiania modułów z katalogu `modules/` w przeglądarce.

Etap 8 zawiera:
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
- pole odpowiedzi na pytanie sprawdzajace w Materiale,
- pole odpowiedzi na pytanie sprawdzajace i miejsce na rozwiazanie w Mini-projekcie.
- segmentowe przyciski `Sprawdz` dla Materialu, Cwiczen, Mini-projektu i Sprawdzenia wiedzy,
- wspolny kontrakt `ReviewContext` przygotowany pod przyszlego agenta,
- diagnostyczny endpoint podgladu contextu review,
- mockowy adapter oceny w backendowym `ReviewService`,
- opcjonalny adapter OpenAI z Responses API i structured output,
- twardy wynik segmentowy `ReviewResult` walidowany przed zapisem progressu,
- zapis feedbacku przy konkretnej odpowiedzi.

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

### Konfiguracja review adaptera

Domyślnie backend używa mocka i nie wymaga żadnych sekretów:

```bash
REVIEW_ADAPTER=mock
```

Opcjonalny prawdziwy adapter OpenAI można włączyć tylko po stronie backendu:

```bash
REVIEW_ADAPTER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5
```

`OPENAI_MODEL` jest opcjonalny i domyślnie ma wartość `gpt-5`. `OPENAI_API_KEY` jest wymagany dopiero wtedy, gdy `REVIEW_ADAPTER=openai`. Brak klucza, błąd API albo odpowiedź niezgodna ze schematem `ReviewResult` przerywa review bez aktualizacji `platform/data/progress.json`.

Frontend nie przechowuje sekretów. Nie ustawiaj `OPENAI_API_KEY` w `platform/frontend/`, w `VITE_*`, w plikach Markdown ani w `platform/data/progress.json`.

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
```

Endpointy postepu:

```text
http://127.0.0.1:8000/api/progress
```

Endpointy segmentowego sprawdzania:

```text
POST http://127.0.0.1:8000/api/modules/module-01-python-foundations/review/material
POST http://127.0.0.1:8000/api/modules/module-01-python-foundations/review/mini-project
POST http://127.0.0.1:8000/api/modules/module-01-python-foundations/review/exercises
POST http://127.0.0.1:8000/api/modules/module-01-python-foundations/review/knowledge-check
```

Endpoint diagnostyczny paczki dla przyszlego agenta:

```text
GET http://127.0.0.1:8000/api/modules/module-01-python-foundations/review-context/exercises
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

## Zakres etapów 6-8

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
- statusy `W trakcie`, `Do sprawdzenia`, `Rozwiazane`, `Do powtorki`,
- przechodzenie do poprzedniego i nastepnego cwiczenia.
- parsowanie pytan z `knowledge_check.md` wedlug sekcji,
- pokazywanie jednego pytania albo scenariusza naraz,
- zapis odpowiedzi w `knowledge_check_answers`,
- statusy `W trakcie`, `Do sprawdzenia`, `Rozwiazane`, `Do powtorki`,
- licznik przerobionych pytan i przechodzenie poprzednie/nastepne.
- zapis odpowiedzi z konca Materialu i Mini-projektu w `part_answers`,
- zapis rozwiazania Mini-projektu do sprawdzenia w `mini_project_submission`.
- przyciski `Sprawdz` dla Materialu, Mini-projektu, Cwiczen i Sprawdzenia wiedzy,
- mockowane endpointy `review/*`, ktore zapisuja feedback przy konkretnej odpowiedzi,
- zapis feedbacku w `part_feedback`, `mini_project_feedback`, `exercise_feedback` i `knowledge_check_feedback`.
- wydzielony backendowy kontrakt `ReviewContext`,
- backendowy `ReviewService`, przez ktory przechodza wszystkie endpointy `review/*`,
- diagnostyczny endpoint `review-context/{segment}` do podejrzenia paczki przekazywanej przyszlemu agentowi.
- segmentowy kontrakt `ReviewResult` z lista wynikow `ReviewResultItem`,
- walidacje, ze adapter zwrocil wynik dla wszystkich i tylko tych `item_id`, ktore byly w `ReviewContext`,
- opcjonalny `OpenAIReviewAdapter` aktywowany przez `REVIEW_ADAPTER=openai`,
- Responses API z JSON schema structured output zamiast luznego parsowania tekstu.

Te etapy celowo nie zawieraja jeszcze:
- uruchamiania kodu Pythona,
- historii rozmowy ani pamieci agenta,
- przechowywania sekretow w kodzie albo w plikach sledzonych przez git.

## Sekrety i dane lokalne

Aplikacja nie potrzebuje klucza API w trybie mockowym. Jesli wlaczasz bezposrednie wywolanie modelu przez `REVIEW_ADAPTER=openai`, sekret powinien byc czytany tylko po stronie backendu z lokalnego `.env` albo zmiennych srodowiskowych.

Repo ignoruje:
- `.env` i `.env.*`,
- pliki kluczy `*.pem` i `*.key`,
- lokalny postep `platform/data/*.json`,
- `node_modules/`, `dist/` i `.venv/`.

Nie zapisuj sekretow w `platform/frontend/src/`, w `vite.config.js`, w Markdownach modulow ani w `platform/data/progress.json`. Frontend powinien komunikowac sie z backendem, a backend powinien trzymac integracje wymagajace sekretow po swojej stronie.
