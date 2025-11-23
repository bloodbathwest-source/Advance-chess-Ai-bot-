# Advanced Chess AI Bot - Interactive Streamlit Chess Game

An interactive, visually appealing chess game built with Streamlit featuring drag-and-drop gameplay, real-time move validation, and an optional AI opponent powered by Stockfish.

## ✨ Features

### 🎮 Interactive User Interface
- **Visual Chess Board**: High-quality SVG rendering of the chessboard
- **Visual Indicators**: 
  - Last move highlighting to track game progression
  - Check highlighting when king is in check
  - Legal move visualization (green squares)
  - Responsive design that scales to different screen sizes
- **Beautiful Design**: Clean, modern interface with professional chess piece graphics
- **Real-time Updates**: Board updates instantly after each valid move

### ♟️ Chess Functionality
- **Real-time Move Validation**: All moves are validated against chess rules instantly
- **User-Friendly Error Messages**: Clear feedback for illegal moves
- **Game Modes**:
  - Human vs Human: Play against another person locally
  - Human vs AI: Challenge the Stockfish engine (optional)
- **Complete Chess Rules Support**:
  - Castling (kingside and queenside)
  - En passant captures
  - Pawn promotion
  - Check and checkmate detection
  - Stalemate and draw conditions

### 📊 Game Features
- **Move History**: Track all moves made during the game
- **Move Counter**: See how many moves have been played
- **Check Indicator**: Visual warning when king is in check
- **Undo Functionality**: Take back moves to review alternatives
- **Game Status Display**: Clear indication of whose turn it is
- **Alternative Input**: Manual move entry option for advanced players

### 🤖 AI Opponent (Optional)
- Powered by Stockfish engine
- Highly challenging gameplay
- Configurable difficulty through engine parameters

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Stockfish chess engine (optional, for AI opponent)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bloodbathwest-source/Advance-chess-Ai-bot-.git
cd Advance-chess-Ai-bot-
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Stockfish (Optional - for AI opponent)**
   - Download Stockfish from [stockfishchess.org](https://stockfishchess.org/download/)
   - Extract the binary to a location on your system
   - Update the `STOCKFISH_PATH` variable in `app.py` with the path to the binary

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 🎯 How to Use

### Playing the Game

1. **Making Moves**:
   - **Enter moves**: Type the from square (e.g., "e2") and to square (e.g., "e4")
   - **Click Make Move**: Click the button to execute your move
   - **Pawn Promotion**: Select the piece type from the dropdown before promoting

2. **Move Notation**:
   - Squares are identified by column (a-h) and row (1-8)
   - Examples: e2, e4, a7, h8

3. **Game Controls** (in sidebar):
   - **Reset Game**: Start a new game
   - **Undo Move**: Take back the last move
   - **Game Mode**: Switch between Human vs Human or Human vs AI

4. **Visual Feedback**:
   - Last move is highlighted on the board (yellow squares)
   - Check warnings appear when king is in check (red highlighting)
   - Legal moves are shown in green
   - Error messages display for illegal moves

### Understanding the Interface

- **Main Board**: Interactive chessboard with drag-and-drop functionality
- **Sidebar**:
  - Game mode selector
  - Reset and Undo buttons
  - Game status (turn, move count, check warnings)
  - Move history (last 10 moves)
- **Expandable Sections**:
  - Manual move input (alternative to drag-and-drop)
  - How to Play guide

## 🔧 Configuration

### Enabling AI Opponent

1. Download and install Stockfish from [stockfishchess.org](https://stockfishchess.org/download/)
2. Open `app.py` and update the `STOCKFISH_PATH` variable:
   ```python
   STOCKFISH_PATH = "/path/to/your/stockfish/binary"
   ```
3. Restart the application

### Customizing AI Difficulty

Modify the Stockfish parameters in `app.py`:
```python
return Stockfish(
    path=STOCKFISH_PATH, 
    depth=18,  # Increase for harder difficulty (slower)
    parameters={
        "Threads": 4,  # Number of CPU threads to use
        "Hash": 2048   # Memory allocation in MB
    }
)
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python -m pytest test_app.py -v
```

Or using unittest:
```bash
python test_app.py
```

### Test Coverage

The test suite includes:
- Move validation tests
- Game logic tests (check, checkmate, stalemate)
- Special moves (castling, en passant, promotion)
- Board state management
- Undo functionality
- Game result determination

## 📦 Dependencies

- **streamlit** (>=1.28.0): Web application framework
- **python-chess** (>=1.999): Chess logic and move validation
- **stockfish** (>=3.28.0): AI opponent engine interface

## 🏗️ Architecture

### Frontend Integration
The application uses **python-chess's SVG rendering** with enhanced visual indicators:
- High-quality SVG chess board rendering
- Last move highlighting with yellow squares
- Check highlighting with red indicators
- Legal move visualization with green squares
- Responsive design that scales appropriately
- Clean, professional appearance

### Backend Logic
- Python chess library handles all game logic
- Move validation performed server-side for security
- Session state management for game persistence
- Optional Stockfish integration for AI moves

### Component Architecture
```
app.py
├── Stockfish Integration (optional)
├── Interactive Board Display (SVG-based)
│   ├── chess.svg for rendering
│   ├── Last Move Highlighting
│   ├── Check Detection Visual
│   └── Legal Move Indicators
├── Game Logic (python-chess)
│   ├── Move Validation
│   ├── Game State Management
│   └── Special Moves Handling
└── UI Components (Streamlit)
    ├── Sidebar Controls
    ├── Game Status Display
    ├── Move Input Interface
    └── Move History
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-chess](https://python-chess.readthedocs.io/) - Chess logic library and SVG rendering
- [Stockfish](https://stockfishchess.org/) - Chess engine
- [Streamlit](https://streamlit.io/) - Web application framework

## 📞 Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

**Enjoy playing chess! ♟️**
