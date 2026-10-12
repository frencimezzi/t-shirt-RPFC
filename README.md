# T-shirt RPFC – lettering "Rugby Parma 1931"

Scritta tonda disegnata a mano nello stile di "Come Run With Us": nessun font,
ogni lettera è un tratto a pennarello posizionato e dimensionato uno per uno
dentro il cerchio. R gigante su due righe, minuscole miste, lettere incastrate
separate da un filo bianco, texture a pennello asciutto.

- `rugby-parma-1931.svg/.png` – nero su bianco, con texture
- `rugby-parma-1931-negativo.svg/.png` – bianco su nero, con texture
- `rugby-parma-1931-pulito.svg/.png` – nero su bianco, senza texture
- `rugby-parma-1931-trasparente.svg/.png` – nero su trasparente, senza texture (per la stampa)

Rigenerare: `pip install shapely cairosvg && python3 lettering.py`
(ogni lettera è in `letters()`, coordinate in un quadrato 1000x1000).

## Badge circolare "Rugby Parma – Since 1931"

Testo bold condensato curvato in cerchio, puntini ai lati, pallone ovale al
centro, finitura consumata. Testo convertito in tracciati (non serve il font).

- `badge-bianco.svg/.png` – bianco su trasparente, per maglia nera
- `badge-nero.svg/.png` – nero su trasparente, per maglia chiara
- `badge-bianco-anteprima.png` – anteprima su fondo scuro
- `mockup.png` – anteprima retro (grande) e fronte (cuore, piccolo)

Rigenerare: `pip install shapely cairosvg fonttools && python3 badge.py && python3 mockup.py`
