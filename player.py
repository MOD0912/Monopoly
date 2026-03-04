import ursina as ur

class Player_Piece(ur.Entity):
    '''
    Basic non-animated player piece.'''
    def __init__(self, parent_board, piece_type="cube", texture="1e5.jpeg", start_position = (3.5, 0.25, -3.5)):
        self.start_position = start_position
        super().__init__(
            parent=parent_board,
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
        self.user_color = ur.color.white
        self.owned_properties = []

class Animated_Piece(ur.Animation):
    '''
    Animated player piece using a gif texture.
    '''
    def __init__(self, parent_board, piece_type="cube", texture="1e5.jpeg", start_position = (3.5, 0.25, -3.5)):
        self.start_position = start_position
        super().__init__(
                parent=parent_board,
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
        self.user_color = ur.color.white
        self.owned_properties = []
