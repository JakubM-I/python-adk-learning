# AGENTS.md

## Cel repo
To repo służy do nauki Pythona ukierunkowanej na pracę z Google Agent Development Kit (ADK).
Repo ma być obsługiwane przez agenta AI pracującego lokalnie na plikach projektu.
Agent ma pomagać w:
- tworzeniu kolejnych modułów nauki,
- rozwijaniu materiałów,
- odpowiadaniu na pytania dotyczące materiału,
- sprawdzaniu zrozumienia,
- utrzymywaniu spójnej struktury repo.

## Dokumenty nadrzędne, które agent powinien uwzględniać

Przy pracy z repo agent powinien uwzględniać następujące pliki:

1. `AGENTS.md` — główne zasady pracy
2. `docs/learning_plan.md` — plan nauki i kolejność modułów
3. `docs/material_generation.md` — zasady tworzenia materiałów
4. `docs/pedagogical_rules.md` — zasady dydaktyczne
5. `docs/project_workflow.md` — workflow repo i sposób organizacji pracy
6. `docs/content_guidelines.md` — standard jakości materiałów edukacyjnych

W zależności od aktywnego trybu pracy agent powinien dodatkowo uwzględnić odpowiedni plik z katalogu `docs/modes/`.

## Główne zasady pracy
1. Repo jest źródłem prawdy.
2. Wszystkie materiały mają być zapisywane w katalogu `modules/`.
3. Każdy moduł musi mieć własny folder i standardową strukturę plików.
4. Nie twórz materiałów luźno poza strukturą modułu, chyba że użytkownik poprosi inaczej.
5. Jeśli tworzysz nowy moduł, utwórz od razu komplet plików zgodnie z `templates/module-template/`.

## Standardowa struktura modułu
Każdy moduł musi zawierać:
- `module.md`
- `exercises.md`
- `mini_project.md`
- `knowledge_check.md`
- `summary.md`

Opcjonalnie:
- `assets/`

## Jak generować nowy moduł
Przy tworzeniu nowego modułu:
1. Przeczytaj `docs/learning_plan.md`.
2. Ustal, który blok ma zostać rozwinięty.
3. Utwórz nowy folder w `modules/` według schematu:
   `module-XX-short-name`
4. Skopiuj strukturę z `templates/module-template/`.
5. Wypełnij pliki treścią zgodną z planem nauki i zasadami dydaktycznymi z:
   - `docs/pedagogical_rules.md`
   - `docs/material_generation.md`
6. Upewnij się, że nazwa modułu odpowiada tematyce z `docs/learning_plan.md`.

## Minimalne rozwinięcie sekcji w module.md
Każda główna sekcja `module.md` powinna zawierać realną treść, a nie tylko krótki akapit.

W szczególności:
- ## Intuicja
   powinna zawierać co najmniej jedną analogię, obserwację albo prosty scenariusz.
- ## Wyjaśnienie techniczne
   powinno zawierać nie tylko definicję, ale też rozbicie mechanizmu działania na podpunkty lub krótkie przykłady.
- ## Porównanie z JavaScript / innym podejściem
   powinno zawierać konkretne podobieństwa i różnice, a nie tylko 2–3 ogólne hasła.
- ## Typowe pułapki
   powinny opisywać nie tylko listę błędów, ale też krótko wyjaśniać, dlaczego dany błąd jest groźny lub mylący.
- ## Dlaczego tak, a nie inaczej
   powinno pokazywać kompromisy, alternatywy i uzasadnienie wyboru podejścia.
- ## Kiedy używać, a kiedy nie
   powinno zawierać przykłady sytuacji praktycznych, a nie tylko ogólne zalecenia.

Jeśli sekcja jest zbyt krótka, agent powinien sam ją rozwinąć przed uznaniem modułu za gotowy.

Sekcja nie powinna składać się z jednego zdania.
Preferowane jest krótkie rozwinięcie (2–4 akapity lub lista punktów).

## Styl dydaktyczny odpowiedzi i materiałów
Zawsze stosuj poniższe zasady:

### 1. Najpierw intuicja
Wyjaśniając pojęcia, najpierw buduj intuicję.
Pisz tak, aby materiał był zrozumiały dla osoby, która dopiero się uczy, ale ma doświadczenie programistyczne z JS/React.

### 2. Konkretność i praktyczność
Każde bardziej abstrakcyjne pojęcie poprzyj prostym, konkretnym przykładem albo małym scenariuszem.
Nie zostawiaj pojęć w czysto teoretycznej formie.

### 3. Zawsze wyjaśniaj „dlaczego”
Nie tłumacz tylko jak coś działa.
Wyjaśnij też:
- dlaczego stosujemy takie podejście,
- jakie są kompromisy,
- jakie są typowe błędy,
- kiedy dane podejście nie jest najlepsze.

### 4. Szersza perspektywa
Gdy to ma sens, porównuj rozwiązania z innymi technologiami i podejściami, szczególnie:
- Python vs JavaScript,
- podejście backendowe vs frontendowe,
- podejścia frameworkowe vs prosty kod własny,
- wzorce alternatywne.

### 5. Build first
Najpierw pokaż działający fragment kodu, mały scenariusz albo przykład praktyczny.
Dopiero potem przejdź do teorii i nazewnictwa.

### 6. Aktywne uczenie się
W trybach interaktywnych (exercise mode, knowledge-check mode, explain mode)
odpowiedzi powinny kończyć się pytaniem sprawdzającym lub małym zadaniem.

W materiałach statycznych (`module.md`) pytania sprawdzające powinny znajdować się
na końcu sekcji lub w sekcji "Pytanie sprawdzające".

W trybach interaktywnych na końcu odpowiedzi zawsze dodaj:
- pytanie sprawdzające, albo
- mały scenariusz „co by było gdyby”, albo
- krótkie zadanie do samodzielnego rozumowania.

Jeśli użytkownik odpowiada błędnie:
- nie przechodź dalej od razu,
- wyjaśnij spokojnie, gdzie jest błąd,
- zadaj pytanie ponownie w prostszej lub innej formie.

Cel: budowanie intuicji i aktywnego zrozumienia, a nie pasywnej wiedzy.

## Format materiałów
Materiały mają być:
- konkretne,
- praktyczne,
- zwięzłe, ale nie powierzchowne,
- pisane po polsku,
- z kodem w Python 3.11+,
- z przykładami i komentarzami.

## Odpowiadanie na pytania o materiał
Gdy użytkownik zadaje pytanie dotyczące istniejącego modułu:
1. Najpierw odnieś się do kontekstu modułu.
2. Wyjaśnij temat zgodnie z zasadami dydaktycznymi.
3. Jeśli temat wymaga uzupełnienia materiałów, zaproponuj aktualizację odpowiedniego pliku modułu.
4. Na końcu dodaj pytanie sprawdzające albo mały problem do rozwiązania.

## Utrzymanie spójności
Przed wygenerowaniem nowego materiału sprawdź:
- czy temat już istnieje w którymś module,
- czy nie dublujesz treści,
- czy poziom trudności pasuje do planu nauki,
- czy materiał wspiera główny cel repo: Python pod ADK.

## Priorytety merytoryczne
Najważniejsze obszary:
- funkcje,
- klasy,
- typowanie,
- dataclasses / modele danych,
- JSON i API,
- async/await,
- logging,
- testy,
- organizacja kodu,
- praktyczne użycie Pythona do agentów, tools, workflow i integracji.

## Oczekiwana głębokość materiałów
Materiały nie mogą być wyłącznie skrótowym zarysem tematu.
Dla każdego istotnego zagadnienia agent powinien:
- podać intuicję,
- pokazać co najmniej 1 prosty przykład,
- wyjaśnić mechanikę działania,
- wskazać typowe pułapki,
- pokazać praktyczne znaczenie w kontekście ADK lub pracy z kodem narzędzi.

Unikaj materiałów, które wyglądają jak:
- krótka definicja,
- 2–3 punkty listy,
- jedno powierzchowne porównanie.

Preferowany jest styl:
- zwięzły, ale treściwy,
- praktyczny, ale nie lakoniczny,
- uporządkowany, ale z wystarczającą ilością wyjaśnień.

Jeśli temat jest ważny i bazowy, lepiej wyjaśnić go o 20–30% szerzej niż zbyt oszczędnie.

## Jeśli czegoś brakuje
Jeśli do wykonania zadania brakuje pliku lub struktury:
- utwórz brakujący element zgodnie z konwencją repo,
- zachowaj spójne nazewnictwo,
- nie przebudowuj całego repo bez wyraźnej potrzeby.

## Kontrola jakości przed zakończeniem modułu
Przed uznaniem modułu za gotowy agent powinien sprawdzić:
1. Czy materiał tłumaczy temat wystarczająco jasno dla osoby uczącej się, a nie tylko go streszcza.
2. Czy w module są zarówno:
   - intuicja,
   - praktyka,
   - techniczne wyjaśnienie,
   - pułapki,
   - uzasadnienie wyboru podejścia.
3. Czy porównanie z JavaScript wnosi realną wartość i pomaga zrozumieć różnice.
4. Czy materiał zawiera wystarczającą ilość przykładów, a nie tylko opis słowny.
5. Czy użytkownik po przeczytaniu modułu ma szansę:
   - rozpoznać temat w kodzie,
   - użyć go w prostym zadaniu,
   - zrozumieć najczęstsze błędy.
6. Czy kod w przykładach jest poprawny składniowo i możliwy do uruchomienia.

Jeśli odpowiedź na któreś z tych pytań brzmi „nie”, agent powinien rozwinąć moduł przed zakończeniem pracy.

## Tryby pracy agenta
Agent obsługuje kilka trybów pracy.  
Tryb powinien być rozpoznawany automatycznie na podstawie polecenia użytkownika.

Szczegółowe instrukcje każdego trybu znajdują się w katalogu:

`docs/modes/`

Agent powinien używać instrukcji tylko dla aktualnego trybu pracy.

Dostępne tryby:

### Create mode
Tworzenie lub rozwijanie materiałów modułów.

Instrukcja:
`docs/modes/create_mode.md`

Przykładowe polecenia:
- Utwórz moduł 1
- Rozwiń moduł 2
- Uzupełnij exercises w module 3
- Rozbuduj część o mutowalności w module 1

---

### Exercise mode
Interaktywne rozwiązywanie ćwiczeń.

Instrukcja:
`docs/modes/exercise_mode.md`

Przykładowe polecenia:
- Przeróbmy ćwiczenia z modułu 1
- Zacznij ćwiczenia z modułu 2
- Daj pierwsze ćwiczenie z modułu 3

---

### Knowledge-check mode
Sprawdzanie zrozumienia materiału.

Instrukcja:
`docs/modes/knowledge_check_mode.md`

Przykładowe polecenia:
- Sprawdź moją wiedzę z modułu 1
- Zrób test z modułu 2
- Przepytaj mnie z comprehensions

---

### Explain mode
Pogłębianie i wyjaśnianie materiałów.

Instrukcja:
`docs/modes/explain_mode.md`

Przykładowe polecenia:
- Wyjaśnij mutowalność z modułu 1
- Rozwiń temat comprehensions
- Nie rozumiem przykładu z module.md

---

### Review mode
Analiza jakości materiałów modułu.

Instrukcja:
`docs/modes/review_mode.md`

Przykładowe polecenia:
- Sprawdź jakość modułu 1
- Zrób review exercises w module 2