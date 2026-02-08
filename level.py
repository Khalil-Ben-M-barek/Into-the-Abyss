import pygame
from player import Player
from settings import *
from enemies import Zombie
class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = cameragroup()
        self.font = pygame.font.Font(None, 28)
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
        self.player = Player((640, 360), self.visible_sprites)#player creation
        self.zombie = Zombie((500, 360),self.player,self.visible_sprites)#zombie creation
        #map creation
        self.ground=pygame.image.load("assets/ground.png").convert_alpha()
        self.ground_w , self.ground_h=self.ground.get_size()


    def run(self):
        #for the xp
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]: 
            if self.space_pressed:    
                self.player.gain_xp()
            self.space_pressed=False
        else:
            self.space_pressed=True
        #camera follows player
        self.visible_sprites.offset.x=(self.player.rect.centerx-self.visible_sprites.half_width)
        self.visible_sprites.offset.y=(self.player.rect.centery-self.visible_sprites.half_height)
        #drawing ground tiles
        for row in range((height // self.ground_h) + 2):
            for col in range((width // self.ground_w) + 2):
                  pos = pygame.math.Vector2(col*self.ground_w,row*self.ground_h)-self.visible_sprites.offset
                  self.display_surface.blit(self.ground,pos)
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.draw_stamina()
        self.draw_xp()


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