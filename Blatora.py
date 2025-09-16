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

deck = []
handsize = 8

class Card:
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()
        self.selected = False
        self.current_offset = 0
        self.target_offset = 0
    def update(self, speed=2):
        if self.current_offset < self.target_offset:
            self.current_offset += speed
            if self.current_offset > self.target_offset:
                self.current_offset = self.target_offset
        elif self.current_offset > self.target_offset:
            self.current_offset -= speed
            if self.current_offset < self.target_offset:
                self.current_offset = self.target_offset

for root, dirs, files in os.walk(SUITS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (80, 110))
            deck.append(image)

random.shuffle(deck)

hand = [Card(deck.pop()) for _ in range(handsize)]

currentFrame = 0
spacing = 600 / handsize

def draw_hand(surface, cards, center_x, center_y, spread=20, max_vertical_offset=-30, angle_range=15):
    n = len(cards)
    if n == 0:
        return
    start_angle = -angle_range / 2
    angle_step = angle_range / (n - 1) if n > 1 else 0
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2

    for i, card in enumerate(cards):
        t = i / (n - 1) if n > 1 else 0.5
        x = start_x + i * spread
        y = center_y - max_vertical_offset * 4 * (t - 0.5)**2 + max_vertical_offset
        y -= card.current_offset
        angle = (t - 0.5) * -2 * angle_range
        rotated = pygame.transform.rotate(card.image, angle)
        rect = rotated.get_rect(center=(x, y))
        surface.blit(rotated, rect.topleft)

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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for card in hand:
                if card.rect.collidepoint(mouse_pos):
                    card.selected = not card.selected
                    card.target_offset = 40 if card.selected else 0
    screen.fill(green)

    draw_hand(screen, hand, WIDTH / 2, HEIGHT - 100, spread=spacing, max_vertical_offset=-30, angle_range=15)
    
    pygame.display.flip()

    clock.tick(60)
    currentFrame += 1

    for card in hand:
        card.update(speed=2)
    
pygame.quit()
