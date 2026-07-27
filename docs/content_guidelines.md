# Content Guidelines

Ten dokument definiuje standard jakości materiałów edukacyjnych generowanych w repo.

Dotyczy przede wszystkim:
- `modules/*/module.md`
- `modules/*/exercises.md`
- `modules/*/mini_project.md`
- `modules/*/knowledge_check.md`

Agent powinien stosować te zasady przy tworzeniu i rozwijaniu materiałów.


# Ogólne zasady

Materiały mają być:

- praktyczne
- konkretne
- zrozumiałe dla osoby uczącej się
- technicznie poprawne
- zorientowane na zastosowania w ADK

Nie twórz materiałów w stylu akademickiego podręcznika.

Preferowany styl:

- wyjaśnienie
- przykład
- zastosowanie


# Preferowana struktura wyjaśnienia

Dla każdego ważnego pojęcia stosuj schemat:

1. Intuicja  
2. Przykład kodu  
3. Wyjaśnienie mechanizmu  
4. Typowe błędy  
5. Zastosowanie praktyczne

Nie zaczynaj od abstrakcyjnej definicji.


# Zasada build-first

Gdy to możliwe, materiał powinien zaczynać się od:

- krótkiego fragmentu kodu
- prostego scenariusza
- małego problemu

Dopiero potem pojawia się wyjaśnienie.


# Styl przykładów kodu

Kod powinien być:

- prosty
- czytelny
- realistyczny
- możliwy do uruchomienia

Preferowane są przykłady związane z:

- przetwarzaniem danych
- JSON
- API
- transformacją struktur danych
- małymi funkcjami narzędzi

Unikaj sztucznych przykładów typu:
```python
class Animal:
    pass

class Dog(Animal):
    pass

class Cat(Animal):
    pass
```

Jeśli to możliwe, pokazuj przykłady bliższe pracy z narzędziami i agentami.


# Porównania z JavaScript

Ponieważ użytkownik zna JavaScript/React:

- warto pokazywać różnice Python vs JS
- warto pokazywać analogie
- warto wskazywać miejsca, gdzie intuicja JS może być myląca

Nie należy jednak zamieniać materiałów w kurs porównawczy.

Porównania mają wspierać zrozumienie.


# Typowe pułapki

Dla każdego ważniejszego tematu postaraj się pokazać:

- najczęstsze błędy
- pułapki składniowe
- pułapki mutowalności
- błędne założenia przeniesione z JS


# Zastosowanie w ADK

Jeśli temat ma zastosowanie w pracy z agentami lub narzędziami, pokaż to.

Przykłady:

- transformacja payloadu
- normalizacja danych wejściowych
- przygotowanie inputu do toola
- walidacja danych
- przetwarzanie odpowiedzi z API


# Głębokość materiału

Materiały nie powinny być zbyt skrótowe.

Każdy ważny temat powinien zawierać:

- wyjaśnienie intuicyjne
- przykład
- wyjaśnienie techniczne
- pułapki

Unikaj materiałów składających się tylko z listy punktów.


# Czytelność

Preferuj:

- krótkie akapity
- listy punktów
- czytelne przykłady kodu
- jasne nagłówki

Unikaj:

- bardzo długich bloków tekstu
- zbyt akademickiego stylu
- nadmiaru teorii bez przykładów