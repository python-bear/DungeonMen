from lib.maps import maps
import random
import os
import math

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame


pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

# Screen setup
WALL_THICKNESS = 32
WALL_GAP = 0
HALF_WALL_THICKNESS = WALL_THICKNESS // 2
MAP_SIZE = 20
MOVEMENT_SPEED = WALL_THICKNESS // 16
CHAR_SIZE = 2.5
HEART_SIZE = CHAR_SIZE + 0.5
HEART_SPACING = 78

DUNGEON_WIDTH = MAP_SIZE * WALL_THICKNESS
DUNGEON_HEIGHT = MAP_SIZE * WALL_THICKNESS

SIDEBAR_WIDTH = 4.5 * WALL_THICKNESS
SIDEBAR_HEIGHT = DUNGEON_HEIGHT

SCREEN_WIDTH = DUNGEON_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = SIDEBAR_HEIGHT if SIDEBAR_WIDTH > DUNGEON_HEIGHT else DUNGEON_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Misc setup.
alkhemikal_font = pygame.font.Font("lib\\fonts\\alkhemikal\\Alkhemikal.ttf", 31)
fps = 64
quarter_fps = fps // 4
current_map = maps[0]

# Basic color constants setup.
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
AQUA = (0, 255, 255)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
SHIELD_BLUE = (73, 122, 200, 128)


def round_to(num, nearest, non=None):
    if non is None:
        return round(num / nearest) * nearest
    else:
        rounded_num = round(num / nearest) * nearest
        rounded_non = round(num / non) * non

        while rounded_num == rounded_non:
            rounded_num += nearest

        return rounded_num


def draw_rectangle(screen, x, y, width=WALL_THICKNESS, height=WALL_THICKNESS, color=RED):
    # Draw a square.
    pygame.draw.rect(screen, color, (x, y, width, height))


def draw_circle(screen, x, y, radius=25, color=YELLOW):
    # Draw a circle.
    pygame.draw.circle(screen, color, (x, y), radius)


def round_coord_to_map(x, y):
    # Calculate the map indexes corresponding to the given coordinates.
    x = math.floor(x / WALL_THICKNESS)
    y = math.floor(y / WALL_THICKNESS)

    return x, y


def tile_snap(x, y):
    # Calculate the map indexes corresponding to the given coordinates.
    map_x, map_y = round_coord_to_map(x, y)

    # Check if the coordinates are within the map boundaries.
    if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
        # Calculate the map index
        map_index = map_y * MAP_SIZE + map_x
        return map_index

    # If the coordinates are outside the map boundaries, return an invalid index.
    return None


def is_valid_movement(x, y, mx, my):
    # Returns true if a coordinate is a valid position for a mobile.
    index = tile_snap(x + mx, y + my)

    if current_map[index] == 0:
        return False

    return True


def key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    raise ValueError("Value not found in the dictionary")


def load_img(image_name, allow_alpha=False):
    if allow_alpha:
        return pygame.image.load(image_name).convert()

    else:
        return pygame.image.load(image_name).convert_alpha()


def scale_image(image, scale=2):
    dimensions = (image.get_width() * scale, image.get_height() * scale)

    scaled_image = pygame.transform.scale(image, dimensions)
    return scaled_image


# Dungeon vars.
full_hearts = {}
knight_skins = {}
item_sprites = {}
knights = monsters = players = used_monster_skins = []
wall_sprite = penny_sprite = dungeon_theme = None
fruit_names = ("apple", "beetroot", "cherries", "mushroom", "pumpkin", "raddish")
knight_skin_names = ("arch", "crud", "diab", "dom", "holy", "maji", "mega", "rusty", "shov", "shy", "syth", "wrak")
monster_skin_names = ("behold", "chopper", "demo", "ender", "gruff", "lich", "neo", "orc", "robe", "spider", "zomb")
empty_heart = scale_image(load_img(f"lib\\sprites\\hearts\\empty_heart.png"), HEART_SIZE)
shield_heart = scale_image(load_img(f"lib\\sprites\\hearts\\shield_heart.png"), HEART_SIZE)
item_codes = {
    "coin": 2,
    "random_fruit": 3,
    "random_buff": 4,
    "raddish": 5,
    "pumpkin": 6,
    "mushroom": 7,
    "apple": 8,
    "cherries": 9,
    "beetroot": 10,
    "gold": 11,
    "gem": 12,
    "silver": 13,
}


class Cursor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Set up the sprite sheet for the cursor.
        self.sprite_index = 0
        self.sprites = []
        for i in range(0, 4):
            self.sprites.append(load_img(f"lib\\sprites\\mouse\\torch_{i}.png"))

        self.image = self.sprites[self.sprite_index]
        self.rect = self.image.get_rect()
        self.click_sound = pygame.mixer.Sound("lib\\sounds\\sfx\\click.wav")

    def increment_sprite(self):
        # Goes to the next sprite in the animation every 1/4 fps rounds.
        self.sprite_index += 1

        if self.sprite_index >= 4 * quarter_fps:
            self.sprite_index = 0

        self.image = self.sprites[self.sprite_index // quarter_fps]

    def click(self):
        self.click_sound.play()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.increment_sprite()


# The following is from stackoverflow @ 
# https://stackoverflow.com/questions/32590131/pygame-blitting-text-with-an-escape-character-or-newline
class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


def multi_line_text(string: str, fnt, rect, fg_col, bg_col=None, justification=0):
    """
    Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    fnt - a font object
    rect - a rect style giving the size of the surface requested.
    fg_col - a three-byte tuple of the rgb value of the text color. ex (0, 0, 0) = BLACK
    bg_col - a three-byte tuple of the rgb value of the background color.
    justification - 0 (default) left-justified, 1 horizontally centered, 2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    final_text = []
    original_text = string.splitlines()
    # Create a series of lines that will fit on the provided rectangle.
    for original_line in original_text:
        if fnt.size(original_line)[0] > rect.width:
            words = original_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if fnt.size(word)[0] >= rect.width:
                    raise TextRectException("The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            added_lines = ""
            for word in words:
                nest_lines = added_lines + word + " "
                # Build the line while the words fit.
                if fnt.size(nest_lines)[0] < rect.width:
                    added_lines = nest_lines
                else:
                    final_text.append(added_lines)
                    added_lines = word + " "
            final_text.append(added_lines)
        else:
            final_text.append(original_line)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)  # Use SRCALPHA to enable transparency
    total_height = 0
    for line in final_text:
        if total_height + fnt.size(line)[1] >= rect.height:
            raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
        temp_surface = None
        if line != "":
            temp_surface = fnt.render(line, True, fg_col)  # Enable anti-aliasing with True
        if temp_surface is not None:
            if justification == 0:
                surface.blit(temp_surface, (0, total_height))
            elif justification == 1:
                surface.blit(temp_surface, ((rect.width - temp_surface.get_width()) // 2, total_height))
            elif justification == 2:
                surface.blit(temp_surface, (rect.width - temp_surface.get_width(), total_height))
            else:
                raise TextRectException("Invalid justification argument: " + str(justification))
        total_height += fnt.size(line)[1]
    return surface
