import random
import sys
import time

from bin.utils import *
from bin.sprites import *

# Screen setup.
pygame.display.set_caption("Dungeon Men")

background = load_img("lib\\sprites\\environ\\floor.png")
background_width = background.get_width()
background_height = background.get_height()

# Clock setup (for fps).
clock = pygame.time.Clock()

# Misc setup.
game_paused = False

# Setup cursor.
pygame.mouse.set_visible(False)
cursor = Cursor(100, 100)

cursor_sprites = pygame.sprite.Group()
cursor_sprites.add(cursor)


def init_dungeon(player_ids, num_monsters, override_monster_skins=None):
    """
    Parameters
    ----------
    player_ids: A list of player name, skin tuples, up to for, one for each player.
    num_monsters: The number of monsters to be in the dungeon.
    override_monster_skins: The skins that will be used for the monsters, if None, all will be used.
    """
    global knights, monsters, wall_sprite, penny_sprite, dungeon_theme, players, full_hearts, used_monster_skins

    # Dungeon setup.
    dungeon_theme = random.choice(('light', 'dark'))

    wall_sprite = load_img(f"lib\\sprites\\environ\\{dungeon_theme}\\wall_{random.randint(0, 14)}.png")
    wall_sprite = scale_image(wall_sprite)
    penny_sprite = load_img(f"lib\\sprites\\items\\penny.png")
    penny_sprite = scale_image(penny_sprite)

    # Get the fruit sprites loaded.
    for fruit in fruit_names:
        item_sprites[fruit] = scale_image(load_img(f"lib\\sprites\\items\\{fruit}.png"), CHAR_SIZE)

    # Knight setup and creation.
    for skin in knight_skin_names:
        knight_skins[skin] = scale_image(load_img(f"lib\\sprites\\helms\\{skin}_helm.png"), CHAR_SIZE)
    knights = pygame.sprite.Group()

    # Create knights for all of the players.
    for i in range(len(player_ids)):
        full_hearts[player_ids[i][1]] = scale_image(load_img(f"lib\\sprites\\hearts\\{player_ids[i][1]}_heart.png"),
                                                    HEART_SIZE)
        if i + 1 == 1:
            knights.add(Knight(1, 1, player_ids[i][0], 1, player_ids[i][1]))
        elif i + 1 == 2:
            knights.add(Knight(18, 18, player_ids[i][0], 2, player_ids[i][1]))
        elif i + 1 == 3:
            knights.add(Knight(1, 18, player_ids[i][0], 3, player_ids[i][1]))
        else:
            knights.add(Knight(18, 1, player_ids[i][0], 4, player_ids[i][1]))

    # Monster setup and creation.
    if override_monster_skins is None:
        used_monster_skins = monster_skin_names

    else:
        used_monster_skins = override_monster_skins

    monsters = pygame.sprite.Group()

    # Create randomized monsters.
    for i in range(num_monsters):
        monsters.add(Monster(random.randint(9, 10), 9, random.choice(used_monster_skins)))

    for monster in monsters:
        monster.choose_random_move()

    # Randomize the items.
    for i, v in enumerate(current_map):
        if v == 3:
            current_map[i] = item_codes[random.choice(fruit_names)]


def draw_screen():
    screen.blit(background, (0, 0))

    # Calculate the number of tiles needed in both x and y directions.
    tiles_x = screen.get_width() // background_width + 1
    tiles_y = screen.get_height() // background_height + 1

    # Loop to tile the background image.
    for y in range(tiles_y):
        for x in range(tiles_x):
            screen.blit(background, (x * background_width, y * background_height))

    # Draw knights.
    for knight in knights:
        knight.draw()

    # Draw the monsters.
    for monster in monsters:
        monster.draw()

    # Draw walls.
    for index in range(len(current_map)):
        tile = current_map[index]

        x = (index % MAP_SIZE) * WALL_THICKNESS
        y = (index // MAP_SIZE) * WALL_THICKNESS

        if tile == 0:
            if wall_sprite:
                screen.blit(wall_sprite, (x, y))

            else:
                draw_rectangle(screen, x, y, WALL_THICKNESS - WALL_GAP, WALL_THICKNESS - WALL_GAP)

        elif tile == 2:
            if penny_sprite:
                screen.blit(penny_sprite, (x, y))

            else:
                draw_circle(screen, x + HALF_WALL_THICKNESS, y + HALF_WALL_THICKNESS, 5)

        elif tile not in (1, 3, 4):
            screen.blit(item_sprites[key_from_value(item_codes, tile)], (x + 3, y + 3))

    # Draw the scores and player names.
    text = ""
    for knight in knights:
        text += f"\n{knight.name}\n\n{' ' * max(8 - len(str(knight.score)), 0)}{knight.score}\n\n"

    text_surface = multi_line_text(text, alkhemikal_font, pygame.Rect(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT), WHITE)

    text_rect = text_surface.get_rect()
    text_rect.topleft = (DUNGEON_WIDTH + WALL_THICKNESS, HALF_WALL_THICKNESS)

    screen.blit(text_surface, text_rect)

    # Draw cursor.
    cursor_sprites.update()
    cursor_sprites.draw(screen)

    # Finish drawing.
    pygame.display.flip()


def update_positions():
    # Update the positions of all mobiles.
    global game_paused, MOVEMENT_SPEED, monster_movement_options

    if game_paused:
        return

    # Update the knights.
    for knight in knights:
        if is_valid_movement(knight.x, knight.y, knight.mx * knight.speed, knight.my * knight.speed):
            knight.x += knight.mx * knight.speed
            knight.y += knight.my * knight.speed

        knight_pos_index = tile_snap(knight.x, knight.y)

        # Check for knight item/coin collisions.
        if knight.retreat_countdown == 0:
            if current_map[knight_pos_index] == 2:
                current_map[knight_pos_index] = 1
                knight.score += 1

            elif current_map[knight_pos_index] == 5:
                current_map[knight_pos_index] = 1
                knight.score += 10

            elif current_map[knight_pos_index] == 6:
                current_map[knight_pos_index] = 1
                knight.speed /= 2

            elif current_map[knight_pos_index] == 7:
                current_map[knight_pos_index] = 1
                knight.speed /= 2
                for monster in monsters:
                    monster.speed /= 2

            elif current_map[knight_pos_index] == 8:
                current_map[knight_pos_index] = 1
                knight.shield_countdown = fps * 7
                knight.has_shield = True
                knight.update_hearts()

            elif current_map[knight_pos_index] == 9:
                current_map[knight_pos_index] = 1
                knight.speed *= 2

            elif current_map[knight_pos_index] == 10:
                current_map[knight_pos_index] = 1
                knight.score += random.randint(-10, 20)

    # Update the monsters.
    for monster in monsters:
        if is_valid_movement(monster.x, monster.y, monster.mx * monster.speed, monster.my * monster.speed):
            monster.x += monster.mx * monster.speed
            monster.y += monster.my * monster.speed

        else:
            monster.choose_random_move()

    # Check for monster collisions with knights.
    for knight in knights:
        for monster in monsters:
            mon_tile = tile_snap(monster.x, monster.y)
            knight_tile = tile_snap(knight.x, knight.y)

            if mon_tile == knight_tile:
                knight.lose_life(1)

    # Check if all pellets are gone.
    if 1 not in current_map:
        game_paused = True

    # Check if all players have 0 hp.
    dead_knights = 0
    for knight in knights:
        if knight.hp == 0:
            dead_knights += 1
    if dead_knights == len(knights.sprites()):
        game_paused = True


def run_dungeon():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Events for when the mouse is clicked/used.
            cursor.click()

        elif event.type == pygame.KEYDOWN:
            # Gets the different movements for each knight.
            for knight in knights:
                if knight.player_id == 1:  # Player 1 gets the W, A, S, D keys.
                    if event.key == pygame.K_w:
                        knight.change_movement(0, -MOVEMENT_SPEED)
                    elif event.key == pygame.K_a:
                        knight.change_movement(-MOVEMENT_SPEED, 0)
                    elif event.key == pygame.K_s:
                        knight.change_movement(0, MOVEMENT_SPEED)
                    elif event.key == pygame.K_d:
                        knight.change_movement(MOVEMENT_SPEED, 0)

                elif knight.player_id == 2:  # Player 2 gets the arrow keys, keyboard or numpad.
                    if event.key == pygame.K_UP or event.key == pygame.K_KP8:
                        knight.change_movement(0, -MOVEMENT_SPEED)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_KP4:
                        knight.change_movement(0, MOVEMENT_SPEED)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_KP2:
                        knight.change_movement(-MOVEMENT_SPEED, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                        knight.change_movement(MOVEMENT_SPEED, 0)

                elif knight.player_id == 3:  # Player 3 gets the H, V, B, N keys.
                    if event.key == pygame.K_v:
                        knight.change_movement(-MOVEMENT_SPEED, 0)
                    elif event.key == pygame.K_b:
                        knight.change_movement(0, MOVEMENT_SPEED)
                    elif event.key == pygame.K_h:
                        knight.change_movement(0, -MOVEMENT_SPEED)
                    elif event.key == pygame.K_n:
                        knight.change_movement(MOVEMENT_SPEED, 0)

                elif knight.player_id == 4:  # Player 4 gets the =, [, ], \ keys.
                    if event.key == pygame.K_BACKSLASH:
                        knight.change_movement(MOVEMENT_SPEED, 0)
                    elif event.key == pygame.K_EQUALS:
                        knight.change_movement(0, -MOVEMENT_SPEED)
                    elif event.key == pygame.K_RIGHTBRACKET:
                        knight.change_movement(0, MOVEMENT_SPEED)
                    elif event.key == pygame.K_LEFTBRACKET:
                        knight.change_movement(-MOVEMENT_SPEED, 0)

    update_positions()
    draw_screen()


def run():
    init_dungeon([("Jerro", 'holy'), ("OWEN", "wrak")], 10, ["lich", "zomb"])

    i = 0
    while True:
        if i == 1:
            time.sleep(1)
            print(3)
            time.sleep(1)
            print(2)
            time.sleep(1)
            print(1)
            time.sleep(1)
            print("GO!")
            time.sleep(1)
        run_dungeon()
        clock.tick(fps)
        i += 1
