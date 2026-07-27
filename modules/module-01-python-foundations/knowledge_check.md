# Sprawdzenie wiedzy — Python foundations for JS developer

## Pytania otwarte

1. Własnymi słowami wyjaśnij różnicę między mutacją obiektu a stworzeniem nowej wartości.
2. Dlaczego w kodzie integrującym narzędzie agenta lepiej używać `payload.get("x")` niż `payload["x"]` w wielu miejscach?
3. Kiedy comprehension poprawia kod, a kiedy już go pogarsza?
4. Jakie 2 różnice między Pythonem i JavaScriptem najbardziej wpływają na Twój styl pisania kodu?

## Krótkie scenariusze

1. Dostajesz `tags = ["AI", " ai ", "", "tools"]`. Napisz jedną linię, która da czystą listę lowercase bez pustych.
2. Funkcja modyfikuje przekazaną listę argumentem i "psuje" dane w innym miejscu aplikacji. Jak to szybko zdiagnozować?
3. W payloadzie `limit` przychodzi jako string. Jakie ryzyko niesie bezpośrednie `int(payload["limit"])` bez walidacji?

## Co by było gdyby

1. Co jeśli zamiast `list` na `tags` użyjesz od razu `set` i oddasz go z funkcji? Co zyskujesz, co tracisz?
2. Co jeśli wszystkie transformacje wrzucisz do jednej wielkiej comprehension? Jakie skutki dla czytelności i debugowania?
3. Co jeśli w kilku miejscach kodu kopiujesz słownik przez zwykłe przypisanie? Jakie to może dać trudne do wykrycia błędy?

## Typowe błędy do rozpoznania

1. `def add_tag(tag, tags=[]): ...`.
   Co jest błędem i jak poprawić?
2. `if value is "ok": ...`.
   Dlaczego to jest ryzykowne i co powinno być zamiast tego?
3. `clean = raw_tags` i później `clean.append(...)`.
   Czemu to może mutować dane wejściowe?

## Samoocena
- Co umiem dobrze
- Co jeszcze jest niejasne
- Co chcę doprecyzować

## Mini zadanie aktywne

Napisz krótką odpowiedź (5-8 zdań):
- jakie 3 zasady z modułu wdrożysz od razu w swoim kodzie,
- jaki błąd z listy pułapek jest dla Ciebie najbardziej prawdopodobny,
- jak go unikniesz w praktyce.
