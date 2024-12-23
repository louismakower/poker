from evaluator import beats, evaluation, equals
from itertools import combinations
import random

class Player:
    def __init__(self, name, money):
        self.cards = []
        self.name = name
        self.money = money
        self.in_hand = True
        self.recent_bet = 0

    def place_bet(self, table_cards):
        raise NotImplementedError

    def match(self, table_cards, high_bet):
        raise NotImplementedError

    def get_best_hand(self, table_cards):
        best_selection = table_cards[:3] + self.cards

        # don't use personal cards
        if len(table_cards) == 5:
            selection = table_cards
            if (not equals(selection, best_selection)) and beats(selection, best_selection):
                best_selection = selection

        # use one card
        if len(table_cards) >= 4:
            for player_card in self.cards:
                for combination in list(list(x) for x in combinations(table_cards, 4)):
                    selection = combination + [player_card]
                    if (not equals(selection, best_selection)) and beats(selection, best_selection):
                        best_selection = selection


        # use both cards:
        for combination in list(list(x) for x in combinations(table_cards, 3)):
            selection = combination + self.cards
            if (not equals(selection, best_selection)) and beats(selection, best_selection):
                best_selection = selection

        return best_selection

class AutomaticPlayer(Player):
    def place_bet(self, table_cards):
        best_hand = self.get_best_hand(table_cards)
        best_hand_score = evaluation(best_hand)[0]
        if best_hand_score > 4:
            bet = self.money # all in for hand above 3
        elif best_hand_score > 2:
            bet = self.money / 3
        else:
            bet = 0

        assert bet <= self.money
        self.recent_bet = bet
        return bet

    def match(self, table_cards, high_bet):
        if self.recent_bet == high_bet:
            return True, 0

        difference = high_bet - self.recent_bet
        has_enough_money = difference < self.money
        if not has_enough_money:
            return False, None

        if self.recent_bet == 0:
            fraction_of_prev_bet = float('inf')
        else:
            fraction_of_prev_bet = difference / self.recent_bet

        best_hand = self.get_best_hand(table_cards)
        best_hand_score = evaluation(best_hand)[0]

        if best_hand_score > 2 and fraction_of_prev_bet < 0.5:
            # if feeling lucky with decent hand, match
            return True, high_bet - self.recent_bet
        else:
            return False, None

class RandomPlayer(Player):
    def place_bet(self, table_cards):
        bet = random.random() * (self.money / 2)
        self.recent_bet = bet
        return bet

    def match(self, table_cards, high_bet):
        if self.recent_bet == high_bet:
            return True, 0

        has_enough_money = (high_bet - self.recent_bet) < self.money
        if not has_enough_money:
            return False, None

        if self.recent_bet <= 0.1 * high_bet:
            return False, None
        else:
            coin = random.random()
            if coin > 0.1:
                return True, high_bet - self.recent_bet
            else:
                return False, None