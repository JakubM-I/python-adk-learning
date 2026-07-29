# Architektura platformy

## Decyzja startowa

Platforma powinna być małą aplikacją lokalną:
- backend: Python,
- frontend: React,
- dane źródłowe: pliki Markdown w `modules/`,
- dane użytkownika: lokalny plik JSON albo SQLite.

Rekomendowany start:
- FastAPI jako backend HTTP,
- React + Vite jako frontend,
- Pythonowy parser Markdown/metadanych,
- prosty zapis postępu w `data/progress.json`.

FastAPI jest dobrym wyborem, bo wzmacnia naukę Pythona w praktycznym kontekście:
- routing,
- modele danych,
- walidacja,
- JSON API,
- organizacja kodu,
- testy backendu.

React jest dobrym wyborem, bo użytkownik zna ten ekosystem i może szybciej oceniać ergonomię UI.

## Granice systemu

### Warstwa treści

Źródłem treści są:
- `modules/<module>/module.md`,
- `modules/<module>/exercises.md`,
- `modules/<module>/mini_project.md`,
- `modules/<module>/knowledge_check.md`,
- `modules/<module>/summary.md`.

Aplikacja nie powinna modyfikować tych plików podczas zwykłej nauki.
Zmiany w materiałach robi agent lub użytkownik w repo.

### Warstwa aplikacji

Kod aplikacji powinien mieszkać poza `modules/`, na przykład:

```text
platform/
  backend/
  frontend/
  data/
```

`platform/backend/` odpowiada za:
- wykrywanie modułów,
- czytanie Markdown,
- parsowanie ćwiczeń i pytań,
- API dla frontendu,
- zapis i odczyt postępu.

`platform/frontend/` odpowiada za:
- widok listy modułów,
- widok modułu,
- tryb ćwiczeń,
- tryb sprawdzenia wiedzy,
- notatki,
- postęp.

`platform/data/` przechowuje dane lokalne użytkownika.
Nie należy tam trzymać źródłowych materiałów dydaktycznych.

## Proponowane API MVP

Minimalne endpointy:

```text
GET /api/modules
GET /api/modules/{module_id}
GET /api/modules/{module_id}/content/{part}
GET /api/modules/{module_id}/exercises
GET /api/modules/{module_id}/knowledge-check
GET /api/progress
PUT /api/progress
```

`part` może przyjmować:
- `module`,
- `exercises`,
- `mini_project`,
- `knowledge_check`,
- `summary`.

W pierwszym MVP backend może zwracać:
- surowy Markdown,
- podstawowe metadane modułu,
- sparsowaną listę ćwiczeń,
- aktualny postęp.

Renderowanie Markdown może odbywać się po stronie frontendu.

## Model danych modułu

Minimalny model zwracany przez API:

```json
{
  "id": "module-01-python-foundations",
  "number": 1,
  "title": "Python foundations for JS developer",
  "path": "modules/module-01-python-foundations",
  "parts": ["module", "exercises", "mini_project", "knowledge_check", "summary"]
}
```

`id` powinien pochodzić z nazwy folderu.
`title` powinien pochodzić z pierwszego nagłówka `#` w `module.md`.

## Model postępu

Na start wystarczy prosty JSON:

```json
{
  "modules": {
    "module-01-python-foundations": {
      "completed_parts": ["module"],
      "current_exercise": "exercise-1",
      "completed_exercises": [],
      "exercise_statuses": {
        "exercise-1": "review"
      },
      "notes": "Moje notatki...",
      "answers": {
        "exercise-1": "Moja odpowiedz..."
      },
      "exercise_feedback": {
        "exercise-1": {
          "status": "solved",
          "summary": "Krótka ocena",
          "comments": ["Konkretna uwaga"],
          "next_step": "Pytanie albo kolejny krok",
          "checked_at": "2026-07-27T10:00:00Z"
        }
      }
    }
  }
}
```

W MVP dane mogą być przechowywane w pliku.
SQLite warto rozważyć dopiero wtedy, gdy pojawi się historia odpowiedzi, wiele sesji, tagowanie albo zaawansowane wyszukiwanie.

Statusy elementów sprawdzanych są wspólne dla ćwiczeń i sprawdzenia wiedzy:
`draft`, `review`, `solved`, `needs_revision`.
Ten sam obiekt feedbacku powinien być używany dla pytań sprawdzających z materiału, mini-projektu, ćwiczeń i sprawdzenia wiedzy.

## Parsing Markdown

W MVP można zastosować pragmatyczny parser oparty o nagłówki Markdown.

Ćwiczenia w `exercises.md` mają strukturę:
- `### Ćwiczenie N: Tytuł`,
- `Cel:`,
- `Opis:`,
- `Ograniczenia / wskazówki:`,
- `Oczekiwany efekt:`.

Backend powinien zamieniać to na listę obiektów:

```json
{
  "id": "exercise-1",
  "title": "Normalizacja listy stringów",
  "level": "warmup",
  "goal": "...",
  "description_markdown": "...",
  "constraints_markdown": "...",
  "expected_effect_markdown": "..."
}
```

Ważne: w trybie ćwiczeń UI nie powinno pokazywać wszystkiego naraz.
Na przykład `expected_effect` może być zwinięte albo dostępne dopiero po kliknięciu.

## Integracja z agentem

Frontend nie powinien znać szczegółów paczki dla agenta.
Użytkownik pracuje przez proste przyciski `Sprawdź`, a backend buduje segmentowy `ReviewContext`.

`ReviewContext` powinien zawierać:
- `segment`,
- `module`,
- `source_context_markdown`,
- `items`,
- `review_instructions`,
- `expected_response_schema`.

Segmenty review:
- `material`,
- `mini_project`,
- `exercises`,
- `knowledge_check`.

Docelowy przepływ:
1. frontend zapisuje odpowiedź i wywołuje `POST review/*`,
2. backend buduje `ReviewContext` tylko dla jednego segmentu,
3. `ReviewService` przekazuje kontekst do adaptera oceny,
4. adapter zwraca feedback w formacie `ReviewFeedback`,
5. backend zapisuje feedback i aktualizuje statusy w `platform/data/progress.json`.

W Etapie 7 adapter pozostaje mockowy.
Prawdziwy model powinien zostać podpięty później przez wymianę adaptera, bez zmiany UI i bez zmiany endpointów `review/*`.

## Zasady bezpieczeństwa

1. Nie uruchamiaj dowolnego kodu użytkownika w MVP.
2. Nie zapisuj postępu do plików modułu.
3. Nie nadpisuj materiałów dydaktycznych przez endpointy aplikacji.
4. Endpointy modyfikujące dane powinny dotyczyć tylko `platform/data/`.
5. Runner kodu, jeśli powstanie, wymaga osobnej specyfikacji.

## Kryteria techniczne

Kod platformy powinien:
- być prosty do uruchomienia lokalnie,
- mieć czytelną strukturę,
- używać typów Pythona tam, gdzie pomaga to zrozumieć kontrakty,
- mieć testy dla parsera modułów i zapisu postępu,
- nie wymagać zewnętrznej bazy danych,
- nie wymagać kont ani usług chmurowych.
