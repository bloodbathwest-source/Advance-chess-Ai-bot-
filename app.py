# Enhanced Streamlit Chess Game with Interactive UI and AI (using Stockfish)
# To run: streamlit run app.py
# Requirements: pip install -r requirements.txt
# Download Stockfish binary from https://stockfishchess.org/download/ and set the path below.

import streamlit as st
import streamlit.components.v1 as components
import chess
import chess.svg
import json

# Optional: Set the path to your Stockfish binary (only needed for AI mode)
STOCKFISH_PATH = "path/to/your/stockfish/binary"  # Update this if you want to use AI mode

# Initialize Stockfish (only if path is valid)
@st.cache_resource
def get_stockfish():
    try:
        from stockfish import Stockfish
        return Stockfish(path=STOCKFISH_PATH, depth=18, parameters={"Threads": 4, "Hash": 2048})
    except (ImportError, FileNotFoundError, Exception):
        return None

# Function to get legal moves for a square
def get_legal_moves_for_square(board, square):
    """Get all legal moves from a specific square."""
    legal_moves = []
    for move in board.legal_moves:
        if move.from_square == square:
            legal_moves.append(chess.square_name(move.to_square))
    return legal_moves

# Function to create interactive chessboard HTML
def create_interactive_board(board, last_move=None):
    """Create an interactive chessboard using Chessboard.js."""
    
    # Get FEN position
    fen = board.fen()
    
    # Get last move squares for highlighting
    last_move_from = ""
    last_move_to = ""
    if last_move:
        last_move_from = chess.square_name(last_move.from_square)
        last_move_to = chess.square_name(last_move.to_square)
    
    # Build legal moves dictionary for highlighting
    legal_moves_dict = {}
    for square in chess.SQUARES:
        moves = get_legal_moves_for_square(board, square)
        if moves:
            legal_moves_dict[chess.square_name(square)] = moves
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
        <style>
            #myBoard {{
                width: 500px;
                margin: 20px auto;
            }}
            .highlight-square {{
                box-shadow: inset 0 0 3px 3px yellow;
            }}
            .legal-move {{
                background: radial-gradient(circle, rgba(0,128,0,0.3) 25%, transparent 25%);
                background-size: 100% 100%;
            }}
            .last-move {{
                background-color: rgba(255, 255, 0, 0.4) !important;
            }}
            #status {{
                text-align: center;
                margin: 20px;
                font-size: 18px;
                font-weight: bold;
            }}
            .error-message {{
                color: red;
                text-align: center;
                margin: 10px;
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div id="status"></div>
        <div id="myBoard"></div>
        <div id="error" class="error-message"></div>
        
        <script>
            var board = null;
            var game_fen = '{fen}';
            var selectedSquare = null;
            var legalMovesDict = {json.dumps(legal_moves_dict)};
            var lastMoveFrom = '{last_move_from}';
            var lastMoveTo = '{last_move_to}';
            
            function removeHighlights() {{
                $('#myBoard .square-55d63').removeClass('highlight-square legal-move');
            }}
            
            function highlightLastMove() {{
                if (lastMoveFrom) {{
                    $('#myBoard .square-' + lastMoveFrom).addClass('last-move');
                }}
                if (lastMoveTo) {{
                    $('#myBoard .square-' + lastMoveTo).addClass('last-move');
                }}
            }}
            
            function highlightLegalMoves(square) {{
                var legalMoves = legalMovesDict[square] || [];
                legalMoves.forEach(function(move) {{
                    $('#myBoard .square-' + move).addClass('legal-move');
                }});
            }}
            
            function onDragStart(source, piece, position, orientation) {{
                // Prevent dragging if game is over or it's not the piece's turn
                if (game_fen.includes(' w ') && piece.search(/^b/) !== -1) {{
                    return false;
                }}
                if (game_fen.includes(' b ') && piece.search(/^w/) !== -1) {{
                    return false;
                }}
                
                // Check if the piece has legal moves
                if (!legalMovesDict[source] || legalMovesDict[source].length === 0) {{
                    return false;
                }}
                
                // Highlight legal moves
                removeHighlights();
                highlightLastMove();
                highlightLegalMoves(source);
            }}
            
            function onDrop(source, target) {{
                removeHighlights();
                highlightLastMove();
                
                // Check if the move is legal
                if (legalMovesDict[source] && legalMovesDict[source].includes(target)) {{
                    // Send move to Streamlit
                    var move = source + target;
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: move
                    }}, '*');
                    return;
                }} else {{
                    document.getElementById('error').textContent = 'Invalid move! Please select a legal move.';
                    setTimeout(function() {{
                        document.getElementById('error').textContent = '';
                    }}, 3000);
                    return 'snapback';
                }}
            }}
            
            function onSnapEnd() {{
                board.position(game_fen);
            }}
            
            function onMouseoutSquare(square, piece) {{
                removeHighlights();
                highlightLastMove();
            }}
            
            function onMouseoverSquare(square, piece) {{
                // Highlight the square
                if (legalMovesDict[square] && legalMovesDict[square].length > 0) {{
                    removeHighlights();
                    highlightLastMove();
                    $('#myBoard .square-' + square).addClass('highlight-square');
                    highlightLegalMoves(square);
                }}
            }}
            
            var config = {{
                draggable: true,
                position: game_fen,
                onDragStart: onDragStart,
                onDrop: onDrop,
                onSnapEnd: onSnapEnd,
                onMouseoutSquare: onMouseoutSquare,
                onMouseoverSquare: onMouseoverSquare,
                pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
            }};
            
            board = Chessboard('myBoard', config);
            
            // Highlight last move on load
            highlightLastMove();
            
            // Update status
            var status = game_fen.includes(' w ') ? "White's turn" : "Black's turn";
            document.getElementById('status').textContent = status;
        </script>
    </body>
    </html>
    """
    return html_code

# Main app
st.set_page_config(page_title="Interactive Chess Game", page_icon="♟️", layout="wide")
st.title("♟️ Interactive Chess Game with AI")

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'last_move' not in st.session_state:
    st.session_state.last_move = None
if 'move_history' not in st.session_state:
    st.session_state.move_history = []
if 'last_processed_move' not in st.session_state:
    st.session_state.last_processed_move = ''

# Sidebar for game controls
with st.sidebar:
    st.header("Game Controls")
    game_mode = st.selectbox("Select Game Mode", ["Human vs Human", "Human vs AI (Extremely Difficult)"])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Game", use_container_width=True):
            st.session_state.board = chess.Board()
            st.session_state.last_move = None
            st.session_state.move_history = []
            st.rerun()
    
    with col2:
        if st.button("⬅️ Undo Move", use_container_width=True):
            if st.session_state.board.move_stack:
                st.session_state.board.pop()
                st.session_state.move_history.pop()
                st.session_state.last_move = st.session_state.board.peek() if st.session_state.board.move_stack else None
                st.rerun()
    
    st.divider()
    
    st.subheader("📜 Move History")
    if st.session_state.move_history:
        for i, move in enumerate(st.session_state.move_history, 1):
            if i % 2 == 1:
                move_num = f"{(i+1)//2}. {move}"
                if i < len(st.session_state.move_history):
                    move_num += f" {st.session_state.move_history[i]}"
                    st.text(move_num)
            elif i % 2 == 0 and i > 1:
                continue
            else:
                st.text(move)
    else:
        st.info("No moves yet")
    
    st.divider()
    
    st.subheader("ℹ️ Game Info")
    st.write(f"**Turn:** {'White ⚪' if st.session_state.board.turn == chess.WHITE else 'Black ⚫'}")
    st.write(f"**Moves:** {len(st.session_state.move_history)}")
    
    # Check game status
    if st.session_state.board.is_checkmate():
        winner = "Black ⚫" if st.session_state.board.turn == chess.WHITE else "White ⚪"
        st.error(f"**Checkmate!** {winner} wins!")
    elif st.session_state.board.is_stalemate():
        st.warning("**Stalemate!** Game is a draw.")
    elif st.session_state.board.is_insufficient_material():
        st.warning("**Draw!** Insufficient material.")
    elif st.session_state.board.is_check():
        st.warning("**Check!**")

board = st.session_state.board

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Display interactive board
    move_input = components.html(
        create_interactive_board(board, st.session_state.last_move),
        height=650,
        scrolling=False
    )
    
    # Process move from interactive board
    if move_input and move_input != st.session_state.get('last_processed_move', ''):
        st.session_state.last_processed_move = move_input
        try:
            # Handle promotion (default to queen)
            move_uci = move_input
            if len(move_input) == 4:
                from_square = chess.parse_square(move_input[:2])
                to_square = chess.parse_square(move_input[2:4])
                piece = board.piece_at(from_square)
                
                # Check if it's a pawn promotion
                if piece and piece.piece_type == chess.PAWN:
                    if (piece.color == chess.WHITE and chess.square_rank(to_square) == 7) or \
                       (piece.color == chess.BLACK and chess.square_rank(to_square) == 0):
                        move_uci += 'q'  # Auto-promote to queen
            
            move = chess.Move.from_uci(move_uci)
            
            if move in board.legal_moves:
                board.push(move)
                st.session_state.board = board
                st.session_state.last_move = move
                st.session_state.move_history.append(board.san(move))
                st.success(f"✓ Move played: {board.san(move)}")
                st.rerun()
            else:
                st.error(f"❌ Illegal move: {move_input}. Please select a valid move from the highlighted squares.")
        except Exception as e:
            st.error(f"❌ Invalid move format: {move_input}. Error: {str(e)}")

with col2:
    st.subheader("📖 How to Play")
    st.markdown("""
    **Interactive Controls:**
    - 🖱️ **Click and drag** pieces to move them
    - 💡 **Hover** over a piece to see legal moves (green circles)
    - 🟨 **Yellow highlight** shows the last move made
    - ✅ Only **legal moves** are allowed
    
    **Features:**
    - Real-time move validation
    - Visual feedback for all legal moves
    - Last move highlighting
    - Move history tracking
    - Undo functionality
    - Human vs Human mode
    - Human vs AI mode (requires Stockfish)
    """)

# AI move logic (runs after human move in AI mode)
if game_mode == "Human vs AI (Extremely Difficult)" and board.turn == chess.BLACK and not board.is_game_over():
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
                        st.session_state.last_move = move
                        st.session_state.move_history.append(board.san(move))
                        st.rerun()
                    else:
                        st.error("❌ AI generated an invalid move!")
                except Exception as e:
                    st.error(f"❌ AI move error: {str(e)}")
    else:
        st.warning("⚠️ Stockfish not configured. Please set STOCKFISH_PATH in app.py to enable AI mode.")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, python-chess, and Chessboard.js")