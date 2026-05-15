import os
import html
import random
import math
from collections import Counter
import sys
import subprocess
import webbrowser
import re
import time
import pygame
import pygame.freetype
import numpy
import cv2
import pyperclip
import colorsys
import JokerEffects
import copy
import operator
from JokerEffects import JokerEffectsManager, JOKER_REGISTRY, initialize_joker_effects
pygame.init()
pygame.freetype.init()

VW, VH = 1920, 1080
WIDTH, HEIGHT = VW, VH

_screen_info = pygame.display.Info()
REAL_W, REAL_H = _screen_info.current_w, _screen_info.current_h
_real_screen = pygame.display.set_mode((REAL_W, REAL_H), pygame.NOFRAME)

screen = pygame.Surface((VW, VH))

def _flip():
    if REAL_W == VW and REAL_H == VH:
        _real_screen.blit(screen, (0, 0)) 
        pygame.display.flip()
    else:
        pygame.transform.scale(screen, (REAL_W, REAL_H), _real_screen)
        pygame.display.flip()

def _virtual_mouse_pos():
    rx, ry = pygame.mouse.get_pos()
    return (int(rx * VW / REAL_W), int(ry * VH / REAL_H))

def _translate_event(event):
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        vx = int(event.pos[0] * VW / REAL_W)
        vy = int(event.pos[1] * VH / REAL_H)
        return pygame.event.Event(event.type, {**event.__dict__, 'pos': (vx, vy)})
    return event

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
CONS_DIR = os.path.join(ASSETS_DIR, "ConsCards")
JOKERSOUND_DIR = os.path.join(SOUNDS_DIR, "Jokers")
BASES_DIR = os.path.join(ASSETS_DIR, "CardBases")
PACKS_DIR = os.path.join(ASSETS_DIR, "CardPacks")
DECKS_DIR = os.path.join(ASSETS_DIR, "Decks")
scroll_offset = 0
scroll_speed = 30
hover_list = []
PLACEHOLDER = os.path.join(GUI_DIR, 'placeholder.png')
has_conquistador = False
screen_rect = screen.get_rect()
def load_image_safe(filepath, fallback_path=PLACEHOLDER):
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

Loading_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "Loading.png")), (VW, VH))
screen.blit(Loading_img, (0, 0))
_flip()

FONT_NATIVE = pygame.freetype.Font(os.path.join(FONTS_DIR, 'Protein Pixels.ttf'), 8)
FONT_NATIVE.antialiased = False

_render_cache   = {}
_width_cache    = {}
_textbox_cache  = {}

_NATIVE_LINE_HEIGHT = None

def _get_native_line_height():
    global _NATIVE_LINE_HEIGHT
    if _NATIVE_LINE_HEIGHT is None:
        _NATIVE_LINE_HEIGHT = FONT_NATIVE.get_sized_height()
    return _NATIVE_LINE_HEIGHT

def render_pixel(text, color, scale=1):
    text = "" if text is None else str(text)
    key = (text, color, scale)
    surf = _render_cache.get(key)
    if surf is None:
        surf, _ = FONT_NATIVE.render(text, color)
        if scale > 1:
            w, h = surf.get_size()
            surf = pygame.transform.scale(surf, (w * scale, h * scale))
        _render_cache[key] = surf
    return surf, surf.get_rect()

def _measure_width(text, scale):
    key = (text, scale)
    w = _width_cache.get(key)
    if w is None:
        w = FONT_NATIVE.get_rect(str(text)).width * scale
        _width_cache[key] = w
    return w

def pixel_text_width(text, scale=1):
    return _measure_width(text, scale)

def pixel_line_height(scale=1):
    return _get_native_line_height() * scale

class _ScaledFont:
    def __init__(self, scale):
        self.scale = scale
    def render(self, text, color):
        return render_pixel(text, color, self.scale)
    def get_sized_height(self):
        return pixel_line_height(self.scale)
    def get_rect(self, text):
        text = str(text) if text is not None else ""
        w = _measure_width(text, self.scale)
        h = pixel_line_height(self.scale)
        return pygame.Rect(0, 0, w, h)

OSDmono   = _ScaledFont(3)
PixelFont  = _ScaledFont(4)
PixelFontS = _ScaledFont(3)
PixelFontXS = _ScaledFont(2)
PixelFontXXS = _ScaledFont(1)
toggleable = True 
LETTERW = WIDTH/12
LETTERH = WIDTH/12
CENTERLETTERW = (WIDTH/2)-(LETTERW/2)
CENTERLETTERH = (HEIGHT/2)-(LETTERH/2)
currentFrame = 0
card_x = -WIDTH  
card_target_x = 0  
card_animating = False  
card_speed = int(WIDTH/66.666666666)
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
blue = (50, 50, 230)
yellow = (250, 220, 80)
orange = (240, 150, 40)
black = (0, 0, 0)
purple = (153, 102, 204)
teal = (0, 149, 182)

RulesHand = None
with open((os.path.join(TEXT_PATH,"HelpMenu.md")), "r", encoding="utf-8") as file:
    helptext = file.read()

help_lines = helptext.split('\n')
helpMenu_surfaces = []
scroll_offset = 0
scroll_speed = 30
line_height = OSDmono.get_sized_height()
jevilActive = False
hands_played = {
    'High Card': 0,
    'Pair': 0,
    'Two Pair': 0,
    'Three of a Kind': 0,
    'Straight': 0,
    'Flush': 0,
    'Full House': 0,
    'Four of a Kind': 0,
    'Straight Flush': 0,
    'Royal Flush': 0,
    'Five of a Kind': 0,
    'Flush Five': 0,
    'Flush House': 0,
    'Huh of a What': 0
}
for line in help_lines:
    clean_line = html.unescape(line.replace('\t', '    ').rstrip())

    if not clean_line.strip():
        helpMenu_surfaces.append(None)
        continue

    if '**' in clean_line:
        parts = clean_line.split('**')
        surfaces = []
        for i, part in enumerate(parts):
            if i % 2 == 1: 
                text_surface, _ = OSDmono.render(part, (0, 0, 0))
            else:
                text_surface, _ = OSDmono.render(part, (0, 0, 0))
            surfaces.append(text_surface)

        total_width = sum(s.get_width() for s in surfaces)
        combined_surface = pygame.Surface((total_width, line_height), pygame.SRCALPHA)
        x = 0
        for s in surfaces:
            combined_surface.blit(s, (x, 0))
            x += s.get_width()

        helpMenu_surfaces.append(combined_surface)
    else:
        surface, _ = OSDmono.render(clean_line, (0, 0, 0))
        helpMenu_surfaces.append(surface)

helpMenu, _  = PixelFont.render(helptext, (0, 0, 0))
clock = pygame.time.Clock()
pygame.mixer.init()

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

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

    if not ret:
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_cap.read()
    
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
        frame = frame.swapaxes(0, 1)
        video_surface = pygame.surfarray.make_surface(frame)
        return video_surface
    
    return None

def close_video():
    global video_cap
    if video_cap is not None:
        video_cap.release()
        video_cap = None

# ==================== SOUNDS ====================
foxsound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "FOCY.mp3"))
soseriousmusic = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "WHYSOSERIOUS.mp3"))
conquistadorsound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "conquistador.mp3"))
# ==================== SPRITESHEETS ====================
FOXYSCARE = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'focy.png'))
##SPINNINGBGIMG = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'StartBackground.png'))
SOSERIOUS = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'SoSerious.png'))
SETTINGSIMG = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'SettingsButton.png'))
SHOPANIMATIONIMG = load_image_safe(os.path.join(SPRITESHEETS_DIR, 'Shop_Animation.png'))
GLITCHSHEET = load_image_safe(os.path.join(SPRITESHEETS_DIR,'GlitchBaseSpriteSheet.png'))

# ==================== CURSORS ====================
cursor_normal = load_image_safe(os.path.join(GUI_DIR, 'CursorNormal.png'))
cursor_hover = load_image_safe(os.path.join(GUI_DIR, 'CursorHover.png'))
cursor_normal = pygame.transform.scale(cursor_normal, (32, 32))
cursor_hover = pygame.transform.scale(cursor_hover, (32, 32))

# ==================== GUI BUTTONS ====================
RunInfo = load_image_safe(os.path.join(GUI_DIR, 'RunInfoButton.png'))
RunInfo = pygame.transform.scale(RunInfo, (WIDTH/20, WIDTH/12))

Settings_2 = load_image_safe(os.path.join(GUI_DIR, 'Settings2.png'))
Settings_2 = pygame.transform.scale(Settings_2, (int(HEIGHT/5), int(HEIGHT/10.5)))

github_link = load_image_safe(os.path.join(GUI_DIR, 'GithubButton.png'))
github_link = pygame.transform.scale(github_link, (int(HEIGHT/5), int(HEIGHT/10.5)))

helpButtonimg = load_image_safe(os.path.join(GUI_DIR, 'HelpButton.png'))
helpButtonimg = pygame.transform.scale(helpButtonimg, (int(HEIGHT/5), int(HEIGHT/10.5)))

STARTBUTTON = load_image_safe(os.path.join(GUI_DIR, 'StartButton.png'))
STARTBUTTON = pygame.transform.smoothscale(STARTBUTTON, (int(WIDTH/4.4), int(HEIGHT/10)))

SETTINGONIMG = load_image_safe(os.path.join(GUI_DIR, 'Setting_on.png'))
SETTINGOFFIMG = load_image_safe(os.path.join(GUI_DIR, 'Setting_off.png'))
SETTINGONIMG = pygame.transform.scale(SETTINGONIMG, (int(HEIGHT/5), int(HEIGHT/10)))
SETTINGOFFIMG = pygame.transform.scale(SETTINGOFFIMG, (int(HEIGHT/5), int(HEIGHT/10)))

xbutton = load_image_safe(os.path.join(GUI_DIR, 'XButton.png'))
xbutton = pygame.transform.scale(xbutton, (int(HEIGHT/10), int(HEIGHT/10)))

quitButtonimg = load_image_safe(os.path.join(GUI_DIR, 'QuitButton.png'))
quitButtonimg = pygame.transform.scale(quitButtonimg, (int(HEIGHT/5), int(HEIGHT/10.5)))

# ==================== GAME UI BUTTONS ====================
Playhand_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "PlayHandButton.png")), (WIDTH/8.33, WIDTH/20))
Discardhand_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "DiscardHandButton.png")), (WIDTH/8.33, WIDTH/20))
SortbuttonRank_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SortbuttonRank.png")), (WIDTH/8.33, WIDTH/20))
SortbuttonSuit_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SortbuttonSuit.png")), (WIDTH/8.33, WIDTH/20))
CashOutButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "CashOutButton.png")), (HEIGHT/1.5, HEIGHT/8))
ShopBuy_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "ShopBuy.png")), (WIDTH/14.5, HEIGHT/14.54))
UseButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "UseButton.png")), (WIDTH/43.5, HEIGHT/15))
CantUseButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "CantUseButton.png")), (WIDTH/43.5, HEIGHT/15))
SellButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SellButton.png")), (WIDTH/14.5, HEIGHT/14.54))
RerollButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "Reroll.png")), (WIDTH/9.1, HEIGHT/12.5))
NextRoundButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "NextRound.png")), (WIDTH/9.1, HEIGHT/12.5))
SelectBlind_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SelectBlind.png")), (WIDTH/6.8, HEIGHT/20))
SkipBlind_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SkipBlind.png")), (WIDTH/12, HEIGHT/18))
PackDesc_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "PackDesc.png")), (WIDTH/5, HEIGHT/6))
Pointer_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "pointer.png")), (WIDTH/21, HEIGHT/17.875))

# ==================== BACKGROUNDS & PANELS ====================
STARTCARD = load_image_safe(os.path.join(GUI_DIR, 'StartCard.png'))
STARTCARD = pygame.transform.smoothscale(STARTCARD, (WIDTH, HEIGHT))

HandBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "Handbackground.png")), (HEIGHT/3.33, HEIGHT/7.62))
ScoreBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "ScoreBackground.png")), (HEIGHT/3.33, HEIGHT/10.66))
GoalBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "GoalBackground.png")), (HEIGHT/5.33, HEIGHT/8))
MoneyBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MoneyBackground.png")), (HEIGHT/4.71, HEIGHT/13.33))
RoundBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "RoundBackground.png")), (HEIGHT/4.71, HEIGHT/16))
SideBar_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "SideBar.png")), (HEIGHT/2.86, HEIGHT/1.33))
CashOutBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "CashOutBackground.png")), (HEIGHT/1.3, HEIGHT))
ShopBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "ShopBackground.png")), (HEIGHT/1.14, HEIGHT))
GameBackground_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "DefaultBackground.png")), (WIDTH, HEIGHT))
JokerBG_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "JokerBG.png")), (HEIGHT/1.5, HEIGHT/4.5))
ConsBG_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "ConsBG.png")), (HEIGHT/2.5, HEIGHT/4.5))
BlindBG_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "BlindBG.png")), (WIDTH/6, HEIGHT*2))
BossBlindBG_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "BossBlindBG.png")), (WIDTH/6, HEIGHT*2))
BlindName_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "BlindName.png")), (WIDTH/6.8, HEIGHT/20))
DeadBG_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "DeadBG.png")), (WIDTH/2.1, HEIGHT/1.1))
NewRun_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "NewRunButton.png")), (WIDTH/6.8, HEIGHT/20))
MainMenu_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MainMenuButton.png")), (WIDTH/6.8, HEIGHT/20))
Copy_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "CopyButton.png")), (WIDTH/6.8, HEIGHT/20))
conquistador_img  = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "conquistadorSplash.png")), (WIDTH,HEIGHT))
GameMenu_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "GameMenu.png")), (WIDTH/1.68, HEIGHT/1.1))
MenuBlinds_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MenuBlinds.png")), (WIDTH/6.462, HEIGHT/9.533))
MenuVouchers_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MenuVouchers.png")), (WIDTH/6.462, HEIGHT/9.533))
MenuPokerHands_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MenuPokerHands.png")), (WIDTH/6.462, HEIGHT/9.533))
MenuHandType_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MenuHandType.png")), (WIDTH/1.892, HEIGHT/26))
MenuBack_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "MenuBack.png")), (WIDTH/1.81, HEIGHT/16.824))
FullPeekMenu_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "FullPeekMenu.png")), (WIDTH/1.1, HEIGHT/1.1))
FullDeckButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "FullDeckButton.png")), (WIDTH/5.526, HEIGHT/16.824))
RemainingButton_img = pygame.transform.scale(load_image_safe(os.path.join(GUI_DIR, "RemainingButton.png")), (WIDTH/5.526, HEIGHT/16.824))

# ==================== OVERLAYS ====================
RedSeal_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "RedSeal.png")), (WIDTH/37.5, HEIGHT/36.35))
GoldSeal_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "GoldSeal.png")), (WIDTH/37.5, HEIGHT/36.35))
PurpleSeal_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "PurpleSeal.png")), (WIDTH/37.5, HEIGHT/36.35))
BlueSeal_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "BlueSeal.png")), (WIDTH/37.5, HEIGHT/36.35))
Foil_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "Foil.png")), (WIDTH/12.5, HEIGHT/7.27))
Holo_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "Holographic.png")), (WIDTH/12.5, HEIGHT/7.27))
Poly_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "Polychrome.png")), (WIDTH/12.5, HEIGHT/7.27))
Debuff_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "DebuffOverlay.png")), (WIDTH/12.5, HEIGHT/7.27))
cardShadow = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "CardShadow.png")), (WIDTH/12.5, HEIGHT/7.27))
Frozen_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "FrozenOverlay.png")), (WIDTH/12.5, HEIGHT/7.27))
Frozen2_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "FrozenOverlay2.png")), (WIDTH/12.5, HEIGHT/7.27))
Frozen3_img = pygame.transform.smoothscale(load_image_safe(os.path.join(OVERLAY_DIR, "FrozenOverlay3.png")), (WIDTH/12.5, HEIGHT/7.27))

# ==================== DECK IMAGES ======================
RedDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "RedDeck.png")), (HEIGHT/8, HEIGHT/5.82))
BlueDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "BlueDeck.png")), (HEIGHT/8, HEIGHT/5.82))
GreenDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "GreenDeck.png")), (HEIGHT/8, HEIGHT/5.82))
YellowDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "YellowDeck.png")), (HEIGHT/8, HEIGHT/5.82))
BlackDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "BlackDeck.png")), (HEIGHT/8, HEIGHT/5.82))
ShatteredDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "ShatteredDeck.png")), (HEIGHT/8, HEIGHT/5.82))
SpiderDeck_img = pygame.transform.smoothscale(load_image_safe(os.path.join(DECKS_DIR, "SpiderDeck.png")), (HEIGHT/8, HEIGHT/5.82))

# ==================== BUTTON RECTANGLES ====================
STARTBUTTON_X = int((WIDTH/2) - ((WIDTH/4.4)/2))
STARTBUTTON_Y = (HEIGHT/2) + CENTERLETTERH/2
start_button_rect = STARTBUTTON.get_rect()
start_button_rect.topleft = (STARTBUTTON_X, STARTBUTTON_Y)
SETTINGSRECT = SETTINGONIMG.get_rect()
xbutton_rect = xbutton.get_rect()
xbutton_rect.topleft = ((WIDTH - xbutton_rect.width), 0)
playhandw = Playhand_img.get_width()
playhandh = Playhand_img.get_height()
sortrankw = SortbuttonSuit_img.get_width()
sortrankh = SortbuttonSuit_img.get_height()
CashOutw = CashOutButton_img.get_width()
CashOuth = CashOutButton_img.get_height()
SortbuttonSuit_rect = SortbuttonSuit_img.get_rect()
SortbuttonSuit_rect.topleft = (int(WIDTH/2 - (sortrankw + sortrankw/2)), int(HEIGHT - int(sortrankh + sortrankh/10)))
SortbuttonRank_rect = SortbuttonRank_img.get_rect()
SortbuttonRank_rect.topleft = (int(WIDTH/2 + (sortrankw/2)), int(HEIGHT - int(sortrankh + sortrankh/10)))
Playhand_rect = Playhand_img.get_rect()
Playhand_rect.topleft = (int(0 + playhandw/4), HEIGHT - int(playhandh * 2))
Discardhand_rect = Playhand_img.get_rect()
Discardhand_rect.topleft = (int(WIDTH - (playhandw + playhandw/4)), HEIGHT - int(playhandh * 2))
CashOut_rect = CashOutButton_img.get_rect()
CashOut_rect.topleft = (WIDTH/3.2, HEIGHT / 1.9)
Reroll_rect = RerollButton_img.get_rect()
Reroll_rect.topleft = (WIDTH/2.95, HEIGHT/1.53)
NextRound_rect = NextRoundButton_img.get_rect()
NextRound_rect.topleft = (WIDTH/2.95, HEIGHT/1.83)
ShopBuy_rect = ShopBuy_img.get_rect()
ShopBuy_rect.topleft =(-100, -100)
SellButton_rect = SellButton_img.get_rect()
SellButton_rect.topleft =(-100, -100)
UseButton_rect = UseButton_img.get_rect()
UseButton_rect.topleft =(-100, -100)
SkipBlind_rect = SkipBlind_img.get_rect()
SkipBlind_rect.topleft =(-100, -100)
SelectBlind_rect = SelectBlind_img.get_rect()
SelectBlind_rect.topleft =(-100, -100)
CopyButton_rect = Copy_img.get_rect()
CopyButton_rect.topleft = (WIDTH/1.7 , HEIGHT/1.365)
NewRunButton_rect = NewRun_img.get_rect()
NewRunButton_rect.topleft = (WIDTH/1.34 , HEIGHT/1.25)
MainMenuButton_rect = MainMenu_img.get_rect()
MainMenuButton_rect.topleft = (WIDTH/1.74 , HEIGHT/1.25)
MenuBackButton_rect = MenuBack_img.get_rect()
MenuBackButton_rect.topleft = (WIDTH/4.53 , HEIGHT/1.15)
MenuBlindsButton_rect = MenuBlinds_img.get_rect()
MenuBlindsButton_rect.topleft = (WIDTH/1.67 , HEIGHT/8)
MenuPokerHandsButton_rect = MenuPokerHands_img.get_rect()
MenuPokerHandsButton_rect.topleft = (WIDTH/4.25 , HEIGHT/8)
MenuVouchersButton_rect = MenuVouchers_img.get_rect()
MenuVouchersButton_rect.topleft = (WIDTH/2.4 , HEIGHT/8)
RunInfo_rect = RunInfo.get_rect()
RunInfo_rect.topleft = (WIDTH/80, HEIGHT/1.67)
RemainingButton_rect = RemainingButton_img.get_rect()
RemainingButton_rect.topleft = (WIDTH/2.4 , HEIGHT/12)
FullDeckButton_rect = FullDeckButton_img.get_rect()
FullDeckButton_rect.topleft = (WIDTH/1.46 , HEIGHT/12)
deck_rect = RedDeck_img.get_rect()
deck_rect.topleft = (WIDTH/1.13 , HEIGHT/1.6)
# ==================== LETTER IMAGES ====================
for root, dirs, files in os.walk(LETTERS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            letter_name = os.path.splitext(filename)[0]
            image = pygame.transform.scale(load_image_safe(filepath), (int(LETTERW), int(LETTERH)))
            letter_images[letter_name] = image

jokerSound = {}
for root, dirs, files in os.walk(JOKERSOUND_DIR):
    for filename in files:
        if filename.endswith((".mp3", ".wav")):
            filepath = os.path.join(root, filename)
            name = os.path.splitext(filename)[0]
            sound = pygame.mixer.Sound(filepath)
            jokerSound[name] = sound

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
    def __init__(self,name, visible = True):
        
        self.toggle = False
        font_size = int(HEIGHT / 40)
        self.name, _ = PixelFont.render(name, (0, 0, 0))
        self.visible = visible
        self.img = SETTINGOFFIMG
        settingsList.append(self)
     
        self.rect = SETTINGSRECT.copy()
        
    def update_img(self):
        if self.visible:

            if self.toggle:
                self.img = SETTINGONIMG
            elif not self.toggle:
                self.img = SETTINGOFFIMG      
prev_attention_state = False
jonkler_sphere_clicked = False
jonkler_sphere_active = False           
dev_toggle = False
SO_SERIOUS = User_settings('SO SERIOUS')
Atttention_helper = User_settings('Attention Span Helper')
Focy = User_settings('Focy')
Music = User_settings('Music')
Music.toggle = True
Kawaii_Mode = User_settings('UWU?')
Pirate_Mode = User_settings('ARR')
Hood_Mode = User_settings('Gangsta')
SUFFIXES = [""]
REPLACEMENTS = [""]



# ==================== KAWAII MODE ====================
_KAWAII_SUFFIXES = [" uwu", " owo", " :3", " >w<", " ^-^", " ~nyaa~", "~"]

_KAWAII_REPLACEMENTS = [
    ("r", "w"), ("l", "w"), ("R", "W"), ("L", "W"),
    ("na", "nya"), ("Na", "Nya"), ("no", "nyo"), ("nu", "nyu"),
    ("th", "d"), ("Th", "D"),
]

_PIRATE_SUFFIXES = ["ie", "y"]
_PIRATE_REPLACEMENTS = [
    ("er", "ar"), ("Er", "Ar"),
    ("you", "ye"), ("You", "Ye"),
    ("your", "yer"), ("Your", "Yer"),
    ("my", "me"), ("My", "Me"),
    ("is", "be"), ("Is", "Be"),
    ("are", "be"), ("Are", "Be"),
    ("the", "th'"), ("The", "Th'"),
    ("to", "t'"), ("To", "T'"),
    ("ing", "in'"), ("ING", "IN'"),
    ("friend", "matey"), ("Friend", "Matey"),
    ("sir", "cap'n"), ("Sir", "Cap'n"),
    ("yes", "aye"), ("Yes", "Aye"),
    ("no ", "nay "), ("No ", "Nay "),
    ("hello", "ahoy"), ("Hello", "Ahoy"),
]

_HOOD_SUFFIXES = [" yo", " dawg", " bro", " fam", " cuz", " homie"]

_HOOD_REPLACEMENTS = [
    ("hello", "yo"), ("Hello", "Yo"),
    ("friend", "bro"), ("Friend", "Bro"),
    ("my ", "ma' "), ("My ", "Ma' "),
    ("is ", "be "), ("Is ", "Be "),
    ("are ", "be "), ("Are ", "Be "),
    ("the ", "da "), ("The ", "Da "),
    ("you ", "u "), ("You ", "U "),
    ("ing", "in'"), ("ING", "IN'"),
]



def _kawaii(text):
    if text is not None:
        if Kawaii_Mode.toggle:
            t = str(text)
            for old, new in _KAWAII_REPLACEMENTS:
                t = t.replace(old, new)
            return t + _KAWAII_SUFFIXES[hash(t) % len(_KAWAII_SUFFIXES)]
        elif Pirate_Mode.toggle:
            t = str(text)
            for old, new in _PIRATE_REPLACEMENTS:
                t = t.replace(old, new)
            return t + _PIRATE_SUFFIXES[hash(t) % len(_PIRATE_SUFFIXES)]
        elif Hood_Mode.toggle:
            t = str(text)
            for old, new in _HOOD_REPLACEMENTS:
                t = t.replace(old, new)
            return t + _HOOD_SUFFIXES[hash(t) % len(_HOOD_SUFFIXES)]
        return str(text)
class _KawaiiFont:
    def __init__(self, inner):
        self._inner = inner
    @property
    def scale(self):
        return self._inner.scale
    def render(self, text, color):
        return self._inner.render(_kawaii(text), color)
    def get_sized_height(self):
        return self._inner.get_sized_height()
    def get_rect(self, text):
        return self._inner.get_rect(_kawaii(text))

OSDmono    = _KawaiiFont(OSDmono)
PixelFont  = _KawaiiFont(PixelFont)
PixelFontS = _KawaiiFont(PixelFontS)
PixelFontXS = _KawaiiFont(PixelFontXS)
PixelFontXXS = _KawaiiFont(PixelFontXXS)
DEV_MODE = User_settings('Developer', False)  #Keep At Bottom#

def dev_commands():
    global dev_toggle
    global dev_command
    if DEV_MODE.toggle:
        if dev_toggle:
            dev_command = input('Insert Developer Command')

dev_code = "talabro"
dev_progress = ""

SHEET_PATH = os.path.join(SPRITESHEETS_DIR, 'Suits.png')
suitsheet = pygame.image.load(SHEET_PATH).convert_alpha()
sheet_w, sheet_h = suitsheet.get_size()
frame_w = sheet_w // 4
base_suits = []
for i in range(4):

    frame = pygame.Surface(
        (frame_w, sheet_h),
        pygame.SRCALPHA
    )

    frame.blit(
        suitsheet,
        (0, 0),
        (i * frame_w, 0, frame_w, sheet_h)
    )

    base_suits.append(frame)


rings = [
    {'radius':   70, 'count':  4, 'speed': 2,   'angle': 0,           'dir':  1, 'size': 20},
    {'radius':  140, 'count':  8, 'speed': 1.5, 'angle': math.pi/8,   'dir': -1, 'size': 32},
    {'radius':  280, 'count': 12, 'speed': 1,   'angle': 0,           'dir':  1, 'size': 46},
    {'radius':  560, 'count': 16, 'speed': 0.5, 'angle': math.pi/16,  'dir': -1, 'size': 60},
    
]

for ring in rings:
    s = ring['size']
    ring['suits'] = [
        pygame.transform.scale(suit, (s, s))
        for suit in base_suits
    ]
    ring['half'] = s // 2
    ring['offsets'] = [
        (i / ring['count']) * math.tau
        for i in range(ring['count'])
    ]

cx, cy = WIDTH // 2, HEIGHT // 2

_ring_surface = pygame.Surface((VW, VH), pygame.SRCALPHA)


def animate_ring():
    _ring_surface.fill((0, 0, 0, 0))

    for ring in rings:
        ring['angle'] += ring['speed'] * ring['dir'] * dt

        angle   = ring['angle']
        radius  = ring['radius']
        half    = ring['half']
        offsets = ring['offsets']
        suits   = ring['suits']
        count   = ring['count']

        for i in range(count):
            a = angle + offsets[i]
            x = cx + int(math.cos(a) * radius)
            y = cy + int(math.sin(a) * radius)
            if -half < x < WIDTH + half and -half < y < HEIGHT + half:
                rotation_deg = -math.degrees(a) + 90
                rotated = pygame.transform.rotate(suits[i % 4], rotation_deg)
                rw, rh = rotated.get_size()
                _ring_surface.blit(rotated, (x - rw // 2, y - rh // 2))

    screen.blit(_ring_surface, (0, 0))
    
def reset_deck_for_new_round():
    global deck, hand
    hand.clear()
    deck.clear()
    for card in perm_deck:
        card.retriggers = 0
        card.retriggers_remaining = 0
        card.state = "hand"
        card.is_debuffed = False
        card.debuff_assigned = False
        card.is_frozen = False
        card.freeze_timer = 0
        card.scoring_x = 0
        card.scoring_y = 0
        card.scaling = False
        card.growing = False
        card.scaling_done = False
        card.scoring_complete = False
        card.is_contributing = False
        card.scoring_animating = False
        card.vx = 0
        card.vy = 0
        card.angle = 0
        card.rotation_speed = 0
        card.scale = 1.0
        deck.append(card)
    random.shuffle(deck)
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
       
settings2 = GUITOGGLES(0, 0, Settings_2, scale_factor=1.15, isbutton=True)
helpButton = GUITOGGLES(0, 0, helpButtonimg, scale_factor=1.15, isbutton=True)    
githubButton = GUITOGGLES(0, 0, github_link, scale_factor=1.15, isbutton=True)    

###Keep Quit Button At Bottom of list###
quitButton  = GUITOGGLES(0,0, quitButtonimg , scale_factor = 1.15, isbutton = True)

def update_gui_buttons():
    if settings:
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
        if setting.visible:
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
    global blitting,dev_command, ante, joker_manager, round_num, current_blind, target_score, blitpositionx, blitpositiony, blitting_img, blitting_img_original, dev_toggle, scaling, dimensionsx, dimensionsy
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
            if dev_command.lower() == 'addjoker':
                print(All_Jokers_Name)
                addedJoker = input("Insert Name Of Joker")
                if addedJoker in All_Jokers_Name:
                    for joke in All_Jokers:
                        if joke.name == addedJoker:
                            new_joka = Joker(joke.image, joke.rarity, joke.name)
                            Active_Jokers.append(new_joka)
                            joker_manager = initialize_joker_effects(Active_Jokers) 
                            print(f"Added {joke.name} and reinitialized joker manager!")
            
            if dev_command.lower() == 'addjokers':
                print(All_Jokers_Name)
                addedJoker = input("Insert Name Of Joker, number of Jokers")
                name, number = addedJoker.split(",")
                name = name.strip()
                number = int(number.strip())
                for i in range(number):
                    if name in All_Jokers_Name:
                        for joke in All_Jokers:
                            if joke.name == addedJoker:
                                new_joka = Joker(joke.image, joke.rarity, joke.name)
                                Active_Jokers.append(new_joka)
                                joker_manager = initialize_joker_effects(Active_Jokers) 
                print(f"Added {number} {name}s and reinitialized joker manager!")
                    
            elif dev_command.lower() == 'setblit':
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
                    
                dimensionsx = input('Choose a width: ')
                dimensionsy = input('Choose a height: ')
                try:
                    dimensionsx = float(dimensionsx)
                    dimensionsy = float(dimensionsy)
                except:
                    print("Invalid dimensions")
                
                try:
                    blitting_img_original = pygame.image.load(os.path.join(directory, str(asset))).convert_alpha()
                except:
                    print("Something went wrong loading image")
                    
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
            
                except:
                    print("Something went wrong scaling")
                    dev_toggle = False
                    return

            elif dev_command.lower() == 'exit':
                dev_toggle = False
            
                DEV_MODE.toggle = False
                return
            
            elif dev_command.lower() == 'unblit':
                blitting = False
                
            elif dev_command.lower() == 'reblit':
                blitting = True
                
            elif dev_command.lower() == 'help':
                print("Commands: \n Help\n reblit\n unblit\n exit\n setblit\n blitW\n blitH\n blitx\n blity\n changescaling\n sethand\n resetdeck\n setresources\n setround\n setboss\naddtarot\n addjoker\n")
            
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
                
            elif dev_command.lower() == 'changescaling':
                new_scale = input("Insert New Scale Config (wh, ww, hh, hw, pixel): ").lower()
                scaling = new_scale
                print(f"Scaling mode changed to: {scaling}")
            
            elif dev_command.lower() == 'blitw':
                new_W = input("Insert New Width: ")
                try:
                    dimensionsx = float(new_W)
                    print(f"Width updated to: {dimensionsx}")
                except:
                    print("Invalid number")
            
            elif dev_command.lower() == 'blith':
                new_H = input("Insert New Height: ")
                try:
                    dimensionsy = float(new_H)
                    print(f"Height updated to: {dimensionsy}")
                except:
                    print("Invalid number")
                
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
                
            elif dev_command.lower() == 'setresources':
                global hands, discards, chips, mult
                try:
                    hands = int(input("Set hands remaining: "))
                    discards = int(input("Set discards remaining: "))
                    print(f"Resources updated: {hands} hands, {discards} discards")
                except:
                    print("Invalid input")
                
            elif dev_command.lower() == 'setround':
                try:
                    new_round = int(input("Set round number: "))
                    round_num = new_round
                    ante = ((round_num - 1) // 3) + 1
                    current_blind = None
                    get_current_blind()
                    print(f"Round set to {round_num}, Ante: {ante}")
                    print(f"Current blind: {current_blind.name if current_blind else 'None'}")
                except:
                    print("Invalid input")
                
            elif dev_command.lower() == 'setboss':
                if not boss_blinds:
                    print("No boss blinds available")
                    
                print("Available boss blinds:")
                for boss in boss_blinds:
                    print(f"  - {boss.name}")
                
                boss_name = input("Enter boss blind name: ").strip()
                if set_boss_blind(boss_name):
                    if round_num % 3 != 0:
                        round_num = ((round_num // 3) + 1) * 3
                        ante = (round_num - 1) // 3 + 1
                    print(f"Boss blind set to: {current_blind.name}")
                    print(f"Round adjusted to: {round_num}, Ante: {ante}")
                else:
                    print(f"Boss blind '{boss_name}' not found")
                
            else:
                print("Unknown command. Type 'help' for list of commands.")

            dev_command = input("Input Developer Command")    

_COLOR_TAGS = {
    'red':    (230, 50,  50),
    'blue':   (50,  150, 255),
    'yellow': (250, 220, 80),
    'orange': (240, 150, 40),
    'green':  (0,   200, 0),
    'white':  (255, 255, 255),
    'grey':   (128, 128, 128),
}
_TAG_PATTERN = re.compile(r'\[(\w+)\](.*?)\[/\1\]', re.DOTALL)

def _parse_segments(line, default_color):
    segments = []
    last = 0
    for m in _TAG_PATTERN.finditer(line):
        if m.start() > last:
            segments.append((line[last:m.start()], default_color))
        segments.append((m.group(2), _COLOR_TAGS.get(m.group(1), default_color)))
        last = m.end()
    if last < len(line):
        segments.append((line[last:], default_color))
    return segments

def _compose_text_box(text, font, color, box_w, bg_color, padding):
    scale     = font.scale
    lh        = pixel_line_height(scale)
    max_width = box_w - padding * 2
    space_w = _measure_width('a a', scale) - _measure_width('aa', scale)
    if space_w <= 0:
            space_w = scale * 3

    rendered_lines = []

    for paragraph in text.split('\n'):
        if paragraph.strip() == '':
            rendered_lines.append([])
            continue

        stripped      = paragraph.lstrip(' ')
        indent_chars  = len(paragraph) - len(stripped)
        indent_px     = space_w * indent_chars
        segments      = _parse_segments(stripped, color)

        words = []
        for seg_text, seg_color in segments:
            for word in seg_text.split(' '):
                if word:
                    words.append((word, seg_color))

        line_words, line_width = [], 0
        for word, col in words:
            w = _measure_width(word + ' ', scale)
            if line_width + w > max_width - indent_px and line_words:
                rendered_lines.append((line_words, indent_px))
                line_words, line_width = [], 0
            line_words.append((word, col))
            line_width += w
        if line_words:
            rendered_lines.append((line_words, indent_px))

    total_h = len(rendered_lines) * lh + padding * 2
    box_surf = pygame.Surface((box_w, total_h), pygame.SRCALPHA)

    if bg_color:
        box_surf.fill(bg_color)
        pygame.draw.rect(box_surf, color, box_surf.get_rect(), 2)

    y = padding
    for entry in rendered_lines:
        if not entry:
            y += lh
            continue
        line_words, indent_px = entry
        draw_x = padding + int(indent_px)
        phrases = []
        if line_words:
            cur_col = line_words[0][1]
            cur_words = [line_words[0][0]]
            for word, col in line_words[1:]:
                if col == cur_col:
                    cur_words.append(word)
                else:
                    phrases.append((' '.join(cur_words), cur_col))
                    cur_col = col
                    cur_words = [word]
            phrases.append((' '.join(cur_words), cur_col))

        for i, (phrase, col) in enumerate(phrases):
            surf, _ = render_pixel(phrase, col, scale)
            box_surf.blit(surf, (draw_x, y))
            draw_x += surf.get_width()
            if i < len(phrases) - 1:
                draw_x += space_w

        y += lh

    return box_surf

def draw_text_box(surface, text, font, color, rect, bg_color=None, padding=10):
    cache_key = (text, font.scale, rect.width, bg_color, color, padding)
    box_surf = _textbox_cache.get(cache_key)
    if box_surf is None:
        box_surf = _compose_text_box(text, font, color, rect.width, bg_color, padding)
        _textbox_cache[cache_key] = box_surf
    surface.blit(box_surf, (rect.x, rect.y))

def process_dev_command(command):
    global dev_command, ante, joker_manager, round_num, current_blind, target_score
    global hands, discards, chips, mult, hand, deck, perm_deck, handsize
    global blitting, blitting_img, blitting_img_original, blitpositionx, blitpositiony
    global scaling, dimensionsx, dimensionsy, Active_Jokers, All_Jokers, All_Jokers_Name
    global dev_awaiting_input, dev_current_command, dev_input_prompt, dev_multi_step_data
    global money,TarotCards,Held_Consumables
    
    command = command.strip()
    if dev_awaiting_input:
        return handle_multi_step_input(command)
    if not command:
        return "No command entered"
    
    command_lower = command.lower()
    if command_lower == 'help':
        return "Commands:\n  help - Show this help\n  addjoker - Add a joker\n addtarot - add a tarot card\n  resetdeck - Reset the deck\n  setresources - Set hands/discards\n  setround - Set round number\n  setboss - Set boss blind\n  money - Set money amount\n  sethand - Build custom hand\n  exit - Close dev mode"

    elif command_lower == 'addtarot':
        dev_awaiting_input = True
        tarots = []
        for tarot in TarotCards:
            tarots.append(tarot.name)
        
        dev_input_prompt = "Tarot Name"
        dev_current_command = "addtarot"
        return f"Available Consumables: {', '.join(tarots)}\n(Type Tarot Card name)"
    
    elif command_lower == 'addshadow':
        dev_awaiting_input = True
        shadow = []
        for s in ShadowCards:
            shadow.append(s.name)
        
        dev_input_prompt = "Shadow Name"
        dev_current_command = "addshadow"
        return f"Available Consumables: {', '.join(shadow)}\n(Type Shadow Card name)"
    
    elif command_lower == 'addspectral':
        dev_awaiting_input = True
        spectrals = []
        for spectral in SpectralCards:
            spectrals.append(spectral.name)
        
        dev_input_prompt = "Spectral Name"
        dev_current_command = "addspectral"
        return f"Available Consumables: {', '.join(spectrals)}\n(Type Spectral Card name)"

    elif command_lower == 'exit':
        DEV_MODE.toggle = False
        return "Developer Mode disabled"
    elif command_lower == 'addjoker':
        dev_awaiting_input = True
        dev_current_command = 'addjoker'
        dev_input_prompt = "Joker name"
        return f"Available jokers: {', '.join(All_Jokers_Name)}\n(Type joker name)"
    elif command_lower == 'addjokers':
        dev_awaiting_input = True
        dev_current_command = 'addjokers'
        dev_input_prompt = "Joker name"
        return f"Available jokers: {', '.join(All_Jokers_Name)}\n(Type joker name)"
    elif command_lower == 'resetdeck':
        hand.clear()
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
        return f"Deck reset! {len(hand)} cards in hand, {len(deck)} in deck"

    elif command_lower == 'setresources':
        dev_awaiting_input = True
        dev_current_command = 'setresources'
        dev_input_prompt = "Hands"
        dev_multi_step_data = {'step': 1}
        return "Enter number of hands:"

    elif command_lower == 'setround':
        dev_awaiting_input = True
        dev_current_command = 'setround'
        dev_input_prompt = "Round number"
        return "Enter round number:"

    elif command_lower == 'setboss':
        dev_awaiting_input = True
        dev_current_command = 'setboss'
        dev_input_prompt = "Boss name"
        boss_names = [b.name for b in boss_blinds]
        return f"Available bosses:\n  {chr(10).join(boss_names)}\n(Type boss name)"

    elif command_lower == 'money':
        dev_awaiting_input = True
        dev_current_command = 'money'
        dev_input_prompt = "Amount"
        return "Enter money amount:"

    elif command_lower == 'sethand':
        dev_awaiting_input = True
        dev_current_command = 'sethand'
        dev_input_prompt = "Card 1 rank"
        dev_multi_step_data = {'cards': [], 'step': 'rank', 'card_num': 1}
        return "Building custom hand.\nEnter rank for card 1 (or 'done'):\n  Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, Ace"
    
    else:
        return f"Unknown command: '{command}'\nType 'help' for available commands"
def get_available_jokers(joker_list):
    yinyang_active = any(j.name == "Yin Yang" for j in Active_Jokers)
    if yinyang_active:
        return [j for j in joker_list if j.name not in ("Yin Joker", "Yang Joker")]
    return joker_list
def handle_multi_step_input(input_text):
    global dev_awaiting_input, dev_current_command, dev_input_prompt, dev_multi_step_data
    global hands, discards, money, round_num, ante, current_blind, hand, deck
    global Active_Jokers, joker_manager, All_Jokers, All_Jokers_Name
    
    input_text = input_text.strip()
  
    if dev_current_command == 'addjoker':
        dev_awaiting_input = False
        joker_name = input_text
        
        for joke in All_Jokers:
            if joke.name.lower() == joker_name.lower():
                new_joka = Joker(joke.image, joke.rarity, joke.name)
                Active_Jokers.append(new_joka)
                joker_manager = initialize_joker_effects(Active_Jokers)
                return f"Added {joke.name}!"
        
        return f"Joker '{joker_name}' not found"
    
    if dev_current_command == 'addjokers':
        dev_awaiting_input = False
        joker_name = input_text
        name, number = joker_name.split(",")
        name = name.strip()
        number = int(number.strip())
        for joke in All_Jokers:
            if joke.name.lower() == name.lower():
                for i in range(number):
                    new_joka = Joker(joke.image, joke.rarity, joke.name)
                    Active_Jokers.append(new_joka)
                    joker_manager = initialize_joker_effects(Active_Jokers)
                return f"Added {number} {name}s!"
        return f"Joker '{joker_name}' not found"
 
    elif dev_current_command == 'setresources':
        if dev_multi_step_data.get('step') == 1:
            try:
                hands = int(input_text)
                dev_multi_step_data['hands'] = hands
                dev_multi_step_data['step'] = 2
                dev_input_prompt = "Discards"
                return f"Hands set to {hands}. Now enter discards:"
            except:
                dev_awaiting_input = False
                return "Invalid number"
        elif dev_multi_step_data.get('step') == 2:
            try:
                discards = int(input_text)
                dev_awaiting_input = False
                return f"Set hands={dev_multi_step_data['hands']}, discards={discards}"
            except:
                dev_awaiting_input = False
                return "Invalid number"
    
    elif dev_current_command == 'setround':
        try:
            round_num = int(input_text)
            ante = ((round_num - 1) // 3) + 1
            current_blind = None
            get_current_blind()
            dev_awaiting_input = False
            return f"Round={round_num}, Ante={ante}"
        except:
            dev_awaiting_input = False
            return "Invalid round number"
    
    elif dev_current_command == 'setboss':
        boss_name = input_text
        if set_boss_blind(boss_name):
            if round_num % 3 != 0:
                round_num = ((round_num // 3) + 1) * 3
                ante = (round_num - 1) // 3 + 1
            dev_awaiting_input = False
            return f"Boss set to {current_blind.name}"
        dev_awaiting_input = False
        return f"Boss '{boss_name}' not found"
    
    elif dev_current_command == 'addtarot':
        tarotToAdd = input_text
        for tarot in TarotCards:
            if (tarot.name).lower() == input_text:
                name = tarot.name
                new_tarot = Consumable(tarot.image, name.title())
                Held_Consumables.append(new_tarot)
                dev_awaiting_input = False
                for card in Held_Consumables:
                    print(card.name)
                return f"Added '{tarotToAdd}' to Consumables"
        dev_awaiting_input = False
        return f"Tarot Card Not Found"

    elif dev_current_command == 'addshadow':
        shadowToAdd = input_text
        for s in ShadowCards:
            if (s.name).lower() == input_text:   
                new_tarot = Consumable(s.image, s.name)
                Held_Consumables.append(new_tarot)
                dev_awaiting_input = False
                return f"Added '{shadowToAdd}' to Consumables"
        dev_awaiting_input = False
        return f"Shadow Card Not Found"

    elif dev_current_command == 'addspectral':
        specToAdd = input_text
        for spec in SpectralCards:
            if (spec.name).lower() == input_text:
                
                new_tarot = Consumable(spec.image, spec.name)
                Held_Consumables.append(new_tarot)
                dev_awaiting_input = False
                return f"Added '{specToAdd}' to Consumables"
        dev_awaiting_input = False
        return f"Spectral Card Not Found"
    
    elif dev_current_command == 'money':
        try:
            money = int(input_text)
            dev_awaiting_input = False
            return f"Money set to ${money}"
        except:
            dev_awaiting_input = False
            return "Invalid amount"
    
    elif dev_current_command == 'sethand':
        data = dev_multi_step_data
        
        if input_text.lower() == 'done':
            hand.clear()
            for card_data in data['cards']:
                rank, suit, image = card_data
                new_card = Card(rank, suit, image)
                new_card.slot = len(hand)
                new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
                new_card.state = "hand"
                hand.append(new_card)
            sort_hand()
            dev_awaiting_input = False
            return f"Hand set with {len(hand)} cards"
        
        if data['step'] == 'rank':
            rank = input_text.title()
            if rank not in ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]:
                return f"Invalid rank. Try again or type 'done'"
            data['current_rank'] = rank
            data['step'] = 'suit'
            dev_input_prompt = f"Card {data['card_num']} suit"
            return f"Card {data['card_num']}: {rank}\nNow enter suit (Hearts, Diamonds, Clubs, Spades):"
        
        elif data['step'] == 'suit':
            suit = input_text.title()
            if suit not in ["Hearts", "Diamonds", "Clubs", "Spades"]:
                return "Invalid suit. Enter: Hearts, Diamonds, Clubs, or Spades"
            
            rank = data['current_rank']
            filepath = os.path.join(SUITS_DIR, suit, f"{rank}Of{suit}.png")
            try:
                image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (HEIGHT/8, HEIGHT/5.82))
                data['cards'].append((rank, suit, image))
                data['card_num'] += 1
                data['step'] = 'rank'
                dev_input_prompt = f"Card {data['card_num']} rank"
                
                if data['card_num'] > 8:
                    hand.clear()
                    for card_data in data['cards']:
                        rank, suit, image = card_data
                        new_card = Card(rank, suit, image)
                        new_card.slot = len(hand)
                        new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
                        new_card.state = "hand"
                        hand.append(new_card)
                    sort_hand()
                    dev_awaiting_input = False
                    return f"Hand set with {len(hand)} cards"
                
                return f"Added {rank} of {suit}. Enter rank for card {data['card_num']} (or 'done'):"
            except:
                return f"Card not found. Try again."
    
    dev_awaiting_input = False
    return "Command cancelled"

def draw_dev_command_bar():
    if not dev_command_bar_active:
        return
    
    bar_height = HEIGHT // 3
    bar_y = HEIGHT - bar_height
    bar_surface = pygame.Surface((WIDTH, bar_height))
    bar_surface.fill((0, 0, 0))
    bar_surface.set_alpha(230)
    screen.blit(bar_surface, (0, bar_y))
    pygame.draw.rect(screen, yellow, (0, bar_y, WIDTH, bar_height), 2)
    
    line_height = PixelFontXXS.get_sized_height() + 5
    max_y = HEIGHT - 50
    
    expanded_lines = []
    for line in dev_command_output_lines:
        color = yellow if line.startswith("> ") else white
        for subline in line.split('\n'):
            expanded_lines.append((subline[:100], color))

    max_lines = (bar_height - 60) // line_height
    visible = expanded_lines[-max_lines:]
    
    y_offset = bar_y + 10
    for subline, color in visible:
        if y_offset + line_height < max_y:
            text, _ = PixelFontXXS.render(subline, color)
            screen.blit(text, (10, y_offset))
            y_offset += line_height
    
    input_y = HEIGHT - 35
    if dev_awaiting_input:
        prompt = f"{dev_input_prompt}> "
    else:
        prompt = "> "
    prompt_text, _ = PixelFontXS.render(prompt, yellow)
    screen.blit(prompt_text, (10, input_y))
    input_text, _ = PixelFontXS.render(dev_command_input + "_", white)
    screen.blit(input_text, (10 + prompt_text.get_width(), input_y))
            
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
            bob_offset = math.sin(self.bob_timer) * (LETTERH / 3)
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
    
    while True:
        shuffled = Letters.copy()
        random.shuffle(shuffled)

        if shuffled != Letters:
            break

    for i, letter in enumerate(shuffled):
        letter.target_x = LetterPosx[i]
def animate_letters():
    global letter_animation
    screen.fill((255,255,255))
    for i in Letters:
        i.draw()
    _flip()
    pygame.time.wait(200)
        
    global letter_animation
    while letter_animation:
        for event in pygame.event.get():
            event = _translate_event(event)
            if event.type  == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        screen.fill((255,255,255))
        for i in Letters:
            i.updatex()
            
            i.draw()
        _flip()
        clock.tick(60)
        if abs(StartingB.xpos - StartingB.target_x) < 1:
            letter_animation = False

def loadAudio(file):
    quackplay = pygame.mixer.Sound(os.path.join(SOUNDS_DIR,'Quack.wav'))
    try:
        sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, file))
        return sound
    except:
        return quackplay
    
def pop_and_check_retrigger(card, scoring_queue):
    if not scoring_queue:
        return
    scoring_queue.pop(0)
    if card.seal == "Red" and not card.seal_triggered:
        card.retriggers_remaining += 1
    card.seal_triggered = True
    if card.retriggers_remaining > 0:
        card.retriggers_remaining -= 1
        card.scoring_complete = False
        card.base_scoring_complete = False
        card.scoring_progress = 1
        card.scaling = True
        card.scaling_done = False
        card.growing = False
        card.scale = 1.0
        card.scaling_delay = 0
        card.rotation_speed = 0
        card.angle = 0
        card.state = "played"
        card.scoring_animating = True
        card.scoring_y = 0
        card.scoring_x = 0
        scoring_queue.insert(0, card)
    else:
        card.state = "scored"

buttonClick = loadAudio('Button.wav')
buttonClick.set_volume(0.5)
ptsdExplosion = loadAudio('PTSD reset.mp3')
ptsdExplosion.set_volume(0.75)
mainMusic = loadAudio('Music.mp3')

mainMusic.set_volume(0.1)
mainMusic.play(-1)
mainMusicPlaying = True

perm_deck = []
default_deck = []
Active_Jokers = []
packHand = []
scoring_queue = []
selectedMenu = "Hands"
menuOpen = False
fullPeekOpen = False
PeekSelected = "Remaining"
CurrentDeck = "Red"
joker_manager = None
shopJokerSelected = False
ActiveJokerSelected = False
base_chance = 1
max_handsize = 8
handsize = max_handsize
chips = 0
mult = 0
current_score = 0
round_score = 0
scored_counter = 0
total_scoring_count = 0
scoring_count = 0
max_hand = 4
max_discard = 4
hands = max_hand
discards = max_discard
DRAG_THRESHOLD = 20
calc_progress = 0.0
saved_base_chips  = 0
saved_base_mult = 0
saved_level = 0
blind_reward = 0
saved_hand = None
sort_mode = "rank"
current_scoring_card = None
discard_timer = 0
mouth_triggered = False
GameState = None
maxJokerCount = 5
rerollCost = 3
highest_hand = 0
most_played = 0
cards_played = 0
cards_discarded = 0
purchases = 0
rerolls = 0
cards_found = 0
lastFool = None
locked_hands = ["Five of a Kind", "Flush House", "Flush Five", "Huh of a What"]
unlocked_hands = ["High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"]
locked_cards = ["Glitch", "King Shadow", "The Reaper", "Tag Team"]
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
    "Huh of a What": 1
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
    "Huh of a What": 10
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
    "Huh of a What": 100
    }

hand_plays = {
    "High Card": 0,
    "Pair": 0,
    "Two Pair": 0,
    "Three of a Kind": 0,
    "Straight": 0,
    "Flush": 0,
    "Full House": 0,
    "Four of a Kind": 0,
    "Straight Flush": 0,
    "Five of a Kind": 0,
    "Flush House": 0,
    "Flush Five": 0,
    "Huh of a What": 0
}

_peek_drag_state = {
    'card': None,
    'row': None,
    'offset_x': 0,
    'offset_y': 0,
    'cur_x': 0,
    'cur_y': 0,
    'drag_start': (0, 0),
    'was_dragged': False,
}
_peek_card_positions = {}

scored = False
scoring_in_progress = False
calculating = False
discarding = False
round_num = 1
visible_round_num = round_num
ante = 1
money = 4
blind_defeated = False
victory = False
target_score = 300
contributing = []
BLIND_X = -500
BLIND_Y = -500
total_score = 0
saved_total_score = 0
is_straight = False
is_flush = False
ShopCount = 2
totalReward = 0
scoreSpeed = 0.1

SCORED_POSITIONS = [
    (WIDTH//2.86, HEIGHT//2.29),
    (WIDTH//2.22, HEIGHT//2.29),
    (WIDTH//1.81, HEIGHT//2.29),
    (WIDTH//1.54, HEIGHT//2.29),
    (WIDTH//1.33, HEIGHT//2.29)
]

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANKS_WRITTEN = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
FACES_WRITTEN = ["Jack", "Queen", "King"]
NUMBERS_WRITTEN = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
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
    }
BOSS_DESC = {
    "The Arrow": "All cards with the Spade suit are debuffed",
    "The Band": "-1 handsize",
    "The Bird": "All cards with the Heart suit are debuffed",
    "The Bounce": "Score caps out at one-third target score",
    "The Bow": "All cards with the Diamond suit are debuffed",
    "The Bridge": "All cards with a rank under 10 are debuffed",
    "The Chair": "All cards with a rank above 9 are debuffed",
    "The Claw": "Played hand must contain an even number of cards",
    "The Cone": "All cards with the Club suit are debuffed",
    "The Crate": "All cards with an odd rank are debuffed",
    "The Eye": "screen blurred",
    "The Fork": "-1 to both hands and discards",
    "The Luck": "1 in 5 cards are debuffed",
    "The Ramp": "Target score is doubled",
    "The Sandwich": "Played hand must contain an odd number of cards",
    "The Sign": "Face cards are frozen at the start of the round",
    "The South": "1 in 5 cards are frozen",
    "The Splinter": "All cards with a black suit are debuffed",
    "The Twin": "Played hand cannot contain duplicate ranks",
    "The Check": "All cards with an even rank are debuffed",
    "The Spear": "Played hand must contain a straight",
    "The Mouth": "The played card with the highest rank is debuffed",
    "The Magnet": "All cards with a red suit are frozen at the start of the round",
    "Jade Butterfly": "idk bro figure it out",
    "Korma Burger": "mmmmmmmm burgre",
    "Sunset Fridge": "im a fridge",
    "Wedgewood Log": "you can get my log",
    "Wisteria Harmony": "[insert angel chorus here]",
    }

conquistadorActive = False
class Card:
    card_id_counter = 0
    def __init__(self, rank, suit, image, slot=None, state="hand", debuff=False, enhancement=None, edition=None, seal=None):
        self.image = image
        self.scale= 1.0
        self.rotation_speed = 0
        self.scaling_delay = 0
        self.enhancement_timer = 10
        self.is_debuffed = debuff
        self.debuff_assigned = False
        self.is_frozen = False
        self.freeze_timer = 0
        self.enhancement = enhancement
        self.edition = edition
        self.seal = seal
        self.scaling = False
        self.growing = False
        self.scaling_done = False
        self.scoring_complete = False
        self.seal_scaling_complete = False
        self.enhancement_scoring_complete = False
        self.edition_scoring_complete = False
        self.seal_triggered = False
        self.scoring_progress = 1
        self._lucky_num = 0
        self._lucky_num1 = 0
        self.rank = rank
        self.suit = suit
        self.saved_rank = rank
        self.saved_suit = suit
        self.value = RANK_VALUES[rank]
        self.card_id = Card.card_id_counter
        self.retriggers = 0 
        self.remaining = 0
        
        self.base_scoring_complete = False
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
    
    def __deepcopy__(self, memo):
        new_card = Card.__new__(Card)
        memo[id(self)] = new_card
        for k, v in self.__dict__.items():
            if k == 'image':
                setattr(new_card, k, v)
            else:
                setattr(new_card, k, copy.deepcopy(v, memo))
        return new_card

    def refresh_image(self):
        if self.enhancement == "Glitched":
            filename = f"GlitchBaseSpriteSheet.png"
            filepath = os.path.join(SPRITESHEETS_DIR, filename)
        else:
            if self.rank == 0:
                self.rank = self.saved_rank
            if self.suit == "Glitched":
                self.suit = self.saved_suit
            filename = f"{self.rank}Of{self.suit}.png"
            filepath = os.path.join(SUITS_DIR, self.suit, filename)

        raw_image = pygame.image.load(filepath).convert_alpha()
        if current_blind.name in ("The Bridge", "The Chair", "The Splinter", "The Bird", "The Bow", "The Arrow", "The Cone"):
            boss_debuff()
        self.image = pygame.transform.smoothscale(
            raw_image,
            (HEIGHT/8, HEIGHT/5.82)
        )

        self.rect = self.image.get_rect()

    def update(self):
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
        self.angle += self.rotation_speed
    def trigger(self, type, amount):
        global scoreSpeed
        match type:
            case "Mult":
                color = red
            case "Chips":
                color = blue
            case "Retrigger":
                color = red
            case "Money":
                color = yellow
            case "XMult":
                color = red
            case "Again":
                color = red
                amount = "Again!"
            case "Break":
                color = None
            case "Debuff":
                color = red
            case _:
                color = black
        if card.scoring_animating:
            if self.scaling_delay < 10:
                self.scaling_delay += 10 * scoreSpeed
            elif not self.growing:
                if self.scale < 1.4:
                    self.scale += 0.1
                    self.rotation_speed = -30 * scoreSpeed
                else:
                    self.scale = 1.4
                    self.rotation_speed = 30 * scoreSpeed
                    self.growing = True
            else:
                if self.scale > 1.0:
                    self.scale -= 0.1
                else:
                    self.scale = 1.0
                    self.rotation_speed = 0
                    self.scaling = False
                    self.growing = False
                    self.scaling_done = True
                    self.scoring_complete = True
                    self.scoring_progress += 1
                    self.scoring_animating = False
                    self.scaling_delay = 10
                    self.angle = 0
                    scoreSpeed += 0.01
                    if type != "Break":
                        if type != "Debuff":
                            indicator = ChipIndicator(int(self.x + 30), int(self.y - 130), amount, color)
                        else:
                            indicator = ChipIndicator(int(self.x + 30), int(self.y - 130), "Debuffed", color)
                    else:
                        perm_deck.remove(self)
                        indicator = ChipIndicator(int(self.x + 30), int(self.y - 130), "Broken", color)
                    chip_indicators.append(indicator)
            self.angle += self.rotation_speed

chip_indicators = []
class ChipIndicator:
    def __init__(self, x, y, value, color):
        self.x = x
        self.y = y
        self.start_y = y
        self.value = value
        self.alpha = 255
        self.lifetime = 20
        self.age = 0
        self.color = color
    def update(self):
        self.age += 1
        self.y = self.start_y - (self.age * 0.1)
        if self.age > (self.lifetime * 2 / 3):
            self.alpha = int(255 * (1 - (self.age - (self.lifetime * 2 / 3)) / (self.lifetime / 3)))
        return self.age < self.lifetime
    def draw(self, surface):
        diamond_size = HEIGHT/13.33
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
        r, g, b = self.color
        pygame.draw.polygon(diamond_surface, (r, g, b, self.alpha), adjusted_points)
        diamond_surface.set_alpha(self.alpha)
        surface.blit(diamond_surface, (self.x - diamond_size, self.y - diamond_size))
        text, _ = PixelFont.render(f"+{self.value}", (255, 255, 255))
        text.set_alpha(self.alpha)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)
for root, dirs, files in os.walk(SUITS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            image = pygame.transform.smoothscale(pygame.image.load(filepath).convert_alpha(), (HEIGHT/8, HEIGHT/5.82))
            name, _ = os.path.splitext(filename)
            rank, suit = name.split("Of")
            card = Card(rank, suit, image)
            default_deck.append(card)
perm_deck = copy.deepcopy(default_deck)
deck = perm_deck.copy()
random.shuffle(deck)
hand = []

currentFrame = 0
spacing = 600 / handsize * WIDTH/1500

def boss_debuff():
    global handsize, max_handsize, round_num, boss_name, boss_calculated, scoring_in_progress, final_score, target_score, hands, discards, max_hand, discarding, discard_queue, hand, deck, current_blind, selected_cards, mouth_triggered, is_straight, saved_hand
    if round_num % 3 == 0:
        if current_blind.name == "The Bird":
            for card in deck:
                if card.suit == "Hearts" or card.enhancement == "Wild":
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Arrow":
            for card in deck:
                if card.suit == "Spades" or card.enhancement == "Wild":
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Cone":
            for card in deck:
                if card.suit == "Clubs" or card.enhancement == "Wild":
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Bow":
            for card in deck:
                if card.suit == "Diamonds" or card.enhancement == "Wild":
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Bounce":
            if final_score > target_score / 3:
                final_score = int(target_score / 3)
        if current_blind.name == "The Eye":
            blur_amount = 25
            small_size = (WIDTH // blur_amount, HEIGHT // blur_amount)
            small_surf = pygame.transform.smoothscale(screen, small_size)
            blurred = pygame.transform.smoothscale(small_surf, (WIDTH, HEIGHT))
            return blurred
        if current_blind.name == "The Bridge":
            for card in deck:
                if card.value <= 9:
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Chair":
            for card in deck:
                if card.value >= 10:
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Crate":
            for card in deck:
                if card.value % 2 == 0:
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Luck":
            for card in deck:
                rand = random.randint(min(base_chance, 5), 5)
                if rand == 5 and not card.debuff_assigned:
                    card.is_debuffed = True
        if current_blind.name == "The Fork":
            if hands >= max_hand:
                hands -= 1
                discards -= 1
        if current_blind.name == "The Ramp":
            for card in deck:
                card.is_debuffed = False
        if current_blind.name == "The Sandwich":
            played_card_count = 0
            for card in hand:
                if card.state:
                    if card.state in ("played", "scored", "scoring"):
                        played_card_count += 1
            for card in hand:
                if played_card_count % 2 != 1 and card.state in ("played", "scored"):
                    card.is_debuffed = True
        if current_blind.name == "The Twin":
            hand_type, contributing = detect_hand(selected_cards)
            value_counts = {}
            for card in contributing:
                if card.state == "played":
                    value_counts[card.value] = value_counts.get(card.value, 0) + 1
            duplicate_values = [val for val, count in value_counts.items() if count > 1]
            for card in contributing:
                if card.value in duplicate_values:
                    card.is_debuffed = True
        if current_blind.name == "The Magnet":
            for card in deck:
                if card.suit in ("Hearts", "Diamonds") or card.enhancement == "Wild":
                    card.is_frozen = True
                    card.freeze_timer = 3
        if current_blind.name == "The Splinter":
            for card in deck:
                if card.suit in ("Spades", "Clubs") or card.enhancement == "Wild":
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The South":
            for card in deck:
                rand = random.randint(min(base_chance, 5), 5)
                if rand == 5 and not card.debuff_assigned:
                    card.is_frozen = True
                    card.freeze_timer = random.randint(1, 3)
        if current_blind.name == "The Band":
            if handsize == max_handsize:
                handsize -= 1
        if current_blind.name == "The Check":
            for card in deck:
                if card.value % 2 == 0:
                    card.is_debuffed = True
                else:
                    card.is_debuffed = False
        if current_blind.name == "The Spear":
            contributing = detect_hand(selected_cards)[0]
            for card in hand:
                if card.state in ("played", "scored"):
                        if not saved_hand in ("Straight", "Straight Flush", "Royal Flush"):
                            card.is_debuffed = True
        if current_blind.name == "The Mouth":
            for card in hand:
                if card.state == "played" and not mouth_triggered:
                    available = [c for c in selected_cards if not c.is_debuffed]
                    if available:
                        highest = max(available, key=lambda c: c.chip_value)
                        highest.is_debuffed = True
                        mouth_triggered = True
        if current_blind.name == "The Claw":
            played_card_count = 0
            for card in hand:
                if card.state:
                    if card.state in ("played", "scored"):
                        played_card_count += 1
            for card in hand:
                if played_card_count % 2 != 0 and card.state in ("played", "scored"):
                    card.is_debuffed = True
        if current_blind.name == "The Sign":
            for card in deck:
                if card.rank in ("J", "Q", "K"):
                    card.freeze_timer = 4
        for card in deck:
            card.debuff_assigned = True
    else:
        for card in deck:
            card.is_debuffed = False
            card.debuff_assigned = False
        handsize = max_handsize
    for card in hand:
        if card.freeze_timer <= 0:
            card.is_frozen = False
      
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
            card.angle = (t - 0.5) * -2 * angle_range
            target_y -= HEIGHT/20
        elif card.state == "played":
            if card.scoring_x == 0:
                if len(scoring_queue) <= len(SCORED_POSITIONS):
                    card.scoring_x, card.scoring_y = SCORED_POSITIONS[selected_cards.index(card)]
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
        if card.scoring_x != 0 and card.state in ("played", "scored"):
            if card.is_contributing:
                if card.scoring_y == HEIGHT//2.29:
                    card.scoring_y -= HEIGHT/32
            target_x, target_y = card.scoring_x, card.scoring_y
            if not card.scaling:
                card.angle = 0
        card.target_x = target_x
        card.target_y = target_y
        angle = card.angle
        scaled_w = int(card.image.get_width() * card.scale)
        scaled_h = int(card.image.get_height() * card.scale)
        scaled_img = pygame.transform.smoothscale(card.image, (scaled_w, scaled_h))
        if card.enhancement == None:
            enhancement = "Default"
        else:
            enhancement = card.enhancement
        if card.enhancement == "Glitched":
            card_base = glitchimage
        else:

            filepath = enhancement + "Base.png"
            filepath = os.path.join(BASES_DIR, filepath)
            
            card_base = pygame.image.load(filepath).convert_alpha()
    
        scaled_base = pygame.transform.scale(card_base, (scaled_w, scaled_h))
        if card.is_debuffed:
            scaled_overlay = pygame.transform.smoothscale(Debuff_img, (scaled_w, scaled_h))
            scaled_img = scaled_img.copy()
            scaled_img.blit(scaled_overlay, (0, 0))
        match card.edition:
            case "Foil":
                scaled_overlay = pygame.transform.smoothscale(Foil_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
            case "Holographic":
                scaled_overlay = pygame.transform.smoothscale(Holo_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
            case "Polychrome":
                scaled_overlay = pygame.transform.smoothscale(Poly_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
        match card.seal:
            case "Red":
                scaled_overlay = pygame.transform.smoothscale(RedSeal_img, (scaled_w / 3, scaled_h / 5))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (scaled_w / 7, scaled_h / 7))
            case "Gold":
                scaled_overlay = pygame.transform.smoothscale(GoldSeal_img, (scaled_w / 3, scaled_h / 5))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (scaled_w / 7, scaled_h / 7))
            case "Blue":
                scaled_overlay = pygame.transform.smoothscale(BlueSeal_img, (scaled_w / 3, scaled_h / 5))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (scaled_w / 7, scaled_h / 7))
            case "Purple":
                scaled_overlay = pygame.transform.smoothscale(PurpleSeal_img, (scaled_w / 3, scaled_h / 5))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (scaled_w / 7, scaled_h / 7))
        if card.is_frozen:
            if card.freeze_timer == 3:
                scaled_overlay = pygame.transform.smoothscale(Frozen_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
            if card.freeze_timer == 2:
                scaled_overlay = pygame.transform.smoothscale(Frozen2_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
            if card.freeze_timer == 1:
                scaled_overlay = pygame.transform.smoothscale(Frozen3_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
        rotated = pygame.transform.rotate(scaled_img, angle)
        rotated_base = pygame.transform.rotate(scaled_base, angle)
        rect = rotated.get_rect(center=(card.x, card.y))
        surface.blit(rotated_base, rect.topleft)
        if card.enhancement != "Glitched":
            surface.blit(rotated, rect.topleft)
        else:
            scaled_glitch = pygame.transform.smoothscale(glitchimage, (scaled_w, scaled_h))
            rotated_glitch = pygame.transform.rotate(scaled_glitch, angle)
            glitch_rect = rotated_glitch.get_rect(center=(card.x, card.y))
            surface.blit(rotated_glitch, glitch_rect.topleft)
        card.rect = rect

class Animation():
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
            if self.sprite_sheet == SHOPANIMATIONIMG:
                scaled = pygame.transform.scale(frame_surface, (setWidth, setHeight))
            else:
                
                scaled = pygame.transform.smoothscale(frame_surface, (setWidth, setHeight))
            self.cached_frames.append(scaled)
        
    def animate(self):
        global draw_fox
        if self.current_frame >= self.frames - 1:
            if self.sprite_sheet == FOXYSCARE:
                draw_fox = False
                self.reset_animation()
                return
        if currentFrame % self.frame_interval == 0:
            self.current_frame = (self.current_frame + 1) % self.frames      
        
        screen.blit(self.cached_frames[self.current_frame], (self.xpos, self.ypos))
      
    def reset_animation(self):
        self.current_frame = 1
    
class Draggable_Animation(Animation):
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
        
#spinningBG = Animation(SPINNINGBGIMG, 1980, 1080, 24, 71, 0, 0, WIDTH, HEIGHT)
settingsButton = Animation(SETTINGSIMG, 333, 333, 23, 50, WIDTH - WIDTH/6,HEIGHT - WIDTH/6, WIDTH/6, WIDTH/6)
soserious = Draggable_Animation(SOSERIOUS, 250, 250, 24, 39, (WIDTH/1.5)-250, (HEIGHT/2)-250, int(WIDTH/5), int(WIDTH/5))
setting_rect = pygame.Rect(WIDTH-WIDTH/6 , HEIGHT - WIDTH/6, WIDTH/6, WIDTH/6)
focy_scare = Animation(FOXYSCARE,200, 150, 18, 14, 0, 0,  WIDTH, HEIGHT)
shopAnimation = Animation(SHOPANIMATIONIMG, 476, 1600, 24, 87, 0 + ((HEIGHT/2.86 - HEIGHT/3.3)/2),0, int(HEIGHT/3.3), (HEIGHT/3.3 * 3.36134453782))

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = filename

    def get_frame(self, x, y, width, height, scale=1):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (x, y, width, height))
        if scale != 1:
            frame = pygame.transform.scale(frame, (width * scale, height * scale))
        return frame

    def get_all_frames(self, frame_width, frame_height, rows=1, cols=1):
        frames = []
        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frames.append(self.get_frame(x, y, frame_width, frame_height))
        return frames

GLITCHOBJ = SpriteSheet(GLITCHSHEET)
glitchframes = GLITCHOBJ.get_all_frames(80, 110, rows=1, cols=42)
glitch_index = 0
glitch = glitchframes[0]  
glitchimage = glitchframes[0]
_peek_base_cache = {}
_peek_card_image_cache = {}
_peek_rows_cache = None
_peek_rows_deck_hash = None
_peek_stats_cache = {}
_peek_stats_hash = None

def draw_peek_view(source_deck, show_remaining_overlay):
    global mouse_display

    for key in list(_peek_rotated_cache.keys()):
        card_id = key[0]
        for c in source_deck:
            if c.card_id == card_id and c.enhancement == "Glitched":
                del _peek_rotated_cache[key]
                break
    ...
def get_peek_base(enhancement):
    if enhancement not in _peek_base_cache:
        path = os.path.join(BASES_DIR, 
            ("GlitchedBase" if enhancement == "Glitched" else enhancement + "Base") + ".png")
        try:
            surf = pygame.image.load(path).convert_alpha()
        except Exception:
            surf = pygame.image.load(os.path.join(BASES_DIR, "DefaultBase.png")).convert_alpha()
        _peek_base_cache[enhancement] = surf
    return _peek_base_cache[enhancement]

def get_peek_card_images(card, mini_cw, mini_ch):
    cache_key = (card.card_id, card.enhancement, card.edition, card.seal, mini_cw, mini_ch)

    if card.enhancement == "Glitched":
        mini_base = pygame.transform.scale(get_peek_base("Glitched"), (mini_cw, mini_ch))
        mini_img  = pygame.transform.smoothscale(glitchimage, (mini_cw, mini_ch))
        return mini_base, mini_img
    if cache_key in _peek_card_image_cache:
        return _peek_card_image_cache[cache_key]


    enh = card.enhancement or "Default"
    base_surf = get_peek_base(enh)
    mini_base = pygame.transform.scale(base_surf, (mini_cw, mini_ch))
    mini_img  = pygame.transform.smoothscale(card.image, (mini_cw, mini_ch))

    overlay_map = {"Foil": Foil_img, "Holographic": Holo_img, "Polychrome": Poly_img}
    if card.edition in overlay_map:
        mini_img = mini_img.copy()
        mini_img.blit(pygame.transform.smoothscale(overlay_map[card.edition], (mini_cw, mini_ch)), (0, 0))

    seal_map = {"Red": RedSeal_img, "Gold": GoldSeal_img, "Blue": BlueSeal_img, "Purple": PurpleSeal_img}
    if card.seal in seal_map:
        mini_img = mini_img.copy()
        seal = pygame.transform.smoothscale(seal_map[card.seal], (mini_cw // 3, mini_ch // 5))
        mini_img.blit(seal, (mini_cw // 7, mini_ch // 7))

    _peek_card_image_cache[cache_key] = (mini_base, mini_img)
    return mini_base, mini_img

def get_peek_rows(source_deck, suit_order, rank_order):
    global _peek_rows_cache, _peek_rows_deck_hash
    deck_hash = tuple((c.card_id, c.enhancement, c.suit, c.rank) for c in source_deck)
    if deck_hash == _peek_rows_deck_hash:
        return _peek_rows_cache
    
    def _peek_rank_key(c):
        r = c.saved_rank if c.enhancement == "Glitched" else c.rank
        try: return rank_order.index(r)
        except: return len(rank_order)
    
    rows = []
    for suit in suit_order:
        normal, glitch = [], []
        for card in source_deck:
            eff = card.saved_suit if card.enhancement == "Glitched" else card.suit
            if eff == suit:
                (glitch if card.enhancement == "Glitched" else normal).append(card)
        normal.sort(key=_peek_rank_key)
        glitch.sort(key=_peek_rank_key)
        rows.append(normal + glitch)
    
    _peek_rows_cache = rows
    _peek_rows_deck_hash = deck_hash
    return rows

def get_peek_stats(source_deck):
    global _peek_stats_hash, _peek_stats_cache
    h = tuple((c.card_id, c.rank, c.suit) for c in source_deck)
    if h == _peek_stats_hash:
        return _peek_stats_cache
    
    face_ranks = {"King", "Queen", "Jack"}
    number_ranks = {"Ten", "Nine", "Eight", "Seven", "Six", "Five", "Four", "Three", "Two"}
    all_ranks = ["Ace","King","Queen","Jack","Ten","Nine","Eight","Seven","Six","Five","Four","Three","Two"]
    all_suits = ["Spades", "Hearts", "Clubs", "Diamonds"]
    
    stats = {
        'aces':    sum(1 for c in source_deck if c.rank == "Ace"),
        'faces':   sum(1 for c in source_deck if c.rank in face_ranks),
        'numbers': sum(1 for c in source_deck if c.rank in number_ranks),
    }
    for suit in all_suits:
        stats[suit] = sum(1 for c in source_deck if c.suit == suit)
    for rank in all_ranks:
        stats[rank] = sum(1 for c in source_deck if c.rank == rank)
    
    _peek_stats_cache = stats
    _peek_stats_hash = h
    return stats

def draw_peek_view(source_deck, show_remaining_overlay):
    global mouse_display
    SUIT_ORDER = ["Spades", "Hearts", "Clubs", "Diamonds"]
    RANK_ORDER = ["Ace","King","Queen","Jack","Ten","Nine","Eight","Seven","Six","Five","Four","Three","Two"]
    PEEK_SECTION_X = int(WIDTH / 2.5)
    PEEK_SECTION_Y = int(HEIGHT / 4)
    PEEK_SECTION_W = int(WIDTH / 2.1)
    PEEK_SECTION_H = int(HEIGHT / 2)
    MINI_CW = int((HEIGHT / 8) * 0.55)
    MINI_CH = int((HEIGHT / 5.82) * 0.55)
    NUM_ROWS = len(SUIT_ORDER)
    ROW_GAP = (PEEK_SECTION_H - MINI_CH) // (NUM_ROWS - 1)
    SPRING_STIFFNESS = 0.18
    SPRING_DAMPING = 0.72
    PEEK_ANGLE_RANGE = 4
    PEEK_VERT_LIFT = 6

    _deck_ids = {c.card_id for c in deck}
    _pds = _peek_drag_state
    _mx, _my = _virtual_mouse_pos()
    _mb = pygame.mouse.get_pressed()

    if not _mb[0] and _pds['card'] is not None:
        _pds['card'] = None
        _pds['row'] = None

    peek_rows = get_peek_rows(source_deck, SUIT_ORDER, RANK_ORDER)

    for row_idx, row_cards in enumerate(peek_rows):
        n = len(row_cards)
        if n == 0:
            continue
        row_y_base = PEEK_SECTION_Y + row_idx * ROW_GAP
        col_gap = (PEEK_SECTION_W - MINI_CW) // (n - 1) if n > 1 else 0
        for col_idx, card in enumerate(row_cards):
            t = col_idx / (n - 1) if n > 1 else 0.5
            arc_y_lift = -PEEK_VERT_LIFT * (1.0 - 4 * (t - 0.5) ** 2)
            target_cx = PEEK_SECTION_X + MINI_CW // 2 + col_idx * col_gap
            target_cy = int(row_y_base + arc_y_lift + MINI_CH // 2)

            if card.card_id not in _peek_card_positions:
                _peek_card_positions[card.card_id] = {
                    'cx': float(target_cx), 'cy': float(target_cy),
                    'vx': 0.0, 'vy': 0.0,
                    'target_cx': float(target_cx), 'target_cy': float(target_cy),
                }
            pos = _peek_card_positions[card.card_id]
            if _pds['card'] is card:
                pos['target_cx'] = float(_mx + _pds['offset_x'])
                pos['target_cy'] = float(_my + _pds['offset_y'])
            else:
                pos['target_cx'] = float(target_cx)
                pos['target_cy'] = float(target_cy)

            pos['vx'] += (pos['target_cx'] - pos['cx']) * SPRING_STIFFNESS
            pos['vy'] += (pos['target_cy'] - pos['cy']) * SPRING_STIFFNESS
            pos['vx'] *= SPRING_DAMPING
            pos['vy'] *= SPRING_DAMPING
            if abs(pos['vx']) < 0.1: pos['vx'] = 0
            if abs(pos['vy']) < 0.1: pos['vy'] = 0
            pos['cx'] += pos['vx']
            pos['cy'] += pos['vy']

    _mini_shadow = pygame.transform.smoothscale(cardShadow, (MINI_CW, MINI_CH))
    _mini_shadow.set_alpha(180)
    _dragged_draw = None

    for row_idx, row_cards in enumerate(peek_rows):
        n = len(row_cards)
        for col_idx, card in enumerate(row_cards):
            t = col_idx / (n - 1) if n > 1 else 0.5
            arc_angle = (t - 0.5) * -PEEK_ANGLE_RANGE
            pos = _peek_card_positions[card.card_id]
            draw_cx, draw_cy = int(pos['cx']), int(pos['cy'])
            is_dragging_this = (_pds['card'] is card)
            draw_angle = 0.0 if is_dragging_this else arc_angle
            not_in_deck = show_remaining_overlay and card.card_id not in _deck_ids

            mini_base, mini_img = get_peek_card_images(card, MINI_CW, MINI_CH)

            if is_dragging_this:
                rotated_base = pygame.transform.rotate(mini_base, 0)
                rotated_img  = pygame.transform.rotate(mini_img,  0)
                shadow_surf  = pygame.transform.rotate(_mini_shadow, 0) if not_in_deck else None
                rect_b = rotated_base.get_rect(center=(draw_cx, draw_cy))
                rect_i = rotated_img.get_rect(center=(draw_cx, draw_cy))
                _dragged_draw = (rotated_base, rect_b, rotated_img, rect_i, not_in_deck, shadow_surf, rect_i)
            else:
                rotated_base, rotated_img, rotated_shadow = get_peek_rotated(
                    mini_base, mini_img, draw_angle, card.card_id, not_in_deck, _mini_shadow
                )
                rect_b = rotated_base.get_rect(center=(draw_cx, draw_cy))
                rect_i = rotated_img.get_rect(center=(draw_cx, draw_cy))
                screen.blit(rotated_base, rect_b.topleft)
                screen.blit(rotated_img,  rect_i.topleft)
                if not_in_deck and rotated_shadow:
                    screen.blit(rotated_shadow, rect_i.topleft)

            if rect_i.collidepoint(_mx, _my):
                mouse_display = cursor_hover
            if _mb[0] and _pds['card'] is None and rect_i.collidepoint(_mx, _my):
                _pds['card']        = card
                _pds['row']         = row_idx
                _pds['offset_x']    = draw_cx - _mx
                _pds['offset_y']    = draw_cy - _my
                _pds['drag_start']  = (_mx, _my)
                _pds['was_dragged'] = False

    if _dragged_draw:
        rb, rect_b, ri, rect_i, has_shadow, rs, rect_s = _dragged_draw
        screen.blit(rb, rect_b.topleft)
        screen.blit(ri, rect_i.topleft)
        if has_shadow and rs:
            screen.blit(rs, rect_s.topleft)

    stats = get_peek_stats(source_deck)
    stat_positions = [
        (stats['aces'],    WIDTH/6.9,  HEIGHT/1.9),
        (stats['faces'],   WIDTH/5.4,  HEIGHT/1.9),
        (stats['numbers'], WIDTH/4.4,  HEIGHT/1.9),
        (stats['Spades'],   WIDTH/6.28, HEIGHT/1.5),
        (stats['Hearts'],   WIDTH/4.77, HEIGHT/1.5),
        (stats['Clubs'],    WIDTH/6.28, HEIGHT/1.285),
        (stats['Diamonds'], WIDTH/4.77, HEIGHT/1.285),
        (stats['Ace'],     WIDTH/3.1,  HEIGHT/4.45),
        (stats['King'],    WIDTH/3.1,  HEIGHT/3.69),
        (stats['Queen'],   WIDTH/3.1,  HEIGHT/3.14),
        (stats['Jack'],    WIDTH/3.1,  HEIGHT/2.735),
        (stats['Ten'],     WIDTH/3.1,  HEIGHT/2.424),
        (stats['Nine'],    WIDTH/3.1,  HEIGHT/2.175),
        (stats['Eight'],   WIDTH/3.1,  HEIGHT/1.966),
        (stats['Seven'],   WIDTH/3.1,  HEIGHT/1.799),
        (stats['Six'],     WIDTH/3.1,  HEIGHT/1.658),
        (stats['Five'],    WIDTH/3.1,  HEIGHT/1.534),
        (stats['Four'],    WIDTH/3.1,  HEIGHT/1.435),
        (stats['Three'],   WIDTH/3.1,  HEIGHT/1.343),
        (stats['Two'],     WIDTH/3.1,  HEIGHT/1.264),
    ]
    for value, sx, sy in stat_positions:
        text, _ = PixelFontS.render(str(value), white)
        text_rect = text.get_rect(center=(sx, sy))
        screen.blit(text, text_rect)
    
_peek_rotated_cache = {}

def get_peek_rotated(mini_base, mini_img, angle, card_id, not_in_deck, mini_shadow):
    rounded_angle = round(angle * 2) / 2
    cache_key = (card_id, rounded_angle)
    if cache_key not in _peek_rotated_cache:
        rotated_base = pygame.transform.rotate(mini_base, rounded_angle)
        rotated_img  = pygame.transform.rotate(mini_img,  rounded_angle)
        rotated_shadow = pygame.transform.rotate(mini_shadow, rounded_angle) if not_in_deck else None
        _peek_rotated_cache[cache_key] = (rotated_base, rotated_img, rotated_shadow)
    return _peek_rotated_cache[cache_key]
def animateGlitch():
    global glitch_index 
    global glitchimage
    glitch_index += 0.15
    if glitch_index >= len(glitchframes):
        glitch_index = 0 
    glitchimage = glitchframes[int(glitch_index)]
    
dev_command_bar_active = False
dev_command_input = ""
dev_command_history = []
dev_command_output_lines = [] 
dev_awaiting_input = False  
dev_current_command = None 
dev_input_prompt = "" 
dev_multi_step_data = {}  
shop_down = False
card_play_counts = {} 
def shopAnimaton():
    global shop_down
    if GameState not in ("Shop", "TarotPack", "SpectralPack", "ShadowPack", "StandardPack") and not shop_down:
        shopAnimation.current_frame = 0
    if GameState in ("Shop", "TarotPack", "SpectralPack", "ShadowPack", "StandardPack"):
        if shop_down == False:
            if shopAnimation.current_frame >= 66:
                shop_down = True
            else:
                shopAnimation.animate()
        else:
            screen.blit(shopAnimation.cached_frames[66], (shopAnimation.xpos, shopAnimation.ypos))
    else:
        if shopAnimation.current_frame == 0:  
            shop_down = False
        if shop_down:
            shopAnimation.animate()
BLIND_INVISIBLE = False
NOBLIND = load_image_safe(os.path.join(BLINDS_DIR, "NOBLIND.png"))
class Blind:
    def __init__(self, name, image, x, y, state):
        self.name = name
        self.image = image
        self.imageS = pygame.transform.scale(self.image, (HEIGHT/10, HEIGHT/10))
        
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
showdown_blinds = []
for root, dirs, files in os.walk(BLINDS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            blind_name_raw = os.path.splitext(filename)[0]
            blind_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', blind_name_raw)
            blind_name = blind_name.title()
            image = pygame.transform.scale(load_image_safe(filepath), (HEIGHT/8, HEIGHT/8))
            if "Small" in blind_name:
                small_blind = Blind(blind_name, image, -150, -150, "small")
            elif "Big" in blind_name:
                big_blind = Blind(blind_name, image, -150, -150, "big")
            elif "_" in blind_name:
                blind_name = blind_name.replace("_", "")
                blind_obj = Blind(blind_name, image, -150, -150, "showdown")
                showdown_blinds.append(blind_obj)
            else:
                blind_obj = Blind(blind_name, image, -150, -150, "boss")
                boss_blinds.append(blind_obj)
boss_blind = random.choice(boss_blinds)
showdown_blind = random.choice(showdown_blinds)
current_blind = None
def calculate_target_score(ante, round_num):
    if ante > 8:
        base_score = math.pow(ANTE_SCALING[8] * (1.6 + (0.75 * (ante - 8))), (ante - 8))
    else:
        base_score = ANTE_SCALING[ante]
    multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 4.0}
    if current_blind.name == "The Ramp":
        return int(base_score * multipliers[4])
    else:
        return int(base_score * multipliers[round_num % 3 if round_num % 3 != 0 else 3])
conquistadorSplashEffect = False
conquistadorSplashTimer  = 0
def conquistadorSplash():
    global conquistadorSplashTimer
    conquistadorSplashTimer -= 1
    if conquistadorSplashTimer <= 0:
        conquistadorSplashEffect = False
    else:
        screen.blit(conquistador_img, (0,0))

def get_current_blind():
    global round_num, ante, current_blind, target_score, blind_reward, victory, total_score, GameState, boss_blind
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
            if ante % 8 == 0:
                if showdown_blinds:
                    current_blind = showdown_blinds
                    blind_reward = 5
                    current_blind_type = "showdown"
            if boss_blinds:
                current_blind = boss_blind
                blind_reward = 5
                current_blind_type = "boss"
        if current_blind:
            current_blind.target_x = BLIND_X
            current_blind.target_y = BLIND_Y
            if GameState in ("Shop", "Cashing", "Blinds"):
                current_blind.target_x = -500
                current_blind.target_y = -500
            current_blind.vx = 0
            current_blind.vy = 0
            current_blind.score_required = calculate_target_score(ante, round_num)
            target_score = current_blind.score_required
            victory = False
            total_score = 0
    return current_blind
def set_boss_blind(boss_name):
    global current_blind, target_score, blind_reward
    for boss in boss_blinds:
        if boss.name.lower() == boss_name.lower():
            current_blind = boss
            current_blind.target_x = BLIND_X
            current_blind.target_y = BLIND_Y
            current_blind.vx = 0
            current_blind.vy = 0
            current_blind.score_required = calculate_target_score(ante, round_num)
            target_score = current_blind.score_required
            blind_reward = 5
            current_blind.blind_type = "boss"
            return True
    return False
def advance_to_next_blind():
    global visible_round_num, totalReward, round_num, ante, hands, discards, current_score, money, blind_reward, GameState, boss_blind, current_blind, jonkler_sphere_active, jonkler_sphere_clicked
    if round_num % 3 == 0:
        ante += 1
        boss_blind = random.choice(boss_blinds)
        showdown_blind = random.choice(showdown_blinds)
        current_blind = None
    round_num += 1
    visible_round_num += 1
    current_score = 0
    totalReward += hands + blind_reward
    hands = max_hand
    discards = max_discard
    jonkler_sphere_active = False
    jonkler_sphere_clicked = False
    reset_deck_for_new_round()
    
def check_blind_defeated():
    global blind_defeated, current_score, GameState
    if current_blind and total_score >= target_score:
        blind_defeated = True
        return True
    else:
        return False
def get_file_names(folder):
    names = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            names.append(filename[:-4]) 
    return names

def get_file_contents(folder, names):
    contents = {}
    for name in names:
        with open(os.path.join(folder, name + ".txt"), "r") as f:
            contents[name] = f.read()
    return contents

joker_folder = os.path.join(TEXT_PATH, "Jokers")
jokerDescription = get_file_contents(joker_folder, get_file_names(joker_folder))
from JokerEffects import JOKER_REGISTRY
class Joker:
    card_id_counter = 0
    def __init__(self, image, rarity, name, slot=None, state="hand", debuff=False, enhancement=None, edition=None, seal=None):
        self.image = image
        self.rarity = rarity
        self.scale= 1.0
        self.rotation_speed = 0
        self.scaling_delay = 0
        self.is_debuffed = debuff
        self.debuff_assigned = False
        self.enhancement = enhancement
        self.edition = edition
        self.seal = seal
        self.scaling = False
        self.growing = False
        self.scaling_done = False
        self.scoring_complete = False
        self.card_id = Card.card_id_counter
        self.card_id_counter += 1
        self.name = name
        self.rect = image.get_rect()
        self.state = state
        self.slot = slot
        self.vx = 0
        self.vy = 0
        self.x = WIDTH/1.6
        self.target_x = WIDTH/1.6
        self.scoring_x = 0
        self.scoring_y = 0
        self.y = HEIGHT/1.565
        self.angle = 0
        self.target_y = HEIGHT/1.565
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
        self.scoring_animating = False
        self.description = JOKER_REGISTRY.get(self.name, {}).get('description', "")
        self.idx = 0
        prices = {'C': 3, 'U': 6, 'R': 8, 'L': 20, 'S': 15}
        self.price = prices.get(self.rarity, 0) 
        self.sound = jokerSound.get(self.name)

    def playsound(self, loop):   
            if self.sound:
                if loop:
                    self.sound.play(-1)
                else:
                    self.sound.play(0)

        
        
           
    def get_description(self):
        
        desc = self.description
        if self.name == "Wet Floor Joker":
            desc = desc.replace("{value}", str(JokerEffects.wetFloorValue))
        elif self.name == "Ptsd Joker":
            desc = desc.replace("{value}", str(1 + (round(JokerEffects.last_hand_counter, 1))))
        elif self.name == "Dead Frog":
            desc = desc.replace("{value}", str(round(20 * JokerEffects.FrogCounter)))
        elif self.name == "Pool Table":
            desc = desc.replace("{value}", str(round(JokerEffects.poolMoney,1)))
        elif self.name == "Skip Joker":
            desc = desc.replace("{value}", str(round(JokerEffects.skipMult,2)))
        elif self.name == "Exponent Joker":
            desc = desc.replace("{value}", str(round(JokerEffects.exponentJoker,1)))
        elif self.name == "Rules Card":
            if RulesHand is None:
                desc = "[yellow]5$[/yellow] For Playing a specified hand. Buy to view hand."
            else:
                desc = desc.replace("{value}", str(RulesHand))
        elif self.name == "Lucky Joker":
            desc = desc.replace("{value}", str(JokerEffects.luck))
        elif self.name == "Lost King":
            desc = desc.replace("{value}", str(JokerEffects.BunsKingScale['TimesMult']))
            desc = desc.replace("{value2}", str(JokerEffects.BunsKingScale['AddMult']))
            desc = desc.replace("{value3}", str(JokerEffects.BunsKingScale['AddChips']))

        desc = desc.replace("{break}", "\n")
        desc = desc.replace("[indent]", "    ")
        desc = desc.replace("[indent2]", "        ")
        return desc
    def update(self):
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
                self.scaling_delay += 10 * scoreSpeed
            else:
                if not self.growing:
                    if self.scale > 0.51:
                        self.scale -= scoreSpeed
                        self.rotation_speed = 5
                    else:
                        self.scale = 0.5
                        self.rotation_speed = -5
                        self.growing = True
                else:
                    if self.scale < 1.0:
                        self.scale += scoreSpeed
                    else:
                        self.scale = 1.0
                        self.rotation_speed = 0
                        self.scaling = False
                        self.growing = False
                        self.scaling_done = True
                        self.scoring_animating = False
                        self.scaling_delay = 10
                        self.angle = 0
        self.angle += self.rotation_speed

Common_Jokers = []
Uncommon_Jokers = []
Rare_Jokers = []
Legendary_Jokers = []
All_Jokers = []
Active_Jokers = []
Shop_Cards = []
All_Jokers_Name = []
rare_joker = False
for root, dirs, files in os.walk(JOKERS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            Joker_name_raw = os.path.splitext(filename)[0]
            rarity = Joker_name_raw[-1]
            Joker_name_raw = Joker_name_raw[:-1]
            Joker_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', Joker_name_raw)
            Joker_name = Joker_name.title()
            image = pygame.transform.scale(load_image_safe(filepath), (HEIGHT/8, HEIGHT/5.82))
            joker = Joker(image, rarity, Joker_name)
            if rarity == 'C':
                Common_Jokers.append(joker)
            elif rarity == 'U':
                Uncommon_Jokers.append(joker)
            elif rarity == 'R':
                Rare_Jokers.append(joker)
            elif rarity == 'L':
                Legendary_Jokers.append(joker)
            All_Jokers.append(joker)
            
for jokername in All_Jokers:
    All_Jokers_Name.append(jokername.name)

def draw_jokers(surface, cards, center_x, center_y, spread=20):
    
    n = len(cards)
    if n == 0:
        return
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2.25
    for i, joker in enumerate(cards):
        joker.spread = spread
        t = i / (n - 1) if n > 1 else 0.5
        target_x = start_x + i * spread
        target_y = center_y
        if joker.state == "selected":
            target_y -= 40
        joker.target_x = target_x
        joker.target_y = target_y
        angle = joker.angle
        scaled_w = int(joker.image.get_width() * joker.scale)
        scaled_h = int(joker.image.get_height() * joker.scale)
        scaled_img = pygame.transform.smoothscale(joker.image, (scaled_w, scaled_h))
        try:
            if joker.is_debuffed:
                scaled_overlay = pygame.transform.smoothscale(Debuff_img, (scaled_w, scaled_h))
                scaled_img = scaled_img.copy()
                scaled_img.blit(scaled_overlay, (0, 0))
            match card.edition:
                case "Foil":
                    scaled_overlay = pygame.transform.smoothscale(Foil_img, (scaled_w, scaled_h))
                    scaled_img = scaled_img.copy()
                    scaled_img.blit(scaled_overlay, (0, 0))
                case "Holographic":
                    scaled_overlay = pygame.transform.smoothscale(Holo_img, (scaled_w, scaled_h))
                    scaled_img = scaled_img.copy()
                    scaled_img.blit(scaled_overlay, (0, 0))
                case "Polychrome":
                    scaled_overlay = pygame.transform.smoothscale(Poly_img, (scaled_w, scaled_h))
                    scaled_img = scaled_img.copy()
                    scaled_img.blit(scaled_overlay, (0, 0))
        except AttributeError:
            a = 2
        finally:
            rotated = pygame.transform.rotate(scaled_img, angle)
            rect = rotated.get_rect(center=(joker.x, joker.y))
            surface.blit(rotated, rect.topleft)
            joker.rect = rect
            active_hover_rects.append(joker.rect)

class Consumable:
    card_id_counter = 0
    def __init__(self, image, name, slot=None, state="hand", edition=None):
        self.image = image
        self.scale= 1.0
        self.rotation_speed = 0
        self.scaling_delay = 0
        self.edition = edition
        self.scaling = False
        self.growing = False
        self.scaling_done = False
        self.scoring_complete = False
        self.card_id = Card.card_id_counter
        self.card_id_counter += 1
        self.name = name
        self.rect = image.get_rect()
        self.state = state
        self.slot = slot
        self.vx = 0
        self.vy = 0
        self.soulx = 0
        self.souly = 0
        self.x = WIDTH/1.6
        self.target_x = WIDTH/1.6
        self.scoring_x = 0
        self.scoring_y = 0
        self.y = HEIGHT/1.565
        self.angle = 0
        self.target_y = HEIGHT/1.565
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
        self.scoring_animating = False
        self.idx = 0
        self.price = 3
    def update(self):
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
                self.scaling_delay += 10 * scoreSpeed
            else:
                if not self.growing:
                    if self.scale > 0.51:
                        self.scale -= 0.1
                        self.rotation_speed = 5
                    else:
                        self.scale = 0.5
                        self.rotation_speed = -5
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
        self.angle += self.rotation_speed

TarotCards = []
ShadowCards = []
SpectralCards = []
Held_Consumables = []
maxConsCount = 2
for root, dirs, files in os.walk(CONS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            Cons_name_raw = filename
            Cons_name_raw = Cons_name_raw.replace(".png", "")
            Cons_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', Cons_name_raw)
            Cons_name = Cons_name.title()
            image = pygame.transform.scale(load_image_safe(filepath), (HEIGHT/8, HEIGHT/5.82))
            consumable = Consumable(image, Cons_name)
            if "TarotCards" in filepath:
                if "SoulOverlay" in filepath:
                    SoulOverlay = image
                elif "SoulShadow" in filepath:
                    SoulShadow = image
                else:
                    TarotCards.append(consumable)
            elif "ShadowCards" in filepath:
                ShadowCards.append(consumable)
            elif "SpectralCards" in filepath:
                SpectralCards.append(consumable)

def draw_consumables(surface, cards, center_x, center_y, spread=20):
    n = len(cards)
    if n == 0:
        return
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2.25
    for i, cons in enumerate(cards):
        cons.spread = spread
        t = i / (n - 1) if n > 1 else 0.5
        target_x = start_x + i * spread
        target_y = center_y
        if cons.state == "selected":
            target_y -= 40
        cons.target_x = target_x
        cons.target_y = target_y
        angle = cons.angle
        scaled_w = int(cons.image.get_width() * cons.scale)
        scaled_h = int(cons.image.get_height() * cons.scale)
        scaled_img = pygame.transform.smoothscale(cons.image, (scaled_w, scaled_h))
        rotated = pygame.transform.rotate(scaled_img, angle)
        rect = rotated.get_rect(center=(cons.x, cons.y))
        surface.blit(rotated, rect.topleft)
        cons.rect = rect
        cons.soulx, cons.souly = rect.topleft
        active_hover_rects.append(cons.rect)
        if abs(cons.vx) < 50:
            cons.soulx -= cons.vx * 2
        if abs(cons.vy) < 50:
            cons.souly -= cons.vy * 2
        if cons.name == "The Soul":
            drift = math.sin(pygame.time.get_ticks() / 500) * 5
            screen.blit(SoulShadow, (cons.soulx, cons.souly + drift))
            screen.blit(SoulOverlay, (cons.soulx, cons.souly + drift))

class Cardpack:
    card_id_counter = 0
    def __init__(self, image, name, size, slot=None, state="hand"):
        self.image = image
        self.scale= 1.0
        self.rotation_speed = 0
        self.scaling_delay = 0
        self.scaling = False
        self.growing = False
        self.scaling_done = False
        self.scoring_complete = False
        self.card_id = Card.card_id_counter
        self.card_id_counter += 1
        self.name = name
        self.rect = image.get_rect()
        self.state = state
        self.slot = slot
        self.vx = 0
        self.vy = 0
        self.x = WIDTH/1.6
        self.target_x = WIDTH/1.6
        self.scoring_x = 0
        self.scoring_y = 0
        self.y = HEIGHT/1.565
        self.angle = 0
        self.target_y = HEIGHT/1.565
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.was_dragged = False
        self.scoring_animating = False
        self.idx = 0
        self.price = 3
        self.cardNum = 3
        self.selection = 1
        if size == "Jumbo":
            self.price = 5
            self.cardNum = 5
            self.selection = 1
        elif size == "Mega":
            self.price = 8
            self.cardNum = 5
            self.selection = 2
    def update(self):
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
                self.scaling_delay += 10 * scoreSpeed
            else:
                if not self.growing:
                    if self.scale > 0.51:
                        self.scale -= 0.1
                        self.rotation_speed = 5
                    else:
                        self.scale = 0.5
                        self.rotation_speed = -5
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
        self.angle += self.rotation_speed

def draw_cardpacks(surface, cards, center_x, center_y, spread=20):
    n = len(cards)
    if n == 0:
        return
    total_width = (n - 1) * spread + 80
    start_x = center_x - total_width / 2.25
    for i, pack in enumerate(cards):
        pack.spread = spread
        t = i / (n - 1) if n > 1 else 0.5
        target_x = start_x + i * spread
        target_y = center_y
        if pack.state == "selected":
            target_y -= 40
        pack.target_x = target_x
        pack.target_y = target_y
        angle = pack.angle
        scaled_w = int(pack.image.get_width() * pack.scale)
        scaled_h = int(pack.image.get_height() * pack.scale)
        scaled_img = pygame.transform.smoothscale(pack.image, (scaled_w, scaled_h))
        rotated = pygame.transform.rotate(scaled_img, angle)
        rect = rotated.get_rect(center=(pack.x, pack.y))
        surface.blit(rotated, rect.topleft)
        pack.rect = rect

StandardPacks = []
TarotPacks = []
SpectralPacks = []
ShadowPacks = []
ShopPacks = []
PackCards = []
for root, dirs, files in os.walk(PACKS_DIR):
    for filename in files:
        if filename.endswith(".png"):
            filepath = os.path.join(root, filename)
            Pack_name_raw = filename
            Pack_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', Pack_name_raw)
            Pack_name = Pack_name.title()
            size = "Normal"
            if "Jumbo" in Pack_name:
                size = "Jumbo"
                Pack_name = Pack_name.replace("Jumbo", "")
            elif "Mega" in Pack_name:
                size = "Mega"
                Pack_name = Pack_name.replace("Mega", "")
            image = pygame.transform.scale(load_image_safe(filepath), (HEIGHT/8, HEIGHT/5.82))
            cardpack = Cardpack(image, Pack_name, size)
            if "Standard" in Pack_name:
                StandardPacks.append(cardpack)
            elif "Shadow" in Pack_name:
                ShadowPacks.append(cardpack)
            elif "Spectral" in Pack_name:
                SpectralPacks.append(cardpack)
            elif "Tarot" in Pack_name:
                TarotPacks.append(cardpack)

def change_notation(number):
    if number > 999999:
        saved_number = number
        place = 0
        while saved_number > 9:
            saved_number /= 10
            saved_number = round(saved_number, 2)
            place += 1
        number = f"{saved_number}e{place}"
    return number

def wrap_text(text, font, max_width):
    scale = font.scale
    words = text.split(' ')
    lines, current_line, current_w = [], [], 0
    for word in words:
        w = _measure_width(word + ' ', scale)
        if current_w + w <= max_width:
            current_line.append(word)
            current_w += w
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line, current_w = [word], w
            else:
                lines.append(word)
    if current_line:
        lines.append(' '.join(current_line))
    return lines

draw_fox = False
def detect_hand(cards):
    n = len(cards)
    if n == 0:
        return "", []
    s = len([c for c in cards if c.enhancement == "Glitched"])
    values = sorted([c.value for c in cards if c.enhancement != "Glitched"])
    suits = [c.suit for c in cards if c.enhancement not in ("Glitched", "Wild")]
    value_counts = Counter(values)
    suits_counts = Counter(suits)
    if s == 0:
        is_flush = n == 5 and 1 == len(suits_counts)
        is_straight = n == 5 and all(values[i] - values[i-1] == 1 for i in range(1,5))
    else:
        is_flush, is_straight = False, False
    is_glitched = s == 5
    if is_glitched:
        contributing = selected_cards.copy()
        return "Huh of a What", contributing
    if values == [2, 3, 4, 5, 14]:
        is_straight = True
        values = [1, 2, 3, 4, 5]
    contributing = []
    if is_flush and 5 in value_counts.values():
        contributing = selected_cards.copy()
        return "Flush Five", contributing
    elif is_flush and sorted(value_counts.values()) == [2, 3]:
        contributing = selected_cards.copy()
        return "Flush House", contributing
    elif 5 in value_counts.values():
        contributing = selected_cards.copy()
        return "Five of a Kind", contributing
    elif is_flush and is_straight and values[-1] == 14:
        contributing = selected_cards.copy()
        return "Royal Flush", contributing
    elif is_flush and is_straight:
        contributing = selected_cards.copy()
        return "Straight Flush", contributing
    elif 4 in value_counts.values():
        four_value = [val for val, count in value_counts.items() if count == 4][0]
        contributing = [c for c in cards if c.value == four_value]
        for c in cards:
            if c.enhancement == "Glitched" and c not in contributing:
                contributing.append(c)
        return "Four of a Kind", contributing
    elif sorted(value_counts.values()) == [2, 3]:
        contributing = selected_cards.copy()
        return "Full House", contributing
    elif is_flush:
        contributing = selected_cards.copy()
        return "Flush", contributing
    elif is_straight:
        contributing = selected_cards.copy()
        return "Straight", contributing
    elif 3 in value_counts.values():
        three_value = [val for val, count in value_counts.items() if count == 3][0]
        contributing = [c for c in cards if c.value == three_value]
        for c in cards:
            if c.enhancement == "Glitched" and c not in contributing:
                contributing.append(c)
        return "Three of a Kind", contributing
    elif list(value_counts.values()).count(2) == 2:
        pair_values = [val for val, count in value_counts.items() if count == 2]
        contributing = [c for c in cards if c.value in pair_values]
        for c in cards:
            if c.enhancement == "Glitched" and c not in contributing:
                contributing.append(c)
        return "Two Pair", contributing
    elif 2 in value_counts.values():
        pair_value = [val for val, count in value_counts.items() if count == 2][0]
        contributing = [c for c in cards if c.value == pair_value]
        for c in cards:
            if c.enhancement == "Glitched" and c not in contributing:
                contributing.append(c)
        return "Pair", contributing
    else:
        if s < len(cards):
            high_value = max(values)
        else:
            high_value = 0
        contributing = [c for c in cards if c.value == high_value]
        for c in cards:
            if c.enhancement == "Glitched" and c not in contributing:
                contributing.append(c)
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
sort_mode == "rank"
startGame = False

def sort_hand():
    global hand, sort_mode
    if sort_mode == "rank":
        hand.sort(key=lambda c: c.value, reverse=True)
    elif sort_mode == "suit":
        suit_order = {"Spades": 4, "Hearts": 3, "Diamonds": 2, "Clubs": 1, "Glitched": 0}
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

def get_selected_Shop_Cards(joker):
    if joker.state == "selected":
        return (joker.x, joker.y)
    else:
        return (-100, -100)

def reset_game_variables():
    global perm_deck, deck, hand, Active_Jokers, Held_Consumables, MaxConsCount
    global max_handsize, max_hand, max_discard, hands, discards
    global scored, scoring_in_progress, calculating, discarding
    global round_num, ante, money, blind_defeated, victory, current_blind, boss_blind, boss_blinds
    global target_score, contributing, BLIND_X, BLIND_Y
    global total_score, saved_total_score, is_straight, is_flush
    global ShopCount, totalReward, joker_manager
    global shopJokerSelected, ActiveJokerSelected, locked_hands, locked_cards, unlocked_hands
    global handsize, chips, mult, current_score
    global round_score, scored_counter, total_scoring_count
    global DRAG_THRESHOLD, calc_progress
    global saved_base_chips, saved_base_mult, saved_level
    global blind_reward, saved_hand, sort_mode
    global current_scoring_card, discard_timer, mouth_triggered
    global GameState, maxJokerCount, rerollCost
    global highest_hand, most_played, cards_played
    global cards_discarded, purchases, rerolls, cards_found, lastFool
    global hand_plays, Hand_levels, Hand_Mult, Hand_Chips
    perm_deck.clear()
    perm_deck = copy.deepcopy(default_deck)
    deck.clear()
    deck = perm_deck.copy()
    for c in deck:
        print(c.enhancement if c.enhancement != None else "")
    hand.clear()
    Active_Jokers.clear()
    Held_Consumables.clear()

    locked_hands = ["Five of a Kind", "Flush House", "Flush Five", "Huh of a What"]
    unlocked_hands = ["High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"]
    locked_cards = ["Glitch", "King Shadow", "The Reaper", "Tag Team"]

    max_handsize = 8
    max_hand = 4
    max_discard = 4
    hands = max_hand
    discards = max_discard
    scored = False
    scoring_in_progress = False
    calculating = False
    discarding = False
    round_num = 1
    visible_round_num = 1
    ante = 1
    money = 4
    blind_defeated = False
    victory = False
    target_score = 300
    contributing = []
    BLIND_X = -500
    BLIND_Y = -500
    total_score = 0
    saved_total_score = 0
    is_straight = False
    is_flush = False
    ShopCount = 2
    totalReward = 0
    joker_manager = None
    shopJokerSelected = False
    ActiveJokerSelected = False
    ActiveJokerSelected = False
    max_handsize = 8
    handsize = max_handsize
    chips = 0
    mult = 0
    current_score = 0
    round_score = 0
    scored_counter = 0
    total_scoring_count = 0
    max_hand = 4
    MaxConsCount = 2
    max_discard = 4
    hands = max_hand
    discards = max_discard
    DRAG_THRESHOLD = 20
    calc_progress = 0.0
    saved_base_chips  = 0
    saved_base_mult = 0
    saved_level = 0
    blind_reward = 0
    saved_hand = None
    sort_mode = "rank"
    current_scoring_card = None
    discard_timer = 0
    mouth_triggered = False
    GameState = None
    maxJokerCount = 5
    rerollCost = 3
    highest_hand = 0
    most_played = 0
    cards_played = 0
    cards_discarded = 0
    purchases = 0
    rerolls = 0
    cards_found = 0
    lastFool = None

    JokerEffects.reset_joker_variables()

    boss_blind = random.choice(boss_blinds)
    current_blind = None

    hand_plays = {
        "High Card": 0,
        "Pair": 0,
        "Two Pair": 0,
        "Three of a Kind": 0,
        "Straight": 0,
        "Flush": 0,
        "Full House": 0,
        "Four of a Kind": 0,
        "Straight Flush": 0,
        "Five of a Kind": 0,
        "Flush House": 0,
        "Flush Five": 0,
        "Huh of a What": 0,
        }
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
        "Huh of a What": 1,
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
        "Huh of a What": 10,
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
        "Huh of a What": 100,
        }

def get_card_limit(name):
    match name:
        case "Chariot":
            return 2
        case "Death":
            return 2
        case "Devil":
            return 2
        case "Empress":
            return 2
        case "Hanged Man":
            return 2
        case "Hierophant":
            return 2
        case "Justice":
            return 1
        case "Lovers":
            return 1
        case "Magician":
            return 2
        case "World":
            return 3
        case "Star":
            return 3
        case "Sun":
            return 3
        case "Moon":
            return 3
        case "Strength":
            return 2
        case "Tower":
            return 1
        case "Aura":
            return 1
        case "Deja Vu":
            return 1
        case "Talisman":
            return 1
        case "Trance":
            return 1
        case "Medium":
            return 1
        case "Cryptid":
            return 1
        case _:
            return 6

def get_spectral_effect(name):
    global money, lastFool, selected_cards, perm_deck, hand, deck, Active_Jokers, GameState, PackCards, max_handsize
    _peek_card_image_cache.clear()
    if name == "Ankh":
        if len(Active_Jokers) > 0:
            copied = random.choice(Active_Jokers)
            Active_Jokers.clear()
            Active_Jokers.append(copied)
            copied = Joker(copied.image, copied.rarity, copied.name, edition=copied.edition)
            Active_Jokers.append(copied)
    if name == "Aura":
        for card in selected_cards:
            edit = random.randint(base_chance, 100)
            if edit < 40:
                edit = "Foil"
            elif edit < 80:
                edit = "Holographic"
            else:
                edit = "Polychrome"
            card.edition = edit
    if name == "Cryptid":
        for card in selected_cards:
            newcard = Card(card.rank, card.suit, card.image, enhancement=card.enhancement, edition=card.edition, seal=card.seal)
            newcard2 = Card(card.rank, card.suit, card.image, enhancement=card.enhancement, edition=card.edition, seal=card.seal)
            if GameState == "Playing":
                newcard.slot = len(hand) + 1
                newcard2.slot = len(hand) + 2
                hand.append(newcard)
                hand.append(newcard2)
            else:
                newcard.slot = len(PackCards) + 1
                newcard2.slot = len(PackCards) + 2
                PackCards.append(newcard)
                PackCards.append(newcard2)
            perm_deck.append(newcard)
            perm_deck.append(newcard2)
    if name == "Deja Vu":
        for card in selected_cards:
            card.seal = "Red"
    if name == "Ectoplasm":
        max_handsize -= 1
        for i in range(len(Active_Jokers)):
            negative = random.choice(Active_Jokers)
            if negative.edition == None:
                break
        if negative.edition == None:
            negative.edition = "Negative"
    if name == "Familiar":
        if GameState == "Playing":
            rand1 = hand.pop(randindex := random.randrange(len(hand)))
            for i in range(3):
                randrank = random.choice(FACES_WRITTEN)
                randsuit = random.choice(SUITS)
                num = random.randint(1 , 100)
                if num > 87:
                    enhancement = "Bonus"
                elif num > 75:
                    enhancement = "Glass"
                elif num > 63:
                    enhancement = "Gold"
                elif num > 50:
                    enhancement = "Lucky"
                elif num > 38:
                    enhancement = "Mult"
                elif num > 25:
                    enhancement = "Steel"
                elif num > 13:
                    enhancement = "Glitched"
                filename = f"{randrank}Of{randsuit}.png"
                filepath = os.path.join(SUITS_DIR, randsuit, filename)
                if enhancement == "Glitched":
                    filename = f"GlitchBaseSpriteSheet.png"
                    filepath = os.path.join(SPRITESHEETS_DIR, filename)
                image = pygame.image.load(filepath).convert_alpha()
                newcard = Card(randrank, randsuit, image, slot=len(hand) + 1 , enhancement=enhancement)
                newcard.refresh_image()
                hand.append(newcard)
                perm_deck.append(newcard)
        else:
            rand1 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            for i in range(3):
                randrank = random.choice(FACES_WRITTEN)
                randsuit = random.choice(SUITS)
                num = random.randint(1 , 100)
                if num > 87:
                    enhancement = "Bonus"
                elif num > 75:
                    enhancement = "Glass"
                elif num > 63:
                    enhancement = "Gold"
                elif num > 50:
                    enhancement = "Lucky"
                elif num > 38:
                    enhancement = "Mult"
                elif num > 25:
                    enhancement = "Steel"
                elif num > 13:
                    enhancement = "Glitched"
                filename = f"{randrank}Of{randsuit}.png"
                filepath = os.path.join(SUITS_DIR, randsuit, filename)
                if enhancement == "Glitched":
                    filename = f"GlitchBaseSpriteSheet.png"
                    filepath = os.path.join(SPRITESHEETS_DIR, filename)
                image = pygame.image.load(filepath).convert_alpha()
                newcard = Card(randrank, randsuit, image, enhancement=enhancement)
                newcard.refresh_image()
                PackCards.append(newcard)
                perm_deck.append(newcard)
    if name == "Grim":
        if GameState == "Playing":
            rand1 = hand.pop(randindex := random.randrange(len(hand)))
            randrank = "Ace"
            for i in range(2):
                randsuit = random.choice(SUITS)
                num = random.randint(1 , 100)
                if num > 87:
                    enhancement = "Bonus"
                elif num > 75:
                    enhancement = "Glass"
                elif num > 63:
                    enhancement = "Gold"
                elif num > 50:
                    enhancement = "Lucky"
                elif num > 38:
                    enhancement = "Mult"
                elif num > 25:
                    enhancement = "Steel"
                elif num > 13:
                    enhancement = "Glitched"
                filename = f"{randrank}Of{randsuit}.png"
                filepath = os.path.join(SUITS_DIR, randsuit, filename)
                if enhancement == "Glitched":
                    filename = f"GlitchBaseSpriteSheet.png"
                    filepath = os.path.join(SPRITESHEETS_DIR, filename)
                image = pygame.image.load(filepath).convert_alpha()
                newcard = Card(randrank, randsuit, image, slot=len(hand) + 1 , enhancement=enhancement)
                newcard.refresh_image()
                hand.append(newcard)
                perm_deck.append(newcard)
        else:
            rand1 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            for i in range(2):
                randrank = random.choice(RANKS_WRITTEN)
                randsuit = random.choice(SUITS)
                num = random.randint(1 , 100)
                if num > 87:
                    enhancement = "Bonus"
                elif num > 75:
                    enhancement = "Glass"
                elif num > 63:
                    enhancement = "Gold"
                elif num > 50:
                    enhancement = "Lucky"
                elif num > 38:
                    enhancement = "Mult"
                elif num > 25:
                    enhancement = "Steel"
                elif num > 13:
                    enhancement = "Glitched"
                filename = f"{randrank}Of{randsuit}.png"
                filepath = os.path.join(SUITS_DIR, randsuit, filename)
                if enhancement == "Glitched":
                    filename = f"GlitchBaseSpriteSheet.png"
                    filepath = os.path.join(SPRITESHEETS_DIR, filename)
                image = pygame.image.load(filepath).convert_alpha()
                newcard = Card(randrank, randsuit, image, enhancement=enhancement)
                newcard.refresh_image()
                PackCards.append(newcard)
                perm_deck.append(newcard)
    if name == "Hex":
        if len(Active_Jokers) > 0:
            hexed = random.choice(Active_Jokers)
            Active_Jokers.clear()
            hexed.edition = "Polychrome"
            Active_Jokers.append(hexed)
    if name == "Immolate":
        money += 20
        if GameState == "Playing":
            rand1 = hand.pop(randindex := random.randrange(len(hand)))
            rand2 = hand.pop(randindex := random.randrange(len(hand)))
            rand3 = hand.pop(randindex := random.randrange(len(hand)))
            rand4 = hand.pop(randindex := random.randrange(len(hand)))
            rand5 = hand.pop(randindex := random.randrange(len(hand)))
        else:
            rand1 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            rand2 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            rand3 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            rand4 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            rand5 = PackCards.pop(randindex := random.randrange(len(PackCards)))
        perm_deck.pop(rand1)
        perm_deck.pop(rand2)
        perm_deck.pop(rand3)
        perm_deck.pop(rand4)
        perm_deck.pop(rand5)
    if name == "Incantation":
        if GameState == "Playing":
            rand1 = hand.pop(randindex := random.randrange(len(hand)))
            for i in range(4):
                randrank = random.choice(NUMBERS_WRITTEN)
                randsuit = random.choice(SUITS)
                num = random.randint(1 , 100)
                if num > 87:
                    enhancement = "Bonus"
                elif num > 75:
                    enhancement = "Glass"
                elif num > 63:
                    enhancement = "Gold"
                elif num > 50:
                    enhancement = "Lucky"
                elif num > 38:
                    enhancement = "Mult"
                elif num > 25:
                    enhancement = "Steel"
                elif num > 13:
                    enhancement = "Glitched"
                filename = f"{randrank}Of{randsuit}.png"
                filepath = os.path.join(SUITS_DIR, randsuit, filename)
                if enhancement == "Glitched":
                    filename = f"GlitchBaseSpriteSheet.png"
                    filepath = os.path.join(SPRITESHEETS_DIR, filename)
                image = pygame.image.load(filepath).convert_alpha()
                newcard = Card(randrank, randsuit, image, slot=len(hand) + 1 , enhancement=enhancement)
                newcard.refresh_image()
                hand.append(newcard)
                perm_deck.append(newcard)
        else:
            rand1 = PackCards.pop(randindex := random.randrange(len(PackCards)))
            for i in range(4):
                randrank = random.choice(NUMBERS_WRITTEN)
                randsuit = random.choice(SUITS)
                num = random.randint(1 , 100)
                if num > 87:
                    enhancement = "Bonus"
                elif num > 75:
                    enhancement = "Glass"
                elif num > 63:
                    enhancement = "Gold"
                elif num > 50:
                    enhancement = "Lucky"
                elif num > 38:
                    enhancement = "Mult"
                elif num > 25:
                    enhancement = "Steel"
                elif num > 13:
                    enhancement = "Glitched"
                filename = f"{randrank}Of{randsuit}.png"
                filepath = os.path.join(SUITS_DIR, randsuit, filename)
                if enhancement == "Glitched":
                    filename = f"GlitchBaseSpriteSheet.png"
                    filepath = os.path.join(SPRITESHEETS_DIR, filename)
                image = pygame.image.load(filepath).convert_alpha()
                newcard = Card(randrank, randsuit, image, enhancement=enhancement)
                newcard.refresh_image()
                PackCards.append(newcard)
                perm_deck.append(newcard)
    if name == "Medium":
        for card in selected_cards:
            card.seal = "Purple"
    if name == "Ouija":
        max_handsize -= 1
        rand = random.randint(0, 13)
        randrank = RANKS_WRITTEN[rand]
        randvalue = RANK_VALUES[randrank]
        if GameState == "Playing":
            for card in hand:
                card.rank = randrank
                card.value = randvalue
                card.chip_value = randvalue
                card.refresh_image()
        else:
            for card in PackCards:
                card.rank = randrank
                card.value = randvalue
                card.chip_value = randvalue
                card.refresh_image()
        for card in perm_deck:
            card.rank = randrank
            card.value = randvalue
            card.chip_value = randvalue
    if name == "Sigil":
        randsuit = random.choice(SUITS)
        if GameState == "Playing":
            for card in hand:
                card.suit = randsuit
                card.refresh_image()
        else:
            for card in PackCards:
                card.suit = randsuit
                card.refresh_image()
        for card in perm_deck:
            card.suit = randsuit
    if name == "Talisman":
        for card in selected_cards:
            card.seal = "Gold"
    if name == "The Soul":
        if len(Active_Jokers) < maxJokerCount:
            newjoke = random.choice(Legendary_Jokers)
            newjoke = Joker(newjoke.image, newjoke.rarity, newjoke.name)
            Active_Jokers.append(newjoke)
    if name == "Trance":
        for card in selected_cards:
            card.seal = "Blue"
    if name == "True Shadow":
        for l in Hand_levels:
            Hand_levels[l] += 1
    if name == "Wraith":
        money = 0
        if len(Active_Jokers) < maxJokerCount:
            Active_Jokers.append(random.choice(Rare_Jokers))

def get_tarot_effect(name):
    global money, lastFool, selected_cards, perm_deck, hand, deck
    _peek_card_image_cache.clear()
    if name == "Hermit":
        if money > 20:
            money += 20
        else:
            money *= 2
        lastFool = "Hermit"
    if name == "Temperance":
        price_count = 0
        for joker in Active_Jokers:
            price_count += int(joker.price / 2)
        if price_count > 50:
            price_count = 50
        money += price_count
        lastFool = "Temperance"
    if name == "Emperor":
        if len(Held_Consumables) < maxConsCount:
            while True:
                card = random.choice(TarotCards)
                if card not in Held_Consumables and card not in Shop_Cards and card.name != "The Soul":
                    break
            Held_Consumables.append(card)
        if len(Held_Consumables) < maxConsCount:
            while True:
                card = random.choice(TarotCards)
                if card not in Held_Consumables and card not in Shop_Cards and card.name != "The Soul":
                    break
            Held_Consumables.append(card)
        lastFool = "Emperor"
    if name == "Fool":
        if lastFool:
            if len(Held_Consumables) < maxConsCount:
                for card in TarotCards + ShadowCards:
                    if card.name == lastFool:
                        new_card = Consumable(card.image, card.name)
                        Held_Consumables.append(new_card)
                lastFool = None
    if name == "High Priest":
        if len(Held_Consumables) < maxConsCount:
            while True:
                card = random.choice(ShadowCards)
                if card not in Held_Consumables and card not in Shop_Cards and card.name != "True Shadow":
                    break
            Held_Consumables.append(card)
        if len(Held_Consumables) < maxConsCount:
            while True:
                card = random.choice(ShadowCards)
                if card not in Held_Consumables and card not in Shop_Cards and card.name != "True Shadow":
                    break
            Held_Consumables.append(card)
        lastFool = "High Priest"
    if name == "Judgement":
        if len(Active_Jokers) < maxJokerCount:
            jokester = random.randint(1, 3)
            while True:
                if jokester == 1:
                    card = random.choice(Common_Jokers)
                    if card not in Active_Jokers and card not in Shop_Cards:
                        break
                elif jokester == 2:
                    card = random.choice(get_available_jokers(Uncommon_Jokers))
                    if card not in Active_Jokers and card not in Shop_Cards:
                        break
                elif jokester == 3:
                    card = random.choice(Rare_Jokers)
                    if card not in Active_Jokers and card not in Shop_Cards:
                        break
            Active_Jokers.append(card)
        lastFool = "Judgement"
    if name == "Chariot":
        if len(selected_cards) < 2:
            for card in selected_cards:
                card.enhancement = "Steel"
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Steel"
                        break
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Steel"
                        break
        lastFool = "Chariot"
    if name == "Death":
        if len(selected_cards) == 2:
            card1 = selected_cards[0]
            card2 = selected_cards[1]
            card1.rank, card1.suit, card1.enhancement, card1.edition, card1.seal, card1.value, card1.chip_value, card1.saved_suit, card1.saved_rank = card2.rank, card2.suit, card2.enhancement, card2.edition, card2.seal, card2.value, card2.chip_value, card2.saved_suit, card2.saved_rank
            card1.refresh_image()
        lastFool = "Death"
    if name == "Devil":
        if len(selected_cards) < 2:
            for card in selected_cards:
                card.enhancement = "Gold"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Gold"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Gold"
                        break
        lastFool = "Devil"
    if name == "Empress":
        if len(selected_cards) < 3:
            for card in selected_cards:
                card.enhancement = "Mult"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Mult"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Mult"
                        break
        lastFool = "Empress"
    if name == "Hanged Man":
        if len(selected_cards) < 3:
            for card in selected_cards:
                hand.remove(card)
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_deck.remove(perm_card)
                        break
        lastFool = "Hanged Man"
    if name == "Hierophant":
        if len(selected_cards) < 3:
            for card in selected_cards:
                card.enhancement = "Bonus"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Bonus"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Bonus"
                        break
        lastFool = "Hierophant"
    if name == "Justice":
        if len(selected_cards) < 2:
            for card in selected_cards:
                card.enhancement = "Glass"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Glass"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Glass"
                        break
        lastFool = "Justice"
    if name == "Lovers":
        if len(selected_cards) < 2:
            for card in selected_cards:
                card.enhancement = "Wild"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Wild"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Wild"
                        break
        lastFool = "Lovers"
    if name == "Magician":
        if len(selected_cards) < 3:
            for card in selected_cards:
                card.enhancement = "Lucky"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Lucky"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement = "Lucky"
                        break
        lastFool = "Magician"
    if name == "Moon":
        if len(selected_cards) <= 3:
            for card in selected_cards:
                card.suit = "Clubs"
                card.saved_suit = card.suit
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Clubs"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Clubs"
                        break
            lastFool = "Clubs"
    if name == "Star":
        if len(selected_cards) <= 3:
            for card in selected_cards:
                card.suit = "Diamonds"
                card.saved_suit = card.suit
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Diamonds"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Diamonds"
                        perm_card.saved_suit = card.saved_suit
                        break
            lastFool = "Star"
    if name == "Strength":
        if len(selected_cards) < 3:
            for card in selected_cards:
                if card.rank in RANK_VALUES:
                    keys = list(RANK_VALUES.keys())
                    idx = keys.index(card.rank)
                    card.rank = keys[idx + 1 if idx < len(RANK_VALUES) else 0]
                    card.saved_rank = card.rank
                card.value = RANK_VALUES[card.rank]
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.rank = card.rank
                        perm_card.saved_rank = card.saved_rank
                        perm_card.value = card.value
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.rank = card.rank
                        perm_card.value = card.value
                        break
        lastFool = "Strength"
    if name == "Sun":
        if len(selected_cards) <= 3:
            for card in selected_cards:
                card.suit = "Hearts"
                card.saved_suit = card.suit
                card.name = f"{card.rank} of {card.suit}"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Hearts"
                        perm_card.name = card.name
                        perm_card.saved_suit = card.saved_suit
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Hearts"
                        perm_card.name = card.name
                        perm_card.saved_suit = card.saved_suit
                        break
            lastFool = "Sun"
    if name == "Tower":
       if len(selected_cards) < 2:
            for card in selected_cards:
                card.enhancement = "Glitched"
                card.rank = 0
                card.value = 0
                card.chip_value = 50
                card.suit = "Glitched"
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement, perm_card.rank, perm_card.value, perm_card.suit = "Glitched", 0, 0, "Glitched"
                        break
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.enhancement, perm_card.rank, perm_card.value, perm_card.suit = "Glitched", 0, 0, "Glitched"
                        break
            lastFool = "Tower"
    if name == "Wheel Of Fortune":
        wheelnum = random.randint(min(base_chance, 4), 4)
        if wheelnum == 4:
            jonker = random.choice(Active_Jokers)
            wheelnum2 = random.randint(1, 3)
            if wheelnum2 == 1:
                jonker.edition = "Foil"
            elif wheelnum2 == 2:
                jonker.edition = "Holographic"
            elif wheelnum2 == 3:
                jonker.edition = "Polychrome"
    if name == "World":
        if len(selected_cards) <= 3:
            for card in selected_cards:
                card.suit = "Spades"
                card.saved_suit = card.suit
                for perm_card in deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Spades"
                        break
                card.refresh_image()
                for perm_card in perm_deck:
                    if perm_card.card_id == card.card_id:
                        perm_card.suit = "Spades"
                        break
            lastFool = "World"
def get_shadow_effect(name):
    global Hand_levels
    _peek_card_image_cache.clear()
    if name == "Big":
        Hand_levels["Flush"] += 1
        lastFool = "Big"
    elif name == "The Reaper":
        Hand_levels["Five of a Kind"] += 1
        lastFool = "The Reaper"
    elif name == "Fists":
        Hand_levels["Four of a Kind"] += 1
        lastFool = "Fists"
    elif name == "Glitch":
        Hand_levels["Huh of a What"] += 1
        lastFool = "Glitch"
    elif name == "Ice":
        Hand_levels["Two Pair"] += 1
        lastFool = "Ice"
    elif name == "King Shadow":
        Hand_levels["Flush House"] += 1
        lastFool = "King Shadow"
    elif name == "Quick":
        Hand_levels["Pair"] += 1
        lastFool = "Quick"
    elif name == "Shadow":
        Hand_levels["Full House"] += 1
        lastFool = "Shadow"
    elif name == "Shadowbot":
        Hand_levels["Straight Flush"] += 1
        lastFool = "Shadowbot"
    elif name == "Stretch":
        Hand_levels["Straight"] += 1
        lastFool = "Stretch"
    elif name == "The Doctor":
        Hand_levels["High Card"] += 1
        lastFool = "The Doctor"
    elif name == "Trick":
        Hand_levels["Three of a Kind"] += 1
        lastFool = "Trick"

init_video()
game = True
mouse_display = cursor_normal
def mouse_hover(rect):
    global mouse_display
    _virtual_mouse_pos = lambda: pygame.mouse.get_pos()
    
    if rect.collidepoint(_virtual_mouse_pos()):
        mouse_display = cursor_hover
   
  
        
    
if joker_manager is None:
    joker_manager = initialize_joker_effects(Active_Jokers)

while game:
    while startGame == False:
        
        dt = clock.tick(60) / 1000.0
        mouse_display = cursor_normal
        if Music.toggle:
            if not mainMusicPlaying:
                mainMusic.play(-1)
                mainMusicPlaying = True
        else:
            mainMusic.stop()
            mainMusicPlaying = False
        mouse_pos = _virtual_mouse_pos()
        
        for toggle in guiToggleList:
            if toggle.should_draw:
                mouse_hover(toggle.rect)
                

        current_blind = get_current_blind()
        if current_blind and GameState != "Dead":
            mouse_hover(current_blind.rect)
        for event in pygame.event.get():
            event = _translate_event(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            keys = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                if event.unicode:
                        dev_progress += event.unicode.lower()
 
                        dev_progress = dev_progress[-len(dev_code):]

                        if dev_progress == dev_code:
                            DEV_MODE.toggle = not DEV_MODE.toggle
                            print("Developer Mode:", DEV_MODE.toggle)
                            dev_progress = ""
                            dev_toggle = True
                                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if start_button_rect.collidepoint(event.pos):
                        buttonClick.play(0)
                        card_x = -WIDTH
                        card_animating = True
                        running = True
                        joker_manager = initialize_joker_effects(Active_Jokers)
                        GameState = "Blinds"
                        seed = ''
                        for i in range(8):
                            num = random.randint(0, 35)
                            if num > 9:
                                num -= 9
                                num = chr(ord('`')+num)
                            num = str(num)
                            seed += num
                        random.seed(seed)
                        running = True
                    elif settings2.toggle:  
                        for setting in settingsList:
                            if setting.rect.collidepoint(event.pos):
                                buttonClick.play(0)
                                setting.toggle = not setting.toggle 
                                setting.update_img()
                    elif setting_rect.collidepoint(event.pos): 
                        buttonClick.play(0)
                        settings2.toggle = True
                    if xbutton_rect.collidepoint(event.pos):
                        buttonClick.play(0)
                        settings2.toggle = False
            
        screen.fill((255, 255, 255))
        animate_ring()
        #spinningBG.animate()
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

        
        for letter in Letters:
            letter.animate()
            letter.draw()
        screen.blit(STARTBUTTON, (STARTBUTTON_X, STARTBUTTON_Y))
        
        
        if settings2.toggle:
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


        if Focy.toggle: 
            if random.randint(min(base_chance, 20000), 20000)  == 20000:
                
                subprocess.run(['powershell', '-Command', 
                '$obj = New-Object -ComObject WScript.Shell;'
                '$obj.SendKeys([char]173);'
                'for($i=0;$i -lt 50;$i++){$obj.SendKeys([char]175)}'], 
                shell=True)
                foxsound.play()   
                draw_fox = True
        if draw_fox:
            focy_scare.animate()
        if not settings:
            screen.blit(mouse_display, mouse_pos)
        
        _flip()
        clock.tick(60)
        currentFrame += 1

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))  
    overlay.set_alpha(128)
    
    while running:
        active_hover_rects = []
        if not settings:
            mouse_display = cursor_normal
        if Music.toggle:
            if not mainMusicPlaying:
                mainMusic.play(-1)
        else:
            mainMusic.stop()
        yin_active = any(j.name == "Yin Joker" for j in Active_Jokers)
        yang_active = any(j.name == "Yang Joker" for j in Active_Jokers)
        yinyang_active = any(j.name == "Yin Yang" for j in Active_Jokers)
        if yin_active and yang_active and not yinyang_active:
            yinyang_template = next((j for j in All_Jokers if j.name == "Yin Yang"), None)
            if yinyang_template:
                Active_Jokers = [j for j in Active_Jokers if j.name not in ("Yin Joker", "Yang Joker")]
                new_joker = Joker(yinyang_template.image, yinyang_template.rarity, yinyang_template.name)
                Active_Jokers.append(new_joker)
                joker_manager = initialize_joker_effects(Active_Jokers)
        global discard_queue
        mouse_pos = _virtual_mouse_pos()
        for toggle in guiToggleList:
            if toggle.should_draw:
                mouse_hover(toggle.rect)
                
        hovered_joker = None
        
        for joker in Active_Jokers:
          
            if joker.x > 0 and joker.rect.collidepoint(mouse_pos):
                hovered_joker = joker
                break
               
        for joker in Shop_Cards:
            if isinstance(joker, Joker) and joker.x > 0 and joker.rect.collidepoint(mouse_pos):
                hovered_joker = joker
                break
        for card in hand:
            if  GameState != "Dead":
                mouse_hover(card.rect)
               
            
        update_gui_buttons()
        if Atttention_helper.toggle and not prev_attention_state:
            init_video()
        elif not Atttention_helper.toggle and prev_attention_state:
            close_video()
        prev_attention_state = Atttention_helper.toggle
        for event in pygame.event.get():
            event = _translate_event(event)
            if event.type == pygame.QUIT:
                running = False
            keys = pygame.key.get_pressed() 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE and DEV_MODE.toggle:
                    dev_command_bar_active = not dev_command_bar_active
                    if not dev_command_bar_active:
                        dev_awaiting_input = False
                        dev_current_command = None
                elif DEV_MODE.toggle and dev_command_bar_active:
                    if event.key == pygame.K_RETURN and dev_command_input:
                        if dev_awaiting_input:
                            dev_command_output_lines.append(f"{dev_input_prompt}> {dev_command_input}")
                        else:
                            dev_command_output_lines.append(f"> {dev_command_input}")
                        result = process_dev_command(dev_command_input)
                        dev_command_output_lines.append(result)
                        dev_command_history.append(dev_command_input)
                        dev_command_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        dev_command_bar_active = False
                        dev_command_input = ""
                        dev_awaiting_input = False
                        dev_current_command = None
                    elif event.key == pygame.K_BACKSPACE:
                        dev_command_input = dev_command_input[:-1]
                        
                    elif event.unicode and len(dev_command_input) < 100:
                        dev_command_input += event.unicode
                
                elif event.unicode and not dev_command_bar_active:
                    dev_progress += event.unicode.lower()
                    dev_progress = dev_progress[-len(dev_code):]
                    if dev_progress == dev_code:
                        DEV_MODE.toggle = not DEV_MODE.toggle
                        print("Developer Mode:", DEV_MODE.toggle)
                        dev_progress = ""
                
                if event.key == pygame.K_ESCAPE and not dev_command_bar_active:
                    settings = not settings
                    if settings:
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                    else:
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    
            if event.type == pygame.MOUSEWHEEL and help_menu:
                scroll_offset += event.y * scroll_speed
            
                max_scroll = -max(0, len(helpMenu_surfaces) * line_height - HEIGHT + 200)
                scroll_offset = max(max_scroll, min(0, scroll_offset))
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

                    if settings2.toggle:
                        for setting in settingsList:
                            if setting.rect.collidepoint(event.pos):
                                buttonClick.play(0)
                                setting.toggle = not setting.toggle
                                setting.update_img()
                        
                    if xbutton_rect.collidepoint(event.pos):
                        buttonClick.play(0)
                        settings2.toggle = False
                        
                    if RunInfo_rect.collidepoint(mouse_pos):
                        menuOpen = True
                        fullPeekOpen = False

                    if MenuBackButton_rect.collidepoint(mouse_pos) and (menuOpen or fullPeekOpen):
                        menuOpen = False
                        fullPeekOpen = False

                    if MenuPokerHandsButton_rect.collidepoint(mouse_pos) and menuOpen:
                        selectedMenu = "Hands"

                    if MenuVouchersButton_rect.collidepoint(mouse_pos) and menuOpen:
                        selectedMenu = "Vouchers"

                    if MenuBlindsButton_rect.collidepoint(mouse_pos) and menuOpen:
                        selectedMenu = "Blinds"

                    if RemainingButton_rect.collidepoint(mouse_pos) and fullPeekOpen:
                        PeekSelected = "Remaining"

                    if FullDeckButton_rect.collidepoint(mouse_pos) and fullPeekOpen:
                        PeekSelected = "Full"

                    if deck_rect.collidepoint(mouse_pos) and GameState == "Playing":
                        fullPeekOpen = True
                        menuOpen = False

                    if CashOut_rect.collidepoint(mouse_pos) and GameState == "Cashing":
                        GameState = "Shop"
                        buttonClick.play(0)
                        money += totalReward
                        totalReward = 0
                        rerollCost = 3
                        for i in range(ShopCount):
                            rarity_choice = random.randint(1, 100)
                            while True:
                                if rare_joker:
                                    card = random.choice(Rare_Jokers)
                                    if card not in Shop_Cards and card not in Active_Jokers:
                                        rare_joker = False
                                        break
                                elif rarity_choice <= 28:
                                    card = random.choice(TarotCards)
                                    if card not in Shop_Cards and card not in Held_Consumables and card.name != "The Soul":
                                        break
                                elif rarity_choice <= 50:
                                    card = random.choice(ShadowCards)
                                    if card not in Shop_Cards and card not in Held_Consumables and card.name not in locked_cards and card.name != "True Shadow":
                                        break
                                elif rarity_choice <= 75:
                                    card = random.choice(Common_Jokers)
                                    if card not in Shop_Cards and card not in Active_Jokers:
                                        break
                                elif rarity_choice <= 95:
                                    card = random.choice(get_available_jokers(Uncommon_Jokers))
                                    if card not in Shop_Cards and card not in Active_Jokers:
                                        break
                                else:
                                    card = random.choice(Rare_Jokers)
                                    if card not in Shop_Cards and card not in Active_Jokers:
                                        break
                            Shop_Cards.append(card)
                        for i in range(2):
                            rarity_choice = random.randint(0, 100)
                            while True:
                                if rarity_choice <= 5:
                                    pack = random.choice(SpectralPacks)
                                    if pack not in ShopPacks:
                                        break
                                if rarity_choice <= 37:
                                    pack = random.choice(StandardPacks)
                                    if pack not in ShopPacks:
                                        break
                                if rarity_choice <= 68:
                                    pack = random.choice(ShadowPacks)
                                    if pack not in ShopPacks:
                                        break
                                else:
                                    pack = random.choice(TarotPacks)
                                    if pack not in ShopPacks:
                                        break
                            ShopPacks.append(pack)
                        break
                       
                    if settings:
                        for toggle in guiToggleList:
                            if toggle.should_draw and toggle.rect.collidepoint(mouse_pos):
                                toggle.toggle = not settings2.toggle
                                buttonClick.play(0)
                                if toggle == settings:
                                    settings2.toggle = True
                                elif not settings2.toggle:    
                                    if toggle == githubButton:
                                        webbrowser.open("https://github.com/eepy-sleepy1234/Barratlo/tree/main")
                                        toggle.toggle = False
                                    if toggle == helpButton:
                                        help_menu = True

                                    if toggle == quitButton:
                                        game = False
                                        running = False
                        
                    if (SO_SERIOUS.toggle or jonkler_sphere_active) and soserious.rect.collidepoint(mouse_pos):
                        if jonkler_sphere_active and not jonkler_sphere_clicked and GameState == "Playing":
                            jonkler_sphere_clicked = True
                            jonkler_sphere_active = False
                            for card in hand:
                                card.state = "discarded"
                            discard_queue = hand.copy()
                            discarding = True
                        else:
                            soserious.dragging = True
                            soserious.drag_offset_x = soserious.xpos - mouse_x
                            soserious.drag_offset_y = soserious.ypos - mouse_y
                            soserious.drag_start = (mouse_x, mouse_y)
                            soserious.was_dragged = False
                    if not scoring_in_progress and not GameState == "Dead":
                        for card in reversed(hand):
                            if card.rect.collidepoint(mouse_pos) and not calculating:
                                card.dragging = True
                                card.drag_offset_x = card.x - mouse_x
                                card.drag_offset_y = card.y - mouse_y
                                card.drag_start = (mouse_x, mouse_y)
                                card.was_dragged = False
                                break
                    for card in reversed(Shop_Cards):
                        if card.rect.collidepoint(mouse_pos):
                            card.dragging = True
                            card.drag_offset_x = card.x - mouse_x
                            card.drag_offset_y = card.y - mouse_y
                            card.drag_start = (mouse_x, mouse_y)
                            card.was_dragged = False
                            break
                    for card in reversed(Active_Jokers):
                        if card.rect.collidepoint(mouse_pos):
                            card.dragging = True
                            card.drag_offset_x = card.x - mouse_x
                            card.drag_offset_y = card.y - mouse_y
                            card.drag_start = (mouse_x, mouse_y)
                            card.was_dragged = False
                            break
                    for card in reversed(Held_Consumables):
                        if card.rect.collidepoint(mouse_pos):
                            card.dragging = True
                            card.drag_offset_x = card.x - mouse_x
                            card.drag_offset_y = card.y - mouse_y
                            card.drag_start = (mouse_x, mouse_y)
                            card.was_dragged = False
                            break
                    for card in reversed(ShopPacks):
                        if card.rect.collidepoint(mouse_pos):
                            card.dragging = True
                            card.drag_offset_x = card.x - mouse_x
                            card.drag_offset_y = card.y - mouse_y
                            card.drag_start = (mouse_x, mouse_y)
                            card.was_dragged = False
                            break
                    for card in reversed(PackCards):
                        if card.rect.collidepoint(mouse_pos):
                            card.dragging = True
                            card.drag_offset_x = card.x - mouse_x
                            card.drag_offset_y = card.y - mouse_y
                            card.drag_start = (mouse_x, mouse_y)
                            card.was_dragged = False
                            break
                    if Playhand_rect.collidepoint(mouse_pos) and GameState == "Playing":
                        buttonClick.play(0)
                        if hands > 0 and not scoring_in_progress:
                            scoring_count = 0
                            mouth_triggered = False
                            for card in hand:
                                if card.freeze_timer >= 0:
                                    card.freeze_timer -= 1
                            selected_cards = [card for card in hand if card.state == "selected"]
                            if len(selected_cards) > 0:
                                hand_type, contributing = detect_hand(selected_cards)
                                saved_base_chips = (Hand_Chips.get(hand_type, 0) * Hand_levels.get(hand_type, 1))
                                saved_base_mult = Hand_Mult.get(hand_type, 1) * Hand_levels.get(hand_type, 1)
                                saved_level = Hand_levels.get(hand_type, 1)
                                saved_hand = hand_type
                                if hand_type == "Royal Flush":
                                    saved_base_chips = (Hand_Chips.get("Straight Flush", 0) * Hand_levels.get("Straight Flush", 1))
                                    saved_base_mult = Hand_Mult.get("Straight Flush", 1)
                                    saved_level = Hand_levels.get("Straight Flush", 1)
                                if hand_type in locked_hands:
                                    locked_hands.remove(hand_type)
                                    unlocked_hands.append(hand_type)
                                    match hand_type:
                                        case "Five of a Kind":
                                            locked_cards.remove("The Reaper")
                                        case "Flush Five":
                                            locked_cards.remove("King Shadow")
                                        case "Flush House":
                                            locked_cards.remove("Tag Team")
                                        case "Huh of a What":
                                            locked_cards.remove("Glitch")
                                dev_selection = False
                                scoring_queue = contributing.copy()
                                for card in contributing:
                                    card.seal_triggered = False
                                    card.retriggers = 0
                                    card.retriggers_remaining = 0

                                context = {
                                    'active_jokers': Active_Jokers,
                                    'hand_type': saved_hand,
                                    'hand_played': selected_cards,
                                    'contributing': contributing,
                                    'deck': deck,
                                }
                                if context.get('fountain_remove_hand'):
                                    hands -= 1
                                context = joker_manager.trigger('on_scoring_start', context)
                                for card in contributing:
                                    card.retriggers_remaining = card.retriggers
                                for card in selected_cards:
                                    card.state = "played"
                                    card.play_timer = 0
                                    card.scaling_delay = 0
                                    card.is_contributing = card in contributing
                                    card.scaling_done = False
                                    card.scoring_animating = False
                                    card.scoring_complete = False
                                    card.scaling = False
                                    cards_played += 1
                                for card in contributing:
                                    card.is_contributing = True
                                hands -= 1
                                total_scoring_count = 0
                                if contributing:
                                    scoring_in_progress = True
                                    if scoring_queue:
                                        scoring_queue[0].scaling = True
                                scoring_sequence_index = 0
                                
                    if Discardhand_rect.collidepoint(mouse_pos) and GameState == "Playing":
                        buttonClick.play(0)
                        if discards > 0 and not scoring_in_progress:
                            for card in hand:
                                if card.freeze_timer >= 0:
                                    card.freeze_timer -= 1
                            dev_selection = False
                            lerp_factor = 0.3
                            discard_timer = 0
                            to_discard = [card for card in hand if card.state == "selected"]
                            discard_queue = to_discard
                            for card in discard_queue:
                                cards_discarded += 1
                            discarding = True
                            discards -= 1
                    if SortbuttonRank_rect.collidepoint(mouse_pos):
                        buttonClick.play(0)
                        sort_mode = "rank"
                        sort_hand()
                    if SortbuttonSuit_rect.collidepoint(mouse_pos):
                        buttonClick.play(0)
                        sort_mode = "suit"
                        sort_hand()
                    if ShopBuy_rect.collidepoint(mouse_pos):
                            buttonClick.play(0)
                            for card in Shop_Cards:
                                if card.state == "selected" and money >= card.price:
                                    if len(Active_Jokers) < maxJokerCount:
                                        if isinstance(card, Joker):
                                            shopJokerSelected = False
                                            card.state = "normal"
                                            Active_Jokers.append(card)
                                            joker_manager = initialize_joker_effects(Active_Jokers)
                                            Shop_Cards.remove(card) 
                                            money -= card.price
                                            purchases += 1    
                                    if isinstance(card, Consumable):
                                        if len(Held_Consumables) < maxConsCount:
                                            shopJokerSelected = False
                                            card.state = "normal"
                                            Held_Consumables.append(card)
                                            Shop_Cards.remove(card)
                                            money -= card.price
                                            purchases += 1
                            for pack in ShopPacks:
                                if pack.state == "selected" and money >= pack.price:
                                    money -= pack.price
                                    shopJokerSelected = False
                                    pack.state = "hand"
                                    selection = pack.selection
                                    if "Standard" in pack.name:
                                        GameState = "StandardPack"
                                        for i in range(pack.cardNum):
                                            randrank = random.choice(RANKS_WRITTEN)
                                            randsuit = random.choice(SUITS)
                                            num = random.randint(min(base_chance, 100), 100)
                                            if num > 97:
                                                enhancement = "Bonus"
                                            elif num > 94:
                                                enhancement = "Glass"
                                            elif num > 91:
                                                enhancement = "Gold"
                                            elif num > 88:
                                                enhancement = "Lucky"
                                            elif num > 85:
                                                enhancement = "Mult"
                                            elif num > 82:
                                                enhancement = "Steel"
                                            elif num > 79:
                                                enhancement = "Glitched"
                                            else:
                                                enhancement = "Default"
                                            num = random.randint(min(base_chance, 100), 100)
                                            if num > 97:
                                                edition = "Polychrome"
                                            elif num > 94:
                                                edition = "Foil"
                                            elif num > 91:
                                                edition = "Holographic"
                                            else:
                                                edition = None
                                            num = random.randint(min(base_chance, 100), 100)
                                            if num > 97:
                                                seal = "Red"
                                            elif num > 94:
                                                seal = "Gold"
                                            elif num > 91:
                                                seal = "Blue"
                                            elif num > 88:
                                                seal = "Purple"
                                            else:
                                                seal = None
                                            filename = f"{randrank}Of{randsuit}.png"
                                            filepath = os.path.join(SUITS_DIR, randsuit, filename)
                                            image = pygame.image.load(filepath).convert_alpha()
                                            newcard = Card(randrank, randsuit, image, enhancement=enhancement, edition=edition, seal=seal)
                                            newcard.refresh_image()
                                            PackCards.append(newcard)
                                    if "Shadow" in pack.name:
                                        GameState = "ShadowPack"
                                        for i in range(pack.cardNum):
                                            while True:
                                                newcard = random.choice(ShadowCards)
                                                if newcard not in PackCards and newcard not in Held_Consumables and newcard not in Shop_Cards and newcard.name not in locked_cards:
                                                    PackCards.append(newcard)
                                                    if newcard.name == "True Shadow":
                                                        num = random.randint(base_chance, 10)
                                                        if num == 10:
                                                            break
                                                    else:
                                                        break
                                    if "Spectral" in pack.name:
                                        GameState = "SpectralPack"
                                        for i in range(pack.cardNum):
                                            while True:
                                                newcard = random.choice(SpectralCards)
                                                if newcard not in PackCards and newcard not in Held_Consumables and newcard not in Shop_Cards and newcard.name not in locked_cards:
                                                    PackCards.append(newcard)
                                                    break
                                        reset_deck_for_new_round()
                                        for i in range(max_handsize):
                                            if deck:
                                                card = deck.pop()
                                                card.slot = i
                                                card.x, card.y = WIDTH + 100, HEIGHT - 170
                                                card.state = "hand"
                                                hand.append(card)
                                    if "Tarot" in pack.name:
                                        GameState = "TarotPack"
                                        for i in range(pack.cardNum):
                                            while True:
                                                newcard = random.choice(TarotCards)
                                                if newcard not in PackCards and newcard not in Held_Consumables and newcard not in Shop_Cards and newcard.name not in locked_cards:
                                                    PackCards.append(newcard)
                                                    if newcard.name == "The Soul":
                                                        num = random.randint(base_chance, 10)
                                                        if num == 10:
                                                            break
                                                    else:
                                                        break
                                        reset_deck_for_new_round()
                                        for i in range(max_handsize):
                                            if deck:
                                                card = deck.pop()
                                                card.slot = i
                                                card.x, card.y = WIDTH + 100, HEIGHT - 170
                                                card.state = "hand"
                                                hand.append(card)
                                    ShopPacks.remove(pack)
                    if SellButton_rect.collidepoint(mouse_pos):
                        buttonClick.play(0)
                        for card in Active_Jokers:
                            if card.state == "selected":
                                ActiveJokerSelected = False
                                card.state = "normal"
                                Active_Jokers.remove(card)
                                joker_manager = initialize_joker_effects(Active_Jokers)
                                money += int(card.price / 2)
                                if card.name == "Jevil":
                                    jevilActive = False
                                if card.name == "Pool Table":
                                    JokerEffects.poolMoney = 0
                                if card.name == "Rules Card":
                                    RulesHand = None
                                if card.name == "Getting An Upgrade":
                                    rare_joker = True
                                if card.name == "Disguised Joker":
                                    JokerEffects.Disguised = False
                        for card in Held_Consumables:
                            if card.state == "selected":
                                ActiveJokerSelected = False
                                card.state = "normal"
                                Held_Consumables.remove(card)
                                money += int(card.price / 2)
                    if UseButton_rect.collidepoint(mouse_pos):
                        buttonClick.play(0)
                        for card in Held_Consumables:
                            if card.state == "selected":
                                ActiveJokerSelected = False
                                card.state = "normal"
                                Held_Consumables.remove(card)
                                for tarot in TarotCards:
                                    if tarot.name == card.name:
                                        get_tarot_effect(card.name)
                                for shadow in ShadowCards:
                                    if shadow.name == card.name:
                                        get_shadow_effect(card.name)
                                for spectral in SpectralCards:
                                    if spectral.name == card.name:
                                        get_spectral_effect(card.name)
                        for card in PackCards:
                            if card.state == "selected":
                                ActiveJokerSelected = False
                                selection -= 1
                                card.state = "normal"
                                PackCards.remove(card)
                                for tarot in TarotCards:
                                    if tarot.name == card.name:
                                        get_tarot_effect(card.name)
                                for shadow in ShadowCards:
                                    if shadow.name == card.name:
                                        get_shadow_effect(card.name)
                                for spectral in SpectralCards:
                                    if spectral.name == card.name:
                                        get_spectral_effect(card.name)
                                if "of" in card.name:
                                    perm_deck.append(card)
                                if selection < 1:
                                    PackCards.clear()
                                    hand.clear()
                                    reset_deck_for_new_round()
                                    GameState = "Shop"
                                    ActiveJokerSelected = False
                    if Reroll_rect.collidepoint(mouse_pos) and GameState == 'Shop':
                        buttonClick.play(0)
                        if rerollCost <= money:
                            rerolls += 1
                            for joker in Shop_Cards:
                                joker.x = WIDTH/1.6
                                joker.y = HEIGHT/1.565
                            Shop_Cards.clear()
                            money -= rerollCost
                            rerollCost += 1
                            for i in range(ShopCount):
                                rarity_choice = random.randint(1, 100)
                                while True:
                                    if rare_joker:
                                        card = random.choice(Rare_Jokers)
                                        if card not in Shop_Cards and card not in Active_Jokers:
                                            rare_joker = False
                                            break
                                    if rarity_choice <= 28:
                                        card = random.choice(TarotCards)
                                        if card not in Shop_Cards and card not in Held_Consumables and card.name != "The Soul":
                                            break
                                    elif rarity_choice <= 50:
                                        card = random.choice(ShadowCards)
                                        if card not in Shop_Cards and card not in Held_Consumables and card.name not in locked_cards and card.name != "True Shadow":
                                            break
                                    elif rarity_choice <= 75:
                                        card = random.choice(Common_Jokers)
                                        if card not in Shop_Cards and card not in Active_Jokers:
                                            break
                                    elif rarity_choice <= 99:
                                        card = random.choice(get_available_jokers(Uncommon_Jokers))
                                        if card not in Shop_Cards and card not in Active_Jokers:
                                            break
                                    else:
                                        card = random.choice(Rare_Jokers)
                                        if card not in Shop_Cards and card not in Active_Jokers:
                                            break
                                Shop_Cards.append(card)
                    if NextRound_rect.collidepoint(mouse_pos) and GameState == "Shop":
                        buttonClick.play(0)
                        GameState = "Blinds"
                        Shop_Cards.clear()
                        ShopPacks.clear()
                        shopJokerSelected = False
                        for card in deck:
                            card.is_debuffed = False
                        break
                    if SelectBlind_rect.collidepoint(mouse_pos) and GameState == "Blinds":
                        buttonClick.play(0)
                        GameState = "Playing"
                        current_blind = None
                        victory = False
                        BLIND_X, BLIND_Y = WIDTH/100, HEIGHT/22.86
                        context = {'active_jokers': Active_Jokers, 'round_num': round_num, 'deck': deck, 'perm_deck': perm_deck, 'glitch': os.path.join(SPRITESHEETS_DIR, "GlitchBaseSpriteSheet.png"),}
                        context = joker_manager.trigger('on_round_start', context)
                        jonkler_sphere_active = context.get('jonkler_sphere_active', False)
                        if jonkler_sphere_active:
                            jonkler_sphere_clicked = False
                        reset_deck_for_new_round()
                        if jevilActive:
                            newSuit = random.choice(['Spades', 'Hearts', 'Clubs', 'Diamonds'])
                            for card in perm_deck:
                                card.suit = newSuit
                                card.refresh_image()
                        get_current_blind()
                        sort_hand()
                        if round_num % 3 == 0:
                            boss_debuff()
                        for i in range(handsize):
                            if deck:
                                card = deck.pop()
                                card.slot = i
                                card.x, card.y = WIDTH + 100, HEIGHT - 170
                                card.state = "hand"
                                hand.append(card)
                                sort_hand()
                        break
                    if SkipBlind_rect.collidepoint(mouse_pos) and GameState == "Blinds":
                        buttonClick.play(0)
                        if JokerEffects.bunsking:
                            JokerEffects.BunsKingScale['TimesMult'] += 0.25
                        else:
                            JokerEffects.skipMult += 0.25
                        round_num += 1
                        current_blind = None
                        victory = False
                        get_current_blind()
                        break
                    if NewRunButton_rect.collidepoint(mouse_pos) and GameState == "Dead":
                        scoring_in_progress = False
                        calculating = False
                        discarding = False
                        endBG = False
                        running = False
                        startGame = True
                        reset_game_variables()
                        card_x = -WIDTH
                        card_animating = True
                        joker_manager = initialize_joker_effects(Active_Jokers)
                        GameState = "Blinds"
                        seed = ''
                        for i in range(8):
                            num = random.randint(0, 35)
                            if num > 9:
                                num -= 9
                                num = chr(ord('`')+num)
                            num = str(num)
                            seed += num
                        random.seed(seed)
                        running = True
                    if MainMenuButton_rect.collidepoint(mouse_pos) and GameState == "Dead":
                        scoring_in_progress = False
                        calculating = False
                        discarding = False
                        endBG = False
                        running = False
                        startGame = False
                        reset_game_variables()
                    if CopyButton_rect.collidepoint(mouse_pos) and GameState == "Dead":
                        pyperclip.copy(seed)
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
                                    if sum(1 for c in hand if c.state == "selected") < 5 and not card.is_frozen:
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
                            slot_target_x = start_x + i * spread_local * WIDTH/1000
                            slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset * HEIGHT/800
                            if not card.state == "played":
                                card.target_x = slot_target_x
                                card.target_y = slot_target_y
                            card.vx = 0
                            card.vy = 0
                    for card in Shop_Cards:
                        if getattr(card, "dragging", False):
                            card.dragging = False
                            if not card.was_dragged and card.rect.collidepoint(mouse_pos):
                                if card.state == "selected":
                                    card.state = "normal"
                                    shopJokerSelected = False
                                elif not shopJokerSelected:
                                    card.state = "selected"
                                    shopJokerSelected = True
                                    if hasattr(card, 'sound') and card.sound: 
                                        card.sound.play() 
                            n = len(Shop_Cards)
                            spread_local = card.spread
                            total_width = (n - 1) * spread_local + 80
                            start_x = (WIDTH / 2) - total_width / 2
                            i = card.slot if card.slot else 1
                            center_y = HEIGHT - 100
                            max_v_offset = -30
                            t = i / (n - 1) if n > 1 else 0.5
                            slot_target_x = start_x + i * spread_local * WIDTH/1000
                            slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset * HEIGHT/800
                            card.target_x = slot_target_x
                            card.target_y = slot_target_y
                            card.vx = 0
                            card.vy = 0
                    for card in Active_Jokers:
                        if getattr(card, "dragging", False):
                            card.dragging = False
                            if not card.was_dragged and card.rect.collidepoint(mouse_pos):
                                if card.state == "selected":
                                    ActiveJokerSelected = False
                                    card.state = "normal"
                                elif not ActiveJokerSelected:
                                    ActiveJokerSelected = True
                                    card.state = "selected"
                                    if hasattr(card, 'sound') and card.sound:  
                                        card.sound.play()   
                            n = len(Active_Jokers)
                            spread_local = card.spread
                            total_width = (n - 1) * spread_local + 80
                            start_x = (WIDTH / 2) - total_width / 2
                            i = card.slot if card.slot else 1
                            center_y = HEIGHT - 100
                            max_v_offset = -30
                            t = i / (n - 1) if n > 1 else 0.5
                            slot_target_x = start_x + i * spread_local * WIDTH/1000
                            slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset * HEIGHT/800
                            card.target_x = slot_target_x
                            card.target_y = slot_target_y
                            card.vx = 0
                            card.vy = 0
                    for card in Held_Consumables:
                        if getattr(card, "dragging", False):
                            card.dragging = False
                            if not card.was_dragged and card.rect.collidepoint(mouse_pos):
                                if card.state == "selected":
                                    ActiveJokerSelected = False
                                    card.state = "normal"
                                elif not ActiveJokerSelected:
                                    ActiveJokerSelected = True
                                    card.state = "selected"
                                  
                            n = len(Held_Consumables)
                            spread_local = card.spread
                            total_width = (n - 1) * spread_local + 80
                            start_x = (WIDTH / 2) - total_width / 2
                            i = card.slot if card.slot else 1
                            center_y = HEIGHT - 100
                            max_v_offset = -30
                            t = i / (n - 1) if n > 1 else 0.5
                            slot_target_x = start_x + i * spread_local * WIDTH/1000
                            slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset * HEIGHT/800
                            card.target_x = slot_target_x
                            card.target_y = slot_target_y
                            card.vx = 0
                            card.vy = 0
                    for card in PackCards:
                        if getattr(card, "dragging", False):
                            card.dragging = False
                            if not card.was_dragged and card.rect.collidepoint(mouse_pos):
                                if card.state == "selected":
                                    ActiveJokerSelected = False
                                    card.state = "normal"
                                elif not ActiveJokerSelected:
                                    ActiveJokerSelected = True
                                    card.state = "selected"  
                            n = len(PackCards)
                            spread_local = 20
                            total_width = (n - 1) * spread_local + 80
                            start_x = (WIDTH / 2) - total_width / 2
                            i = card.slot if card.slot else 1
                            center_y = HEIGHT - 100
                            max_v_offset = -30
                            t = i / (n - 1) if n > 1 else 0.5
                            slot_target_x = start_x + i * spread_local * WIDTH/1000
                            slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset * HEIGHT/800
                            card.target_x = slot_target_x
                            card.target_y = slot_target_y
                            card.vx = 0
                            card.vy = 0
                    for card in ShopPacks:
                        if getattr(card, "dragging", False):
                            card.dragging = False
                            if not card.was_dragged and card.rect.collidepoint(mouse_pos):
                                if card.state == "selected":
                                    shopJokerSelected = False
                                    card.state = "normal"
                                elif not shopJokerSelected:
                                    shopJokerSelected = True
                                    card.state = "selected"
                            n = len(ShopPacks)
                            spread_local = card.spread
                            total_width = (n - 1) * spread_local + 80
                            start_x = (WIDTH / 2) - total_width / 2
                            i = card.slot if card.slot else 1
                            center_y = HEIGHT - 100
                            max_v_offset = -30
                            t = i / (n - 1) if n > 1 else 0.5
                            slot_target_x = start_x + i * spread_local * WIDTH/1000
                            slot_target_y = center_y - max_v_offset * 2 * (t - 0.5)**2 + max_v_offset * HEIGHT/800
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
                        if getattr(card, "dragging", False) and not card.state == "played" and not calculating:
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
                for card in Shop_Cards:
                    if getattr(card, "dragging", False):
                        dx = mouse_x - card.drag_start[0]
                        dy = mouse_y - card.drag_start[1]
                        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                            card.was_dragged = True
                            card.x = mouse_x + card.drag_offset_x
                            card.y = mouse_y + card.drag_offset_y
                            card.target_x = card.x
                            card.target_y = card.y
                            n = len(Shop_Cards)
                            for idx, c in enumerate(Shop_Cards):
                                c.slot = idx
                for card in Active_Jokers:
                    if getattr(card, "dragging", False):
                        dx = mouse_x - card.drag_start[0]
                        dy = mouse_y - card.drag_start[1]
                        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                            card.was_dragged = True
                            card.x = mouse_x + card.drag_offset_x
                            card.y = mouse_y + card.drag_offset_y
                            card.target_x = card.x
                            card.target_y = card.y
                            n = len(Active_Jokers)
                            new_index = get_hand_slot_from_x(card.x, n, spread=spacing, center_x=WIDTH/1.8)
                            current_index = Active_Jokers.index(card)
                            if new_index != current_index:
                                Active_Jokers.pop(current_index)
                                Active_Jokers.insert(new_index, card)
                                for idx, c in enumerate(Active_Jokers):
                                    c.slot = idx
                for card in Held_Consumables:
                    if getattr(card, "dragging", False):
                        dx = mouse_x - card.drag_start[0]
                        dy = mouse_y - card.drag_start[1]
                        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                            card.was_dragged = True
                            card.x = mouse_x + card.drag_offset_x
                            card.y = mouse_y + card.drag_offset_y
                            card.target_x = card.x
                            card.target_y = card.y
                            n = len(Held_Consumables)
                            new_index = get_hand_slot_from_x(card.x, n, spread=spacing, center_x=WIDTH/1.8)
                            current_index = Held_Consumables.index(card)
                            if new_index != current_index:
                                Held_Consumables.pop(current_index)
                                Held_Consumables.insert(new_index, card)
                                for idx, c in enumerate(Held_Consumables):
                                    c.slot = idx
                for card in ShopPacks:
                    if getattr(card, "dragging", False):
                        dx = mouse_x - card.drag_start[0]
                        dy = mouse_y - card.drag_start[1]
                        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                            card.was_dragged = True
                            card.x = mouse_x + card.drag_offset_x
                            card.y = mouse_y + card.drag_offset_y
                            card.target_x = card.x
                            card.target_y = card.y
                            n = len(ShopPacks)
                            for idx, c in enumerate(ShopPacks):
                                c.slot = idx
                for card in PackCards:
                    if getattr(card, "dragging", False):
                        dx = mouse_x - card.drag_start[0]
                        dy = mouse_y - card.drag_start[1]
                        if abs(dx) > DRAG_THRESHOLD or abs(dy) > DRAG_THRESHOLD:
                            card.was_dragged = True
                            card.x = mouse_x + card.drag_offset_x
                            card.y = mouse_y + card.drag_offset_y
                            card.target_x = card.x
                            card.target_y = card.y
                            n = len(PackCards)
                            new_index = get_hand_slot_from_x(card.x, n, spread=spacing, center_x=WIDTH/1.8)
                            current_index = PackCards.index(card)
                            if new_index != current_index:
                                PackCards.pop(current_index)
                                PackCards.insert(new_index, card)
                                for idx, c in enumerate(PackCards):
                                    c.slot = idx
        screen.blit(GameBackground_img, (0, 0))
        screen.blit(SideBar_img, (0, 0))
        screen.blit(RunInfo, RunInfo_rect.topleft)
        active_hover_rects.append(RunInfo_rect)
        if scoring_queue and not calculating:
            card = scoring_queue[0]
            if card.is_contributing:
                card_play_counts[card.card_id] = card_play_counts.get(card.card_id, 0)
                card.scaling = True
                if not card.base_scoring_complete:
                    if not card.is_debuffed:
                        card.scoring_animating = True
                        card.trigger("Chips", card.chip_value)
                    else:
                        card.scoring_animating = True
                        card.trigger("Debuff", 0)
                    if card.scoring_complete:
                        if not card.is_debuffed:
                            saved_base_chips += card.chip_value
                        card.rotation_speed = 0
                        card.angle = 0
                        card.scoring_complete = False
                        card.base_scoring_complete = True
                        card.scaling_delay = 10
                        if card.enhancement == "Lucky" and not card.is_debuffed:
                            card._lucky_num  = random.randint(min(base_chance, 5), 5)
                            card._lucky_num1 = random.randint(min(base_chance, 5), 15)
                elif card.scoring_progress == 2:
                    if not card.is_debuffed:
                        if card.enhancement_timer > 0:
                            card.enhancement_timer -= 1
                        else:
                            has_enhancement = card.enhancement in ("Mult", "Bonus", "Lucky", "Glass")
                            if has_enhancement:
                                card.scoring_animating = True
                                match card.enhancement:
                                    case "Mult":
                                        card.trigger("Mult", 4)
                                    case "Bonus":
                                        card.trigger("Chips", 30)
                                    case "Lucky":
                                        num  = getattr(card, '_lucky_num',  1)
                                        num1 = getattr(card, '_lucky_num1', 1)
                                        if num == 5:
                                            card.trigger("Mult", 20)
                                        elif num1 == 15:
                                            card.trigger("Money", 20)
                                        else:
                                            card.scoring_progress += 1
                                    case "Glass":
                                        card.trigger("XMult", 2)
                            else:
                                card.scoring_progress += 1
                                card.enhancement_scoring_complete = True
                                card.scaling_delay = 10
                            if card.scoring_complete:
                                match card.enhancement:
                                    case "Mult":
                                        saved_base_mult += 4
                                    case "Bonus":
                                        saved_base_chips += 30
                                    case "Lucky":
                                        num  = getattr(card, '_lucky_num',  1)
                                        num1 = getattr(card, '_lucky_num1', 1)
                                        if num == 5:
                                            saved_base_mult += 20
                                        if num1 == 15:
                                            money += 20
                                    case "Glass":
                                        brk = random.randint(min(base_chance, 4), 4)
                                        saved_base_mult *= 2
                                        if brk == 4:
                                            if card in perm_deck:
                                                perm_deck.remove(card)
                                            card.scoring_animating = True
                                            card.trigger("Break", 0)
                                card.scoring_complete = False
                                card.enhancement_scoring_complete = True
                                card.scaling_delay = 10
                    else:
                        card.scoring_animating = True
                        card.trigger("Debuff", 0)
                        if card.scoring_complete:
                            card.scoring_complete = False
                            card.enhancement_scoring_complete = True
                elif card.scoring_progress == 3:
                    if not card.is_debuffed:
                        if card.enhancement_timer > 0:
                            card.enhancement_timer -= 1
                        else:
                            has_edition = card.edition in ("Foil", "Holographic", "Polychrome")
                            if has_edition:
                                card.scoring_animating = True
                                match card.edition:
                                    case "Foil":
                                        card.trigger("Chips", 50)
                                    case "Holographic":
                                        card.trigger("Mult", 10)
                                    case "Polychrome":
                                        card.trigger("XMult", 1.5)
                            else:
                                card.scoring_progress += 1
                                card.edition_scoring_complete = True
                            if card.scoring_complete:
                                match card.edition:
                                    case "Foil":
                                        saved_base_chips += 50
                                    case "Holographic":
                                        saved_base_mult += 10
                                    case "Polychrome":
                                        saved_base_mult *= 1.5
                                card.scoring_complete = False
                                card.edition_scoring_complete = True
                                card.scaling_delay = 10
                    else:
                        card.scoring_animating = True
                        card.trigger("Debuff", 0)
                        if card.scoring_complete:
                            card.scoring_complete = False
                            card.edition_scoring_complete = True
                elif card.scoring_progress == 4:
                    if not card.is_debuffed:
                        if card.enhancement_timer > 0:
                            card.enhancement_timer -= 1
                        else:
                            if card.seal in ("Red", "Gold"):
                                card.scoring_animating = True
                                match card.seal:
                                    case "Red":
                                        card.trigger("Again", 0)
                                    case "Gold":
                                        card.trigger("Money", 3)
                            else:
                                card.scoring_progress += 1
                                card.seal_scoring_complete = True

                            if card.scoring_complete:
                                if card.seal == "Gold":
                                    money += 3
                                card.scoring_complete = False
                                card.seal_scoring_complete = True
                    else:
                        card.scoring_animating = True
                        card.trigger("Debuff", 0)
                        if card.scoring_complete:
                            card.scoring_complete = False
                            card.seal_scoring_complete = True
                if card.base_scoring_complete and card.scoring_progress >= 5:
                    pop_and_check_retrigger(card, scoring_queue)
                    card.enhancement_timer = 10
                    card.base_scoring_complete = False
                    card.scoring_complete = False
                    card.scoring_animating = False
                context = {
                    'card': card,
                    'chips': saved_base_chips,
                    'mult': saved_base_mult,
                    'active_jokers': Active_Jokers,
                    'hand_type': saved_hand,
                    'deck': deck,
                    'card_play_counts': card_play_counts,
                }
                context = joker_manager.trigger('on_card_scored', context)
                saved_base_chips = context['chips']
                saved_base_mult = context['mult']
                if 'triggered_jokers' in context:
                    for joker_name in context['triggered_jokers']:
                        if joker_name == "Jevil":
                            jevilActive = True
                                        
        if not calculating:
            selected_cards = [card for card in hand if card.state in ("selected", "played", "scoring", "scored")]
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
            if hand_type == "Royal Flush":
                level = Hand_levels.get("Straight Flush", 1)
                base_chips = Hand_Chips.get("Straight Flush", 0)
                base_mult = Hand_Mult.get("Straight Flush", 1)
            chips = base_chips * level
            mult = base_mult * level
            if math.isinf(saved_base_chips * saved_base_mult):
                final_score = math.inf
            else:
                final_score = int(round(saved_base_chips * saved_base_mult))
        screen.blit(HandBackground_img, (WIDTH/50, HEIGHT / 2.75))
        if GameState == "Playing":
            screen.blit(ScoreBackground_img, (WIDTH/50, HEIGHT / 3.75))
            screen.blit(GoalBackground_img, (WIDTH/12, HEIGHT / 7.2))
        screen.blit(MoneyBackground_img, (WIDTH/14, HEIGHT / 1.7))
        screen.blit(RoundBackground_img, (WIDTH/14, HEIGHT / 1.5))
        if GameState == "Cashing":
            screen.blit(CashOutBackground_img, (WIDTH/3.5, HEIGHT / 2))
            screen.blit(CashOutButton_img, (WIDTH/3.2, HEIGHT / 1.9))
            active_hover_rects.append(CashOut_rect)
        if GameState == "Shop":
            screen.blit(ShopBackground_img, (WIDTH/3, HEIGHT/2))
            screen.blit(RerollButton_img, (WIDTH/2.95, HEIGHT/1.53))
            active_hover_rects.append(Reroll_rect)
            text, text_rect = PixelFontS.render(f"${rerollCost}", white)
            text_rect.center = (int(WIDTH/2.55), int(HEIGHT / 1.4))
            screen.blit(text, text_rect)
            screen.blit(NextRoundButton_img, (WIDTH/2.95, HEIGHT/1.83))
            active_hover_rects.append(NextRound_rect)
        if GameState == "Blinds":
            if round_num % 3 == 1:
                screen.blit(BlindBG_img, (WIDTH/3.5, HEIGHT/2))
                screen.blit(BlindName_img, (WIDTH/3.4, HEIGHT/1.73))
                screen.blit(SelectBlind_img, (WIDTH/3.4, HEIGHT/1.93))
                screen.blit(SkipBlind_img, (WIDTH/2.8, HEIGHT/1.18))
                SelectBlind_rect.topleft = (WIDTH/3.4, HEIGHT/1.93)
                SkipBlind_rect.topleft = (WIDTH/2.8, HEIGHT/1.18)
                active_hover_rects.append(SelectBlind_rect)
                active_hover_rects.append(SkipBlind_rect)

                text, text_rect = PixelFontS.render(small_blind.name, black)
                text_rect.center = (int(WIDTH/2.72), int(HEIGHT/1.65))
                screen.blit(text, text_rect)
                screen.blit(small_blind.imageS,(WIDTH/2.97, HEIGHT/1.59))
            else:
                screen.blit(BlindBG_img, (WIDTH/3.5, HEIGHT/1.83))
                screen.blit(BlindName_img, (WIDTH/3.4, HEIGHT/1.6))
                screen.blit(SelectBlind_img, (WIDTH/3.4, HEIGHT/1.8))
                screen.blit(SkipBlind_img, (WIDTH/2.8, HEIGHT/1.12))
                text, _ = PixelFontS.render(small_blind.name, black)
                text_rect = text.get_rect(center=(WIDTH/2.72, HEIGHT/1.53))
                screen.blit(text, text_rect)
                screen.blit(small_blind.imageS,(WIDTH/2.97, HEIGHT/1.48))
            if round_num % 3 == 2:
                screen.blit(BlindBG_img, (WIDTH/2, HEIGHT/2))
                screen.blit(BlindName_img, (WIDTH/1.97, HEIGHT/1.73))
                screen.blit(SelectBlind_img, (WIDTH/1.97, HEIGHT/1.93))
                screen.blit(SkipBlind_img, (WIDTH/1.75, HEIGHT/1.18))
                SelectBlind_rect.topleft = (WIDTH/1.97, HEIGHT/1.93)
                SkipBlind_rect.topleft = (WIDTH/1.75, HEIGHT/1.18)
                text, _ = PixelFontS.render(big_blind.name, black)
                text_rect = text.get_rect(center=(WIDTH/1.72, HEIGHT/1.65))
                screen.blit(text, text_rect)
                screen.blit(big_blind.imageS,(WIDTH/1.82, HEIGHT/1.59))
            else:
                screen.blit(BlindBG_img, (WIDTH/2, HEIGHT/1.83))
                screen.blit(BlindName_img, (WIDTH/1.97, HEIGHT/1.6))
                screen.blit(SelectBlind_img, (WIDTH/1.97, HEIGHT/1.8))
                screen.blit(SkipBlind_img, (WIDTH/1.75, HEIGHT/1.12))
                text, _ = PixelFontS.render(big_blind.name, black)
                text_rect = text.get_rect(center=(WIDTH/1.72, HEIGHT/1.53))
                screen.blit(text, text_rect)
                screen.blit(big_blind.imageS,(WIDTH/1.82, HEIGHT/1.48))
            if JokerEffects.Disguised:
                bossIMG = NOBLIND
                text, _ = PixelFontS.render("N/A", black)
                
            else:
                bossIMG = boss_blind.imageS
                text, _ = PixelFontS.render(boss_blind.name, black)
                
            

            if round_num % 3 == 0:
                screen.blit(BossBlindBG_img, (WIDTH/1.4, HEIGHT/2))
                screen.blit(BlindName_img, (WIDTH/1.38, HEIGHT/1.73))
                screen.blit(SelectBlind_img, (WIDTH/1.38, HEIGHT/1.93))
                SelectBlind_rect.topleft = (WIDTH/1.38, HEIGHT/1.93)
                text_rect = text.get_rect(center=(WIDTH/1.25, HEIGHT/1.65))
                screen.blit(text, text_rect)
                screen.blit(bossIMG,(WIDTH/1.305, HEIGHT/1.59))
            else:
                screen.blit(BossBlindBG_img, (WIDTH/1.4, HEIGHT/1.83))
                screen.blit(BlindName_img, (WIDTH/1.38, HEIGHT/1.6))
                screen.blit(SelectBlind_img, (WIDTH/1.38, HEIGHT/1.8))
                text_rect = text.get_rect(center=(WIDTH/1.25, HEIGHT/1.53))
                screen.blit(text, text_rect)
                screen.blit(bossIMG,(WIDTH/1.305, HEIGHT/1.48))
        
        if not calculating:
            if scoring_in_progress:
                text, _ = PixelFontS.render(saved_hand, white)
            else:
                text, _ = PixelFontS.render(hand_type, white)
        else:
            current_score_text = change_notation(current_score)
            text, _ = PixelFontS.render(f"{current_score_text}", white)
        text_rect = text.get_rect(center=(WIDTH/9.4, HEIGHT / 2.5))
        screen.blit(text, text_rect)
        text, _ = PixelFontS.render(f"{hands}", white)
        text_rect = text.get_rect(center=(WIDTH/20, HEIGHT / 1.79))
        screen.blit(text, text_rect)
        text, _ = PixelFontS.render(f"{discards}", white)
        text_rect = text.get_rect(center=(WIDTH/6.9, HEIGHT / 1.79))
        screen.blit(text, text_rect)
        if scoring_in_progress or calculating:
            saved_base_chips_text = change_notation(saved_base_chips)
            text, _ = PixelFontS.render(f"{saved_base_chips_text}", white)
        else:
            chips_text = change_notation(chips)
            text, _ = PixelFontS.render(f"{chips_text}", white)
        text_rect = text.get_rect(center=(WIDTH/15, HEIGHT / 2.2))
        screen.blit(text, text_rect)
        if scoring_in_progress or calculating:
            saved_base_mult_text = change_notation(saved_base_mult)
            text, _ = PixelFontS.render(f"{saved_base_mult_text}", white)
        else:
            mult_text = change_notation(mult)
            text, _ = PixelFontS.render(f"{mult_text}", white)
        text_rect = text.get_rect(center=(WIDTH/7, HEIGHT / 2.2))
        screen.blit(text, text_rect)
        if GameState == "Playing":
            text, _ = PixelFontS.render(f"{len(hand)} / {handsize}", white)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT / 1.05))
            screen.blit(text, text_rect)
            total_score_text = change_notation(total_score)
            text, _ = PixelFontS.render(f"{total_score_text}", white)
            text_rect = text.get_rect(center=(WIDTH/7.5, HEIGHT / 3.17))
            screen.blit(text, text_rect)
            target_score_text = change_notation(target_score)
            text, _ = PixelFontS.render(f"{target_score_text}", red)
            text_rect = text.get_rect(center=(WIDTH/7.4, HEIGHT / 5))
            screen.blit(text, text_rect)
        text, _ = PixelFontS.render(f"{visible_round_num}", orange)
        text_rect = text.get_rect(center=(WIDTH/6.3, HEIGHT / 1.415))
        screen.blit(text, text_rect)
        text, _ = PixelFontS.render(f"{ante}", orange)
        text_rect = text.get_rect(center=(WIDTH/11, HEIGHT / 1.419))
        screen.blit(text, text_rect)
        text, _ = PixelFontS.render(f"${money}", yellow)
        text_rect = text.get_rect(center=(WIDTH/7.7, HEIGHT / 1.595))
        screen.blit(text, text_rect)
        if GameState == "Playing":
            match CurrentDeck:
                case "Red":
                    screen.blit(RedDeck_img, deck_rect.topleft)
                case "Blue":
                    screen.blit(BlueDeck_img, deck_rect.topleft)
                case "Green":
                    screen.blit(GreenDeck_img, deck_rect.topleft)
                case "Yellow":
                    screen.blit(YellowDeck_img, deck_rect.topleft)
                case "Black":
                    screen.blit(BlackDeck_img, deck_rect.topleft)
                case "Shattered":
                    screen.blit(ShatteredDeck_img, deck_rect.topleft)
                case "Spider":
                    screen.blit(SpiderDeck_img, deck_rect.topleft)
            text, _ = PixelFontXS.render(f"{'$' * blind_reward}", yellow)
            text_rect = text.get_rect(center=(WIDTH/6, HEIGHT / 4.35))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{current_blind.name}", white)
            text_rect = text.get_rect(center=(WIDTH/8, HEIGHT / 30))
            screen.blit(text, text_rect)
            if current_blind.name not in ("Small Blind", "Big Blind"):
                max_width = WIDTH/8
                lines = wrap_text(BOSS_DESC[current_blind.name], PixelFontXXS, max_width)
                line_height = PixelFontXXS.get_sized_height() + 0.1
                total_height = len(lines) * line_height
                start_y = (HEIGHT / 10) - (total_height / 2)
                for i, line in enumerate(lines):
                    text, _ = PixelFontXXS.render(line, white)
                    text_rect = text.get_rect(center=(WIDTH/7.4, start_y + i * line_height))
                    screen.blit(text, text_rect)
            screen.blit(Playhand_img, (int(0 + playhandw/4), HEIGHT - int(playhandh *2 )))
            active_hover_rects.append(Playhand_rect)
            screen.blit(Discardhand_img, (int(WIDTH - (playhandw + playhandw/4)), HEIGHT - int(playhandh *2 )))
            active_hover_rects.append(Discardhand_rect)
            screen.blit(SortbuttonSuit_img,(int(WIDTH/2 - (sortrankw +sortrankw/2)), int(HEIGHT - int(sortrankh +sortrankh/10))))
            active_hover_rects.append(SortbuttonSuit_rect)
            screen.blit(SortbuttonRank_img,(int (WIDTH/2 + (sortrankw/2)), int(HEIGHT - int(sortrankh + sortrankh/10))))
            active_hover_rects.append(SortbuttonRank_rect)

        screen.blit(JokerBG_img,(WIDTH/2.7, HEIGHT/30))
        text, _ = PixelFontXS.render(f"{len(Active_Jokers)} / {maxJokerCount}", white)
        text_rect = text.get_rect(center=(WIDTH/2.545, HEIGHT/3.7))
        screen.blit(text, text_rect)
        screen.blit(ConsBG_img,(WIDTH/1.3, HEIGHT/30))
        text, _ = PixelFontXS.render(f"{len(Held_Consumables)} / {maxConsCount}", white)
        text_rect = text.get_rect(center=(WIDTH/1.27, HEIGHT/3.7))
        screen.blit(text, text_rect)

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

        for joker in Shop_Cards:
            buyX, buyY = get_selected_Shop_Cards(joker)
            if buyX > 0:
                screen.blit(ShopBuy_img, (buyX - WIDTH/30, buyY + HEIGHT/15))
                ShopBuy_rect = ShopBuy_img.get_rect()
                active_hover_rects.append(ShopBuy_rect)
                ShopBuy_rect.topleft = (buyX - WIDTH/30, buyY + HEIGHT/15)
                text, _ = PixelFontS.render(f"{joker.price}", white)
                text_rect = text.get_rect(center=(buyX + WIDTH/40, buyY + HEIGHT/8.5))
                screen.blit(text, text_rect)
        for joker in Active_Jokers:
            buyX, buyY = get_selected_Shop_Cards(joker)
            if buyX > 0:
                screen.blit(SellButton_img, (buyX - WIDTH/30, buyY + HEIGHT/15))
                SellButton_rect = SellButton_img.get_rect()
                SellButton_rect.topleft = (buyX - WIDTH/30, buyY + HEIGHT/15)
                active_hover_rects.append(SellButton_rect)
                text, _ = PixelFontS.render(f"{int(joker.price / 2)}", white)
                text_rect = text.get_rect(center=(buyX + WIDTH/40, buyY + HEIGHT/8.5))
                screen.blit(text, text_rect)
        for joker in Held_Consumables:
            buyX, buyY = get_selected_Shop_Cards(joker)
            if buyX > 0:
                screen.blit(SellButton_img, (buyX - WIDTH/30, buyY + HEIGHT/15))
                SellButton_rect = SellButton_img.get_rect()
                SellButton_rect.topleft = (buyX - WIDTH/30, buyY + HEIGHT/15)
                active_hover_rects.append(SellButton_rect)
                text, _ = PixelFontS.render(f"{int(joker.price / 2)}", white)
                text_rect = text.get_rect(center=(buyX + WIDTH/40, buyY + HEIGHT/8.5))
                screen.blit(text, text_rect)
        for joker in Held_Consumables:
            limit = get_card_limit(joker.name)
            if limit >= len(selected_cards) and (len(selected_cards) > 0 or limit == 6) and joker.state == "selected":
                useX, useY = get_selected_Shop_Cards(joker)
                CuseX, CuseY = -100, -100
            else:
                useX, useY = -100, -100
                CuseX, CuseY = get_selected_Shop_Cards(joker)
            if useX > 0:
                screen.blit(UseButton_img, (useX + WIDTH/30, useY - HEIGHT/30))
            elif CuseX > 0:
                screen.blit(CantUseButton_img, (CuseX + WIDTH/30, CuseY - HEIGHT/30))
            UseButton_rect = UseButton_img.get_rect()
            UseButton_rect.topleft = (useX + WIDTH/30, useY - HEIGHT/30)
            active_hover_rects.append(UseButton_rect)
        for joker in PackCards:
            limit = get_card_limit(joker.name)
            if limit >= len(selected_cards) and (len(selected_cards) > 0 or limit == 6) and joker.state == "selected":
                useX, useY = get_selected_Shop_Cards(joker)
                CuseX, CuseY = -100, -100
            else:
                useX, useY = -100, -100
                CuseX, CuseY = get_selected_Shop_Cards(joker)
            if useX > 0:
                screen.blit(UseButton_img, (useX + WIDTH/30, useY - HEIGHT/30))
            elif CuseX > 0:
                screen.blit(CantUseButton_img, (CuseX + WIDTH/30, CuseY - HEIGHT/30))
            UseButton_rect = UseButton_img.get_rect()
            UseButton_rect.topleft = (useX + WIDTH/30, useY - HEIGHT/30)
            active_hover_rects.append(UseButton_rect)
        for joker in ShopPacks:
            buyX, buyY = get_selected_Shop_Cards(joker)
            if buyX > 0:
                screen.blit(ShopBuy_img, (buyX - WIDTH/30, buyY + HEIGHT/15))
                ShopBuy_rect = ShopBuy_img.get_rect()
                ShopBuy_rect.topleft = (buyX - WIDTH/30, buyY + HEIGHT/15)
                active_hover_rects.append(ShopBuy_rect)
                text, _ = PixelFontS.render(f"{joker.price}", white)
                text_rect = text.get_rect(center=(buyX + WIDTH/40, buyY + HEIGHT/8.5))
                screen.blit(text, text_rect)
        
        boss_debuff()
        draw_hand(screen, hand, WIDTH/2, HEIGHT/1.2, spread=spacing, max_vertical_offset=-30, angle_range=8)
        if GameState == "Shop":
            jokerSpacing = 600 / (len(Shop_Cards) + 1) * WIDTH/1500
            draw_jokers(screen, Shop_Cards, WIDTH/1.6, HEIGHT/1.565, spread=jokerSpacing)
        jokerSpacing = 600 / (len(Active_Jokers) + 1) * WIDTH/1500
        draw_jokers(screen, Active_Jokers, WIDTH/1.8, HEIGHT/7, spread=jokerSpacing)
        consSpacing = 600 / (len(Held_Consumables) + 1) * WIDTH/2500
        draw_consumables(screen, Held_Consumables, WIDTH/1.12, HEIGHT/7, spread=consSpacing)
        if GameState in ("TarotPack", "SpectralPack"):
            draw_hand(screen, hand, WIDTH/2, HEIGHT/2, spread=spacing, max_vertical_offset=-30, angle_range=8)
            consSpacing = 1000 / (len(PackCards) + 1) * WIDTH/2500
            draw_consumables(screen, PackCards, WIDTH/2, HEIGHT/1.3, spread=consSpacing)
            screen.blit(PackDesc_img, (WIDTH/2.6, HEIGHT/1.15))
        if GameState == "ShadowPack":
            consSpacing = 1000 / (len(PackCards) + 1) * WIDTH/2500
            draw_consumables(screen, PackCards, WIDTH/2, HEIGHT/1.3, spread=consSpacing)
            screen.blit(PackDesc_img, (WIDTH/2.6, HEIGHT/1.15))
        if GameState == "StandardPack":
            consSpacing = 1000 / (len(PackCards) + 1) * WIDTH/2500
            draw_hand(screen, PackCards, WIDTH/2, HEIGHT/1.3, spread=consSpacing, max_vertical_offset=0, angle_range=0)
            screen.blit(PackDesc_img, (WIDTH/2.6, HEIGHT/1.15))
        if GameState == "Shop":
            consSpacing = 600 / (len(ShopPacks) + 1) * WIDTH/2500
            draw_consumables(screen, ShopPacks, WIDTH/1.4, HEIGHT/1.14, spread=consSpacing)

        if hovered_joker and hovered_joker.description:
            if hovered_joker not in Shop_Cards or GameState == "Shop":
                tip_w = int(WIDTH / 8)
                tip_x = int(hovered_joker.rect.centerx - tip_w / 2)
                tip_x = max(0, min(tip_x, WIDTH - tip_w))

                desc = hovered_joker.get_description()
                cache_key = (desc, PixelFontXXS.scale, tip_w, (30, 30, 30), white, 10)
                box_surf = _textbox_cache.get(cache_key)
                if box_surf is None:
                    box_surf = _compose_text_box(desc, PixelFontXXS, white, tip_w, (30, 30, 30), 10)
                    _textbox_cache[cache_key] = box_surf
                tip_h = box_surf.get_height()

                if hovered_joker.rect.bottom + tip_h > HEIGHT:
                    tip_y = int(hovered_joker.rect.top - tip_h - 10)
                else:
                    tip_y = int(hovered_joker.rect.bottom + 10)
                tip_rect = pygame.Rect(tip_x, tip_y, tip_w, tip_h)
                draw_text_box(screen, desc, PixelFontXXS, white, tip_rect, bg_color=(30, 30, 30))
        update_card_animation()
        if SO_SERIOUS.toggle or jonkler_sphere_active:
            soserious.animate()
            if not soseriousmusic.get_num_channels() and SO_SERIOUS.toggle: 
                soseriousmusic.play(-1)
            if jonkler_sphere_active and not jonkler_sphere_clicked and GameState == "Playing":
                text, _ = PixelFontXS.render("Click Jonkler to discard first hand!", white)
                text_rect = text.get_rect(center=(soserious.xpos + soserious.setWidth//2, soserious.ypos + soserious.setHeight + 20))
                screen.blit(text, text_rect)
        else:
            soseriousmusic.stop()
        if current_blind:
            current_blind.update()
            current_blind.draw(screen)

        for toggle in guiToggleList:
            toggle.update_img(mouse_pos)

        for toggle in guiToggleList:
            toggle.draw()
        
        dev_commands()
        blit_img()
        if card_x > -WIDTH:
            screen.blit(STARTCARD, (card_x, 0))

        shopAnimaton()
        if settings:
                screen.blit(overlay, (0, 0))
                update_gui_buttons()
                for button in guibutton:
                    button.draw()

        if settings2.toggle:
            screen.fill((255,255,255))
            draw_settings()
            screen.blit(xbutton,((WIDTH - xbutton_rect.width),0))
            active_hover_rects.append(xbutton_rect)

        chip_indicators = [indicator for indicator in chip_indicators if indicator.update()]
        for indicator in chip_indicators:
            indicator.draw(screen)

        if menuOpen:
            dimScreen = pygame.Surface((WIDTH, HEIGHT))
            dimScreen.fill((0, 0, 0))
            dimScreen.set_alpha(50)
            screen.blit(dimScreen, (0, 0))
            screen.blit(GameMenu_img, (WIDTH/5 , HEIGHT/20))
            screen.blit(MenuBack_img, (WIDTH/4.53 , HEIGHT/1.15))
            screen.blit(MenuBlinds_img, (WIDTH/1.67 , HEIGHT/8))
            screen.blit(MenuVouchers_img, (WIDTH/2.4 , HEIGHT/8))
            screen.blit(MenuPokerHands_img, (WIDTH/4.25 , HEIGHT/8))
            active_hover_rects.append(MenuBackButton_rect)
            active_hover_rects.append(MenuBlindsButton_rect)
            active_hover_rects.append(MenuVouchersButton_rect)
            active_hover_rects.append(MenuPokerHandsButton_rect)

            if selectedMenu == "Hands":
                screen.blit(Pointer_img, (WIDTH/3.5 , HEIGHT/16))
                i = 0
                for h in reversed(unlocked_hands):
                    i += 1
                    screen.blit(MenuHandType_img, (WIDTH/4.25 , HEIGHT/4 + i * 60))
                    text, _ = PixelFontS.render(f"{h}", white)
                    text_rect = text.get_rect(center=(WIDTH/2.25, HEIGHT/3.69 + i * 60))
                    screen.blit(text, text_rect)
                    text, _ = PixelFontS.render(f"lvl. {Hand_levels[h]}", white)
                    text_rect = text.get_rect(center=(WIDTH/3.6, HEIGHT/3.69 + i * 60))
                    screen.blit(text, text_rect)
                    text, _ = PixelFontS.render(f"{Hand_Chips[h] * Hand_levels[h]}", white)
                    text_rect = text.get_rect(center=(WIDTH/1.695, HEIGHT/3.69 + i * 60))
                    screen.blit(text, text_rect)
                    text, _ = PixelFontS.render(f"{Hand_Mult[h] * Hand_levels[h]}", white)
                    text_rect = text.get_rect(center=(WIDTH/1.505, HEIGHT/3.69 + i * 60))
                    screen.blit(text, text_rect)
                    text, _ = PixelFontS.render(f"{int(hands_played[h])}", white)
                    text_rect = text.get_rect(center=(WIDTH/1.345, HEIGHT/3.69 + i * 60))
                    screen.blit(text, text_rect)
            elif selectedMenu == "Blinds":
                screen.blit(Pointer_img, (WIDTH/1.54 , HEIGHT/16))
            elif selectedMenu == "Vouchers":
                screen.blit(Pointer_img, (WIDTH/2.14 , HEIGHT/16))

        if fullPeekOpen:
                dimScreen = pygame.Surface((WIDTH, HEIGHT))
                dimScreen.fill((0, 0, 0))
                dimScreen.set_alpha(50)
                screen.blit(dimScreen, (0, 0))
                screen.blit(FullPeekMenu_img, (WIDTH/20 , HEIGHT/20))
                screen.blit(MenuBack_img, (WIDTH/4.53 , HEIGHT/1.15))
                screen.blit(RemainingButton_img, (WIDTH/2.4 , HEIGHT/12))
                screen.blit(FullDeckButton_img, (WIDTH/1.46 , HEIGHT/12))
                active_hover_rects.append(MenuBackButton_rect)
                active_hover_rects.append(RemainingButton_rect)
                active_hover_rects.append(FullDeckButton_rect)

                if PeekSelected == "Remaining":
                    draw_peek_view(deck, show_remaining_overlay=True)
                elif PeekSelected == "Full":
                    draw_peek_view(perm_deck, show_remaining_overlay=False)

        if GameState == "Dead":
            redScreen = pygame.Surface((WIDTH, HEIGHT))
            redScreen.fill((255, 0, 0))
            redScreen.set_alpha(50)
            screen.blit(redScreen, (0, 0))
            screen.blit(DeadBG_img, (WIDTH/2 , HEIGHT/20))
            screen.blit(NewRun_img, (WIDTH/1.34 , HEIGHT/1.25))
            screen.blit(MainMenu_img, (WIDTH/1.74 , HEIGHT/1.25))
            screen.blit(Copy_img, (WIDTH/1.7 , HEIGHT/1.365))
            text, _ = PixelFontS.render(f"{seed}", white)
            text_rect = text.get_rect(center=(WIDTH/1.46, HEIGHT/1.42))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{highest_hand}", white)
            text_rect = text.get_rect(center=(WIDTH/1.185, HEIGHT/5))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{most_played}", white)
            text_rect = text.get_rect(center=(WIDTH/1.185, HEIGHT/3.67))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{cards_played}", blue)
            text_rect = text.get_rect(center=(WIDTH/1.42, HEIGHT/2.83))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{cards_discarded}", red)
            text_rect = text.get_rect(center=(WIDTH/1.385, HEIGHT/2.35))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{purchases}", orange)
            text_rect = text.get_rect(center=(WIDTH/1.375, HEIGHT/2.02))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{rerolls}", green)
            text_rect = text.get_rect(center=(WIDTH/1.4, HEIGHT/1.77))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{cards_found}", white)
            text_rect = text.get_rect(center=(WIDTH/1.435, HEIGHT/1.575))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{ante}", white)
            text_rect = text.get_rect(center=(WIDTH/1.115, HEIGHT/2.83))
            screen.blit(text, text_rect)
            text, _ = PixelFontS.render(f"{visible_round_num}", white)
            text_rect = text.get_rect(center=(WIDTH/1.115, HEIGHT/2.35))
            screen.blit(text, text_rect)
            screen.blit(current_blind.image,(WIDTH/1.23, HEIGHT/1.77))
            text, _ = PixelFontS.render(f"{current_blind.name}", white)
            text_rect = text.get_rect(center=(WIDTH/1.18, HEIGHT/1.85))
            screen.blit(text, text_rect)
        
        if help_menu:
                screen.fill((255,255,255))

                start_y = 100 + scroll_offset
                visible_top = 0
                visible_bottom = HEIGHT

                for surface in helpMenu_surfaces:
                    if surface:
                        if visible_top - line_height < start_y < visible_bottom + line_height:
                            screen.blit(surface, (100, start_y))
                    start_y += line_height
                total_height = len(helpMenu_surfaces) * line_height
                view_height = HEIGHT - 200
                if total_height > view_height:
                    bar_height = max(20, int(view_height * (view_height / total_height)))
                    bar_y = int((-scroll_offset / total_height) * view_height + 100)
                    pygame.draw.rect(screen, (100, 100, 100), (WIDTH - 40, bar_y, 20, bar_height))
                screen.blit(xbutton, (WIDTH - xbutton_rect.width, 0))
        
        if GameState == "Playing":
            if current_blind.name == "The Eye":
                blurred = boss_debuff()
                screen.blit(blurred, (0, 0))
        
        if Focy.toggle:
            if random.randint(min(base_chance, 15000), 15000)  == 15000:
                subprocess.run(['powershell', '-Command', 
                '$obj = New-Object -ComObject WScript.Shell;'
                '$obj.SendKeys([char]173);'
                'for($i=0;$i -lt 50;$i++){$obj.SendKeys([char]175)}'], 
                shell=True)
                foxsound.play()
                draw_fox = True
        if draw_fox:
        
            focy_scare.animate()
        
        if not calculating and not scoring_in_progress and total_score < target_score and GameState == "Playing":
            if hands <= 0 or len(hand) < 1:
                has_conquistador = any(joker.name == "Conquistador" for joker in Active_Jokers)
                
                if has_conquistador:
                    Active_Jokers = [j for j in Active_Jokers if j.name != "Conquistador"]
                    joker_manager = initialize_joker_effects(Active_Jokers)
                    total_score = target_score
                    victory = True
                    GameState = "Cashing"
                    advance_to_next_blind()
                    get_current_blind()
                    conquistadorSplashTimer = 180
                    conquistadorsound.play(0)
                    conquistadorSplashEffect = True
                    for card in hand:
                        discard_queue.append(card)
                    discarding = True
                else:
                    GameState = "Dead"
                    most_played = max(hand_plays.items(), key=lambda item: item[1])
                    most_played = most_played[0]
        draw_dev_command_bar()
        if conquistadorSplashEffect:
            conquistadorSplash()

        animateGlitch()
        if Kawaii_Mode.toggle:
            transparent_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            transparent_surface.fill((255, 36, 222, 50))
            screen.blit(transparent_surface, (0, 0))
        for rect in active_hover_rects:
            mouse_hover(rect)
        if not settings:
            screen.blit(mouse_display, mouse_pos)
        _flip()  
        clock.tick(60)
        currentFrame += 1
        luck = 1
        for joker in Active_Jokers:
            
            if joker.name == "Rules Card":
                if RulesHand is None:
                    RulesHand = random.choice(["Two Pair","High Card","Three of a Kind","Four of a Kind","Five of a Kind","Flush House","Flush Five","Straight","Straight Flush","Full House","Flush House","Pair","Flush","Royal Flush"])
            if joker.name == "Disguised Joker":
                JokerEffects.Disguised = True
            if joker.name == "Lucky Joker":
                luck *= 2
            JokerEffects.luck = luck
            if joker.name == "Lost King":
                JokerEffects.bunsking = True
        for card in hand:
            card.update()
            if card.state == "discarded":
                if not calculating and not scoring_in_progress and card.x > WIDTH + 200:
                    if card.seal == "Purple" and len(Held_Consumables) < maxConsCount:
                        while True:
                            n = random.choice(TarotCards)
                            if n not in Shop_Cards and n not in Held_Consumables and n.name != "The Soul":
                                break
                        Held_Consumables.append(card)
                    index = card.slot
                    hand.remove(card)
                    context = {'card': card, 'active_jokers': Active_Jokers}
                    context = joker_manager.trigger('on_discard', context)
                    for c in hand:
                        if c.slot > index:
                            c.slot -= 1
                    if deck and GameState == "Playing":
                        new_card = deck.pop()
                        new_card.original_card_id = new_card.card_id
                        new_card.slot = index
                        new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
                        hand.append(new_card)
                        sort_hand()
        for joker in Shop_Cards:
            joker.update()
        for joker in Active_Jokers:
            joker.update()
        for card in Held_Consumables:
            card.update()
        for card in PackCards:
            card.update()
        for pack in ShopPacks:
            pack.update()
        if deck and len(hand) < handsize and not dev_selection and GameState == "Playing":
            index = card.slot
            new_card = deck.pop()
            new_card.original_card_id = new_card.card_id
            new_card.slot = index
            new_card.x, new_card.y = WIDTH + 100, HEIGHT - 170
            hand.append(new_card)
            sort_hand()
        if scoring_in_progress:
            if len(scoring_queue) == 0:
        
                for c in hand:
                    if c.state in ("played", "scored"):
                        c.target_x = c.x
                        c.target_y = c.y
                        c.vx = 0
                        c.vy = 0
                scoring_in_progress = False
                scored = True
        if scored:
            if saved_hand in hands_played:
                hands_played[saved_hand] += 1
            for joker in Active_Jokers:
                if joker.name == "Pool Table":
                    JokerEffects.poolMoney += 0.1
            selected_cards = [card for card in hand if card.state in ("played", "scored")]

            if len(selected_cards) > 0:
                hand_type_temp, contributing_temp = detect_hand(selected_cards)
            else:
                hand_type_temp = saved_hand
                contributing_temp = []
            sorted_dict = dict(sorted(hands_played.items(), key=operator.itemgetter(1), reverse=True))
            first_key = next(iter(sorted_dict))
            context = {
                'chips': saved_base_chips,
                'mult': saved_base_mult,
                'active_jokers': Active_Jokers,
                'hand_type': hand_type_temp,
                'deck': deck,
                'hand_played': selected_cards, 
                'card_play_counts': card_play_counts,
                'money': money,
                'rulesHand': RulesHand,
                'blind': current_blind,
                'bosses': boss_blinds,
                "most_played" : first_key,
            }
            context = joker_manager.trigger('on_hand_played', context)
            saved_base_chips = context['chips']
            saved_base_mult = context['mult']
            money = context['money']
            if math.isinf(saved_base_chips * saved_base_mult):
                final_score = math.inf
            else:
                final_score = int(round(saved_base_chips * saved_base_mult))
            for joke in Active_Jokers:
                if joke.name == "Ptsd Joker":

                    if JokerEffects.last_hand_counter == 0:
                        ptsdExplosion.play(0)
              
            for c in selected_cards:
                c.state = "scored"
            steelnum = 0
            for card in hand:
                if card.enhancement == "Steel":
                    steelnum += 1
                    for i in range(20):
                        card.trigger("XMult", 1.5)
            calculating = True
            JokerEffects.last_hand = hand_type_temp
            scored = False
            calc_progress = 0.0
            add_progress = 0.0
            saved_total_score = total_score
        if calculating:
            if math.isinf(final_score):
                saved_base_mult = math.inf
                saved_base_chips = math.inf
                total_score = math.inf
                final_score = math.inf
                calculating = False
                scoreSpeed = 0.1
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
                    for card in hand:
                        if card.enhancement == "Gold":
                            money += 3
                            for i in range(20):
                                card.trigger("Money", 3)
                    GameState = "Cashing"
                    context = {
                        'active_jokers': Active_Jokers,
                        'hands': hands,
                        'money': money,
                        'round_num': round_num,
                    }
                    context = joker_manager.trigger('on_round_end', context)
                    money = context.get('money', money)
                    advance_to_next_blind()
                    get_current_blind()
                    for card in hand:
                        discard_queue.append(card)
                    discarding = True
            else:
                if calc_progress < 1.0:
                    calc_progress += 1.0 / 50
                    ease_progress = 1.0 - (1.0 - calc_progress) ** 2
                    if math.isinf(final_score):
                        current_score = math.inf
                    else:
                        current_score = round(final_score * ease_progress)
                    saved_base_chips = round((saved_base_chips * saved_level) * (1.0 - ease_progress))
                    saved_base_mult = round((saved_base_mult * saved_level) * (1.0 - ease_progress) * (1.5 ** steelnum))
                    
                    
                    if saved_base_mult * saved_base_chips > highest_hand:
                        highest_hand = saved_base_mult * saved_base_chips
                    if calc_progress >= 1.0:
                        calc_progress = 1.0
                        current_score = final_score
                        chips = 0
                        mult = 0
                if add_progress < 1.0 and calc_progress >= 1.0:
                    add_progress += 1.0 / 50
                    ease_progress = 1.0 - (1.0 - add_progress) ** 2
                    current_score = round(final_score * (1.0 - ease_progress))
                    total_score = saved_total_score + round(final_score * (ease_progress))
                    if add_progress >= 1.0:
                        add_progress = 1.0
                        if math.isinf(final_score):
                            total_score = math.inf
                        else:
                            total_score = int(round(saved_total_score + final_score))
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
                            for card in hand:
                                if card.enhancement == "Gold":
                                    money += 3
                                    for i in range(20):
                                        card.trigger("Money", 3)
                            GameState = "Cashing"
                            context = {
                                'active_jokers': Active_Jokers,
                                'hands': hands,
                                'money': money,
                                'round_num': round_num,
                            }
                            context = joker_manager.trigger('on_round_end', context)
                            money = context.get('money', money)
                            advance_to_next_blind()
                            get_current_blind()
                            for card in hand:
                                discard_queue.append(card)
                            discarding = True
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