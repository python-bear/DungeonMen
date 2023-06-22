from bin.utils import *


# button class
class Button:
    def __init__(self, x, y, text=False, image=False):
        self.text = text
        self.image = image

        if text:
            self.rect = self.text.get_rect()
            self.rect.topleft = (x, y)

        elif image:
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

        self.clicked = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button on screen
        if self.image:
            surface.blit(self.image, (self.rect.x, self.rect.y))
        elif self.text:
            surface.blit(self.text, (self.rect.x, self.rect.y))

        return action


class InputBox:
    def __init__(self, x, y, w, h=32, text='', bg=(255, 255, 255), max_text_len=5, allowed_chars=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLORS["tan"]
        self.max_text_len = max_text_len
        self.text = text
        self.txt_surface = ALKHEMIKAL_FNT.render(text, True, COLORS["brown"])
        self.active = False
        self.bg_color = bg
        self.allowed_chars = allowed_chars

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLORS["l_tan"] if self.active else COLORS["tan"]
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode not in ("\n", "\r"):
                        if self.allowed_chars is None:
                            self.text += event.unicode
                        elif event.unicode in self.allowed_chars:
                            self.text += event.unicode
                self.txt_surface = ALKHEMIKAL_FNT.render(self.text[:self.max_text_len], True, COLORS["brown"])

        if len(self.text) > self.max_text_len:
            self.text = self.text[:self.max_text_len]

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect.inflate(10, 10))
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(surface, self.color, self.rect.inflate(20, 20), 5)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, fps):
        super().__init__()

        # Set up the sprite sheet for the cursor.
        self.sprite_index = 0
        self.sprites = []
        for i in range(0, 4):
            self.sprites.append(load_img(f"lib\\sprites\\mouse\\torch_{i}.png"))

        self.image = self.sprites[self.sprite_index]
        self.rect = self.image.get_rect()
        self.click_sound = pygame.mixer.Sound("lib\\sounds\\sfx\\click.wav")
        self.fps = fps
        self.quarter_fps = self.fps // 4

    def increment_sprite(self):
        # Goes to the next sprite in the animation every 1/4 fps rounds.
        self.sprite_index += 1

        if self.sprite_index >= 4 * self.quarter_fps:
            self.sprite_index = 0

        self.image = self.sprites[self.sprite_index // self.quarter_fps]

    def click(self):
        self.click_sound.play()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.increment_sprite()


class SkinSelector:
    def __init__(self, surface, skins, screen_width, screen_height, true_knight_skins, skins_per_row=5):
        self.screen = surface
        self.skins = skins
        self.skin_surfaces = []
        self.skins_per_row = skins_per_row
        self.selected_skins = [0, 4, 10, 14]
        self.selected_colors = [COLORS['p_1'], COLORS['p_2'], COLORS['p_3'], COLORS['p_4']]
        self.num_of_rows = len(self.skins) // self.skins_per_row
        self.skin_width = 60
        self.skin_height = 60
        self.select_width = self.skin_width + 10
        self.select_height = self.skin_height + 10
        self.margin = 70
        self.positions = []
        self.skin_surfaces = []
        self.active_player = 0
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.true_knight_skins = true_knight_skins

        # Load the skin images and create surface objects
        for s in self.skins:
            skin_surface = scale_image(self.true_knight_skins[s], 6)
            self.skin_surfaces.append(skin_surface)

        # Calculate the positions of each skin in the grid
        for i in range(len(self.skins)):
            row = i // self.skins_per_row
            col = i % self.skins_per_row
            x = col * (self.skin_width + self.margin) + 40 + \
                (self.SCREEN_WIDTH - (self.skins_per_row * (self.skin_width + self.margin))) // 2
            y = row * (self.skin_height + self.margin) + 50 + \
                (self.SCREEN_HEIGHT - (self.num_of_rows * (self.skin_height + self.margin))) // 2
            self.positions.append((x, y))

    def draw(self):
        # Display the skins on the screen
        for i, skin_surface in enumerate(self.skin_surfaces):
            x, y = self.positions[i]
            if i in self.selected_skins:
                draw_rectangle(self.screen, x - 5, y - 5, self.select_width,
                               self.select_height, self.selected_colors[self.selected_skins.index(i)])
            self.screen.blit(skin_surface, (x, y))

    def handle_mouse_click(self, position):
        for i, skin_surface in enumerate(self.skin_surfaces):
            x, y = self.positions[i]
            rect = pygame.Rect(x, y, self.skin_width, self.skin_height)
            if i not in self.selected_skins:
                # Select new skin
                if rect.collidepoint(position):
                    self.selected_skins[self.active_player] = i
                    break
            else:
                # Change active skin
                if rect.collidepoint(position):
                    self.active_player = self.selected_skins.index(i)


# The following is from StackOverflow @
# https://stackoverflow.com/questions/19877900/tips-on-adding-creating-a-drop-down-selection-box-in-pygame
class OptionBox:
    def __init__(self, x, y, w, h, option_list, color=COLORS["tan"], highlight_color=COLORS["l_tan"], selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surface):
        pygame.draw.rect(surface, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surface, COLORS["brown"], self.rect, 5)
        msg = ALKHEMIKAL_FNT.render(self.option_list[self.selected], 1, COLORS["brown"])
        surface.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y -= (i + 1) * self.rect.height  # Subtract instead of adding
                pygame.draw.rect(surface, self.highlight_color if i == self.active_option else self.color, rect)
                msg = ALKHEMIKAL_FNT.render(text, 1, COLORS["brown"])
                surface.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y - self.rect.height * len(self.option_list), self.rect.width,
                self.rect.height * len(self.option_list))
            pygame.draw.rect(surface, COLORS["brown"], outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y -= (i + 1) * self.rect.height  # Subtract instead of adding
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False


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

    if bg_col is not None:
        surface.fill(bg_col)  # Set the background color

    total_height = 0
    for line in final_text:
        if total_height + fnt.size(line)[1] >= rect.height:
            raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
        temp_surface = None
        if line != "":
            temp_surface = fnt.render(line, True, fg_col, bg_col)  # Enable anti-aliasing with True
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
