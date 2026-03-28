import pygame
import math
from support import import_sprite_sheet

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, despawn_x=0, despawn_y=0, direction=(-1, 0)):
        super().__init__(groups)
        self.image = pygame.Surface((15, 8))
        self.image.fill("cyan")
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.math.Vector2(direction).normalize()
        self.speed = 5
        self.damage = 100
        self.despawn_x = despawn_x
        self.despawn_y = despawn_y

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        if self.direction.x < 0 and self.rect.right < self.despawn_x:
            self.kill()
        elif self.direction.x > 0 and self.rect.left > self.despawn_x:
            self.kill()

        if self.direction.y < 0 and self.rect.bottom < self.despawn_y:
            self.kill()
        elif self.direction.y > 0 and self.rect.top > self.despawn_y:
            self.kill()

class MiniBoss(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, projectile_spawn_pos, projectile_direction=(-1, 0), projectile_despawn_x=0, projectile_despawn_y=1080):
        super().__init__(groups)
        self.max_hp = 200
        self.hp = 200
        self.original = pygame.image.load("assets/enemies/miniboss.png").convert_alpha()
        self.original = pygame.transform.scale(self.original, (200, 150))
        dx, dy = projectile_direction
        if dx > 0:
            self.image = pygame.transform.rotate(self.original, -90) # Flip horizontally
        elif dy > 0:
            self.image = pygame.transform.rotate(self.original, 90) # Flip vertically
        else:
            self.image = self.original # Default (facing left)

        self.rect = self.image.get_rect(center=pos)
        self.player = player
        self.projectile_spawn_pos = projectile_spawn_pos
        self.projectile_direction = projectile_direction
        self.projectile_despawn_x = projectile_despawn_x
        self.projectile_despawn_y = projectile_despawn_y

        # Needed to limit spawning projectiles to 1 per second
        self.projectile_timer = 0
        self.projectile_delay = 60

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.player.gain_xp(100)
            self.kill()

    def update(self, visible_sprites):
        self.projectile_timer += 1
        if self.projectile_timer >= self.projectile_delay:
            Projectile(self.projectile_spawn_pos, visible_sprites, self.projectile_despawn_x, self.projectile_despawn_y, self.projectile_direction)
            self.projectile_timer = 0

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