import random
import os
import math

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame


pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

# Font setup.
ALKHEMIKAL_FNT = pygame.font.Font("lib\\fonts\\alkhemikal\\Alkhemikal.ttf", 31)

# Basic color constants setup.
COLORS = {
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "aqua": (0, 255, 255),
    "blue": (0, 0, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    
    "shield_blue": (73, 122, 200, 128),
    "l_tan": (238, 175, 123),
    "tan": (200, 140, 97),
    "brown": (51, 34, 22),
    "p_1": (146, 15, 240),
    "p_2": (240, 34, 15),
    "p_3": (109, 240, 15),
    "p_4": (15, 221, 240),
}


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


def draw_rectangle(screen, x, y, width, height, color=COLORS["red"]):
    # Draw a square.
    pygame.draw.rect(screen, color, (x, y, width, height))


def draw_circle(screen, x, y, radius=25, color=COLORS["yellow"]):
    # Draw a circle.
    pygame.draw.circle(screen, color, (x, y), radius)


def round_coord_to_map(x, y, wall_thickness):
    # Calculate the map indexes corresponding to the given coordinates.
    x = math.floor(x / wall_thickness)
    y = math.floor(y / wall_thickness)

    return x, y


def tile_snap(x, y, map_size, wall_thickness):
    # Calculate the map indexes corresponding to the given coordinates.
    map_x, map_y = round_coord_to_map(x, y, wall_thickness)

    # Check if the coordinates are within the map boundaries.
    if 0 <= map_x < map_size and 0 <= map_y < map_size:
        # Calculate the map index
        map_index = map_y * map_size + map_x
        return map_index

    # If the coordinates are outside the map boundaries, return an invalid index.
    return None


def create_walls(map_data, wall_thickness):
    walls = []
    width = 20  # Width of the map

    for i in range(len(map_data)):
        x = i % width
        y = i // width

        if map_data[i] == 0:
            wall = Wall(x, y, wall_thickness)
            walls.append(wall)

    return walls


def is_valid_movement(x, y, mx, my, movement_speed, char_size, map_size, wall_thickness, map_data=None, walls=None,):
    # Returns True if a coordinate is a valid position for a mobile.
    if walls is not None:
        char_dim = char_size * 7
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
        index = tile_snap(x + mx, y + my, map_size, wall_thickness)

        if map_data[index] == 0:
            return False

        return True


def key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    raise ValueError("Value not found in the dictionary")


def change_img_hue(image, hue=120):
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
            # Add the provided hue value to the current hue and wrap to under 360
            new_hue = (h + hue) % 360
            color.hsla = int(new_hue), int(s), int(l), int(a)
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
    def __init__(self, x, y, wall_thickness):
        super().__init__()
        self.WALL_THICKNESS = wall_thickness
        self.image = pygame.Surface((self.WALL_THICKNESS, self.WALL_THICKNESS))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * self.WALL_THICKNESS, y * self.WALL_THICKNESS)
