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

% manga_qualita_nascosto/1
% Trova manga non letti con voto medio >= 8 e popolarità (valore numerico alto = poco noti) superiore a 1500.
manga_qualita_nascosto(TitoloLeggibile) :-
    manga(ID, Titolo, _, Mean, _, Pop, _, _),
    number(Mean), Mean >= 8,
    number(Pop), Pop > 1500,
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% consiglia_plan_to_read/1
% Suggerisce manga presenti nella lista "plan_to_read" dell'utente che condividono almeno un genere con i manga già letti.
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

% manga_premiato/1
% Raccomanda manga non letti che sono "award_winning" e che contengono almeno un genere tra quelli preferiti.
manga_premiato(TitoloLeggibile) :-
    generi_ordinati(Generi),
    member(Genere-_, Generi),
    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    member(Genere, GeneriManga),
    member(award_winning, GeneriManga),
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% manga_genere_nuovo/1
% Suggerisce manga non letti con almeno 2 generi mai letti e massimo 1 genere già letto. Serve per esplorare novità.
manga_genere_nuovo(TitoloLeggibile) :-
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

    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    intersection(GeneriManga, GeneriMaiLetti, Nuovi),
    intersection(GeneriManga, GeneriUtente, Noti),
    length(Nuovi, LN), LN >= 2,
    length(Noti, LO), LO =< 1,
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% manga_misto_generi_nuovi/1
% Trova manga che combinano almeno un genere mai letto con almeno un genere già letto (anche se visto una sola volta).
% Serve per espandere i gusti restando in parte nel comfort zone.
manga_misto_generi_nuovi(TitoloLeggibile) :-
    findall(Genere, 
        (manga(_, _, Generi, _, _, _, _, _), member(Genere, Generi)),
        TuttiGeneri),
    sort(TuttiGeneri, GeneriTotali),

    findall(GenereLetto,
        (lettura_utente(_, _, Stato, _, GeneriLetti),
         Stato \= plan_to_read,
         member(GenereLetto, GeneriLetti)),
        GeneriLettiRaw),
    sort(GeneriLettiRaw, GeneriUtente),

    subtract(GeneriTotali, GeneriUtente, GeneriMaiLetti),

    manga(ID, Titolo, GeneriManga, _, _, _, _, _),
    intersection(GeneriManga, GeneriUtente, ComuneLetti),
    intersection(GeneriManga, GeneriMaiLetti, ComuneNuovi),
    ComuneLetti \= [],
    ComuneNuovi \= [],
    \+ lettura_utente(ID, _, _, _, _),
    formatta_titolo(Titolo, TitoloLeggibile).

% valuta_compatibilita/1
% Dato un elenco di generi, li confronta con quelli ordinati per frequenza e valuta quanto sono compatibili con i gusti dell'utente.
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


% raccomanda_random/1
% Versione randomizzata di raccomanda/1: suggerisce manga non letti che condividono un genere con quelli preferiti.
% Utilizza solo generi con almeno 10 letture e randomizza i risultati.
raccomanda_random(TitoloLeggibile) :-
    generi_ordinati(Generi),
    member(Genere-Count, Generi),
    Count >= 10,
    findall(ID-Titolo, (
        manga(ID, Titolo, GeneriManga, _, _, _, _, _),
        member(Genere, GeneriManga),
        \+ lettura_utente(ID, _, _, _, _)
    ), Candidati),
    list_to_set(Candidati, Unici),
    random_permutation(Unici, Mischiati),
    member(_-TitoloGrezzo, Mischiati),
    formatta_titolo(TitoloGrezzo, TitoloLeggibile).


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
    writeln('=== SISTEMA DI RACCOMANDAZIONE MANGA ==='),
    writeln('1. Visualizza i generi preferiti (ordinati per frequenza)'),
    writeln('2. Consiglia 5 manga basati sui tuoi gusti più frequenti (random)'),
    writeln('3. Consiglia 5 manga di qualità ma poco popolari'),
    writeln('4. Consiglia 5 manga dalla tua lista "plan_to_read" con generi familiari'),
    writeln('5. Consiglia 5 manga premiati compatibili con i tuoi generi preferiti'),
    writeln('6. Consiglia 5 manga con almeno 2 generi completamente nuovi per te'),
    writeln('7. Consiglia 5 manga che combinano generi noti e generi mai letti'),
    writeln('8. Valuta la compatibilità di una lista di generi rispetto alle tue preferenze'),
    writeln('9. Esci dal programma'),
    write('Scelta (1-9): '),
    read(Scelta),
    esegui_scelta(Scelta).

% --- Gestione delle scelte ---

esegui_scelta(1) :-
    writeln('--- Generi preferiti (ordinati) ---'),
    generi_ordinati(Generi),
    stampa_lista(Generi), nl,
    menu.



esegui_scelta(2) :-
    writeln('--- Manga consigliati in base ai tuoi gusti (randomizzati) ---'),
    findall(Titolo, raccomanda_random(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.




esegui_scelta(3) :-
    writeln('--- Manga di qualità poco popolari (randomizzati) ---'),
    findall(Titolo, manga_qualita_nascosto(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.



esegui_scelta(4) :-
    writeln('--- Consigliati tra i PLAN_TO_READ (randomizzati) ---'),
    findall(Titolo, consiglia_plan_to_read(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.



esegui_scelta(5) :-
    writeln('--- Manga premiati nei tuoi generi preferiti (randomizzati) ---'),
    findall(Titolo, manga_premiato(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.



esegui_scelta(6) :-
    writeln('--- Manga di un genere mai letto (randomizzati) ---'),
    findall(Titolo, manga_genere_nuovo(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.



esegui_scelta(7) :-
    writeln('--- Manga che mischiano generi già letti e generi mai letti (randomizzati) ---'),
    findall(Titolo, manga_misto_generi_nuovi(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
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