import ursina as ur

class Dice(ur.Entity):
    '''
    Simulates two dice with basic physics.
    '''
    def __init__(self, game_instance, scale=0.25):
        super().__init__()
        self.game = game_instance
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
        throw em dice
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
        
        # Uses self.game instead of global main
        self.game.move_bitch(amount, double)
        self.cunt = 0 
        


    def input(self, key):
        if key == "space" and self.game.ready:
            # Prevent throwing if already rolling or other states if needed
            self.game.ready = False
            self.throw_dice()
            
        if key == "m":
            self.game.move_bitch(1)

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
            
            if self.cunt == 2:
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


if __name__ == "__main__":
    import main