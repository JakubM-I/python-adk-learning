# Workflow repo

## Typowe zadania dla agenta AI

### 1. Utworzenie nowego modułu
- sprawdź plan,
- utwórz folder modułu,
- dodaj komplet plików,
- wypełnij pliki treścią.

### 2. Rozwinięcie istniejącego modułu
- przeczytaj aktualne pliki modułu,
- nie duplikuj treści,
- rozbuduj tylko tam, gdzie potrzeba.

### 3. Odpowiedź na pytanie użytkownika
- odnieś się do istniejącego materiału,
- odpowiedz zgodnie z zasadami dydaktycznymi,
- dodaj pytanie sprawdzające.

### 4. Aktualizacja planu
- jeśli użytkownik zmienia priorytety nauki, zaktualizuj `docs/learning_plan.md`.

## Nazewnictwo modułów
Używaj schematu:
`module-XX-short-name`

Przykłady:
- `module-01-python-foundations`
- `module-02-functions-and-tools`
- `module-03-classes-and-models`

## Zasady spójności
- jeden moduł = jeden blok tematyczny,
- nie mieszaj kilku dużych bloków w jednym module,
- zawsze zachowuj ten sam zestaw plików.

## Praca z materiałami modułów
Repo służy nie tylko do przechowywania materiałów, ale również do prowadzenia procesu nauki.
Agent AI powinien umożliwiać interaktywną pracę z materiałami modułów.

## Tworzenie modułu
Użytkownik może polecić:
- Utwórz moduł 1
- Wygeneruj moduł 2
- Rozwiń moduł 3

Agent generuje materiały w katalogu `modules/`.

## Rozwiązywanie ćwiczeń
Polecenia użytkownika:
- Przeróbmy ćwiczenia z modułu 1
- Zacznij ćwiczenia z modułu 2

Agent:
1. czyta `exercises.md`
2. podaje jedno ćwiczenie
3. czeka na rozwiązanie
4. ocenia odpowiedź
5. przechodzi dalej dopiero po ocenie.

## Sprawdzanie wiedzy
Polecenia użytkownika:
- Sprawdź moją wiedzę z modułu 1
- Zrób test z modułu 2

Agent:
1. czyta `knowledge_check.md`
2. zadaje jedno pytanie
3. czeka na odpowiedź
4. ocenia odpowiedź
5. kontynuuje dopiero po wyjaśnieniu błędów.

## Wyjaśnianie materiału
Polecenia użytkownika:
- Wyjaśnij fragment modułu
- Rozwiń temat
- Podaj więcej przykładów

Agent:
1. odnosi się do materiałów modułu
2. stosuje zasady z `docs/pedagogical_rules.md`
3. kończy odpowiedź pytaniem sprawdzającym.
