# Streamlit Chess Game with Extremely Difficult AI (using Stockfish)
# To run: streamlit run app.py
# Requirements: pip install -r requirements.txt
# Stockfish binary: download from https://stockfishchess.org/download/ and either
# add it to your PATH or set the STOCKFISH_PATH environment variable to its location.

import os
import shutil

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish

# Resolve the Stockfish binary: the STOCKFISH_PATH environment variable wins,
# otherwise look for a "stockfish" binary on the system PATH.
def resolve_stockfish_path():
    env_path = os.environ.get("STOCKFISH_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    return shutil.which("stockfish")

# Initialize Stockfish. Returns None (instead of crashing) when no usable
# binary is available, so the UI can show setup guidance and degrade gracefully.
@st.cache_resource
def get_stockfish():
    path = resolve_stockfish_path()
    if not path:
        return None
    try:
        return Stockfish(path=path, depth=18, parameters={"Threads": 4, "Hash": 2048})  # High depth for difficulty
    except Exception:
        return None

# Function to display the board
def display_board(board):
    # Responsive board size based on container
    svg = chess.svg.board(board=board, size=500)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
            {svg}
        </div>
        """,
        unsafe_allow_html=True
    )

# Main app
st.title("Chess Game on Streamlit")

game_mode = st.selectbox("Select Game Mode", ["Human vs Human", "Human vs AI (Extremely Difficult)", "Four-Player Chess (Experimental)"])

if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True  # True for White
if 'move_count' not in st.session_state:
    st.session_state.move_count = 0

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

board = st.session_state.board
display_board(board)

if board.is_game_over():
    st.write("Game Over!")
    result = board.result()
    if result == "1-0":
        st.success("🏆 White wins!")
    elif result == "0-1":
        st.success("🏆 Black wins!")
    else:
        st.info("🤝 It's a draw!")
    if st.button("Reset Game"):
        st.session_state.board = chess.Board()
        st.session_state.player_turn = True
        st.session_state.move_count = 0
        st.rerun()
else:
    # Enhanced visual turn indicator
    if board.turn == chess.WHITE:
        st.markdown("### 🔵 **White's Turn**")
        st.progress(1.0, text="White to move")
    else:
        st.markdown("### ⚫ **Black's Turn**")
        st.progress(1.0, text="Black to move")

    ai_turn = game_mode == "Human vs AI (Extremely Difficult)" and board.turn == chess.BLACK
    if ai_turn:
        stockfish = get_stockfish()
        if stockfish is None:
            st.error(
                "⚠️ **Stockfish engine not found — the AI can't move.** "
                "Download Stockfish from https://stockfishchess.org/download/, then either add the "
                "binary to your PATH or set the `STOCKFISH_PATH` environment variable to its location "
                "and restart the app. You can play Black's move manually below in the meantime."
            )
            ai_turn = False  # Degrade gracefully: let the human play Black's move
        else:
            stockfish.set_fen_position(board.fen())
            best_move = stockfish.get_best_move()
            if best_move:
                move = chess.Move.from_uci(best_move)
                if move in board.legal_moves:
                    board.push(move)
                    st.session_state.board = board
                    st.rerun()
                else:
                    st.error("Invalid AI move!")
    if not ai_turn:
        st.markdown("#### 🎯 Enter Your Move")
        col1, col2 = st.columns([3, 1])
        with col1:
            move_input = st.text_input("Move (e.g., e2e4):", key=f"move_input_{st.session_state.move_count}", label_visibility="collapsed", placeholder="Enter move (e.g., e2e4)")
        with col2:
            submit_move = st.button("➤ Move", use_container_width=True)
        
        if submit_move and move_input:
            try:
                move = chess.Move.from_uci(move_input)
                if move in board.legal_moves:
                    board.push(move)
                    st.session_state.board = board
                    st.session_state.player_turn = not st.session_state.player_turn
                    st.session_state.move_count += 1
                    st.rerun()
                else:
                    st.error("❌ Illegal move! Please try again.")
            except ValueError:
                st.error("❌ Invalid move format! Use format like 'e2e4'.")
        
        # Show legal moves hint
        with st.expander("💡 Show Legal Moves"):
            legal_moves_list = [str(move) for move in board.legal_moves]
            st.write(", ".join(legal_moves_list[:20]))  # Show first 20 moves
            if len(legal_moves_list) > 20:
                st.write(f"... and {len(legal_moves_list) - 20} more moves")

col1, col2 = st.columns(2)
with col1:
    if st.button("↶ Undo Last Move", use_container_width=True):
        if board.move_stack:
            # In AI mode, take back the AI's reply AND the player's own move,
            # so it is the player's turn again with their move undone.
            pops = 2 if game_mode == "Human vs AI (Extremely Difficult)" else 1
            for _ in range(min(pops, len(board.move_stack))):
                board.pop()
            st.session_state.board = board
            st.session_state.player_turn = board.turn == chess.WHITE
            st.rerun()
        else:
            st.warning("No moves to undo!")

with col2:
    if st.button("🔄 Reset Game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.player_turn = True
        st.session_state.move_count = 0
        st.rerun()

st.markdown("---")
st.subheader("📜 Move History")
moves = [str(move) for move in board.move_stack]
if moves:
    # Display moves in a more readable format (pairs for White and Black)
    move_pairs = []
    for i in range(0, len(moves), 2):
        if i + 1 < len(moves):
            move_pairs.append(f"{i//2 + 1}. {moves[i]} {moves[i+1]}")
        else:
            move_pairs.append(f"{i//2 + 1}. {moves[i]}")
    st.text("\n".join(move_pairs))
else:
    st.info("No moves yet. Start playing!")