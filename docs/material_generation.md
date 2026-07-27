# Instrukcje tworzenia materiałów modułów

## Cel
Ten dokument opisuje, jak agent AI ma tworzyć kolejne moduły nauki.

## Ogólna zasada
Materiały mają być tworzone modułami i zapisywane do osobnych folderów w `modules/`.

## Co musi powstać dla każdego modułu
1. `module.md`
2. `exercises.md`
3. `mini_project.md`
4. `knowledge_check.md`
5. `summary.md`

## Obowiązkowa struktura `module.md`
Każdy materiał główny modułu musi zawierać następujące nagłówki:
1. `O co chodzi w tym module`
2. `Dlaczego ten temat jest ważny w kontekście ADK`
3. `Build first — krótki przykład kodu na start`
4. `Intuicja`
5. `Wyjaśnienie techniczne`
6. `Porównanie z JavaScript / innym podejściem`
7. `Typowe pułapki`
8. `Dlaczego tak, a nie inaczej`
9. `Kiedy używać, a kiedy nie`
10. `Przykład praktyczny w kontekście ADK`
11. `Pytanie sprawdzające`

To jest domyślny szablon materiału. Agent ma go traktować jako wymagany standard.

## Jak pisać `exercises.md`
Ćwiczenia powinny być warstwowe:
- łatwe rozgrzewkowe,
- średnie,
- 1–2 bardziej praktyczne.

Każde ćwiczenie powinno zawierać:
- cel,
- krótki opis,
- ograniczenia lub wskazówki,
- oczekiwany efekt.

## Jak pisać `mini_project.md`
Mini-projekt ma:
- scalać pojęcia z modułu,
- być praktyczny,
- być możliwy do wykonania w małej skali,
- mieć związek z agentami, narzędziami, integracją lub workflow.

## Jak pisać `knowledge_check.md`
To nie ma być tylko test ABC.
Powinny tu być:
- pytania otwarte,
- krótkie scenariusze,
- „co by było gdyby”,
- sprawdzanie rozumienia kompromisów.

## Jak pisać `summary.md`
Powinno zawierać:
- najważniejsze pojęcia,
- checklistę umiejętności,
- rzeczy do powtórki,
- typowe błędy,
- połączenie z kolejnym modułem.

## Styl materiałów
- po polsku,
- konkretnie,
- bez lania wody,
- z naciskiem na praktykę,
- z budowaniem intuicji,
- z porównaniami do JS tam, gdzie pomaga to zrozumieniu.

## Build first
Jeśli tylko temat na to pozwala:
- zacznij od małego działającego kodu,
- dopiero potem nazwij i opisz pojęcie.

## Zasada aktywnego uczenia
Każdy większy fragment materiału powinien kończyć się:
- pytaniem sprawdzającym, albo
- małym zadaniem myślowym.