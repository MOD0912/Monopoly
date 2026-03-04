import ursina as ur

class UI(ur.Entity):
    '''
    Manages the User Interface elements.
    '''
    def __init__(self):
        super().__init__(model=ur.Quad(aspect=0.75, radius=0.02), parent=ur.camera.ui, position=(0.8, 0.3), scale=(.2, .0), color=ur.color.rgba(0, 0, 0, 0.5), origin=(0.5, 0.5))
        self.pos = (-0.14+self.position[0]*20, -1+self.position[1]*20, -0.1)
        top = ur.Animation(parent=ur.camera.ui, name='wth', position=(0, 0.5), scale=(1.6, 0.01), fps=12, loop=True, autoplay=True)
        left = ur.Animation(parent=ur.camera.ui, name='wth', position=(-0.799, 0), scale=(1, 0.01), rotation=(0, 0, -90), fps=10, loop=True, autoplay=True)
        right = ur.Animation(parent=ur.camera.ui, name='wth', position=(0.799, 0), scale=(1, 0.01), rotation=(0, 0, 90), fps=12, loop=True, autoplay=True)
        bottom = ur.Animation(parent=ur.camera.ui, name='wth', position=(0, -0.498), scale=(1.6, 0.01), fps=12, loop=True, autoplay=True)

        

    def add_player_info(self, player):
        print(player.tex)
        if player.tex.endswith("gif"):
            self.bg = ur.Animation(model=ur.Quad(aspect=2, radius=0.05),name=player.tex, parent=self, world_position=self.pos, world_scale=(3.7, 1.7), color=ur.color.rgba(1, 1, 1, .5), origin=(0.5, 0))
        else:
            self.bg = ur.Entity(model=ur.Quad(aspect=2, radius=0.05), texture=player.tex, parent=self, world_position=self.pos, world_scale=(3.7, 1.7), color=ur.color.rgba(1, 1, 1, .5), origin=(0.5, 0))
        #print(self.pos)
        #print(self.bg.world_position)
        #print(self.bg.world_scale)
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
