# Mini projekt — Python foundations for JS developer

## Cel projektu

Zbudować mały "Input Preprocessor" do narzędzia agenta, który:
- czyści dane wejściowe użytkownika,
- normalizuje strukturę,
- zwraca przewidywalny format gotowy do dalszego workflow.

## Kontekst praktyczny

W realnym ADK tool dostaje dane z promptu, UI lub API.
Te dane często są niepełne, niespójne albo mają zły typ.
Ten mini-projekt symuluje pierwszy krok pipeline'u: "brudne wejście" -> "czyste wejście".

## Wymagania

Napisz funkcję:

```python
def preprocess_tool_input(payload: dict) -> dict:
    ...
```

Wynik ma zawierać pola:
- `user_id`: zawsze jako `str`, domyślnie `"anonymous"`,
- `query`: przycięte spacje, minimalna długość 3 znaki,
- `tags`: lista lowercase, bez pustych, bez duplikatów, posortowana,
- `limit`: `int` w zakresie 1-20 (domyślnie 5),
- `metadata`: słownik z `source` (domyślnie `"unknown"`).

## Kroki realizacji

1. Zdefiniuj 2-3 przykładowe payloady testowe (poprawne i błędne).
2. Zaimplementuj funkcję krok po kroku (najpierw `query`, potem `tags`, potem `limit`).
3. Upewnij się, że nie mutujesz wejściowego `payload`.
4. Dodaj prosty blok uruchomieniowy (`if __name__ == "__main__":`) i wydrukuj wynik dla każdego payloadu.
5. Dla jednego przypadku dodaj krótki komentarz: "co by się zepsuło bez normalizacji".

## Rozszerzenia opcjonalne

- Dodaj pole `warnings` z listą ostrzeżeń (np. "limit obcięty do 20").
- Rozbij kod na małe funkcje pomocnicze (`normalize_tags`, `normalize_limit`).
- Dodaj type hints do wszystkich funkcji.

## Kryteria ukończenia

- Funkcja zwraca spójny format niezależnie od jakości wejścia.
- Kod jest czytelny i łatwy do testowania.
- Wykorzystujesz elementy z modułu: `dict`, `list`, `set`, mutowalność, importy.
- Potrafisz wyjaśnić, które decyzje poprawiają bezpieczeństwo i przewidywalność toola.

## Pytanie sprawdzające

Którą część projektu najłatwiej "przekombinować" i jak uprościć ją bez utraty jakości?
