% --- Carica la Knowledge Base ---
:- set_prolog_flag(encoding, utf8).
:- consult('knowledge_base.pl').

% === GESTIONE GENERI ===

% Estrai i generi dei manga letti (escludendo quelli ancora da leggere)
genere_letto(GenerePulito) :-
    lettura_utente(_, _, Stato, _, Generi),
    Stato \= plan_to_read,
    member(Genere, Generi),
    normalizza_genere(Genere, GenerePulito).

% Rimuove underscore iniziale, se presente
normalizza_genere(Genere, GenerePulito) :-
    atom_chars(Genere, ['_'|Rest]) -> atom_chars(GenerePulito, Rest) ;
    GenerePulito = Genere.

% Calcola la frequenza di ciascun genere
frequenza_generi(Frequenze) :-
    findall(Genere, genere_letto(Genere), ListaGeneri),
    sort(ListaGeneri, GeneriUnici),
    findall(Genere-Conta,
        (member(Genere, GeneriUnici),
         aggregate_all(count, genere_letto(Genere), Conta)),
        Frequenze).

% Ordina i generi per frequenza (decrescente)
generi_ordinati(GeneriOrdinati) :-
    frequenza_generi(Frequenze),
    sort(2, @>=, Frequenze, GeneriOrdinati).

% === RACCOMANDAZIONE MANGA ===

% Raccomanda manga che appartengono ai generi preferiti e non sono già letti
raccomanda(TitoloLeggibile) :-
    generi_ordinati(Generi),
    member(Genere-_, Generi),
    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    member(Genere, GeneriManga),
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% Manga con alto punteggio ma bassa popolarità (non letti)
manga_qualita_nascosto(TitoloLeggibile) :-
    manga(ID, Titolo, _, Mean, _, Pop, _, _),
    number(Mean), Mean >= 8,
    number(Pop), Pop > 300,
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% Suggerisce manga nel plan_to_read con generi simili a quelli già letti
consiglia_plan_to_read(TitoloLeggibile) :-
    lettura_utente(_, Titolo, plan_to_read, _, GeneriPlan),
    findall(G,
        (lettura_utente(_, _, Stato, _, GeneriLetti),
         Stato \= plan_to_read,
         member(G, GeneriLetti)),
        ListaGeneriLetti),
    intersection(GeneriPlan, ListaGeneriLetti, Comune),
    Comune \= [],
    formatta_titolo(Titolo, TitoloLeggibile).

% Manga premiati con generi preferiti
manga_premiato(TitoloLeggibile) :-
    generi_ordinati(Generi),
    member(Genere-_, Generi),
    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    member(Genere, GeneriManga),
    member(award_winning, GeneriManga),
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% Manga con generi completamente mai letti
manga_genere_nuovo(TitoloLeggibile) :-
    % Trova tutti i generi presenti nella top 1000
    findall(Genere, 
        (manga(_, _, Generi, _, _, _, _, _), member(Genere, Generi)),
        TuttiGeneri),
    sort(TuttiGeneri, GeneriTotali),

    % Trova i generi già letti dall'utente
    findall(GenereLetto,
        (lettura_utente(_, _, Stato, _, GeneriLetti),
         Stato \= plan_to_read,
         member(GenereLetto, GeneriLetti)),
        GeneriLetti),
    sort(GeneriLetti, GeneriUtente),

    % Trova i generi mai letti
    subtract(GeneriTotali, GeneriUtente, GeneriMaiLetti),

    % Cerca manga che abbiano SOLO generi mai letti
    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    forall(member(GenereManga, GeneriManga), member(GenereManga, GeneriMaiLetti)),
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% Manga che uniscono generi già letti e generi nuovi
manga_misto_generi_nuovi(TitoloLeggibile) :-
    % Trova generi mai letti
    findall(Genere, 
        (manga(_, _, Generi, _, _, _, _, _), member(Genere, Generi)),
        TuttiGeneri),
    sort(TuttiGeneri, GeneriTotali),
    findall(GenereLetto,
        (lettura_utente(_, _, Stato, _, GeneriLetti),
         Stato \= plan_to_read,
         member(GenereLetto, GeneriLetti)),
        GeneriLetti),
    sort(GeneriLetti, GeneriUtente),
    subtract(GeneriTotali, GeneriUtente, GeneriMaiLetti),

    % Trova manga con almeno un genere letto e almeno uno nuovo
    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    intersection(GeneriManga, GeneriUtente, ComuneLetti),
    intersection(GeneriManga, GeneriMaiLetti, ComuneNuovi),
    ComuneLetti \= [],
    ComuneNuovi \= [],
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% Valuta la compatibilità tra i generi forniti e le preferenze dell'utente
valuta_compatibilita(GeneriForniti) :-
    generi_ordinati(GeneriOrdinati),  % Prende i generi ordinati per frequenza
    length(GeneriOrdinati, TotGeneri),
    Half is TotGeneri // 2,
    Quarter is TotGeneri // 4,

    findall(Punteggio,
        (member(Genere, GeneriForniti),
         nth1(Posizione, GeneriOrdinati, Genere-_),
         ( Posizione =< Half -> Punteggio = 2    % Prima metà
         ; Posizione =< Quarter * 3 -> Punteggio = 1 % Tra 25% e 50%
         ; Punteggio = 0                          % Ultimo quarto
         )
        ),
        ListaPunteggi),

    sum_list(ListaPunteggi, Somma),
    length(GeneriForniti, NGen),
    (NGen =:= 0 -> Media = 0 ; Media is Somma / NGen),

    % Media finale valutata
    ( Media >= 1.5 ->
        writeln('Questo manga è MOLTO compatibile con i tuoi gusti!')
    ; Media >= 0.75 ->
        writeln('Questo manga è ABBASTANZA compatibile con i tuoi gusti.')
    ;
        writeln('Questo manga è POCO compatibile con i tuoi gusti.')
    ).

% === UTILITIES ===

% Rimuove gli underscore dal titolo per leggibilità
formatta_titolo(TitoloRaw, TitoloFormattato) :-
    atom_chars(TitoloRaw, Chars),
    maplist(sostituisci_underscore_spazio, Chars, CharsFormattati),
    atom_chars(TitoloFormattato, CharsFormattati).

sostituisci_underscore_spazio('_', ' ') :- !.
sostituisci_underscore_spazio(Char, Char).

% Stampa una lista di elementi
stampa_lista([]).
stampa_lista([X|Xs]) :- writeln(X), stampa_lista(Xs).

% Estrae i primi N elementi da una lista
primi_n(0, _, []) :- !.
primi_n(_, [], []) :- !.
primi_n(N, [X|Xs], [X|Ys]) :-
    N1 is N - 1,
    primi_n(N1, Xs, Ys).

% Stampa il miglior manga per ciascun genere
stampa_migliori_per_generi([]).
stampa_migliori_per_generi([Genere-_|T]) :-
    (miglior_manga_per_genere(Genere, Titolo) ->
        format('~w: ~w~n', [Genere, Titolo])
    ;
        format('~w: Nessun manga consigliabile~n', [Genere])
    ),
    stampa_migliori_per_generi(T).

% Normalizza input dell'utente (spazi -> underscore)
normalize_input(Originale, Normalizzato) :-
    atom_chars(Originale, Chars),
    maplist(sostituisci_spazio_underscore, Chars, NewChars),
    atom_chars(Normalizzato, NewChars).

sostituisci_spazio_underscore(' ', '_') :- !.
sostituisci_spazio_underscore(C, C).

% === MENU INTERATTIVO ===

menu :-
    writeln(''),
    writeln('=== SISTEMA RACCOMANDAZIONE MANGA ==='),
    writeln('1. Mostra generi in ordine di preferenza'),
    writeln('2. Raccomanda 5 manga in base ai tuoi gusti'),
    writeln('3. Raccomanda 5 manga di qualità poco popolari'),
    writeln('4. Consiglia 5 manga dal plan_to_read'),
    writeln('5. Consiglia 5 manga premiati'),
    writeln('6. Consiglia 5 manga con un genere mai letto'),
    writeln('7. Consiglia 5 manga che mischiano generi preferiti e generi mai letti'),
    writeln('8. Compatibilità manga'),
    writeln('9. Esci'),
    write('Scelta (1-8): '),
    read(Scelta),
    esegui_scelta(Scelta).

% --- Gestione delle scelte ---

esegui_scelta(1) :-
    writeln('--- Generi preferiti (ordinati) ---'),
    generi_ordinati(Generi),
    stampa_lista(Generi), nl,
    menu.

esegui_scelta(2) :-
    writeln('--- Manga consigliati in base ai tuoi gusti ---'),
    findall(Titolo, raccomanda(Titolo), Lista),
    primi_n(5, Lista, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(3) :-
    writeln('--- Manga di qualità poco popolari ---'),
    findall(Titolo, manga_qualita_nascosto(Titolo), Lista),
    primi_n(5, Lista, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(4) :-
    writeln('--- Consigliati tra i PLAN_TO_READ ---'),
    findall(Titolo, consiglia_plan_to_read(Titolo), Lista),
    primi_n(5, Lista, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(5) :-
    writeln('--- Manga premiati nei tuoi generi preferiti ---'),
    findall(Titolo, manga_premiato(Titolo), Lista),
    primi_n(5, Lista, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(6) :-
    writeln('--- Manga di un genere mai letto ---'),
    findall(Titolo, manga_genere_nuovo(Titolo), Lista),
    primi_n(5, Lista, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(7) :-
    writeln('--- Manga che mischiano generi già letti e generi mai letti ---'),
    findall(Titolo, manga_misto_generi_nuovi(Titolo), Lista),
    primi_n(5, Lista, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(8) :-
    read_line_to_string(user_input, _), % Mangia invio residuo
    writeln('Inserisci i generi separati da virgola (es: action, fantasy, drama):'),
    read_line_to_string(user_input, InputString),
    split_string(InputString, ",", " ", GeneriFornitiStrings),
    maplist(string_lower, GeneriFornitiStrings, GeneriLower),
    maplist(atom_string, GeneriAtoms, GeneriLower),
    maplist(normalize_input, GeneriAtoms, GeneriNormalizzati),
    ( GeneriNormalizzati == [] ->
        writeln('Non hai inserito nessun genere! Per favore riprova.')
    ;
        valuta_compatibilita(GeneriNormalizzati)
    ),
    nl,
    menu.

esegui_scelta(9) :-
    writeln('Uscita. Grazie!').


esegui_scelta(_) :-
    writeln('Scelta non valida. Riprova.'), nl,
    menu.