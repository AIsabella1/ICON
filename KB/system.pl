% imposta la codifica dei caratteri a UTF-8 per gestire i caratteri speciali (altrimenti gli accenti non escono correttamente nel menu)
:- set_prolog_flag(encoding, utf8).

% carica la KB
:- consult('knowledge_base.pl').

% verifica se un genere è stato letto almeno 10 volte.
over_10(_-N) :- N >= 10.

% estrae i generi associati ai manga già letti (escludendo quelli in plan_to_read), normalizza per rimuovere eventuali underscore iniziali dai nomi dei generi
genere_letto(GenerePulito) :-
    lettura_utente(_, _, Stato, _, Generi),
    Stato \= plan_to_read,
    member(Genere, Generi),
    normalizza_genere(Genere, GenerePulito).

% rimuove underscore iniziale dal nome dei generi
normalizza_genere(Genere, GenerePulito) :-
    atom_chars(Genere, ['_'|Rest]) -> atom_chars(GenerePulito, Rest) ;
    GenerePulito = Genere.

% calcola la frequenza con cui ciascun genere è stato letto (escludendo plan_to_read), ritornando una lista ordinata alfabeticamwente
frequenza_generi(Frequenze) :-
    findall(Genere, genere_letto(Genere), ListaGeneri),
    sort(ListaGeneri, GeneriUnici),
    findall(Genere-Conta,(member(Genere, GeneriUnici),aggregate_all(count, genere_letto(Genere), Conta)),Frequenze).

% ordina i generi letti in base alla loro frequenza, in ordine decrescente
generi_ordinati(GeneriOrdinati) :-
    frequenza_generi(Frequenze),
    sort(2, @>=, Frequenze, GeneriOrdinati).


% raccomanda manga non ancora letti che hanno voto maggiore o uguale a 8, poco popolari (un valore alto=poco popolare, mentre uno basso=molto popolare), che condividono almeno un genere letto 10 volte
manga_qualita_nascosto(Output) :-
    generi_ordinati(Generi),
    member(Genere-Count, Generi), % basta un genere in comune
    Count >= 10,
    findall(ID-Titolo,(manga(ID, Titolo, GeneriManga, Mean, _, Pop, _, _),number(Mean), Mean >= 8,number(Pop), Pop > 1500,member(Genere, GeneriManga),\+ lettura_utente(ID, _, _, _, _)),Candidati),
    list_to_set(Candidati, Unici),
    random_permutation(Unici, Mischiati),
    member(ID-Titolo, Mischiati),
    manga(ID, _, _, _, _, _, Stato, Autori),
    formatta_output_nome(Titolo, Autori, Stato, Output).

% suggerisce manga presenti nella lista plan_to_read che condividono almeno il 50% dei generi letti almeno 10 volte
consiglia_plan_to_read(Output) :-
    generi_ordinati(Generi),
    include(over_10, Generi, Dominanti),
    maplist(arg(1), Dominanti, GeneriForti),
    lettura_utente(_, Titolo, plan_to_read, _, GeneriPlan),
    intersection(GeneriPlan, GeneriForti, Comune),
    length(Comune, NComune),
    length(GeneriPlan, NTot),
    NTot > 0,
    Ratio is NComune / NTot,
    Ratio >= 0.5,
    formatta_nome_manga(Titolo, Output).

% suggerisce manga non ancora lettio che hanno un premio e con almeno 2 generi preferiti
manga_premiato(Output) :-
    generi_ordinati(Generi),
    include(over_10, Generi, Dominanti),
    maplist(arg(1), Dominanti, GeneriForti),
    manga(ID, Titolo, GeneriManga, _, _, _, Stato, Autori),
    member(award_winning, GeneriManga),
    \+ lettura_utente(ID, _, _, _, _),
    normalizza_lista(GeneriManga, Puliti),
    intersection(Puliti, GeneriForti, Comune),
    length(Comune, NComune),
    NComune >= 2,
    formatta_output_nome(Titolo, Autori, Stato, Output).

% suggerisce manga non ancora letti che combinano generi letti almeno 10 volte con quelli mai letti
manga_misto_generi_nuovi(Output) :-
    findall(Genere, (manga(_, _, Generi, _, _, _, _, _), member(Genere, Generi)), TuttiGeneri),
    sort(TuttiGeneri, GeneriTotali),
    frequenza_generi(Freq),
    include(over_10, Freq, GeneriFrequenti),
    maplist(arg(1), GeneriFrequenti, GeneriDominanti),
    findall(GenereLetto, genere_letto(GenereLetto), GeneriLetti),
    sort(GeneriLetti, GeneriUtente),
    subtract(GeneriTotali, GeneriUtente, GeneriMaiLetti),
    manga(ID, Titolo, GeneriManga, _, _, _, Stato, Autori),
    normalizza_lista(GeneriManga, Normalizzati),
    intersection(Normalizzati, GeneriDominanti, ComuneLetti),
    intersection(Normalizzati, GeneriMaiLetti, ComuneNuovi),
    ComuneLetti \= [],
    ComuneNuovi \= [],
    \+ lettura_utente(ID, _, _, _, _),
    formatta_output_nome(Titolo, Autori, Stato, Output).

% valuta il grado di compatibilità tra un elenco di generi dati in base a quante volte ha letto quei generi
valuta_compatibilita(GeneriForniti) :-
    frequenza_generi(Frequenze),
    maplist(valuta_genere(Frequenze), GeneriForniti, Punteggi),
    sum_list(Punteggi, Somma),
    length(Punteggi, N),
    (N =:= 0 -> Media = 0 ; Media is Somma / N),
    (
        Media >= 2 -> writeln('Questo manga è MOLTO compatibile con i tuoi gusti!')
    ;   Media >= 1 -> writeln('Questo manga è ABBASTANZA compatibile con i tuoi gusti.')
    ;   writeln('Questo manga è POCO compatibile con i tuoi gusti.')
    ).

% normalizza il nome del genere in input e assegna un punteggio in base alla frequenza di lettura
valuta_genere(Frequenze, Genere, Punteggio) :-
    normalizza_genere(Genere, G),
    ( member(G-Conta, Frequenze) ->
        ( Conta >= 20 -> Punteggio = 3
        ; Conta >= 10 -> Punteggio = 2
        ; Conta >= 5  -> Punteggio = 1
        ; Punteggio = 0 )
    ;   Punteggio = 0 ).

% suggerisce un manga non letto che condivide almeno un genere con i generi letti frequentemente (almeno 10 volte).
raccomanda_random(Output) :-
    generi_ordinati(Generi),
    member(Genere-Count, Generi),
    Count >= 10,
    findall(ID-Titolo,(manga(ID, Titolo, GeneriManga, _, _, _, _, _),member(Genere, GeneriManga),\+ lettura_utente(ID, _, _, _, _)), Candidati),
    list_to_set(Candidati, Unici),
    random_permutation(Unici, Mischiati),
    member(ID-Titolo, Mischiati),
    manga(ID, _, _, _, _, _, Stato, Autori),
    formatta_output_nome(Titolo, Autori, Stato, Output).

% interazione con l’utente: chiede il titolo di un manga e verifica se è stato letto.
ha_letto_manga :-
    write('Inserisci il nome del manga: '),
    read_line_to_string(user_input, Input),
    normalize_input(Input, TitoloNorm),
    (
        lettura_utente(_, TitoloNorm, Stato, Voto, _),
        Stato \= plan_to_read
    ->  format('Hai letto ~w. Stato: ~w, Punteggio: ~w~n', [TitoloNorm, Stato, Voto])
    ;   lettura_utente(_, TitoloNorm, plan_to_read, _, _)
    ->  format('Vorresti leggere ~w (presente in plan_to_read).~n', [TitoloNorm])
    ;   format('Non hai letto ~w.~n', [TitoloNorm])
    ).

% converte un titolo di manga in un formato leggibile sostituendo gli underscore con spazi
formatta_titolo(TitoloRaw, TitoloFormattato) :-
    atom_chars(TitoloRaw, Chars),
    maplist(sostituisci_underscore_spazio, Chars, CharsFormattati),
    atom_chars(TitoloFormattato, CharsFormattati).

% sostituisce il carattere underscore '_' con uno spazio, altrimenti lascia invariato il carattere
sostituisci_underscore_spazio('_', ' ') :- !.
sostituisci_underscore_spazio(Char, Char).

% stampa ogni elemento di una lista su una nuova riga
stampa_lista([]).
stampa_lista([X|Xs]) :- writeln(X), stampa_lista(Xs).

% estrae i primi N elementi da una lista, nell’ordine originale
primi_n(0, _, []) :- !.
primi_n(_, [], []) :- !.
primi_n(N, [X|Xs], [X|Ys]) :-
    N1 is N - 1,
    primi_n(N1, Xs, Ys).

% converte una stringa sostituendo tutti gli spazi con underscore
normalize_input(Originale, Normalizzato) :-
    atom_chars(Originale, Chars),
    maplist(sostituisci_spazio_underscore, Chars, NewChars),
    atom_chars(Normalizzato, NewChars).

% sostituisce uno spazio (' ') con un underscore ('_'); altrimenti restituisce il carattere invariato
sostituisci_spazio_underscore(' ', '_') :- !.
sostituisci_spazio_underscore(C, C).

% converte un titolo con underscore in una stringa leggibile e lo formatta come "NOME MANGA: Titolo".
formatta_nome_manga(TitoloRaw, Output) :-
    formatta_titolo(TitoloRaw, TitoloFormattato),
    format(atom(Output), 'NOME MANGA: ~w', [TitoloFormattato]).

% converte il titolo e la lista degli autori in formato leggibile (gli underscore diventano spazi)
formatta_output_nome(TitoloRaw, Autori, Stato, Output) :-
    formatta_titolo(TitoloRaw, TitoloFormattato),
    maplist(formatta_titolo, Autori, AutoriFormattati),  % nuova riga: formatta ogni autore
    atomic_list_concat(AutoriFormattati, ', ', AutoriConcat),
    format(atom(Output), 'NOME MANGA: ~w - AUTORE/I: ~w - STATO: ~w', [TitoloFormattato, AutoriConcat, Stato]).

% applica normalizzazione (rimozione underscore iniziale) a ciascun genere nella lista di input
normalizza_lista([], []).
normalizza_lista([G|Gs], [GN|GNs]) :-
    normalizza_genere(G, GN),
    normalizza_lista(Gs, GNs).

% mostra il menu principale del sistema di raccomandazione e gestisce gli input.
menu :-
    writeln(''),
    writeln('       SISTEMA DI RACCOMANDAZIONE MANGA        '),
    writeln('1. Visualizza i generi preferiti (ordinati per frequenza)'),
    writeln('2. Consiglia 5 manga basati sui gusti più frequenti'),
    writeln('3. Consiglia 5 manga di qualità ma poco popolari basati sui gusti più frequenti'),
    writeln('4. Consiglia 5 manga dalla tua lista "plan_to_read" basati sui gusti più frequenti'),
    writeln('5. Consiglia 5 manga premiati basati sui gusti più frequenti'),
    writeln('6. Consiglia 5 manga che combinano generi basati sui gusti più frequenti e generi mai letti'),
    writeln('7. Valuta la compatibilità di una lista di generi rispetto alle preferenze'),
    writeln('8. Verifica lettura di un manga specifico'),
    writeln('9. Esci dal programma'),
    write('Scelta (1-9): '),
    read(Scelta),
    esegui_scelta(Scelta).

esegui_scelta(1) :-
    writeln('       Generi preferiti (ordinati)     '),
    generi_ordinati(Generi),
    stampa_lista(Generi), nl,
    menu.

esegui_scelta(2) :-
    writeln('       Manga consigliati in base ai tuoi gusti (randomizzati)      '),
    findall(Titolo, raccomanda_random(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(3) :-
    writeln('       Manga di qualità poco popolari (randomizzati)       '),
    findall(Titolo, manga_qualita_nascosto(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(4) :-
    writeln('       Consigliati tra i PLAN_TO_READ (randomizzati)       '),
    findall(Titolo, consiglia_plan_to_read(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(5) :-
    writeln('       Manga premiati nei tuoi generi preferiti (randomizzati)     '),
    findall(Titolo, manga_premiato(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(6) :-
    writeln('       Manga che mischiano generi già letti e generi mai letti (randomizzati)      '),
    findall(Titolo, manga_misto_generi_nuovi(Titolo), Tutti),
    list_to_set(Tutti, Unici),
    random_permutation(Unici, Mischiati),
    primi_n(5, Mischiati, Top5),
    stampa_lista(Top5), nl,
    menu.

esegui_scelta(7) :-
    read_line_to_string(user_input, _), % Mangia invio residuo
    writeln('Inserisci i generi separati da virgola (es: action, fantasy, drama):'),
    read_line_to_string(user_input, InputString),
    split_string(InputString, ",", " ", GeneriFornitiStrings),
    maplist(string_lower, GeneriFornitiStrings, GeneriLower),
    maplist(atom_string, GeneriAtoms, GeneriLower),
    maplist(normalize_input, GeneriAtoms, GeneriNormalizzati),
    ( GeneriNormalizzati == [] ->
        writeln('Non hai inserito nessun genere! Per favore riprova.');
        valuta_compatibilita(GeneriNormalizzati)),
        nl,menu.

esegui_scelta(8) :-
    read_line_to_string(user_input, _),  % Pulisce il buffer dell'invio precedente
    ha_letto_manga,
    nl,
    menu.

esegui_scelta(9) :-
    writeln('Uscita. Grazie!').

esegui_scelta(_) :-
    writeln('Scelta non valida. Riprova.'), nl,
    menu.