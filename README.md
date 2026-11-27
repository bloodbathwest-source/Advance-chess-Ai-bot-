# Advance Chess AI Bot

A chess game that runs in the browser with [Streamlit](https://streamlit.io).
Play against a friend on the same screen, or against the **Stockfish** engine —
the strongest open-source chess engine in the world — at three difficulty
levels. Includes a 10-minute game clock, full move history in standard chess
notation, and automatic checkmate / stalemate / draw detection.

## Features

- **Human vs Human** — two players, one screen.
- **Human vs AI** — three difficulties (Easy / Medium / Hard), and you can
  play as **White or Black** (as Black, the engine opens the game).
- **Game clock** — 10 minutes per side, ticking only on your turn; run out of
  time and you lose on the spot ("flag fall").
- **Game-over detection** — checkmate, stalemate, insufficient material,
  seventy-five-move and fivefold-repetition draws are announced, and the
  board stops accepting moves.
- **Move history in SAN** — proper chess notation (`1. e4 e5 2. Nf3`), and
  moves can be typed either as UCI (`e2e4`) or as notation (`e4`, `Nf3`).
- **Full legal-move helper** — the "Show Legal Moves" expander lists every
  legal move, not just the first 20.
- **Undo** — takes back your last move (in AI mode, the engine's reply too).

## Requirements

- Python 3.10+
- The packages in `requirements.txt`
- **For AI mode only:** a Stockfish binary (see below). Human vs Human works
  without it.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local address Streamlit prints (usually http://localhost:8501).

## Stockfish setup (for AI mode)

1. Download Stockfish from https://stockfishchess.org/download/ and unzip it.
2. Either:
   - add the folder containing the `stockfish` binary to your system `PATH`, **or**
   - set the `STOCKFISH_PATH` environment variable to the binary's full path
     before starting the app, e.g. `STOCKFISH_PATH=/path/to/stockfish streamlit run app.py`.
3. Restart the app.

If no usable binary is found, the app does **not** crash: it shows these
setup instructions in place of the AI's move and lets you play that move
manually, so the game can continue.

## Game modes

| Mode | Notes |
| --- | --- |
| Human vs Human | Both sides typed in by hand. |
| Human vs AI | Pick a difficulty and a colour. Easy/Medium limit the engine's skill level, depth and thinking time; Hard is full-strength Stockfish. |
| Four-Player Chess (Experimental) | Placeholder screen only — the four-player rules are not implemented yet. |

## Tests

A small pytest suite (Streamlit AppTest) covers move gating, undo behaviour,
game-over detection, the game clock, AI difficulty/side choices and the
degraded no-Stockfish path:

```bash
pip install pytest
python -m pytest tests/
```

The tests force the "no engine" path (via a bogus `STOCKFISH_PATH`), so they
pass on machines without Stockfish installed.

## Project layout

- `app.py` — the whole game (UI, clock, AI glue).
- `requirements.txt` — runtime dependencies.
- `tests/` — the pytest/AppTest suite.
