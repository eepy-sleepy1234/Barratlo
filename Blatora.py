# ----------------------------
# Pygame setup & constants
# ----------------------------
import pygame
import random
import sys
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple
from collections import Counter

pygame.init()
pygame.display.set_caption("Enhanced Balatro-Style Card Game")

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 120, 220)
GREEN = (50, 180, 50)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (45, 45, 55)
DARKER_GRAY = (25, 25, 35)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 200, 200)
DARK_RED = (150, 30, 30)

CARD_WIDTH = 80
CARD_HEIGHT = 110
HAND_Y = SCREEN_HEIGHT - CARD_HEIGHT - 40

# ----------------------------
# Enums & Data
# ----------------------------
class Suit(Enum):
    HEARTS = ("♥", RED)
    DIAMONDS = ("♦", RED)
    CLUBS = ("♣", BLACK)
    SPADES = ("♠", BLACK)

class Rank(Enum):
    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("J", 11)
    QUEEN = ("Q", 12)
    KING = ("K", 13)
    ACE = ("A", 14)

class HandType(Enum):
    HIGH_CARD = ("High Card", 1, 5)
    PAIR = ("Pair", 2, 10)
    TWO_PAIR = ("Two Pair", 2, 20)
    THREE_KIND = ("Three of a Kind", 3, 30)
    STRAIGHT = ("Straight", 4, 30)
    FLUSH = ("Flush", 4, 35)
    FULL_HOUSE = ("Full House", 4, 40)
    FOUR_KIND = ("Four of a Kind", 7, 60)
    STRAIGHT_FLUSH = ("Straight Flush", 8, 100)
    ROYAL_FLUSH = ("Royal Flush", 10, 300)

class BlindType(Enum):
    SMALL = ("Small Blind", "A modest challenge", 1.0, False)
    BIG = ("Big Blind", "A standard test", 1.0, False)
    WHEEL = ("The Wheel", "Cards play in random order", 1.2, False)
    WALL = ("The Wall", "Extra large target score", 2.0, False)
    HOUSE = ("The House", "First hand is worth nothing", 1.1, False)
    PLANT = ("The Plant", "All face cards are debuffed", 1.3, False)
    PILLAR = ("The Pillar", "Cards played are drawn face down", 1.1, False)
    NEEDLE = ("The Needle", "Play only 1 hand", 1.0, False)
    MARK = ("The Mark", "All spades are debuffed", 1.2, False)
    FISH = ("The Fish", "Start after playing 2 hands", 1.3, False)
    # Boss blinds (cannot be skipped)
    CRIMSON_HEART = ("The Crimson Heart", "Hearts give no chip bonus", 1.5, True)
    VERDANT_LEAF = ("The Verdant Leaf", "All cards face down until played", 2.0, True)
    VIOLET_VESSEL = ("The Violet Vessel", "Very large target score", 3.0, True)

@dataclass
class Card:
    suit: Suit
    rank: Rank
    selected: bool = False
    x: float = 0
    y: float = 0
    target_x: float = 0
    target_y: float = 0
    scale: float = 1.0
    target_scale: float = 1.0
    rotation: float = 0.0
    hover: bool = False
    play_effect_timer: float = 0.0
    contributes_to_hand: bool = False

    def get_color(self):
        return self.suit.value[1]

    def get_display_rank(self):
        return self.rank.value[0]

    def get_numeric_value(self):
        return self.rank.value[1]

    def get_chip_value(self):
        """Get chip value for scoring (different from poker value)"""
        if self.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        elif self.rank == Rank.ACE:
            return 11
        else:
            return self.rank.value[1]

    def get_suit_symbol(self):
        return self.suit.value[0]

    def update_animation(self, dt):
        # Smoother animations with higher lerp factors
        self.x += (self.target_x - self.x) * 18 * dt
        self.y += (self.target_y - self.y) * 18 * dt
        self.scale += (self.target_scale - self.scale) * 20 * dt
        if self.play_effect_timer > 0:
            self.play_effect_timer -= dt

def evaluate_hand(cards: List[Card]) -> Tuple[HandType, int, List[Card]]:
    """Evaluate poker hand and return hand type, base score, and contributing cards"""
    if len(cards) < 1:
        return HandType.HIGH_CARD, 0, []
    
    # Reset all contribution flags first
    for card in cards:
        card.contributes_to_hand = False
    
    # Sort cards by rank
    sorted_cards = sorted(cards, key=lambda c: c.get_numeric_value())
    ranks = [c.get_numeric_value() for c in sorted_cards]
    suits = [c.suit for c in sorted_cards]
    
    # Count ranks
    rank_counts = Counter(ranks)
    count_values = sorted(rank_counts.values(), reverse=True)
    
    # Check for flush
    is_flush = len(set(suits)) == 1 and len(cards) == 5
    
    # Check for straight
    is_straight = False
    if len(cards) == 5:
        if ranks == list(range(ranks[0], ranks[0] + 5)):
            is_straight = True
        # Special case: A-2-3-4-5 straight
        elif ranks == [2, 3, 4, 5, 14]:
            is_straight = True
    
    # Determine hand type and contributing cards
    contributing_cards = []
    hand_type = None
    
    if is_straight and is_flush:
        if ranks == [10, 11, 12, 13, 14]:
            hand_type = HandType.ROYAL_FLUSH
        else:
            hand_type = HandType.STRAIGHT_FLUSH
        contributing_cards = sorted_cards  # All 5 cards contribute
    elif len(count_values) > 0 and count_values[0] == 4:
        hand_type = HandType.FOUR_KIND
        # Find the four of a kind
        four_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
        contributing_cards = [c for c in cards if c.get_numeric_value() == four_rank]
    elif len(count_values) > 1 and count_values[0] == 3 and count_values[1] == 2:
        hand_type = HandType.FULL_HOUSE
        contributing_cards = sorted_cards  # All 5 cards contribute
    elif is_flush:
        hand_type = HandType.FLUSH
        contributing_cards = sorted_cards  # All 5 cards contribute
    elif is_straight:
        hand_type = HandType.STRAIGHT
        contributing_cards = sorted_cards  # All 5 cards contribute
    elif len(count_values) > 0 and count_values[0] == 3:
        hand_type = HandType.THREE_KIND
        # Find the three of a kind
        three_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        contributing_cards = [c for c in cards if c.get_numeric_value() == three_rank]
    elif len(count_values) > 1 and count_values[0] == 2 and count_values[1] == 2:
        hand_type = HandType.TWO_PAIR
        # Find both pairs
        pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
        contributing_cards = [c for c in cards if c.get_numeric_value() in pair_ranks]
    elif len(count_values) > 0 and count_values[0] == 2:
        hand_type = HandType.PAIR
        # Find the pair
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        contributing_cards = [c for c in cards if c.get_numeric_value() == pair_rank]
    else:
        hand_type = HandType.HIGH_CARD
        # Only the highest card contributes
        highest_rank = max(ranks)
        contributing_cards = [c for c in cards if c.get_numeric_value() == highest_rank][:1]
    
    # Mark contributing cards
    for card in contributing_cards:
        card.contributes_to_hand = True
    
    # Calculate base score from only contributing cards
    base_score = sum(c.get_chip_value() for c in contributing_cards)
    
    return hand_type, base_score, contributing_cards

# ----------------------------
# Core Game State
# ----------------------------
class GameState:
    def __init__(self):
        self.deck: List[Card] = []
        self.hand: List[Card] = []
        self.selected_cards: List[Card] = []
        self.played_cards: List[Card] = []
        self.score = 0
        self.target_score = 300
        self.hands_left = 4
        self.discards_left = 3
        self.money = 4
        self.last_sort_type: Optional[str] = 'rank'
        self.last_hand_type: Optional[HandType] = None
        self.last_hand_score = 0
        self.round_number = 1
        self.current_blind: BlindType = BlindType.SMALL
        self.next_blind: BlindType = BlindType.BIG
        self.game_phase = "blind_select"  # "blind_select", "playing", "shop", or "scoring"
        self.money_earned_this_blind = 0
        self.initial_deck_size = 52
        
        # Blind selection variables
        self.blind_pool = list(BlindType)
        self.blind_index = 0
        
        # Scoring animation variables
        self.scoring_cards: List[Card] = []
        self.scoring_timer = 0.0
        self.scoring_stage = 0  # 0: setup, 1: base chips, 2: card chips, 3: multiply, 4: complete
        self.current_chips = 0
        self.current_multiplier = 0
        self.base_chips = 0
        self.card_chip_index = 0
        self.final_score = 0
        self.contributing_cards: List[Card] = []

        self.setup_initial_blinds()

    def setup_initial_blinds(self):
        """Set up the initial blind progression"""
        self.current_blind = BlindType.SMALL
        self.next_blind = BlindType.BIG
        self.blind_index = 0

    def get_next_blind_after(self, blind: BlindType) -> BlindType:
        """Get the next blind in progression"""
        blind_sequence = [
            BlindType.SMALL, BlindType.BIG, BlindType.WHEEL,
            BlindType.WALL, BlindType.HOUSE, BlindType.PLANT,
            BlindType.PILLAR, BlindType.NEEDLE, BlindType.MARK, BlindType.FISH,
            BlindType.CRIMSON_HEART, BlindType.VERDANT_LEAF, BlindType.VIOLET_VESSEL
        ]
        
        try:
            current_index = blind_sequence.index(blind)
            if current_index + 1 < len(blind_sequence):
                return blind_sequence[current_index + 1]
            else:
                # Loop back to harder blinds
                return random.choice([BlindType.CRIMSON_HEART, BlindType.VERDANT_LEAF, BlindType.VIOLET_VESSEL])
        except ValueError:
            return BlindType.BIG

    def select_blind(self):
        """Player chooses to play the current blind"""
        self.game_phase = "playing"
        # Apply blind modifiers
        self.target_score = int(300 * (1.5 ** (self.round_number - 1)) * self.current_blind.value[2])
        self.create_deck()
        self.deal_hand()

    def skip_blind(self):
        """Player chooses to skip the blind for a reward"""
        if self.current_blind.value[3]:  # Can't skip boss blinds
            return
        
        # Give skip reward
        skip_reward = max(5, self.round_number * 2)
        self.money += skip_reward
        
        # Move to next blind
        self.current_blind = self.next_blind
        self.next_blind = self.get_next_blind_after(self.current_blind)
        self.round_number += 1

    def create_deck(self):
        self.deck = [Card(s, r) for s in Suit for r in Rank]
        random.shuffle(self.deck)
        self.initial_deck_size = len(self.deck)

    def deal_hand(self):
        self.hand = []
        cards_to_deal = min(8, len(self.deck))
        
        for i in range(cards_to_deal):
            if self.deck:
                card = self.deck.pop()
                card.x = SCREEN_WIDTH + 100 + i * 20
                card.y = HAND_Y
                card.scale = 0.5
                card.target_scale = 1.0
                self.hand.append(card)
        
        self.position_hand_cards()
        self.auto_sort_hand()

    def position_hand_cards(self):
        """Position cards evenly across the bottom of the screen"""
        if not self.hand:
            return
            
        total_width = len(self.hand) * CARD_WIDTH + (len(self.hand) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, card in enumerate(self.hand):
            card.target_x = start_x + i * (CARD_WIDTH + 10)
            card.target_y = HAND_Y - (30 if card.selected else 0)

    def toggle_card_selection(self, card):
        if card in self.hand and self.game_phase == "playing":
            if card.selected:
                # Deselecting a card
                card.selected = False
                if card in self.selected_cards:
                    self.selected_cards.remove(card)
            else:
                # Selecting a card - check if we're at the 5 card limit
                if len(self.selected_cards) < 5:
                    card.selected = True
                    if card not in self.selected_cards:
                        self.selected_cards.append(card)
                # If at limit, don't select the card
            
            self.position_hand_cards()

    def update_game(self, dt):
        """Update game logic including animations"""
        # Update scoring animation
        self.update_scoring_animation(dt)
        
        # Update card animations
        for card in self.hand + self.scoring_cards + self.played_cards:
            card.update_animation(dt)

    def auto_sort_hand(self):
        if self.last_sort_type == 'rank':
            self.sort_hand_by_rank()
        elif self.last_sort_type == 'suit':
            self.sort_hand_by_suit()
        else:
            self.sort_hand_by_rank()

    def sort_hand_by_rank(self):
        self.hand.sort(key=lambda c: c.get_numeric_value())
        self.last_sort_type = 'rank'
        self.position_hand_cards()

    def sort_hand_by_suit(self):
        suit_order = {Suit.SPADES: 0, Suit.HEARTS: 1, Suit.DIAMONDS: 2, Suit.CLUBS: 3}
        self.hand.sort(key=lambda c: (suit_order[c.suit], c.get_numeric_value()))
        self.last_sort_type = 'suit'
        self.position_hand_cards()

    def play_selected_cards(self):
        if not self.selected_cards or self.hands_left <= 0 or self.game_phase != "playing":
            return
            
        # Start scoring animation
        self.start_scoring_animation()

    def start_scoring_animation(self):
        """Initialize the scoring animation"""
        self.game_phase = "scoring"
        self.scoring_cards = self.selected_cards.copy()
        self.scoring_timer = 0.0
        self.scoring_stage = 0
        self.current_chips = 0
        self.current_multiplier = 1
        self.card_chip_index = 0
        
        # Evaluate the hand and get contributing cards
        hand_type, base_score, contributing_cards = evaluate_hand(self.selected_cards)
        self.last_hand_type = hand_type
        self.base_chips = hand_type.value[2]  # Base chips from hand type
        self.current_multiplier = hand_type.value[1]  # Multiplier from hand type
        self.contributing_cards = contributing_cards
        self.final_score = (base_score + self.base_chips) * self.current_multiplier
        
        # Position cards for scoring animation
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 100
        card_spacing = 100
        start_x = center_x - (len(self.scoring_cards) - 1) * card_spacing // 2
        
        for i, card in enumerate(self.scoring_cards):
            card.target_x = start_x + i * card_spacing
            card.target_y = center_y
            card.target_scale = 1.2
            card.selected = False  # Remove selection highlight

    def update_scoring_animation(self, dt):
        """Update the scoring animation"""
        if self.game_phase != "scoring":
            return
            
        self.scoring_timer += dt
        
        if self.scoring_stage == 0:  # Setup stage
            if self.scoring_timer > 0.8:  # Wait for cards to position
                self.scoring_stage = 1
                self.scoring_timer = 0.0
                
        elif self.scoring_stage == 1:  # Add base chips
            if self.scoring_timer > 0.4:
                self.current_chips += self.base_chips
                self.scoring_stage = 2
                self.scoring_timer = 0.0
                
        elif self.scoring_stage == 2:  # Add card chips one by one (only contributing cards)
            if self.scoring_timer > 0.25:
                if self.card_chip_index < len(self.contributing_cards):
                    card = self.contributing_cards[self.card_chip_index]
                    # Add bounce effect to current card
                    card.target_scale = 1.4
                    card.play_effect_timer = 0.25
                    # Add chip value
                    self.current_chips += card.get_chip_value()
                    self.card_chip_index += 1
                    self.scoring_timer = 0.0
                    
                    # Reset scale after bounce
                    if self.card_chip_index > 1:
                        self.contributing_cards[self.card_chip_index - 2].target_scale = 1.2
                else:
                    # Reset last card scale and move to multiply stage
                    if self.contributing_cards:
                        self.contributing_cards[-1].target_scale = 1.2
                    self.scoring_stage = 3
                    self.scoring_timer = 0.0
                    
        elif self.scoring_stage == 3:  # Show multiplication
            if self.scoring_timer > 0.8:
                self.scoring_stage = 4
                self.scoring_timer = 0.0
                
        elif self.scoring_stage == 4:  # Complete scoring
            if self.scoring_timer > 0.4:
                self.complete_scoring_animation()

    def complete_scoring_animation(self):
        """Complete the scoring animation and update game state"""
        # Store for display
        self.last_hand_score = self.final_score
        
        # Update game state
        self.score += self.final_score
        self.hands_left -= 1
        
        # Add money based on contributing cards only
        money_earned = max(1, len(self.contributing_cards))
        self.money += money_earned
        self.money_earned_this_blind += money_earned
        
        # Remove cards from hand
        for card in self.selected_cards:
            if card in self.hand:
                self.hand.remove(card)
                self.played_cards.append(card)
        
        self.selected_cards = []
        self.scoring_cards = []
        self.contributing_cards = []
        self.game_phase = "playing"
        self.position_hand_cards()
        
        # Deal new cards if deck has cards
        self.refill_hand()
        
        # Check win/lose conditions
        if self.score >= self.target_score:
            self.enter_shop()
        elif self.hands_left <= 0 and self.score < self.target_score:
            self.game_over()

    def discard_selected_cards(self):
        if not self.selected_cards or self.discards_left <= 0 or self.game_phase != "playing":
            return
            
        # Remove cards from hand
        for card in self.selected_cards:
            if card in self.hand:
                self.hand.remove(card)
                
        self.selected_cards = []
        self.discards_left -= 1
        
        # Deal new cards if deck has cards
        self.refill_hand()
        
        # Auto-sort after discarding
        self.auto_sort_hand()

    def refill_hand(self):
        """Refill hand to 8 cards if possible"""
        cards_needed = 8 - len(self.hand)
        cards_to_deal = min(cards_needed, len(self.deck))
        
        for i in range(cards_to_deal):
            if self.deck:
                card = self.deck.pop()
                card.x = SCREEN_WIDTH + 100 + i * 20
                card.y = HAND_Y
                card.scale = 0.5
                card.target_scale = 1.0
                self.hand.append(card)
        
        self.position_hand_cards()

    def enter_shop(self):
        """Enter shop phase"""
        self.game_phase = "shop"
        # Clear played cards
        self.played_cards = []

    def advance_blind(self):
        """Advance to next blind selection"""
        self.round_number += 1
        self.hands_left = 4
        self.discards_left = 3
        self.score = 0
        self.money_earned_this_blind = 0
        self.game_phase = "blind_select"
        
        # Update blind progression
        self.current_blind = self.next_blind
        self.next_blind = self.get_next_blind_after(self.current_blind)

    def game_over(self):
        """Handle game over"""
        # For now, just reset the game
        self.__init__()

# ----------------------------
# Main Game Class
# ----------------------------
class BalatroGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 64)
        self.game_state = GameState()
        self.hovered_card: Optional[Card] = None

        # Gameplay Buttons
        self.PLAY_BUTTON = pygame.Rect(60, SCREEN_HEIGHT - 180, 140, 50)
        self.DISCARD_BUTTON = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 180, 140, 50)
        self.SORT_RANK_BUTTON = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 260, 140, 40)
        self.SORT_SUIT_BUTTON = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 260, 140, 40)
        
        # Shop Buttons
        self.CONTINUE_BUTTON = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60)
        self.SHOP_ITEM_1 = pygame.Rect(SCREEN_WIDTH // 2 - 300, 200, 180, 120)
        self.SHOP_ITEM_2 = pygame.Rect(SCREEN_WIDTH // 2 - 90, 200, 180, 120)
        self.SHOP_ITEM_3 = pygame.Rect(SCREEN_WIDTH // 2 + 120, 200, 180, 120)
        
        # Blind Selection Buttons
        self.PLAY_BLIND_BUTTON = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 150, 120, 60)
        self.SKIP_BLIND_BUTTON = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 150, 120, 60)

    def wrap_text(self, text, max_width, font):
        """Wrap text to fit within a given width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    def draw_button(self, rect: pygame.Rect, text, color, hover_color=LIGHT_GRAY, enabled=True):
        mx, my = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mx, my)
        rect_color = hover_color if (is_hover and enabled) else color
        if not enabled:
            rect_color = GRAY
        pygame.draw.rect(self.screen, rect_color, rect, border_radius=12)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=12)
        label = self.button_font.render(text, True, BLACK if enabled else DARKER_GRAY)
        label_rect = label.get_rect(center=rect.center)
        self.screen.blit(label, label_rect)

    def draw_card(self, card: Card):
        """Draw a playing card"""
        # Calculate position and scale
        x = int(card.x)
        y = int(card.y)
        width = int(CARD_WIDTH * card.scale)
        height = int(CARD_HEIGHT * card.scale)
        
        # Card background
        card_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Draw card background
        bg_color = GOLD if card.selected else WHITE
        if card.contributes_to_hand and card.play_effect_timer > 0:
            # Glowing effect for contributing cards
            glow_size = int(5 * (card.play_effect_timer * 4))
            glow_rect = pygame.Rect(x - width//2 - glow_size, y - height//2 - glow_size, 
                                  width + glow_size*2, height + glow_size*2)
            pygame.draw.rect(self.screen, CYAN, glow_rect, border_radius=8)
        
        pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, card_rect, 2, border_radius=8)
        
        # Draw rank and suit
        color = card.get_color()
        rank_text = self.font.render(card.get_display_rank(), True, color)
        suit_text = self.font.render(card.get_suit_symbol(), True, color)
        
        # Position text based on card size
        rank_pos = (x - width//2 + 8, y - height//2 + 5)
        suit_pos = (x - width//2 + 8, y - height//2 + 25)
        
        self.screen.blit(rank_text, rank_pos)
        self.screen.blit(suit_text, suit_pos)
        
        # Draw chip value in corner if it's a scoring card
        if card.contributes_to_hand:
            chip_text = self.small_font.render(str(card.get_chip_value()), True, CYAN)
            chip_pos = (x + width//2 - 20, y + height//2 - 15)
            self.screen.blit(chip_text, chip_pos)

    def draw_ui(self):
        if self.game_state.game_phase == "blind_select":
            self.draw_blind_select_ui()
        elif self.game_state.game_phase == "playing" or self.game_state.game_phase == "scoring":
            self.draw_gameplay_ui()
        else:
            self.draw_shop_ui()

    def draw_blind_select_ui(self):
        # Title
        title = self.title_font.render("SELECT BLIND", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Round info
        round_text = self.font.render(f"Round {self.game_state.round_number}", True, WHITE)
        round_rect = round_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(round_text, round_rect)
        
        # Money display
        money_text = self.font.render(f"Money: ${self.game_state.money}", True, GOLD)
        money_rect = money_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(money_text, money_rect)
        
        # Current blind info
        blind = self.game_state.current_blind
        blind_name = blind.value[0]
        blind_desc = blind.value[1]
        blind_mult = blind.value[2]
        is_boss = blind.value[3]
        
        # Blind display box
        blind_box = pygame.Rect(SCREEN_WIDTH // 2 - 250, 250, 500, 200)
        box_color = DARK_RED if is_boss else DARK_GRAY
        pygame.draw.rect(self.screen, box_color, blind_box, border_radius=15)
        pygame.draw.rect(self.screen, GOLD if is_boss else WHITE, blind_box, 3, border_radius=15)
        
        # Blind name
        name_text = self.large_font.render(blind_name, True, GOLD if is_boss else WHITE)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(name_text, name_rect)
        
        # Blind description
        desc_lines = self.wrap_text(blind_desc, 400, self.font)
        for i, line in enumerate(desc_lines):
            line_surface = self.font.render(line, True, WHITE)
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, 330 + i * 25))
            self.screen.blit(line_surface, line_rect)
        
        # Target score
        target = int(300 * (1.5 ** (self.game_state.round_number - 1)) * blind_mult)
        target_text = self.font.render(f"Target Score: {target}", True, CYAN)
        target_rect = target_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(target_text, target_rect)
        
        # Next blind preview
        next_blind = self.game_state.next_blind
        next_text = self.small_font.render(f"Next: {next_blind.value[0]}", True, LIGHT_GRAY)
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, 430))
        self.screen.blit(next_text, next_rect)
        
        # Buttons
        self.draw_button(self.PLAY_BLIND_BUTTON, "PLAY", GREEN, LIGHT_GRAY)
        skip_enabled = not is_boss
        skip_color = ORANGE if skip_enabled else GRAY
        self.draw_button(self.SKIP_BLIND_BUTTON, f"SKIP (+${max(5, self.game_state.round_number * 2)})", 
                        skip_color, LIGHT_GRAY, skip_enabled)

    def draw_gameplay_ui(self):
        # Top bar with game info
        info_y = 20
        
        # Score display
        score_text = f"Score: {self.game_state.score} / {self.game_state.target_score}"
        score_surface = self.font.render(score_text, True, CYAN)
        self.screen.blit(score_surface, (20, info_y))
        
        # Round info
        round_text = f"Round {self.game_state.round_number}"
        round_surface = self.font.render(round_text, True, WHITE)
        self.screen.blit(round_surface, (SCREEN_WIDTH // 2 - 60, info_y))
        
        # Money display
        money_text = f"${self.game_state.money}"
        money_surface = self.font.render(money_text, True, GOLD)
        self.screen.blit(money_surface, (SCREEN_WIDTH - 120, info_y))
        
        # Hands and discards left
        hands_text = f"Hands: {self.game_state.hands_left}"
        discards_text = f"Discards: {self.game_state.discards_left}"
        hands_surface = self.font.render(hands_text, True, GREEN)
        discards_surface = self.font.render(discards_text, True, ORANGE)
        self.screen.blit(hands_surface, (20, info_y + 40))
        self.screen.blit(discards_surface, (20, info_y + 70))
        
        # Current blind info
        blind_text = f"Blind: {self.game_state.current_blind.value[0]}"
        blind_surface = self.font.render(blind_text, True, WHITE)
        self.screen.blit(blind_surface, (SCREEN_WIDTH - 300, info_y + 40))
        
        # Selected hand evaluation
        if self.game_state.selected_cards:
            hand_type, base_score, contributing = evaluate_hand(self.game_state.selected_cards)
            hand_name = hand_type.value[0]
            hand_mult = hand_type.value[1]
            hand_chips = hand_type.value[2]
            card_chips = sum(c.get_chip_value() for c in contributing)
            total_score = (card_chips + hand_chips) * hand_mult
            
            eval_text = f"{hand_name}: ({card_chips} + {hand_chips}) × {hand_mult} = {total_score}"
            eval_surface = self.font.render(eval_text, True, CYAN)
            eval_rect = eval_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
            self.screen.blit(eval_surface, eval_rect)
        
        # Scoring animation display
        if self.game_state.game_phase == "scoring":
            self.draw_scoring_animation()
        
        # Draw cards
        for card in self.game_state.hand:
            self.draw_card(card)
        
        for card in self.game_state.scoring_cards:
            self.draw_card(card)
        
        # Draw buttons (only during playing phase)
        if self.game_state.game_phase == "playing":
            play_enabled = len(self.game_state.selected_cards) > 0 and self.game_state.hands_left > 0
            discard_enabled = len(self.game_state.selected_cards) > 0 and self.game_state.discards_left > 0
            
            self.draw_button(self.PLAY_BUTTON, f"PLAY HAND", GREEN, LIGHT_GRAY, play_enabled)
            self.draw_button(self.DISCARD_BUTTON, f"DISCARD", RED, LIGHT_GRAY, discard_enabled)
            self.draw_button(self.SORT_RANK_BUTTON, "SORT BY RANK", BLUE, LIGHT_GRAY)
            self.draw_button(self.SORT_SUIT_BUTTON, "SORT BY SUIT", PURPLE, LIGHT_GRAY)

    def draw_scoring_animation(self):
        """Draw the scoring animation overlay"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Hand type display
        if self.game_state.last_hand_type:
            hand_name = self.game_state.last_hand_type.value[0]
            hand_text = self.large_font.render(hand_name, True, GOLD)
            hand_rect = hand_text.get_rect(center=(center_x, center_y - 200))
            self.screen.blit(hand_text, hand_rect)
        
        # Scoring breakdown
        y_offset = center_y + 150
        
        if self.game_state.scoring_stage >= 1:
            base_text = f"Base: {self.game_state.base_chips}"
            base_surface = self.font.render(base_text, True, WHITE)
            base_rect = base_surface.get_rect(center=(center_x - 100, y_offset))
            self.screen.blit(base_surface, base_rect)
        
        if self.game_state.scoring_stage >= 2:
            chips_text = f"Cards: {self.game_state.current_chips - self.game_state.base_chips}"
            chips_surface = self.font.render(chips_text, True, CYAN)
            chips_rect = chips_surface.get_rect(center=(center_x, y_offset))
            self.screen.blit(chips_surface, chips_rect)
        
        if self.game_state.scoring_stage >= 3:
            mult_text = f"× {self.game_state.current_multiplier}"
            mult_surface = self.font.render(mult_text, True, GREEN)
            mult_rect = mult_surface.get_rect(center=(center_x + 100, y_offset))
            self.screen.blit(mult_surface, mult_rect)
        
        # Total score
        total_text = f"Total: {self.game_state.current_chips * self.game_state.current_multiplier if self.game_state.scoring_stage >= 3 else self.game_state.current_chips}"
        total_surface = self.large_font.render(total_text, True, GOLD)
        total_rect = total_surface.get_rect(center=(center_x, y_offset + 50))
        self.screen.blit(total_surface, total_rect)

    def draw_shop_ui(self):
        # Title
        title = self.title_font.render("SHOP", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Money display
        money_text = self.large_font.render(f"Money: ${self.game_state.money}", True, GOLD)
        money_rect = money_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(money_text, money_rect)
        
        # Success message
        success_text = f"Blind completed! Earned ${self.game_state.money_earned_this_blind}"
        success_surface = self.font.render(success_text, True, GREEN)
        success_rect = success_surface.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(success_surface, success_rect)
        
        # Shop items (placeholder)
        items = [
            ("Extra Hand", "$8", "Gain +1 hand per round"),
            ("Extra Discard", "$5", "Gain +1 discard per round"),
            ("Bonus Card", "$12", "Add a bonus card to deck")
        ]
        
        shop_rects = [self.SHOP_ITEM_1, self.SHOP_ITEM_2, self.SHOP_ITEM_3]
        
        for i, (name, price, desc) in enumerate(items):
            rect = shop_rects[i]
            can_afford = self.game_state.money >= int(price[1:])
            color = DARK_GRAY if can_afford else DARKER_GRAY
            border_color = WHITE if can_afford else GRAY
            
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)
            
            # Item name
            name_surface = self.font.render(name, True, WHITE if can_afford else GRAY)
            name_rect = name_surface.get_rect(center=(rect.centerx, rect.y + 30))
            self.screen.blit(name_surface, name_rect)
            
            # Price
            price_surface = self.font.render(price, True, GOLD if can_afford else GRAY)
            price_rect = price_surface.get_rect(center=(rect.centerx, rect.y + 60))
            self.screen.blit(price_surface, price_rect)
            
            # Description
            desc_lines = self.wrap_text(desc, rect.width - 20, self.small_font)
            for j, line in enumerate(desc_lines):
                line_surface = self.small_font.render(line, True, LIGHT_GRAY if can_afford else GRAY)
                line_rect = line_surface.get_rect(center=(rect.centerx, rect.y + 85 + j * 15))
                self.screen.blit(line_surface, line_rect)
        
        # Continue button
        self.draw_button(self.CONTINUE_BUTTON, "CONTINUE", GREEN)

    def handle_click(self, pos):
        """Handle mouse clicks"""
        if self.game_state.game_phase == "blind_select":
            if self.PLAY_BLIND_BUTTON.collidepoint(pos):
                self.game_state.select_blind()
            elif self.SKIP_BLIND_BUTTON.collidepoint(pos) and not self.game_state.current_blind.value[3]:
                self.game_state.skip_blind()
                
        elif self.game_state.game_phase == "playing":
            # Check card clicks
            for card in reversed(self.game_state.hand):  # Check from top card first
                card_rect = pygame.Rect(card.x - CARD_WIDTH//2, card.y - CARD_HEIGHT//2, 
                                      CARD_WIDTH, CARD_HEIGHT)
                if card_rect.collidepoint(pos):
                    self.game_state.toggle_card_selection(card)
                    break
            
            # Check button clicks
            if self.PLAY_BUTTON.collidepoint(pos):
                self.game_state.play_selected_cards()
            elif self.DISCARD_BUTTON.collidepoint(pos):
                self.game_state.discard_selected_cards()
            elif self.SORT_RANK_BUTTON.collidepoint(pos):
                self.game_state.sort_hand_by_rank()
            elif self.SORT_SUIT_BUTTON.collidepoint(pos):
                self.game_state.sort_hand_by_suit()
                
        elif self.game_state.game_phase == "shop":
            if self.CONTINUE_BUTTON.collidepoint(pos):
                self.game_state.advance_blind()
            # Add shop item purchase logic here
            
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update game state
            self.game_state.update_game(dt)
            
            # Draw everything
            self.screen.fill(DARKER_GRAY)
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# ----------------------------
# Main entry point
# ----------------------------
if __name__ == "__main__":
    game = BalatroGame()
    game.run()
