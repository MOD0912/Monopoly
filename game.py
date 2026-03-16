import ursina as ur
from player import Player_Piece, Animated_Piece
class Main(ur.Entity):
    '''
    Meant to be the father of them all. Forced to be the class pulling the strings
    '''
    def __init__(self, board_instance, camera_instance, ui_instance):
        super().__init__()
        self.players = []
        self.current_player = 0
        self.board = board_instance
        self.cam = camera_instance
        self.ui = ui_instance
        self.dice = None # Generated later

        self.ready = True # Used to prevent dice throwing at inappropriate times (e.g., during animations or card interactions).

        self.tile_positions = self.generate_tile_positions()
        self._moving = False
        self._steps_left = 0
        self._move_double = False
        self._step_duration = 0.1
        self._jump_height = 7.5
        # Simple custom tween state for the card display (avoids animate_position/animate_rotation).
        self._card_tween = None
        self._card_tween_on_done = None
        ur.Text.size=0.05
        self.buy = ur.Button(parent=ur.camera.ui, text="Buy", color=ur.color.blue, position=(-0.115, -0.4), scale=(0.115*2, 0.1), on_click=self.buy_property, enabled=False)
        self.auction = ur.Button(parent=ur.camera.ui, text="Auction", color=ur.color.white, position=(0.115, -0.4), scale=(0.115*2, 0.1), on_click=self.auction_property, enabled=False, text_color=ur.color.black)

    def set_dice(self, dice_instance):
        self.dice = dice_instance

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
        amount = 3
        self.start_move(amount, double)


    def spawn_piece(self, piece_type="cube", texture="1e5.jpeg"):
        '''
        Spawn a new player piece on the board.
        '''
        if texture.endswith("gif"):
            player = Animated_Piece(self.board, piece_type=piece_type, texture=texture)
        else:
            player = Player_Piece(self.board, piece_type=piece_type, texture=texture)
        self.players.append(player)
        return player

    def start_move(self, amount: int, double: bool = False):
        if not self.players:
            return

        if self._moving:
            # Ignore overlapping move requests for now.
            return

        self._moving = True
        self._steps_left = max(0, int(amount))
        self._move_double = bool(double)
        self._move_step()

    def _move_step(self):
        curr_player = self.players[self.current_player]

        if self._steps_left <= 0:
            self._moving = False

            if self._move_double:
                if self.dice:
                    ur.invoke(self.dice.throw_dice)
            elif self.board.cards[curr_player.tile_position].owner is not None:
                self.board.cards[curr_player.tile_position].owner.money += self.board.cards[curr_player.tile_position].rent[0]
                curr_player.money -= self.board.cards[curr_player.tile_position].rent[0]
                print(f"Paid rent of {self.board.cards[curr_player.tile_position].rent[0]} to {self.board.cards[curr_player.tile_position].owner}.")
                self.reset_card()
                

            else:    
                ur.invoke(self.show_card, self.board.cards[curr_player.tile_position])            
            return

        curr_player.tile_position = (curr_player.tile_position + 1) % 40
        target_pos = self.tile_positions[curr_player.tile_position]

        dur = self._step_duration
        jump = self._jump_height

        curr_player.animate_y(jump, duration=dur / 2, curve=ur.curve.out_sine)
        curr_player.animate_position((target_pos.x, jump, target_pos.z), duration=dur / 2, curve=ur.curve.linear)
        ur.invoke(curr_player.animate_position, target_pos, duration=dur / 2, curve=ur.curve.in_sine, delay=dur / 2)

        self._steps_left -= 1
        ur.invoke(self._move_step, delay=dur)

            
    
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
        
    def show_card(self, card):
            '''
            Valla Kriese
            '''
            # Placeholder implementation
            if card.name in ["Income Tax", "Luxury Tax", "Go To Jail", "Free Parking", "Jail", "Start"]:
                return
            
            print(f"Showing card: {card.name}")
            self.card = card
            self.card_price = card.price
            card_ent = card.entity
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
            
            # Use self.cam instead of global cam
            self.cam.look_at_board = False
            self.cam.look_at_card()
            
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
        print(self.card_price)
        if self.card_price is None:
            print("chance or community chest ")
            self.chance_or_community()
            return
        self.buy.enable()
        self.auction.enable()

    def chance_or_community(self):
        print("Chance or Community Chest card drawn!")
        # Implement logic to randomly select a Chance or Community Chest card and apply its effects.
        self.reset_card()    
        
    def buy_property(self):
        curr_player = self.players[self.current_player]
        if curr_player.money < self.card_price:
            print("Not enough money to buy this property.")
            return
        print("Property bought!")
        print(curr_player.money)
        curr_player.money -= self.card_price
        print(curr_player.money)
        print(self.card)
        self.card.owner = curr_player
        print(self.card.owner)
        if self.temp_card.bar_color != None:
            self.temp_card.bar_color.color = curr_player.user_color
        if self.temp_card.texture != None:
            print(curr_player.texture)
            self.temp_card.texture = curr_player.texture
                    
        self.reset_card()   
    
    def auction_property(self):
        print("Property auctioned!")
        # Implement auction logic here (e.g., start bidding process, determine winner, etc.)
        self.reset_card()
    
    def reset_card(self):
        self.ui.update_ui(self.players[self.current_player])
        self.ready = True
        self.current_player = (self.current_player + 1) % len(self.players)
        self.buy.disable()
        self.auction.disable()
        self.cam.return_to_board_view()
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


if __name__ == "__main__":
    import main