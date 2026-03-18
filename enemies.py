import pygame
import math
from support import import_sprite_sheet

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, despawn_x=0):
        super().__init__(groups)
        self.image = pygame.Surface((15, 8))
        self.image.fill("cyan")
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.math.Vector2(-1, 0)
        self.speed = 5
        self.damage = 100
        self.despawn_x = despawn_x 

    def update(self):
        self.rect.x += self.direction.x * self.speed
        if self.rect.right < self.despawn_x:
            self.kill()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, pos, player, *groups):
        super().__init__(*groups)
        self.max_hp = 100
        self.hp = 100
        self.distraction = None
        self.state = "IDLE"
        self.player = player
        self.status = 'IDLE'
        self.prev_status = self.status
        self.frame_index = 0
        self.speed = 1.5
        self.detection_range = 200
        self.xp_reward = 50

        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.1

        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(center=pos)
        
        self.hitbox = pygame.Rect(0, 0, self.rect.width * 0.1, 10)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom - 40
        
        self.hitbox_mask = pygame.Mask(self.hitbox.size)
        self.hitbox_mask.fill()
        self.pos = pygame.math.Vector2(self.hitbox.center)

    def import_assets(self):
        path = 'assets/enemies/'
        frame_width=64
        frame_height=64
        self.animations = {
        'IDLE': import_sprite_sheet(path + 'IDLE.png', frame_width, frame_height),
        'walk': import_sprite_sheet(path + 'walk.png', frame_width, frame_height)
        }
        

    def animate(self):
        if self.status != self.prev_status:
            self.frame_index = 0
            self.prev_status = self.status
        
        animation = self.animations[self.status]

        if len(animation) == 0:
            return

        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom + 40
    
    def update(self, distraction_pos, map_mask):
        self.pos = pygame.math.Vector2(self.hitbox.center)
        target = None
        if distraction_pos:
            dist_vec = pygame.math.Vector2(distraction_pos) - pygame.math.Vector2(self.hitbox.center)
            if dist_vec.length() < self.detection_range:
                target = pygame.math.Vector2(distraction_pos)
                self.status = 'walk'

        if not target:
            player_vec = pygame.math.Vector2(self.player.hitbox.center) - pygame.math.Vector2(self.hitbox.center)
            if player_vec.length() < self.detection_range:
                target = pygame.math.Vector2(self.player.hitbox.center)

        if target:
            direction = (target - pygame.math.Vector2(self.hitbox.center))
            if direction.length() > 5:
                direction = direction.normalize()
                self.hitbox.x += direction.x * self.speed
                if map_mask.overlap(self.hitbox_mask, (self.hitbox.x, self.hitbox.y)):
                    self.hitbox.x -= direction.x * self.speed
                
                self.hitbox.y += direction.y * self.speed
                if map_mask.overlap(self.hitbox_mask, (self.hitbox.x, self.hitbox.y)):
                    self.hitbox.y -= direction.y * self.speed
                    
                self.pos = pygame.math.Vector2(self.hitbox.center)
                self.status = 'walk'
            else:
                self.status = 'IDLE'
        else:
            self.status = 'IDLE'

        self.animate()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.player.gain_xp(self.xp_reward)
            self.kill()