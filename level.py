import pygame
from player import Player, Item
from settings import *
from enemies import Zombie, Projectile, MiniBoss

LEVELS = [
    {   # Level 1
        "map": "assets/map.png",
        "collision": "assets/map_collision.png",
        "map_size": (1920, 1080),
        "player_spawn": (100, 400),
        "teleport_zone": (1600, 530, 130, 80),
        "zombies": [
            (500, 470), (500, 100), (500, 660), (500, 850), (500, 220),
            (900, 850), (900, 680), (900, 480), (900, 280), (900, 100),
            (1200, 470), (1200, 150), (1200, 660), (1200, 870),
            (1200, 770), (1200, 250), (1200, 360)
        ],
        "items": [
            (400, 250), (1100, 900), (1350, 100), (400, 100)
        ],
        "minibosses": [{"pos": (1500, 580), "projectile_spawn_pos": (1500, 580), "projectile_direction": (-1, 0), "projectile_despawn_x": 400, "projectile_despawn_y": 0}]
    },

    {   # Level 2
        "map": "assets/map_2.png",
        "collision": "assets/map_collision_2.png",
        "map_size": (1920, 1080),
        "player_spawn": (100, 400),
        "teleport_zone": (1780, 450, 130, 80),
        "zombies": [
            (780, 220), (750, 240), (800, 250),
            (900, 550), (920, 620), (900, 580), 
            (400, 700), (430, 780), (480, 780),
            (1130, 200), (1140, 180), (1170, 280), (1190, 300),
            (1130, 500), (1330, 400), (1190, 500), (1400, 400), 
            (1400, 700), (1350, 700), (1330, 800),
            (1030, 400), (1070, 420)
        ],
        "items": [
            (820, 320), (1050, 400), (1120, 190), (380, 650), (1040, 630), (1430, 720)
        ],
        "minibosses": [
            {"pos": (1650, 460), "projectile_spawn_pos": (1650, 425), "projectile_direction": (-1, 0), "projectile_despawn_x": 380, "projectile_despawn_y": 0}, 
            {"pos": (1570, 270), "projectile_spawn_pos": (1550, 280), "projectile_direction": (0, 1), "projectile_despawn_x": 220, "projectile_despawn_y": 870}
        ]
    }
]


ITEM_EFFECTS = {
    "Small Potion": {"type": "heal", "amount": 200},
    "Medium Potion": {"type": "heal", "amount": 400},
    "Large Potion": {"type": "heal", "amount": 800},
    "Distraction Object": {"type": "distraction"}
}

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = cameragroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.font = pygame.font.Font(None, 28)

        self.distraction_pos = None
        self.distraction_timer = 0

        self.item_sprites = pygame.sprite.Group()
        self.paused = False
        self.menu_index = 0

        self.upgrade_menu_active = False
        self.upgrade_options = ["HP", "Stamina", "Attack"]
        self.upgrade_index = 0

        self.p_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.e_pressed = True

        self.current_map_index = 0
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
            self.paused = False

    def draw_stamina(self):
        text = f"{int(self.player.stamina)}/{self.player.max_stamina}"
        stamina_surf = self.font.render(text, True, "yellow")
        self.display_surface.blit(stamina_surf, (10, 10))
    def draw_xp(self):
        xp_text = f"{int(self.player.xp_self)} / {self.player.xp}"
        xp_surf = self.font.render(xp_text, True, "yellow")
        self.display_surface.blit(xp_surf, (1400, 10))
        lvl_text=f"level: {self.player.lvl}"
        lvl_surf=self.font.render(lvl_text, True, "yellow")
        self.display_surface.blit(lvl_surf, (1400, 30))
    
    def create_map(self, save_stats=True):
        # Saving stats between levels except after death
        if hasattr(self, "player") and save_stats:
            saved_hp = self.player.hp
            saved_max_hp = self.player.max_hp
            saved_stamina = self.player.stamina
            saved_max_stam = self.player.max_stamina
            saved_damage = self.player.attack_damage
            saved_inventory = self.player.inventory[:]
            saved_xp = self.player.xp
            saved_xp_self = self.player.xp_self
            saved_lvl = self.player.lvl
        else:
            saved_hp = saved_max_hp = saved_stamina = saved_max_stam = None
            
        # Clearing the map
        self.visible_sprites.empty()
        self.item_sprites.empty()
        self.obstacle_sprites.empty()

        self.player = Player(LEVELS[self.current_map_index]["player_spawn"], self, self.visible_sprites)

        if saved_hp is not None:
            self.player.hp = saved_hp
            self.player.max_hp = saved_max_hp
            self.player.stamina = saved_stamina
            self.player.max_stamina = saved_max_stam
            self.player.attack_damage = saved_damage
            self.player.inventory = saved_inventory
            self.player.xp = saved_xp
            self.player.xp_self = saved_xp_self
            self.player.lvl = saved_lvl

        for pos in LEVELS[self.current_map_index]["zombies"]:
            Zombie(pos, self.player, self.visible_sprites)
        
        for pos in LEVELS[self.current_map_index]["items"]:
            Item(pos, self.visible_sprites, self.item_sprites)

        self.map = pygame.image.load(LEVELS[self.current_map_index]["map"]).convert_alpha()
        self.map = pygame.transform.scale(self.map, LEVELS[self.current_map_index]["map_size"])
        self.collision_surf = pygame.image.load(LEVELS[self.current_map_index]["collision"]).convert_alpha()
        self.collision_surf = pygame.transform.scale(self.collision_surf, LEVELS[self.current_map_index]["map_size"])
        self.map_mask = pygame.mask.from_surface(self.collision_surf)
        self.teleport_zone = pygame.Rect(LEVELS[self.current_map_index]["teleport_zone"])

        miniboss_data = LEVELS[self.current_map_index].get("minibosses")
        if miniboss_data:
            for mb in miniboss_data:
                MiniBoss(mb["pos"], [self.visible_sprites, self.obstacle_sprites], self.player, mb["projectile_spawn_pos"], mb.get("projectile_direction", (-1, 0)), mb.get("projectile_despawn_x", 0), mb.get("projectile_despawn_y", 1080))

    def next_level(self):
        next_index = self.current_map_index + 1
        if next_index < len(LEVELS):
            self.current_map_index = next_index
            pygame.time.delay(120)
            self.create_map()

    def draw_inventory_menu(self):
        w, h = self.display_surface.get_size()
        menu_rect = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(self.display_surface, (0, 0, 100), menu_rect)
        title_surf = self.font.render("INVENTORY [ C ]: use item | [ P ]: close menu", True, (255, 255, 255))
        self.display_surface.blit(title_surf, (w // 2 - 100, 100))

        if not self.player.inventory:
            empty = self.font.render("— inventory is empty —", True, (180, 180, 180))
            self.display_surface.blit(empty, (w // 2 - 110, 280))
            return

        self.menu_index = min(self.menu_index, len(self.player.inventory) - 1) # Ensures the cursor remains accurate just in case

        for i, name in enumerate(self.player.inventory):
            tx = w // 2 - 100
            ty = 250 + (i * 60)

            text_color = "yellow" if i == self.menu_index else "white"
            surf = self.font.render(name, True, text_color)
            self.display_surface.blit(surf, (tx, ty))

            if i == self.menu_index:
                pointer_x = tx - 45
                pointer_y = ty + 5
                pygame.draw.polygon(self.display_surface, "white", [(pointer_x, pointer_y), (pointer_x + 20, pointer_y + 10), (pointer_x, pointer_y + 20)])


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
                self.draw_inventory_menu()
                if keys[pygame.K_UP]:
                    if not self.up_pressed:
                        self.menu_index = (self.menu_index - 1) % max(len(self.player.inventory), 1)
                        self.up_pressed = True
                else:
                    self.up_pressed = False

                if keys[pygame.K_DOWN]:
                    if not self.down_pressed:
                        self.menu_index = (self.menu_index + 1) % max(len(self.player.inventory), 1)
                        self.down_pressed = True
                else:
                    self.down_pressed = False

                if keys[pygame.K_c] and self.player.inventory:
                    selected_item = self.player.inventory[self.menu_index]
                    effect = ITEM_EFFECTS[selected_item] 
                    if effect["type"] == "heal":
                        self.player.hp = min(self.player.max_hp, self.player.hp + effect["amount"])
                    elif effect["type"] == "distraction":
                        self.distraction_pos = self.player.rect.center
                        self.distraction_timer = 180
                    self.player.inventory.pop(self.menu_index)
                    self.paused = False

        if not self.paused:
            if keys[pygame.K_d] and self.distraction_timer <= 0:
                if "Distraction Object" in self.player.inventory:
                    self.player.inventory.remove("Distraction Object")
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
                    self.player.gain_xp(50)
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
                    sprite.update(self.map_mask, self.obstacle_sprites)
                elif isinstance(sprite, MiniBoss):
                    sprite.update(self.visible_sprites)
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

            for item in self.item_sprites:
                if self.player.hitbox.colliderect(item.rect):
                    item.pick_up(self.player)

            if self.distraction_pos:
                rock_draw_pos = pygame.math.Vector2(self.distraction_pos) - self.visible_sprites.offset
                pygame.draw.circle(self.display_surface, (100, 100, 100), (int(rock_draw_pos.x), int(rock_draw_pos.y)), 8)

            if self.player.sword_hitbox:
                for sprite in self.visible_sprites:
                    if isinstance(sprite, (Zombie, MiniBoss)):
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
                self.next_level()
            
    def draw_hp_bars(self):
        for sprite in self.visible_sprites:
            if hasattr(sprite, "hp"):
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
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0]//2
        self.half_height = self.display_surface.get_size()[1]//2
        self.offset=pygame.math.Vector2()
    
    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
