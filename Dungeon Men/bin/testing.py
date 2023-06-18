import pygame
import pygame_menu

pygame.init()
surface = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Text Box Example')

def on_text_change(value):
    # This function is called whenever the text in the text box changes
    print("Text changed:", value)

def submit_button_action():
    # This function is called when the submit button is clicked
    print("Submit button clicked")
    menu.disable()

menu = pygame_menu.Menu('Text Box', 400, 300, theme=pygame_menu.themes.THEME_DEFAULT)

text_input = menu.add.text_input('Enter text: ', default='', onchange=on_text_change)
menu.add.button('Submit', submit_button_action)

menu.mainloop(surface)
