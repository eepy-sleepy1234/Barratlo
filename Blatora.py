import os
import pygame
import random
import math
from collections import Counter
import sys
import subprocess

try:
    import cv2
except ImportError:
    import subprocess
    import sys
    print("opencv-python not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
    import cv2
    

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

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

green = (0, 120, 0)
white = (255, 255, 255)

clock = pygame.time.Clock()
pygame.init()
pygame.mixer.init()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
SUITS_DIR = os.path.join(ASSETS_DIR, "Suits")
JOKERS_DIR = os.path.join(ASSETS_DIR, "Jokers")
GUI_DIR = os.path.join(ASSETS_DIR, "GUI")
LETTERS_DIR = os.path.join(GUI_DIR, "Letters")
SPRITESHEETS_DIR = os.path.join(ASSETS_DIR, "SpriteSheets")
FONTS_DIR = os.path.join(ASSETS_DIR, "Fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "Sounds")

\
VIDEO_PATH = os.path.join(ASSETS_DIR, "Soobway.mp4")
video_cap = None
video_surface = None
VIDEO_WIDTH = 200
VIDEO_HEIGHT = 150
VIDEO_X = 10
VIDEO_Y = 10

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

Question_mark = pygame.image.load(os.path.join(GUI_DIR, 'QuestionMark.png')).convert_alpha()
Question_mark = pygame.transform.scale(Question_mark, (WIDTH/20, WIDTH/12))
soseriousmusic = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "WHYSOSERIOUS.mp3"))
Playhand_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "PlayHandButton.png")), (120, 50))
Playhand_rect = pygame.Rect(25, HEIGHT - 130, 120, 50)
Discardhand_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "DiscardHandButton.png")), (120, 50))
Discardhand_rect = pygame.Rect(WIDTH - 170, HEIGHT - 130, 120, 50)
SortbuttonRank_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "SortbuttonRank.png")), (120, 50))
SortbuttonRank_rect = pygame.Rect(WIDTH / 2 - 175, HEIGHT - 60, 120, 50)
SortbuttonSuit_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "SortbuttonSuit.png")), (120, 50))
SortbuttonSuit_rect = pygame.Rect(WIDTH / 2 - 25, HEIGHT - 60, 120, 50)
HandBackground_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "Handbackground.png")), (240, 150))
SideBar_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "SideBar.png")), (280, 600))
STARTCARD = pygame.image.load(os.path.join(GUI_DIR, 'StartCard.png')).convert_alpha()
STARTCARD = pygame.transform.smoothscale(STARTCARD,(WIDTH,HEIGHT))
SPINNINGBGIMG = pygame.image.load(os.path.join(SPRITESHEETS_DIR, 'StartBackground.png')).convert_alpha()
SOSERIOUS = pygame.image.load(os.path.join(SPRITESHEETS_DIR, 'SoSerious.png')).convert_alpha()
STARTBUTTON = pygame.image.load(os.path.join(GUI_DIR, 'StartButton.png')).convert_alpha()
STARTBUTTON = pygame.transform.smoothscale(STARTBUTTON,(int(WIDTH/4.4),int(HEIGHT/10)))
STARTBUTTON_X = int((WIDTH/2)- ((WIDTH/4.4)/2))
STARTBUTTON_Y = (HEIGHT/2)+CENTERLETTERH/2
start_button_rect = STARTBUTTON.get_rect()
start_button_rect.topleft = (STARTBUTTON_X, STARTBUTTON_Y)
SETTINGSIMG = pygame.image.load(os.path.join(SPRITESHEETS_DIR, 'SettingsButton.png')).convert_alpha()
SETTINGONIMG = pygame.image.load(os.path.join(GUI_DIR, 'Setting_on.png')).convert_alpha()
SETTINGOFFIMG = pygame.image.load(os.path.join(GUI_DIR, 'Setting_off.png')).convert_alpha()
SETTINGONIMG = pygame.transform.scale(SETTINGONIMG,(int(HEIGHT/5),int(HEIGHT/10)))
SETTINGOFFIMG = pygame.transform.scale(SETTINGOFFIMG, (int(HEIGHT/5),int(HEIGHT/10)))
SETTINGSRECT = SETTINGONIMG.get_rect()
xbutton = pygame.image.load(os.path.join(GUI_DIR, 'XButton.png')).convert_alpha()
xbutton = pygame.transform.scale(xbutton,(int(HEIGHT/10), int(HEIGHT/10)))
xbutton_rect = xbutton.get_rect()
xbutton_rect.topleft = ((WIDTH - xbutton_rect.width), 0)
for root, dirs, files in os.walk(LETTERS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            letter_name = os.path.splitext(filename)[0]
            image = pygame.transform.scale(pygame.image.load(filepath).convert_alpha(), (int(LETTERW), int(LETTERH)))
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
PixelFont = pygame.font.Font((os.path.join(FONTS_DIR, 'Pixel Game.otf')), int(HEIGHT/10))
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

            


guiToggleList = []
class GUITOGGLES():
    def __init__(self, x, y, sprite, scale_factor=1.1):
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
    
    def draw(self):
        if self.should_draw:
            # Center the sprite at x, y
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
                                                    
                    
question = GUITOGGLES( WIDTH - (WIDTH/20),0 + WIDTH/20, Question_mark, scale_factor = 1.15)
 
        

        

        
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
                

                hand.clear()
                

                temp_deck = []
                for root, dirs, files in os.walk(SUITS_DIR):
                    for filename in files:
                        if filename.endswith(".png"):
                            filepath = os.path.join(root, filename)
                            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
                            name, _ = os.path.splitext(filename)
                            rank, suit = name.split("Of")
                            card = Card(rank, suit, image)
                            temp_deck.append(card)
                
                card_count = 0
                while card_count < 8:
                    rank_input = input(f"Card {card_count + 1} - Rank (or 'done'): ").strip()
                    
                    if rank_input.lower() == 'done':
                        break
                        
                    suit_input = input(f"Card {card_count + 1} - Suit: ").strip()
                    
                    # Find matching card
                    found = False
                    for card in temp_deck:
                        if card.rank == rank_input and card.suit == suit_input:
                            card.slot = card_count
                            card.x, card.y = WIDTH + 100, HEIGHT - 170
                            card.state = "hand"
                            hand.append(card)
                            card_count += 1
                            found = True
                            print(f"Added {card.rank} of {card.suit}")
                            break
                    
                    if not found:
                        print(f"Card '{rank_input}' of '{suit_input}' not found. Check spelling.")
                        print(f"Example: 'Three' and 'Diamonds' (capital first letter)")
                
                sort_hand()
                print(f"Hand set with {len(hand)} cards")
                dev_toggle = False
                return

            elif dev_command.lower() == 'resetdeck':
            
                hand.clear()
                

                deck.clear()
                for root, dirs, files in os.walk(SUITS_DIR):
                    for filename in files:
                        if filename.endswith(".png"):
                            filepath = os.path.join(root, filename)
                            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
                            name, _ = os.path.splitext(filename)
                            rank, suit = name.split("Of")
                            card = Card(rank, suit, image)
                            deck.append(card)
                
   
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

deck = []
handsize = 8
chips = 0
mult = 0
current_score = 0
round_score = 0
scored_counter = 0
hands = 4
discards = 4
DRAG_THRESHOLD = 10
sort_mode = "rank"
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
    }
playing = False
scored = False

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


class Card:
    def __init__(self, rank, suit, image, slot=None):
        self.image = image
        self.scale= 1.0
        self.rotation_speed = 0
        self.scaling_delay = 0
        self.scaling = False
        self.growing = False
        self.scaling_done = False
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]
        if self.value in ("11", "12", "13"):
            self.chip_value = 10
        elif self.value == "14":
            self.chip_value = 11
        else:
            self.chip_value = self.value
        self.name = f"{rank} of {suit}"
        self.rect = image.get_rect()
        self.state = "hand"
        self.slot = slot
        self.vx = 0
        self.vy = 0
        self.x = 0
        self.target_x = 0
        self.y = 0
        self.angle = 0
        self.target_y = 0
        self.play_timer = 0
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
    def update(self):
        scored_counter = 0
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
        if abs(dx) > 0.5 and abs(dy) < 0:
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            tilt_strength = 0.75
            self.angle = angle_deg * tilt_strength
        else:
            self.angle *= 0.75
        if self.scaling:
            if self.scaling_delay > 0:
                self.scaling_delay -= 1
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
                        self.scaling_delay = 10
                        scored_counter += 1
        self.angle += self.rotation_speed

for root, dirs, files in os.walk(SUITS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
            name, _ = os.path.splitext(filename)
            rank, suit = name.split("Of")
            card = Card(rank, suit, image)
            deck.append(card)

random.shuffle(deck)

hand = []
for i in range(handsize):
    card = deck.pop()
    card.slot = i
    card.x, card.y = WIDTH + 100, HEIGHT - 170
    hand.append(card)

currentFrame = 0
spacing = 600 / handsize

def draw_hand(surface, cards, center_x, center_y, spread=20, max_vertical_offset=-30, angle_range=8):
    n = len(cards)
    scored_counter = 0
    if not cards:
        return
    start_angle = -angle_range / 2
    angle_step = angle_range / (n - 1) if n > 1 else 0
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2
    for card in cards:
        i = card.slot
        t = i / (n - 1) if n > 1 else 0.5
    for card in hand:
        card.is_contributing = card in contributing

    for i, card in enumerate(cards):
        t = i / (n - 1) if n > 1 else 0.5
        target_x = start_x + i * spread
        target_y = center_y - max_vertical_offset * 2 * (t - 0.5)**2 + max_vertical_offset
        if card.state == "selected":
            target_y -= 40
        elif card.state == "played":
            scored_cards = [c for c in hand if c.state == "scored"]
            index = len(scored_cards)
            if index < len(SCORED_POSITIONS):
                for c in scored_cards:
                    abs_x, abs_y = SCORED_POSITIONS[scored_counter]
                    target_x, target_y = card.x + (abs_x - card.x), card.y + (abs_y - card.y)
                    if c in contributing:
                        for contrib_pos, c in enumerate(contributing):
                            if contrib_pos == scored_counter and not card.scaling and not card.scaling_done:
                                c.scaling_delay = 0
                                c.scaling = True
                                target_y -= 25
                                c.rotation_speed = 0
                            elif contrib_pos == scored_counter and card.scaling_done:
                                scored_counter += 1
                                card.state = "scored"
                                card.scaling_done = False
                    else:
                        scored_counter += 1
        elif card.state == "discarded":
            target_y -= 100
            target_x += WIDTH + 200
            card.angle -= 15
        elif card.state == "scored":
            target_y -= 500
            target_x += WIDTH + 200
            card.angle -= 5
        card.target_x = target_x
        card.target_y = target_y
        if card.state == "hand":
            card.angle = (t - 0.5) * -2 * angle_range
        angle = card.angle
        scaled_w = int(card.image.get_width() * card.scale)
        scaled_h = int(card.image.get_height() * card.scale)
        scaled_img = pygame.transform.smoothscale(card.image, (scaled_w, scaled_h))
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

spinningBG = Joker_Animation(SPINNINGBGIMG, 1980, 1080, 24, 71, 0, 0, WIDTH, HEIGHT)
settingsButton = Joker_Animation(SETTINGSIMG, 333, 333, 23, 50, WIDTH - WIDTH/6,HEIGHT - WIDTH/6, WIDTH/6, WIDTH/6)
soserious = Joker_Animation(SOSERIOUS, 250, 250, 24, 39,0,0, WIDTH/5, WIDTH/5)
setting_rect = pygame.Rect(WIDTH-WIDTH/6 , HEIGHT - WIDTH/6, WIDTH/6, WIDTH/6)


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
    if is_flush and is_straight and values[-1] == 14:
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
        pair_values = [val for val, count in value_counts.items() if count == 2][0]
        contributing = [c for c in cards if c.value == pair_values]
        return "Two Pair", contributing
    elif 2 in value_counts.values():
        pair_value = [val for val, count in value_counts.items() if count == 2]
        contributing = [c for c in cards if c.value in pair_value]
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
print (sorted_letters)

# Initialize video
init_video()

while startGame == False:
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

    # Handle attention helper video
    if Atttention_helper.toggle and not prev_attention_state:
        init_video()
    elif not Atttention_helper.toggle and prev_attention_state:
        close_video()
    prev_attention_state = Atttention_helper.toggle
    
    # Draw video if attention helper is on
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
    for idx, c in enumerate(hand):
        c.slot = idx

def get_hand_slot_from_x(x_pos, hand_len, spread=spacing, center_x=WIDTH/2):
    if hand_len <= 1:
        return 0
    total_width = (hand_len - 1) * spread + 80
    start_x = center_x - total_width / 2
    rel = x_pos - start_x
    idx = int(round(rel / spread))
    idx = max(0, min(hand_len - 1, idx))
    return idx

while running:
    question.should_draw = True 
    mouse_pos = pygame.mouse.get_pos()
    
    # Handle attention helper video
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
                selected_count = sum(1 for card in hand if card.state == "selected")
                for card in reversed(hand):
                    if card.rect.collidepoint(mouse_pos):
                        card.dragging = True
                        card.drag_offset_x = card.x - mouse_x
                        card.drag_offset_y = card.y - mouse_y
                        card.drag_start = (mouse_x, mouse_y)
                        card.was_dragged = False
                        break
                if Playhand_rect.collidepoint(mouse_pos):
                    if hands > 0:
                        playing = True
                        PCC = 0
                        selected_cards = [card for card in hand if card.state == "selected"]
                        num_selected = len(selected_cards)
                        start_x = (WIDTH / 8) - (num_selected - 1) * 60 / 2
                        start_y = HEIGHT / 2
                        for card in hand:
                            if card.state == "selected":
                                card.state = "played"
                                card.target_x = 0
                                card.target_y = 0
                                card.angle = 0
                                PCC += 1
                        if len(selected_cards) > 0:
                            hands -= 1
                            
                if Discardhand_rect.collidepoint(mouse_pos):
                    if discards > 0:
                        lerp_factor = 0.3
                        to_discard = [card for card in hand if card.state == "selected"]
                        for card in to_discard:
                           card.state = "discarded"
                        if len(to_discard) > 0:
                            discards -= 1
                if SortbuttonRank_rect.collidepoint(mouse_pos):
                    sort_mode = "rank"
                    sort_hand()
                if SortbuttonSuit_rect.collidepoint(mouse_pos):
                    sort_mode = "suit"
                    sort_hand()
            if event.button == 3:
                for card in hand:
                    card.state = "hand"
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_pos = event.pos
                for card in hand:
                    if getattr(card, "dragging", False):
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
                        card.target_x = slot_target_x
                        card.target_y = slot_target_y
                        card.vx = 0
                        card.vy = 0
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
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
    
    # Draw video if attention helper is on
    if Atttention_helper.toggle:
        frame = get_video_frame()
        if frame:
            screen.blit(frame, (VIDEO_X, VIDEO_Y))
    
    selected_cards = [card for card in hand if card.state in ("selected", "played")]
    hand_type, contributing = detect_hand(selected_cards)
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
    current_score = chips * mult
    screen.blit(HandBackground_img, (20, HEIGHT / 3.5))
    font = pygame.font.SysFont(None, 40)
    if not scored:
        text = font.render(hand_type, True, white)
    else:
        text = font.render(f"{current_score}", True, white)
    text_rect = text.get_rect(center=(140, 20 + HEIGHT / 3))
    screen.blit(text, text_rect)
    text = font.render(f"{hands}", True, white)
    text_rect = text.get_rect(center=(70, HEIGHT / 1.79))
    screen.blit(text, text_rect)
    text = font.render(f"{discards}", True, white)
    text_rect = text.get_rect(center=(205, HEIGHT / 1.79))
    screen.blit(text, text_rect)
    text = font.render(f"{chips}", True, white)
    text_rect = text.get_rect(center=(80, HEIGHT / 2.45))
    screen.blit(text, text_rect)
    text = font.render(f"{mult}", True, white)
    text_rect = text.get_rect(center=(200, HEIGHT / 2.45))
    screen.blit(text, text_rect)

    screen.blit(Playhand_img, (25, HEIGHT - 130))
    screen.blit(Discardhand_img, (WIDTH - 195, HEIGHT - 130))
    screen.blit(SortbuttonRank_img, SortbuttonRank_rect)
    screen.blit(SortbuttonSuit_img, SortbuttonSuit_rect)

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
    pygame.display.flip()
    
    
    clock.tick(60)
    currentFrame += 1
    for card in hand:
        card.update()
        if card.state == "played":
            card.play_timer += 1
            if card.play_timer > 120:
                card.state = "scored"
                playing = False
                scored = False
            elif card.play_timer > 100:
                scored = True
        if card.state == "scored" or card.state == "discarded":
            if card.x > WIDTH + 200:
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

close_video()
pygame.quit()
