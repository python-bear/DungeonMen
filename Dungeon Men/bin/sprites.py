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
        self.speed = 1
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
            circle_pos = (self.x - circle_radius, self.y - circle_radius)

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

        screen.blit(self.sprite, (self.x - half_rect_width, self.y - half_rect_height))

        # Draw hearts
        self.hearts.draw(screen)

        # Updates retreat countdown and other countdowns
        self.shield_countdown = max(self.shield_countdown - 1, 0)
        if self.hp > 0:
            self.retreat_countdown = max(self.retreat_countdown - 1, 0)

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
    def __init__(self, x, y, skin):
        super().__init__()

        self.skin = skin
        self.x = WALL_THICKNESS * x + HALF_WALL_THICKNESS
        self.y = WALL_THICKNESS * y + HALF_WALL_THICKNESS
        self.mx = 0
        self.my = 0
        self.speed = 1

        self.sprite = scale_image(load_img(f"lib\\sprites\\enemies\\{self.skin}.png"), CHAR_SIZE)
        self.rect = self.sprite.get_rect()

    def change_movement(self, x, y):
        # Change knight movement direction.
        self.mx = x
        self.my = y

    def movement_options(self):
        return [(MOVEMENT_SPEED, 0), (-MOVEMENT_SPEED, 0), (0, MOVEMENT_SPEED), (0, -MOVEMENT_SPEED)]

    def choose_random_move(self):
        next_movement = random.choice(self.movement_options())
        self.change_movement(*next_movement)

    def draw(self):
        # Draws itself on the screen.
        half_rect_width = self.rect.width // 2
        half_rect_height = self.rect.height // 2
        screen.blit(self.sprite, (self.x - half_rect_width, self.y - half_rect_height))
