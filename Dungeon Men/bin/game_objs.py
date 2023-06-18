from bin.utils import *


class Heart(pygame.sprite.Sprite):
    def __init__(self, pos, skin):
        super().__init__()
        self.image = full_hearts[skin]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class Knight(pygame.sprite.Sprite):
    def __init__(self, x, y, name, player_id, skin):
        super().__init__()

        self.name = name
        self.skin = skin
        self.player_id = player_id
        self.hp = 3
        self.retreat_countdown = 0
        self.shield_countdown = 0
        self.has_shield = False
        self.has_retreat_shield = False
        self.speed_effects = []  # full of: (countdown, effect)
        self.speed = 1
        self.luck_effects = []  # full of: (countdown, effect)
        self.luck = 1
        self.score = 0
        self.x = WALL_THICKNESS * x + HALF_WALL_THICKNESS
        self.y = WALL_THICKNESS * y + HALF_WALL_THICKNESS
        self.mx = 0
        self.my = 0

        self.sprite = knight_skins[self.skin]
        self.rect = self.sprite.get_rect()

        self.hearts = pygame.sprite.Group()
        heart_positions = [(DUNGEON_WIDTH + WALL_THICKNESS + i * 30,
                            HEART_SPACING * (1 + 2 * (self.player_id - 1))) for i in range(self.hp)]
        for position in heart_positions:
            self.hearts.add(Heart(position, self.skin))

    def change_movement(self, x, y):
        # Change knight movement direction.
        self.mx = x
        self.my = y

    def draw(self):
        # Draws itself on the screen.
        half_rect_width = self.rect.width // 2
        half_rect_height = self.rect.height // 2

        # Check if the retreat countdown is not zero
        if self.retreat_countdown != 0 or self.shield_countdown != 0:
            # Calculate the circle's position and size relative to the character sprite
            circle_radius = max(half_rect_width, half_rect_height) + 5
            circle_center = (self.x, self.y)
            circle_pos = (self.x - circle_radius - 2, self.y - circle_radius - 2)

            # Create a surface for the circle
            circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, SHIELD_BLUE, (circle_radius, circle_radius), circle_radius)
            screen.blit(circle_surface, circle_pos)

        if self.has_retreat_shield and self.retreat_countdown == 0:
            self.has_retreat_shield = False
            self.update_hearts()

        if self.has_shield and self.shield_countdown == 0:
            self.has_shield = False
            self.update_hearts()

        if len(self.luck_effects) != 0:
            screen.blit(alt_knight_skins[self.skin], (self.x - half_rect_width - 2, self.y - half_rect_height - 2))
        else:
            screen.blit(self.sprite, (self.x - half_rect_width - 2, self.y - half_rect_height - 2))

        # Draw hearts
        self.hearts.draw(screen)

        # Updates retreat countdown and other countdowns
        self.shield_countdown = max(self.shield_countdown - 1, 0)
        if self.hp > 0:
            self.retreat_countdown = max(self.retreat_countdown - 1, 0)
        self.update_speed_effects()
        self.update_luck_effects()

    def update_speed_effects(self):
        self.speed = 1
        indices_to_remove = []
        for i in range(len(self.speed_effects)):
            effect_duration, effect_expression = self.speed_effects[i]
            if effect_duration <= 0:
                indices_to_remove.append(i)
            else:
                self.speed = eval("self.speed" + effect_expression)
                self.speed_effects[i][0] -= 1
        for i in reversed(indices_to_remove):
            del self.speed_effects[i]

    def update_luck_effects(self):
        self.luck = 1
        indices_to_remove = []
        for i in range(len(self.luck_effects)):
            effect_duration, effect_expression = self.luck_effects[i]
            if effect_duration <= 0:
                indices_to_remove.append(i)
            else:
                self.luck = eval("self.luck" + effect_expression)
                self.luck_effects[i][0] -= 1
        for i in reversed(indices_to_remove):
            del self.luck_effects[i]

    def lose_life(self, num):
        if self.retreat_countdown == 0 and self.shield_countdown == 0:
            self.hp = min(max(self.hp - num, 0), 3)
            self.retreat_countdown = fps * 3
            self.has_retreat_shield = True
        self.update_hearts()

    def update_hearts(self):
        # Update hearts
        for heart in self.hearts:
            heart.image = empty_heart

        if self.hp >= 1:
            if self.shield_countdown != 0:
                self.hearts.sprites()[0].image = shield_heart
            else:
                self.hearts.sprites()[0].image = full_hearts[self.skin]
            if self.has_retreat_shield:
                self.hearts.sprites()[1].image = shield_heart
        if self.hp >= 2:
            if self.shield_countdown != 0:
                self.hearts.sprites()[1].image = shield_heart
            else:
                self.hearts.sprites()[1].image = full_hearts[self.skin]
            if self.has_retreat_shield:
                self.hearts.sprites()[2].image = shield_heart
        if self.hp == 3:
            if self.shield_countdown != 0:
                self.hearts.sprites()[2].image = shield_heart
            else:
                self.hearts.sprites()[2].image = full_hearts[self.skin]


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, skin, movement_speed):
        super().__init__()

        self.movement_speed = movement_speed
        self.skin = skin
        self.x = WALL_THICKNESS * x + HALF_WALL_THICKNESS
        self.y = WALL_THICKNESS * y + HALF_WALL_THICKNESS
        self.mx = 0
        self.my = 0
        self.speed = 1
        self.speed_effects = []  # full of: (countdown, effect)

        self.sprite = scale_image(load_img(f"lib\\sprites\\enemies\\{self.skin}.png"), CHAR_SIZE)
        self.rect = self.sprite.get_rect()

    def change_movement(self, x, y):
        # Change knight movement direction.
        self.mx = x
        self.my = y

    def choose_random_move(self):
        next_movement = random.choice(movement_options(self.movement_speed))
        self.change_movement(*next_movement)

    def update_speed_effects(self):
        self.speed = 1
        indices_to_remove = []
        for i in range(len(self.speed_effects)):
            effect_duration, effect_expression = self.speed_effects[i]
            if effect_duration <= 0:
                indices_to_remove.append(i)
            else:
                self.speed = eval("self.speed" + effect_expression)
                self.speed_effects[i][0] -= 1
        for i in reversed(indices_to_remove):
            del self.speed_effects[i]

    def draw(self):
        # Draws itself on the screen.
        half_rect_width = self.rect.width // 2
        half_rect_height = self.rect.height // 2
        screen.blit(self.sprite, (self.x - half_rect_width - 2, self.y - half_rect_height - 2))

        # Update effects
        self.update_speed_effects()
