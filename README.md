# T-shirt RPFC – lettering "Rugby Parma 1931"

Scritta tonda con lettere incastrate (stile "Come Run With Us"), bianco e nero.

- `rugby-parma-1931.svg/.png` – nero su bianco
- `rugby-parma-1931-negativo.svg/.png` – bianco su nero
- `rugby-parma-1931-trasparente.svg/.png` – nero su trasparente (per la stampa)

Rigenerare: `pip install shapely cairosvg && python3 lettering.py`
(forma delle lettere in `GLYPHS`, disposizione delle righe in `ROWS`,
spessore in `STROKE`, filo bianco tra le lettere in `compose(gap=...)`).
