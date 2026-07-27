# Create Mode

## Cel trybu

Create mode służy do tworzenia lub rozwijania materiałów modułów nauki.

Agent generuje lub aktualizuje pliki w katalogu:

modules/


## Źródła kontekstu

Podczas pracy w tym trybie agent powinien uwzględnić:

- docs/learning_plan.md
- docs/material_generation.md
- docs/pedagogical_rules.md
- docs/project_workflow.md
- AGENTS.md


## Co agent może robić w tym trybie

- tworzyć nowe moduły
- rozwijać istniejące materiały
- poprawiać strukturę modułu
- uzupełniać przykłady
- rozbudowywać sekcje które są zbyt skrótowe


## Tworzenie nowego modułu

Agent powinien:

1. sprawdzić plan nauki w `docs/learning_plan.md`
2. utworzyć katalog w `modules/`
3. zastosować template z `templates/module-template/`
4. wygenerować pliki:

- module.md
- exercises.md
- mini_project.md
- knowledge_check.md
- summary.md


## Zasada build-first

Materiały powinny zaczynać się od przykładu kodu, a dopiero potem przechodzić do teorii.

Preferowany schemat:

kod  
↓  
intuicja  
↓  
wyjaśnienie techniczne  
↓  
pułapki  
↓  
kontekst ADK


## Kontrola jakości

Przed zakończeniem pracy agent powinien sprawdzić:

- czy każda sekcja ma realną treść
- czy są przykłady kodu
- czy materiał nie jest zbyt skrótowy
- czy pojawia się kontekst ADK