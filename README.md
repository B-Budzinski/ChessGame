# Chess Game

A feature-rich chess game implementation in Python using Pygame, offering a complete chess playing experience with a graphical user interface.

## Features

- Complete chess rules implementation
- Interactive graphical user interface
- Legal move validation
- Pawn promotion
- Move undoing (using 'z' key)
- Game state logging
- Piece highlighting and move visualization

## Requirements

- Python 3.x
- Pygame 2.6.1

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ChessGame
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

To start the game, run:
```bash
python main.py
```

## How to Play

- Click on a piece to select it
- Click on a valid destination square to make a move
- Double-click a square to deselect the piece
- Press 'z' to undo the last move
- When a pawn reaches the opposite end of the board, a promotion dialog will appear

## Project Structure

```
ChessGame/
├── images/          # Chess piece images
├── src/             # Source code
│   ├── constants.py         # Game constants and configurations
│   ├── game_engine.py      # Core game logic
│   ├── move_validation.py  # Move validation rules
│   ├── moves.py           # Move handling
│   ├── resource_manager.py # Resource loading and management
│   └── ui_renderer.py     # UI rendering and display
├── main.py          # Main game entry point
└── requirements.txt # Project dependencies
```

## Logging

The game includes comprehensive logging functionality that records:
- Game start and termination
- Move attempts and validation
- Invalid moves and errors

Logs are written to both the console and `app.log` file.

## Contributing

Not accepting contributions as this is a personal project, but if you'd like to contribute please reach out.