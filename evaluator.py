from cards import Card, suits
import random
from collections import Counter

class EqualsError(Exception):
    pass

values = {
    'high card': 0,
    'pair': 1,
    'two pair': 2,
    'three of a kind': 3,
    'straight': 4,
    'flush': 5,
    'full house': 6,
    'four of a kind': 7,
    'straight flush': 8,
    'royal flush': 9
}

def evaluation(cards: list[Card]):
    assert len(cards) == 5

    # check for duplicate cards
    for i in range(len(cards)):
        for j in range(i+1, len(cards)):
            assert not (cards[i].value == cards[j].value and cards[i].suit == cards[j].suit)
    cards = sorted(cards)

    values_counts = Counter(card.value for card in cards)
    counts_values = {count: value for value, count in values_counts.items()}
    suits_counts = Counter(card.suit for card in cards)

    is_flush = max(suits_counts.values()) == 5
    is_straight = (all(cards[i].value == cards[i-1].value + 1 for i in range(1, 5)) or
                   all(cards[i].value == cards[i-1].value + 1 for i in range(1, 4)) and cards[-1].value == 14 and cards[0].value==2)
    is_royal = is_flush and is_straight and cards[0].value == 10
    is_four_oak = max(values_counts.values()) == 4
    is_full_house = max(values_counts.values()) == 3 and min(values_counts.values()) == 2
    is_three_oak = max(values_counts.values()) == 3
    is_two_pair = sum([1 for count in values_counts.values() if count == 2]) == 2
    is_pair = max(values_counts.values()) == 2

    if is_royal:
        # print("royal flush"*100)
        return [values['royal flush']] # None
    if is_straight and is_flush:
        return [values['straight flush']] + [cards[-1].value] # value of highest card
    if is_four_oak:
        return [values['four of a kind']] + [counts_values[4], counts_values[1]] # value of 4s, value of 1
    if is_full_house:
        return [values['full house']] + [counts_values[3], counts_values[2]] # value of 3s, value of 2s
    if is_flush:
        return [values['flush']] + [card.value for card in cards[::-1]] # value of top, second top, etc. down to last card
    if is_straight:
        low_ace = cards[-1].value == 14 and cards[0].value == 2
        return [values['straight']] + ([cards[-1].value] if not low_ace else [5]) # value of top card or 5 if low ace
    if is_three_oak:
        ones = sorted([[count, value] for value, count in values_counts.items() if count == 1], key=lambda x: x[1])
        return [values['three of a kind']] + [counts_values[3], ones[1][1], ones[0][1]] # value of 3s, value of higher non3, last non3
    if is_two_pair:
        pairs = sorted([[count, value] for value, count in values_counts.items() if count == 2], key=lambda x: x[1])
        return [values['two pair']] + [pairs[1][1], pairs[0][1], counts_values[1]]  # value of pair 1, value of pair 2, value of last card
    if is_pair:
        ones = sorted([[count, value] for value, count in values_counts.items() if count == 1], key=lambda x: x[1])
        return [values['pair'], counts_values[2], ones[2][1], ones[1][1], ones[0][1]] # value of pair, each value of other 3
    return [values['high card']] + [card.value for card in reversed(cards)] # value of all 5 going down

def equals(hand1: list[Card], hand2: list[Card]):
    scores1 = evaluation(hand1)
    scores2 = evaluation(hand2)

    rank1 = scores1.pop(0)
    rank2 = scores2.pop(0)

    return scores1 == scores2 if rank1 == rank2 else False


def beats(hand_1: list[Card], hand_2: list[Card]) -> bool:
    """ Does hand_1 beat hand_2?

    Raise an error if hands are equal.
    """
    scores1 = evaluation(hand_1)
    scores2 = evaluation(hand_2)

    rank1 = scores1.pop(0)
    rank2 = scores2.pop(0)

    if rank1 != rank2:
        return rank1 > rank2
    else:
        for index in range(len(scores1)):
            if scores1[index] != scores2[index]:
                return scores1 > scores2
    raise EqualsError("The hands have equal value, this function shouldn't be used")


def winners(hands: list):
    # Evaluate all hands and find the maximum main score
    scores = [evaluation(hand) for hand in hands]
    highest_score = max(score[0] for score in scores)

    # Filter hands with the highest main score
    candidates = [hand for hand, score in zip(hands, scores) if score[0] == highest_score]

    # Determine the strongest hands among the candidates
    strongest_hands = []
    for hand in candidates:
        if all(equals(hand, other) or beats(hand, other) for other in candidates if hand != other):
            strongest_hands.append(hand)

    # Find the indices of the strongest hands in the original list
    return {i for i, hand in enumerate(hands) if hand in strongest_hands}


def test_flush():
    cards = []
    for value in [7,2,5,6,9]:
        cards.append(Card('hearts', value))
    assert evaluation(cards) == [5, 9, 7, 6, 5, 2]

def test_straight():
    cards = []
    for value in [6,5,2,4,3]:
        suit = random.choice(suits)
        cards.append(Card(suit, value))
    assert evaluation(cards) == [4, 6]

    cards = []
    for value in [2,3,4,5,14]:
        suit = random.choice(suits)
        cards.append(Card(suit, value))
    assert evaluation(cards) == [4, 5]

def test_four_of_a_kind():
    cards = []
    for suit in suits:
        cards.append(Card(suit, 7))
    cards.append(Card('hearts', 2))
    assert evaluation(cards) == [7, 7, 2]

def test_full_house():
    cards = []
    for suit in suits[:3]:
        cards.append(Card(suit, 7))
    for suit in suits[:1:-1]:
        cards.append(Card(suit, 2))
    assert evaluation(cards) == [6, 7, 2]

def test_three_of_a_kind():
    cards = []
    for suit in suits[:3]:
        cards.append(Card(suit, 7))
    cards.append(Card('hearts', 2))
    cards.append(Card('clubs', 3))
    assert evaluation(cards) == [3, 7, 3, 2]

def test_two_pair():
    cards = []
    for suit in suits[:2]:
        cards.append(Card(suit, 7))
    for suit in suits[2:]:
        cards.append(Card(suit, 2))
    cards.append(Card('clubs', 13))
    assert evaluation(cards) == [2, 7, 2, 13]

def test_pair():
    cards = []
    for suit in suits[:2]:
        cards.append(Card(suit, 7))
    cards.append(Card('clubs', 13))
    cards.append(Card('hearts', 12))
    cards.append(Card('spades', 11))
    assert evaluation(cards) == [1, 7, 13, 12, 11]

def test_high_card():
    cards = [
        Card('clubs', 7),
        Card('hearts', 2),
        Card('clubs', 13),
        Card('hearts', 12),
        Card('spades', 11)
    ]
    assert evaluation(cards) == [0, 13, 12, 11, 7, 2]

def test_royal_flush():
    cards = []
    for value in range(13, 9, -1):
        cards.append(Card('hearts', value))
    cards.append(Card('hearts', 14))
    assert evaluation(cards) == [9]

def test_compare_higher_flush():
    hand1 = [
        Card('hearts', 5),
        Card('hearts', 4),
        Card('hearts', 3),
        Card('hearts', 12),
        Card('hearts', 7)
    ]

    hand2 = [
        Card('diamonds', 5),
        Card('diamonds', 4),
        Card('diamonds', 3),
        Card('diamonds', 13),
        Card('diamonds', 7)
    ]
    assert beats(hand1, hand2) == False

def test_compare_higher_card():
    hand1 = [
        Card('hearts', 5),
        Card('hearts', 4),
        Card('hearts', 3),
        Card('diamonds', 14),
        Card('hearts', 7)
    ]

    hand2 = [
        Card('diamonds', 5),
        Card('diamonds', 4),
        Card('spades', 3),
        Card('diamonds', 13),
        Card('diamonds', 7)
    ]
    assert beats(hand1, hand2) == True

def test_compare_royal_flush_split_pot():
    hand1 = [
        Card('hearts', 14),
        Card('hearts', 13),
        Card('hearts', 12),
        Card('hearts', 11),
        Card('hearts', 10)
    ]

    hand2 = [
        Card('diamonds', 14),
        Card('diamonds', 13),
        Card('diamonds', 12),
        Card('diamonds', 11),
        Card('diamonds', 10)
    ]
    try:
        beats(hand1, hand2)
        assert False, "This should raise an EqualsError"
    except EqualsError:
        pass
    assert equals(hand1, hand2) == True

def test_compare_two_straights_low_ace():
    hand1 = [
        Card('hearts', 14),
        Card('diamonds', 2),
        Card(random.choice(suits), 3),
        Card(random.choice(suits), 4),
        Card(random.choice(suits), 5)
    ]

    hand2 = [
        Card('clubs', 2),
        Card('spades', 3),
        Card('diamonds', 4),
        Card('diamonds', 5),
        Card('diamonds', 6)
    ]
    assert beats(hand1, hand2) == False

def test_compare_two_straights_high_ace():
    hand1 = [
        Card('hearts', 14),
        Card('diamonds', 12),
        Card(random.choice(suits), 13),
        Card(random.choice(suits), 10),
        Card(random.choice(suits), 11)
    ]

    hand2 = [
        Card('clubs', 14),
        Card('spades', 2),
        Card('diamonds', 4),
        Card('diamonds', 5),
        Card('diamonds', 3)
    ]
    assert beats(hand1, hand2) == True

def test_compare_split_pot_high_card():
    hand1 = [
        Card('hearts', 4),
        Card('diamonds', 5),
        Card(random.choice(suits), 7),
        Card(random.choice(suits), 10),
        Card(random.choice(suits), 11)
    ]

    hand2 = [
        Card('clubs', 4),
        Card('spades', 5),
        Card('diamonds', 7),
        Card('diamonds', 10),
        Card('diamonds', 11)
    ]
    try:
        beats(hand1, hand2)
        assert False, "This should raise an EqualsError"
    except EqualsError:
        pass
    assert equals(hand1, hand2) == True

def test_duplicate_cards():
    cards = [
        Card('hearts', 7),
        Card('diamonds', 5),
        Card('clubs', 2),
        Card('spades', 9),
        Card('hearts', 7)
    ]
    try:
        evaluation(cards)
        assert False, "Should raise an exception for duplicate cards"
    except AssertionError:  # Assuming your code raises ValueError for duplicates
        pass

def test_winners_3_winners():
    hand1 = [
        Card('hearts', 4),
        Card('hearts', 5),
        Card('hearts', 7),
        Card('hearts', 10),
        Card('hearts', 11)
    ]

    hand2 = [
        Card('diamonds', 4),
        Card('diamonds', 5),
        Card('diamonds', 7),
        Card('diamonds', 10),
        Card('diamonds', 11)
    ]

    hand3 = [
        Card('clubs', 4),
        Card('clubs', 5),
        Card('clubs', 7),
        Card('clubs', 10),
        Card('clubs', 11)
    ]

    hands = [hand1, hand2, hand3]
    assert winners(hands) == {0,1,2}

def test_winners_2_winners():
    hand1 = [
        Card('hearts', 3),
        Card('hearts', 5),
        Card('hearts', 7),
        Card('hearts', 10),
        Card('hearts', 11)
    ]

    hand2 = [
        Card('diamonds', 4),
        Card('diamonds', 5),
        Card('diamonds', 7),
        Card('diamonds', 10),
        Card('diamonds', 11)
    ]

    hand3 = [
        Card('clubs', 4),
        Card('clubs', 5),
        Card('clubs', 7),
        Card('clubs', 10),
        Card('clubs', 11)
    ]

    hands = [hand1, hand2, hand3]
    assert winners(hands) == {1,2}

def test_winners_1_winner():
    hand1 = [
        Card('hearts', 14),
        Card('hearts', 13),
        Card('hearts', 12),
        Card('hearts', 10),
        Card('hearts', 11)
    ]

    hand2 = [
        Card('diamonds', 4),
        Card('diamonds', 5),
        Card('diamonds', 7),
        Card('diamonds', 10),
        Card('diamonds', 11)
    ]

    hand3 = [
        Card('clubs', 2),
        Card('clubs', 5),
        Card('clubs', 7),
        Card('clubs', 10),
        Card('clubs', 11)
    ]

    hands = [hand1, hand2, hand3]
    assert winners(hands) == {0}

def test_winners_straights():
    hand1 = [
        Card('diamonds', 4),
        Card('hearts', 4),
        Card('hearts', 12),
        Card('hearts', 10),
        Card('hearts', 11)
    ]

    hand2 = [
        Card('diamonds', 4),
        Card('diamonds', 5),
        Card('diamonds', 7),
        Card('diamonds', 6),
        Card('clubs', 8)
    ]

    hand3 = [
        Card('clubs', 13),
        Card('spades', 12),
        Card('clubs', 11),
        Card('clubs', 10),
        Card('clubs', 9)
    ]

    hands = [hand1, hand2, hand3]
    assert winners(hands) == {2}

if __name__ == "__main__":
    test_flush()
    test_straight()
    test_four_of_a_kind()
    test_full_house()
    test_three_of_a_kind()
    test_two_pair()
    test_pair()
    test_high_card()
    test_royal_flush()
    test_compare_higher_card()
    test_compare_higher_flush()
    test_compare_royal_flush_split_pot()
    test_compare_two_straights_low_ace()
    test_compare_two_straights_high_ace()
    test_compare_split_pot_high_card()
    test_duplicate_cards()
    test_winners_3_winners()
    test_winners_2_winners()
    test_winners_1_winner()
    test_winners_straights()