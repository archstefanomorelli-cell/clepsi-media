# clepsi-media

Media pubblici di Clepsi per Instagram e LinkedIn, con sorgenti e strumenti per rifarli.
Metricool prende i file da qui tramite raw.githubusercontent.com: quando si aggiorna un file
già programmato, usare l'URL con l'impronta del commit (…/clepsi-media/<sha>/percorso), non `main`.

## Cartelle
- `settimana-1/`, `reel/`, `linkedin/`: file pubblicati o programmati.
- `grafiche/`: sorgenti dei post (tavole 1080×1350, file .dc.html del canvas Design "Instagram Clepsi · primi post").
- `sorgenti/racconto/`, `sorgenti/serate/`, `sorgenti/audio/`: clip e suoni di partenza.
- `strumenti/`: script. I risultati finiscono in `lavoro/` (non versionata).

## Preparare l'ambiente
```
# font del marchio (Bricolage Grotesque, DM Sans, Instrument Serif) dall'archivio Google Fonts
git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts /tmp/gfonts
git -C /tmp/gfonts sparse-checkout set ofl/dmsans ofl/bricolagegrotesque ofl/instrumentserif
mkdir -p ~/.fonts && cp /tmp/gfonts/ofl/*/*.ttf ~/.fonts/ && fc-cache -f
# servono anche ffmpeg, python3 con numpy, scipy, opencv, pillow e playwright (Chromium)
```

## Script
- `strumenti/reel_serate.py`: 4 reel delle serate (scena con schermata dell'app, tabella della settimana, chiusura con logo).
- `strumenti/reel_racconto_scene.py`: 6 reel del racconto (caso in alto, latino e italiano di Seneca in basso, chiusura con logo).
- `strumenti/render_ig.py <cartella .dc.html> <uscita>`: trasforma le tavole in PNG con i font del marchio (aggiornare l'elenco `names` e `DATA` per tavole nuove con liste).
- `strumenti/reel_lib.py`: funzioni comuni (PNG trasparenti da HTML, sovrapposizioni temporizzate).
- `strumenti/ombra.py`, `push_still.py`, `blur_volto.py`: utilità per le clip (ombra della meridiana in movimento, avvicinamento fluido su immagine ferma, volto sfocato).

## Stile
Colori: #0B0B0D, #121214, #F6F5F1, lime #D4FF3A. Commesse: Villa Rossi #D4FF3A, Scuola Brera #9B8CFF, Uffici Lambrate #6FD3FF, Loft Navigli #FF9ECF.
Stati: In attivo #D4FF3A, Margine stretto #FFC46B, In perdita #FF8A7A, Appena iniziata #C9C8D0.
Reel: 1080×1920, testi grandi e fermi a lungo (niente scritte veloci in apertura), etichetta "creato con IA" se ci sono clip generate.
