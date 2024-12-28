from cards import Card, suits
from evaluator import evaluation
import random

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

def generate_high_card():
    while True:
        # Select 5 unique values from 2 to 14 (Ace as 14)
        chosen_values = random.sample(range(2, 15), 5)

        # Sort the values to easily check for a straight
        chosen_values.sort()

        # Check if the values form a straight
        if any(chosen_values[i] + 1 == chosen_values[i + 1] for i in range(4)):
            continue  # If the values form a straight, regenerate

        # Randomly select 5 suits, allowing duplicates (since multiple cards can have the same suit)
        chosen_suits = random.choices(suits, k=5)

        # Check if all suits are the same (flush condition)
        if len(set(chosen_suits)) == 1:
            continue  # If all suits are the same (flush), regenerate

        # Create the hand of cards using the chosen values and suits
        cards = [Card(suit, value) for suit, value in zip(chosen_suits, chosen_values)]

        # Return the hand of cards as a high card
        return cards

def generate_pair():
    pair_value = random.randint(2, 14)
    pair_suit = random.sample(suits, 2)
    other_values = random.sample([v for v in range(2, 15) if v != pair_value], 3)
    other_suits = random.sample(suits, 3)

    cards = [
                Card(pair_suit[0], pair_value),
                Card(pair_suit[1], pair_value)
            ] + [Card(suit, value) for suit, value in zip(other_suits, other_values)]

    return cards

def generate_two_pair():
    pair_values = random.sample(range(2, 15), 2)
    pair_suits = [random.sample(suits, 2) for _ in range(2)]
    kicker_value = random.choice([v for v in range(2, 15) if v not in pair_values])
    kicker_suit = random.choice(suits)

    cards = [
        Card(pair_suits[0][0], pair_values[0]),
        Card(pair_suits[0][1], pair_values[0]),
        Card(pair_suits[1][0], pair_values[1]),
        Card(pair_suits[1][1], pair_values[1]),
        Card(kicker_suit, kicker_value)
    ]
    return cards

def generate_three_of_a_kind():
    triplet_value = random.randint(2, 14)
    triplet_suits = random.sample(suits, 3)
    other_values = random.sample([v for v in range(2, 15) if v != triplet_value], 2)
    other_suits = random.sample(suits, 2)

    cards = [
                Card(suit, triplet_value) for suit in triplet_suits
            ] + [Card(suit, value) for suit, value in zip(other_suits, other_values)]

    return cards

def generate_straight():
    while True:
        # Start with a random starting point for the straight
        start_value = random.randint(2, 10)  # Values from 2 to 10 so we can have a full 5-card straight
        if start_value == 10:  # Handle Ace-high straight (10, J, Q, K, A)
            values = [10, 11, 12, 13, 14]
        else:
            values = [start_value + i for i in range(5)]  # Generate a straight sequence

        # Randomly choose 5 suits, allowing duplicates
        suits_for_straight = random.choices(suits, k=5)

        # Check if the hand is a flush (all suits are the same)
        if len(set(suits_for_straight)) == 1:
            continue  # If it's a flush (straight flush), regenerate

        # Create the hand using the chosen values and suits
        cards = [Card(suit, value) for suit, value in zip(suits_for_straight, values)]

        return cards

def generate_flush():
    while True:
        # Randomly select a suit for the flush
        suit = random.choice(suits)

        # Randomly select 5 values from 2 to 14
        chosen_values = random.sample(range(2, 15), 5)

        # Check if this flush is actually a royal flush
        if set(chosen_values) == {10, 11, 12, 13, 14}:  # Royal flush check
            continue  # If it's a royal flush, regenerate

        # Check if this flush is actually a low straight flush
        if set(chosen_values) == {14, 2, 3, 4, 5}:
            continue  # regenerate

        # Check if the flush is a straight flush
        chosen_values.sort()  # Sort the values to check for a straight
        if all(chosen_values[i] + 1 == chosen_values[i + 1] for i in range(4)):  # Check for consecutive values
            continue  # If it's a straight flush, regenerate

        # Create the flush hand
        cards = [Card(suit, value) for value in chosen_values]

        # Return the flush hand
        return cards

def generate_full_house():
    triplet_value = random.randint(2, 14)
    pair_value = random.choice([v for v in range(2, 15) if v != triplet_value])
    triplet_suits = random.sample(suits, 3)
    pair_suits = random.sample(suits, 2)

    cards = [
                Card(suit, triplet_value) for suit in triplet_suits
            ] + [
                Card(suit, pair_value) for suit in pair_suits
            ]
    return cards

def generate_four_of_a_kind():
    quad_value = random.randint(2, 14)
    quad_suits = random.sample(suits, 4)
    kicker_value = random.choice([v for v in range(2, 15) if v != quad_value])
    kicker_suit = random.choice(suits)

    cards = [
                Card(suit, quad_value) for suit in quad_suits
            ] + [Card(kicker_suit, kicker_value)]
    return cards

def generate_straight_flush():
    suit = random.choice(suits)
    upper_value = random.randint(5,13)
    if upper_value == 5:
        cards = [
            Card(suit, upper_value),
            Card(suit, upper_value - 1),
            Card(suit, upper_value - 2),
            Card(suit, upper_value - 3),
            Card(suit, 14)
        ]
    else:
        cards = [
            Card(suit, upper_value),
            Card(suit, upper_value-1),
            Card(suit, upper_value-2),
            Card(suit, upper_value-3),
            Card(suit, upper_value-4)
        ]
    return cards

def generate_royal_flush():
    suit = random.choice(suits)
    cards = [
        Card(suit, 14),
        Card(suit, 13),
        Card(suit, 12),
        Card(suit, 11),
        Card(suit, 10)
    ]
    return cards


def test_high_card():
    hand = generate_high_card()
    assert evaluation(hand)[0] == values['high card']

def test_pair():
    hand = generate_pair()
    assert evaluation(hand)[0] == values['pair']

def test_two_pair():
    hand = generate_two_pair()
    assert evaluation(hand)[0] == values['two pair']

def test_three_of_a_kind():
    hand = generate_three_of_a_kind()
    assert evaluation(hand)[0] == values['three of a kind']

def test_straight():
    hand = generate_straight()
    assert evaluation(hand)[0] == values['straight']

def test_flush():
    hand = generate_flush()
    assert evaluation(hand)[0] == values['flush']

def test_full_house():
    hand = generate_full_house()
    assert evaluation(hand)[0] == values['full house']

def test_four_of_a_kind():
    hand = generate_four_of_a_kind()
    assert evaluation(hand)[0] == values['four of a kind']

def test_royal_flush():
    royal_flush = generate_royal_flush()
    assert evaluation(royal_flush)[0] == values['royal flush']

def test_straight_flush():
    straight_flush = generate_straight_flush()
    assert evaluation(straight_flush)[0] == values['straight flush']


if __name__ == "__main__":
    num_tests = 10000
    for i in range(num_tests):
        test_high_card()
        test_pair()
        test_two_pair()
        test_three_of_a_kind()
        test_straight()
        test_flush()
        test_full_house()
        test_four_of_a_kind()
        test_royal_flush()
        test_straight_flush()