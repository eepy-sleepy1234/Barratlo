import os
import pygame
import random
import math

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

green = (0, 120, 0)

clock = pygame.time.Clock()
pygame.init()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
SUITS_DIR = os.path.join(ASSETS_DIR, "Suits")
JOKERS_DIR = os.path.join(ASSETS_DIR, "Jokers")
GUI_DIR = os.path.join(ASSETS_DIR, "GUI")

Playhand_img = pygame.image.load(os.path.join(ASSETS_DIR, "PlayHandButton.png"))
Playhand_rect = pygame.Rect(50, HEIGHT - 130, 120, 50)
Discardhand_img = pygame.image.load(os.path.join(ASSETS_DIR, "DiscardHandButton.png"))
Discardhand_rect = pygame.Rect(WIDTH - 170, HEIGHT - 130, 120, 50)

deck = []
handsize = 8

class Card:
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()
        self.selected = False
        self.played = False
        self.x = 0
        self.target_x = 0
        self.y = 0
        self.target_y = 0
    def update(self, lerp_factor=0.2):
        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor

for root, dirs, files in os.walk(SUITS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
            deck.append(image)

random.shuffle(deck)

hand = [Card(deck.pop()) for _ in range(handsize)]
for card in hand:
    card.x, card.y = WIDTH + 100, HEIGHT - 170

currentFrame = 0
spacing = 600 / handsize

def draw_hand(surface, cards, center_x, center_y, spread=20, max_vertical_offset=-30, angle_range=8):
    n = len(cards)
    if n == 0:
        return
    start_angle = -angle_range / 2
    angle_step = angle_range / (n - 1) if n > 1 else 0
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2

    for i, card in enumerate(cards):
        t = i / (n - 1) if n > 1 else 0.5
        target_x = start_x + i * spread
        target_y = center_y - max_vertical_offset * 2 * (t - 0.5)**2 + max_vertical_offset
        if card.selected:
            target_y -= 40
        card.target_x = target_x
        card.target_y = target_y
        angle = (t - 0.5) * -2 * angle_range
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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                selected_count = sum(1 for card in hand if card.selected)
                for card in hand:
                    if card.rect.collidepoint(mouse_pos):
                        if card.selected:
                            card.selected = False
                        elif selected_count < 5:
                            card.selected = True
                            selected_count += 1
                if Playhand_rect.collidepoint(mouse_pos):
                    card.lerp_factor = 0.3
                    PCC = 0
                    selected_cards = [card for card in hand if card.selected]
                    num_selected = len(selected_cards)
                    start_x = (WIDTH / 8) - (num_selected - 1) * 60 / 2
                    start_y = HEIGHT / 2
                    for card in hand:
                        if card.selected:
                            card.selected = False
                            card.played = True
                            card.target_x = -start_x - PCC * 60
                            card.target_y = start_y + PCC * 15
                            card.angle = 0
                            PCC += 1
                            
                if Discardhand_rect.collidepoint(mouse_pos):
                    lerp_factor = 0.3
                    for card in hand:
                        if card.selected:
                            card.selected = False
                            card.played = True
                            card.target_x = WIDTH + 100
                            card.angle = 0
            if event.button == 3:
                for card in hand:
                    card.selected = False
    screen.fill(green)

    screen.blit(Playhand_img, (50, HEIGHT - 130))
    screen.blit(Discardhand_img, (WIDTH - 170, HEIGHT - 130))

    draw_hand(screen, hand, WIDTH / 2, HEIGHT - 100, spread=spacing, max_vertical_offset=-30, angle_range=8)
    
    pygame.display.flip()

    clock.tick(60)
    currentFrame += 1

    for card in hand:
        card.update(lerp_factor=0.2)
    
pygame.quit()
