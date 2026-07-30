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
- segmentowe przyciski `Sprawdź` dla materiału, ćwiczeń, mini-projektu i sprawdzenia wiedzy,
- format feedbacku zapisywany przy konkretnej odpowiedzi,
- endpointy `review/*`, które na start mogą zwracać mock oceny,
- jasne rozdzielenie: treść segmentu, odpowiedź użytkownika, kryteria, feedback.

Kryteria ukończenia:
- agent albo mock dostaje tylko kontekst jednego segmentu,
- agent nie pokazuje odpowiedzi przed próbą użytkownika,
- feedback jest zapisany przy odpowiedzi,
- status ocenianego elementu przechodzi na `Rozwiązane` albo `Do powtórki`.

## Etap 7: Kontrakt review context i adapter agenta

Cel:
- przygotować backend pod prawdziwe sprawdzanie przez agenta bez zmiany prostego flow w UI.

Zakres:
- wydzielenie modeli, parserów, zapisu postępu i logiki review z jednego dużego pliku backendu,
- wspólny model `ReviewContext` dla materiału, ćwiczeń, mini-projektu i sprawdzenia wiedzy,
- diagnostyczny endpoint `GET /api/modules/{module_id}/review-context/{segment}`,
- `ReviewService`, który przyjmuje kontekst segmentu i zwraca feedback w obecnym formacie,
- mockowy adapter jako wymienialna warstwa przed przyszłym podpięciem modelu.

Kryteria ukończenia:
- endpointy `POST review/*` działają przez `ReviewService`,
- endpoint `review-context/{segment}` pokazuje tylko dane danego segmentu,
- ćwiczenia i sprawdzenie wiedzy wysyłają do kontekstu tylko elementy oznaczone jako `Do sprawdzenia`,
- UI nie musi znać paczki kontekstu i nadal używa obecnego flow `Sprawdź`,
- backend nie wymaga sekretów ani zewnętrznego modelu.

## Etap 8: Structured Agent Review Adapter

Cel:
- dodać opcjonalny adapter OpenAI do istniejącego `ReviewService`,
- utrzymać mock jako domyślne zachowanie lokalne,
- wymusić twardy kontrakt segmentowego wyniku `ReviewResult`.

Zakres:
- modele `ReviewResult` i `ReviewResultItem`,
- adaptery zwracające wynik dla całego segmentu, a nie pojedynczy feedback,
- `OpenAIReviewAdapter` aktywowany przez `REVIEW_ADAPTER=openai`,
- structured output przez JSON schema w Responses API,
- walidacja kompletności `item_id` przed zapisem progressu,
- zapis progressu dopiero po poprawnej odpowiedzi adaptera.

Kryteria ukończenia:
- `REVIEW_ADAPTER=mock` działa bez `OPENAI_API_KEY`,
- `REVIEW_ADAPTER=openai` wymaga `OPENAI_API_KEY` tylko po stronie backendu,
- błędy API, konfiguracji albo walidacji nie aktualizują `platform/data/progress.json`,
- endpointy `POST review/*` i `GET review-context/{segment}` zachowują dotychczasowy kontrakt dla frontendu,
- frontend nie przechowuje sekretów i nie zna szczegółów adaptera.

## Etap 9: Provider Profiles for Review LLM

Cel:
- odwiązać review od jednego API i jednego modelu,
- wybierać model przez lokalne profile providerów,
- zachować mock jako domyślny tryb bez sekretów.

Zakres:
- śledzony plik `platform/backend/review_profiles.json` z bezpiecznymi przykładami,
- ignorowany plik `platform/backend/review_profiles.local.json` na prywatne ustawienia,
- override aktywnego profilu przez `REVIEW_PROFILE`,
- wspólny `LLMReviewAdapter` i osobne klienty providerów,
- profile dla OpenAI-compatible, LM Studio i Ollama,
- read-only endpoint `GET /api/review-profiles` bez wartości sekretów.

Kryteria ukończenia:
- `mock` działa bez kluczy API,
- OpenAI i LM Studio używają OpenAI-compatible chat completions ze structured output,
- Ollama używa natywnego `/api/chat` z JSON schema w `format`,
- brak sekretu, błąd API albo błędny `ReviewResult` nie aktualizują progressu,
- frontend nie przechowuje ani nie wysyła sekretów.

## Etap 10: Segment Review Prompts

Cel:
- oddzielić wybór providera/modelu od instrukcji rozmowy z modelem,
- utrzymywać prompt review jako pliki Markdown per segment,
- przyspieszyć lokalne modele przez wariant `compact`.

Zakres:
- katalog `platform/backend/review_prompts/`,
- warianty `default` i `compact` dla `material`, `exercises`, `mini_project`, `knowledge_check`,
- pole `prompt_variant` w profilu review,
- lekki payload review zamiast pełnego dumpa `ReviewContext`,
- metadata-only endpoint `GET /api/review-prompt-info/{segment}`.

Kryteria ukończenia:
- `ReviewContext.review_instructions` pochodzi z plików promptów,
- LM Studio i Ollama używają wariantu `compact`,
- endpoint diagnostyczny nie zwraca odpowiedzi ucznia ani pełnego promptu,
- istnieją testy loadera promptów, wariantu profilu i lżejszego payloadu.

## Etap 11: Review Operations Runbook

Cel:
- ułatwić codzienne uruchamianie platformy i ręczne testowanie prawdziwego review,
- opisać przewidywalny flow backend + frontend + lokalny LLM,
- zebrać diagnostykę w jednym miejscu przed dodawaniem kolejnych funkcji.

Zakres:
- krótkie instrukcje startu backendu i frontendu,
- opis konfiguracji `review_profiles.local.json`,
- checklisty dla mocka, LM Studio, Ollama i OpenAI,
- ręczne scenariusze testowe dla `material`, `exercises`, `mini_project`, `knowledge_check`,
- opis typowych problemów: zajęte porty, brak modelu, wolny model, błędny JSON, brak sekretu.

Kryteria ukończenia:
- da się uruchomić platformę z README bez szukania komend w historii rozmowy,
- da się potwierdzić aktywny profil i prompt przez endpointy diagnostyczne,
- manualny test review nie modyfikuje przypadkowo plików modułu,
- wiadomo, co sprawdzić przed zgłoszeniem błędu adaptera LLM.

## Zasady pracy

1. Każdy etap ma być mały i możliwy do uruchomienia.
2. Nie dodawaj funkcji z późniejszych etapów, jeśli utrudniają domknięcie obecnego.
3. Nie przebudowuj struktury modułów bez wyraźnej potrzeby.
4. Jeśli parser Markdown wymaga zmiany stylu modułów, najpierw zaktualizuj kontrakt treści.
5. Po każdej zmianie aplikacji uruchom minimalną weryfikację.
6. Preferuj prosty kod i czytelne kontrakty zamiast frameworkowej magii.

## Porty i sprzątanie procesów

Stałe porty platformy:
- backend: `127.0.0.1:8000`,
- frontend: `127.0.0.1:5173`.

Przed uruchomieniem lokalnych serwerów sprawdź:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

Jeśli port jest zajęty przez proces z katalogu `platform/backend` albo `platform/frontend`, zamknij ten proces i dopiero wtedy uruchom nową instancję. Nie traktuj portów `8001`, `8010`, `8020`, `5174`, `5180` ani `5181` jako domyślnego obejścia; pojawiły się jako skutek pozostawionych wcześniejszych uruchomień i nie powinny być utrwalane w workflow.

Po zakończeniu pracy nad etapem:
1. zatrzymaj backend i frontend uruchomione na potrzeby weryfikacji,
2. sprawdź ponownie porty `8000` i `5173`,
3. w podsumowaniu pracy napisz, czy procesy zostały zamknięte.

## Definicja gotowości zmiany

Zmiana w platformie jest gotowa, jeśli:
- aplikacja uruchamia się lokalnie,
- główny przepływ zmiany działa w przeglądarce lub przez API,
- nie zostały przypadkowo zmienione materiały w `modules/`,
- dokumentacja uruchomienia jest aktualna,
- parser treści nadal działa dla modułu 1.
- procesy backendu i frontendu uruchomione podczas pracy zostały zatrzymane.
