import ursina as ur
import threading

class Camera(ur.Entity):
    '''
    Controls the camera movement and views.
    '''
    def __init__(self, board_instance=None):
        super().__init__()
        self.look_at_board = True
        self.board = board_instance

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
        
        # Uses self.board if available
        if self.board:
            if key == "3":
                self.board.rotate_board()
            if key == "4":
                tex = str(self.board.texture)
                if "mario.gif" in tex:
                    self.board.texture = "Board1.jpg"
                else:
                    self.board.texture = "mario.gif"


if __name__ == "__main__":
    import main