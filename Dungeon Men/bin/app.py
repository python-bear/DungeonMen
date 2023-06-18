import random
import sys
import time

from lib.maps import maps
from bin.utils import *
from bin.gui import *
from bin.game_objs import *

# Screen setup.
pygame.display.set_caption("Dungeon Men")

background = load_img("lib\\sprites\\environ\\floor.png")
background_width = background.get_width()
background_height = background.get_height()

# Clock setup (for fps).
clock = pygame.time.Clock()

# Misc setup.
run_app = True
game_paused = False
game_state = 'start menu'
frame_index = 0
enter_dungeon = False

# Store buttons and other widgets
enter_dungeon_button = Button(SCREEN_WIDTH - (194 + WALL_THICKNESS), SCREEN_HEIGHT - (32 + WALL_THICKNESS),
                              multi_line_text(" Enter Dungeon ", alkhemikal_font, pygame.Rect(0, 0, 194, 32), BROWN,
                                              TAN))
input_boxes = [
    InputBox(WALL_THICKNESS, WALL_THICKNESS * 2, 150, bg=P_1_COL),  # Player 1
    InputBox(WALL_THICKNESS * 2 + 160, WALL_THICKNESS * 2, 150, bg=P_2_COL),  # Player 2
    InputBox(WALL_THICKNESS * 3 + 320, WALL_THICKNESS * 2, 150, bg=P_3_COL),  # Player 3
    InputBox(WALL_THICKNESS * 4 + 480, WALL_THICKNESS * 2, 150, bg=P_4_COL),  # Player 4

    InputBox(SCREEN_WIDTH - WALL_THICKNESS * 11, SCREEN_HEIGHT - WALL_THICKNESS * 2, 60, text='14', max_text_len=3,
             allowed_chars=("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"))  # Num enemies
]
option_boxes = [
    OptionBox(SCREEN_WIDTH - WALL_THICKNESS * 16.25, SCREEN_HEIGHT - WALL_THICKNESS * 2.3 - 1, 130, 54,
              ("snail", "slow", "medium", "fast", "flash"), selected=2),
    OptionBox(SCREEN_WIDTH - WALL_THICKNESS * 23, SCREEN_HEIGHT - WALL_THICKNESS * 2.3 - 1, 190, 54,
              ("all precise", "precise mobs", "precise walls", "none precise"), selected=1),
]
skin_selector = SkinSelector(screen)

# Setup cursor.
pygame.mouse.set_visible(False)
cursor = Cursor(100, 100)

cursor_sprites = pygame.sprite.Group()
cursor_sprites.add(cursor)


def reset_dungeon():
    global knights, monsters, wall_sprite, penny_sprite, dungeon_theme, players, full_hearts, used_monster_skins, \
        game_paused, current_map, current_walls

    game_paused = False
    monsters = players = used_monster_skins = []
    dungeon_theme = random.choice(('light', 'dark'))
    current_map = random.choice(maps).copy()
    current_walls = create_walls(current_map)
    wall_sprite = load_img(f"lib\\sprites\\environ\\{dungeon_theme}\\wall_{random.randint(0, 14)}.png")
    wall_sprite = scale_image(wall_sprite)
    knights = pygame.sprite.Group()


def init_dungeon(player_ids, num_monsters, override_monster_skins=None):
    """
    Parameters
    ----------
    player_ids: A list of player name, skin tuples, up to for, one for each player.
    num_monsters: The number of monsters to be in the dungeon.
    override_monster_skins: The skins that will be used for the monsters, if None, all will be used.
    """
    global knights, monsters, wall_sprite, penny_sprite, dungeon_theme, players, full_hearts, used_monster_skins, \
        game_paused, current_map

    # Reset vars
    reset_dungeon()

    # Get the fruit sprites loaded.
    for fruit in fruit_names:
        item_sprites[fruit] = scale_image(load_img(f"lib\\sprites\\items\\{fruit}.png"), CHAR_SIZE)

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
        monsters.add(Monster(random.randint(9, 10), 9, random.choice(used_monster_skins), MOVEMENT_SPEED))

    for monster in monsters:
        monster.choose_random_move()

    # Randomize the items.
    for i, v in enumerate(current_map):
        if v == 3:
            current_map[i] = item_codes[random.choice(fruit_names)]


def draw_screen():
    global current_map

    screen.blit(background, (0, 0))

    # Calculate the number of tiles needed in both x and y directions.
    tiles_x = screen.get_width() // background_width + 1
    tiles_y = screen.get_height() // background_height + 1

    # Loop to tile the background image.
    for y in range(tiles_y):
        for x in range(tiles_x):
            screen.blit(background, (x * background_width, y * background_height))

    if game_state == "game":
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
                screen.blit(wall_sprite, (x, y))

            elif tile == 2:
                screen.blit(penny_sprite, (x, y))

            elif tile == 11:
                screen.blit(gem_sprite, (x, y))

            elif tile == 12:
                screen.blit(gold_sprite, (x, y))

            elif tile == 13:
                screen.blit(silver_sprite, (x, y))

            elif tile not in (1, 3, 4, 11, 12, 13):
                screen.blit(item_sprites[key_from_value(item_codes, tile)], (x + 3, y + 3))

        # Draw the scores and player names.
        text = ""
        for knight in knights:
            text += f"\n{knight.name}\n\n{' ' * max(8 - len(str(knight.score)), 0)}{knight.score}\n\n"

        text_surface = multi_line_text(text, alkhemikal_font, pygame.Rect(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT), WHITE)

        text_rect = text_surface.get_rect()
        text_rect.topleft = (DUNGEON_WIDTH + WALL_THICKNESS // 2, HALF_WALL_THICKNESS)

        screen.blit(text_surface, text_rect)

    elif game_state == "start menu":
        for box in input_boxes:
            box.draw(screen)
        enter_dungeon_button.draw(screen)
        skin_selector.draw()
        for box in option_boxes:
            box.draw(screen)

    # Draw cursor.
    cursor_sprites.update()
    cursor_sprites.draw(screen)

    # Finish drawing.
    pygame.display.flip()


def update_positions(do_mobile_collision_detection=True, do_wall_collision_detection=False):
    global current_map, current_walls, game_paused, MOVEMENT_SPEED, monster_movement_options

    # Update the positions of all mobiles.
    if game_paused:
        return

    # Update the knights.
    for knight in knights:
        if wall_collision_detection:
            movement_validity = is_valid_movement(knight.x, knight.y, knight.mx * knight.speed,
                                                  knight.my * knight.speed, MOVEMENT_SPEED, walls=current_walls)
        else:
            movement_validity = is_valid_movement(knight.x, knight.y, knight.mx * knight.speed, knight.my * 
                                                  knight.speed, MOVEMENT_SPEED, current_map)
        if movement_validity:
            knight.x += knight.mx * knight.speed
            knight.y += knight.my * knight.speed

        knight_pos_index = tile_snap(knight.x, knight.y)

        # Check for knight item/coin collisions.
        if knight.retreat_countdown == 0:
            if current_map[knight_pos_index] == 2:
                current_map[knight_pos_index] = 1
                knight.score += 1 * knight.luck

            elif current_map[knight_pos_index] == 5:
                current_map[knight_pos_index] = 1
                if random.randint(0, 1):
                    knight.score += random_number_faded()
                else:
                    knight.luck_effects.append([fps * 5, "* 2"])

            elif current_map[knight_pos_index] == 6:
                current_map[knight_pos_index] = 1
                knight.score += random.randint(5, 20)
                knight.speed_effects.append([fps * 20, "/ 2"])

            elif current_map[knight_pos_index] == 7:
                current_map[knight_pos_index] = 1

                for k in knights:
                    k.speed_effects.append([fps * 40, "/ 2"])

                for monster in monsters:
                    monster.speed_effects.append([fps * 40, "/ 2"])

            elif current_map[knight_pos_index] == 8:
                current_map[knight_pos_index] = 1
                knight.shield_countdown = fps * 7
                knight.has_shield = True
                knight.update_hearts()

            elif current_map[knight_pos_index] == 9:
                current_map[knight_pos_index] = 1
                knight.speed_effects.append([fps * 20, "* 2"])

            elif current_map[knight_pos_index] == 10:
                current_map[knight_pos_index] = 1
                knight.score += random.randint(-10, 20)

            elif current_map[knight_pos_index] == 11:
                current_map[knight_pos_index] = 1
                knight.luck_effects.append([fps * 5, "* 2"])

    # Update the monsters.
    for monster in monsters:
        if do_wall_collision_detection:
            movement_validity = is_valid_movement(monster.x, monster.y, monster.mx * monster.speed,
                                                  monster.my * monster.speed, MOVEMENT_SPEED, walls=current_walls)
        else:
            movement_validity = is_valid_movement(monster.x, monster.y, monster.mx * monster.speed, monster.my * 
                                                  monster.speed, MOVEMENT_SPEED, current_map)
        if movement_validity:
            monster.x += monster.mx * monster.speed
            monster.y += monster.my * monster.speed

        else:
            monster.choose_random_move()

    # Check for monster collisions with knights.
    if do_mobile_collision_detection:
        for knight in knights:
            for monster in monsters:
                # Update the rect attributes of the sprites
                knight.rect.center = (knight.x, knight.y)
                monster.rect.center = (monster.x, monster.y)

                if pygame.sprite.collide_rect(knight, monster):
                    knight.lose_life(1)

    else:
        for knight in knights:
            for monster in monsters:
                mon_tile = tile_snap(monster.x, monster.y)
                knight_tile = tile_snap(knight.x, knight.y)

                if mon_tile == knight_tile:
                    knight.lose_life(1)

    # Check if all pellets are gone.
    if item_codes["coin"] not in current_map:
        game_paused = True

    # Check if all players have 0 hp.
    dead_knights = 0
    for knight in knights:
        if knight.hp == 0:
            dead_knights += 1
    if dead_knights == len(knights.sprites()):
        game_paused = True


def run_dungeon_frame():
    global game_state, mobile_collision_detection, wall_collision_detection

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Events for when the mouse is clicked/used.
            cursor.click()

        elif event.type == pygame.KEYDOWN:
            # Check to restart the game
            if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN) and game_paused:
                game_state = 'start menu'

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
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                        knight.change_movement(0, MOVEMENT_SPEED)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
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

    update_positions(mobile_collision_detection, wall_collision_detection)


def start_menu_to_dungeon():
    global game_state, enter_dungeon_button, screen, program_icon, MOVEMENT_SPEED, speed_conversions, \
        wall_collision_detection, mobile_collision_detection

    # Starts the dungeon/game
    try:
        num_monsters = int(input_boxes[-1].text)
    except ValueError:
        num_monsters = 0

    precision = option_boxes[1].option_list[option_boxes[1].selected]
    if precision == "all precise":
        wall_collision_detection = True
        mobile_collision_detection = True
    elif precision == "precise walls":
        wall_collision_detection = True
        mobile_collision_detection = False
    elif precision == "precise mobs":
        wall_collision_detection = False
        mobile_collision_detection = True
    elif precision == "none precise":
        wall_collision_detection = False
        mobile_collision_detection = False

    MOVEMENT_SPEED = speed_conversions[option_boxes[0].option_list[option_boxes[0].selected]]

    player_attribs_raw = [[box.text, skin_selector.skins[skin_selector.selected_skins[i]]] for i, box in
                          enumerate(input_boxes[:-1])]
    player_attribs = [attrib for attrib in player_attribs_raw if attrib[0] != ""]

    enter_dungeon_button.clicked = False
    init_dungeon(player_attribs, num_monsters,
                 [random.choice(monster_skin_names), random.choice(monster_skin_names)])

    game_state = 'game'


def run_start_menu_frame():
    global game_state, enter_dungeon_button, screen, program_icon, MOVEMENT_SPEED

    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Events for when the mouse is clicked/used.
            cursor.click()
            skin_selector.handle_mouse_click(pygame.mouse.get_pos())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                start_menu_to_dungeon()

            if pygame.K_1 <= event.key <= pygame.K_8:
                number = event.key - pygame.K_1
                program_icon = pygame.image.load(f"lib\\sprites\\gui\\icon_{number}.png")
                pygame.display.set_icon(program_icon)

        for box in input_boxes:
            box.handle_event(event)

    for i in range(len(option_boxes)):
        option_boxes[i].update(event_list)

    if enter_dungeon_button.clicked:
        start_menu_to_dungeon()


def run_main_menu_frame():
    pass


def run():
    global frame_index, game_state

    # pygame.mixer.music.set_volume(0.3)
    # pygame.mixer.music.play(-1)

    while run_app:
        draw_screen()
        if game_state == 'game':
            run_dungeon_frame()
        elif game_state == 'main menu':
            run_main_menu_frame()
        elif game_state == 'start menu':
            run_start_menu_frame()

        clock.tick(fps)
        frame_index += 1
