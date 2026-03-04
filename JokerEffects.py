import random
from collections import Counter
wetFloorValue = 0
last_hand = 0
last_hand_counter = 0
YinYang_Active = False
poolMoney = 0
skipMult = 1
exponentJoker = 1
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
            'on_scoring_start': [],
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
        
        context['current_event'] = event_type
        
        for effect in self.effects[event_type]:
            old_chips = context.get('chips', 0)
            old_mult = context.get('mult', 0)
            context = effect['function'](context)
            new_chips = context.get('chips', 0)
            new_mult = context.get('mult', 0)
        return context
    
def hand_contains(context):
    cards = context.get('hand_played')
    if not cards:
        return []
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
    if list(value_counts.values()).count(2) == 2 or (list(value_counts.values()).count(3) == 1 and list(value_counts.values()).count(2) == 1):
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
    
def Bald_effect(context):
    hand_played = context.get('hand_played', [])
    for card in hand_played:
        if card.value < 10:
            context['mult'] += 4
            context.setdefault('triggered_jokers', []).append('Bald Joker')
    return context

def Useful_effect(context):
    context['mult'] += 1
    context.setdefault('triggered_jokers', []).append('Useful Joker')
    return context
def Clever_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    hand = hand_contains(context)
    if "Two Pair" in hand:
        old_chips = context.get('chips', 0)
        context['chips'] = context.get('chips', 0) + 80 
        context.setdefault('triggered_jokers', []).append('Clever Joker')
    return context

def Disguised_effect(context):
    return context

def Crafty_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Flush" in hand:
        context['chips'] = context.get('chips', 0) + 80
        context.setdefault('triggered_jokers', []).append('Crafty Joker')
    return context

def Crazy_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Straight" in hand:
        context['mult'] = context.get('mult', 0) + 12
        context.setdefault('triggered_jokers', []).append('Crazy Joker')
    return context

def Devious_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Straight" in hand:
        context['chips'] = context.get('chips', 0) + 100
        context.setdefault('triggered_jokers', []).append('Devious Joker')
    return context

def Droll_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Flush" in hand:
        context["mult"] = context.get('mult', 0) + 10
        context.setdefault('triggered_jokers', []).append('Droll Joker')
    return context

def Jolly_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Pair" in hand:
        context["mult"] = context.get('mult', 0) + 8
        context.setdefault('triggered_jokers', []).append('Jolly Joker')
    return context

def Mad_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Four of a Kind" in hand:
        context["mult"] = context.get('mult', 0) + 20
        context.setdefault('triggered_jokers', []).append('Mad Joker')
    return context

def Sly_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Pair" in hand:
        context["chips"] = context.get('chips', 0) + 50
        context.setdefault('triggered_jokers', []).append('Sly Joker')
    return context

def Wily_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Straight" in hand:
        context["chips"] = context.get('chips', 0) + 100
        context.setdefault('triggered_jokers', []).append('Wily Joker')
    return context

def Zany_effect(context):
    if 'hand_played' not in context or not context.get('hand_played'):
        return context
    
    hand = hand_contains(context)
    if "Three of a Kind" in hand:
        context["mult"] = context.get('mult', 0) + 12
        context.setdefault('triggered_jokers', []).append('Zany Joker')
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
    card = context.get('card')
    if not card:
        return context
    card_play_counts = context.get('card_play_counts', {})
    top_5 = sorted(card_play_counts, key=card_play_counts.get, reverse=True)[:5]
    
    if card.card_id in top_5:
        context['chips'] = context.get('chips', 0) + card.chip_value
        context.setdefault('triggered_jokers', []).append('Hacked Joker')
    
    return context
def Exponent_effect(context):
    global exponentJoker
    hand = hand_contains(context)
    cards = context.get('hand_played', [])
    
    if "Full House" in hand:
        card_values = [c.value for c in cards]
        if (2 in card_values and 4 in card_values) or (3 in card_values and 9 in card_values):
            exponentJoker += 0.1
    context["mult"] = pow(context.get('mult', 0), exponentJoker)
            
    
    return context
def Invincible_effect(context):
    return context

def Lucky_effect(context):
    return context

def Michigan_effect(context):
    hand_played = context.get('hand_played', [])
    contributing = context.get('contributing', [])
    suits = {c.suit for c in hand_played}
    has_heart  = 'Hearts' in suits
    has_spade  = 'Spades' in suits

    if (has_heart or has_spade) and not (has_heart and has_spade):
        for card in contributing:
            card.retriggers += 1
        context.setdefault('triggered_jokers', []).append('Michigan Joker')

    return context

def PoolTable_effect(context):
    money = context.get('money')
    money += poolMoney
    money = round(money,1)
    context.setdefault('triggered_jokers', []).append('Pool Table')
    context['money'] = context.get('money',0) + money
    

    return context

def RulesCard_effect(context):
    hand_played = context.get("hand_played")
    rules_hand = context.get("rulesHand") 
    hand_type, _ = hand_played and (context.get("hand_type"), None) or (None, None)
    if context.get("hand_type") == rules_hand:
        context["money"] = context.get('money', 0) + 5
    context.setdefault('triggered_jokers', []).append('RulesCard')
    return context

def TheJonklerBaby_effect(context):
    context['jonkler_sphere_active'] = True
    context.setdefault('triggered_jokers', []).append('The Jonkler Baby')
    return context

def UpsideDown_effect(context):
    contributing = context.get('contributing', [])
    
    has_six_or_nine = any(c.value in (6, 9) for c in contributing)
    
    if has_six_or_nine:
        for card in contributing:
            if card.value == 6 or card.value == 9:
                card.retriggers += 1
        context.setdefault('triggered_jokers', []).append('UpsideDown Joker')
   
    return context

def GettingAnUpgrade_effect(context):
    return context

def FlyDeity_effect(context):
    blind = context.get("blind")
    boss = context.get("bosses")
    if blind in boss:
        context['mult'] = context.get("mult") + 50
    else:
        context['mult'] = context.get("mult") + 5


    context.setdefault('triggered_jokers', []).append('Fly Deity')

    return context

def Yin_effect(context):
    context["mult"] = context.get('mult', 0) + 4
    context.setdefault('triggered_jokers', []).append('Yin Joker')
    return context

def Yang_effect(context):
    context["mult"] = context.get('mult', 0) + 4
    context.setdefault('triggered_jokers', []).append('Yin Joker')
    return context

def PTSD_effect(context):
    global last_hand
    global last_hand_counter
    hand = context.get("hand_type", 0)
    if hand == last_hand:
        last_hand_counter = 0
        
    else:
        
        last_hand_counter += 0.1
        context["mult"] = context.get('mult', 0) * (1 + last_hand_counter)
    context.setdefault('triggered_jokers', []).append('PTSD Joker')
    return context





def WetFloor_effect(context):
    global wetFloorValue
    hand_played = [c for c in context.get('hand_played', []) if not isinstance(c, str)]
    has_numbered = any(2 <= card.value <= 9 for card in hand_played)
    if has_numbered:
        wetFloorValue = 0
    else:
        wetFloorValue += 1
    context.setdefault('triggered_jokers', []).append('Wet Floor Joker')
    context['mult'] = context.get('mult', 0) + wetFloorValue
    return context

def YinYang_effect(context):
    cardsuits = []
    hand_played = [c for c in context.get('hand_played', []) if not isinstance(c, str)]
    for card in hand_played:
        if card.suit not in cardsuits:
            cardsuits.append(card.suit)
    if len(cardsuits) == 2:
        context['mult'] = context.get('mult', 0) * 5
    else:
        context['mult'] = context.get('mult', 0) * 1.5
    return context

def Fountain_effect(context):
    hand_played = context.get('hand_played', [])
    contributing = context.get('contributing', [])
    has_enhancement = any(card.enhancement is not None for card in hand_played)
    if has_enhancement:
        for card in contributing:
            if card.enhancement is not None:
                card.retriggers += 1
        context['fountain_remove_hand'] = True
        context.setdefault('triggered_jokers', []).append('Fountain')
    return context
def Skip_effect(context):
    context['mult'] = round((context.get('mult',0) * skipMult),2)
    return context

def OopyGoopy_effect(context):
    jokers = context.get('active_jokers')
    if not jokers:
        return context
    
    oopy_goopy_index = -1
    for i, joker in enumerate(jokers):
        if joker.name == 'Oopy Goopy':
            oopy_goopy_index = i
            break
    
    if oopy_goopy_index == -1:
        return context
    
    if oopy_goopy_index + 1 < len(jokers):
        next_joker = jokers[oopy_goopy_index + 1]
        next_joker_name = next_joker.name
        
        if next_joker_name in JOKER_REGISTRY:
            joker_data = JOKER_REGISTRY[next_joker_name]
            
            if joker_data.get('Oopy Goopy', False):
                current_event = context.get('current_event')
                
                for event_type, effect_func in joker_data['events']:
                    if event_type == current_event:
                        context = effect_func(context)
                        context = effect_func(context)
                        context.setdefault('triggered_jokers', []).append('Oopy Goopy')
                        break
    
    return context

JOKER_REGISTRY = {
    'Bald Joker': {
        'events': [('on_hand_played', Bald_effect)],
        'description': '+4 mult to every card with a rank under 10',
        'Oopy Goopy': True
    },
    'Clever Joker': {
        'events': [('on_hand_played', Clever_effect)],
        'description': '+80 Chips if the played hand contains a Two Pair',
        'Oopy Goopy': True
    },
    'Crafty Joker': {
        'events': [('on_hand_played', Crafty_effect)],
        'description': '+80 Chips if the played hand contains a Flush',
        'Oopy Goopy': True
    },
    'Crazy Joker': {
        'events': [('on_hand_played', Crazy_effect)],
        'description': '+12 Mult if the played hand contains a Straight',
        'Oopy Goopy': True
    },
    'Devious Joker': {
        'events': [('on_hand_played', Devious_effect)],
        'description': '+100 Chips if the played hand contains a Straight',
        'Oopy Goopy': True
    },
    'Disguised Joker': {
        'events': [('on_hand_played', Disguised_effect)],
        'description': 'X2 Mult, but you can\'t see the boss blind before the blind',
        'Oopy Goopy': True
    },
    'Droll Joker': {
        'events': [('on_hand_played', Droll_effect)],
        'description': '+10 Mult if the played hand contains a Flush',
        'Oopy Goopy': True
    },
    'Jolly Joker': {
        'events': [('on_hand_played', Jolly_effect)],
        'description': '+8 Mult if the played hand contains a Pair',
        'Oopy Goopy': True
    },
    'Mad Joker': {
        'events': [('on_hand_played', Mad_effect)],
        'description': '+20 Mult if the played hand contains a Four of a Kind',
        'Oopy Goopy': True
    },
    'Sly Joker': {
        'events': [('on_hand_played', Sly_effect)],
        'description': '+50 Chips if the played hand contains a Pair',
        'Oopy Goopy': True
    },
    'Wily Joker': {
        'events': [('on_hand_played', Wily_effect)],
        'description': '+100 Chips if the played hand contains a Straight',
        'Oopy Goopy': True
    },
    'Zany Joker': {
        'events': [('on_hand_played', Zany_effect)],
        'description': '+12 Mult if the played hand contains a Three of a Kind',
        'Oopy Goopy': True
    },
    'Hacked Joker': {
        'events': [('on_card_scored', Hacked_effect)],
        'description': 'Retriggers your 5 most played cards',
        'Oopy Goopy': True
    },
    'Invincible Joker': {
        'events': [('on_hand_played', Invincible_effect)],
        'description': 'If blind is lost, complete blind as if it was won. Do not collect any money and destry Invincible Joker. Cannot be destroyed in any other way',
        'Oopy Goopy': False
    },
    'Lucky Joker': {
        'events': [('on_round_start', Lucky_effect)],
        'description': 'Doubles chances',
        'Oopy Goopy': True
    },
    'Michigan Joker': {
        'events': [('on_scoring_start', Michigan_effect)],
        'description': 'If the hand includes a Heart or a Spade, retrigger all scored cards once. Do not retrigger if hand has both',
        'Oopy Goopy': True
    },
    'Pool Table': {
        'events': [('on_round_end', PoolTable_effect)],
        'description': '+ S0.1 earned at the end of round for every hand left',
        'Oopy Goopy': False
    },
    'Rules Card': {
        'events': [('on_hand_played', RulesCard_effect)],
        'description': 'Rewards you $4 for playing (hand)',
        'Oopy Goopy': True
    },
    'The Jonkler Baby': {
        'events': [('on_round_start', TheJonklerBaby_effect)],
        'description': 'Click on the Jonkler Sphere at the start of the round to discard your first hand',
        'Oopy Goopy': False
    },
    'Upside Down Joker': {
        'events': [('on_scoring_start', UpsideDown_effect)],
        'description': 'counts 6\'s and 9\'s as the same card, retrigger both', #Temporarly only retriggers them
        'Oopy Goopy': True
    },
    'Getting An Upgrade': {
        'events': [('on_round_start', GettingAnUpgrade_effect)],
        'description': 'Sell to guarantee a rare Joker in the next shop',
        'Oopy Goopy': False
    },
    'Fly Deity': {
        'events': [('on_hand_played', FlyDeity_effect)],
        'description': 'give +5 chips on Small and Big Blind, give +50 mult on Boss Blinds',
        'Oopy Goopy': True
    },
    'Yin Joker': {
        'events': [('on_hand_played', Yin_effect)],
        'description': '+4 mult, becomes YinYang Joker when Yang Joker is also active',
        'Oopy Goopy': True
    },
    'Yang Joker': {
        'events': [('on_hand_played', Yang_effect)],
        'description': '+4 mult, becomes YinYang Joker when Yin Joker is also active',
        'Oopy Goopy': True
    },
    'Ptsd Joker': {
        'events': [('on_hand_played', PTSD_effect)],
        'description': 'Adds X0.1 Mult for every consecutive hand that isn\'t your last played hand',
        'Oopy Goopy': True
    },
    'Wet Floor Joker': {
        'events': [('on_hand_played', WetFloor_effect)],
        'description': '+1 Mult for every hand played without a numbered card',
        'Oopy Goopy': True
    },
    'Yin Yang': {
        'events': [('on_hand_played', YinYang_effect)],
        'description': 'If Hand played with exactly two colors X5 Mult, otherwise gives X1.5 Mult',
        'Oopy Goopy': True
    },
    'Fountain': {
        'events': [('on_scoring_start', Fountain_effect)],
        'description': 'Cards with enhancements repeat once. Removes 1 Hand',
        'Oopy Goopy': True
    },
    'Jevil': {
        'events': [('on_round_start', Jevil_effect)],
        'description': 'Converts all cards in deck to a random suit every time round starts',
        'Oopy Goopy': False
    },
    'Oopy Goopy': {
        'events': [('on_hand_played', OopyGoopy_effect)],
        'description': 'Duplicates the joker to the right of it and double its effect',
        'Oopy Goopy': True 
    },
    'Skip Joker': {
        'events': [('on_hand_played', Skip_effect)],
        'description': 'Gains X0.25 Mult For Every Skipped Blind',
        'Oopy Goopy': True 
    },
    'Exponent Joker': {
        'events': [('on_hand_played', Exponent_effect)],
        'description': 'Gains ^0.1 each time a Full House is played that contains a four and a two',
        'Oopy Goopy': True 
    },
    'Useful Joker': {
        'events': [('on_hand_played', Useful_effect)],
        'description': '+1 Mult when hand contains a card',
        'Oopy Goopy': True 
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