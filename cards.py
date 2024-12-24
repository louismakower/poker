import random
suits = ['hearts', 'diamonds', 'clubs', 'spades']
class Card:
    def __init__(self, suit, value):
        assert suit in suits, "invalid suit"
        assert value in [i for i in range(2, 15)], "invalid value"
        self.suit = suit
        self.value = value


    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        names = {14:'A', 11:'J', 12:'Q', 13:'K'}
        if self.value in names:
            return names[self.value] + self.suit[0].upper()
        else:
            return str(self.value) + self.suit[0].upper()

class Pack:
    def __init__(self):
        self.cards = []
        for value in range(2,15):
            for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
                self.cards.append(Card(suit, value))

    def shuffle(self):
        random.shuffle(self.cards)

    def print_deck(self):
        for card in self.cards:
            print(card)

    def top_card(self):
        return self.cards.pop(0)

if __name__ == "__main__":
    pack = Pack()
    pack.print_deck()

    pack.shuffle()
    pack.print_deck()