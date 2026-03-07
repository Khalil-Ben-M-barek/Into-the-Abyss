import pygame
from player import Player
from settings import *
from enemies import Zombie, Projectile

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = cameragroup()
        self.font = pygame.font.Font(None, 28)
        self.e_pressed = True

        self.distraction_pos = None
        self.distraction_timer = 0

        self.paused = False
        self.menu_index = 0
        self.potions = {
            "Small Potion": 100,
            "Medium Potion": 200,
            "Large Potion": 400
        }
        self.potion_names = list(self.potions.keys()) # Extracting potion names.
        self.p_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.upgrade_menu_active = False
        self.upgrade_options = ["HP", "Stamina", "Attack"]
        self.upgrade_index = 0

        self.current_map_index = 1
        self.teleport_zone = pygame.Rect(1600, 530, 130, 80)

        # Needed to limit spawning projectiles to 1 per second
        self.projectile_timer = 0 
        self.projectile_delay = 60

        self.create_map()


    def draw_upgrade_menu(self):
        w, h = self.display_surface.get_size()
        self.display_surface.fill((0, 0, 50))
        title_surf = self.font.render("LEVEL UP! CHOOSE AN UPGRADE", True, "white")
        self.display_surface.blit(title_surf, (w//2 - 150, 150))

        for i, option in enumerate(self.upgrade_options):
            color = "yellow" if i == self.upgrade_index else "white"
            text_surf = self.font.render(option, True, color)
            self.display_surface.blit(text_surf, (w//2 - 50, 250 + i * 60))

    def handle_upgrade(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP] and not self.up_pressed:
            self.upgrade_index = (self.upgrade_index - 1) % len(self.upgrade_options)
            self.up_pressed = True
        elif not keys[pygame.K_UP]:
            self.up_pressed = False

        if keys[pygame.K_DOWN] and not self.down_pressed:
            self.upgrade_index = (self.upgrade_index + 1) % len(self.upgrade_options)
            self.down_pressed = True
        elif not keys[pygame.K_DOWN]:
            self.down_pressed = False

        if keys[pygame.K_c]:
            selection = self.upgrade_options[self.upgrade_index]
            if selection == "HP":
                self.player.max_hp += 200
                self.player.hp = self.player.max_hp
            elif selection == "Stamina":
                self.player.max_stamina += 20
                self.player.stamina = self.player.max_stamina
            elif selection == "Attack":
                self.player.attack_damage += 2
            
            self.player.waiting_for_upgrade = False
            self.upgrade_menu_active = False



    def draw_stamina(self):
        text=f"{int(self.player.stamina)}/{self.player.max_stamina}"
        stamina_surf=self.font.render(text,True,"yellow")
        self.display_surface.blit(stamina_surf,(10,10))
    def draw_xp(self):
        xp_text = f"{int(self.player.xp_self)} / {self.player.xp}"
        xp_surf = self.font.render(xp_text,True,"yellow")
        self.display_surface.blit(xp_surf,(1400,10))
        lvl_text=f"level:{self.player.lvl}"
        lvl_surf=self.font.render(lvl_text,True,"yellow")
        self.display_surface.blit(lvl_surf,(1400,30))
    
    def create_map(self):
        self.player = Player((100, 400), self.visible_sprites) # original spawn location (100, 400). level exit location (1550, 450).
        self.zombie = Zombie((500, 470),self.player,self.visible_sprites)
        self.zombie = Zombie((500, 100),self.player,self.visible_sprites)
        self.zombie = Zombie((500, 660),self.player,self.visible_sprites)
        self.zombie = Zombie((500, 850),self.player,self.visible_sprites)
        self.zombie = Zombie((900, 850),self.player,self.visible_sprites)
        self.zombie = Zombie((900, 680),self.player,self.visible_sprites)
        self.zombie = Zombie((900, 480),self.player,self.visible_sprites)
        self.zombie = Zombie((900, 280),self.player,self.visible_sprites)
        self.zombie = Zombie((900, 100),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 470),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 150),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 660),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 870),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 770),self.player,self.visible_sprites)
        self.zombie = Zombie((500, 220),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 660),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 870),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 250),self.player,self.visible_sprites)
        self.zombie = Zombie((1200, 360),self.player,self.visible_sprites)
        
        if self.current_map_index == 1:
            map_path = "assets/map.png"
            col_path = "assets/map_collision.png"
        else:
            map_path = "assets/map_2.png"
            col_path = "assets/map_collision_2.png"

        self.map=pygame.image.load(map_path).convert_alpha()
        self.map = pygame.transform.scale(self.map, (1920, 1080))
        self.collision_surf = pygame.image.load(col_path).convert_alpha()
        self.collision_surf = pygame.transform.scale(self.collision_surf, (1920, 1080))
        self.map_mask = pygame.mask.from_surface(self.collision_surf)

        #self.map_w , self.map_h=self.map.get_size()

    def draw_potion_menu(self):
        w, h = self.display_surface.get_size()
        menu_rect = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(self.display_surface, (0, 0, 100), menu_rect)
        title_surf = self.font.render("INVENTORY", True, (255, 255, 255))
        self.display_surface.blit(title_surf, (w // 2 - 100, 100))

        for i, name in enumerate(self.potion_names):
            tx = w // 2 - 100
            ty = 250 + (i * 60)

            text_color = (255, 255, 0) if i == self.menu_index else (255, 255, 255)
            surf = self.font.render(name, True, text_color)
            self.display_surface.blit(surf, (tx, ty))

            if i == self.menu_index:
                pointer_x = tx - 45
                pointer_y = ty + 5
                pygame.draw.polygon(self.display_surface, (255, 255, 255), [(pointer_x, pointer_y), (pointer_x + 20, pointer_y + 10), (pointer_x, pointer_y + 20)])


    def run(self):
        if self.player.waiting_for_upgrade:
            self.upgrade_menu_active = True
            self.paused = True
            self.player.waiting_for_upgrade = False

        keys = pygame.key.get_pressed()

        if not self.upgrade_menu_active:
            if keys[pygame.K_p]:
                if not self.p_pressed:
                    self.paused = not self.paused
                    self.p_pressed = True
            else:
                self.p_pressed = False
                
        if self.paused:
            if self.upgrade_menu_active:
                self.draw_upgrade_menu()
                self.handle_upgrade()
            
            else:
                self.draw_potion_menu()
                if keys[pygame.K_UP]:
                    if not self.up_pressed:
                        self.menu_index = (self.menu_index - 1) % len(self.potion_names)
                        self.up_pressed = True
                else:
                    self.up_pressed = False

                if keys[pygame.K_DOWN]:
                    if not self.down_pressed:
                        self.menu_index = (self.menu_index + 1) % len(self.potion_names)
                        self.down_pressed = True
                else:
                    self.down_pressed = False

                if keys[pygame.K_c]:
                    selected_item = self.potion_names[self.menu_index]
                    heal_amount = self.potions[selected_item]
                    self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
                    self.paused = False

                
            
  
        if not self.paused:
            self.projectile_timer += 1
            if self.projectile_timer >= self.projectile_delay:
                projectile_spawn_pos = (self.teleport_zone.left - 80, self.teleport_zone.centery + 20)
                Projectile(projectile_spawn_pos, self.visible_sprites)
                self.projectile_timer = 0

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
                    self.player.gain_xp(55)
                self.e_pressed=False
            else:
                self.e_pressed=True
            # camera follows player
            self.visible_sprites.offset.x=(self.player.rect.centerx-self.visible_sprites.half_width)
            self.visible_sprites.offset.y=(self.player.rect.centery-self.visible_sprites.half_height)
            # drawing map tiles
            """for row in range((height // self.map_h) + 2):
                for col in range((width // self.map_w) + 2):
                    pos = pygame.math.Vector2(col*self.map_w,row*self.map_h)-self.visible_sprites.offset
                    self.display_surface.blit(self.map,pos)
                """
            map_offset_pos = pygame.math.Vector2(0, 0) - self.visible_sprites.offset
            self.display_surface.blit(self.map, map_offset_pos)

            for sprite in self.visible_sprites:
                if isinstance(sprite, Zombie):
                    sprite.update(self.distraction_pos, self.map_mask)
                elif isinstance(sprite, Player):
                    sprite.update(self.map_mask)
                else:
                    sprite.update()

            for sprite in self.visible_sprites:
                if isinstance(sprite, Projectile):
                    if sprite.rect.colliderect(self.player.hitbox):
                        self.player.take_damage(sprite.damage)
                        sprite.kill()
            self.visible_sprites.custom_draw(self.player)


            for sprite in self.visible_sprites:
                if isinstance(sprite, Zombie):
                    z_debug = sprite.hitbox.copy()
                    z_debug.topleft -= self.visible_sprites.offset
                    pygame.draw.rect(self.display_surface, (0, 0, 255), z_debug, 2)


            if self.distraction_pos:
                rock_draw_pos = pygame.math.Vector2(self.distraction_pos) - self.visible_sprites.offset
                pygame.draw.circle(self.display_surface, (100, 100, 100), (int(rock_draw_pos.x), int(rock_draw_pos.y)), 8)

            if self.player.sword_hitbox:
                for sprite in self.visible_sprites:
                    if isinstance(sprite, Zombie):
                        if self.player.sword_hitbox.colliderect(sprite.rect):
                            sprite.take_damage(self.player.attack_damage)

            

            for sprite in self.visible_sprites:
                if isinstance(sprite, Zombie):
                    if sprite.hitbox.colliderect(self.player.hitbox):
                        self.player.take_damage(2)

            self.draw_hp_bars()
            self.draw_stamina()
            self.draw_xp()

            t_debug = self.teleport_zone.copy()
            t_debug.topleft -= self.visible_sprites.offset
            if self.player.hitbox.colliderect(self.teleport_zone):
                pygame.time.delay(120)
                for sprite in self.visible_sprites:
                    if isinstance(sprite, Zombie):
                        sprite.kill()
                self.current_map_index +=1
                self.create_map()


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

                hp_text = f"{int(sprite.hp)}"
                text_surf = self.font.render(hp_text, True, "white")
                self.display_surface.blit(text_surf, (bar_pos.x, bar_pos.y - 30))




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
