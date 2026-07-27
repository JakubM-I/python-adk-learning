# Specyfikacja platformy lokalnej

## Cel

Platforma ma zamienić repo z materiałami Markdown w lokalne środowisko nauki w przeglądarce.
Nie zastępuje katalogu `modules/` i nie przenosi treści do bazy danych.
Repo nadal jest źródłem prawdy, a aplikacja jest wygodną warstwą pracy nad modułami.

Główny problem do rozwiązania:
- materiały w plikach są dobre do przechowywania,
- ale ćwiczenia, sprawdzanie wiedzy, notatki i postęp są wygodniejsze w aplikacji.

## Użytkownik docelowy

Platforma jest projektowana dla jednej osoby uczącej się lokalnie:
- zna JavaScript/React,
- uczy się Pythona pod praktyczne użycie z ADK,
- chce przechodzić moduły etapami,
- chce dostawać pojedyncze ćwiczenie, a nie cały plik z odpowiedziami lub podpowiedziami naraz.

To nie jest publiczny LMS ani produkt SaaS.
Priorytetem jest ergonomia osobistej nauki, a nie konta użytkowników, role, płatności albo panel administracyjny.

## Zakres MVP

Pierwsza wersja ma obsłużyć moduł 1 i pokazać pełny pionowy przepływ nauki.

MVP powinno zawierać:
- listę modułów wykrytą z katalogu `modules/`,
- widok wybranego modułu,
- zakładki: materiał, ćwiczenia, mini-projekt, sprawdzenie wiedzy, podsumowanie,
- renderowanie Markdown,
- zapis postępu lokalnie,
- możliwość oznaczenia sekcji jako ukończonej,
- pole na prywatne notatki do modułu,
- tryb ćwiczeń, który pokazuje jedno ćwiczenie naraz,
- miejsce na odpowiedź użytkownika do ćwiczenia.

MVP nie musi jeszcze zawierać:
- automatycznego uruchamiania kodu Pythona,
- kont użytkowników,
- synchronizacji w chmurze,
- edytora modułów,
- pełnej integracji z agentem AI w UI,
- systemu oceniania rozwiązania przez model.

## Zakres drugiego etapu

Drugi etap powinien rozwinąć interaktywność:
- zapisywanie odpowiedzi do ćwiczeń,
- przechodzenie ćwiczeń po kolei,
- osobny tryb knowledge check,
- ukrywanie odpowiedzi, wskazówek i kryteriów do momentu, w którym użytkownik ich potrzebuje,
- eksport notatek lub odpowiedzi do plików w `shared/`,
- przygotowanie punktu integracji z agentem sprawdzającym odpowiedzi.

## Zakres trzeciego etapu

Trzeci etap może dodać pracę z kodem:
- uruchamianie małych snippetów Pythona lokalnie,
- sprawdzanie prostych testów dla ćwiczeń,
- zapisywanie rozwiązań do katalogu roboczego,
- powiązanie ćwiczeń z testami,
- bezpieczny runner ograniczony do lokalnego środowiska nauki.

Ten etap wymaga osobnej decyzji bezpieczeństwa.
Nie należy dodawać wykonywania dowolnego kodu w pierwszym MVP.

## Zasady produktu

1. Aplikacja wspiera aktywną naukę, nie tylko czytanie.
2. Użytkownik nie powinien widzieć całego pliku ćwiczeń naraz w trybie ćwiczeń.
3. Materiały źródłowe pozostają w Markdownie.
4. Platforma może dodawać metadane, ale nie powinna wymuszać ciężkiego CMS-a.
5. Interfejs ma być lokalny, spokojny i praktyczny.
6. Pierwszy ekran aplikacji ma być miejscem pracy, nie landing page.
7. Każda funkcja powinna odpowiadać realnemu etapowi nauki.

## Kluczowe przepływy

### Czytanie materiału

1. Użytkownik wybiera moduł.
2. Otwiera zakładkę `Materiał`.
3. Czyta wyrenderowany `module.md`.
4. Zaznacza sekcję jako ukończoną albo dodaje notatkę.

### Praca z ćwiczeniem

1. Użytkownik otwiera zakładkę `Ćwiczenia`.
2. Platforma pokazuje pierwsze nierozwiązane ćwiczenie.
3. Użytkownik wpisuje odpowiedź.
4. Odpowiedź zostaje zapisana lokalnie.
5. Użytkownik oznacza ćwiczenie jako gotowe do sprawdzenia albo rozwiązane.

### Sprawdzenie wiedzy

1. Użytkownik otwiera zakładkę `Sprawdzenie wiedzy`.
2. Platforma pokazuje jedno pytanie lub scenariusz.
3. Użytkownik odpowiada.
4. Odpowiedź zostaje zapisana jako materiał do późniejszego omówienia z agentem.

## Kryteria sukcesu MVP

MVP jest gotowe, jeśli:
- można uruchomić aplikację lokalnie,
- moduł 1 jest widoczny w przeglądarce,
- wszystkie pięć plików modułu da się czytać w UI,
- ćwiczenia można przerabiać pojedynczo,
- postęp i notatki nie znikają po odświeżeniu strony,
- dodanie przyszłego modułu do `modules/` nie wymaga ręcznej zmiany kodu aplikacji.
