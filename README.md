# Monopoly (Ursina)

3D Monopoly board prototype built with the **Ursina** game engine.

## Run

From the repo root:

```bash
python main.py
```

Notes:
- Run from the repo root so Ursina can find `assets/`.
- The current game starts in fullscreen.

## Requirements

This project is a Python app using Ursina (Panda3D).

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Assets

- Board texture(s): `assets/Board1.jpg`, `assets/Printables.jpg`, etc.
- Dice model: `assets/pieces/models/dice.glb`
- Piece textures/gifs: `assets/pieces/textuers/`

## Controls

- `Space`: Roll dice
- `M`: Move by 1 (debug)
- `1`: Standard camera view (animated)
- `2`: Top-down camera view (animated)
- `3`: Rotate board
- `4`: Toggle board texture (Mario / Classic)
- `Escape`: Quit (with a surprise)

## Project Structure

The project has been refactored into a modular structure:

- `main.py`: Entry point. Initializes the app and entities.
- `game.py`: Core game logic (`Main` class).
- `board.py`: Board generation and rendering.
- `player.py`: Player pieces.
- `camera.py`: Camera controls (uses smooth animations).
- `dice.py`: Dice physics.
- `ui.py`: UI management.
- `card.py`: Card data structure.
