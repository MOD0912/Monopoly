import ursina as ur
player_count = 0 

class Player_Piece(ur.Entity):
    '''
    Basic non-animated player piece.
    '''
    def __init__(self, parent_board, piece_type="cube", texture="1e5.jpeg", start_position = (3.5, 0.25, -3.5), player_name=None):
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
        self.p_name = player_name if player_name else f"Player {parent_board.player_count}"
        parent_board.player_count += 1
        self.money = 1500
        self.tex = texture
        self.user_color = ur.color.white
        self.owned_properties = []
        
    def __repr__(self):
        return f"<Player_Piece name={self.p_name} money={self.money} tile_position={self.tile_position}>"



class Animated_Piece(ur.Animation):
    '''
    Animated player piece using a gif texture.
    '''
    def __init__(self, parent_board, piece_type="cube", texture="1e5.jpeg", start_position = (3.5, 0.25, -3.5), player_name=None):
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
        self.p_name = player_name if player_name else f"Player {parent_board.player_count}"
        parent_board.player_count += 1
        self.money = 1500 
        self.tex = texture
        self.user_color = ur.color.white
        self.owned_properties = []

    
    def __repr__(self):
        return f"<Animated_Piece name={self.p_name} money={self.money} tile_position={self.tile_position}>"



if __name__ == "__main__":
    import main