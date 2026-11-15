# Video delle pagine "funzioni" · 16/11/2026

Sei video nuovi, uno per pagina, registrati dall'app vera con lo studio di esempio del sito. Stessi formati del video della home ("Dopo le 19"): **1080×1080** per il computer e **864×1080** per il telefono, 30 fps, senza audio, con il poster di ciascuno.

| Pagina | Computer (1:1) | Telefono (4:5) | Durata |
|---|---|---|---|
| /funzioni/senza-timesheet | senza-timesheet-1x1.mp4 | senza-timesheet-4x5.mp4 | 21,0 s |
| /funzioni/previsione-margine-commessa | previsione-margine-commessa-1x1.mp4 | previsione-margine-commessa-4x5.mp4 | 23,0 s |
| /funzioni/budget-commessa-giornate | budget-commessa-giornate-1x1.mp4 | budget-commessa-giornate-4x5.mp4 | 27,9 s |
| /funzioni/varianti-commessa | varianti-commessa-1x1.mp4 | varianti-commessa-4x5.mp4 | 24,9 s |
| /funzioni/settimana-studio | settimana-studio-1x1.mp4 | settimana-studio-4x5.mp4 | 22,5 s |
| /funzioni/bilancio-commessa | bilancio-commessa-1x1.mp4 | bilancio-commessa-4x5.mp4 | 19,9 s |

Ogni video ha il suo poster: `<nome>-1x1-poster.jpg` e `<nome>-4x5-poster.jpg`.

## Cosa cambiare nelle sei pagine

1. Copiare i 24 file in `/video/funzioni/` del sito.
2. Nel riquadro del video (`figure.reel`) usare lo stesso schema del video della home: `data-desktop` con il file 1x1 e `data-mobile` con il file 4x5, e il poster giusto per ciascuno (sotto 860 px il 4x5). Il video parte muto, in loop, solo quando è a schermo, come oggi.
3. Il riquadro oggi ha `aspect-ratio: 720/986` e larghezza massima 380 px: va portato a **1/1** sul computer e **4/5** sul telefono. La larghezza la sceglie Code perché si legga bene: i video mostrano l'app desktop, quindi conviene più grande di 380 px (per esempio come nella home).
4. Aggiornare in ogni pagina il JSON-LD `VideoObject` (`contentUrl`, `thumbnailUrl`, `duration`, `description`) e l'`aria-label` del video con i testi qui sotto.
5. I vecchi file in `/video/reel/` non servono più alle pagine funzioni (controllare che nessun'altra pagina li usi prima di toglierli).

## Descrizioni (aria-label e description del JSON-LD)

- **senza-timesheet**: Video dell'app sul telefono: alle 19 arriva la domanda, mattina e pomeriggio si segnano con due tap; chi se ne dimentica riceve il promemoria delle 21.
- **previsione-margine-commessa**: Video dell'app dal computer: le commesse dello studio con il loro stato, Scuola Brera con il margine stretto, Uffici Lambrate in perdita con giornate usate, lavoro fatto e fasi.
- **budget-commessa-giornate**: Video dell'app dal computer: una commessa nuova da 18.000 € diventa giornate fase per fase, il margine che vuoi tenere le ricalcola, poi le fasi di Scuola Brera con le giornate oltre il budget.
- **varianti-commessa**: Video dell'app dal computer: il venerdì di Villa Rossi, la fase fatta, quattro mezze giornate di varianti del cliente e il loro valore da chiedere a fine commessa.
- **settimana-studio**: Video dell'app dal computer: la griglia delle mezze giornate dello studio, il filtro su Uffici Lambrate con le giornate per commessa, la correzione di una casella.
- **bilancio-commessa**: Video dell'app dal computer: si chiude Uffici Lambrate e compare il bilancio, 34 giornate su 27, 265 € a giornata contro 320 € di costo, 6 giornate di varianti non fatturate e la resa media per tipo di incarico.

## Da controllare nel testo della pagina varianti

La pagina dice che il venerdì il responsabile indica le mezze giornate di lavoro in più «e per cosa: Seconda proposta per la cucina». Nell'app oggi la domanda del venerdì chiede solo quante mezze giornate (non c'è un campo per la descrizione), e il video mostra questo. Stefano decide se cambiare il testo della pagina o aggiungere il campo nell'app.
