# Streamlit Chess Game with Stockfish AI
# To run: streamlit run app.py
# Requirements: pip install -r requirements.txt
# Stockfish binary: download from https://stockfishchess.org/download/ and either
# add it to your PATH or set the STOCKFISH_PATH environment variable to its location.

import os
import shutil
import time

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLOCK_START_SECONDS = 10 * 60  # 10 minutes per side

AI_MODE = "Human vs AI"
GAME_MODES = ["Human vs Human", AI_MODE, "Four-Player Chess (Experimental)"]

# AI difficulty levels: engine depth, Stockfish "Skill Level" (0-20) and the
# maximum thinking time per move. Hard is the original full-strength setup.
DIFFICULTY_LEVELS = {
    "Easy": {"depth": 5, "skill_level": 3, "time_ms": 200},
    "Medium": {"depth": 10, "skill_level": 10, "time_ms": 600},
    "Hard (Extremely Difficult)": {"depth": 18, "skill_level": 20, "time_ms": None},
}

# Board colours: light/dark squares plus explicit piece colours so White's
# pieces render bright white with a dark outline and Black's render dark.
BOARD_COLORS = {
    "square light": "#f0d9b5",
    "square dark": "#b58863",
    "square light lastmove": "#cdd26a",
    "square dark lastmove": "#aaa23a",
    "margin": "#f0d9b5",
    "coord": "#946f51",
}
WHITE_PIECE_FILL = "#ffffff"
WHITE_PIECE_STROKE = "#000000"
BLACK_PIECE_FILL = "#000000"
# Injected into the board SVG (chess.svg's `style` hook): CSS rules override
# the piece paths' built-in fill attributes, so White is guaranteed bright
# white with a dark outline and Black stays solid dark.
PIECE_STYLE = (
    f".white path {{ fill: {WHITE_PIECE_FILL}; stroke: {WHITE_PIECE_STROKE}; }}"
    f".black path {{ fill: {BLACK_PIECE_FILL}; }}"
)

# ---------------------------------------------------------------------------
# Stockfish setup
# ---------------------------------------------------------------------------

# Resolve the Stockfish binary: the STOCKFISH_PATH environment variable wins,
# otherwise look for a "stockfish" binary on the system PATH.
def resolve_stockfish_path():
    env_path = os.environ.get("STOCKFISH_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    return shutil.which("stockfish")

# Initialize Stockfish for a difficulty level. Returns None (instead of
# crashing) when no usable binary is available, so the UI can show setup
# guidance and degrade gracefully.
@st.cache_resource
def get_stockfish(difficulty):
    path = resolve_stockfish_path()
    if not path:
        return None
    cfg = DIFFICULTY_LEVELS[difficulty]
    try:
        return Stockfish(
            path=path,
            depth=cfg["depth"],
            parameters={"Threads": 2, "Hash": 512, "Skill Level": cfg["skill_level"]},
        )
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Pure helpers (also exercised by the test suite)
# ---------------------------------------------------------------------------

def format_clock(seconds):
    """Format remaining seconds as M:SS."""
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60}:{seconds % 60:02d}"

def tick_clock(clock_white, clock_black, turn, last_ts, now):
    """Deduct the time elapsed since `last_ts` from the side to move.

    Returns (clock_white, clock_black, last_ts, flag_winner) where
    flag_winner is chess.WHITE/chess.BLACK when the side to move has run
    out of time (so the *other* side wins), otherwise None.
    """
    if last_ts is None:
        return clock_white, clock_black, now, None
    elapsed = max(0.0, now - last_ts)
    flag_winner = None
    if turn == chess.WHITE:
        clock_white = max(0.0, clock_white - elapsed)
        if clock_white <= 0.0:
            flag_winner = chess.BLACK
    else:
        clock_black = max(0.0, clock_black - elapsed)
        if clock_black <= 0.0:
            flag_winner = chess.WHITE
    return clock_white, clock_black, now, flag_winner

def outcome_message(board, flag_winner=None):
    """Return (is_over, message) for the position, including flag fall."""
    if flag_winner is not None:
        winner = "White" if flag_winner == chess.WHITE else "Black"
        loser = "Black" if flag_winner == chess.WHITE else "White"
        return True, f"⏰ {loser}'s flag fell — {winner} wins on time!"
    outcome = board.outcome()
    if outcome is None:
        return False, ""
    if outcome.termination == chess.Termination.CHECKMATE:
        winner = "White" if outcome.winner == chess.WHITE else "Black"
        return True, f"🏆 Checkmate! {winner} wins!"
    if outcome.termination == chess.Termination.STALEMATE:
        return True, "🤝 Stalemate — it's a draw!"
    if outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
        return True, "🤝 Draw — insufficient material to checkmate."
    if outcome.termination == chess.Termination.SEVENTYFIVE_MOVES:
        return True, "🤝 Draw — seventy-five-move rule."
    if outcome.termination == chess.Termination.FIVEFOLD_REPETITION:
        return True, "🤝 Draw — fivefold repetition."
    return True, "🤝 The game is a draw."

def san_history(board):
    """Move history in standard algebraic notation (SAN), e.g. ['e4', 'e5', 'Nf3']."""
    replay = chess.Board()
    sans = []
    for move in board.move_stack:
        sans.append(replay.san(move))
        replay.push(move)
    return sans

def parse_move_input(board, text):
    """Parse a typed move as UCI ('e2e4') or SAN ('e4', 'Nf3').

    Returns a legal chess.Move, or None when the text is neither a valid
    format nor a legal move in this position.
    """
    text = (text or "").strip()
    if not text:
        return None
    try:
        move = chess.Move.from_uci(text.lower())
        if move in board.legal_moves:
            return move
    except ValueError:
        pass
    try:
        return board.parse_san(text)
    except ValueError:
        return None

def ai_undo_pops(board, human_color):
    """How many half-moves Undo should pop in AI mode: the AI's reply plus
    the player's own move, so it is the player's turn again. Pops at least
    one move and never more than the stack holds (e.g. when the human plays
    Black, only the engine's opening move may be on the stack)."""
    stack = list(board.move_stack)
    pops = 0
    while stack and pops < 2:
        stack.pop()
        pops += 1
        # Whose turn would it be after these pops?
        turn_after = chess.WHITE if len(stack) % 2 == 0 else chess.BLACK
        if pops >= 1 and turn_after == human_color:
            break
    return pops

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def reset_game():
    st.session_state.board = chess.Board()
    st.session_state.player_turn = True  # True for White
    st.session_state.move_count = 0
    st.session_state.clock_white = float(CLOCK_START_SECONDS)
    st.session_state.clock_black = float(CLOCK_START_SECONDS)
    st.session_state.clock_last_ts = time.time()
    st.session_state.flag_winner = None

def init_state():
    if 'board' not in st.session_state:
        reset_game()
    # Defaults for sessions created before the clock existed.
    st.session_state.setdefault('clock_white', float(CLOCK_START_SECONDS))
    st.session_state.setdefault('clock_black', float(CLOCK_START_SECONDS))
    st.session_state.setdefault('clock_last_ts', time.time())
    st.session_state.setdefault('flag_winner', None)

def sync_clock():
    """Charge the side to move for the time since the last rerun and record
    a flag fall when a clock reaches zero. Frozen once the game is over."""
    board = st.session_state.board
    if st.session_state.flag_winner is not None or board.is_game_over():
        st.session_state.clock_last_ts = time.time()
        return
    w, b, ts, flag = tick_clock(
        st.session_state.clock_white,
        st.session_state.clock_black,
        board.turn,
        st.session_state.clock_last_ts,
        time.time(),
    )
    st.session_state.clock_white = w
    st.session_state.clock_black = b
    st.session_state.clock_last_ts = ts
    if flag is not None:
        st.session_state.flag_winner = flag

# ---------------------------------------------------------------------------
# Board display
# ---------------------------------------------------------------------------

def display_board(board, orientation=chess.WHITE):
    svg = chess.svg.board(board=board, orientation=orientation, size=500,
                          colors=BOARD_COLORS, style=PIECE_STYLE)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
            {svg}
        </div>
        """,
        unsafe_allow_html=True
    )

def display_clocks(board, game_over):
    col_w, col_b = st.columns(2)
    white_label = f"⚪ White: **{format_clock(st.session_state.clock_white)}**"
    black_label = f"⚫ Black: **{format_clock(st.session_state.clock_black)}**"
    with col_w:
        if not game_over and board.turn == chess.WHITE:
            st.success(f"⏱ {white_label} — thinking…")
        else:
            st.info(f"⏱ {white_label}")
    with col_b:
        if not game_over and board.turn == chess.BLACK:
            st.success(f"⏱ {black_label} — thinking…")
        else:
            st.info(f"⏱ {black_label}")

# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

st.title("Chess Game on Streamlit")

game_mode = st.selectbox("Select Game Mode", GAME_MODES)

# Handle Four-Player Chess mode
if game_mode == "Four-Player Chess (Experimental)":
    st.warning("⚠️ **Experimental Feature**: Four-Player Chess is a placeholder for future development. Full functionality coming soon!")

    st.subheader("Four-Player Chess Board (Conceptual)")

    # Create a pseudo-interface for four-player chess
    cols = st.columns(4)
    with cols[0]:
        st.markdown("### 👤 Player 1 (White)")
        st.info("Bottom position")
    with cols[1]:
        st.markdown("### 👤 Player 2 (Black)")
        st.info("Top position")
    with cols[2]:
        st.markdown("### 👤 Player 3 (Red)")
        st.info("Left position")
    with cols[3]:
        st.markdown("### 👤 Player 4 (Blue)")
        st.info("Right position")

    st.markdown("---")
    st.markdown("#### 🎮 Four-Player Chess Rules (Preview)")
    st.markdown("""
    - **Turn Order**: White → Black → Red → Blue
    - **Board Layout**: Extended 14x14 board with four starting positions
    - **Objective**: Last player with their king remaining wins
    - **Alliances**: Players can form temporary alliances
    """)

    # Display a placeholder board visualization
    st.markdown("""
    <div style="
        width: 100%;
        height: 400px;
        background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 10px;
        color: #ECF0F1;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        margin: 20px 0;
    ">
        Four-Player Chess Board<br/>Coming Soon
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Tip**: Switch to 'Human vs Human' or 'Human vs AI' modes to play regular chess!")

    st.stop()  # Stop execution for four-player mode

# AI options (difficulty + which colour the human plays)
difficulty = "Hard (Extremely Difficult)"
human_color = chess.WHITE
if game_mode == AI_MODE:
    opt_col1, opt_col2 = st.columns(2)
    with opt_col1:
        difficulty = st.selectbox("AI Difficulty", list(DIFFICULTY_LEVELS.keys()),
                                  index=list(DIFFICULTY_LEVELS.keys()).index(difficulty))
    with opt_col2:
        side_choice = st.selectbox("Play as", ["White", "Black"])
        human_color = chess.WHITE if side_choice == "White" else chess.BLACK

init_state()
sync_clock()

board = st.session_state.board
game_over, result_message = outcome_message(board, st.session_state.flag_winner)

orientation = human_color if game_mode == AI_MODE else chess.WHITE
display_board(board, orientation=orientation)
display_clocks(board, game_over)

if game_over:
    st.write("Game Over!")
    st.success(result_message)
    if st.button("Reset Game"):
        reset_game()
        st.rerun()
else:
    # Enhanced visual turn indicator
    if board.turn == chess.WHITE:
        st.markdown("### 🔵 **White's Turn**")
        st.progress(1.0, text="White to move")
    else:
        st.markdown("### ⚫ **Black's Turn**")
        st.progress(1.0, text="Black to move")

    ai_turn = game_mode == AI_MODE and board.turn != human_color
    if ai_turn:
        stockfish = get_stockfish(difficulty)
        if stockfish is None:
            st.error(
                "⚠️ **Stockfish engine not found — the AI can't move.** "
                "Download Stockfish from https://stockfishchess.org/download/, then either add the "
                "binary to your PATH or set the `STOCKFISH_PATH` environment variable to its location "
                "and restart the app. You can play the AI's move manually below in the meantime."
            )
            ai_turn = False  # Degrade gracefully: let the human play the AI's move
        else:
            stockfish.set_fen_position(board.fen())
            cfg = DIFFICULTY_LEVELS[difficulty]
            if cfg["time_ms"]:
                best_move = stockfish.get_best_move_time(cfg["time_ms"])
            else:
                best_move = stockfish.get_best_move()
            if best_move:
                move = chess.Move.from_uci(best_move)
                if move in board.legal_moves:
                    board.push(move)
                    st.session_state.board = board
                    st.session_state.clock_last_ts = time.time()
                    st.rerun()
                else:
                    st.error("Invalid AI move!")
    if not ai_turn:
        st.markdown("#### 🎯 Enter Your Move")
        col1, col2 = st.columns([3, 1])
        with col1:
            move_input = st.text_input("Move (e.g., e2e4 or Nf3):", key=f"move_input_{st.session_state.move_count}", label_visibility="collapsed", placeholder="Enter move (e.g., e2e4 or Nf3)")
        with col2:
            submit_move = st.button("➤ Move", use_container_width=True)

        if submit_move and move_input:
            move = parse_move_input(board, move_input)
            if move is not None:
                board.push(move)
                st.session_state.board = board
                st.session_state.player_turn = not st.session_state.player_turn
                st.session_state.move_count += 1
                st.session_state.clock_last_ts = time.time()
                st.rerun()
            else:
                st.error("❌ Illegal or unrecognised move! Use UCI ('e2e4') or notation ('e4', 'Nf3').")

        # Show legal moves hint — the full list, in standard notation
        with st.expander("💡 Show Legal Moves"):
            legal_sans = sorted(board.san(m) for m in board.legal_moves)
            st.write(f"{len(legal_sans)} legal moves: " + ", ".join(legal_sans))

col1, col2 = st.columns(2)
with col1:
    if st.button("↶ Undo Last Move", use_container_width=True):
        if board.move_stack:
            # In AI mode, take back the AI's reply AND the player's own move,
            # so it is the player's turn again with their move undone.
            if game_mode == AI_MODE:
                pops = ai_undo_pops(board, human_color)
            else:
                pops = 1
            for _ in range(min(pops, len(board.move_stack))):
                board.pop()
            st.session_state.board = board
            st.session_state.player_turn = board.turn == chess.WHITE
            st.session_state.flag_winner = None
            st.session_state.clock_last_ts = time.time()
            st.rerun()
        else:
            st.warning("No moves to undo!")

with col2:
    if st.button("🔄 Reset Game", use_container_width=True):
        reset_game()
        st.rerun()

st.markdown("---")
st.subheader("📜 Move History")
sans = san_history(board)
if sans:
    # Display moves in a more readable format (pairs for White and Black)
    move_pairs = []
    for i in range(0, len(sans), 2):
        if i + 1 < len(sans):
            move_pairs.append(f"{i//2 + 1}. {sans[i]} {sans[i+1]}")
        else:
            move_pairs.append(f"{i//2 + 1}. {sans[i]}")
    st.text("\n".join(move_pairs))
else:
    st.info("No moves yet. Start playing!")
