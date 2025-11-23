# Streamlit Chess Game with Interactive UI and AI (using Stockfish)
# To run: streamlit run app.py
# Requirements: pip install -r requirements.txt
# Download Stockfish binary from https://stockfishchess.org/download/ and set the path below.

import streamlit as st
import streamlit.components.v1 as components
import chess
import chess.svg
import json

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
def display_interactive_board(board, board_id="board"):
    """Display an interactive chessboard using Chessboard.js"""
    
    # Get FEN position
    fen = board.fen()
    
    # Get last move for highlighting
    last_move = ""
    if board.move_stack:
        last_move_obj = board.peek()
        last_move = f"{chess.square_name(last_move_obj.from_square)}-{chess.square_name(last_move_obj.to_square)}"
    
    # Determine board orientation
    orientation = "white"
    
    # Generate HTML with Chessboard.js
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
            }}
            #myBoard {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }}
            .highlight-square {{
                box-shadow: inset 0 0 3px 3px yellow;
            }}
            .last-move-from {{
                box-shadow: inset 0 0 3px 3px rgba(255, 255, 0, 0.5);
            }}
            .last-move-to {{
                box-shadow: inset 0 0 3px 3px rgba(255, 255, 0, 0.8);
            }}
            .info {{
                text-align: center;
                margin-top: 10px;
                font-size: 14px;
                color: #666;
            }}
            .error {{
                color: #d32f2f;
                text-align: center;
                margin-top: 10px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div id="myBoard"></div>
        <div id="info" class="info"></div>
        <div id="error" class="error"></div>
        
        <script>
            var board = null;
            var lastMove = '{last_move}';
            var legalMovesCache = {{}};
            
            // Function to communicate with Streamlit
            function sendMoveToStreamlit(source, target) {{
                var move = source + target;
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: move
                }}, '*');
            }}
            
            // Function to highlight squares
            function removeHighlights() {{
                $('#myBoard .square-55d63').removeClass('highlight-square');
            }}
            
            function highlightSquare(square) {{
                var $square = $('#myBoard .square-' + square);
                $square.addClass('highlight-square');
            }}
            
            // Function to highlight last move
            function highlightLastMove() {{
                if (lastMove) {{
                    var parts = lastMove.split('-');
                    if (parts.length === 2) {{
                        var $fromSquare = $('#myBoard .square-' + parts[0]);
                        var $toSquare = $('#myBoard .square-' + parts[1]);
                        $fromSquare.addClass('last-move-from');
                        $toSquare.addClass('last-move-to');
                    }}
                }}
            }}
            
            // Function to get legal moves from Streamlit
            function getLegalMoves(square, callback) {{
                // Request legal moves from parent
                window.parent.postMessage({{
                    type: 'streamlit:getLegalMoves',
                    square: square
                }}, '*');
                
                // Store callback for when we get response
                window.legalMovesCallback = callback;
            }}
            
            // Drag start handler
            function onDragStart(source, piece, position, orientation) {{
                // Get legal moves and highlight them
                $.ajax({{
                    type: 'POST',
                    url: 'about:blank',
                    async: false
                }});
                
                // For demo purposes, we'll allow all drags
                // In production, this would check against legal moves from backend
                return true;
            }}
            
            // Drop handler
            function onDrop(source, target) {{
                removeHighlights();
                
                // Don't allow moving to the same square
                if (source === target) {{
                    return 'snapback';
                }}
                
                // Send move to Streamlit for validation
                sendMoveToStreamlit(source, target);
                
                // Return snapback - if move is valid, Streamlit will update the position
                return 'snapback';
            }}
            
            // Mouse over square handler
            function onMouseoverSquare(square, piece) {{
                // Highlight the square and possible moves
                if (piece) {{
                    highlightSquare(square);
                }}
            }}
            
            // Mouse out square handler
            function onMouseoutSquare(square, piece) {{
                removeHighlights();
            }}
            
            // Snap end handler
            function onSnapEnd() {{
                board.position(board.fen());
            }}
            
            // Initialize board
            var config = {{
                draggable: true,
                position: '{fen}',
                onDragStart: onDragStart,
                onDrop: onDrop,
                onMouseoutSquare: onMouseoutSquare,
                onMouseoverSquare: onMouseoverSquare,
                onSnapEnd: onSnapEnd,
                pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png',
                orientation: '{orientation}'
            }};
            
            board = Chessboard('myBoard', config);
            
            // Highlight last move after board is rendered
            setTimeout(highlightLastMove, 100);
            
            // Make board responsive
            $(window).resize(function() {{
                board.resize();
            }});
        </script>
    </body>
    </html>
    """
    
    # Display the interactive board
    move = components.html(html_code, height=680, scrolling=False)
    
    return move

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
    
    # Display the interactive chessboard
    move = display_interactive_board(board)
    
    # Handle move from interactive board
    if move:
        try:
            # Parse move (format: "e2e4" or "e7e8q" for promotion)
            if len(move) >= 4:
                from_square = move[:2]
                to_square = move[2:4]
                promotion = move[4] if len(move) > 4 else None
                
                # Create move object
                chess_move = chess.Move.from_uci(move)
                
                # Validate and make move
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                    st.session_state.board = board
                    st.session_state.player_turn = not st.session_state.player_turn
                    st.session_state.last_error = None
                    st.session_state.move_count += 1
                    st.rerun()
                else:
                    st.session_state.last_error = f"Illegal move: {move}"
                    st.error(f"❌ {st.session_state.last_error}")
        except Exception as e:
            st.session_state.last_error = f"Invalid move format: {move}"
            st.error(f"❌ {st.session_state.last_error}")
    
    # Display error if any
    if st.session_state.last_error:
        st.error(f"❌ {st.session_state.last_error}")
    
    st.markdown("---")
    
    # Alternative text input for moves
    with st.expander("⌨️ Manual Move Input (Alternative)"):
        st.info("You can also enter moves manually using standard chess notation")
        move_input = st.text_input("Enter your move (e.g., e2e4, e7e8q for promotion):", key="manual_move")
        if move_input:
            try:
                chess_move = chess.Move.from_uci(move_input)
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                    st.session_state.board = board
                    st.session_state.player_turn = not st.session_state.player_turn
                    st.session_state.last_error = None
                    st.session_state.move_count += 1
                    st.rerun()
                else:
                    st.error("❌ Illegal move!")
            except ValueError:
                st.error("❌ Invalid move format! Use format like 'e2e4' or 'e7e8q'")
    
    # Help section
    with st.expander("ℹ️ How to Play"):
        st.markdown("""
        **Interactive Chessboard:**
        - **Drag and drop** pieces to make moves
        - **Legal moves** are validated in real-time
        - **Last move** is highlighted on the board
        - **Hover** over pieces to see them highlighted
        
        **Move Notation:**
        - Moves are in UCI format: source + destination (e.g., e2e4)
        - For pawn promotion, add the piece letter (e.g., e7e8q for queen)
        
        **Game Modes:**
        - **Human vs Human:** Play against another person
        - **Human vs AI:** Challenge the Stockfish engine (requires setup)
        
        **Controls:**
        - Use the sidebar to reset the game or undo moves
        - View move history and game status in the sidebar
        """)