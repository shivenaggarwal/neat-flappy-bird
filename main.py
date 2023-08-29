import pygame
import neat
import time
import os 
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

ICON = pygame.image.load('favicon.ico')

pygame.display.set_caption('AI Learning Flappy Bird') # Window title
pygame.display.set_icon(ICON) # Window icon

STAT_FONT = pygame.font.SysFont("comicsans",50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 # How much the bird will tilt
    ROT_VEL = 20 # How much we will rotate on each frame
    ANIMATION_TIME = 5 # How long we will show each bird animation
    
    def __init__(self,x,y):
        self.x = x # Starting position of the bird
        self.y = y
        self.tilt = 0 # How much the image is tilted
        self.tick_count = 0 # Physics of the bird
        self.vel = 0 
        self.height = self.y
        self.img_count = 0 # Which image we are showing
        self.img = self.IMGS[0]
        
    def jump(self):
        self.vel = -10.5 # Negative velocity means going up
        self.tick_count = 0 # When we last jumped
        self.height = self.y
        
    def move(self):
        self.tick_count += 1 # How many times we moved since last jump
        d = self.vel*self.tick_count + 1.5*self.tick_count**2 # How many pixels we move up or down {d = displacement}
        
        if d >= 16: # Terminal velocity
            d = 16
        if d < 0: #Smooth jumping
            d -= 2
            
        self.y = self.y + d # New position of the bird
        
        if d<0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
                
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL # Tilt the bird to 90 degrees while falling
                
    def draw(self,win):
        self.img_count += 1 
        # For the flapping animation of the bird
        if self.img_count < self.ANIMATION_TIME: 
            self.img = self.IMGS[0]
            
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
            
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
            
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
            
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
            
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
            
        rotated_image = pygame.transform.rotate(self.img,self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x,self.y)).center) # Rotating the image around the center
        win.blit(rotated_image,new_rect.topleft)
    
    def get_mask(self): # For pixel perfect collision
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200 # Space between the pipes
    VEL = 5 # How fast the pipe moves
       
    def __init__(self,x): #No y because the height of the pipe is random
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True) # Flipping the pipe image
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False # If the bird has passed the pipe
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height() # Find the top of the pipe
        self.bottom = self.height + self.GAP # Find the bottom of the pipe
    
    def move(self):
        self.x -= self.VEL 
    
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))
        
    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        #Mask in pygame is a way to detect pixel perfect collision by converting the image into a 2D array of 1s and 0s
        
        top_offset = (self.x - bird.x,self.top - round(bird.y)) # How far away the two masks are from each other
        bottom_offset = (self.x - bird.x,self.bottom - round(bird.y))
        
        b_point = bird_mask.overlap(bottom_mask,bottom_offset) # Returns point of collision
        t_point = bird_mask.overlap(top_mask,top_offset)
        
        if t_point or b_point:
            return True
        return False

class Base:
    VEL = 5 # Same as pipe velocity
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH # Two images of the base to make it look like it is moving
        
    def move(self):
        self.x1 -= self.VEL 
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH # If the first image goes off the screen, move it to the right of the second image
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

  
def draw_window(win,birds, pipes, base, score, gen):
    win.blit(BG_IMG,(0,0))
    for pipe in pipes:
        pipe.draw(win) # Drawing the pipes
    
    text = STAT_FONT.render("Score: " + str(score),1,(255,255,255)) # Printing the score
    win.blit(text,(WIN_WIDTH - 10 - text.get_width(),10)) # Printing the score on the top right corner
    
    text = STAT_FONT.render("Gen: " + str(gen),1,(255,255,255)) # Printing the generation
    win.blit(text,(10,10)) # Printing the generation on the top left corner
    
    base.draw(win) # Drawing the base
    
    for bird in birds:
        bird.draw(win)
    pygame.display.update()
    
def main(genomes,config):
    global GEN
    GEN+= 1
    nets= [] # Neural network for each bird
    ge = [] # Genome for each bird
    birds = []
    
    for _, g in genomes: #Underscore because we don't care about the genome(tuple) id
        net = neat.nn.FeedForwardNetwork.create(g,config) # Creating a neural network for each genome
        nets.append(net) 
        birds.append(Bird(230,350)) #Bird object that starts at the middle of the screen
        g.fitness = 0
        ge.append(g)
    
    base = Base(730)
    pipes = [Pipe(600)] # List of pipes
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    
    score = 0
    
    run = True
    
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        #making sure only one pipe is read at a time
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # If the bird has passed the first pipe
                pipe_ind = 1
        else:
            run = False
            break
        #getting the fitness calculated
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            #applying the activation function (tanh in this case)
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))) # Where the bird is, where the top of the pipe is, where the bottom of the pipe is

            if output[0] > 0.5: # Only one output neuron
                bird.jump()

        add_pipe = False
        base.move()
        #this list is to remove used pipes
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1 #if the bird hits the pipe, reduce the fitness
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            
                if not pipe.passed and pipe.x < bird.x: #if the bird has passed the pipe
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.x +pipe.PIPE_TOP.get_width() < -100: #removing the pipe if it is off the screen
                rem.append(pipe)
            
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
        
        for r in rem:
            pipes.remove(r)

        #check if the bird touches the ground or the ceiling
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > 730 or bird.y < 0: # If the bird hits the ground or the ceiling
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        if score > 50:
            break
        
        base.move()
        draw_window(win,birds,pipes,base,score, GEN)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    
    #population
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True)) # Prints out the stats
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(main,50) # 50 is the number of generations

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"neat-config.txt")
    run(config_path)