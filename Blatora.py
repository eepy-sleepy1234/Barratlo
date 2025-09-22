import os
import pygame
import random
import math
from collections import Counter

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

green = (0, 120, 0)
white = (255, 255, 255)

clock = pygame.time.Clock()
pygame.init()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
SUITS_DIR = os.path.join(ASSETS_DIR, "Suits")
JOKERS_DIR = os.path.join(ASSETS_DIR, "Jokers")
GUI_DIR = os.path.join(ASSETS_DIR, "GUI")

Playhand_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "PlayHandButton.png")), (120, 50))
Playhand_rect = pygame.Rect(25, HEIGHT - 130, 120, 50)
Discardhand_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "DiscardHandButton.png")), (120, 50))
Discardhand_rect = pygame.Rect(WIDTH - 170, HEIGHT - 130, 120, 50)
HandBackground_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(GUI_DIR, "Handbackground.png")), (240, 150))

deck = []
handsize = 8
chips = 0
mult = 0
hands = 4
discards = 4

SCORED_POSITIONS = [
    (WIDTH//2 - 200, HEIGHT//2 - 50),
    (WIDTH//2 - 100, HEIGHT//2 - 50),
    (WIDTH//2,     HEIGHT//2 - 50),
    (WIDTH//2 + 100, HEIGHT//2 - 50),
    (WIDTH//2 + 200, HEIGHT//2 - 50)
]

SUITS = ["hearts", "diamonds", "clubs", "spades"]
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
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]
        self.name = f"{rank} of {suit}"
        self.rect = image.get_rect()
        self.state = "hand"
        self.slot = slot
        self.x = 0
        self.target_x = 0
        self.y = 0
        self.angle = 0
        self.target_y = 0
        self.play_timer = 0
    def update(self, lerp_factor=0.2):
        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor

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
    if not cards:
        return
    start_angle = -angle_range / 2
    angle_step = angle_range / (n - 1) if n > 1 else 0
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2
    for card in cards:
        i = card.slot
        t = i / (n - 1) if n > 1 else 0.5

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
                abs_x, abs_y = SCORED_POSITIONS[index]
                target_x, target_y = card.x + (abs_x - card.x), card.y + (abs_y - card.y)
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
        rotated = pygame.transform.rotate(card.image, angle)
        rect = rotated.get_rect(center=(card.x, card.y))
        surface.blit(rotated, rect.topleft)
        card.rect = rect

class Joker_Animation():
    def __init__(self,sprite_name, frame_width, frame_height, fps, frames, xpos, ypos,setWidth, setHeight):
        
        self.sprite_sheet = sprite_sheet
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

def detect_hand(cards):
    n = len(cards)
    values = sorted([c.value for c in cards])
    suits = [c.suit for c in cards]
    value_counts = Counter(values)
    suits_counts = Counter(suits)
    is_flush = n == 5 and max(suits_counts.values()) == 5
    is_straight = n == 5 and all(values[i] - values[i-1] == 1 for i in range(1,5))
    if values == [2, 3, 4, 5, 14]:
        is_straight = True
        values = [1, 2, 3, 4, 5]
    if is_flush and is_straight and values[-1] == 14:
        return "Royal Flush"
    elif is_flush and is_straight:
        return "Straight Flush"
    elif 4 in value_counts.values():
        return "Four of a Kind"
    elif sorted(value_counts.values()) == [2, 3]:
        return "Full House"
    elif is_flush:
        return "Flush"
    elif is_straight:
        return "Straight"
    elif 3 in value_counts.values():
        return "Three of a Kind"
    elif list(value_counts.values()).count(2) == 2:
        return "Two Pair"
    elif 2 in value_counts.values():
        return "Pair"
    else:
        return "High Card"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                selected_count = sum(1 for card in hand if card.state == "selected")
                for card in reversed(hand):
                    if card.state in ("selected", "hand") and card.rect.collidepoint(mouse_pos):
                        if card.state == "selected":
                            card.state = "hand"
                            break
                        elif selected_count < 5:
                            card.state = "selected"
                            selected_count += 1
                            break
                if Playhand_rect.collidepoint(mouse_pos):
                    if hands > 0:
                        card.lerp_factor = 0.3
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
            if event.button == 3:
                for card in hand:
                    card.state = "hand"
    screen.fill(green)
    selected_cards = [card for card in hand if card.state == "selected"]
    hand_type = detect_hand(selected_cards)
    font = pygame.font.SysFont(None, 40)
    text = font.render(hand_type, True, white)
    text_rect = text.get_rect(center=(149, 25 + HEIGHT / 3))

    screen.blit(Playhand_img, (25, HEIGHT - 130))
    screen.blit(Discardhand_img, (WIDTH - 195, HEIGHT - 130))
    screen.blit(HandBackground_img, (25, HEIGHT / 3))
    screen.blit(text, text_rect)

    draw_hand(screen, hand, WIDTH / 2, HEIGHT - 100, spread=spacing, max_vertical_offset=-30, angle_range=8)
    
    pygame.display.flip()

    clock.tick(60)
    currentFrame += 1
    for card in hand:
        card.update(lerp_factor=0.1)
        if card.state == "played":
            card.play_timer += 1
            if card.play_timer > 120:
                card.state = "scored"
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

pygame.quit()
