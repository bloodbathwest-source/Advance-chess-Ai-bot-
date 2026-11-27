"""AppTest suite for the Streamlit chess app.

Covers: move gating (moves apply only on the Move button), undo behaviour
(HvH pops 1, AI mode pops 2), game-over detection (checkmate + flag fall stop
the game), clock state transitions, AI difficulty + play-as-Black choices,
SAN move history, the full legal-moves list, and the explicit white-piece
board styling.

Deterministic engine behaviour: STOCKFISH_PATH is pointed at /bin/true, an
executable that is not a UCI engine, so the app always takes its graceful
"engine not found" path (guidance + manual fallback) regardless of whether a
real Stockfish happens to be installed on the machine running the tests.
"""

import os
import time
from pathlib import Path

os.environ["STOCKFISH_PATH"] = "/bin/true"

import chess
import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
AI_MODE = "Human vs AI"


def make_app():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception, f"exception on load: {at.exception}"
    return at


def all_text(at):
    parts = []
    for attr in ("markdown", "text", "success", "info", "error", "warning"):
        for el in getattr(at, attr, []):
            parts.append(el.value)
    return "\n".join(parts)


def click_button(at, label):
    matches = [b for b in at.button if b.label == label]
    assert matches, f"button {label!r} not found; have {[b.label for b in at.button]}"
    matches[0].click().run()
    assert not at.exception, f"exception after clicking {label!r}: {at.exception}"


def play(at, move_text):
    at.text_input[0].set_value(move_text)
    click_button(at, "➤ Move")


def board(at):
    return at.session_state["board"]


# ---------------------------------------------------------------------------
# Move gating + undo (the PR #4 fixes, kept under test)
# ---------------------------------------------------------------------------

def test_move_applies_only_on_button_click():
    at = make_app()
    at.text_input[0].set_value("e2e4").run()  # type, but do NOT click Move
    assert not at.exception
    assert len(board(at).move_stack) == 0, "move applied without the Move button"
    click_button(at, "➤ Move")
    assert [str(m) for m in board(at).move_stack] == ["e2e4"]
    assert board(at).turn == chess.BLACK


def test_undo_hvh_pops_one():
    at = make_app()
    play(at, "e2e4")
    play(at, "e7e5")
    click_button(at, "↶ Undo Last Move")
    assert len(board(at).move_stack) == 1
    assert board(at).turn == chess.BLACK


def test_undo_ai_mode_pops_two():
    at = make_app()
    at.selectbox[0].set_value(AI_MODE).run()
    play(at, "e2e4")
    # No usable engine -> guidance shown and a manual fallback offered.
    assert any("Stockfish engine not found" in e.value for e in at.error)
    play(at, "e7e5")  # human plays the AI's move manually
    assert len(board(at).move_stack) == 2
    click_button(at, "↶ Undo Last Move")
    assert len(board(at).move_stack) == 0, "AI-mode undo should pop both half-moves"
    assert board(at).turn == chess.WHITE


# ---------------------------------------------------------------------------
# Game-over detection
# ---------------------------------------------------------------------------

def test_checkmate_is_announced_and_moves_stop():
    at = make_app()
    for mv in ("f2f3", "e7e5", "g2g4", "d8h4"):  # Fool's mate
        play(at, mv)
    assert board(at).is_checkmate()
    text = all_text(at)
    assert "Checkmate! Black wins!" in text
    assert not [b for b in at.button if b.label == "➤ Move"], "moves still accepted after mate"
    assert len(at.text_input) == 0, "move input still shown after mate"


def test_flag_fall_ends_the_game():
    at = make_app()
    at.session_state["clock_white"] = 5.0
    at.session_state["clock_last_ts"] = time.time() - 10.0  # 10s pass on White's turn
    at.run()
    assert not at.exception
    assert at.session_state["flag_winner"] == chess.BLACK
    assert "wins on time" in all_text(at)
    assert not [b for b in at.button if b.label == "➤ Move"], "moves still accepted after flag fall"


# ---------------------------------------------------------------------------
# Clock state transitions
# ---------------------------------------------------------------------------

def test_clock_starts_at_ten_minutes_each():
    at = make_app()
    # A hair under 600 is fine: the side to move is charged for the
    # sub-second gap between state initialisation and the clock sync.
    assert at.session_state["clock_white"] == pytest.approx(600.0, abs=1.0)
    assert at.session_state["clock_black"] == 600.0


def test_clock_ticks_only_for_side_to_move():
    at = make_app()
    at.session_state["clock_last_ts"] = time.time() - 30.0
    at.run()
    white = at.session_state["clock_white"]
    black = at.session_state["clock_black"]
    assert 565.0 < white < 571.0, f"White should have ~570s left, has {white}"
    assert black == 600.0, "Black's clock must not tick on White's turn"
    assert at.session_state["flag_winner"] is None


def test_clock_switches_after_a_move():
    at = make_app()
    play(at, "e2e4")
    white_after_move = at.session_state["clock_white"]
    at.session_state["clock_last_ts"] = time.time() - 20.0
    at.run()
    assert at.session_state["clock_white"] == pytest.approx(white_after_move, abs=0.01), \
        "White's clock must not tick on Black's turn"
    assert 575.0 < at.session_state["clock_black"] < 581.0


# ---------------------------------------------------------------------------
# AI difficulty + play as Black
# ---------------------------------------------------------------------------

def test_ai_options_exist_and_easy_is_selectable():
    at = make_app()
    at.selectbox[0].set_value(AI_MODE).run()
    labels = [s.label for s in at.selectbox]
    assert "AI Difficulty" in labels and "Play as" in labels
    difficulty_box = [s for s in at.selectbox if s.label == "AI Difficulty"][0]
    assert set(difficulty_box.options) == {"Easy", "Medium", "Hard (Extremely Difficult)"}
    difficulty_box.set_value("Easy").run()
    assert not at.exception


def test_play_as_black_engine_opens_with_manual_fallback():
    at = make_app()
    at.selectbox[0].set_value(AI_MODE).run()
    side_box = [s for s in at.selectbox if s.label == "Play as"][0]
    side_box.set_value("Black").run()
    assert not at.exception
    # It is White's (the engine's) turn: with no engine, guidance + fallback.
    assert any("Stockfish engine not found" in e.value for e in at.error)
    play(at, "e2e4")  # human plays the engine's opening move manually
    assert len(board(at).move_stack) == 1
    assert board(at).turn == chess.BLACK  # now the human (Black) is to move
    assert not [e for e in at.error if "Stockfish engine not found" in e.value]


# ---------------------------------------------------------------------------
# Notation, legal moves, board styling
# ---------------------------------------------------------------------------

def test_san_input_and_san_history():
    at = make_app()
    play(at, "e2e4")
    play(at, "e7e5")
    play(at, "Nf3")  # SAN input is accepted too
    assert [str(m) for m in board(at).move_stack] == ["e2e4", "e7e5", "g1f3"]
    history = " ".join(t.value for t in at.text).replace("\n", " ")
    assert "1. e4 e5 2. Nf3" in history, f"SAN history missing: {history!r}"


def test_legal_moves_list_is_not_truncated():
    at = make_app()
    play(at, "e2e4")
    play(at, "e7e5")
    play(at, "g1f3")
    expected = len(list(board(at).legal_moves))
    assert expected > 20, "test position should have more than 20 legal moves"
    text = all_text(at)
    assert "more moves" not in text, "legal-move list still truncates"
    listing = [line for line in text.splitlines() if "legal moves:" in line]
    assert listing, "legal-moves listing not rendered"
    shown = listing[0].split("legal moves:", 1)[1]
    count = len([s for s in shown.split(",") if s.strip()])
    assert count == expected, f"listed {count} moves, expected all {expected}"


def test_white_pieces_are_explicitly_white_in_board_svg():
    at = make_app()
    text = all_text(at)
    assert ".white path" in text and "#ffffff" in text, "explicit white-piece style missing"
    assert ".black path" in text, "explicit black-piece style missing"
