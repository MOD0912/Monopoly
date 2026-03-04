import ursina as ur
from ursina.shaders import unlit_shader
from card import Card

class Board(ur.Entity):
    '''
    Destined to be the father of them all. 
    '''
    def __init__(self, position=(0,0,0), scale=(1,1,1), color=ur.color.black, texture="Board1", map="maps/Map1.txt"):
        super().__init__(
            model="plane",
            texture=texture,
            scale=scale,
            color=color,
            position=position
        )
        
        self._rotating = False
        self.cards = []
        try:
            with open(map, "r") as file:
                for line in file:
                    parts = line.strip().split(";")
                    name = parts[0]
                    price = int(parts[1]) if parts[1] else None
                    color = parts[2] if len(parts) > 2 and parts[2] else None
                    self.cards.append(Card(name, price, color))
        except FileNotFoundError:
            print("Error: Map file not found. Please create 'maps/Map1.txt'.")
            # Fallback or exit? For now, empty list will likely crash later code, 
            # but printing error is standard.
        
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

        for i, card in enumerate(self.cards):
            name = card.name
            price = card.price
            color = card.color
            
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
                card.entity = ent # Store entity reference for corners


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
            price_txt = ur.Text(
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

            card.entity = par

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
