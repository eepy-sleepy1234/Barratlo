import random
from collections import Counter
class JokerEffectsManager:
    def __init__(self):
        self.effects = {
            'on_card_scored': [],
            'on_hand_played': [],
            'on_discard': [],
            'on_round_start': [],
            'on_round_end': [],
            'final_mult': [],
            'final_chips': [],
            'retrigger': [],
            'copy': [],
            'on_joker_sell': [],
        }

    def register_joker(self, joker_name, event_type, effect_function):
        if event_type in self.effects:
            self.effects[event_type].append({
                'name': joker_name,
                'function': effect_function,
            })
    def trigger(self, event_type, context):
        if event_type not in self.effects:
            return context
        for effect in self.effects[event_type]:
            context = effect['function'](context)
        return context
    
def hand_contains(context):
    if context.get("hand_type"):
        cards = context.get('hand_played')
        n = len(cards)
        values = sorted([c.value for c in cards])
        suits = [c.suit for c in cards]
        value_counts = Counter(values)
        suits_counts = Counter(suits)
        is_flush = n == 5 and max(suits_counts.values()) == 5
        is_straight = n == 5 and all(values[i] - values[i-1] == 1 for i in range(1,5))
        hand_contains = []
        if is_flush:
            hand_contains.append('Flush')
        if is_straight:
            hand_contains.append('Straight')
        if is_straight and is_flush:
            hand_contains.append('Straight Flush')
        if 4 in value_counts.values():
            hand_contains.append('Four of a Kind')
        if 3 in value_counts.values():
            hand_contains.append('Three of a Kind')
        if 2 in value_counts.values():
            hand_contains.append('Pair')
        if sorted(value_counts.values()) == [2, 3]:
            hand_contains.append('Full House')
        if list(value_counts.values()).count(2) == 2:
            hand_contains.append('Two Pair')
        if is_flush and is_straight and values[-1] == 14:
            hand_contains.append('Royal Flush')
        if 5 in value_counts.values():
            hand_contains.append('Five of a Kind')
        if 5 in value_counts.values() and is_flush:
            hand_contains.append('Flush Five')
        if sorted(value_counts.values()) == [2, 3] and is_flush:
            hand_contains.append('Flush House')
        hand_contains.append('High Card')
        return hand_contains
    return []
    
def Bald_effect(context):
    card = context.get('card')
    if card and card.value < 10:
        context['mult'] += 4
        context.setdefault('triggered_jokers', []).append('Bald')
    return context

def Clever_effect(context):
    hand = hand_contains(context)
    if "Two Pair" in hand:
        context['chips'] += 80
        context.setdefault('triggered_jokers', []).append('Clever')
    return context

def Disguised_effect(context):
    return context

def Crafty_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Flush":
        context['chips'] += 80
        context.setdefault('triggered_jokers', []).append('Crafty')
    return context

def Crazy_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Straight":
        context['mult'] += 12
        context.setdefault('triggered_jokers', []).append('Crazy')
    return context

def Devious_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Straight":
        context['chips'] += 100
        context.setdefault('triggered_jokers', []).append('Crazy')
    return context

def Droll_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Flush":
        context["mult"] += 10
        context.setdefault('triggered_jokers', []).append('Droll')
    return context

def Jolly_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Pair":
        context["mult"] += 8
        context.setdefault('triggered_jokers', []).append('Jolly')
    return context

def Mad_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Four of a Kind":
        context["mult"] += 20
        context.setdefault('triggered_jokers', []).append('Mad')
    return context

def Sly_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Pair":
        context["chips"] += 50
        context.setdefault('triggered_jokers', []).append('Sly')
    return context

def Wily_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Straight":
        context["chips"] += 100
        context.setdefault('triggered_jokers', []).append('Wily')
    return context

def Zany_effect(context):
    hand = context.get('hand_type')
    if hand and hand == "Three of a Kind":
        context["mult"] += 12
        context.setdefault('triggered_jokers', []).append('Mad')
    return context

def Jevil_effect(context):
    deck = context.get('deck')
    if deck:
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        random_suit = random.choice(suits)
        for card in deck:
            card.suit = random_suit

        context.setdefault('triggered_jokers', []).append('Jevil')
    return context

def Hacked_effect(context):
    return context

def Michigan_effect(context):
    return context

def Invincible_effect(context):
    return context

def Lucky_effect(context):
    return context

def PoolTable_effect(context):
    return context

def RulesCard_effect(context):
    return context

def TheJonklerBaby_effect(context):
    return context

def UpsideDown_effect(context):
    return context

def GettingAnUpgrade_effect(context):
    return context

def FlyDeity_effect(context):
    return context

def Yin_effect(context):
    return context

def Yang_effect(context):
    return context

def PTSD_effect(context):
    return context

def WetFloor_effect(context):
    return context

def YinYang_effect(context):
    return context

def Fountain_effect(context):
    return context

def OopyGoopy_effect(context):
    return context

JOKER_REGISTRY = {
    'Bald Joker': {
        'events': [('on_card_scored', Bald_effect)],
        'description': '+4 mult to every card with a rank under 10'
    },
    'Clever Joker': {
        'events': [('on_hand_played', Clever_effect)],
        'description': '+80 Chips if the played hand contains a Two Pair'
    },
    'Crafty Joker': {
        'events': [('on_hand_played', Crafty_effect)],
        'description': '+80 Chips if the played hand contains a Flush'
    },
    'Crazy Joker': {
        'events': [('on_hand_played', Crazy_effect)],
        'description': '+12 Mult if the played hand contains a Straight'
    },
    'Devious Joker': {
        'events': [('on_hand_played', Devious_effect)],
        'description': '+100 Chips if the played hand contains a Straight'
    },
    'Disguised Joker': {
        'events': [('on_hand_played', Disguised_effect)],
        'description': 'X2 Mult, but you can\'t see the boss blind before the blind'
    },
    'Droll Joker': {
        'events': [('on_hand_played', Droll_effect)],
        'description': '+10 Mult if the played hand contains a Flush'
    },
    'Jolly Joker': {
        'events': [('on_hand_played', Jolly_effect)],
        'description': '+8 Mult if the played hand contains a Pair'
    },
    'Mad Joker': {
        'events': [('on_hand_played', Mad_effect)],
        'description': '+20 Mult if the played hand contains a Four of a Kind'
    },
    'Sly Joker': {
        'events': [('on_hand_played', Sly_effect)],
        'description': '+50 Chips if the played hand contains a Pair'
    },
    'Wily Joker': {
        'events': [('on_hand_played', Wily_effect)],
        'description': '+100 Chips if the played hand contains a Straight'
    },
    'Zany Joker': {
        'events': [('on_hand_played', Zany_effect)],
        'description': '+12 Mult if the played hand contains a Three of a Kind'
    },
    'Hacked Joker': {
        'events': [('on_card_scored', Hacked_effect)],
        'description': 'Retriggers your 5 most played cards'
    },
    'Invincible Joker': {
        'events': [('on_round_end', Invincible_effect)],
        'description': 'If blind is lost, complete blind as if it was won. Do not collect any money and destry Invincible Joker. Cannot be destroyed in any other way'
    },
    'Lucky Joker': {
        'events': [('on_round_start', Lucky_effect)],
        'description': 'Doubles chances'
    },
    'Michigan Joker': {
        'events': [('on_card_scored', Michigan_effect)],
        'description': 'If the hand includes a Heart or a Spade, retrigger all scored cards once. Do not retrigger if hand has both'
    },
    'Pool Table': {
        'events': [('on_round_end', PoolTable_effect)],
        'description': '+ S0.1 earned at the end of round for every hand left'
    },
    'Rules Card': {
        'events': [('on_hand_played', RulesCard_effect)],
        'description': 'Rewards you $4 for playing (hand)'
    },
    'The Jonkler Baby': {
        'events': [('on_round_start', TheJonklerBaby_effect)],
        'description': 'Click on the Jonkler Sphere at the start of the round to discard your first hand'
    },
    'Upside Down Joker': {
        'events': [('on_card_scored', UpsideDown_effect)],
        'description': 'counts 6\'s and 9\'s as the same card, retrigger both'
    },
    'Getting An Upgrade': {
        'events': [('on_round_start', GettingAnUpgrade_effect)],
        'description': 'Sell to guarantee a rare Joker in the next shop'
    },
    'Fly Deity': {
        'events': [('on_hand_played', FlyDeity_effect)],
        'description': 'give +5 chips on Small and Big Blind, give +50 mult on Boss Blinds'
    },
    'Yin': {
        'events': [('on_hand_played', Yin_effect)],
        'description': '+4 mult, becomes YinYang Joker when Yang Joker is also active'
    },
    'Yang': {
        'events': [('on_hand_played', Yang_effect)],
        'description': '+4 mult, becomes YinYang Joker when Yin Joker is also active'
    },
    'Ptsd Joker': {
        'events': [('on_hand_played', PTSD_effect)],
        'description': 'Adds X0.1 Mult for every consecutive hand that isn\'t your last played hand'
    },
    'Wet Floor Joker': {
        'events': [('on_hand_played', WetFloor_effect)],
        'description': '+1 Mult for every hand played without a numbered card'
    },
    'Yin Yang': {
        'events': [('on_hand_played', YinYang_effect)],
        'description': 'If Hand played with exactly two colors X5 Mult'
    },
    'Fountain': {
        'events': [('on_card_scored', Fountain_effect)],
        'description': 'Cards with special attachments repeat once. Removes 1 Hand'
    },
    'Jevil': {
        'events': [('on_round_start', Jevil_effect)],
        'description': 'Converts all cards in deck to a random suit every time round starts'
    },
    'Oopy Goopy': {
        'events': [('on_hand_played', OopyGoopy_effect)],
        'description': 'Duplicates the joker to the right of it and double its effect'
    },
}

def initialize_joker_effects(active_jokers):
    manager = JokerEffectsManager()
    for joker in active_jokers:
        joker_name = joker.name
        if joker_name in JOKER_REGISTRY:
            joker_data = JOKER_REGISTRY[joker_name]
            for event_type, effect_function in joker_data['events']:
                manager.register_joker(joker_name, event_type, effect_function)
    return manager
