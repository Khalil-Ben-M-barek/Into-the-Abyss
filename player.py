import pygame
from settings import *
from support import import_sprite_sheet
from enemies import Zombie


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.hp = 1000
        self.max_hp = 1000
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 10
        self.attack_damage = 2
        self.sword_hitbox = None
        

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

        self.hitbox = pygame.Rect(0, 0, self.rect.width * 0.1, 30)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom - 40
        self.hitbox_mask = pygame.Mask(self.hitbox.size)
        self.hitbox_mask.fill()

        self.direction=pygame.math.Vector2()
        self.base_speed=2.2
        self.run_multiplier=1.5
        self.speed=self.base_speed
        self.waiting_for_upgrade = False
        self.mask = pygame.mask.from_surface(self.image)

        #player stamina
        self.max_stamina=100
        self.stamina=100
        self.stamina_drain=0.4
        self.stamina_regen=0.2
        self.attack_cost=15
        #exp
        self.lvl=1
        self.xp=100
        self.xp_self=0

    def import_player_assets(self):
        
        character_path = 'assets/player/'
        actions = ['idle', 'walk', 'run','attack']
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
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
           self.direction.y=-1
        elif keys[pygame.K_DOWN]and not keys[pygame.K_UP]:
           self.direction.y=1
        else:
            self.direction.y=0  
        if keys[pygame.K_RIGHT]and not keys[pygame.K_LEFT]:
           self.direction.x=1
        elif keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
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
        elif keys[pygame.K_s]:
            self.status=f'run_{self.facing}'
        else:
            self.status = f'walk_{self.facing}'       
       #sprint and stamina
        self.speed=self.base_speed
        if keys[pygame.K_s] and self.stamina>0:  
            self.speed=self.base_speed*self.run_multiplier
            self.stamina-=self.stamina_drain
        else:
            self.stamina+=self.stamina_regen
        if self.stamina<=0:
            self.stamina=0
            self.speed=self.base_speed
        if  self.stamina>self.max_stamina:
            self.stamina=self.max_stamina

        # Attack
        if keys[pygame.K_SPACE] and self.attack_timer <= 0 and self.stamina>self.attack_cost:
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown
            self.stamina-=self.attack_cost
            self.status = f'attack_{self.facing}'

    def move(self, map_mask):
        if self.direction.length()>0:
            self.direction=self.direction.normalize()
            self.hitbox.x += self.direction.x * self.speed

            if map_mask.overlap(self.hitbox_mask, (self.hitbox.x, self.hitbox.y)):
                self.hitbox.x -= self.direction.x * self.speed

            self.hitbox.y += self.direction.y * self.speed

            if map_mask.overlap(self.hitbox_mask, (self.hitbox.x, self.hitbox.y)):
                self.hitbox.y -= self.direction.y * self.speed
            
            self.rect.midbottom = self.hitbox.midbottom

            self.rect.bottom = self.hitbox.bottom + 40
            self.rect.centerx = self.hitbox.centerx

    def animate(self):
        if self.status!=self.old_status:
            self.frame_index=0
            self.old_status=self.status
        if not self.is_attacking:
            if self.status != self.old_status:
                self.frame_index = 0
                self.old_status = self.status
        else:

            self.status = f'attack_{self.facing}'

        animation = self.animations.get(self.status)
        if not animation:
            return
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.is_attacking:
                self.is_attacking = False
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]


    def gain_xp(self,amount):
        self.xp_self+=amount
        if self.xp_self>=self.xp:
            self.xp_self-=self.xp
            self.lvl_up()

    def lvl_up(self):
        self.lvl+=1
        self.xp= int(self.xp * 1.5)
        self.waiting_for_upgrade = True
        print("New Stats -> HP:", self.max_hp,
          "Stamina:", self.max_stamina,
          "Damage:", self.attack_damage,
          "XP needed:", self.xp)
    def update(self, map_mask):
        self.movement()
        self.move(map_mask)
        self.animate()
        
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        
        if self.is_attacking:
            if self.facing == "right":
                self.sword_hitbox = pygame.Rect(self.rect.centerx, self.rect.centery - 20, 40, 20)
            elif self.facing == "left":
                self.sword_hitbox = pygame.Rect(self.rect.centerx - 60, self.rect.centery - 20, 40, 20)
            elif self.facing == "up":
                self.sword_hitbox = pygame.Rect(self.rect.centerx - 20, self.rect.centery - 60, 20, 40)
            elif self.facing == "down":
                self.sword_hitbox = pygame.Rect(self.rect.centerx - 20, self.rect.centery, 20, 40)

        else:
            self.sword_hitbox = None



    def take_damage(self, amount):
            self.hp -= amount
            self.hit_time = pygame.time.get_ticks()
            if self.hp <= 0:
                self.is_alive = False
                self.kill()