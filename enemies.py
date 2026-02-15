import pygame
import math
from support import import_sprite_sheet

class Zombie(pygame.sprite.Sprite):
    def __init__(self, pos, player, *groups):
        super().__init__(*groups)
        self.max_hp = 100
        self.hp = 100
        self.is_alive = True
        self.flash_timer = 0
        self.distraction = None
        self.state = "IDLE"
        self.player = player
        self.status = 'IDLE'
        self.prev_status = self.status
        self.frame_index = 0

        self.speed = 1.7
        self.detection_range = 300
        self.xp_reward = 50

        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15

        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy()

    def import_assets(self):
        path = 'assets/enemies/'
        frame_width=64
        frame_height=64
        self.animations = {
        'IDLE': import_sprite_sheet(path + 'IDLE.png', frame_width, frame_height),
        'walk': import_sprite_sheet(path + 'walk.png', frame_width, frame_height)
        }

    def distance_to_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        return math.hypot(dx, dy)

    def move_towards_player(self):
        direction = pygame.math.Vector2(
            self.player.rect.centerx - self.rect.centerx,
            self.player.rect.centery - self.rect.centery
        )
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()
            self.rect.centerx += direction.x * self.speed
            self.rect.centery += direction.y * self.speed
            self.status = 'walk'
        else:
            self.status = 'IDLE'


    def animate(self):
        if self.status != self.prev_status:
            self.frame_index = 0
            self.prev_status = self.status

        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(255)

    def update(self, distraction_pos):
        target = None
        self.state = "IDLE"
        if distraction_pos:
            dist_vec = pygame.math.Vector2(distraction_pos) - pygame.math.Vector2(self.rect.center)
            if dist_vec.length() < self.detection_range:
                target = pygame.math.Vector2(distraction_pos)
                self.state = "DISTRACTED"

        if not target:
            player_vec = pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)
            if player_vec.length() < self.detection_range:
                target = pygame.math.Vector2(self.player.rect.center)
                self.state = "CHASE"
            else:
                self.state = "IDLE"

        if target and self.state != "IDLE":
            direction = (target - pygame.math.Vector2(self.rect.center))
            if direction.length() > 5:
                direction = direction.normalize()
                self.rect.x += direction.x * self.speed
                self.rect.y += direction.y * self.speed
                self.status = 'walk'
        else:
            self.status = 'IDLE'

        self.animate()

    def take_damage(self, amount):
        self.hp -= amount
        self.flash_timer = 5
        if self.hp <= 0:
            self.is_alive = False
            self.player.gain_xp(self.xp_reward)
            self.kill()