import os
import pygame
import random
import math
from collections import Counter
import sys

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

green = (0, 120, 0)
white = (255, 255, 255)

clock = pygame.time.Clock()
pygame.init()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
SUITS_DIR = os.path.join(ASSETS_DIR, "Suits")
JOKERS_DIR = os.path.join(ASSETS_DIR, "Jokers")
GUI_DIR = os.path.join(ASSETS_DIR, "GUI")
LETTERS_DIR = os.path.join(GUI_DIR, "Letters")
SPRITESHEETS_DIR = os.path.join(ASSETS_DIR, "SpriteSheets")

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
SPINNINGBGIMG = pygame.image.load(os.path.join(GUI_DIR, 'StartBackground.png')).convert_alpha()
STARTBUTTON = pygame.image.load(os.path.join(GUI_DIR, 'StartButton.png')).convert_alpha()
STARTBUTTON = pygame.transform.smoothscale(STARTBUTTON,(int(WIDTH/4.4),int(HEIGHT/10)))
STARTBUTTON_X = int((WIDTH/2)- ((WIDTH/4.4)/2))
STARTBUTTON_Y = (HEIGHT/2)+CENTERLETTERH/2
start_button_rect = STARTBUTTON.get_rect()
start_button_rect.topleft = (STARTBUTTON_X, STARTBUTTON_Y)
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
    def __init__(self,sprite_name, frame_width, frame_height, fps, frames, xpos, ypos,setWidth, setHeight):
        
        self.sprite_sheet = sprite_name
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        self.current_frame = 0
        self.xpos = xpos
        self.ypos = ypos
        self.frames = frames
        self.xpos = xpos
        self.ypos = ypos
        self.frame_interval = int(60//fps)
        self.setWidth = setWidth
        self.setHeight = setHeight
        
        
    
    def animate(self):
        
        
        if currentFrame % self.frame_interval == 0:
            self.current_frame = (self.current_frame + 1) % self.frames
            
        frame_x = self.current_frame * self.frame_width

        
        scaled_surface = pygame.transform.smoothscale(self.sprite_sheet.subsurface((frame_x, 0, self.frame_width, self.frame_height)), (self.setWidth, self.setHeight))
        screen.blit(scaled_surface, (self.xpos, self.ypos))
    def reset_animation(self):
        self.current_frame = 1
#sprite_name = Joker_Animation(sprite_sheet, 80, 110, 60, 10, 0, 0, 80, 110)
spinningBG = Joker_Animation(SPINNINGBGIMG, 1980, 1080, 24, 71, 0, 0, WIDTH, HEIGHT)

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
startGame = True
sorted_letters = sorted(Letters, key=lambda letter: letter.xpos)      
startAnimation = True
for i, letter in enumerate(sorted_letters):
    letter.delay = i * 10  
    letter.animation = True

startGame = False 

while startGame == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    
                    card_animating = True 
                    
    screen.fill((0, 0, 0))  
    spinningBG.animate()
    
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
    
  
    update_card_animation()
    if card_x > -WIDTH:  
        screen.blit(STARTCARD, (card_x, 0))
    if endBG == True:
        startGame = True 
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
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

pygame.quit()
