# Wytyczne UI platformy

## Charakter interfejsu

Platforma ma być narzędziem do nauki, nie stroną marketingową.
Pierwszy ekran powinien od razu pokazywać miejsce pracy:
- listę modułów,
- aktualny moduł,
- postęp,
- szybki powrót do ostatniego ćwiczenia.

Nie twórz landing page.
Nie dodawaj sekcji promocyjnych.

## Priorytety

Najważniejsze są:
- czytelność materiału,
- łatwe przełączanie części modułu,
- skupienie podczas ćwiczeń,
- jasny status postępu,
- brak przypadkowego ujawniania zbyt wielu podpowiedzi.

## Widoki MVP

### Dashboard

Powinien pokazywać:
- moduły,
- status każdego modułu,
- ostatnio otwierany moduł,
- ogólny postęp.

### Widok modułu

Powinien zawierać:
- tytuł modułu,
- nawigację po częściach,
- obszar treści,
- akcję oznaczenia części jako ukończonej,
- notatki modułu.

### Tryb ćwiczeń

Powinien zawierać:
- jedno ćwiczenie na ekranie,
- cel,
- opis,
- ograniczenia lub wskazówki jako sekcję możliwą do zwinięcia,
- pole odpowiedzi,
- status odpowiedzi,
- nawigację poprzednie/następne.

Oczekiwany efekt nie powinien być pokazany tak, żeby zastępował samodzielną próbę.

### Tryb sprawdzenia wiedzy

Powinien zawierać:
- jedno pytanie lub scenariusz,
- pole odpowiedzi,
- możliwość zapisania odpowiedzi,
- status pytania.

## Styl

Interfejs powinien być:
- spokojny,
- użytkowy,
- czytelny na laptopie,
- bez dekoracyjnego nadmiaru.

To jest aplikacja robocza.
Karty są dopuszczalne dla pojedynczych ćwiczeń lub modułów, ale nie należy budować całej strony z zagnieżdżonych kart.

## Dostępność i ergonomia

W MVP warto zadbać o:
- czytelny kontrast,
- wygodną szerokość tekstu,
- zachowanie stanu przy odświeżeniu,
- brak przesunięć layoutu po zapisaniu odpowiedzi,
- pola tekstowe wystarczająco duże dla kodu i krótkich wyjaśnień.

## Komponenty

Preferowane komponenty:
- zakładki dla części modułu,
- przyciski ikonowe dla prostych akcji,
- checkboxy lub przełączniki dla statusów,
- textarea dla odpowiedzi i notatek,
- pasek postępu dla modułu,
- zwijane sekcje dla wskazówek i oczekiwanego efektu.
