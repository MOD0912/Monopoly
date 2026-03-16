import ursina as ur
ai = True
try:
    from ai_service import AIService # Use separate process for AI
except ImportError:
    ai = False
    print("Noob")
import atexit
from game import Main
from board import Board
from camera import Camera
from ui import UI
from dice import Dice
from ursina.shaders import unlit_shader

# #tf.keras.models.load_model('mt.h5') # Load the trained model (adjust path as needed)
app = ur.Ursina(fullscreen=True)

# Start AI Service in background process
if ai:
    ai_service = AIService()
    ai_service.start()


# Make sure to stop AI service when closing app (simple way)
if ai:
    atexit.register(ai_service.stop)

# Create Ground
ground = ur.Entity(
    model="plane",
    scale=(20,1,20),
    color=ur.color.gray,
    position=(0,-0.1,0),
    shader = unlit_shader
)

# Initialize Components
ur.camera.position = (0, 10, -12.5)

# 1. Create Board
board = Board(scale=(8,0.1,8), texture=None, map="Map1") #

# 2. Create Camera (needs board)
cam = Camera(board_instance=board)

# 3. Create UI
ui = UI()

# 4. Create Game Logic (needs board, cam, ui)
main = Main(board, cam, ui)

# 5. Create Dice (needs game)
dice = Dice(game_instance=main)
main.set_dice(dice) # Link dice back to main

# --- Setup Players ---
# piece1 = main.spawn_piece("cube", texture="1e5.jpeg")

for i in range(1):
    piece1 = main.spawn_piece("cube", texture="Bobux_r_bg")
    piece2 = main.spawn_piece("cube", texture="mario-super-mario-64.gif")
    #piece3 = main.spawn_piece("cube", texture="eis-futzi.png")

# Update UI with players
for i in main.players:
    ui.add_player_info(i)

# Exit handler
ur.window.exit_button.on_click_setter(main.display_gif)

if ai:
    ai_service.predict("Guter Zug!")

    # Checking for response (in your update loop):
    result = ai_service.check_result()
if result:
    prompt, response = result
    print(f"Prompt: {prompt}\n"*20)
    print(f"AI says: {response}")
    # Show in UI...

# Run
app.run()

