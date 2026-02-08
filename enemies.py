import pygame
import math
from support import import_sprite_sheet

class Zombie(pygame.sprite.Sprite):
    def __init__(self, pos, player, *groups):
        super().__init__(*groups)
        self.player = player
        self.status = 'idle'
        self.prev_status = self.status
        self.frame_index = 0

        self.speed = 1.7
        self.detection_range = 250

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
        'idle': import_sprite_sheet(path + 'idle.png', frame_width, frame_height),
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

        if distance > 20:
            direction = direction.normalize()
            self.rect.center += direction * self.speed
            self.status = 'walk'
        else:
            self.status = 'idle'


    def animate(self):
        if self.status not in self.animations:
            self.status='idle'
        animation = self.animations[self.status]
        if len(animation)==0:
            return
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
    def update(self):
        if self.distance_to_player() <= self.detection_range:
            self.move_towards_player()
        else:
            self.status = 'idle'

        self.animate()
