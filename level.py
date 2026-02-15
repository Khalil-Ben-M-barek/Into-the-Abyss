import pygame
from player import Player
from settings import *
from enemies import Zombie

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = cameragroup()
        self.font = pygame.font.Font(None, 28)
        self.e_pressed = True

        self.distraction_pos = None
        self.distraction_timer = 0

        self.create_map()
    def draw_stamina(self):
        text=f"{int(self.player.stamina)}/{self.player.max_stamina}"
        stamina_surf=self.font.render(text,True,"white")
        self.display_surface.blit(stamina_surf,(10,10))
    def draw_xp(self):
        xp_text = f"{int(self.player.xp_self)} / {self.player.xp}"
        xp_surf = self.font.render(xp_text,True,"white")
        self.display_surface.blit(xp_surf,(1200,10))
        lvl_text=f"level:{self.player.lvl}"
        lvl_surf=self.font.render(lvl_text,True,"white")
        self.display_surface.blit(lvl_surf,(1200,30))
    
    
    def create_map(self):
        self.player = Player((640, 360), self.visible_sprites) # player creation
        self.zombie = Zombie((500, 360),self.player,self.visible_sprites) # zombie creation
        # map creation
        self.ground=pygame.image.load("assets/ground.png").convert_alpha()
        self.ground_w , self.ground_h=self.ground.get_size()


    def run(self):
        # for the xp
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and self.distraction_timer <= 0:
            self.distraction_pos = self.player.rect.center
            self.distraction_timer = 180 # 3 seconds

        if self.distraction_timer > 0:
            self.distraction_timer -= 1
            draw_pos = pygame.math.Vector2(self.distraction_pos) - self.visible_sprites.offset
            pygame.draw.circle(self.display_surface, (100, 100, 100), (int(draw_pos.x), int(draw_pos.y)), 5)
        else:
            self.distraction_pos = None


        if keys[pygame.K_e]: 
            if self.e_pressed:    
                self.player.gain_xp()
            self.e_pressed=False
        else:
            self.e_pressed=True
        # camera follows player
        self.visible_sprites.offset.x=(self.player.rect.centerx-self.visible_sprites.half_width)
        self.visible_sprites.offset.y=(self.player.rect.centery-self.visible_sprites.half_height)
        # drawing ground tiles
        for row in range((height // self.ground_h) + 2):
            for col in range((width // self.ground_w) + 2):
                  pos = pygame.math.Vector2(col*self.ground_w,row*self.ground_h)-self.visible_sprites.offset
                  self.display_surface.blit(self.ground,pos)

        for sprite in self.visible_sprites:
            if isinstance(sprite, Zombie):
                sprite.update(self.distraction_pos)
            else:
                sprite.update()
        self.visible_sprites.custom_draw(self.player)

        

        if self.distraction_pos:
            rock_draw_pos = pygame.math.Vector2(self.distraction_pos) - self.visible_sprites.offset
            pygame.draw.circle(self.display_surface, (100, 100, 100), (int(rock_draw_pos.x), int(rock_draw_pos.y)), 8)

        if self.player.sword_hitbox:
            draw_rect = self.player.sword_hitbox.move(-self.visible_sprites.offset.x, -self.visible_sprites.offset.y)
            pygame.draw.rect(self.display_surface, (255, 200, 0), draw_rect)
            for sprite in self.visible_sprites:
                if isinstance(sprite, Zombie):
                    if self.player.sword_hitbox.colliderect(sprite.rect):
                        sprite.take_damage(self.player.attack_damage)

        

        for sprite in self.visible_sprites:
            if isinstance(sprite, Zombie):
                if sprite.rect.colliderect(self.player.rect):
                    self.player.take_damage(0.5)

        self.draw_hp_bars()
        self.draw_stamina()
        self.draw_xp()

    def draw_hp_bars(self):
        for sprite in self.visible_sprites:
            if hasattr(sprite, 'hp'):
                bar_pos = sprite.rect.topleft - self.visible_sprites.offset
                back_rect = pygame.Rect(bar_pos.x, bar_pos.y - 12, sprite.rect.width, 5)
                pygame.draw.rect(self.display_surface, (50, 50, 50), back_rect)
                
                hp_ratio = sprite.hp / sprite.max_hp
                hp_color = (0, 255, 0) if hp_ratio > 0.4 else (255, 0, 0)
                current_hp_rect = pygame.Rect(bar_pos.x, bar_pos.y - 12, sprite.rect.width * hp_ratio, 5)
                pygame.draw.rect(self.display_surface, hp_color, current_hp_rect)





class cameragroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.half_width=self.display_surface.get_size()[0]//2
        self.half_height=self.display_surface.get_size()[1]//2
        self.offset=pygame.math.Vector2()
    
    def custom_draw(self,player):
        self.offset.x=player.rect.centerx - self.half_width
        self.offset.y=player.rect.centery - self.half_height

        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            offset_pos=sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)