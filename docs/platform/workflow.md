# Workflow pracy nad platformą

## Cel

Ten workflow dotyczy tylko lokalnej platformy webowej.
Nie zastępuje workflow tworzenia modułów.

Praca nad platformą ma iść etapami.
Każdy etap powinien kończyć się działającym fragmentem aplikacji, który można uruchomić lokalnie.

## Dokumenty źródłowe

Przy pracy nad platformą agent powinien uwzględniać:
- `AGENTS.md`,
- `docs/platform/product_spec.md`,
- `docs/platform/architecture.md`,
- `docs/platform/content_contract.md`,
- `docs/platform/workflow.md`,
- `docs/platform/ui_guidelines.md`.

Gdy zmiana dotyka sposobu pisania modułów, agent powinien dodatkowo sprawdzić:
- `docs/material_generation.md`,
- `docs/content_guidelines.md`,
- `templates/module-template/`.

## Etap 0: Przygotowanie specyfikacji

Cel:
- ustalić zakres MVP,
- zapisać architekturę,
- oddzielić instrukcje platformy od instrukcji tworzenia modułów.

Kryteria ukończenia:
- istnieje dokumentacja w `docs/platform/`,
- `AGENTS.md` wskazuje, kiedy używać dokumentów platformy,
- wiadomo, czego nie budujemy w MVP.

## Etap 1: Szkielet aplikacji

Cel:
- utworzyć katalog `platform/`,
- dodać backend i frontend,
- uruchomić lokalną aplikację,
- pokazać prosty ekran roboczy.

Zakres:
- FastAPI backend,
- React frontend,
- podstawowe komendy uruchomieniowe,
- bez pełnego parsera modułów.

Kryteria ukończenia:
- backend startuje lokalnie,
- frontend startuje lokalnie,
- frontend potrafi pobrać prostą odpowiedź z backendu,
- instrukcja uruchomienia jest zapisana w repo.

## Etap 2: Czytnik modułów

Cel:
- wykrywać moduły z katalogu `modules/`,
- czytać pięć plików modułu,
- renderować materiał w UI.

Zakres:
- endpoint `GET /api/modules`,
- endpoint treści modułu,
- widok listy modułów,
- widok szczegółów modułu,
- zakładki części modułu.

Kryteria ukończenia:
- moduł 1 jest widoczny w aplikacji,
- można przełączać części modułu,
- dodanie folderu kolejnego modułu nie wymaga zmiany kodu frontendu.

## Etap 3: Postęp i notatki

Cel:
- zapisywać lokalny postęp użytkownika,
- dodać prywatne notatki.

Zakres:
- plik `platform/data/progress.json`,
- endpoint odczytu postępu,
- endpoint zapisu postępu,
- oznaczanie części modułu jako ukończonej,
- pole notatek per moduł.

Kryteria ukończenia:
- postęp zostaje po odświeżeniu,
- notatki zostają po odświeżeniu,
- aplikacja nie modyfikuje plików w `modules/`.

## Etap 4: Tryb ćwiczeń

Cel:
- poprawić doświadczenie ćwiczeń, żeby użytkownik nie widział całego pliku naraz.

Zakres:
- parser `exercises.md`,
- lista ćwiczeń jako dane strukturalne,
- jedno ćwiczenie na ekranie,
- pole odpowiedzi,
- zapis odpowiedzi,
- oznaczanie ćwiczenia jako rozwiązane lub do sprawdzenia.

Kryteria ukończenia:
- ćwiczenie 1 z modułu 1 jest pokazane jako osobna karta,
- odpowiedź użytkownika jest zapisywana,
- oczekiwany efekt nie dominuje widoku przed próbą użytkownika,
- można przejść do następnego ćwiczenia.

## Etap 5: Knowledge check

Cel:
- przeprowadzać sprawdzenie wiedzy jako serię pytań.

Zakres:
- parser `knowledge_check.md`,
- jedno pytanie lub scenariusz na ekranie,
- zapis odpowiedzi,
- status pytań.

Kryteria ukończenia:
- pytania z modułu 1 można przechodzić pojedynczo,
- odpowiedzi są zapisane,
- użytkownik ma jasny status, co zostało już przerobione.

## Etap 6: Integracja z agentem

Cel:
- przygotować sprawdzanie odpowiedzi przez agenta bez przepisywania całego materiału w UI.

Zakres:
- format kontekstu dla agenta,
- endpoint lub eksport paczki sprawdzania,
- jasne rozdzielenie: treść ćwiczenia, odpowiedź użytkownika, oczekiwany efekt, feedback.

Kryteria ukończenia:
- agent dostaje tylko potrzebny kontekst,
- agent nie pokazuje odpowiedzi przed próbą użytkownika,
- feedback jest zapisany przy odpowiedzi.

## Zasady pracy

1. Każdy etap ma być mały i możliwy do uruchomienia.
2. Nie dodawaj funkcji z późniejszych etapów, jeśli utrudniają domknięcie obecnego.
3. Nie przebudowuj struktury modułów bez wyraźnej potrzeby.
4. Jeśli parser Markdown wymaga zmiany stylu modułów, najpierw zaktualizuj kontrakt treści.
5. Po każdej zmianie aplikacji uruchom minimalną weryfikację.
6. Preferuj prosty kod i czytelne kontrakty zamiast frameworkowej magii.

## Definicja gotowości zmiany

Zmiana w platformie jest gotowa, jeśli:
- aplikacja uruchamia się lokalnie,
- główny przepływ zmiany działa w przeglądarce lub przez API,
- nie zostały przypadkowo zmienione materiały w `modules/`,
- dokumentacja uruchomienia jest aktualna,
- parser treści nadal działa dla modułu 1.
