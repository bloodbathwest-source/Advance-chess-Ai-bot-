# ♟️ Advanced Interactive Chess Game with AI

An elegant, feature-rich chess application built with Streamlit and python-chess, featuring an interactive drag-and-drop interface, real-time move validation, and a powerful AI opponent powered by Stockfish.

![Chess Game](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🎮 Interactive Chessboard
- **Drag-and-drop piece movement** - Intuitive click-and-drag interface using Chessboard.js
- **Visual move highlighting** - See all legal moves when you hover over or select a piece
- **Last move indicator** - Yellow highlighting shows the most recent move made
- **Real-time validation** - Every move is validated instantly by the backend

### 🎯 Game Modes
- **Human vs Human** - Play against a friend on the same device
- **Human vs AI** - Challenge a powerful Stockfish-based AI (requires Stockfish installation)

### 🛡️ Smart Features
- **Real-time move validation** - Only legal moves are allowed
- **Descriptive error messages** - Clear feedback when moves are invalid
- **Move history tracking** - Complete game notation in the sidebar
- **Undo functionality** - Take back moves to explore different strategies
- **Game status indicators** - Visual alerts for check, checkmate, stalemate, and draws

### 🎨 User Interface
- **Modern, responsive design** - Clean layout with sidebar controls
- **Visual feedback** - Hover effects, highlights, and status indicators
- **Move counter** - Track the game progress
- **Turn indicator** - Always know whose turn it is

## 📋 Requirements

- Python 3.8 or higher
- Streamlit 1.28.0+
- python-chess 1.999+
- Stockfish 3.28.0+ (Python package)
- Stockfish Chess Engine binary (for AI mode only)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/bloodbathwest-source/Advance-chess-Ai-bot-.git
cd Advance-chess-Ai-bot-
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: (Optional) Install Stockfish for AI Mode

To enable the AI opponent, you need to download the Stockfish chess engine:

1. **Download Stockfish:**
   - Visit [Stockfish Downloads](https://stockfishchess.org/download/)
   - Download the appropriate version for your operating system
   - Extract the downloaded file

2. **Configure the path:**
   - Open `app.py` in a text editor
   - Update the `STOCKFISH_PATH` variable with the path to your Stockfish binary:
   
   ```python
   # Example paths:
   # Windows: STOCKFISH_PATH = "C:/stockfish/stockfish.exe"
   # Mac: STOCKFISH_PATH = "/usr/local/bin/stockfish"
   # Linux: STOCKFISH_PATH = "/usr/games/stockfish"
   STOCKFISH_PATH = "path/to/your/stockfish/binary"
   ```

## 🎮 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### How to Play

1. **Select Game Mode:**
   - Choose between "Human vs Human" or "Human vs AI" from the sidebar

2. **Make Moves:**
   - **Click and drag** any piece to move it
   - **Hover over pieces** to see available legal moves (shown as green circles)
   - **Invalid moves** are prevented automatically

3. **Game Controls:**
   - **Reset Game** - Start a new game
   - **Undo Move** - Take back the last move
   - **Move History** - View all moves in standard chess notation

4. **Visual Indicators:**
   - 🟨 **Yellow squares** = Last move made
   - 🟢 **Green circles** = Legal destination squares
   - ⚪ **White's turn** or ⚫ **Black's turn** shown in sidebar

### Playing Against the AI

The AI opponent (when Stockfish is configured) provides a challenging game:
- **Difficulty:** Extremely Difficult (Depth 18)
- **Strength:** ~2800 ELO rating
- **Think Time:** 1-5 seconds per move
- **Features:** Multi-threaded analysis with 2GB hash table

## 📁 Project Structure

```
Advance-chess-Ai-bot-/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── LICENSE            # MIT License
```

## 🔧 Technical Details

### Architecture

The application uses a modern architecture combining:
- **Backend:** Python with python-chess for game logic and move validation
- **Frontend:** Streamlit for the web interface
- **Interactive Board:** Chessboard.js for drag-and-drop functionality
- **AI Engine:** Stockfish for computer opponent

### Key Components

1. **Game State Management:**
   - Streamlit session state maintains board position
   - Move history tracking with full notation
   - Last move highlighting for visual continuity

2. **Move Validation:**
   - All moves validated using python-chess legal move generation
   - Real-time feedback for invalid attempts
   - Automatic pawn promotion to queen

3. **Interactive Board:**
   - Chessboard.js provides drag-and-drop interface
   - JavaScript-Python communication via Streamlit components
   - Dynamic legal move highlighting
   - Visual feedback for selections and moves

## 🎨 Customization

### Changing Board Size

Edit the board width in `create_interactive_board()` function:

```javascript
#myBoard {
    width: 500px;  // Change this value
    margin: 20px auto;
}
```

### Adjusting AI Difficulty

Modify the Stockfish parameters in `get_stockfish()`:

```python
def get_stockfish():
    return Stockfish(
        path=STOCKFISH_PATH,
        depth=18,  # Increase for harder (10-20 range)
        parameters={
            "Threads": 4,  # CPU threads to use
            "Hash": 2048   # Memory in MB
        }
    )
```

### Color Schemes

Customize the highlighting colors in the HTML template:

```css
.legal-move {
    background: radial-gradient(circle, rgba(0,128,0,0.3) 25%, transparent 25%);
}
.last-move {
    background-color: rgba(255, 255, 0, 0.4) !important;
}
```

## 🐛 Troubleshooting

### Common Issues

**Issue:** "Stockfish not configured" warning
- **Solution:** Install Stockfish binary and update `STOCKFISH_PATH` in `app.py`

**Issue:** Board doesn't load or appears blank
- **Solution:** Check internet connection (Chessboard.js loads from CDN)
- **Alternative:** Download Chessboard.js locally and update paths

**Issue:** Moves not registering
- **Solution:** Ensure you're clicking and dragging pieces (not clicking twice)
- **Check:** Verify it's the correct player's turn

**Issue:** AI takes too long to move
- **Solution:** Reduce `depth` parameter in `get_stockfish()` (try 12-15)

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **python-chess** - Comprehensive chess library for Python
- **Streamlit** - Framework for building data apps
- **Chessboard.js** - JavaScript chessboard component
- **Stockfish** - Powerful open-source chess engine
- **Chess.com** - Inspiration for UI/UX features

## 📧 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

---

**Enjoy playing chess!** ♟️🎮
