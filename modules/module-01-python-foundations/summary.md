# Podsumowanie — Python foundations for JS developer

## Najważniejsze pojęcia

- Wcięcia w Pythonie definiują strukturę kodu.
- `list`, `tuple`, `dict`, `set` to podstawowe kolekcje do pracy z danymi.
- Mutowalność ma realny wpływ na stabilność kodu narzędzi.
- Comprehensions przyspieszają transformacje, ale wymagają umiaru.
- Importy i podział kodu na moduły ułatwiają rozwój i testowanie.

## Checklista
- [ ] Rozumiem intuicję
- [ ] Potrafię wyjaśnić temat własnymi słowami
- [ ] Potrafię napisać prosty przykład
- [ ] Rozumiem typowe pułapki
- [ ] Widzę związek z ADK
- [ ] Potrafię znormalizować payload bez mutowania wejścia
- [ ] Potrafię użyć comprehension i ocenić, czy jest czytelna

## Do powtórki

- Różnica: przypisanie referencji vs kopia (`copy`, `deepcopy` kiedy potrzebne).
- Bezpieczne pobieranie danych ze słownika (`get`, wartości domyślne).
- Konwersja i walidacja danych wejściowych (`str`, `int`, zakresy).

## Najczęstsze błędy

- Mutowalne argumenty domyślne.
- Nadmiernie złożone jednowierszowce.
- Zbyt późne walidowanie danych wejściowych.
- Przypadkowe nadpisywanie nazw modułów.

## Most do następnego modułu

W module 2 przechodzimy do funkcji w podejściu "tools mindset":
- jak projektować podpis funkcji pod użycie narzędziowe,
- jak pracować z argumentami (`*args`, `**kwargs`),
- jak dokumentować kontrakt funkcji (docstring) i przygotować grunt pod testy.

## Pytanie na start modułu 2

Która z funkcji, które napisałeś(-aś) w module 1, mogłaby już teraz stać się narzędziem agenta i jaki miałaby kontrakt wejścia/wyjścia?
