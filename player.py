import pygame
from settings import *
from support import import_sprite_sheet


class Player(pygame.sprite.Sprite):
    def __init__(self,pos, *groups):
        super().__init__(*groups)
        self.import_player_assets()
        self.facing = 'down'
        self.status = f'idle_{self.facing}'
        self.old_status = self.status
        self.frame_index = 0
        self.animation_speed = 0.15

        frames = self.animations.get(self.status)
        if frames and len(frames) > 0:
            self.image = frames[0]
        self.rect=self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0,-26)
        self.direction=pygame.math.Vector2()
        self.base_speed=2.2
        self.run_multiplier=1.5
        self.speed=self.base_speed
        #player stamina
        self.max_stamina=100
        self.stamina=100
        self.stamina_drain=0.6
        self.stamina_regen=0.3
        #exp
        self.lvl=1
        self.xp=100
        self.xp_self=0
        self.xp_gain=20
    def import_player_assets(self):
        
        character_path = 'assets/player/'
        actions = ['idle', 'walk', 'run']
        directions = ['up', 'down', 'left', 'right']
        self.animations = {}

        for action in actions:
            for direction in directions:
                path = f"{character_path}{action}_{direction}.png"
                sheet = pygame.image.load(path).convert_alpha()

                frame_count = 8
                frame_width = sheet.get_width() // frame_count
                frame_height = sheet.get_height()
                frames = import_sprite_sheet(path, frame_width, frame_height)
                self.animations[f"{action}_{direction}"] = frames

    def movement(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_z] and not keys[pygame.K_s]:
           self.direction.y=-1
        elif keys[pygame.K_s]and not keys[pygame.K_z]:
           self.direction.y=1
        else:
            self.direction.y=0  
        if keys[pygame.K_d]and not keys[pygame.K_q]:
           self.direction.x=1
        elif keys[pygame.K_q] and not keys[pygame.K_d]:
            self.direction.x=-1 
        else:
            self.direction.x=0
        #status
        if self.direction.x > 0:
            self.facing = 'right'
        elif self.direction.x < 0:
            self.facing = 'left'
        elif self.direction.y < 0:
            self.facing = 'up'
        elif self.direction.y > 0:
            self.facing = 'down'
        if self.direction.length() == 0:
            self.status = f'idle_{self.facing}'
        elif keys[pygame.K_LSHIFT]:
            self.status=f'run_{self.facing}'
        else:
            self.status = f'walk_{self.facing}'       
       #sprint and stamina
        self.speed=self.base_speed
        if keys[pygame.K_LSHIFT] and self.stamina>0:  
            self.speed=self.base_speed*self.run_multiplier
            self.stamina-=self.stamina_drain
        else:
            self.stamina+=self.stamina_regen
        if self.stamina<=0:
            self.stamina=0
            self.speed=self.base_speed
        if  self.stamina>self.max_stamina:
            self.stamina=self.max_stamina
    def move(self):
        if self.direction.length()>0:
            self.direction=self.direction.normalize()
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
    def animate(self):
        if self.status!=self.old_status:
            self.frame_index=0
            self.old_status=self.status
        animation=self.animations.get(self.status)
        if not animation:
            return
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
    def gain_xp(self):
        self.xp_self+=self.xp_gain
        if self.xp_self>=self.xp:
            self.xp_self-=self.xp
            self.lvl+=1
            self.xp = int(self.xp * 1.3)
    def update(self):
        self.movement()
        self.move()
        self.animate()