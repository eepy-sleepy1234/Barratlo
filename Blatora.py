import os
try:
    import pygame
except ImportError:
    print("pygame not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame
    print("Installed pygame")
import random
import math
from collections import Counter
import sys
import subprocess
import webbrowser
import re
pygame.font.init()
try:
    import numpy
except ImportError:
    print("numpy not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy
    print("Installed numpy")
    
try:
    import cv2
except ImportError:
    import subprocess
    import sys
    print("opencv-python not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
    import cv2
    print("Installed opencv-python")

    

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
SUITS_DIR = os.path.join(ASSETS_DIR, "Suits")
JOKERS_DIR = os.path.join(ASSETS_DIR, "Jokers")
GUI_DIR = os.path.join(ASSETS_DIR, "GUI")
LETTERS_DIR = os.path.join(GUI_DIR, "Letters")
SPRITESHEETS_DIR = os.path.join(ASSETS_DIR, "SpriteSheets")
FONTS_DIR = os.path.join(ASSETS_DIR, "Fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "Sounds")
VIDEO_PATH = os.path.join(ASSETS_DIR, "Soobway.mp4")
TEXT_PATH = os.path.join(ASSETS_DIR, "Text")
BLINDS_DIR = os.path.join(GUI_DIR, "Blinds")
OVERLAY_DIR = os.path.join(ASSETS_DIR, "Overlays")


PLACEHOLDER = os.path.join(GUI_DIR, 'placeholder.png')

def load_image_safe(filepath, fallback_path=PLACEHOLDER):
    """Load image with fallback to placeholder if file not found"""
    try:
        return pygame.image.load(filepath).convert_alpha()
    except (FileNotFoundError, pygame.error):
        print(f"Warning: Could not load {filepath}")
        if fallback_path and os.path.exists(fallback_path):
            print(f"Using fallback image: {fallback_path}")
            return pygame.image.load(fallback_path).convert_alpha()
        else:

            print("Creating placeholder surface")
            surf = pygame.Surface((80, 110))
            surf.fill((200, 200, 200))  
            return surf
        
PixelFont = pygame.font.Font((os.path.join(FONTS_DIR, 'Pixel Game.otf')), int(HEIGHT/10))
PixelFontS = pygame.font.Font((os.path.join(FONTS_DIR, 'Pixel Game.otf')), int(HEIGHT/20))
PixelFontXS = pygame.font.Font((os.path.join(FONTS_DIR, 'Pixel Game.otf')), int(HEIGHT/30))
toggleable = True 
LETTERW = WIDTH/12
LETTERH = WIDTH/12
CENTERLETTERW = (WIDTH/2)-(LETTERW/2)
CENTERLETTERH = (HEIGHT/2)-(LETTERH/2)
currentFrame = 0
card_x = -WIDTH  
card_target_x = 0  
card_animating = False  
card_speed = 15
letter_images = {}
fade_alpha = 255
letters = []
letter_animation = True
endBG = False
settings = False 
help_menu = False
green = (0, 120, 0)
white = (255, 255, 255)
red = (230, 50, 50)
yellow = (250, 220, 80)
orange = (240, 150, 40)
with open((os.path.join(TEXT_PATH,"HelpMenu.txt")), "r", encoding="utf-8") as file:
    helptext = file.read()

help_lines = helptext.split('\n')
helpMenu_surfaces = []
line_height = PixelFont.get_height()

for line in help_lines:
    if line.strip():  
        surface = PixelFont.render(line, True, (0, 0, 0))
        helpMenu_surfaces.append(surface)
    else:
        helpMenu_surfaces.append(None)

helpMenu  = PixelFont.render(helptext, True, (0, 0, 0))
clock = pygame.time.Clock()
pygame.init()
pygame.mixer.init()


pygame.mouse.set_visible(False)


video_cap = None
video_surface = None
VIDEO_WIDTH = 200
VIDEO_HEIGHT = 150
VIDEO_X = 10
VIDEO_Y = 10
VideoVelocityX = 0
VideoVelocityY = 0

def init_video():
    global video_cap
    if os.path.exists(VIDEO_PATH):
        video_cap = cv2.VideoCapture(VIDEO_PATH)
        if not video_cap.isOpened():
            print(f"Error: Could not open video at {VIDEO_PATH}")
            video_cap = None
    else:
        print(f"Video not found at {VIDEO_PATH}")
        video_cap = None

def get_video_frame():
    global video_cap, video_surface
    if video_cap is None or not video_cap.isOpened():
        return None
    
    ret, frame = video_cap.read()
    
    # Loop video if it ends
    if not ret:
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_cap.read()
    
    if ret:
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize frame
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
        
        # Convert to pygame surface
        frame = frame.swapaxes(0, 1)
        video_surface = pygame.surfarray.make_surface(frame)
        return video_surface
    
    return None

def close_video():
    global video_cap
    if video_cap is not None:
        video_cap.release()
        video_cap = None


cursor_normal = load_image_safe(os.path.join(GUI_DIR, 'CursorNormal.png'))
cursor_hover = load_image_safe(os.path.join(GUI_DIR, 'CursorHover.png'))
cursor_normal = pygame.transform.scale(cursor_normal, (32, 32))
cursor_hover = pygame.transform.scale(cursor_hover, (32, 32))
Question_mark = load_image_safe(os.path.join(GUI_DIR, 'QuestionMark.png'))
Question_mark = pygame.transform.scale(Question_mark, (WIDTH/20, WIDTH/12))
Settings_2 = load_image_safe(os.path.join(GUI_DIR, 'Settings2.png'))
Settings_2 = pygame.transform.scale(Settings_2,(int(HEIGHT/5), int(HEIGHT/10.5)))
github_link = load_image_safe(os.path.join(GUI_DIR, 'GithubButton.png'))
github_link = pygame.transform.scale(github_link,(int(HEIGHT/5), int(HEIGHT/10.5)))
helpButtonimg = load_image_safe(os.path.join(GUI_DIR, 'HelpButton.png'))
helpButtonimg = pygame.transform.scale(helpButtonimg,(int(HEIGHT/5), int(HEIGHT/10.5)))  

soseriousmusic = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "WHYSOSERIOUS.mp3"))
Playhand_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "PlayHandButton.png")), (120, 50))
Discardhand_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "DiscardHandButton.png")), (120, 50))
SortbuttonRank_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SortbuttonRank.png")), (120, 50))
SortbuttonSuit_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SortbuttonSuit.png")), (120, 50))
HandBackground_img = pygame.transform.smoothscale(load_image_safe(os.path.join(GUI_DIR, "Handbackground.png")), (240, 105))
ScoreBackground_img = pygame.transform.smoothscale(load_image_safe(os.path.join(GUI_DIR, "ScoreBackground.png")), (240, 75))
GoalBackground_img = pygame.transform.smoothscale(load_image_safe(os.path.join(GUI_DIR, "GoalBackground.png")), (150, 100))
MoneyBackground_img = pygame.transform.smoothscale(load_image_safe(os.path.join(GUI_DIR, "MoneyBackground.png")), (170, 60))
RoundBackground_img = pygame.transform.smoothscale(load_image_safe(os.path.join(GUI_DIR, "RoundBackground.png")), (170, 50))
SideBar_img = pygame.transform.smoothscale(load_image_safe(os.path.join(GUI_DIR, "SideBar.png")), (280, 600))
Debuff_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "DebuffOverlay.png")), (80, 110))
STARTCARD = load_image_safe(os.path.join(GUI_DIR, 'StartCard.png'))
STARTCARD = pygame.transform.smoothscale(STARTCARD,(WIDTH,HEIGHT))
SPINNINGBGIMG = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'StartBackground.png'))
SOSERIOUS = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'SoSerious.png'))
STARTBUTTON = load_image_safe(os.path.join(GUI_DIR, 'StartButton.png'))
STARTBUTTON = pygame.transform.smoothscale(STARTBUTTON,(int(WIDTH/4.4),int(HEIGHT/10)))
STARTBUTTON_X = int((WIDTH/2)- ((WIDTH/4.4)/2))
STARTBUTTON_Y = (HEIGHT/2)+CENTERLETTERH/2
start_button_rect = STARTBUTTON.get_rect()
start_button_rect.topleft = (STARTBUTTON_X, STARTBUTTON_Y)
SETTINGSIMG = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'SettingsButton.png'))
SETTINGONIMG = load_image_safe(os.path.join(GUI_DIR, 'Setting_on.png'))
SETTINGOFFIMG = load_image_safe(os.path.join(GUI_DIR, 'Setting_off.png'))
SETTINGONIMG = pygame.transform.scale(SETTINGONIMG,(int(HEIGHT/5),int(HEIGHT/10)))
SETTINGOFFIMG = pygame.transform.scale(SETTINGOFFIMG, (int(HEIGHT/5),int(HEIGHT/10)))
SETTINGSRECT = SETTINGONIMG.get_rect()
xbutton = load_image_safe(os.path.join(GUI_DIR, 'XButton.png'))
xbutton = pygame.transform.scale(xbutton,(int(HEIGHT/10), int(HEIGHT/10)))
xbutton_rect = xbutton.get_rect()
xbutton_rect.topleft = ((WIDTH - xbutton_rect.width), 0)
playhandw = Playhand_img.get_width()
playhandh = Playhand_img.get_height()
sortrankw = SortbuttonSuit_img.get_width()
sortrankh = SortbuttonSuit_img.get_height()
SortbuttonSuit_rect = SortbuttonSuit_img.get_rect()
SortbuttonSuit_rect.topleft = (int(WIDTH/2 - (sortrankw +sortrankw/2)), int(HEIGHT - int(sortrankh + sortrankh/10)))
SortbuttonRank_rect = SortbuttonRank_img.get_rect()
SortbuttonRank_rect.topleft = (int (WIDTH/2 + (sortrankw/2)), int(HEIGHT - int(sortrankh + sortrankh/10)))
Playhand_rect = Playhand_img.get_rect()
Playhand_rect.topleft = (int(0 + playhandw/4), HEIGHT - int(playhandh *2 ))
Discardhand_rect = Playhand_img.get_rect()
Discardhand_rect.topleft = (int(WIDTH - (playhandw + playhandw/4)), HEIGHT - int(playhandh *2 ))
for root, dirs, files in os.walk(LETTERS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            letter_name = os.path.splitext(filename)[0]
            image = pygame.transform.scale(load_image_safe(filepath), (int(LETTERW), int(LETTERH)))
            letter_images[letter_name] = image
StartingBimg = letter_images['StartBimg']
StartingAimg = letter_images['StartAimg']
StartingLimg = letter_images['StartLimg']
StartingA2img = letter_images['StartAimg']
StartingTimg = letter_images['StartTimg']
StartingRimg = letter_images['StartRimg']
StartingOimg = letter_images['StartOimg']


developer = False
setting_width = WIDTH/6
setting_height = HEIGHT/5
settingsList = []
devtoggle = ""


class User_settings():
    def __init__(self,name):
        
        self.toggle = False
        font_size = int(HEIGHT / 40)
        self.name = PixelFont.render(name, True, (0, 0, 0))

        self.img = SETTINGOFFIMG
        settingsList.append(self)
     
        self.rect = SETTINGSRECT.copy()
        
    def update_img(self):
        if self.toggle:
            self.img = SETTINGONIMG
        elif not self.toggle:
            self.img = SETTINGOFFIMG
    def check_dev(self):
        global developer
        global devtoggle
        
        if developer == False:
            
            if self == DEV_MODE:
                answer = input("Insert Dev Key")
                if answer == devkey:
                    self.toggle = True
                    developer = True
                    global answer2
                    devtoggle = input("Insert Toggle Key")
             
                elif answer != devkey:
                    self.toggle = False
                    print('incorect')
            self.update_img()



            
prev_attention_state = False
            
    
        
    
DEV_MODE = User_settings('Developer')
dev_toggle = False
SO_SERIOUS = User_settings('SO SERIOUS')
Atttention_helper = User_settings('Attention Span Helper')

def dev_commands():
    global dev_toggle
    global dev_command
    if DEV_MODE.toggle:
        if dev_toggle:
            dev_command = input('Insert Developer Command')

            

guibutton = []
guiToggleList = []
class GUITOGGLES():
    def __init__(self, x, y, sprite, scale_factor=1.1, isbutton = False):
        self.x = x
        self.y = y
        self.toggle = False
        self.hover = False
        self.should_draw = False
        self.rect = sprite.get_rect(center=(x, y))
        self.original_image = sprite
        self.sprite = sprite
        self.scale_factor = scale_factor
        guiToggleList.append(self)
        self.isbutton = isbutton
        if self.isbutton == True:
            guibutton.append(self)
            
    
    def draw(self):
        if self.should_draw:
 
            blit_rect = self.sprite.get_rect(center=(self.x, self.y))
            screen.blit(self.sprite, blit_rect)
            self.rect = blit_rect
    
    def update_img(self, mouse_pos):
        if self.should_draw:
            if self.rect.collidepoint(mouse_pos):
                self.hover = True
            else:
                self.hover = False
        
            if self.hover:
                w, h = self.original_image.get_size()
                new_w = int(w * self.scale_factor)
                new_h = int(h * self.scale_factor)
                self.sprite = pygame.transform.scale(self.original_image, (new_w, new_h))
            else:
                self.sprite = self.original_image                  
                                                    
                    
question = GUITOGGLES(WIDTH - (WIDTH/20), 0 + WIDTH/20, Question_mark, scale_factor=1.15, isbutton=False)
settings2 = GUITOGGLES(0, 0, Settings_2, scale_factor=1.15, isbutton=True)
helpButton = GUITOGGLES(0, 0, helpButtonimg, scale_factor=1.15, isbutton=True)    
githubButton = GUITOGGLES(0, 0, github_link, scale_factor=1.15, isbutton=True)    

def update_gui_buttons():

    if question.toggle:

        button_spacing = int(HEIGHT / 10)
        start_y = int(HEIGHT / 10)
        
        for index, button in enumerate(guibutton):
            button.should_draw = True
            button.x = int(WIDTH / 10)
            button.y = start_y + (index * button_spacing)
    else:

        for button in guibutton:
            button.should_draw = False        
 
        

        

        
def draw_settings():
    index = 0
    for setting in settingsList:
        x_pos = int(WIDTH/20)
        y_pos = int((HEIGHT/10 + 20) * index) + 20
        text_x = x_pos + setting.img.get_width() + 10 
        screen.blit(setting.name, (text_x, y_pos))
    
        screen.blit(setting.img, (x_pos, y_pos))
        setting.rect.x = x_pos
        setting.rect.y = y_pos
        index += 1
        setting.update_img()


        
dev_selection = True
blitting = False    
def blit_img():
    global blitting
    global blitpositionx
    global blitpositiony
    global blitting_img
    global blitting_img_original
    global dev_toggle
    global scaling
    global dimensionsx
    global dimensionsy
    if blitting and blitting_img_original:
        if scaling == 'wh':
            blitting_img = pygame.transform.scale(blitting_img_original, (int(WIDTH/dimensionsx), int(HEIGHT/dimensionsy)))
        elif scaling == 'ww':
            blitting_img = pygame.transform.scale(blitting_img_original, (int(WIDTH/dimensionsx), int(WIDTH/dimensionsy)))
        elif scaling == 'hh':
            blitting_img = pygame.transform.scale(blitting_img_original, (int(HEIGHT/dimensionsx), int(HEIGHT/dimensionsy)))
        elif scaling == 'hw':
            blitting_img = pygame.transform.scale(blitting_img_original, (int(HEIGHT/dimensionsx), int(WIDTH/dimensionsy)))
        elif scaling == 'pixel':
            blitting_img = pygame.transform.scale(blitting_img_original, (int(dimensionsx), int(dimensionsy)))
        
        screen.blit(blitting_img, (blitpositionx, blitpositiony))

    if DEV_MODE.toggle:
        while dev_toggle:
            
            if dev_command.lower() == 'setblit':
                asset = input('Input asset name, including .png if a png: ')
                directory = input('Choose a directory(assets, joker, gui, Suits): ').lower()

                if directory == 'assets':
                    directory = ASSETS_DIR
                elif directory == 'joker':
                    directory = JOKERS_DIR
                elif directory == 'gui':
                    directory = GUI_DIR
                elif directory == 'suits':
                    directory = SUITS_DIR
                else:
                    print("Invalid Directory")
                    dev_toggle = False
                    return

                scaling = input('WH, WW, HH, HW, pixel: ').lower()

                blitpositionx = input('Xposition (Width/chosenxpos): ')
                blitpositiony = input('Yposition (Height/Chosenypos): ')
                try:
                    if blitpositionx == '0':
                        blitpositionx = 0
                    if blitpositiony == '0':
                        blitpositiony = 0

                    if blitpositionx != 0:
                        blitpositionx = int(WIDTH/(float(blitpositionx)))
                    if blitpositiony != 0:
                        blitpositiony = int(HEIGHT/(float(blitpositiony)))
                except:
                    print("Invalid position")
                    dev_toggle = False
                    return
                
                dimensionsx = input('Choose a width: ')
                dimensionsy = input('Choose a height: ')
                try:
                    dimensionsx = float(dimensionsx)
                    dimensionsy = float(dimensionsy)
                except:
                    print("Invalid dimensions")
                    dev_toggle = False
                    return
                
                try:
                    blitting_img_original = pygame.image.load(os.path.join(directory, str(asset))).convert_alpha()
                except:
                    print("Something went wrong loading image")
                    dev_toggle = False
                    return
                
                try:
                    if scaling == 'wh':
                        blitting_img = pygame.transform.scale(blitting_img_original, (int(WIDTH/dimensionsx), int(HEIGHT/dimensionsy)))
                    elif scaling == 'ww':
                        blitting_img = pygame.transform.scale(blitting_img_original, (int(WIDTH/dimensionsx), int(WIDTH/dimensionsy)))
                    elif scaling == 'hh':
                        blitting_img = pygame.transform.scale(blitting_img_original, (int(HEIGHT/dimensionsx), int(HEIGHT/dimensionsy)))
                    elif scaling == 'hw':
                        blitting_img = pygame.transform.scale(blitting_img_original, (int(HEIGHT/dimensionsx), int(WIDTH/dimensionsy)))
                    elif scaling == 'pixel':
                        blitting_img = pygame.transform.scale(blitting_img_original, (int(dimensionsx), int(dimensionsy)))
                    
                    blitting = True
                    dev_toggle = False
                    return

                except:
                    print("Something went wrong scaling")
                    dev_toggle = False
                    return

            elif dev_command.lower() == 'cancel':
                dev_toggle = False
                return
            
            elif dev_command.lower() == 'unblit':
                blitting = False
                dev_toggle = False
                return
            
            elif dev_command.lower() == 'reblit':
                blitting = True
                dev_toggle = False
                return
            
            elif dev_command.lower() == 'help':
                print("Commands: \n Help\n reblit\n unblit\n cancel\n setblit\n blitW\n blitH\n blitx\n blity\n changescaling\n sethand\n resetdeck\n setresources\n")
                dev_toggle = False
                return

            elif dev_command.lower() == 'blitx':
                new_x = input("Insert New X position (Width/x): ")
                try:
                    if new_x == '0':
                        blitpositionx = 0
                    else:
                        blitpositionx = int(WIDTH/float(new_x))
                    print(f"X position updated to: {blitpositionx}")
                except:
                    print("Invalid position")
                dev_toggle = False
                return
            
            elif dev_command.lower() == 'blity':
                new_y = input("Insert New Y position (Height/y): ")
                try:
                    if new_y == '0':
                        blitpositiony = 0
                    else:
                        blitpositiony = int(HEIGHT/float(new_y))
                    print(f"Y position updated to: {blitpositiony}")
                except:
                    print("Invalid position")
                dev_toggle = False
                return
            
            elif dev_command.lower() == 'changescaling':
                new_scale = input("Insert New Scale Config (wh, ww, hh, hw, pixel): ").lower()
                scaling = new_scale
                print(f"Scaling mode changed to: {scaling}")
                dev_toggle = False
                return

            elif dev_command.lower() == 'blitw':
                new_W = input("Insert New Width: ")
                try:
                    dimensionsx = float(new_W)
                    print(f"Width updated to: {dimensionsx}")
                except:
                    print("Invalid number")
                dev_toggle = False
                return
            
            elif dev_command.lower() == 'blith':
                new_H = input("Insert New Height: ")
                try:
                    dimensionsy = float(new_H)
                    print(f"Height updated to: {dimensionsy}")
                except:
                    print("Invalid number")
                dev_toggle = False
                return

            elif dev_command.lower() == 'sethand':
                print("Available ranks: Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, Ace")
                print("Available suits: Hearts, Diamonds, Clubs, Spades")
                print("Enter cards one at a time. Type 'done' when finished.")
                dev_selection = True

                hand.clear()
                
                card_templates = {}
                temp_deck = []
                for root, dirs, files in os.walk(SUITS_DIR):
                    for filename in files:
                        if filename.endswith(".png"):
                            filepath = os.path.join(root, filename)
                            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
                            name, _ = os.path.splitext(filename)
                            rank, suit = name.split("Of")
                            card_key = f"{rank}Of{suit}"
                            if card_key not in card_templates:
                                card_templates[card_key] = (rank, suit, image)
                            card = Card(rank, suit, image)
                            temp_deck.append(card)
                
                card_count = 0
                hand.clear()
                while card_count < 8:
                    rank_input = input(f"Card {card_count + 1} - Rank (or 'done'): ").strip()
                    rank_input.lower()
                    
                    if rank_input.lower() == 'done':
                        break
                        
                    suit_input = input(f"Card {card_count + 1} - Suit: ").strip()

                    card_key = f"{rank_input}Of{suit_input}"
                    if card_key in card_templates:
                        rank, suit, image = card_templates[card_key]
                        new_card = Card(rank, suit, image)
                        new_card.slot = card_count
                        new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
                        new_card.state = "hand"
                        hand.append(new_card)
                        card_count += 1
                        print(f"Added {card.rank} of {card.suit}")
                    else:
                        print(f"Card '{rank_input}' of '{suit_input}' not found. Check spelling.")
                        print(f"Example: 'Three' and 'Diamonds' (capital first letter)")
                
                sort_hand()
                print(f"Hand set with {len(hand)} cards")
                dev_toggle = False
                return

            elif dev_command.lower() == 'resetdeck':
            
                hand.clear()
                
                card_count = {}
                deck.clear()
                deck = perm_deck.copy()
                random.shuffle(deck)
                

                for i in range(handsize):
                    if deck:
                        card = deck.pop()
                        card.slot = i
                        card.x, card.y = WIDTH + 100, HEIGHT - 170
                        card.state = "hand"
                        hand.append(card)
                
                sort_hand()
                print(f"Deck reset! New hand dealt with {len(hand)} cards. {len(deck)} cards remaining in deck.")
                dev_toggle = False
                return


            elif dev_command.lower() == 'setresources':
                global hands, discards, chips, mult
                try:
                    hands = int(input("Set hands remaining: "))
                    discards = int(input("Set discards remaining: "))
                    print(f"Resources updated: {hands} hands, {discards} discards")
                except:
                    print("Invalid input")
                dev_toggle = False
                return
            elif dev_command.lower() == 'setround':
                global ante, round_num
                try:
                    ante = int(input("set current ante:"))
                    blind_num = int(input(f"set current blind:\n(1 for small blind, 2 for big blind, and 3 for boss blind)"))
                    round_num = (ante * 3) + blind_num
                    print(f"Round set: ante {ante}, round {round_num}")
                except:
                    print("Invalid input")
                dev_toggle = False
                return
            else:
                print("Unknown command. Type 'help' for list of commands.")
                dev_toggle = False
                return
            
class starting_letters():
    def __init__(self,sprite_name,xpos,ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.sprite_name = sprite_name
        self.move_speed = 0.2
        self.target_x = 0
        self.target_y = LETTERH
        self.is_moving = False
        self.move_progress = 0.0
        self.animation = False
        self.main_ypos = CENTERLETTERH
        self.delay  = 0
        self.delay_timer = 0
        if sprite_name == StartingBimg: self.letter = 'B'
        elif sprite_name == StartingAimg: self.letter = 'A' 
        elif sprite_name == StartingLimg: self.letter = 'L'
        elif sprite_name == StartingA2img: self.letter = 'A'
        elif sprite_name == StartingTimg: self.letter = 'T'
        elif sprite_name == StartingRimg: self.letter = 'R'
        elif sprite_name == StartingOimg: self.letter = 'O'

    def draw(self):
        screen.blit(self.sprite_name,(int(self.xpos),int(self.ypos)))
    def updatex(self, lerp_factor=0.05):
        self.xpos += (self.target_x - self.xpos) * lerp_factor
    def updatey(self, lerp_factor=0.05):
        self.ypos += (self.target_y - self.ypos) * lerp_factor

    def animate(self):
        if self.delay > 0:
            self.delay -= 1
            return
    
        if not hasattr(self, 'bob_timer'):
            self.bob_timer = 0
    
        if startAnimation:
            self.bob_timer += 0.05  
            bob_offset = math.sin(self.bob_timer) * (LETTERH/3)  
            self.ypos = self.main_ypos + bob_offset
def update_card_animation():
    global endBG
    global card_x, card_animating
    
    if card_animating:
        if card_x < WIDTH:  
            card_x += card_speed
            if card_x >= WIDTH:
                card_x = WIDTH
                card_animating = False
        if card_x >= 0:  
            endBG = True
        
def letter_classes():
    
    global LetterPosx
    
    
    LetterPosx = [(CENTERLETTERW - LETTERW*3),
                       (CENTERLETTERW - LETTERW*2),
                       (CENTERLETTERW - LETTERW),
                       (CENTERLETTERW),
                       (CENTERLETTERW + LETTERW),
                       (CENTERLETTERW + LETTERW*2),
                       (CENTERLETTERW + LETTERW*3)]

    global Letters
    
    
    
    global StartingB
    global StartingA
    global StartingL
    global StartingA2
    global StartingT
    global StartingR
    global StartingO
    StartingB = starting_letters(StartingBimg,LetterPosx[0], CENTERLETTERH)
    StartingA = starting_letters(StartingAimg,LetterPosx[1], CENTERLETTERH)
    StartingL = starting_letters(StartingLimg,LetterPosx[2], CENTERLETTERH)
    StartingA2 = starting_letters(StartingA2img,LetterPosx[3], CENTERLETTERH)
    StartingT = starting_letters(StartingTimg,LetterPosx[4], CENTERLETTERH)
    StartingR = starting_letters(StartingRimg,LetterPosx[5], CENTERLETTERH)
    StartingO = starting_letters(StartingOimg,LetterPosx[6], CENTERLETTERH)
    Letters = [StartingB, StartingA, StartingL, StartingA2, StartingT, StartingR, StartingO]
    
    
    global shuffled_letters
    shuffled_letters = LetterPosx.copy()
    random.shuffle(shuffled_letters)
    if shuffled_letters == LetterPosx:
        random.shuffle(shuffled_letters)
    StartingB.target_x = shuffled_letters[0]
    StartingA.target_x = shuffled_letters[1]
    StartingL.target_x = shuffled_letters[2]
    StartingA2.target_x = shuffled_letters[3]
    StartingT.target_x = shuffled_letters[4]
    StartingR.target_x = shuffled_letters[5]
    StartingO.target_x = shuffled_letters[6]

    
            
def animate_letters():
    global letter_animation
    screen.fill((255,255,255))
    for i in Letters:
        i.draw()
    pygame.display.flip()
    pygame.time.wait(200)
        
    global letter_animation
    while letter_animation:
        for event in pygame.event.get():
            if event.type  == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        screen.fill((255,255,255))
        for i in Letters:
            i.updatex()
            
            i.draw()
        pygame.display.flip()
        clock.tick(60)
        if abs(StartingB.xpos - StartingB.target_x) < 1:
            letter_animation = False

perm_deck = []
handsize = 8
chips = 0
mult = 0
current_score = 0
round_score = 0
scored_counter = 0
total_scoring_count = 0
max_hand = 4
max_discard = 4
hands = max_hand
discards = max_discard
DRAG_THRESHOLD = 10
calc_progress = 0.0
saved_base_chips  = 0
saved_base_mult = 0
saved_level = 0
blind_reward = 0
saved_hand = None
boss_calculated = False
sort_mode = "rank"
current_scoring_card = None
Hand_levels = {
    "High Card": 1,
    "Pair": 1,
    "Two Pair": 1,
    "Three of a Kind": 1,
    "Straight": 1,
    "Flush": 1,
    "Full House": 1,
    "Four of a Kind": 1,
    "Straight Flush": 1,
    "Five of a Kind": 1,
    "Flush House": 1,
    "Flush Five": 1,
    }

Hand_Mult = {
    "High Card": 1,
    "Pair": 2,
    "Two Pair": 2,
    "Three of a Kind": 3,
    "Straight": 4,
    "Flush": 4,
    "Full House": 4,
    "Four of a Kind": 7,
    "Straight Flush": 8,
    "Five of a Kind": 12,
    "Flush House": 14,
    "Flush Five": 16,
    }

Hand_Chips = {
    "High Card": 5,
    "Pair": 10,
    "Two Pair": 20,
    "Three of a Kind": 30,
    "Straight": 30,
    "Flush": 35,
    "Full House": 40,
    "Four of a Kind": 60,
    "Straight Flush": 100,
    "Five of a Kind": 120,
    "Flush House": 140,
    "Flush Five": 160,
    }
scored = False
scoring_in_progress = False
calculating = False
discarding = False
round_num = 1
ante = 1
money = 0
blind_defeated = False
victory = False
target_score = 300
contributing = []
BLIND_X = 10
BLIND_Y = 25
total_score = 0
saved_total_score = 0

SCORED_POSITIONS = [
    (WIDTH//2 - 150, HEIGHT//2 - 50),
    (WIDTH//2 - 50, HEIGHT//2 - 50),
    (WIDTH//2 + 50, HEIGHT//2 - 50),
    (WIDTH//2 + 150, HEIGHT//2 - 50),
    (WIDTH//2 + 250, HEIGHT//2 - 50)
]

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUES = {
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
    "Six": 6,
    "Seven": 7,
    "Eight": 8,
    "Nine": 9,
    "Ten": 10,
    "Jack": 11,
    "Queen": 12,
    "King": 13,
    "Ace": 14
}
ANTE_SCALING = {
    1: 300,
    2: 800,
    3: 2000,
    4: 5000,
    5: 11000,
    6: 20000,
    7: 35000,
    8: 50000,
    9: 110000,
    10: 560000,
    11: 7200000,
    12: 300000000,
    13: 47000000000,
    14: 290000000000000,
    15: 77000000000000000000,
    16: 860000000000000000000000,
    }

class Card:
    card_id_counter = 0
    def __init__(self, rank, suit, image, slot=None, state="hand", debuff=False, enhancement=None, edition=None, seal=None):
        self.image = image
        self.scale= 1.0
        self.rotation_speed = 0
        self.scaling_delay = 0
        self.is_debuffed = debuff
        self.enhancement = enhancement
        self.edition = edition
        self.seal = seal
        self.scaling = False
        self.growing = False
        self.scaling_done = False
        self.scoring_complete = False
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]
        self.card_id = Card.card_id_counter
        Card.card_id_counter += 1
        if self.is_debuffed:
            self.chip_value = 0
        else:
            if self.value in (11, 12, 13):
                self.chip_value = 10
            elif self.value == 14:
                self.chip_value = 11
            else:
                self.chip_value = self.value
        self.name = f"{rank} of {suit}"
        self.rect = image.get_rect()
        self.state = state
        self.slot = slot
        self.vx = 0
        self.vy = 0
        self.x = 0
        self.target_x = 0
        self.scoring_x = 0
        self.scoring_y = 0
        self.y = 0
        self.angle = 0
        self.target_y = 0
        self.play_timer = 0
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
        self.is_contributing = False
        self.scoring_animating = False
        self.idx = 0
    def update(self):
        scoring_count = 0
        stiffness = 0.3
        damping = 0.7
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        if not self.dragging:
            self.vx += dx * stiffness
            self.vy += dy * stiffness
            self.vx *= damping
            self.vy *= damping
            if abs(self.vx) > 0.1:
                self.x += self.vx
            if abs(self.vy) > 0.1:
                self.y += self.vy
        elif self.scoring_animating:
            lerp_t = 0.18
            self.x += (self.target_x - self.x) * lerp_t
            self.y += (self.target_y - self.y) * lerp_t
            self.angle += (0 - self.angle) * 0.15
            if abs(self.x - self.target_x) < 2 and abs(self.y - self.target_y) < 2:
                self.x = self.target_x
                self.y = self.target_y
        if self.scaling:
            if self.scaling_delay < 30:
                self.scaling_delay += 1
            else:
                if not self.growing:
                    if self.scale > 0.51:
                        self.scale -= 0.1
                        self.rotation_speed = 3
                    else:
                        self.scale = 0.5
                        self.rotation_speed = -3
                        self.growing = True
                else:
                    if self.scale < 1.0:
                        self.scale += 0.1
                    else:
                        self.scale = 1.0
                        self.rotation_speed = 0
                        self.scaling = False
                        self.growing = False
                        self.scaling_done = True
                        self.scoring_animating = False
                        self.scaling_delay = 10
                        self.angle = 0
                        scoring_count += 1
                        if self.is_contributing:
                            global saved_base_chips
                            saved_base_chips += self.chip_value
                            indicator = ChipIndicator(int(self.x - 50), int(self.y - 100), self.chip_value)
                            chip_indicators.append(indicator)
                            self.state = "scored"
                            self.scoring_complete = True
                        else:
                            self.state = "discarded"
        self.angle += self.rotation_speed
        return scoring_count

chip_indicators = []
class ChipIndicator:
    def __init__(self, x, y, chip_value):
        self.x = x
        self.y = y
        self.start_y = y
        self.chip_value = chip_value
        self.alpha = 255
        self.lifetime = 60
        self.age = 0
    def update(self):
        self.age += 1
        self.y = self.start_y - (self.age * 0.1)
        if self.age > 40:
            self.alpha = int(255 * (1 - (self.age - 40) / 20))
        return self.age < self.lifetime
    def draw(self, surface):
        diamond_size = 60
        half = diamond_size//2
        diamond_points = [
            (self.x, self.y - half),
            (self.x + half, self.y),
            (self.x, self.y + half),
            (self.x - half, self.y)
            ]
        angle = math.radians(3)
        rotated_points = []
        for px, py in diamond_points:
            dx, dy = px - self.x, py - self.y
            new_x = dx * math.cos(angle) - dy * math.sin(angle)
            new_y = dx * math.sin(angle) + dy * math.cos(angle)
            rotated_points.append((new_x + self.x, new_y + self.y))
        diamond_surface = pygame.Surface((diamond_size * 2, diamond_size * 2), pygame.SRCALPHA)
        adjusted_points = [(p[0] - self.x + diamond_size, p[1] - self.y + diamond_size) for p in rotated_points]
        pygame.draw.polygon(diamond_surface, (0, 100, 255, self.alpha), adjusted_points)
        diamond_surface.set_alpha(self.alpha)
        surface.blit(diamond_surface, (self.x - diamond_size, self.y - diamond_size))
        font = pygame.font.SysFont(None, 48)
        text = PixelFont.render(f"+{self.chip_value}", True, (255, 255, 255))
        text.set_alpha(self.alpha)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)
for root, dirs, files in os.walk(SUITS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
            name, _ = os.path.splitext(filename)
            rank, suit = name.split("Of")
            card = Card(rank, suit, image)
            perm_deck.append(card)

deck = perm_deck.copy()

random.shuffle(deck)

hand = []
for i in range(handsize):
    card = deck.pop()
    card.slot = i
    card.x, card.y = WIDTH + 100, HEIGHT - 170
    card.state = "hand"
    hand.append(card)

currentFrame = 0
spacing = 600 / handsize

def boss_debuff():
    global round_num, boss_name, boss_calculated
    if round_num % 3 == 0:
        if current_blind.name == "The Bird":
            for card in deck:
                if card.suit == "Hearts":
                    card.is_debuffed = True
        if current_blind.name == "The Arrow":
            for card in deck:
                if card.suit == "Spades":
                    card.is_debuffed = True
        if current_blind.name == "The Cone":
            for card in deck:
                if card.suit == "Clubs":
                    card.is_debuffed = True
        if current_blind.name == "The Eye":
            for card in deck:
                if card.suit == "Diamonds":
                    card.is_debuffed = True
        if current_blind.name == "The Bounce":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Bow":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Bridge":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Chair":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Crate":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Luck":
            for card in deck:
                rand = random.randint(1, 10)
                if rand == 1:
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Fork":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Ramp":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Sandwich":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
        if current_blind.name == "The Twin":
            for card in deck:
                if card.suit == "idk":
                    card.is_debuffed = True
    else:
        for card in deck:
            card.is_debuffed = False
            

def draw_hand(surface, cards, center_x, center_y, spread=20, max_vertical_offset=-30, angle_range=8):
    global scoring_in_progress, scoring_sequence_index
    if "scoring_in_progress" not in globals():
        scoring_in_progress = False
    if "scoring_sequence_index" not in globals():
        scoring_sequence_index = 0
    n = len(cards)
    if n == 0:
        return
    start_angle = -angle_range / 2
    angle_step = angle_range / (n - 1) if n > 1 else 0
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2.25

    for i, card in enumerate(cards):
        t = i / (n - 1) if n > 1 else 0.5
        target_x = start_x + i * spread
        target_y = center_y - max_vertical_offset * 2 * (t - 0.5)**2 + max_vertical_offset
        if card.state == "selected":
            target_y -= 40
        elif card.state == "played":
            if card.scoring_x == 0:
                if scoring_sequence_index < len(SCORED_POSITIONS):
                    card.scoring_x, card.scoring_y = SCORED_POSITIONS[scoring_sequence_index]
                    scoring_sequence_index += 1
                    card.angle = 0
            if card.is_contributing:
                card.scoring_animating = True
            else:
                card.waiting = True
            card.idx = scoring_sequence_index
        elif card.state == "discarded":
            target_y -= 100
            target_x += WIDTH + 200
            card.angle -= 15
                
        if card.state == "hand":
            card.angle = (t - 0.5) * -2 * angle_range
        if card.scoring_x != 0:
            if card.is_contributing:
                if card.scoring_y == HEIGHT//2 - 50:
                    card.scoring_y -= 25
            target_x, target_y = card.scoring_x, card.scoring_y
            if not card.scaling:
                card.angle = 0
        card.target_x = target_x
        card.target_y = target_y
        angle = card.angle
        scaled_w = int(card.image.get_width() * card.scale)
        scaled_h = int(card.image.get_height() * card.scale)
        scaled_img = pygame.transform.smoothscale(card.image, (scaled_w, scaled_h))
        if card.is_debuffed and not boss_calculated:
            card.chip_value = 0
            scaled_overlay = pygame.transform.smoothscale(Debuff_img, (scaled_w, scaled_h))
            scaled_img = scaled_img.copy()
            scaled_img.blit(scaled_overlay, (0, 0))
        rotated = pygame.transform.rotate(scaled_img, angle)
        rect = rotated.get_rect(center=(card.x, card.y))
        surface.blit(rotated, rect.topleft)
        card.rect = rect

class Joker_Animation():
    def __init__(self, sprite_name, frame_width, frame_height, fps, frames, xpos, ypos, setWidth, setHeight):
        self.sprite_sheet = sprite_name
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        self.current_frame = 0
        self.xpos = xpos
        self.ypos = ypos
        self.frames = frames
        self.frame_interval = int(60//fps)
        self.setWidth = setWidth
        self.setHeight = setHeight
        
        self.cached_frames = []
        for i in range(frames):
            frame_x = i * frame_width
            frame_surface = sprite_name.subsurface((frame_x, 0, frame_width, frame_height))
            scaled = pygame.transform.smoothscale(frame_surface, (setWidth, setHeight))
            self.cached_frames.append(scaled)
        
    def animate(self):
        if currentFrame % self.frame_interval == 0:
            self.current_frame = (self.current_frame + 1) % self.frames
        
        screen.blit(self.cached_frames[self.current_frame], (self.xpos, self.ypos))
    
    def reset_animation(self):
        self.current_frame = 1
class Draggable_Animation(Joker_Animation):
    def __init__(self, sprite_name, frame_width, frame_height, fps, frames, xpos, ypos, setWidth, setHeight):
        super().__init__(sprite_name, frame_width, frame_height, fps, frames, xpos, ypos, setWidth, setHeight)
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
        self.rect = pygame.Rect(xpos, ypos, setWidth, setHeight)
    
    def animate(self):
        if currentFrame % self.frame_interval == 0:
            self.current_frame = (self.current_frame + 1) % self.frames
        
        screen.blit(self.cached_frames[self.current_frame], (int(self.xpos), int(self.ypos)))
        self.rect.x = int(self.xpos)
        self.rect.y = int(self.ypos)


spinningBG = Joker_Animation(SPINNINGBGIMG, 1980, 1080, 24, 71, 0, 0, WIDTH, HEIGHT)
settingsButton = Joker_Animation(SETTINGSIMG, 333, 333, 23, 50, WIDTH - WIDTH/6,HEIGHT - WIDTH/6, WIDTH/6, WIDTH/6)
soserious = Draggable_Animation(SOSERIOUS, 250, 250, 24, 39, 0, 0, int(WIDTH/5), int(WIDTH/5))
setting_rect = pygame.Rect(WIDTH-WIDTH/6 , HEIGHT - WIDTH/6, WIDTH/6, WIDTH/6)

class Blind:
    def __init__(self, name, image, x, y, state):
        self.name = name
        self.image = image
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.vx = 0
        self.vy = 0
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
        self.rect = image.get_rect()
        self.rect.topleft = (x, y)
        self.drag_start = (0, 0)
    def update(self):
        stiffness = 0.5
        damping = 0.4
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        if not self.dragging:
            self.vx += dx * stiffness
            self.vy += dy * stiffness
            self.vx *= damping
            self.vy *= damping
            if abs(self.vx) > 0.1:
                self.x += self.vx
            if abs(self.vy) > 0.1:
                self.y += self.vy
        self.rect.topleft = (int(self.x), int(self.y))
    def draw(self, surface):
        surface.blit(self.image, (int(self.x), int(self.y)))

small_blind = None
big_blind = None
boss_blinds = []
for root, dirs, files in os.walk(BLINDS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            blind_name_raw = os.path.splitext(filename)[0]
            blind_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', blind_name_raw)
            blind_name = blind_name.title()
            image = pygame.transform.scale(load_image_safe(filepath), (100, 100))
            if "Small" in blind_name:
                small_blind = Blind(blind_name, image, -150, -150, "small")
            elif "Big" in blind_name:
                big_blind = Blind(blind_name, image, -150, -150, "big")
            else:
                blind_obj = Blind(blind_name, image, -150, -150, "boss")
                boss_blinds.append(blind_obj)
current_blind = None
def calculate_target_score(ante, round_num):
    base_score = ANTE_SCALING[ante]
    multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 4.0}
    return int(base_score * multipliers[round_num % 3 if round_num % 3 != 0 else 3])
def get_current_blind():
    global round_num, ante, current_blind, target_score, blind_reward, victory, total_score
    if not current_blind or victory:
        if round_num % 3 == 1:
            if small_blind:
                current_blind = small_blind
                blind_reward = 3
                current_blind.blind_type = "small"
        elif round_num % 3 == 2:
            if big_blind:
                current_blind = big_blind
                blind_reward = 4
                current_blind.blind_type = "big"
        elif round_num % 3 == 0:
            if boss_blinds:
                current_blind = random.choice(boss_blinds)
                blind_reward = 5
                current_blind_type = "boss"
        if current_blind:
            current_blind.target_x = BLIND_X
            current_blind.target_y = BLIND_Y
            current_blind.vx = 0
            current_blind.vy = 0
            current_blind.score_required = calculate_target_score(ante, round_num)
            target_score = current_blind.score_required
            victory = False
            total_score = 0
    return current_blind
def advance_to_next_blind():
    global round_num, ante, hands, discards, current_score, money, blind_reward, deck, perm_deck, hand
    if round_num % 3 == 0:
        ante += 1
    round_num += 1
    current_score = 0
    money += hands
    hands = max_hand
    discards = max_discard
    money += blind_reward
    hand.clear()
    deck.clear()
    deck = perm_deck.copy()
    print(len(perm_deck))
    print(len(deck))
    random.shuffle(deck)
def check_blind_defeated():
    global blind_defeated, current_score
    if current_blind and total_score >= target_score:
        blind_defeated = True
        return True
    else:
        return False
get_current_blind()

def change_notation(number):
    if number > 999999999999:
        saved_number = number
        place = 0
        while saved_number > 9:
            saved_number /= 10
            saved_number = round(saved_number, 2)
            place += 1
        number = f"{saved_number}e{place}"
    return number

def detect_hand(cards):
    n = len(cards)
    if n == 0:
        return "", []
    values = sorted([c.value for c in cards])
    suits = [c.suit for c in cards]
    value_counts = Counter(values)
    suits_counts = Counter(suits)
    is_flush = n == 5 and max(suits_counts.values()) == 5
    is_straight = n == 5 and all(values[i] - values[i-1] == 1 for i in range(1,5))
    if values == [2, 3, 4, 5, 14]:
        is_straight = True
        values = [1, 2, 3, 4, 5]
    contributing = []
    if is_flush and 5 in value_counts.values():
        contributing = cards[:]
        return "Flush Five", contributing
    elif is_flush and sorted(value_counts.values()) == [2, 3]:
        contributing = cards[:]
        return "Flush House", contributing
    elif 5 in value_counts.values():
        contributing = cards[:]
        return "Five of a Kind", contributing
    elif is_flush and is_straight and values[-1] == 14:
        contributing = cards[:]
        return "Royal Flush", contributing
    elif is_flush and is_straight:
        contributing = cards[:]
        return "Straight Flush", contributing
    elif 4 in value_counts.values():
        four_value = [val for val, count in value_counts.items() if count == 4][0]
        contributing = [c for c in cards if c.value == four_value]
        return "Four of a Kind", contributing
    elif sorted(value_counts.values()) == [2, 3]:
        contributing = cards[:]
        return "Full House", contributing
    elif is_flush:
        contributing = cards[:]
        return "Flush", contributing
    elif is_straight:
        contributing = cards[:]
        return "Straight", contributing
    elif 3 in value_counts.values():
        three_value = [val for val, count in value_counts.items() if count == 3][0]
        contributing = [c for c in cards if c.value == three_value]
        return "Three of a Kind", contributing
    elif list(value_counts.values()).count(2) == 2:
        pair_values = [val for val, count in value_counts.items() if count == 2]
        contributing = [c for c in cards if c.value in pair_values]
        return "Two Pair", contributing
    elif 2 in value_counts.values():
        pair_value = [val for val, count in value_counts.items() if count == 2][0]
        contributing = [c for c in cards if c.value == pair_value]
        return "Pair", contributing
    else:
        high_value = max(values)
        contributing = [c for c in cards if c.value == high_value]
        return "High Card", contributing

letter_animation = True
running = True

letter_classes()
animate_letters()


sorted_letters = sorted(Letters, key=lambda letter: letter.xpos)
    
startAnimation = True

for i, letter in enumerate(sorted_letters):
    letter.delay = i * 10  
    letter.animation = True
current_order = sorted(Letters, key=lambda letter: letter.xpos)
letter_string = ''.join([letter.letter for letter in current_order])

devkey = 'holyguac' + letter_string
startGame = False


init_video()

while startGame == False:
    cursor_pos = pygame.mouse.get_pos()
    hovering = False
    for toggle in guiToggleList:
        if toggle.should_draw and toggle.rect.collidepoint(cursor_pos):
            hovering = True
            break
    current_blind = get_current_blind()
    if current_blind and current_blind.rect.collidepoint(cursor_pos):
        hovering = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        
        if event.type == pygame.KEYDOWN:
            if event.unicode.lower() == devtoggle.lower() and DEV_MODE.toggle:
                dev_toggle = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    
                    card_animating = True
                elif settings:  
                    for setting in settingsList:
                        if setting.rect.collidepoint(event.pos):
                            setting.toggle = not setting.toggle
                            setting.check_dev()
                            setting.update_img()
                elif setting_rect.collidepoint(event.pos): 
                    settings = True
                if xbutton_rect.collidepoint(event.pos):
                    settings = False
    screen.fill((0, 0, 0))  
    spinningBG.animate()
    settingsButton.animate()

    if Atttention_helper.toggle and not prev_attention_state:
        init_video()
    elif not Atttention_helper.toggle and prev_attention_state:
        close_video()
    prev_attention_state = Atttention_helper.toggle
    

    if Atttention_helper.toggle:
        frame = get_video_frame()
        if frame:
            screen.blit(frame, (VIDEO_X, VIDEO_Y))
    
    if SO_SERIOUS.toggle:
        soserious.animate()
        if not soseriousmusic.get_num_channels(): 
            soseriousmusic.play(-1) 
    else:
        soseriousmusic.stop()
    if fade_alpha > 0:
        fade_alpha -= 2 
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((255, 255, 255))  
        fade_surface.set_alpha(fade_alpha) 
        screen.blit(fade_surface, (0, 0))

    pygame.draw.circle(screen, (255, 255, 255), (WIDTH//2, HEIGHT//2), WIDTH//37)
    for letter in Letters:
        letter.animate()
        letter.draw()
    screen.blit(STARTBUTTON, (STARTBUTTON_X, STARTBUTTON_Y))
    
    if settings:
        screen.fill((255,255,255))
        draw_settings()
        screen.blit(xbutton,((WIDTH - xbutton_rect.width),0))
        

        
    update_card_animation()
    if card_x > -WIDTH:  
        screen.blit(STARTCARD, (card_x, 0))
        
    if endBG == True:
        startGame = True

    dev_commands()
    blit_img()

    
        
    if hovering:
        screen.blit(cursor_hover, cursor_pos)
    else:
        screen.blit(cursor_normal, cursor_pos)   
    pygame.display.flip()
    clock.tick(60)
    currentFrame += 1
    

    
def sort_hand():
    global hand, sort_mode
    if sort_mode == "rank":
        hand.sort(key=lambda c: c.value, reverse=True)
    elif sort_mode == "suit":
        suit_order = {"Spades": 4, "Hearts": 3, "Diamonds": 2, "Clubs": 1}
        hand.sort(key=lambda c: (suit_order[c.suit], c.value), reverse = True)
    for scoring_sequence_index, c in enumerate(hand):
        c.slot = scoring_sequence_index

def get_hand_slot_from_x(x_pos, hand_len, spread=spacing, center_x=WIDTH/2):
    if hand_len <= 1:
        return 0
    total_width = (hand_len - 1) * spread + 80
    start_x = center_x - total_width / 2
    rel = x_pos - start_x
    idx = int(round(rel / spread))
    idx = max(0, min(hand_len - 1, idx))
    return idx


overlay = pygame.Surface((WIDTH, HEIGHT))
overlay.fill((0, 0, 0))  
overlay.set_alpha(128)


while running:
    global discard_queue
    global scoring_queue
    question.should_draw = True 
    mouse_pos = pygame.mouse.get_pos()
    
    cursor_pos = pygame.mouse.get_pos()
    
    hovering = False
    for toggle in guiToggleList:
        if toggle.should_draw and toggle.rect.collidepoint(cursor_pos):
            hovering = True
            break
    for card in hand:
        if card.rect.collidepoint(cursor_pos):
            hovering = True
            break
        
    update_gui_buttons()
    

    if Atttention_helper.toggle and not prev_attention_state:
        init_video()
    elif not Atttention_helper.toggle and prev_attention_state:
        close_video()
    prev_attention_state = Atttention_helper.toggle
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.unicode.lower() == devtoggle.lower() and DEV_MODE.toggle:
                dev_toggle = True
       
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = mouse_pos
                if current_blind and current_blind.rect.collidepoint(mouse_pos):
                    current_blind.dragging = True
                    current_blind.drag_offset_x = current_blind.x - mouse_x
                    current_blind.drag_offset_y = current_blind.y - mouse_y
                    current_blind.drag_start = (mouse_x, mouse_y)
                    current_blind.was_dragged = False

                if help_menu and xbutton_rect.collidepoint(event.pos):
                    help_menu = False
                    helpButton.toggle = False

                if settings:  
                    for setting in settingsList:
                        if setting.rect.collidepoint(event.pos):
                            setting.toggle = not setting.toggle
                            setting.check_dev()
                            setting.update_img()
                    
                
                if xbutton_rect.collidepoint(event.pos):
                    settings = False
                    settings2.toggle = False

                    ###Gui toggles###
                if settings == False:
                    for toggle in guiToggleList:
                        if toggle.should_draw and toggle.rect.collidepoint(mouse_pos):
                            toggle.toggle = not question.toggle
                            if toggle == settings2:
                                settings = True
                            if toggle == githubButton:
                                webbrowser.open("https://github.com/eepy-sleepy1234/Barratlo/tree/main")
                                toggle.toggle = False
                            if toggle == helpButton:
                                help_menu = True
                    
                if SO_SERIOUS.toggle and soserious.rect.collidepoint(mouse_pos):
                    soserious.dragging = True
                    soserious.drag_offset_x = soserious.xpos - mouse_x
                    soserious.drag_offset_y = soserious.ypos - mouse_y
                    soserious.drag_start = (mouse_x, mouse_y)
                    soserious.was_dragged = False
                else:
                    selected_count = sum(1 for card in hand if card.state == "selected")
                if not scoring_in_progress:
                    for card in reversed(hand):
                        if card.rect.collidepoint(mouse_pos):
                            card.dragging = True
                            card.drag_offset_x = card.x - mouse_x
                            card.drag_offset_y = card.y - mouse_y
                            card.drag_start = (mouse_x, mouse_y)
                            card.was_dragged = False
                            break
                if Playhand_rect.collidepoint(mouse_pos):
                    if hands > 0 and not scoring_in_progress:
                        selected_cards = [card for card in hand if card.state == "selected"]
                        if len(selected_cards) > 0:
                            hand_type, contributing = detect_hand(selected_cards)
                            saved_base_chips = (Hand_Chips.get(hand_type, 0) * Hand_levels.get(hand_type, 1))
                            saved_base_mult = Hand_Mult.get(hand_type, 1)
                            saved_level = Hand_levels.get(hand_type, 1)
                            saved_hand = hand_type
                            dev_selection = False
                            scoring_queue = contributing.copy()
                            for card in selected_cards:
                                card.state = "played"
                                card.play_timer = 0
                                card.scaling_delay = 0
                                card.is_contributing = card in contributing
                                card.scaling_done = False
                                card.scoring_animating = False
                                card.scoring_complete = False
                                card.scaling = False
                            for card in contributing:
                                card.is_contributing = True
                            hands -= 1
                            total_scoring_count = 0
                            if contributing:
                                scoring_in_progress = True
                                if scoring_queue:
                                    scoring_queue[0].scaling = True
                            scoring_sequence_index = 0
                            
                if Discardhand_rect.collidepoint(mouse_pos):
                    if discards > 0 and not scoring_in_progress:
                        dev_selection = False
                        lerp_factor = 0.3
                        discard_timer = 0
                        to_discard = [card for card in hand if card.state == "selected"]
                        discard_queue = to_discard
                        discarding = True
                        discards -= 1
                if SortbuttonRank_rect.collidepoint(mouse_pos):
                    sort_mode = "rank"
                    sort_hand()
                if SortbuttonSuit_rect.collidepoint(mouse_pos):
                    sort_mode = "suit"
                    sort_hand()
            if event.button == 3:
                if not scoring_in_progress:
                    for card in hand:
                        card.state = "hand"
        if event.type == pygame.MOUSEBUTTONUP:
            if soserious.dragging:
                soserious.dragging = False
            if event.button == 1:
                current_blind = get_current_blind()
                if current_blind and current_blind.dragging:
                    current_blind.dragging = False
                    current_blind.target_x = BLIND_X
                    current_blind.target_y = BLIND_Y
                    current_blind.vx = 0
                    current_blind.vy = 0
                mouse_pos = event.pos
                for card in hand:
                    if getattr(card, "dragging", False) and not scoring_in_progress:
                        card.dragging = False
                        if not card.was_dragged and card.rect.collidepoint(mouse_pos):
                            if card.state == "hand":
                                if sum(1 for c in hand if c.state == "selected") < 5:
                                    card.state = "selected"
                            else:
                                card.state = "hand"
                        n = len(hand)
                        spread_local = spacing
                        total_width = (n - 1) * spread_local + 80
                        start_x = (WIDTH / 2) - total_width / 2
                        i = card.slot
                        center_y = HEIGHT - 100
                        max_v_offset = -30
                        t = i / (n - 1) if n > 1 else 0.5
                        slot_target_x = start_x + i * spread_local
                        slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset
                        if not card.state == "played":
                            card.target_x = slot_target_x
                            card.target_y = slot_target_y
                        card.vx = 0
                        card.vy = 0
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            current_blind = get_current_blind()
            if current_blind and current_blind.dragging:
                dx = mouse_x - current_blind.drag_start[0]
                dy = mouse_y - current_blind.drag_start[1]
                if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                    current_blind.was_dragged = True
                    current_blind.x = mouse_x + current_blind.drag_offset_x
                    current_blind.y = mouse_y + current_blind.drag_offset_y
                    current_blind.target_x = current_blind.x
                    current_blind.target_y = current_blind.y
            if SO_SERIOUS.toggle and soserious.dragging:
                soserious.xpos = mouse_x + soserious.drag_offset_x
                soserious.ypos = mouse_y + soserious.drag_offset_y
            if not scoring_in_progress:
                for card in hand:
                    if getattr(card, "dragging", False) and not card.state == "played":
                        dx = mouse_x - card.drag_start[0]
                        dy = mouse_y - card.drag_start[1]
                        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                            card.was_dragged = True
                            card.x = mouse_x + card.drag_offset_x
                            card.y = mouse_y + card.drag_offset_y
                            card.target_x = card.x
                            card.target_y = card.y
                            n = len(hand)
                            new_index = get_hand_slot_from_x(card.x, n, spread=spacing, center_x=WIDTH/2)
                            current_index = hand.index(card)
                            if new_index != current_index:
                                hand.pop(current_index)
                                hand.insert(new_index, card)
                                for idx, c in enumerate(hand):
                                    c.slot = idx
    screen.fill(green)
    screen.blit(SideBar_img, (0, 0))
    

    if Atttention_helper.toggle:
        frame = get_video_frame()
        if VideoVelocityX == 0:
            VideoVelocityX = random.randint(0, 10)
        if VideoVelocityY == 0:
            VideoVelocityY = random.randint(0, 10)
        if VIDEO_X >= WIDTH - VIDEO_WIDTH or VIDEO_X <= 0:
            VideoVelocityX *= -1
        if VIDEO_Y >= HEIGHT - VIDEO_HEIGHT or VIDEO_Y <= 0:
            VideoVelocityY *= -1
        VIDEO_X += VideoVelocityX
        VIDEO_Y += VideoVelocityY
        if frame:
            screen.blit(frame, (VIDEO_X, VIDEO_Y))
    if not calculating:
        selected_cards = [card for card in hand if card.state in ("selected", "played", "scoring")]
        if len(selected_cards) > 0:
            hand_type, contributing = detect_hand(selected_cards)
        else:
            hand_type, contributing = None, None
        if hand_type:
            level = Hand_levels.get(hand_type, 1)
            base_chips = Hand_Chips.get(hand_type, 0)
            base_mult = Hand_Mult.get(hand_type, 1)
        else:
            level = 0
            base_chips = 0
            base_mult = 0
        chips = base_chips * level
        mult = base_mult * level
        final_score = saved_base_chips * saved_base_mult
    screen.blit(HandBackground_img, (20, HEIGHT / 2.75))
    screen.blit(ScoreBackground_img, (20, HEIGHT / 3.75))
    screen.blit(GoalBackground_img, (110, HEIGHT / 7.2))
    screen.blit(MoneyBackground_img, (100, HEIGHT / 1.7))
    screen.blit(RoundBackground_img, (100, HEIGHT / 1.5))
    font = pygame.font.SysFont(None, 40)
    if not calculating:
        if scoring_in_progress:
            text = PixelFontS.render(saved_hand, True, white)
        else:
            text = PixelFontS.render(hand_type, True, white)
    else:
        current_score_text = change_notation(current_score)
        text = PixelFontS.render(f"{current_score_text}", True, white)
    text_rect = text.get_rect(center=(140, 20 + HEIGHT / 2.67))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"{hands}", True, white)
    text_rect = text.get_rect(center=(70, HEIGHT / 1.79))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"{discards}", True, white)
    text_rect = text.get_rect(center=(205, HEIGHT / 1.79))
    screen.blit(text, text_rect)
    if scoring_in_progress or calculating:
        saved_base_chips_text = change_notation(saved_base_chips)
        text = PixelFontS.render(f"{saved_base_chips_text}", True, white)
    else:
        chips_text = change_notation(chips)
        text = PixelFontS.render(f"{chips_text}", True, white)
    text_rect = text.get_rect(center=(80, HEIGHT / 2.2))
    screen.blit(text, text_rect)
    if scoring_in_progress or calculating:
        saved_base_mult_text = change_notation(saved_base_mult)
        text = PixelFontS.render(f"{saved_base_mult_text}", True, white)
    else:
        mult_text = change_notation(mult)
        text = PixelFontS.render(f"{mult_text}", True, white)
    text_rect = text.get_rect(center=(200, HEIGHT / 2.2))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"{len(hand)} / {handsize}", True, white)
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT / 1.05))
    screen.blit(text, text_rect)
    total_score_text = change_notation(total_score)
    text = PixelFontS.render(f"{total_score_text}", True, white)
    text_rect = text.get_rect(center=(180, HEIGHT / 3.17))
    screen.blit(text, text_rect)
    target_score_text = change_notation(target_score)
    text = PixelFontS.render(f"{target_score_text}", True, red)
    text_rect = text.get_rect(center=(190, HEIGHT / 5))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"{round_num}", True, orange)
    text_rect = text.get_rect(center=(227, HEIGHT / 1.415))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"{ante}", True, orange)
    text_rect = text.get_rect(center=(127, HEIGHT / 1.419))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"${money}", True, yellow)
    text_rect = text.get_rect(center=(180, HEIGHT / 1.595))
    screen.blit(text, text_rect)
    text = PixelFontXS.render(f"{'$' * blind_reward}", True, yellow)
    text_rect = text.get_rect(center=(220, HEIGHT / 4.35))
    screen.blit(text, text_rect)
    text = PixelFontS.render(f"{current_blind.name}", True, white)
    text_rect = text.get_rect(center=(190, HEIGHT / 12))
    screen.blit(text, text_rect)

    screen.blit(Playhand_img, (int(0 + playhandw/4), HEIGHT - int(playhandh *2 )))
    screen.blit(Discardhand_img, (int(WIDTH - (playhandw + playhandw/4)), HEIGHT - int(playhandh *2 )))
    screen.blit(SortbuttonSuit_img,(int(WIDTH/2 - (sortrankw +sortrankw/2)), int(HEIGHT - int(sortrankh +sortrankh/10))))
    screen.blit(SortbuttonRank_img,(int (WIDTH/2 + (sortrankw/2)), int(HEIGHT - int(sortrankh + sortrankh/10))))

    boss_debuff()
    draw_hand(screen, hand, WIDTH / 2, HEIGHT - 100, spread=spacing, max_vertical_offset=-30, angle_range=8)

    update_card_animation()

    if SO_SERIOUS.toggle:
        soserious.animate()
        if not soseriousmusic.get_num_channels(): 
            soseriousmusic.play(-1) 
    else:
        soseriousmusic.stop()

    for toggle in guiToggleList:
        toggle.update_img(mouse_pos)

    for toggle in guiToggleList:
        toggle.draw()
    
    dev_commands()
    blit_img()
    if card_x > -WIDTH:
        screen.blit(STARTCARD, (card_x, 0))

    
    if question.toggle:
            screen.blit(overlay, (0, 0))
            update_gui_buttons()
            for button in guibutton:
                button.draw()
    if settings2.toggle:
        settings = True

    if current_blind:
        current_blind.update()
        current_blind.draw(screen)

    if settings:
        screen.fill((255,255,255))
        draw_settings()
        screen.blit(xbutton,((WIDTH - xbutton_rect.width),0))

    chip_indicators = [indicator for indicator in chip_indicators if indicator.update()]
    for indicator in chip_indicators:
        indicator.draw(screen)



    if hovering:
        screen.blit(cursor_hover, cursor_pos)
    else:
        screen.blit(cursor_normal, cursor_pos)
    if help_menu:
        screen.fill((255, 255, 255))
    
        y_offset = 20
        
        for surface in helpMenu_surfaces:
            if surface:
                screen.blit(surface, (20, y_offset))
            y_offset += line_height + 5

        screen.blit(xbutton, (WIDTH - xbutton_rect.width, 0))
    


    
    pygame.display.flip()   ###########################################################
    clock.tick(60)
    currentFrame += 1

    for card in hand:
        card.update()
        if card.state == "discarded":
            if not calculating and not scoring_in_progress and card.x > WIDTH + 200:
                index = card.slot
                hand.remove(card)
                for c in hand:
                    if c.slot > index:
                        c.slot -= 1
                if deck:
                    new_card = deck.pop()
                    new_card.slot = index
                    new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
                    hand.append(new_card)
                    sort_hand()
    if deck and len(hand) < handsize and not dev_selection:
        index = card.slot
        new_card = deck.pop()
        new_card.slot = index
        new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
        hand.append(new_card)
        sort_hand()
    if scoring_in_progress:
        if scoring_in_progress:
            if len(scoring_queue) == 0:
                for c in hand:
                    if c.state in ("played", "scored"):
                        c.state = "scored"
                        c.target_x = c.x
                        c.target_y = c.y
                        c.vx = 0
                        c.vy = 0
                scoring_in_progress = False
                scored = True

    if scoring_in_progress and scoring_queue:
        current_card = scoring_queue[0]
        if current_card.scoring_complete:
            scoring_queue.pop(0)
            if len(scoring_queue) > 0:
                scoring_queue[0].scaling = True

    if scored:
        calculating = True
        scored = False
        calc_progress = 0.0
        add_progress = 0.0
        saved_total_score = total_score
    if calculating:
        if calc_progress < 1.0:
            calc_progress += 1.0 / 100
            ease_progress = 1.0 - (1.0 - calc_progress) ** 2
            current_score = round(final_score * ease_progress)
            saved_base_chips = round((saved_base_chips * saved_level) * (1.0 - ease_progress))
            saved_base_mult = round((saved_base_mult * saved_level) * (1.0 - ease_progress))
            if calc_progress >= 1.0:
                calc_progress = 1.0
                current_score = final_score
                chips = 0
                mult = 0
        if add_progress < 1.0 and calc_progress >= 1.0:
            add_progress += 1.0 / 100
            ease_progress = 1.0 - (1.0 - add_progress) ** 2
            current_score = round(final_score * (1.0 - ease_progress))
            total_score = saved_total_score + round(final_score * (ease_progress))
            if add_progress >= 1.0:
                add_progress = 1.0
                total_score = saved_total_score + final_score
                calculating = False
                discard_queue = []
                discard_timer = 0
                for c in hand:
                    if c.state == "scored":
                        c.scoring_x, c.scoring_y = 0, 0
                        c.scoring_complete = False
                        c.is_contributing = False
                        discard_queue.append(c)
                discarding = True
                victory = check_blind_defeated()
                if victory:
                    advance_to_next_blind()
                    get_current_blind()

    if discarding:
        if discard_queue:
            if discard_timer >= 2:
                discard_queue[0].state = "discarded"
                discard_queue.pop(0)
                discard_timer = 0
            else:
                discard_timer += 1
        else:
            discarding = False
            

close_video()
pygame.quit()
