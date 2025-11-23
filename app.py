# Streamlit Chess Game with Extremely Difficult AI (using Stockfish)
# To run: streamlit run app.py
# Requirements: pip install streamlit chess stockfish
# Download Stockfish binary from https://stockfishchess.org/download/ and set the path below.

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish

# Set the path to your Stockfish binary
STOCKFISH_PATH = "path/to/your/stockfish/binary"  # Update this!

# Initialize Stockfish
@st.cache_resource
def get_stockfish():
    return Stockfish(path=STOCKFISH_PATH, depth=18, parameters={"Threads": 4, "Hash": 2048})  # High depth for difficulty

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

    if game_mode == "Human vs AI (Extremely Difficult)" and board.turn == chess.BLACK:
        stockfish = get_stockfish()
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
    else:
        st.markdown("#### 🎯 Enter Your Move")
        col1, col2 = st.columns([3, 1])
        with col1:
            move_input = st.text_input("Move (e.g., e2e4):", key=f"move_input_{st.session_state.move_count}", label_visibility="collapsed", placeholder="Enter move (e.g., e2e4)")
        with col2:
            submit_move = st.button("➤ Move", use_container_width=True)
        
        if move_input:
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
            board.pop()
            st.session_state.board = board
            st.session_state.player_turn = not st.session_state.player_turn
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