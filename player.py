from evaluator import beats
from itertools import combinations

class Player:
    def __init__(self):
        self.cards = []

    def get_best_hand(self, table_cards):
        best_selection = table_cards[:3] + self.cards

        # don't use personal cards
        if len(table_cards) == 5:
            selection = table_cards
            if beats(selection, best_selection):
                best_selection = selection

        # use one card
        if len(table_cards) >= 4:
            for player_card in self.cards:
                for combination in list(list(x) for x in combinations(table_cards, 4)):
                    selection = combination + [player_card]
                    if beats(selection, best_selection):
                        best_selection = selection


        # use both cards:
        for combination in list(list(x) for x in combinations(table_cards, 3)):
            selection = combination + self.cards
            if beats(selection, best_selection):
                best_selection = selection

        return best_selection









