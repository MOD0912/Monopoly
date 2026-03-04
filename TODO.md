# TODO

## Gameplay

- Implement real player turns (roll → move → resolve tile → end turn).
- Add property ownership + rent + houses/hotels.
- Add Chance / Community Chest decks and effects.
- Add jail rules (doubles, pay fine, cards).
- Add trading and mortgaging.

## UI / UX

- Replace debug prints with on-screen messages.
- Show current player, last roll, and tile details.
- Make Buy/Auction actually affect ownership + money.

## Code health

- Remove/contain threading in movement (prefer Ursina timing / invoke patterns).
- Split `main.py` into modules (board, pieces, dice, ui, game_state).
- Add a minimal config file for things like fullscreen, player count, asset paths.

## Assets / pipeline

- Fix folder naming (`assets/pieces/textuers` → `textures`) and update references.
- Add a repeatable way to generate tile/card textures (document `tools/` scripts).
- Consider adding a `requirements.txt` for reproducible installs.
