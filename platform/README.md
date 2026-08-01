# Lokalna platforma nauki

To jest aplikacja webowa do przerabiania modułów z katalogu `modules/` w przeglądarce.

## Szybki start

Platforma używa stałych portów:

```text
backend:  http://127.0.0.1:8000
frontend: http://127.0.0.1:5173
```

Przed startem sprawdź, czy nie działa poprzednia instancja:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

Terminal 1 — backend:

```bash
cd platform/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend:

```bash
cd platform/frontend
npm install
npm run dev
```

Otwórz aplikację:

```text
http://127.0.0.1:5173
```

Szybkie endpointy kontrolne:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/modules
http://127.0.0.1:8000/api/review-profiles
http://127.0.0.1:8000/api/review-prompt-info/material
```

Po pracy zamknij backend i frontend, a potem sprawdź porty ponownie:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

## Szybki start z LM Studio

1. Uruchom lokalny server LM Studio na:

```text
http://127.0.0.1:1234
```

2. Sprawdź dostępne modele:

```bash
curl http://127.0.0.1:1234/v1/models
```

3. Ustaw lokalny profil w ignorowanym pliku:

```text
platform/backend/review_profiles.local.json
```

Przykład:

```json
{
  "active_profile": "lmstudio_local",
  "profiles": {
    "lmstudio_local": {
      "model": "google/gemma-4-e4b",
      "base_url": "http://127.0.0.1:1234/v1"
    }
  }
}
```

Profil `lmstudio_local` dziedziczy z domyślnej konfiguracji `provider: "openai_compatible"` i `prompt_variant: "compact"`.

Etap 10 zawiera:
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
- profile providerów dla mocka, OpenAI-compatible API, LM Studio i Ollama,
- opcjonalny adapter LLM ze structured output,
- twardy wynik segmentowy `ReviewResult` walidowany przed zapisem progressu,
- diagnostyczny endpoint aktywnego profilu review bez sekretów,
- segmentowe prompty review w plikach Markdown,
- warianty promptow `default` i `compact` wybierane przez profil modelu,
- diagnostyczny endpoint promptu review bez odpowiedzi ucznia i bez tresci promptu,
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

### Konfiguracja review providerów

Domyślnie backend używa profilu `mock` i nie wymaga żadnych sekretów. Profile są w:

```text
platform/backend/review_profiles.json
```

Ten plik jest śledzony przez git i powinien zawierać tylko bezpieczne przykłady konfiguracji. Prywatne ustawienia lokalne można zapisać w ignorowanym pliku:

```text
platform/backend/review_profiles.local.json
```

Aktywny profil można też nadpisać bez edycji plików:

```bash
REVIEW_PROFILE=lmstudio_local
```

Przykład lokalnego override:

```json
{
  "active_profile": "ollama_local",
  "profiles": {
    "ollama_local": {
      "provider": "ollama",
      "model": "llama3.1",
      "base_url": "http://127.0.0.1:11434",
      "temperature": 0,
      "prompt_variant": "compact"
    }
  }
}
```

Przykład profilu wymagającego sekretu:

```bash
REVIEW_PROFILE=openai_gpt5
OPENAI_API_KEY=sk-...
```

### OpenRouter

OpenRouter jest skonfigurowany jako profil OpenAI-compatible:

```bash
REVIEW_PROFILE=openrouter_openai_latest
```

`REVIEW_PROFILE` to zmienna środowiskowa ustawiana przy uruchamianiu backendu, a nie wpis w pliku z kluczem. Jeśli nie chcesz ustawiać jej w terminalu za każdym razem, ustaw aktywny profil w ignorowanym pliku lokalnym:

```text
platform/backend/review_profiles.local.json
```

Przykład wyboru OpenRouter i konkretnego modelu:

```json
{
  "active_profile": "openrouter_openai_latest",
  "profiles": {
    "openrouter_openai_latest": {
      "model": "openai/gpt-5-mini"
    }
  }
}
```

Ten plik lokalny nadpisuje tylko podane pola. Reszta profilu, czyli `provider`, `base_url`, `api_key_env`, `api_key_file`, nagłówki i wariant promptu, zostaje odziedziczona z `platform/backend/review_profiles.json`.

Jeśli chcesz jednorazowo wymusić profil bez edycji pliku lokalnego, uruchom backend z env var:

```bash
REVIEW_PROFILE=openrouter_openai_latest uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Klucz API można podać jako env var:

```bash
OPENROUTER_API_KEY=sk-or-...
```

Wygodniejsza lokalna opcja to ignorowany plik z samą wartością klucza:

```text
platform/backend/.secrets/openrouter_api_key.txt
```

Utwórz katalog `.secrets`, wklej do pliku tylko klucz API i nie dodawaj składni `OPENROUTER_API_KEY=...`. Backend najpierw sprawdza env var `OPENROUTER_API_KEY`, a jeśli jej nie ma, czyta ten lokalny plik.

Sekret jest czytany z env var wskazanego w `api_key_env` albo z lokalnego pliku wskazanego w `api_key_file`. Brak klucza, błąd API albo odpowiedź niezgodna ze schematem `ReviewResult` przerywa review bez aktualizacji `platform/data/progress.json`.

Frontend nie przechowuje sekretów. Nie ustawiaj kluczy API w `platform/frontend/`, w `VITE_*`, w plikach Markdown, w `platform/data/progress.json` ani w `review_profiles*.json`.

### Instrukcje review per segment

Prompt/instrukcje dla modelu są w plikach:

```text
platform/backend/review_prompts/
```

Każdy segment ma wariant `default` i `compact`, na przykład:

```text
material.default.md
material.compact.md
exercises.default.md
exercises.compact.md
```

Profile lokalne, takie jak LM Studio i Ollama, powinny używać `prompt_variant: "compact"`. Ten wariant ogranicza długość feedbacku i zmniejsza payload wysyłany do modelu. Mocniejsze modele mogą używać `default`.

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

Endpoint diagnostyczny profili review bez sekretów:

```text
GET http://127.0.0.1:8000/api/review-profiles
```

Endpoint diagnostyczny promptu review bez odpowiedzi ucznia:

```text
GET http://127.0.0.1:8000/api/review-prompt-info/material
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

## Zakres etapów 6-10

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
- profile providerow wybierane przez `review_profiles.json`, `review_profiles.local.json` albo `REVIEW_PROFILE`,
- OpenAI-compatible chat completions dla OpenAI i LM Studio,
- natywny endpoint `/api/chat` dla Ollama,
- JSON schema structured output zamiast luznego parsowania tekstu.
- pliki promptow review per segment i wariant,
- lekki payload review dla lokalnych modeli,
- endpoint diagnostyczny promptu bez prywatnych odpowiedzi.

Te etapy celowo nie zawieraja jeszcze:
- uruchamiania kodu Pythona,
- historii rozmowy ani pamieci agenta,
- przechowywania sekretow w kodzie albo w plikach sledzonych przez git.

## Sekrety i dane lokalne

Aplikacja nie potrzebuje klucza API w trybie mockowym ani przy lokalnych profilach bez `api_key_env`. Jesli wlaczasz profil wymagajacy sekretu, sekret powinien byc czytany tylko po stronie backendu z lokalnego `.env` albo zmiennych srodowiskowych.

Repo ignoruje:
- `.env` i `.env.*`,
- pliki kluczy `*.pem` i `*.key`,
- lokalny postep `platform/data/*.json`,
- lokalny override `platform/backend/review_profiles.local.json`,
- lokalny katalog sekretow `platform/backend/.secrets/`,
- `node_modules/`, `dist/` i `.venv/`.

Nie zapisuj sekretow w `platform/frontend/src/`, w `vite.config.js`, w Markdownach modulow, w `platform/data/progress.json` ani w sledzonych plikach profili review. Frontend powinien komunikowac sie z backendem, a backend powinien trzymac integracje wymagajace sekretow po swojej stronie.

Pliki `platform/backend/review_prompts/*.md` sa sledzone przez git i nie powinny zawierac prywatnych odpowiedzi ucznia ani sekretow.
