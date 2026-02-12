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
            print(f"✓ Registered {joker_name} for {event_type}")  
    
    def trigger(self, event_type, context):
        if event_type not in self.effects:
            print(f"⚠ No effects registered for {event_type}")
            return context
        
        print(f"\n=== TRIGGERING {event_type} ===")
        print(f"Number of effects: {len(self.effects[event_type])}")
        print(f"Context keys: {context.keys()}")
        print(f"Hand type: {context.get('hand_type')}")
        print(f"Chips before: {context.get('chips')}")
        print(f"Mult before: {context.get('mult')}")
        
        context['current_event'] = event_type
        
        for effect in self.effects[event_type]:
            print(f"\n  → Running {effect['name']}...")
            old_chips = context.get('chips', 0)
            old_mult = context.get('mult', 0)
            context = effect['function'](context)
            new_chips = context.get('chips', 0)
            new_mult = context.get('mult', 0)
            
            if new_chips != old_chips:
                print(f"    Chips changed: {old_chips} → {new_chips} (+{new_chips - old_chips})")
            if new_mult != old_mult:
                print(f"    Mult changed: {old_mult} → {new_mult} (+{new_mult - old_mult})")
        
        print(f"\nChips after: {context.get('chips')}")
        print(f"Mult after: {context.get('mult')}")
        print(f"=== END {event_type} ===\n")
        return context
    
def hand_contains(context):
    print(f"\n  [hand_contains] Checking context...")
    if context.get("hand_type"):
        cards = context.get('hand_played')
        print(f"  [hand_contains] hand_played: {cards}")
        if not cards:
            print(f"  [hand_contains] No cards in hand_played!")
            return []
        
        print(f"  [hand_contains] Number of cards: {len(cards)}")
        n = len(cards)
        values = sorted([c.value for c in cards])
        suits = [c.suit for c in cards]
        print(f"  [hand_contains] Values: {values}")
        print(f"  [hand_contains] Suits: {suits}")
        
        value_counts = Counter(values)
        print(f"  [hand_contains] Value counts: {dict(value_counts)}")
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
            print(f"  [hand_contains] ✓ TWO PAIR DETECTED!")
        if is_flush and is_straight and values[-1] == 14:
            hand_contains.append('Royal Flush')
        if 5 in value_counts.values():
            hand_contains.append('Five of a Kind')
        if 5 in value_counts.values() and is_flush:
            hand_contains.append('Flush Five')
        if sorted(value_counts.values()) == [2, 3] and is_flush:
            hand_contains.append('Flush House')
        hand_contains.append('High Card')
        
        print(f"  [hand_contains] Result: {hand_contains}")
        return hand_contains
    else:
        print(f"  [hand_contains] No hand_type in context!")
    return []
    
def Bald_effect(context):
    card = context.get('card')
    if card and card.value < 10:
        context['mult'] += 4
        context.setdefault('triggered_jokers', []).append('Bald Joker')
    return context

def Clever_effect(context):
    print(f"\n  [Clever_effect] Starting...")
    print(f"  [Clever_effect] Context hand_type: {context.get('hand_type')}")
    hand = hand_contains(context)
    print(f"  [Clever_effect] hand_contains returned: {hand}")
    
    if "Two Pair" in hand:
        print(f"  [Clever_effect] ✓✓✓ TWO PAIR FOUND! Adding 80 chips!")
        old_chips = context.get('chips', 0)
        context['chips'] += 80
        print(f"  [Clever_effect] Chips: {old_chips} → {context['chips']}")
        context.setdefault('triggered_jokers', []).append('Clever Joker')
    else:
        print(f"  [Clever_effect] Two Pair NOT in hand_contains result")
    return context

def Disguised_effect(context):
    return context

def Crafty_effect(context):
    hand = hand_contains(context)
    if "Flush" in hand:
        context['chips'] += 80
        context.setdefault('triggered_jokers', []).append('Crafty Joker')
    return context

def Crazy_effect(context):
    hand = hand_contains(context)
    if "Straight" in hand:
        context['mult'] += 12
        context.setdefault('triggered_jokers', []).append('Crazy Joker')
    return context

def Devious_effect(context):
    hand = hand_contains(context)
    if "Straight" in hand:
        context['chips'] += 100
        context.setdefault('triggered_jokers', []).append('Devious')
    return context

def Droll_effect(context):
    hand = hand_contains(context)
    if "Flush" in hand:
        context['mult'] += 10
        context.setdefault('triggered_jokers', []).append('Droll')
    return context

def Jolly_effect(context):
    hand = hand_contains(context)
    if "Pair" in hand:
        context['mult'] += 8
        context.setdefault('triggered_jokers', []).append('Jolly')
    return context

def Mad_effect(context):
    hand = hand_contains(context)
    if "Four of a Kind" in hand:
        context['mult'] += 20
        context.setdefault('triggered_jokers', []).append('Mad')
    return context

def Sly_effect(context):
    hand = hand_contains(context)
    if "Pair" in hand:
        context['chips'] += 50
        context.setdefault('triggered_jokers', []).append('Sly')
    return context

def Wily_effect(context):
    hand = hand_contains(context)
    if "Straight" in hand:
        context['chips'] += 100
        context.setdefault('triggered_jokers', []).append('Wily')
    return context

def Zany_effect(context):
    hand = hand_contains(context)
    if "Three of a Kind" in hand:
        context['mult'] += 12
        context.setdefault('triggered_jokers', []).append('Zany')
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
        'events': [('on_card_scored', Bald_effect)],
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
        'events': [('on_round_end', Invincible_effect)],
        'description': 'If blind is lost, complete blind as if it was won. Do not collect any money and destry Invincible Joker. Cannot be destroyed in any other way',
        'Oopy Goopy': True
    },
    'Lucky Joker': {
        'events': [('on_round_start', Lucky_effect)],
        'description': 'Doubles chances',
        'Oopy Goopy': True
    },
    'Michigan Joker': {
        'events': [('on_card_scored', Michigan_effect)],
        'description': 'If the hand includes a Heart or a Spade, retrigger all scored cards once. Do not retrigger if hand has both',
        'Oopy Goopy': True
    },
    'Pool Table': {
        'events': [('on_round_end', PoolTable_effect)],
        'description': '+ S0.1 earned at the end of round for every hand left',
        'Oopy Goopy': True
    },
    'Rules Card': {
        'events': [('on_hand_played', RulesCard_effect)],
        'description': 'Rewards you $4 for playing (hand)',
        'Oopy Goopy': True
    },
    'The Jonkler Baby': {
        'events': [('on_round_start', TheJonklerBaby_effect)],
        'description': 'Click on the Jonkler Sphere at the start of the round to discard your first hand',
        'Oopy Goopy': True
    },
    'Upside Down Joker': {
        'events': [('on_card_scored', UpsideDown_effect)],
        'description': 'counts 6\'s and 9\'s as the same card, retrigger both',
        'Oopy Goopy': True
    },
    'Getting An Upgrade': {
        'events': [('on_round_start', GettingAnUpgrade_effect)],
        'description': 'Sell to guarantee a rare Joker in the next shop',
        'Oopy Goopy': True
    },
    'Fly Deity': {
        'events': [('on_hand_played', FlyDeity_effect)],
        'description': 'give +5 chips on Small and Big Blind, give +50 mult on Boss Blinds',
        'Oopy Goopy': True
    },
    'Yin': {
        'events': [('on_hand_played', Yin_effect)],
        'description': '+4 mult, becomes YinYang Joker when Yang Joker is also active',
        'Oopy Goopy': True
    },
    'Yang': {
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
        'description': 'If Hand played with exactly two colors X5 Mult',
        'Oopy Goopy': True
    },
    'Fountain': {
        'events': [('on_card_scored', Fountain_effect)],
        'description': 'Cards with special attachments repeat once. Removes 1 Hand',
        'Oopy Goopy': True
    },
    'Jevil': {
        'events': [('on_round_start', Jevil_effect)],
        'description': 'Converts all cards in deck to a random suit every time round starts',
        'Oopy Goopy': True
    },
    'Oopy Goopy': {
        'events': [('on_hand_played', OopyGoopy_effect)],
        'description': 'Duplicates the joker to the right of it and double its effect',
        'Oopy Goopy': False  
    },
}

def initialize_joker_effects(active_jokers):
    print(f"\n=== INITIALIZING JOKER EFFECTS ===")
    print(f"Number of active jokers: {len(active_jokers)}")
    for joker in active_jokers:
        print(f"  - {joker.name}")
    
    manager = JokerEffectsManager()
    for joker in active_jokers:
        joker_name = joker.name
        if joker_name in JOKER_REGISTRY:
            joker_data = JOKER_REGISTRY[joker_name]
            for event_type, effect_function in joker_data['events']:
                manager.register_joker(joker_name, event_type, effect_function)
        else:
            print(f"⚠ WARNING: {joker_name} not found in JOKER_REGISTRY!")
    
    print(f"=== INITIALIZATION COMPLETE ===\n")
    return manager