import sys
import time

from lib.maps import maps
from bin.utils import *
from bin.gui import *
from bin.game_objs import *


class Application:
    def __init__(self):
        # Screen measurement setup.
        self.WALL_THICKNESS = 32
        self.HALF_WALL_THICKNESS = self.WALL_THICKNESS // 2
        self.MAP_SIZE = 20
        self.MOVEMENT_SPEED = self.WALL_THICKNESS // 16

        self.POSSIBLE_CHAR_SIZES = (1, 1.5, 2, 2.5)
        self.CHAR_SIZE = 2.5
        self.HEART_SIZE = 2.5 + 0.5
        self.HEART_SPACING = 78

        self.DUNGEON_WIDTH = self.MAP_SIZE * self.WALL_THICKNESS
        self.DUNGEON_HEIGHT = self.MAP_SIZE * self.WALL_THICKNESS

        self.SIDEBAR_WIDTH = 4.5 * self.WALL_THICKNESS
        self.SIDEBAR_HEIGHT = self.DUNGEON_HEIGHT

        # Application screen setup.
        self.SCREEN_WIDTH = self.DUNGEON_WIDTH + self.SIDEBAR_WIDTH
        self.SCREEN_HEIGHT = self.SIDEBAR_HEIGHT if self.SIDEBAR_WIDTH > self.DUNGEON_HEIGHT else self.DUNGEON_HEIGHT
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Men")
        self.program_icon = pygame.image.load("lib\\sprites\\gui\\icon_5.png")
        pygame.display.set_icon(self.program_icon)

        # Clock setup (for fps).
        self.clock = pygame.time.Clock()
        self.fps = 64
        self.frame_index = 0

        # Background setup
        self.background = load_img("lib\\sprites\\environ\\floor.png")
        self.background_width = self.background.get_width()
        self.background_height = self.background.get_height()

        # Setup cursor.
        pygame.mouse.set_visible(False)
        self.cursor = Cursor(self.fps)
        self.cursor_sprites = pygame.sprite.Group()
        self.cursor_sprites.add(self.cursor)

        # Songs
        self.music_volume = 0.3
        pygame.mixer.music.load("lib\\sounds\\music\\vafen.wav")
        pygame.mixer.music.set_volume(self.music_volume)

        # Misc setup.
        self.game_state = 'start menu'
        self.run_app = True
        self.game_paused = False
        self.enter_dungeon = False

        # Misc setup.
        self.current_map = None
        self.current_walls = None
        self.wall_collision_detection = False
        self.mobile_collision_detection = True

        # Speed conversions
        self.SPEED_CONVERSIONS = {
            "snail": self.WALL_THICKNESS // 22,
            "slow": self.WALL_THICKNESS // 19,
            "medium": self.WALL_THICKNESS // 16,
            "fast": self.WALL_THICKNESS // 8,
            "flash": self.WALL_THICKNESS // 4
        }

        # Dungeon variables.
        self.HEART_SPRITES = {}
        self.KNIGHT_SKINS = {
            "1": [{}, {}],
            "1.5": [{}, {}],
            "2": [{}, {}],
            "2.5": [{}, {}],
        }
        self.item_sprites = {}
        self.monsters = []
        self.players = []
        self.used_monster_skins = []
        self.knights = pygame.sprite.Group()
        self.wall_sprite = None
        self.dungeon_theme = None
        self.SPECIAL_ITEM_NAMES = ("apple", "beetroot", "cherries", "mushroom", "pumpkin", "radish", "gem")
        self.KNIGHT_SKIN_NAMES = ("arch", "skul", "diab", "dom", "syth", "crud", "plag", "maji", "mega", "pink", "holy",
                                  "wrak", "shov", "shy", "rusty")
        self.SECRET_KNIGHT_SKIN_NAMES = ("andy", "kirb", "ngor", "spawn", "gpt")
        self.MONSTER_SKIN_NAMES = ("behold", "chopper", "demo", "ender", "gruff", "lich", "neo", "orc", "robe",
                                   "spider", "zomb")
        self.penny_sprite = scale_image(load_img(f"lib\\sprites\\items\\penny.png"))
        self.gold_sprite = scale_image(load_img(f"lib\\sprites\\items\\gold.png"))
        self.silver_sprite = scale_image(load_img(f"lib\\sprites\\items\\coin.png"))
        self.gem_sprite = scale_image(load_img(f"lib\\sprites\\items\\gem.png"))
        self.banana_sprite = scale_image(load_img(f"lib\\sprites\\items\\banana.png"), self.CHAR_SIZE)
        self.banana_time = False
        self.rabbit_of_caerbannog = False
        self.among_us = False
        self.music_is_paused = False
        self.ITEM_CODES = {
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
        for skin in (*self.KNIGHT_SKIN_NAMES, *self.SECRET_KNIGHT_SKIN_NAMES):
            for size in self.POSSIBLE_CHAR_SIZES:
                self.KNIGHT_SKINS[f"{size}"][0][skin] = scale_image(load_img(f"lib\\sprites\\helms\\{skin}_helm.png"),
                                                                    size)
                self.KNIGHT_SKINS[f"{size}"][1][skin] = change_img_hue(self.KNIGHT_SKINS[f"{size}"][0][skin])

            # Setup heart sprites.
            self.HEART_SPRITES[skin] = scale_image(load_img(f"lib\\sprites\\hearts\\{skin}_heart.png"), self.HEART_SIZE)

        for sprite in ("empty", "shield"):
            self.HEART_SPRITES[sprite] = scale_image(load_img(f"lib\\sprites\\hearts\\{sprite}_heart.png"),
                                                     self.HEART_SIZE)

        # Get among us skins loaded.
        self.among_us_skins = []
        for i in range(0, 6):
            self.among_us_skins.append(scale_image(load_img(f"lib\\sprites\\enemies\\among_{i}.png"), self.CHAR_SIZE))

            # Store buttons and other widgets
            self.enter_dungeon_button = Button(self.SCREEN_WIDTH - (194 + self.WALL_THICKNESS), self.SCREEN_HEIGHT -
                                               (32 + self.WALL_THICKNESS),
                                               multi_line_text(" Enter Dungeon ", ALKHEMIKAL_FNT,
                                                               pygame.Rect(0, 0, 194, 32), COLORS["brown"],
                                                               COLORS["tan"]))
            self.input_boxes = [
                InputBox(self.WALL_THICKNESS, self.WALL_THICKNESS * 2, 150, bg=COLORS["p_1"]),  # Player 1
                InputBox(self.WALL_THICKNESS * 2 + 160, self.WALL_THICKNESS * 2, 150, bg=COLORS["p_2"]),  # Player 2
                InputBox(self.WALL_THICKNESS * 3 + 320, self.WALL_THICKNESS * 2, 150, bg=COLORS["p_3"]),  # Player 3
                InputBox(self.WALL_THICKNESS * 4 + 480, self.WALL_THICKNESS * 2, 150, bg=COLORS["p_4"]),  # Player 4

                InputBox(self.SCREEN_WIDTH - self.WALL_THICKNESS * 11, self.SCREEN_HEIGHT - self.WALL_THICKNESS * 2, 60,
                         text='14', allowed_chars=("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"),
                         max_text_len=3)  # Num enemies
            ]
            self.option_boxes = [
                OptionBox(self.SCREEN_WIDTH - self.WALL_THICKNESS * 16.25,
                          self.SCREEN_HEIGHT - self.WALL_THICKNESS * 2.3 - 1, 130, 54,
                          ("snail", "slow", "medium", "fast", "flash"), selected=2),
                OptionBox(self.SCREEN_WIDTH - self.WALL_THICKNESS * 23,
                          self.SCREEN_HEIGHT - self.WALL_THICKNESS * 2.3 - 1, 190, 54,
                          ("all precise", "precise mobs", "precise walls", "none precise"), selected=1),
            ]

            self.skin_selector = SkinSelector(self.SCREEN, remove_key_value_pairs(self.KNIGHT_SKINS["1"],
                                                                                  self.SECRET_KNIGHT_SKIN_NAMES),
                                              self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

            self.run()

    def run(self):
        pygame.mixer.music.play(-1)

        while self.run_app:
            self.draw_screen()
            if self.game_state == 'game':
                self.run_dungeon_frame()
            elif self.game_state == 'start menu':
                self.run_start_menu_frame()

            self.clock.tick(self.fps)
            self.frame_index += 1

    def reset_dungeon(self):
        self.game_paused = False
        self.monsters = []
        self.players = []
        self.used_monster_skins = []
        self.dungeon_theme = random.choice(('light', 'dark'))
        self.current_map = random.choice(maps).copy()
        self.current_walls = create_walls(self.current_map, self.WALL_THICKNESS)
        self.wall_sprite = load_img(f"lib\\sprites\\environ\\{self.dungeon_theme}\\wall_{random.randint(0, 14)}.png")
        self.wall_sprite = scale_image(self.wall_sprite)
        self.knights = pygame.sprite.Group()

    def init_dungeon(self, player_ids, num_monsters, override_monster_skins=None, among_us=False,
                     rabbit_of_caerbannog=False):
        """
        Parameters
        ----------
        player_ids: A list of player name, skin tuples, up to for, one for each player.
        num_monsters: The number of monsters to be in the dungeon.
        override_monster_skins: The skins that will be used for the monsters, if None, all will be used.
        among_us: Whether or not to do among us skins for enemies
        rabbit_of_caerbannog: Whether or not to have the Rabbit of Caerbannog attack.
        """
        # Reset vars
        self.reset_dungeon()

        # Get the fruit sprites loaded.
        for fruit in self.SPECIAL_ITEM_NAMES:
            self.item_sprites[fruit] = scale_image(load_img(f"lib\\sprites\\items\\{fruit}.png"), self.CHAR_SIZE)

        # Create knights for all of the players.
        for i in range(len(player_ids)):
            if i + 1 == 1:
                self.knights.add(Knight(self.SCREEN, 1, 1, player_ids[i][0], 1, player_ids[i][1], self.WALL_THICKNESS,
                                        self.fps, self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][0][player_ids[i][1]],
                                        self.DUNGEON_WIDTH, self.HEART_SPACING,
                                        self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][1][player_ids[i][1]],
                                        self.HEART_SPRITES["shield"], self.HEART_SPRITES[player_ids[i][1]],
                                        self.HEART_SPRITES["empty"]))
            elif i + 1 == 2:
                self.knights.add(Knight(self.SCREEN, 18, 18, player_ids[i][0], 2, player_ids[i][1], self.WALL_THICKNESS,
                                        self.fps, self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][0][player_ids[i][1]],
                                        self.DUNGEON_WIDTH, self.HEART_SPACING,
                                        self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][1][player_ids[i][1]],
                                        self.HEART_SPRITES["shield"], self.HEART_SPRITES[player_ids[i][1]],
                                        self.HEART_SPRITES["empty"]))
            elif i + 1 == 3:
                self.knights.add(Knight(self.SCREEN, 1, 18, player_ids[i][0], 3, player_ids[i][1], self.WALL_THICKNESS,
                                        self.fps, self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][0][player_ids[i][1]],
                                        self.DUNGEON_WIDTH, self.HEART_SPACING,
                                        self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][1][player_ids[i][1]],
                                        self.HEART_SPRITES["shield"], self.HEART_SPRITES[player_ids[i][1]],
                                        self.HEART_SPRITES["empty"]))
            else:
                self.knights.add(Knight(self.SCREEN, 18, 1, player_ids[i][0], 4, player_ids[i][1], self.WALL_THICKNESS,
                                        self.fps, self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][0][player_ids[i][1]],
                                        self.DUNGEON_WIDTH, self.HEART_SPACING,
                                        self.KNIGHT_SKINS[f"{self.CHAR_SIZE}"][1][player_ids[i][1]],
                                        self.HEART_SPRITES["shield"], self.HEART_SPRITES[player_ids[i][1]],
                                        self.HEART_SPRITES["empty"]))

        # Monster setup and creation.
        if override_monster_skins is None:
            used_monster_skins = self.MONSTER_SKIN_NAMES

        elif rabbit_of_caerbannog:
            used_monster_skins = ["rabbit_of_caerbannog"]
        else:
            used_monster_skins = override_monster_skins

        self.monsters = pygame.sprite.Group()

        # Create randomized monsters.
        for i in range(num_monsters):
            self.monsters.add(Monster(self.SCREEN, random.randint(9, 10), 9, random.choice(used_monster_skins),
                                      self.MOVEMENT_SPEED, self.WALL_THICKNESS, self.CHAR_SIZE, among_us,
                                      self.among_us_skins))

        for monster in self.monsters:
            monster.choose_random_move()

        # Randomize the items.
        for i, v in enumerate(self.current_map):
            if v == 3:
                self.current_map[i] = self.ITEM_CODES[random.choice(self.SPECIAL_ITEM_NAMES)]
            elif v == 2:
                item_choice = random.randint(1, 30)
                if item_choice == 30:
                    self.current_map[i] = self.ITEM_CODES["gold"]
                elif item_choice > 25:
                    self.current_map[i] = self.ITEM_CODES["silver"]

    def draw_screen(self):
        self.SCREEN.blit(self.background, (0, 0))

        # Calculate the number of tiles needed in both x and y directions.
        tiles_x = self.SCREEN.get_width() // self.background_width + 1
        tiles_y = self.SCREEN.get_height() // self.background_height + 1

        # Loop to tile the background image.
        for y in range(tiles_y):
            for x in range(tiles_x):
                self.SCREEN.blit(self.background, (x * self.background_width, y * self.background_height))

        if self.game_state == "game":
            # Draw knights.
            for knight in self.knights:
                knight.draw()

            # Draw the monsters.
            for monster in self.monsters:
                monster.draw()

            # Draw walls.
            for index in range(len(self.current_map)):
                tile = self.current_map[index]

                x = (index % self.MAP_SIZE) * self.WALL_THICKNESS
                y = (index // self.MAP_SIZE) * self.WALL_THICKNESS

                if tile == 0:
                    self.SCREEN.blit(self.wall_sprite, (x, y))

                elif tile == 2:
                    self.SCREEN.blit(self.penny_sprite, (x, y))

                elif self.banana_time and tile != 1:
                    self.SCREEN.blit(self.banana_sprite, (x + 3, y + 3))

                elif tile == 11:
                    self.SCREEN.blit(self.gem_sprite, (x, y))

                elif tile == 12:
                    self.SCREEN.blit(self.gold_sprite, (x, y))

                elif tile == 13:
                    self.SCREEN.blit(self.silver_sprite, (x, y))

                elif tile not in (1, 3, 4, 11, 12, 13):
                    self.SCREEN.blit(self.item_sprites[key_from_value(self.ITEM_CODES, tile)], (x + 3, y + 3))

            # Draw the scores and player names.
            text = ""
            for knight in self.knights:
                text += f"\n{knight.name}\n\n{' ' * max(8 - len(str(knight.score)), 0)}{knight.score}\n\n"

            text_surface = multi_line_text(text, ALKHEMIKAL_FNT,
                                           pygame.Rect(0, 0, self.SIDEBAR_WIDTH, self.SIDEBAR_HEIGHT), COLORS['white'])

            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.DUNGEON_WIDTH + self.WALL_THICKNESS // 2, self.HALF_WALL_THICKNESS)

            self.SCREEN.blit(text_surface, text_rect)

        elif self.game_state == "start menu":
            for box in self.input_boxes:
                box.draw(self.SCREEN)
            self.enter_dungeon_button.draw(self.SCREEN)
            self.skin_selector.draw()
            for box in self.option_boxes:
                box.draw(self.SCREEN)

        # Draw cursor.
        self.cursor_sprites.update()
        self.cursor_sprites.draw(self.SCREEN)

        # Finish drawing.
        pygame.display.flip()

    def update_positions(self, do_mobile_collision_detection=True, do_wall_collision_detection=False):
        # Update the positions of all mobiles.
        if self.game_paused:
            return

        # Update the knights.
        for knight in self.knights:
            if self.wall_collision_detection:
                movement_validity = is_valid_movement(knight.x, knight.y, knight.mx * knight.speed,
                                                      knight.my * knight.speed, self.MOVEMENT_SPEED, self.CHAR_SIZE,
                                                      self.MAP_SIZE, self.WALL_THICKNESS, walls=self.current_walls)
            else:
                movement_validity = is_valid_movement(knight.x, knight.y, knight.mx * knight.speed, knight.my *
                                                      knight.speed, self.MOVEMENT_SPEED, self.CHAR_SIZE, self.MAP_SIZE,
                                                      self.WALL_THICKNESS, self.current_map)
            if movement_validity:
                knight.x += knight.mx * knight.speed
                knight.y += knight.my * knight.speed

            knight_pos_index = tile_snap(knight.x, knight.y, self.MAP_SIZE, self.WALL_THICKNESS)

            # Check for knight item/coin collisions.
            if knight.retreat_countdown == 0:
                if self.current_map[knight_pos_index] == 2:
                    self.current_map[knight_pos_index] = 1
                    knight.score += 1 * knight.luck

                elif self.current_map[knight_pos_index] == 5:
                    self.current_map[knight_pos_index] = 1
                    if random.randint(0, 1):
                        knight.score += random.choice(
                            [1, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 30, 30,
                             30, 40, 50])
                    else:
                        knight.luck_effects.append([self.fps * 5, "* 2"])

                elif self.current_map[knight_pos_index] == 6:
                    self.current_map[knight_pos_index] = 1
                    knight.score += random.randint(5, 20)
                    knight.speed_effects.append([self.fps * 20, "/ 2"])

                elif self.current_map[knight_pos_index] == 7:
                    self.current_map[knight_pos_index] = 1

                    for k in self.knights:
                        k.speed_effects.append([self.fps * 40, "/ 2"])

                    for monster in self.monsters:
                        monster.speed_effects.append([self.fps * 40, "/ 2"])

                elif self.current_map[knight_pos_index] == 8:
                    self.current_map[knight_pos_index] = 1
                    knight.shield_countdown = self.fps * 7
                    knight.has_shield = True
                    knight.update_hearts()

                elif self.current_map[knight_pos_index] == 9:
                    self.current_map[knight_pos_index] = 1
                    knight.speed_effects.append([self.fps * 20, "* 2"])

                elif self.current_map[knight_pos_index] == 10:
                    self.current_map[knight_pos_index] = 1
                    knight.score += random.randint(-10, 20)

                elif self.current_map[knight_pos_index] == 11:
                    self.current_map[knight_pos_index] = 1
                    knight.luck_effects.append([self.fps * 5, "* 2"])

                elif self.current_map[knight_pos_index] == 12:
                    self.current_map[knight_pos_index] = 1
                    knight.score += 3 * knight.luck

                elif self.current_map[knight_pos_index] == 13:
                    self.current_map[knight_pos_index] = 1
                    knight.score += 2 * knight.luck

        # Update the monsters.
        for monster in self.monsters:
            if do_wall_collision_detection:
                movement_validity = is_valid_movement(monster.x, monster.y, monster.mx * monster.speed,
                                                      monster.my * monster.speed, self.MOVEMENT_SPEED, self.CHAR_SIZE,
                                                      self.MAP_SIZE, self.WALL_THICKNESS, walls=self.current_walls)
            else:
                movement_validity = is_valid_movement(monster.x, monster.y, monster.mx * monster.speed, monster.my *
                                                      monster.speed, self.MOVEMENT_SPEED, self.CHAR_SIZE, self.MAP_SIZE,
                                                      self.WALL_THICKNESS, self.current_map)
            if movement_validity:
                monster.x += monster.mx * monster.speed
                monster.y += monster.my * monster.speed

            else:
                monster.choose_random_move()

        # Check for monster collisions with knights.
        if do_mobile_collision_detection:
            for knight in self.knights:
                for monster in self.monsters:
                    # Update the rect attributes of the sprites
                    knight.rect.center = (knight.x, knight.y)
                    monster.rect.center = (monster.x, monster.y)

                    if pygame.sprite.collide_mask(knight, monster):
                        knight.lose_life(1)

        else:
            for knight in self.knights:
                for monster in self.monsters:
                    mon_tile = tile_snap(monster.x, monster.y, self.MAP_SIZE, self.WALL_THICKNESS)
                    knight_tile = tile_snap(knight.x, knight.y, self.MAP_SIZE, self.WALL_THICKNESS)

                    if mon_tile == knight_tile:
                        knight.lose_life(1)

        # Check if all pellets are gone.
        if self.ITEM_CODES["coin"] not in self.current_map:
            self.game_paused = True

        # Check if all players have 0 hp.
        dead_knights = 0
        for knight in self.knights:
            if knight.hp == 0:
                dead_knights += 1
        if dead_knights == len(self.knights.sprites()):
            self.game_paused = True

    def run_dungeon_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Events for when the mouse is clicked/used.
                self.cursor.click()

            elif event.type == pygame.KEYDOWN:
                # Check to restart the game
                if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN) and self.game_paused:
                    self.game_state = 'start menu'

                # Pause and play music
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                    if self.music_is_paused:
                        pygame.mixer.music.play()
                        self.music_is_paused = False
                    else:
                        self.music_is_paused = True
                        pygame.mixer.music.pause()

                # Gets the different movements for each knight.
                for knight in self.knights:
                    if knight.player_id == 1:  # Player 1 gets the W, A, S, D keys.
                        if event.key == pygame.K_w:
                            knight.change_movement(0, -self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_a:
                            knight.change_movement(-self.MOVEMENT_SPEED, 0)
                        elif event.key == pygame.K_s:
                            knight.change_movement(0, self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_d:
                            knight.change_movement(self.MOVEMENT_SPEED, 0)

                    elif knight.player_id == 2:  # Player 2 gets the arrow keys, keyboard or numpad.
                        if event.key == pygame.K_UP or event.key == pygame.K_KP8:
                            knight.change_movement(0, -self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                            knight.change_movement(0, self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                            knight.change_movement(-self.MOVEMENT_SPEED, 0)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                            knight.change_movement(self.MOVEMENT_SPEED, 0)

                    elif knight.player_id == 3:  # Player 3 gets the H, V, B, N keys.
                        if event.key == pygame.K_v:
                            knight.change_movement(-self.MOVEMENT_SPEED, 0)
                        elif event.key == pygame.K_b:
                            knight.change_movement(0, self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_h:
                            knight.change_movement(0, -self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_n:
                            knight.change_movement(self.MOVEMENT_SPEED, 0)

                    elif knight.player_id == 4:  # Player 4 gets the =, [, ], \ keys.
                        if event.key == pygame.K_BACKSLASH:
                            knight.change_movement(self.MOVEMENT_SPEED, 0)
                        elif event.key == pygame.K_EQUALS:
                            knight.change_movement(0, -self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_RIGHTBRACKET:
                            knight.change_movement(0, self.MOVEMENT_SPEED)
                        elif event.key == pygame.K_LEFTBRACKET:
                            knight.change_movement(-self.MOVEMENT_SPEED, 0)

        self.update_positions(self.mobile_collision_detection, self.wall_collision_detection)

    def start_menu_to_dungeon(self):
        # Starts the dungeon/game
        try:
            num_monsters = int(self.input_boxes[-1].text)
        except ValueError:
            num_monsters = 0

        precision = self.option_boxes[1].option_list[self.option_boxes[1].selected]
        if precision == "all precise":
            self.wall_collision_detection = True
            self.mobile_collision_detection = True
        elif precision == "precise walls":
            self.wall_collision_detection = True
            self.mobile_collision_detection = False
        elif precision == "precise mobs":
            self.wall_collision_detection = False
            self.mobile_collision_detection = True
        elif precision == "none precise":
            self.wall_collision_detection = False
            self.mobile_collision_detection = False

        self.MOVEMENT_SPEED = self.SPEED_CONVERSIONS[self.option_boxes[0].option_list[self.option_boxes[0].selected]]
        player_attribs_raw = [[box.text, *[self.KNIGHT_SKIN_NAMES
                              [self.skin_selector.selected_skins[i]]]] for i, box in enumerate(self.input_boxes[:-1])]
        player_attribs = [attrib for attrib in player_attribs_raw if attrib[0] != ""]

        # Among us music and easter eggs
        self.banana_time = False
        self.among_us = False
        self.rabbit_of_caerbannog = False
        for i in range(len(player_attribs)):
            if player_attribs[i][0].lower().strip() in ("sus", "sussy", "among", "bussy", "crew"):
                self.among_us = True

            elif player_attribs[i][0].lower().strip() in ("james", "bnn", "tran"):
                self.banana_time = True

            elif player_attribs[i][0].lower().strip().replace("4", "a") in ("andy", "kirra", "mgirl", "ander"):
                player_attribs[i][1] = "andy"

            elif player_attribs[i][0].lower().strip() in ("kirb", "kirby", "kobe"):
                player_attribs[i][1] = "kirb"

            elif player_attribs[i][0].lower().strip() in ("ngor", "niga", "nigga", "niger"):
                player_attribs[i][1] = "ngor"

            elif player_attribs[i][0].lower().strip().replace("-", "") in ("gpt", "gpt3", "chat3", "ai"):
                player_attribs[i][1] = "gpt"

            elif player_attribs[i][0].lower().strip().replace("4", "a") == "spawn":
                player_attribs[i][1] = "spawn"

        if random.randint(0, 50) == 42:
            self.rabbit_of_caerbannog = True
            if self.music_is_paused:
                play_video("lib\\videos\\Monty Python The Holy Grail - The killer bunny.mp4")

        if self.among_us:
            pygame.mixer.music.load("lib\\sounds\\music\\Hide n Seek Impostor.wav")
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)

        self.init_dungeon(player_attribs, num_monsters,
                          [random.choice(self.MONSTER_SKIN_NAMES), random.choice(self.MONSTER_SKIN_NAMES)],
                          self.among_us, self.rabbit_of_caerbannog)

        self.enter_dungeon_button.clicked = False
        self.game_state = 'game'

    def run_start_menu_frame(self):
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Events for when the mouse is clicked/used.
                self.cursor.click()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_menu_to_dungeon()

                # Pause and play music
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                    if self.music_is_paused:
                        pygame.mixer.music.play()
                        self.music_is_paused = False
                    else:
                        self.music_is_paused = True
                        pygame.mixer.music.pause()

                elif pygame.K_1 <= event.key <= pygame.K_8:
                    number = event.key - pygame.K_1
                    program_icon = pygame.image.load(f"lib\\sprites\\gui\\icon_{number}.png")
                    pygame.display.set_icon(program_icon)

            self.skin_selector.handle_event(event)
            for box in self.input_boxes:
                box.handle_event(event)

        for i in range(len(self.option_boxes)):
            self.option_boxes[i].update(event_list)

        if self.enter_dungeon_button.clicked:
            self.start_menu_to_dungeon()
