# Spaceship by Nick Togneri
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False
rock_group = set()
missile_group = set()
remove_list = set()
speed_constant = 1

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://sampleswap.org/mp3/artist/19161/Fulano47_freimology-part-II-160.mp3")
soundtrack.set_volume(.3)
missile_sound = simplegui.load_sound("http://www.sa-matra.net/sounds/starwars/XWing-Laser.wav")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("https://dl.dropbox.com/s/1ganaqhyr6tzg4j/thrust2.mp3")
ship_thrust_sound.set_volume(.5)
explosion_sound = simplegui.load_sound("http://www.sa-matra.net/sounds/starwars/ISD-Laser4.wav")
explosion_sound.set_volume(.5)
ship_explosion = simplegui.load_sound("http://www.mediacollege.com/downloads/sound-effects/explosion/explosion-01.mp3")
ship_explosion.set_volume(.6)
# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    global a_missile
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.forward = None
        
    def draw(self,canvas):
        if self.thrust == False:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, (self.image_center[0] + 90, self.image_center[1]), self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += (self.angle_vel)
        if self.thrust:
            self.forward = angle_to_vector(self.angle)
            ship_thrust_sound.play()
            self.vel[0]+=self.forward[0]
            self.vel[1]+=self.forward[1]
            self.vel[0] *= .8
            self.vel[1] *= .8
        else:    
            self.vel[0] *= .995
            self.vel[1] *= .995
        
        self.pos[0]=(self.pos[0]+self.vel[0])%WIDTH
        self.pos[1]=(self.pos[1]+self.vel[1])%HEIGHT
        
    def shoot(self):
        global a_missile
        forward = angle_to_vector(self.angle)
        self.m_pos = [self.pos[0]+45*forward[0],self.pos[1]+45*forward[1]]
        missile_group.add(Sprite(self.m_pos, [self.vel[0] + forward[0] * 10, self.vel[1] + forward[1] * 10],self.angle,0,missile_image, missile_info, missile_sound))
        missile_sound.play()

    def key_down(self, key_down):
        self.key = key_down
        if started:
            if self.key == simplegui.KEY_MAP["right"]:
                self.angle_vel += .1
            if self.key == simplegui.KEY_MAP["left"]:
                self.angle_vel -= .1
            if self.key == simplegui.KEY_MAP["up"]:
                self.thrust = True
            if self.key == simplegui.KEY_MAP['space']:
                self.shoot()

    def key_up(self, key_up):
        self.key = key_up
        if self.key == simplegui.KEY_MAP['left']:
            self.angle_vel = 0
        if self.key == simplegui.KEY_MAP['right']:
            self.angle_vel = 0
        if self.key == simplegui.KEY_MAP['up']:
            self.thrust = False
            ship_thrust_sound.pause()
            
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0]* speed_constant,vel[1]*speed_constant] 
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        self.spin_dir = (random.choice([True, False]))
        if sound:
            sound.rewind()
            sound.play()
            
    def collide(self, sprite2):
        r1 = self.radius       
        r2 = sprite2.radius        
        p1 = self.pos       
        p2 = sprite2.pos 
        
        if dist(p1, p2) < r1+r2:           
            return True            
        else:                        
            return False

    def draw(self, canvas):
        global lives, started
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle) 
        
                
    def update(self): 
        global remove_list, missile_group
        self.pos[0]=(self.pos[0]+self.vel[0])%WIDTH
        self.pos[1]=(self.pos[1]+self.vel[1])%HEIGHT
        self.age += 1
        
        if self.spin_dir:
            self.angle += .05 
        else:
            self.angle -= .05
            
        #for missile in missile_group:
        return self.age > self.lifespan
            
            
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score, soundtrack
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.play()
        timer.start()
        
def draw(canvas):
    global time, lives, score, speed_constant
    
    # animate background
    time += 1
    speed_constant *= 1.0005
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    #draw ship
    my_ship.draw(canvas)
    group_collide(rock_group, my_ship)
    group_group_collide(missile_group, rock_group)
    if group_collide(rock_group, my_ship):
        if lives <= 1:
            lives -= 1
            start_restart()
        else:
            lives -= 1
            ship_explosion.play()
            speed_constant = 1
     
    # update ship and sprites
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    my_ship.update()

    if not started:
        #timer.stop()
        canvas.draw_image(splash_image, splash_info.get_center(), 
                      splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                      splash_info.get_size())
        canvas.draw_text('Music, "freimology II" by: Fulano47 -- sampleswap.org', (130, 550), 24, 'White')


    canvas.draw_text(('Lives = ' +  str(lives)), (100,30) , 20, 'white')
    canvas.draw_text(('Score = ' +  str(score)), (600,30) , 20, 'white')

# timer handler that spawns a rock    
def rock_spawner():
    global a_rock
    if started:
        first_pos = [random.randrange(0, WIDTH), random.randrange(0,HEIGHT)]
        if len(rock_group) < 14 and started: 
            if dist(my_ship.pos, first_pos) > my_ship.radius * 1.6:
                rock_group.add(Sprite(first_pos, [(random.random()*random.choice([-1,1])), (random.random()*random.choice([-1, 1]))], 
                              0, 0, asteroid_image, asteroid_info))
    
def process_sprite_group(group_set, canvas):
    for item in group_set:
        if item.age > item.lifespan / speed_constant:
            remove_list.add(item)
        group_set.difference_update(remove_list)
        item.draw(canvas)
        item.update()
        
def group_collide(group, object):
    for thing in group:
        if thing.collide(object):
            explosion_sound.play()
            remove_list.add(thing)
            return True

def group_group_collide(group_1, group_2):
    global score, speed_constant
    for hit in group_1:
        if group_collide(group_2, hit):
            score += 100
            remove_list.add(hit)

def start_restart():
    global started, rock_group, speed_constant
    soundtrack.pause()
    soundtrack.rewind()
    started = False
    rock_group = set()
    my_ship.thrust = False
    speed_constant = 1
    ship_thrust_sound.pause()
    my_ship.pos = [WIDTH / 2, HEIGHT / 2]
    my_ship.vel = [0, 0]
 
 # initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(my_ship.key_down)
frame.set_mouseclick_handler(click)
frame.set_keyup_handler(my_ship.key_up)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
frame.start()
