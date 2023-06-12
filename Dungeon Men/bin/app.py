import sys

from bin.sprites import *
from bin.utils import *


# Screen setup
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Men")

background = pygame.image.load("lib\\sprites\\environ\\floor.png")
background_width = background.get_width()
background_height = background.get_height()

# Clock setup
clock = pygame.time.Clock()

# Setup cursor
pygame.mouse.set_visible(False)
cursor = Cursor(100, 100)

cursor_sprites = pygame.sprite.Group()
cursor_sprites.add(cursor)

# Make knight classes
# rusty_knight = Knight(350, 350, 'rusty', 'phallanax')
#
# knight_sprites = pygame.sprite.Group()
# knight_sprites.add(rusty_knight)


def draw_screen():
    screen.blit(background, (0, 0))

    # Calculate the number of tiles needed in both x and y directions
    tiles_x = screen.get_width() // background_width + 1
    tiles_y = screen.get_height() // background_height + 1

    # Loop to tile the background image
    for y in range(tiles_y):
        for x in range(tiles_x):
            screen.blit(background, (x * background_width, y * background_height))

    # knight_sprites.draw(screen)
    cursor_sprites.update()
    cursor_sprites.draw(screen)
    pygame.display.flip()


def run():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                cursor.click()

        draw_screen()

        clock.tick(fps)
