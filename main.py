import ursina as ur 
import threading 
from ursina.shaders import unlit_shader
import time

app = ur.Ursina(fullscreen=True)
class Main(ur.Entity):
    '''
    Meant to be the father of them all. Forced to be the class pulling the strings
    '''
    def __init__(self):
        super().__init__()
        self.players = []
        self.current_player = 0
        self.tile_positions = self.generate_tile_positions()
        # Simple custom tween state for the card display (avoids animate_position/animate_rotation).
        self._card_tween = None
        self._card_tween_on_done = None
        ur.Text.size=0.05
        self.buy = ur.Button(parent=ur.camera.ui, text="Buy", color=ur.color.blue, position=(-0.115, -0.4), scale=(0.115*2, 0.1), on_click=self.buy_property, enabled=False)
        self.auction = ur.Button(parent=ur.camera.ui, text="Auction", color=ur.color.white, position=(0.115, -0.4), scale=(0.115*2, 0.1), on_click=self.auction_property, enabled=False, text_color=ur.color.black)

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

    def move_bitch(self, amount, double=False):
        '''
        Move the current player piece by a specified amount of tiles.
        '''
        print(f"""
            players: {self.players}
            amount: {amount}
              """)
        
        th = threading.Thread(target=self.move, args=(amount, double))
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
        return player

    def move(self, amount, double=False):
        curr_player = self.players[self.current_player]
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

        if double:
            ur.invoke(dice.throw_dice)
        else:
            ur.invoke(self.show_card, board.cards[curr_player.tile_position])
            self.current_player = (self.current_player + 1) % len(self.players)

            
    
    def display_gif(self):
        '''
        Mario is the mastermind behind this game. He gets angry if you try to exit the game.
        '''
        x = ur.Animation(name="mario-super-mario-64.gif", parent=ur.camera, position=(0,0,2), scale=(1.456, 0.91))
        print("You can't escape Mario's wrath!")
        print(x.world_position)
        x.pause()
        ur.invoke(x.start, delay=0.7)
        ur.invoke(ur.application.quit, delay=3.7)
    
    def show_card(self, card_name):
        '''
        Show a card on the UI. Meant to be used for Chance and Community Chest cards.
        '''
        # Placeholder implementation
        if card_name[0] in ["Income Tax", "Luxury Tax", "Go To Jail", "Free Parking", "Jail", "Start"]:
            return
        
        print(f"Showing card: {card_name}")

        card_ent = card_name[2]
        self.temp_card = card_ent

        # Store original transform so we can put the tile back exactly.
        self.temp_parent = card_ent.parent
        self.temp_position = card_ent.position
        self.temp_rotation = card_ent.rotation
        self.temp_scale = card_ent.scale
        self.temp_world_position = card_ent.world_position
        self.temp_world_rotation = card_ent.world_rotation

        # Move into camera-space for a stable "UI-like" animation.
        card_ent.world_parent = ur.camera
        card_ent.always_on_top = True

        # Tween to a fixed spot in front of the camera (manual, dt-based).
        self._card_tween = {
            'entity': card_ent,
            't': 0.0,
            'duration': 1.0,
            'start_pos': ur.Vec3(card_ent.position),
            'end_pos': ur.Vec3(0, -0.11, 3) if self.temp_card.bar_color != None else ur.Vec3(0, 0.02, 3),
            'start_rot': ur.Vec3(card_ent.rotation),
            'end_rot': ur.Vec3(-90 , 0, 0),
            'curve': ur.curve.out_sine,
        }
        self._card_tween_on_done = None
        print(ur.camera.rotation)
        cam.look_at_board = False
        cam.look_at_card()
        #ur.invoke(cam.return_to_board_view, delay=2.0)
        ur.invoke(self.interact_with_card, delay=1.0 )
        #ur.camera.animate_rotation((0, 0, 0), duration=1.0, curve=ur.curve.linear)
        #ur.invoke(self.return_to_origin, delay=3)

    def return_to_origin(self):

        # Return in world space, then reattach to the board hierarchy.
        self.temp_card.world_parent = ur.scene

        # Tween back to the original world transform.
        self._card_tween = {
            'entity': self.temp_card,
            't': 0.0,
            'duration': 1.0,
            'start_pos': ur.Vec3(self.temp_card.position),
            'end_pos': ur.Vec3(self.temp_world_position),
            'start_rot': ur.Vec3(self.temp_card.rotation),
            'end_rot': ur.Vec3(self.temp_world_rotation),
            'curve': ur.curve.in_sine,
        }

        def _reattach():
            self.temp_card.parent = self.temp_parent
            self.temp_card.position = self.temp_position
            self.temp_card.rotation = self.temp_rotation
            self.temp_card.scale = self.temp_scale
            self.temp_card.always_on_top = False

        self._card_tween_on_done = _reattach

    def interact_with_card(self):
        self.buy.enable()
        self.auction.enable()    
        
    def buy_property(self):
        print("Property bought!")
        # Implement property buying logic here (e.g., deduct money, assign ownership, etc.)
        self.reset_card()   
    
    def auction_property(self):
        print("Property auctioned!")
        # Implement auction logic here (e.g., start bidding process, determine winner, etc.)
        self.reset_card()
    
    def reset_card(self):
        self.buy.disable()
        self.auction.disable()
        cam.return_to_board_view()
        self.return_to_origin()


    def update(self):
        # Drive the custom card tween each frame.
        if not self._card_tween:
            return

        tw = self._card_tween
        ent = tw['entity']

        tw['t'] += ur.time.dt
        duration = max(1e-6, tw['duration'])
        p = min(1.0, tw['t'] / duration)
        eased = tw['curve'](p) if tw.get('curve') else p

        ent.position = ur.lerp(tw['start_pos'], tw['end_pos'], eased)
        ent.rotation = ur.lerp(tw['start_rot'], tw['end_rot'], eased)

        if p < 1.0:
            return

        # Finish.
        self._card_tween = None
        if self._card_tween_on_done:
            cb = self._card_tween_on_done
            self._card_tween_on_done = None
            cb()
        


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
        self.p_name = "Player 2"
        self.money = 1500
        self.tex = texture



  
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
        self.p_name = "Player 1"
        self.money = 1500 
        self.tex = texture


    
class Board(ur.Entity):
    '''
    Destined to be the father of them all. 
    '''
    def __init__(self, position=(0,0,0), scale=(1,1,1), color=ur.color.black, texture="Board1"):
        super().__init__(
            model="plane",
            texture=texture,
            scale=scale,
            color=color,
            position=position
        )
        
        self._rotating = False
        self.cards = [
            ("Start", (None, None)), ("Mediterranean Avenue", (60, "#964B00")), ("Community Chest", (None, None)), ("Baltic Avenue", (60, "#964B00")), ("Income Tax", (-200, None)), ("Reading Railroad", (200, None)),
            ("Oriental Avenue", (100, "#00FFFF")), ("Chance", (None, None)), ("Vermont Avenue", (100, "#00FFFF")), ("Connecticut Avenue", (120, "#00FFFF")), ("Jail", (None, None)), ("St. Charles Place", (140, "#FF00FF")),
            ("Electric Company", (150, None)), ("States Avenue", (140, "#FF00FF")), ("Virginia Avenue", (160, "#FF00FF")), ("Pennsylvania Railroad", (200, None)), ("St. James Place", (180, "#FF00FF")),
            ("Community Chest", (None, None)), ("Tennessee Avenue", (180, "#FFA500")), ("New York Avenue", (200, "#FFA500")), ("Free Parking", (None, None)), ("Kentucky Avenue", (220, "#FF0000")),
            ("Chance", (None, None)), ("Indiana Avenue", (220, "#FF0000")), ("Illinois Avenue", (240, "#FF0000")), ("B. & O. Railroad", (200, None)), ("Atlantic Avenue", (260, "#FFFF00")), ("Ventnor Avenue", (260, "#FFFF00")),
            ("Water Works", (150, None)), ("Marvin Gardens", (280, "#FFFF00")), ("Go To Jail", (None, None)), ("Pacific Avenue", (300, "#008000")), ("North Carolina Avenue", (300, "#008000")),
            ("Community Chest", (None, None)), ("Pennsylvania Avenue", (320, "#008000")), ("Short Line", (200, None)), ("Chance", (None, None)), ("Park Place", (350, "#0000FF")), ("Luxury Tax", (-100, None)), ("Boardwalk", (400, "#0000FF"))
        ]
        
        if self.texture == None:
            self.draw_board()

    def draw_board(self):
        '''
        Draw the board with colored properties.
        '''
        
        
        # Geometry constants based on Main.generate_tile_positions logic
        c = 0.4375                   # Center of the track (3.5 / 8)
        k = 1.63                     # Corner width ratio
        total_span = 2 * c           # 0.875
        tile_width = total_span / (k + 9) # ~0.0823
        corner_width = tile_width * k
        
        # Track depth matches approximately the corner width
        track_depth = 0.125 

        for i, (name, (price, color)) in enumerate(self.cards):
            
            side_index = i // 10
            local_index = i % 10

            # --- CORNERS ---
            if local_index == 0:
                if side_index == 0: pos = ur.Vec3(c, 0.01, -c)
                elif side_index == 1: pos = ur.Vec3(-c, 0.01, -c)
                elif side_index == 2: pos = ur.Vec3(-c, 0.01, c)
                else: pos = ur.Vec3(c, 0.01, c)
                
                ent = ur.Entity(
                    parent=self,
                    model="plane",
                    texture=name if price is None else None,
                    position=pos,
                    rotation=(0,0,0),
                    scale=(corner_width * 0.95, 1, corner_width * 0.95), 
                    #color=ur.color.hex("#8BEAD5"),
                    shader=unlit_shader
                ) 
                self.cards[i] = (self.cards[i][0], self.cards[i][1], ent) # Store entity reference for corners


                continue
            
            # --- REGULAR TILES ---
            # Calculate distance from the starting corner of the side to this tile
            dist = (corner_width + tile_width) / 2 + (local_index - 1) * tile_width

            scale_x = tile_width * 0.95
            
            # Determine coverage
            if color is None:
                # Full coverage for non-colored properties (Railroads, Utilities, etc)
                scale_z = track_depth
                offset = 0
            else:
                # Partial coverage for colored properties (leave 25% for color bar)
                scale_z = track_depth * 0.75
                # Align to outer edge
                offset = (track_depth - scale_z) / 2

            y_pos = 0.01 
            
            if side_index == 0:  # Bottom (Go -> Jail) | Right -> Left
                pos = ur.Vec3(c - dist, y_pos, -c - offset)
                rot = ur.Vec3(0, 0, 0)
            elif side_index == 1:  # Left (Jail -> Free Parking) | Bottom -> Top
                pos = ur.Vec3(-c - offset, y_pos, -c + dist)
                rot = ur.Vec3(0, 90, 0)
            elif side_index == 2:  # Top (Free Parking -> Go To Jail) | Left -> Right
                pos = ur.Vec3(-c + dist, y_pos, c + offset)
                rot = ur.Vec3(0, 180, 0)
            else:  # Right (Go To Jail -> Go) | Top -> Bottom
                pos = ur.Vec3(c + offset, y_pos, c - dist)
                rot = ur.Vec3(0, 270, 0)
            
            par = ur.Entity(
                parent=self,
                model="plane",
                position=pos,
                rotation=rot,
                scale=(scale_x, 1, scale_z), 
                color=ur.color.hex("#8BEAD5"),
                shader=unlit_shader,
                bar_color=None
            )
            ur.Text.size=0.2
            name_txt = ur.Text(
                    parent=par,
                    text=name,
                    #world_scale=2,
                    position=(0, 0.1, 0.35),
                    rotation=(90, 0, 0),
                    origin=(0, 0),
                    color=ur.color.black,
                    wordwrap=True,
                    world_scale=0.4
                    #always_on_top=True
                )
            ur.Text.size=0.2
            price = ur.Text(
                    parent=par,
                    text=f"${price}" if price is not None else "",
                    #world_scale=2,
                    position=(0, 0.1, -0.4 if par.scale_z == 0.125 else -0.35),
                    rotation=(90, 0, 0),
                    origin=(0, 0),
                    color=ur.color.black,
                    world_scale=0.4
                    #always_on_top=True
            )

            self.cards[i] = (self.cards[i][0], self.cards[i][1], par)

            # --- COLOR BAR ---
            if color is not None:
                bar_scale_z = track_depth * 0.25
                # Offset to place the bar at the inner edge (facing center of board)
                bar_offset = 0.375 * track_depth
                
                if side_index == 0:   # Bottom, inner edge is +Z
                    bar_pos = ur.Vec3(c - dist, y_pos, -c + bar_offset)
                elif side_index == 1: # Left, inner edge is +X
                    bar_pos = ur.Vec3(-c + bar_offset, y_pos, -c + dist)
                elif side_index == 2: # Top, inner edge is -Z
                    bar_pos = ur.Vec3(-c + dist, y_pos, c - bar_offset)
                else:                 # Right, inner edge is -X
                    bar_pos = ur.Vec3(c - bar_offset, y_pos, c - dist)

                par.bar_color = ur.Entity(
                    parent=par,
                    model="plane",
                    world_position=bar_pos/0.125,
                    world_rotation=rot,
                    world_scale=ur.Vec3(scale_x, 1, bar_scale_z)/0.125,
                    color=ur.color.hex(color),
                    shader=unlit_shader
                )
                par.bar_color.y = 0.01

            else:
                if "Railroad" in name or "Line" in name:
                    name = "Railroad"
                    scale = 0.4
                elif "Income" in name: 
                    ent = ur.Entity(
                        parent=par,
                        model='plane',
                        position=(0, 0.05, -0.05),
                        color=ur.color.black,
                        shader=unlit_shader,
                        rotation=(0, 45, 0),
                        scale=(0.15, 0.15, 0.15),
                        #always_on_top=True 
                    )
                    continue
                else: 
                    scale = 0.6
                ent = ur.Entity(
                    parent=par,
                    model='plane',
                    texture=name,
                    scale=(0.6, 1, scale),
                    position=(0, 0.01, -0.05),
                    rotation=(0, 0, 0),
                    #color=ur.color.hex("#8BEAD5"),
                    shader=unlit_shader
                )
                #self.cards[name] = (self.cards[name][0], self.cards[name][1], ent)
        
        self.middle_square = ur.Entity(
            parent=self,
            model="plane",
            position=(0, 0.01, 0),
            scale=(corner_width * 5.5, 1, corner_width * 5.5),
            color=ur.color.hex("#8BEAD5"),
            shader=unlit_shader
        )
        
    
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
        self.look_at_board = True

    def standard_camera(self):
        while ur.camera.z > -12.5:
            ur.camera.z -= 0.007
            if ur.camera.y > 10:
                ur.camera.y -= 0.0045
            ur.time.sleep(0.0005)
    
    def top_down_camera(self):
        while ur.camera.z < 0:
            if ur.camera.y < 20:
                ur.camera.y += 0.0045
            ur.camera.z += 0.007
            ur.time.sleep(0.0005)

    def update(self):
        if self.look_at_board:
            ur.camera.look_at((0,0,0))
    
    def look_at_card(self):
        self.look_at_board = False
        ur.camera.animate_rotation((0, 0, 0), duration=1.0, curve=ur.curve.in_cubic)
        ur.camera.animate_y(3.5, duration=1.0, curve=ur.curve.in_cubic)
    
    def return_to_board_view(self):
        ur.camera.animate_rotation((38.647682, 0, 0), duration=1.0, curve=ur.curve.in_cubic)
        ur.camera.animate_y(10, duration=1.0, curve=ur.curve.in_cubic)
        ur.invoke(self.look_at_board_func, delay=1.0)

    def look_at_board_func(self):
        self.look_at_board = True

        
    
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



class UI(ur.Entity):
    '''
    Manages the User Interface elements.
    '''
    def __init__(self):
        super().__init__(model=ur.Quad(aspect=0.75, radius=0.05), parent=ur.camera.ui, position=(0.8, 0.3), scale=(.2, .0), color=ur.color.rgba(0, 0, 0, 0.5), origin=(0.5, 0.5))
        self.pos = (-0.14+self.position[0]*20, -1+self.position[1]*20, -0.1)
        

    def add_player_info(self, player):
        print(player.tex)
        if player.tex.endswith("gif"):
            self.bg = ur.Animation(model=ur.Quad(aspect=2, radius=0.05),name=player.tex, parent=self, world_position=self.pos, world_scale=(3.7, 1.7), color=ur.color.rgba(1, 1, 1, .5), origin=(0.5, 0))
        else:
            self.bg = ur.Entity(model=ur.Quad(aspect=2, radius=0.05), texture=player.tex, parent=self, world_position=self.pos, world_scale=(3.7, 1.7), color=ur.color.rgba(1, 1, 1, .5), origin=(0.5, 0))
        print(self.pos)
        print(self.bg.world_position)
        print(self.bg.world_scale)
        ur.Text.default_resolution = 2160 * ur.Text.size
        self.info_text = ur.Text(
            parent=self.bg,
            text=f"{player.p_name}\n${player.money}",
            position=(-0.5, 0.2), 
            scale=(2, 4), 
            origin=(0, 0.5), 
            color=ur.color.white, 
            wordwrap=25,
            #background=True
 
        )
        self.bg.world_parent = ur.camera.ui
        self.pos = tuple(x + y for x, y in zip(self.pos, (0, -2, 0)))

        self.scale = tuple(x + y for x, y in zip(self.scale, (0, 0.1, 0)))
        print("---"*10)
        print(self.info_text.background_entity)
        print("---"*10)
        print(ur.camera.ui.scale)


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
        double = False
        if values[0] == values[1]:
            double = True
            print("DOUBLES! You get another turn!")
            #ur.invoke(self.throw_dice, delay=0.5)
        
        main.move_bitch(amount, double)
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
    position=(0,-0.1,0),
    shader = unlit_shader
)

#sky = ur.Sky(texture="1e5.jpeg")
ur.camera.position = (0, 10, -12.5)
board = Board(scale=(8,0.1,8),
              texture=None
              )
main = Main()

#piece1 = main.spawn_piece("cube", texture="1e5.jpeg")

for i in range(2):
    piece1 = main.spawn_piece("cube", texture="gd.jpg")

    piece2 = main.spawn_piece("cube", texture="mario-super-mario-64.gif")

    piece3 = main.spawn_piece("cube", texture="1e5.jpeg")


dice = Dice()

ui = UI()

for i in main.players:
    ui.add_player_info(i)
ur.window.exit_button.on_click_setter(main.display_gif)
#ur.mouse.visible = False
#ur.Cursor(visible=True, texture="mario.gif", scale=0.05)

app.run()