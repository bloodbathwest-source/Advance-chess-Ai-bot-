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
    svg = chess.svg.board(board=board, size=400)
    st.write(svg, unsafe_allow_html=True)

# Main app
st.title("Chess Game on Streamlit")

game_mode = st.selectbox("Select Game Mode", ["Human vs Human", "Human vs AI (Extremely Difficult)"])

if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True  # True for White

board = st.session_state.board
display_board(board)

if board.is_game_over():
    st.write("Game Over!")
    result = board.result()
    if result == "1-0":
        st.write("White wins!")
    elif result == "0-1":
        st.write("Black wins!")
    else:
        st.write("It's a draw!")
    if st.button("Reset Game"):
        st.session_state.board = chess.Board()
        st.session_state.player_turn = True
        st.rerun()
else:
    if board.turn == chess.WHITE:
        st.write("White's turn")
    else:
        st.write("Black's turn")

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
        move_input = st.text_input("Enter your move (e.g., e2e4):")
        if move_input:
            try:
                move = chess.Move.from_uci(move_input)
                if move in board.legal_moves:
                    board.push(move)
                    st.session_state.board = board
                    st.session_state.player_turn = not st.session_state.player_turn
                    st.rerun()
                else:
                    st.error("Illegal move!")
            except ValueError:
                st.error("Invalid move format!")

if st.button("Undo Last Move"):
    if board.move_stack:
        board.pop()
        st.session_state.board = board
        st.session_state.player_turn = not st.session_state.player_turn
        st.rerun()

st.subheader("Move History")
moves = [str(move) for move in board.move_stack]
st.write(moves)