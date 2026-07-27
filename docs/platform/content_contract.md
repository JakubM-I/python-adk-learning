# Kontrakt treści dla platformy

## Cel

Ten dokument opisuje, jak materiały Markdown powinny być interpretowane przez platformę.
Nie zastępuje zasad tworzenia modułów.
Jest dodatkową warstwą, która pozwala aplikacji czytać moduły w przewidywalny sposób.

## Zasada główna

Pliki w `modules/` pozostają czytelne dla człowieka.
Kontrakt platformy nie powinien wymuszać ciężkiego formatu, który utrudni pisanie materiałów.

Jeśli platforma potrzebuje metadanych, należy dodawać je lekko i konsekwentnie.

## Identyfikacja modułu

Moduł jest wykrywany po folderze:

```text
modules/module-XX-short-name/
```

Wymagane pliki:
- `module.md`,
- `exercises.md`,
- `mini_project.md`,
- `knowledge_check.md`,
- `summary.md`.

Tytuł modułu powinien pochodzić z pierwszego nagłówka `#` w `module.md`.

## Części modułu

Platforma powinna mapować pliki na części:

```text
module.md          -> material
exercises.md       -> exercises
mini_project.md    -> mini_project
knowledge_check.md -> knowledge_check
summary.md         -> summary
```

Nazwy plików pozostają zgodne z obecnym standardem repo.

## Ćwiczenia

Ćwiczenie powinno zaczynać się od nagłówka:

```markdown
### Ćwiczenie 1: Tytuł ćwiczenia
```

Zalecane sekcje w ćwiczeniu:
- `Cel:`,
- `Opis:`,
- `Ograniczenia / wskazówki:`,
- `Oczekiwany efekt:`.

Platforma może używać tych sekcji do podziału widoku.
Przykładowo:
- cel i opis są widoczne od razu,
- wskazówki mogą być zwinięte,
- oczekiwany efekt może być ukryty do momentu próby użytkownika.

## Poziom ćwiczenia

Poziom może wynikać z najbliższego nagłówka `##`:

```markdown
## Ćwiczenia rozgrzewkowe
## Ćwiczenia średnie
## Ćwiczenia praktyczne
```

Platforma może mapować je na:
- `warmup`,
- `medium`,
- `practical`.

## Knowledge check

Pytania w `knowledge_check.md` mogą być parsowane według sekcji:
- `Pytania otwarte`,
- `Krótkie scenariusze`,
- `Co by było gdyby`,
- `Typowe błędy do rozpoznania`,
- `Mini zadanie aktywne`.

W MVP wystarczy wyświetlanie sekcji Markdown.
W kolejnym etapie można rozbijać pytania numerowane na pojedyncze karty.

## Notatki i odpowiedzi użytkownika

Notatki, odpowiedzi i postęp nie należą do plików modułu.
Powinny być zapisywane w `platform/data/`.

To rozdzielenie jest ważne:
- materiały pozostają czyste,
- odpowiedzi użytkownika można łatwo resetować,
- agent może aktualizować moduł bez ryzyka nadpisania pracy użytkownika.

## Metadane w przyszłości

Jeśli parser nagłówków okaże się zbyt kruchy, można dodać opcjonalny plik:

```text
modules/<module>/module.json
```

Przykład:

```json
{
  "id": "module-01-python-foundations",
  "title": "Python foundations for JS developer",
  "order": 1,
  "status": "ready",
  "estimated_time_minutes": 60
}
```

Nie należy dodawać tego pliku przedwcześnie.
Najpierw trzeba sprawdzić, czy obecna struktura Markdown wystarczy dla MVP.

## Reguły dla przyszłych modułów

Przy tworzeniu kolejnych modułów agent powinien:
- zachować wymagany zestaw pięciu plików,
- stosować stabilne nagłówki ćwiczeń,
- numerować ćwiczenia kolejno,
- nie umieszczać pełnych rozwiązań bezpośrednio w treści ćwiczenia,
- oddzielać wskazówki od oczekiwanego efektu,
- pisać pytania knowledge check tak, żeby dało się je zadawać pojedynczo.
