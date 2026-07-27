# Ćwiczenia — Python foundations for JS developer

## Ćwiczenia rozgrzewkowe

### Ćwiczenie 1: Normalizacja listy stringów
Cel: przećwiczyć list comprehension i podstawową obróbkę tekstu.

Opis:
Masz listę:

```python
raw = ["  API", "adk ", "", " Tool ", "API"]
```

Przygotuj nową listę z wartościami:
- bez spacji na brzegach,
- lowercase,
- bez pustych stringów.

Ograniczenia / wskazówki:
- użyj jednej list comprehension,
- nie mutuj listy `raw`.

Oczekiwany efekt:
`['api', 'adk', 'tool', 'api']`

### Ćwiczenie 2: Mutowalność w praktyce
Cel: zrozumieć różnicę między kopią referencji a kopią danych.

Opis:
Utwórz listę `a = [1, 2, 3]`, potem:
- `b = a`
- `c = a.copy()`

Dodaj `4` do `b` i sprawdź wartości `a`, `b`, `c`.

Ograniczenia / wskazówki:
- wypisz wynik i własnymi słowami opisz, co zaszło.

Oczekiwany efekt:
- `a` i `b` mają ten sam stan,
- `c` zostaje bez zmiany.

## Ćwiczenia średnie

### Ćwiczenie 3: Czyszczenie payloadu narzędzia
Cel: użyć `dict`, `.get()`, konwersji typów i walidacji.

Opis:
Napisz funkcję `clean_payload(payload: dict) -> dict`, która:
- pobiera `query` i przycina spacje,
- pobiera `limit` i konwertuje do `int`,
- jeśli `limit` < 1 ustaw 1,
- jeśli `limit` > 10 ustaw 10,
- zwraca nowy słownik.

Ograniczenia / wskazówki:
- nie mutuj wejściowego `payload`,
- obsłuż brak klucza `limit` (domyślnie 5).

Oczekiwany efekt:
Funkcja daje stabilny, bezpieczny wynik nawet dla nieidealnych danych wejściowych.

### Ćwiczenie 4: Importy i podział kodu
Cel: przećwiczyć podstawowe importy i organizację plików.

Opis:
Utwórz dwa pliki:
- `text_utils.py` z funkcją `normalize(text: str) -> str`,
- `main.py`, który importuje `normalize` i używa jej na 3 przykładach.

Ograniczenia / wskazówki:
- użyj `from text_utils import normalize`,
- w `main.py` dodaj blok `if __name__ == "__main__":`.

Oczekiwany efekt:
Po uruchomieniu `python main.py` widzisz 3 znormalizowane wyniki.

## Ćwiczenia praktyczne

### Ćwiczenie 5: Unikalne tagi do wyszukiwarki
Cel: połączyć `list`, `set`, `dict` i sortowanie.

Opis:
Masz payload:

```python
payload = {
    "query": "  Agent tools  ",
    "tags": ["AI", "tools", "ai", "", " ADK "]
}
```

Napisz funkcję, która zwraca:
- `query` bez spacji,
- `tags` jako unikalną, posortowaną listę lowercase,
- `tag_count` jako liczbę tagów po czyszczeniu.

Ograniczenia / wskazówki:
- zrób to w max 12 liniach kodu (bez pustych linii),
- użyj przynajmniej jednej comprehension.

Oczekiwany efekt:
Stabilny format wejścia gotowy pod kolejne kroki workflow agenta.

### Ćwiczenie 6: Co by było gdyby
Cel: sprawdzić rozumienie kompromisów czytelność vs skrótowość.

Opis:
Przepisz rozwiązanie z ćwiczenia 5 na dwa sposoby:
- wersja "krótka" (maksymalnie zwięzła),
- wersja "czytelna" (bardziej jawna, z krokami pośrednimi).

Ograniczenia / wskazówki:
- porównaj obie wersje w 4-6 zdaniach,
- wskaż, którą wybrał(a)byś do kodu produkcyjnego i dlaczego.

Oczekiwany efekt:
Świadoma decyzja projektowa, a nie tylko działający kod.

## Pytanie sprawdzające

W którym ćwiczeniu najłatwiej przypadkowo zmutować dane wejściowe i jak temu zapobiec?
