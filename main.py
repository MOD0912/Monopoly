import ursina as ur 
import threading 

import time

app = ur.Ursina(fullscreen=False)
class Main(ur.Entity):
    '''
    Meant to be the father of them all. Forced to be the class pulling the strings
    '''
    def __init__(self):
        super().__init__()
        self.players = []
        self.current_player = 0
        self.tile_positions = self.generate_tile_positions()

    def generate_tile_positions(self) -> ur.Vec3:
        '''
        Generate the 3D positions for each of the 40 Monopoly tiles around the board.
        Returns a list of Vec3 positions.
        '''
        # 40 tiles total. 
        # Using LOCAL coordinates relative to the board parent.
        # Board scale is (8, 0.1, 8). 
        # World 3.5 -> Local 3.5/8 = 0.4375
        
        c = 0.4375 # Corner constant (3.5 / 8)
        y = 2.5    # Height constant (0.25 / 0.1)
        
        # Calculate step sizes based on tile widths
        # Standard Monopoly ratio: Corner tiles are wider than property tiles
        # Approx ratio K = Width_Corner / Width_Prop ≈ 1.55 to 1.63
        k = 1.63 
        
        # Distance calculation:
        # Distance center-to-center from Corner to Prop 1 = (W_c + W_p) / 2 = W_p * (k + 1) / 2
        # Distance center-to-center from Prop to Prop = W_p
        # Total Side Length (center-to-center corner) = 2 * Step_Corner + 8 * Step_Prop
        # Total = 2 * (W_p * (k+1)/2) + 8 * W_p 
        # Total = W_p * (k + 1) + 8 * W_p = W_p * (k + 9)
        
        total_span = 2 * c
        w_p = total_span / (k + 9) # Property width unit
        
        step_corner = w_p * (k + 1) / 2
        step_normal = w_p
        
        offsets = [0.0] * 11
        current = 0.0
        for i in range(1, 11):
            if i == 1 or i == 10:
                dist = step_corner
            else:
                dist = step_normal
            current += dist
            offsets[i] = current

        positions = []
        
        # Side 1: Bottom (Go -> Jail) - Right to Left
        # Start at (c, y, -c)
        for i in range(11):
            positions.append(ur.Vec3(c - offsets[i], y, -c))
            
        # Side 2: Left (Jail -> Free Parking) - Bottom to Top
        # Start at (-c, y, -c). Note offsets start from corner.
        for i in range(1, 11):
            positions.append(ur.Vec3(-c, y, -c + offsets[i]))
            
        # Side 3: Top (Free Parking -> Go To Jail) - Left to Right
        # Start at (-c, y, c)
        for i in range(1, 11):
            positions.append(ur.Vec3(-c + offsets[i], y, c))
            
        # Side 4: Right (Go To Jail -> Go) - Top to Bottom
        # Start at (c, y, c)
        for i in range(1, 10):
            positions.append(ur.Vec3(c, y, c - offsets[i]))
            
        return positions

    def move_bitch(self, amount):
        '''
        Move the current player piece by a specified amount of tiles.
        '''
        print(f"""
            players: {self.players}
            amount: {amount}
              """)
        th = threading.Thread(target=self.move, args=(amount,))
        th.start()

    def spawn_piece(self, piece_type="cube", texture="1e5.jpeg"):
        '''
        Spawn a new player piece on the board.
        '''
        if texture.endswith("gif"):
            player = Animated_Piece(piece_type=piece_type, texture=texture)
        else:
            player = Player_Piece(piece_type=piece_type, texture=texture)
        self.players.append(player)

    def move(self, amount):
        curr_player = self.players[self.current_player]
        self.current_player = (self.current_player + 1) % len(self.players)
        step_duration = 0.5
        
        jump_height = 7.5
        
        for i in range(amount):
            curr_player.tile_position = (curr_player.tile_position + 1) % 40
            
            target_pos = self.tile_positions[curr_player.tile_position]
            
            curr_player.animate_y(jump_height, duration=step_duration/2, curve=ur.curve.out_sine)
            curr_player.animate_position(
                (target_pos.x, jump_height, target_pos.z), 
                duration=step_duration/2, 
                curve=ur.curve.linear
            )
            
            time.sleep(step_duration/2)
            
            curr_player.animate_position(target_pos, duration=step_duration/2, curve=ur.curve.in_sine)
            time.sleep(step_duration/2)
    
    def display_gif(self):
        '''
        Mario is the mastermind behind this game. He gets angry if you try to exit the game.
        '''
        x = ur.Animation(name="mario-super-mario-64.gif", parent=ur.camera, position=(0,0,2), scale=(1.456, 0.91))
        x.pause()
        ur.invoke(x.start, delay=0.7)
        print(x.__sizeof__())
        print(x.world_scale)
        ur.invoke(ur.application.quit, delay=3.7)



class Player_Piece(ur.Entity):
    '''
    Basic non-animated player piece.'''
    def __init__(self, piece_type="cube", texture="1e5.jpeg", start_position = (3.5, 0.25, -3.5)):
        self.start_position = start_position
        super().__init__(
            parent=board,
            model=piece_type,
            #color=ur.color.black,
            texture=texture,
            world_position=(
                self.start_position[0],
                self.start_position[1],
                self.start_position[2] 
            ),
            world_scale=0.5
        )
        self.tile_position = 0




class Animated_Piece(ur.Animation):
    '''
    Animated player piece using a gif texture.
    '''
    def __init__(self, piece_type="cube", texture="1e5.jpeg", start_position = (3.5, 0.25, -3.5)):
        self.start_position = start_position
        super().__init__(
                parent=board,
                model=piece_type, 
                name=texture, 
                world_position=(
                    self.start_position[0],
                    self.start_position[1],
                    self.start_position[2] 
                ),                
                world_scale=0.5
                )
        self.tile_position = 0


    
class Board(ur.Entity):
    '''
    Destined to be the father of them all. 
    '''
    def __init__(self, position=(0,0,0), scale=(1,1,1), color=ur.color.white):
        super().__init__(
            model="plane",
            texture="Board1",
            scale=scale,
            color=color,
            position=position
        )
        
        self._rotating = False
    
    def rotate_board(self):
        if self._rotating:
            return

        self._rotating = True
        duration = 0.35
        target_y = self.rotation_y - 90
        self.animate_rotation_y(target_y, duration=duration, curve=ur.curve.in_out_sine)
        ur.invoke(setattr, self, "_rotating", False, delay=duration)



class Camera(ur.Entity):
    '''
    Controls the camera movement and views.
    '''
    def __init__(self):
        super().__init__()

    def standard_camera(self):
        while ur.camera.z > -22.5:
            ur.camera.z -= 0.01
            if ur.camera.y > 10:
                ur.camera.y -= 0.0045
            ur.time.sleep(0.0005)
    
    def top_down_camera(self):
        while ur.camera.z < 0:
            if ur.camera.y < 20:
                ur.camera.y += 0.0045
            ur.camera.z += 0.01
            ur.time.sleep(0.0005)

    def update(self):

        ur.camera.look_at((0,0,0))
    
    def input(self, key):
        if key == "1":
            th = threading.Thread(target=self.standard_camera)
            th.start()
        if key == "2":
            th = threading.Thread(target=self.top_down_camera)
            th.start()
        if key == "3":
            board.rotate_board()
        if key == "4":
            tex = str(board.texture)
            if tex == "mario.gif":
                board.texture = "Board1.jpg"
            else:
                board.texture = "mario.gif"



class Dice(ur.Entity):
    '''
    Simulates two dice with basic physics.
    '''
    def __init__(self, scale=0.25):
        super().__init__()
        self.dice_1 = ur.Entity(
            model="dice",
            world_position=(0, 20, 0),
            world_scale=scale,
            ani=False
        )
        self.dice_2 = ur.Entity(
            model="dice",
            world_position=(2, 20, 0),
            world_scale=scale,
            top_value=6,
            ani=False
        )

        self.dices = [self.dice_1, self.dice_2]
        self.cunt = 0

        
        for dice in self.dices:
            dice.velocity = ur.Vec3(0, 0, 0)
            dice.angular_velocity = ur.Vec3(0, 0, 0)
            dice.rolling = False

    def throw_dice(self):
        '''
        trhow em dices
        '''
        for i in self.dices:
            # Start position high up
            i.position = (ur.random.uniform(-2, 2), 5, ur.random.uniform(-2, 2))
            
            # Random initial rotation
            i.rotation = (ur.random.uniform(0, 360), ur.random.uniform(0, 360), ur.random.uniform(0, 360))
            
            # Physics initialization
            # Downward velocity + some random horizontal velocity
            i.velocity = ur.Vec3(
                ur.random.uniform(-3, 3), 
                ur.random.uniform(-2, 0), 
                ur.random.uniform(-3, 3)
            )
            
            # Random spin
            i.angular_velocity = ur.Vec3(
                ur.random.uniform(-500, 500), 
                ur.random.uniform(-500, 500), 
                ur.random.uniform(-500, 500)
            )
            
            i.rolling = True

    def move_b(self):
        '''
        move
        '''
        values = self.read_values()
        amount = values[0] + values[1]

        main.move_bitch(amount)
        dice.cunt = 0 


    def input(self, key):
        if key == "space":
            self.throw_dice()
        if key == "m":
            main.move_bitch(1)

    def update(self):
        dt = ur.time.dt
        gravity = 15 # Adjust gravity strength
        ground_level = 0.2 # Approximate floor level
        

        for i in self.dices:
            if i.ani:
                x = round(i.rotation.z / 90) * 90
        
            if not i.rolling:
                continue

            # Apply gravity
            i.velocity.y -= gravity * dt

            # Update position and rotation
            i.position += i.velocity * dt
            i.rotation += i.angular_velocity * dt
            # Ground collision
            if i.y <= ground_level:
                i.y = ground_level
                
                # Check if we should stop
                if abs(i.velocity.y) < 1 and i.velocity.x**2 + i.velocity.z**2 < 1:
                    i.rolling = False
                    i.ani = True
                    i.velocity = ur.Vec3(0,0,0)
                    i.angular_velocity = ur.Vec3(0,0,0)
                    # Snap to nearest face *smoothly*.
                    target_rot = (
                        round(i.rotation_x / 90) * 90,
                        i.rotation_y,
                        round(i.rotation_z / 90) * 90,
                    )
                    i.animate_rotation(target_rot, duration=0.2, curve=ur.curve.out_sine)
                    self.cunt += 1
                    
                    

                # Bounce
                i.velocity.y *= -0.6 # Restitution
                
                # Friction
                i.velocity.x *= 0.7
                i.velocity.z *= 0.7
                i.angular_velocity *= 0.7
            
            # Optional: Wall collisions (keep on board)
            if abs(i.x) > 4:
                i.x = MAX_X = 4 if i.x > 0 else -4
                i.velocity.x *= -0.8
            
            if abs(i.z) > 4:
                i.z = MAX_Z = 4 if i.z > 0 else -4
                i.velocity.z *= -0.8
            
            if dice.cunt == 2:
                ur.invoke(self.move_b, delay=0.1)


    def read_values(self):
        '''
        read values of the dice
        '''
        values = []
        for i in self.dices:
            face_values = {
                "up": 1,      # Local +Y (Top)
                "down": 6,    # Local -Y (Bottom)
                "forward": 3, # Local +Z (Front)
                "back": 4,    # Local -Z (Back)
                "right": 2,   # Local +X (Right) 
                "left": 5     # Local -X (Left)  
            }

            # Get the direction vectors in world space
            vectors = {
                "up": i.up,
                "down": i.down,
                "forward": i.forward,
                "back": i.back,
                "right": i.right,
                "left": i.left
            }
            
            # Find which local vector is most aligned with global up (0,1,0)
            # Since global up is the Y axis, we just look for the max Y component
            facing_up = max(vectors, key=lambda k: vectors[k].y)
            values.append(face_values[facing_up])
        print(values)
        return values
        
cam = Camera()


ground = ur.Entity(
    model="plane",
    #texture="mario_dark.gif",
    scale=(20,1,20),
    color=ur.color.gray,
    position=(0,-0.1,0)
)


ur.camera.position = (0, 10, -22.5)
ur.camera.rotation_x = 22.5
board = Board(scale=(8,0.1,8))
main = Main()

piece1 = main.spawn_piece("cube", texture="1e5.jpeg")
piece2 = main.spawn_piece("cube", texture="mario-super-mario-64.gif")
main.pieces = [piece1, piece2]
dice = Dice()

ur.window.exit_button.on_click_setter(main.display_gif)


app.run()