import pygame
from os.path import join
from random import randint,uniform

class Player(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.image=pygame.image.load(join('images','player.png')).convert_alpha()
        self.rect=self.image.get_frect(center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2))
        self.direction=pygame.Vector2()
        self.speed=300

        # cooldown
        self.can_shoot=True
        self.laser_shoot_time=0
        self.cooldown_duration=400

        #mask
        mask=pygame.mask.from_surface(self.image)
        # mask_surf=mask.to_surface()
        # mask_surf.set_colorkey((0,0,0)) 
        # self.image=mask_surf
    
    def laser_time(self):
        if not self.can_shoot:
            current_time=pygame.time.get_ticks()
            if current_time-self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot=True

    def update(self,dt):
        keys=pygame.key.get_pressed()
        self.direction.x=int(keys[pygame.K_RIGHT])-int(keys[pygame.K_LEFT]) 
        self.direction.y=int(keys[pygame.K_DOWN])-int(keys[pygame.K_UP]) 
        self.direction=self.direction.normalize() if self.direction else self.direction
        self.rect.center +=self.direction*self.speed*dt

        recent_keys=pygame.key.get_just_pressed()
        if(recent_keys[pygame.K_SPACE] and self.can_shoot):
            Laser(laser_surface,self.rect.midtop,(all_sprites,laser_sprites))
            self.can_shoot=False
            self.laser_shoot_time=pygame.time.get_ticks() 
            laser_sound.play()
        self.laser_time()

class Star(pygame.sprite.Sprite):
    def __init__(self,groups,star_surface):
        super().__init__(groups)
        self.image=star_surface
        self.rect=self.image.get_frect(center=(randint(0,WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):

    def __init__(self,surf,pos,group):
        super().__init__(group)
        self.image=surf
        self.rect=self.image.get_frect(midbottom=pos)

    def update(self,dt):
        self.rect.centery-= 400*dt
        if(self.rect.bottom <0):
            self.kill()
        
class Meteor(pygame.sprite.Sprite):
    def __init__(self,surf,pos,group):
        super().__init__(group)
        self.original_surface=surf
        self.image=surf
        self.rect=self.image.get_frect(center=pos)
        self.start_time=pygame.time.get_ticks()
        self.lifetime=3000
        self.direction=pygame.Vector2(uniform(-0.5,0.5),1)  
        self.speed=randint(400,500)
        self.rotation_speed=int(randint(40,80))
        self.rotation=0
        

    def update(self,dt):
        self.rect.center += self.direction*self.speed*dt
        if(pygame.time.get_ticks()-self.start_time>=self.lifetime):
            self.kill()
        self.rotation+=self.rotation_speed*dt
        self.image=pygame.transform.rotozoom(self.original_surface,self.rotation,1)
        self.rect=self.image.get_frect(center=self.rect.center)
    
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__ (self,frames,pos,groups):
        super().__init__(groups)
        self.frames=frames
        self.frame_index=0
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_frect(center=pos)

    def update(self,dt):
        self.frame_index+=20*dt
        if self.frame_index<len(self.frames):
            self.image=self.frames[int(self.frame_index)]
        else:
            self.kill()


def collisions():
    global running
    collisionMP=pygame.sprite.spritecollide(player,meteor_sprites,True,pygame.sprite.collide_mask)# if we set do kill to true then it will remove the meteor which it will collide to 
    if collisionMP:    
        running=False

    for laser in laser_sprites:
        collided_sprites=pygame.sprite.spritecollide(laser,meteor_sprites,True,pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames,laser.rect.midtop,all_sprites)
            explosion_sound.play()

def display_score():
    current_time=pygame.time.get_ticks()//100
    text_surf=font.render(str(current_time),True,(240,240,240))
    text_rect=text_surf.get_frect(midbottom=(WINDOW_WIDTH/2,WINDOW_HEIGHT-50))
    display_surface.blit(text_surf,text_rect)
    pygame.draw.rect(display_surface,'white',text_rect.inflate(20,10).move(0,-10),10,10)

# general setup
pygame.init()
WINDOW_WIDTH,WINDOW_HEIGHT=1280,720
display_surface=pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
running =True
clock=pygame.time.Clock()

#import
star_surface=pygame.image.load(join('images','star.png')).convert_alpha()
meteor_surface=pygame.image.load(join('images','meteor.png')).convert_alpha()
laser_surface=pygame.image.load(join('images','laser.png')).convert_alpha()
font=pygame.font.Font(join('images','Oxanium-Bold.ttf'),40)
text_surf=font.render('text',True,'white')
explosion_frames=[pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha() for i in range(1,21)]

# audio
laser_sound=pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound=pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.5)
game_music=pygame.mixer.Sound(join('audio','game_music.wav'))
game_music.set_volume(0.4)
game_music.play()

# plain surface
surf=pygame.Surface((100,200))
surf.fill('orange')
x=100

all_sprites=pygame.sprite.Group()
meteor_sprites=pygame.sprite.Group()#to store all meteor sprites
laser_sprites=pygame.sprite.Group()
for i in range(20):
    Star(all_sprites,star_surface)
player=Player(all_sprites)

# import a meteor 
# meteor_rect=meteor_surface.get_frect(center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2))

# import a laser
# laser_rect=laser_surface.get_frect(bottomleft=(20,WINDOW_HEIGHT))

# custom event-> meteor event 
meteor_event= pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)

while running:
    dt=clock.tick()/1000
    # event loop 

    # for checking the events and quiting the game 
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==meteor_event:
            Meteor(meteor_surface,(int(randint(0,WINDOW_WIDTH)),int(randint(-200,-100))),(all_sprites,meteor_sprites))

    # update
    all_sprites.update(dt)

    # collisionML=pygame.sprite.spritecollide(laser_sprites,meteor_sprites,True) 
    # this will not work cause both are group but one needs to be constant
    collisions()

    # draw the game
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    display_score()
   
    pygame.display.update()



pygame.quit()