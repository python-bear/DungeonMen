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
POSSIBLE_CHAR_SIZES = (1, 1.5, 2, 2.5)
HEART_SIZE = 2.5 + 0.5
HEART_SPACING = 78

DUNGEON_WIDTH = MAP_SIZE * WALL_THICKNESS
DUNGEON_HEIGHT = MAP_SIZE * WALL_THICKNESS

SIDEBAR_WIDTH = 4.5 * WALL_THICKNESS
SIDEBAR_HEIGHT = DUNGEON_HEIGHT

SCREEN_WIDTH = DUNGEON_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = SIDEBAR_HEIGHT if SIDEBAR_WIDTH > DUNGEON_HEIGHT else DUNGEON_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

program_icon = pygame.image.load("lib\\sprites\\gui\\icon_5.png")
pygame.display.set_icon(program_icon)

# Misc setup.
alkhemikal_font = pygame.font.Font("lib\\fonts\\alkhemikal\\Alkhemikal.ttf", 31)
fps = 64
quarter_fps = fps // 4
current_map = None
current_walls = None
wall_collision_detection = False
mobile_collision_detection = True

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
L_TAN = (238, 175, 123)
TAN = (200, 140, 97)
BROWN = (51, 34, 22)
P_1_COL = (146, 15, 240)
P_2_COL = (240, 34, 15)
P_3_COL = (109, 240, 15)
P_4_COL = (15, 221, 240)

# Speed conversions
speed_conversions = {
    "snail": WALL_THICKNESS // 22,
    "slow": WALL_THICKNESS // 19,
    "medium": WALL_THICKNESS // 16,
    "fast": WALL_THICKNESS // 8,
    "flash": WALL_THICKNESS // 4
}

# Songs
pygame.mixer.music.load("lib\\sounds\\music\\vafen.wav")


def round_to(num, nearest, non=None):
    if non is None:
        return round(num / nearest) * nearest
    else:
        rounded_num = round(num / nearest) * nearest
        rounded_non = round(num / non) * non

        while rounded_num == rounded_non:
            rounded_num += nearest

        return rounded_num


def remove_all(iterable, target):
    return [i for i in iterable if i != target]


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


def create_walls(map_data):
    walls = []
    width = 20  # Width of the map
    height = len(map_data) // width

    for i in range(len(map_data)):
        x = i % width
        y = i // width

        if map_data[i] == 0:
            wall = Wall(x, y)
            walls.append(wall)

    return walls


def is_valid_movement(x, y, mx, my, movement_speed, map_data=None, walls=None):
    # Returns True if a coordinate is a valid position for a mobile.
    if walls is not None:
        char_dim = CHAR_SIZE * 7
        future_x = x + mx * movement_speed
        future_y = y + my * movement_speed

        # Calculate the bounding box for the mobile's future position
        mobile_rect = pygame.Rect(future_x - char_dim / 2, future_y - char_dim / 2, char_dim, char_dim)

        # Check for collision with walls
        for wall in walls:
            if mobile_rect.colliderect(wall.rect):
                return False

        return True
    elif map_data is not None:
        index = tile_snap(x + mx, y + my)

        if map_data[index] == 0:
            return False

        return True


def key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    raise ValueError("Value not found in the dictionary")


def change_img_hue(image, hue):
    img_copy = image.copy()
    pixels = pygame.PixelArray(img_copy)
    # Iterate over every pixel
    for x in range(img_copy.get_width()):
        for y in range(img_copy.get_height()):
            # Turn the pixel data into an RGB tuple
            rgb = img_copy.unmap_rgb(pixels[x][y])
            # Get a new color object using the RGB tuple and convert to HSLA
            color = pygame.Color(*rgb)
            h, s, l, a = color.hsla
            # Add 120 to the hue (or however much you want) and wrap to under 360
            color.hsla = (int(h) + 120) % 360, int(s), int(l), int(a)
            # Assign directly to the pixel
            pixels[x][y] = color
    # The old way of closing a PixelArray object
    del pixels
    return img_copy


def load_img(image_name, allow_alpha=False):
    if allow_alpha:
        return pygame.image.load(image_name).convert()

    else:
        return pygame.image.load(image_name).convert_alpha()


def scale_image(image, scale=2):
    dimensions = (image.get_width() * scale, image.get_height() * scale)

    scaled_image = pygame.transform.scale(image, dimensions)
    return scaled_image


def movement_options(movement_speed):
    return [(movement_speed, 0), (-movement_speed, 0), (0, movement_speed), (0, -movement_speed)]


def play_video(file_path):
    if os.name == 'nt':  # for Windows
        os.startfile(file_path)

    elif os.name == 'posix':  # for Linux/Mac OS
        os.system(f'open "{file_path}"')


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WALL_THICKNESS, WALL_THICKNESS))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * WALL_THICKNESS, y * WALL_THICKNESS)


# Dungeon vars.
full_hearts = {}
knight_skins = {}
true_knight_skins = {}
alt_knight_skins = {}
item_sprites = {}
monsters = players = used_monster_skins = []
wall_sprite = dungeon_theme = None
fruit_names = ("apple", "beetroot", "cherries", "mushroom", "pumpkin", "radish", "gem")
knight_skin_names = ("arch", "skul", "diab", "dom", "syth", "crud", "plag", "maji", "mega", "pink", "holy", "wrak",
                     "shov", "shy", "rusty")
secret_knight_skin_names = ("andy", "kirb", "ngor", "spawn", "gpt")
monster_skin_names = ("behold", "chopper", "demo", "ender", "gruff", "lich", "neo", "orc", "robe", "spider", "zomb")
empty_heart = scale_image(load_img(f"lib\\sprites\\hearts\\empty_heart.png"), HEART_SIZE)
shield_heart = scale_image(load_img(f"lib\\sprites\\hearts\\shield_heart.png"), HEART_SIZE)
penny_sprite = scale_image(load_img(f"lib\\sprites\\items\\penny.png"))
gold_sprite = scale_image(load_img(f"lib\\sprites\\items\\gold.png"))
silver_sprite = scale_image(load_img(f"lib\\sprites\\items\\coin.png"))
gem_sprite = scale_image(load_img(f"lib\\sprites\\items\\gem.png"))
banana_sprite = scale_image(load_img(f"lib\\sprites\\items\\banana.png"), CHAR_SIZE)
banana_time = False
music_is_paused = False
item_codes = {
    "coin": 2,
    "random_fruit": 3,
    "random_buff": 4,
    "radish": 5,
    "pumpkin": 6,
    "mushroom": 7,
    "apple": 8,
    "cherries": 9,
    "beetroot": 10,
    "gem": 11,
    "gold": 12,
    "silver": 13,
}

# Knight setup and creation.
for skin in (*knight_skin_names, *secret_knight_skin_names):
    true_knight_skins[skin] = scale_image(load_img(f"lib\\sprites\\helms\\{skin}_helm.png"), 1)
    knight_skins[skin] = scale_image(load_img(f"lib\\sprites\\helms\\{skin}_helm.png"), CHAR_SIZE)
    alt_knight_skins[skin] = change_img_hue(knight_skins[skin], 90)

# Get among us skins loaded.
among_us_skins = []
for i in range(0, 6):
    among_us_skins.append(scale_image(load_img(f"lib\\sprites\\enemies\\among_{i}.png"), CHAR_SIZE))
