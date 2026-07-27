# Plan nauki Pythona pod Google ADK

## Założenia
- Nauka przez pryzmat praktycznego użycia Pythona do Agent Development Kit.
- Użytkownik nie jest początkujący w programowaniu: ma doświadczenie w JS/React.
- Materiały mają pomijać przesadnie podstawowe wprowadzenia i skupiać się na różnicach JS -> Python, idiomach oraz praktyce.
- Preferowane tempo: około 1 godzina dziennie, 5 dni w tygodniu.

## Główne bloki
### Moduł 1 — Python foundations for JS developer
Cel:
- wejść w składnię Pythona,
- zrozumieć podstawowe struktury danych,
- oswoić różnice względem JS.

Zakres:
- składnia,
- mutowalność,
- list, tuple, dict, set,
- comprehensions,
- importy.

### Moduł 2 — Funkcje i tools mindset
Cel:
- nauczyć się pisać funkcje tak, jak później buduje się narzędzia dla agentów.

Zakres:
- def,
- argumenty,
- wartości domyślne,
- *args i **kwargs,
- docstringi,
- dekoratory,
- funkcje jako obiekty.

### Moduł 3 — Klasy, obiekty i modele
Cel:
- rozumieć klasy, bo agent, tool i stan często są modelowane obiektowo.

Zakres:
- klasy,
- self,
- __init__,
- dziedziczenie,
- metody klasowe i statyczne,
- magic methods,
- dataclasses.

### Moduł 4 — Typowanie, modele danych i API
Cel:
- umieć tworzyć typowane wejścia/wyjścia, parsować dane i pracować z API.

Zakres:
- type hints,
- Optional, Union, Literal,
- TypedDict,
- dataclasses lub pydantic,
- JSON,
- requests / httpx,
- obsługa błędów.

### Moduł 5 — Async i logging
Cel:
- zrozumieć I/O, równoległość i diagnostykę kodu.

Zakres:
- async/await,
- asyncio,
- gather,
- logowanie,
- debugowanie,
- typowe pułapki async.

### Moduł 6 — Wprowadzenie do ADK
Cel:
- zbudować pierwszego działającego agenta.

Zakres:
- struktura prostego agenta,
- tool registry,
- context,
- memory,
- prompting,
- pętla wykonania.

### Moduł 7 — Workflow i orkiestracja
Cel:
- budować agentów wieloetapowych.

Zakres:
- przekazywanie stanu,
- przepływ wielokrokowy,
- multi-tool,
- memory updates,
- bardziej złożone scenariusze.

### Moduł 8 — Testy, produkcja i projekt końcowy
Cel:
- domknąć proces od nauki do użycia praktycznego.

Zakres:
- pytest,
- mockowanie,
- testowanie narzędzi,
- organizacja projektu,
- wdrożenie lokalne lub jako API,
- projekt końcowy.

## Zasada progresji
Każdy kolejny moduł:
- korzysta z poprzedniego,
- nie powinien zbyt wcześnie wchodzić w zaawansowaną abstrakcję,
- ma kończyć się sprawdzeniem zrozumienia,
- ma zawierać element praktyczny i mini-projekt.

## Forma materiałów modułu
Każdy moduł musi zawierać:
- materiał główny,
- ćwiczenia,
- mini projekt,
- sprawdzenie wiedzy,
- podsumowanie.