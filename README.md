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

What’s included in `requirements.txt`:
- Core runtime: `ursina` (brings in Panda3D)
- Tooling (only needed for `tools/` scripts): `Pillow`, `opencv-python`, `numpy`

## Assets

- Board texture(s): `assets/Board1.jpg`, `assets/Printables.jpg`, etc.
- Dice model: `assets/pieces/models/dice.glb`
- Piece textures/gifs: `assets/pieces/textuers/`

## Controls (current)

- `Space`: throw dice
- `M`: move by 1 (debug)
- `1`: camera standard view motion
- `2`: camera top-down view motion
- `3`: rotate board
- `4`: toggle board texture

## Repo layout

- `main.py`: main game prototype / entrypoint
- `tools/extract_printables.py`: extracts/crops assets from `assets/Printables.jpg`
- `tools/process_textures.py`: batch background replacement / rotation for card textures

## Known rough edges

- The code is prototype-quality (threading + sleeps drive some animation).
- Some naming/paths are inconsistent (e.g. `textuers/`).
