# Python foundations for JS developer

## O co chodzi w tym module

Celem modułu jest szybkie i praktyczne wejście w podstawy Pythona z perspektywy osoby, która zna już JavaScript/React.
Skupiamy się na tym, co realnie przyda Ci się przy budowie narzędzi i agentów: składni, kolekcjach, mutowalności, comprehensions i importach.

## Dlaczego ten temat jest ważny w kontekście ADK

W ADK bardzo często przetwarzasz dane wejściowe i wyjściowe narzędzi:
- czyścisz i mapujesz struktury JSON,
- budujesz małe transformacje danych,
- składasz workflow z wielu funkcji.

Jeśli dobrze rozumiesz podstawy Pythona, piszesz krótszy, czytelniejszy i mniej awaryjny kod tooli.

## Build first — krótki przykład kodu na start

```python
from typing import Any


def normalize_request(payload: dict[str, Any]) -> dict[str, Any]:
    # Pobierz listę tagów; jeśli brak, użyj pustej listy
    raw_tags = payload.get("tags", [])

    # Usuń spacje, zamień na lowercase i odfiltruj puste elementy
    tags = [tag.strip().lower() for tag in raw_tags if tag and tag.strip()]

    # Zwróć nowy słownik, bez mutowania oryginału
    return {
        "user_id": str(payload.get("user_id", "anonymous")),
        "query": payload.get("query", "").strip(),
        "tags": tags,
    }


incoming = {
    "user_id": 42,
    "query": "  Szukaj dokumentacji ADK  ",
    "tags": [" Docs ", "ADK", "", "Tools"],
}

print(normalize_request(incoming))
# {'user_id': '42', 'query': 'Szukaj dokumentacji ADK', 'tags': ['docs', 'adk', 'tools']}
```

Co tu jest ważne:
- `dict` i `list` są podstawowymi nośnikami danych wejściowych,
- comprehension daje krótki, czytelny zapis transformacji,
- funkcja zwraca nową strukturę zamiast mutować wejście.

Mini-check: dlaczego `payload.get("tags", [])` jest bezpieczniejsze niż `payload["tags"]`?

## Intuicja

Myśl o Pythonie jak o "języku do szybkiego porządkowania danych".
Masz wejście (często słownik po JSON), kilka prostych reguł, czysty wynik.

Dla developera JS największa zmiana to zwykle:
- mniej nawiasów i znaków specjalnych,
- większy nacisk na czytelność,
- inne domyślne zachowania mutowalności.

Python premiuje prosty kod, który za pół roku odczytasz bez bólu.

Pytanie kontrolne: co jest dla Ciebie bardziej czytelne po pierwszym kontakcie: klasyczna pętla `for` czy list comprehension?

## Wyjaśnienie techniczne

### 1. Składnia i bloki kodu

W Pythonie blok kodu wyznacza wcięcie (najczęściej 4 spacje), a nie `{}`.

```python
if is_valid:
    result = "ok"
else:
    result = "error"
```

To wymusza spójny styl i zmniejsza chaos formatowania.

### 2. Podstawowe kolekcje

- `list`: uporządkowana, mutowalna (`append`, `pop`, modyfikacja elementów)
- `tuple`: uporządkowana, niemutowalna (dobre do stałych rekordów)
- `dict`: mapowanie klucz -> wartość
- `set`: zbiór unikalnych elementów

```python
names = ["Ada", "Bob", "Ada"]
unique_names = set(names)  # {'Ada', 'Bob'}
profile = {"name": "Ada", "role": "developer"}
point = (10, 20)
```

### 3. Mutowalność

Mutowalny obiekt można zmienić "w miejscu" (`list`, `dict`, `set`).
Niemutowalny tworzy nową wartość (`tuple`, `str`, `int`).

```python
a = [1, 2]
b = a
b.append(3)
print(a)  # [1, 2, 3]
```

To częste źródło błędów w kodzie narzędzi.

### 4. Comprehensions

Comprehension to skrót do tworzenia nowych kolekcji na podstawie istniejących.

```python
nums = [1, 2, 3, 4, 5]
even_squares = [n * n for n in nums if n % 2 == 0]
# [4, 16]
```

Są szybkie i czytelne, o ile logika jest prosta.

### 5. Importy

Importuj moduły jawnie i lokalnie logicznie:

```python
import json
from pathlib import Path
```

Dzięki temu łatwiej znaleźć zależności i testować kod.

Mini-zadanie: napisz comprehension, które z listy `['  A', 'b ', '', 'C']` zrobi `['a', 'b', 'c']`.

## Porównanie z JavaScript / innym podejściem

- Bloki: Python używa wcięć, JS używa `{}`.
- Brak `++` i `--`: w Pythonie częściej używasz jawnych operacji (`x += 1`).
- Kolekcje: `dict` jest bardziej centralny niż obiekt w JS do pracy z danymi aplikacyjnymi.
- Comprehensions vs `map/filter`: Pythonowy zapis bywa krótszy, ale przy zbyt złożonej logice lepiej wrócić do zwykłej pętli.
- Importy: oba języki mają moduły, ale Python zwykle trzyma prostszą strukturę bez bundlera.

Perspektywa backendowa: Pythonowe transformacje danych często są bliżej logiki biznesowej niż "manipulacji UI", więc czytelność przepływu danych jest krytyczna.

Pytanie: kiedy w JS użyłbyś `map().filter()`, a w Pythonie lepiej napisać zwykły `for` zamiast comprehension?

## Typowe pułapki

- Używanie mutowalnych wartości domyślnych w funkcji (`def f(items=[])`).
- Zakładanie, że kopiowanie przez przypisanie tworzy nową listę/słownik.
- Zbyt rozbudowane comprehensions, których nikt nie rozumie.
- Mylenie `is` z `==`.
- Nadpisywanie nazw modułów, np. plik `json.py` w projekcie.

Krótki test: co się stanie, jeśli dwa miejsca kodu trzymają referencję do tej samej listy i jedno z nich zrobi `append`?

## Dlaczego tak, a nie inaczej

Ten zestaw tematów jest na start, bo daje największy zwrot w praktyce ADK:
- większość pracy to wejście/wyjście funkcji i transformacje,
- dobre nawyki mutowalności ograniczają "dziwne" bugi,
- importy i struktura plików przygotowują grunt pod większe moduły.

Kompromis: nie wchodzimy jeszcze głęboko w klasy i typowanie zaawansowane.
Zysk: szybciej budujesz działające rzeczy i rozumiesz, co się dzieje w kodzie.

## Kiedy używać, a kiedy nie

Używaj tych technik, gdy:
- piszesz małe i średnie funkcje narzędzi,
- porządkujesz dane z API,
- tworzysz warstwę "przed" i "po" wywołaniu narzędzia.

Nie wystarczą same podstawy, gdy:
- model domeny robi się większy (wtedy klasy/dataclasses),
- wejścia/wyjścia są złożone (wtedy solidne typowanie i walidacja),
- pojawia się dużo I/O (wtedy async).

Mini-scenariusz: masz 4 kolejne transformacje danych. Czy trzymać je w jednej ogromnej funkcji, czy rozbić na mniejsze? Dlaczego?

## Przykład praktyczny w kontekście ADK

Załóżmy, że tool wyszukujący dokumenty dostaje dane od użytkownika i musi oddać uporządkowany payload.

```python
from typing import Any


def prepare_search_input(raw: dict[str, Any]) -> dict[str, Any]:
    query = raw.get("query", "").strip()
    tags = [t.strip().lower() for t in raw.get("tags", []) if t and t.strip()]

    # set usuwa duplikaty, sorted daje stabilny wynik
    normalized_tags = sorted(set(tags))

    return {
        "query": query,
        "tags": normalized_tags,
        "limit": int(raw.get("limit", 5)),
    }
```

To jest dokładnie ten typ kodu, który piszesz przy integracji tooli: mały, przewidywalny, łatwy do przetestowania.

Pytanie praktyczne: jak zabezpieczysz `limit`, żeby wartość ujemna albo ogromna nie psuła działania toola?

## Pytanie sprawdzające

Masz wejście:

```python
payload = {
    "query": "  Python ADK  ",
    "tags": ["AI", " adk", "", "Python", "ai"],
    "limit": "3"
}
```

Napisz funkcję, która zwróci:
- `query` bez nadmiarowych spacji,
- `tags` znormalizowane do lowercase, bez pustych i bez duplikatów,
- `limit` jako `int` ograniczony do zakresu 1-20.

Wyjaśnij krótko, gdzie w tym zadaniu jest ryzyko związane z mutowalnością.
