import pygame,sys
from settings import *
from level import Level
class Game:
    def __init__(self):
        # Initialization
        pygame.init()
        self.screen = pygame.display.set_mode((0,0), pygame.RESIZABLE)
        pygame.display.set_caption("Into the Abyss")
        self.clock=pygame.time.Clock()
        self.level=Level()
        
    def run(self):
        # Game loop
        while True:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_n:
                        self.level.next_level()

            self.screen.fill("black") # Old color #71B5D1
            self.level.run()
            pygame.display.flip()


if __name__== '__main__':
    game=Game()
    game.run()