# Streamlit Chess Game with Interactive UI and AI (using Stockfish)
# To run: streamlit run app.py
# Requirements: pip install -r requirements.txt
# Download Stockfish binary from https://stockfishchess.org/download/ and set the path below.

import streamlit as st
import chess
import chess.svg

# Optional: Set the path to your Stockfish binary if you want AI opponent
STOCKFISH_PATH = None  # Set to "path/to/your/stockfish/binary" to enable AI

# Initialize Stockfish (optional)
@st.cache_resource
def get_stockfish():
    if STOCKFISH_PATH:
        try:
            from stockfish import Stockfish
            return Stockfish(path=STOCKFISH_PATH, depth=18, parameters={"Threads": 4, "Hash": 2048})
        except Exception as e:
            st.warning(f"Stockfish not available: {e}")
            return None
    return None

# Function to get legal moves for a piece at a given square
def get_legal_moves_for_square(board, square):
    """Get all legal moves from a given square in UCI format."""
    legal_moves = []
    square_obj = chess.parse_square(square)
    for move in board.legal_moves:
        if move.from_square == square_obj:
            legal_moves.append(chess.square_name(move.to_square))
    return legal_moves

# Function to display the interactive chessboard
def display_interactive_board(board, selected_square=None):
    """Display an interactive chessboard with move selection"""
    
    # Get last move for highlighting
    last_move = None
    if board.move_stack:
        last_move = board.peek()
    
    # Get legal moves if a square is selected
    legal_moves = []
    if selected_square is not None:
        try:
            square_obj = chess.parse_square(selected_square)
            for move in board.legal_moves:
                if move.from_square == square_obj:
                    legal_moves.append(move.to_square)
        except:
            pass
    
    # Create SVG with highlighting
    svg = chess.svg.board(
        board=board,
        size=500,
        lastmove=last_move,
        check=board.king(board.turn) if board.is_check() else None,
        squares=chess.SquareSet(legal_moves) if legal_moves else None
    )
    
    # Display the board
    st.write(svg, unsafe_allow_html=True)
    
    return None

# Configure page
st.set_page_config(page_title="Interactive Chess Game", page_icon="♟️", layout="centered")

# Main app
st.title("♟️ Interactive Chess Game")
st.markdown("---")

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True  # True for White
if 'last_error' not in st.session_state:
    st.session_state.last_error = None
if 'move_count' not in st.session_state:
    st.session_state.move_count = 0

board = st.session_state.board

# Game controls in sidebar
with st.sidebar:
    st.header("🎮 Game Controls")
    
    game_mode = st.selectbox(
        "Select Game Mode", 
        ["Human vs Human", "Human vs AI (Extremely Difficult)"],
        help="Choose whether to play against another human or the AI"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Game", use_container_width=True):
            st.session_state.board = chess.Board()
            st.session_state.player_turn = True
            st.session_state.last_error = None
            st.session_state.move_count = 0
            st.rerun()
    
    with col2:
        if st.button("↩️ Undo Move", use_container_width=True):
            if board.move_stack:
                board.pop()
                st.session_state.board = board
                st.session_state.player_turn = not st.session_state.player_turn
                st.session_state.move_count -= 1
                st.rerun()
    
    st.markdown("---")
    
    # Game status
    st.subheader("📊 Game Status")
    st.write(f"**Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.write(f"**Moves:** {st.session_state.move_count}")
    
    if board.is_check():
        st.warning("⚠️ **Check!**")
    
    st.markdown("---")
    
    # Move history
    st.subheader("📜 Move History")
    if board.move_stack:
        moves = []
        for i, move in enumerate(board.move_stack):
            move_num = i // 2 + 1
            if i % 2 == 0:
                moves.append(f"{move_num}. {move.uci()}")
            else:
                moves[-1] += f" {move.uci()}"
        
        # Display last 10 moves
        for move_text in moves[-10:]:
            st.text(move_text)
    else:
        st.info("No moves yet")

# Check for game over
if board.is_game_over():
    st.balloons()
    
    result = board.result()
    if result == "1-0":
        st.success("🎉 **Game Over! White wins!**")
    elif result == "0-1":
        st.success("🎉 **Game Over! Black wins!**")
    else:
        st.info("🤝 **Game Over! It's a draw!**")
    
    # Display final board position
    move = display_interactive_board(board)
    
    st.markdown("---")
    st.info("Click 'Reset Game' in the sidebar to start a new game")
    
else:
    # Display turn indicator
    turn_col1, turn_col2, turn_col3 = st.columns([1, 2, 1])
    with turn_col2:
        if board.turn == chess.WHITE:
            st.info("⚪ **White's Turn**")
        else:
            st.info("⚫ **Black's Turn**")
    
    # Handle AI move if it's AI's turn
    if game_mode == "Human vs AI (Extremely Difficult)" and board.turn == chess.BLACK:
        stockfish = get_stockfish()
        if stockfish:
            with st.spinner("🤖 AI is thinking..."):
                stockfish.set_fen_position(board.fen())
                best_move = stockfish.get_best_move()
                if best_move:
                    try:
                        move = chess.Move.from_uci(best_move)
                        if move in board.legal_moves:
                            board.push(move)
                            st.session_state.board = board
                            st.session_state.move_count += 1
                            st.rerun()
                        else:
                            st.error("❌ Invalid AI move!")
                    except Exception as e:
                        st.error(f"❌ AI error: {e}")
        else:
            st.warning("⚠️ AI not available. Please configure Stockfish path in the code.")
    
    # Display the chessboard
    display_interactive_board(board)
    
    # Alternative text input for moves
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        move_input = st.text_input(
            "From square (e.g., e2):",
            key="from_square",
            help="Enter the square you want to move from"
        )
    
    with col2:
        to_input = st.text_input(
            "To square (e.g., e4):",
            key="to_square",
            help="Enter the destination square"
        )
    
    if st.button("Make Move", type="primary"):
        if move_input and to_input:
            try:
                # Handle promotion if specified
                promotion_choice = st.selectbox(
                    "Promotion piece (if applicable):",
                    ["None", "q", "r", "b", "n"],
                    key="promotion"
                )
                
                move_str = move_input.lower() + to_input.lower()
                if promotion_choice != "None":
                    move_str += promotion_choice
                
                chess_move = chess.Move.from_uci(move_str)
                
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                    st.session_state.board = board
                    st.session_state.player_turn = not st.session_state.player_turn
                    st.session_state.last_error = None
                    st.session_state.move_count += 1
                    st.rerun()
                else:
                    st.error(f"❌ Illegal move: {move_str}")
            except Exception as e:
                st.error(f"❌ Invalid move format: {str(e)}")
        else:
            st.warning("⚠️ Please enter both from and to squares")
    
    # Help section
    with st.expander("ℹ️ How to Play"):
        st.markdown("""
        **Interactive Chessboard:**
        - **Visual indicators** show the last move played (highlighted squares)
        - **Check detection** is indicated with special highlighting
        - **Legal moves** are shown in green when a piece can be moved
        - The board updates in real-time after each valid move
        
        **Making Moves:**
        - Enter the **from square** (e.g., e2) and **to square** (e.g., e4)
        - Click **Make Move** to execute the move
        - For pawn promotion, select the piece type before moving
        
        **Move Notation:**
        - Squares are named by column (a-h) and row (1-8)
        - Example: e2 to e4 moves the pawn forward two squares
        
        **Game Modes:**
        - **Human vs Human:** Play against another person locally
        - **Human vs AI:** Challenge the Stockfish engine (requires setup)
        
        **Controls:**
        - Use the sidebar to reset the game or undo moves
        - View move history and game status in the sidebar
        - Check warnings appear automatically when applicable
        """)