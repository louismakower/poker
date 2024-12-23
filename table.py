from cards import Pack
from player import Player, AutomaticPlayer, RandomPlayer
from evaluator import winners, values
import matplotlib.pyplot as plt
import numpy as np

hands = {value: key for key, value in values.items()}

class Table:
    """ A simple poker game when players bet once per round."""
    def __init__(self, players: list[Player], verbose=0):
        self.pack = Pack()
        self.pack.shuffle()
        self.players_list = players
        self.players = {player.name: player for player in players}
        self.face_up_cards = []
        self.money = 0
        self.verbose = verbose
        self.highest_bet = 0

    def reset(self):
        self.pack = Pack()
        self.pack.shuffle()
        self.face_up_cards = []
        self.players_list = list(self.players.values())

    def deal(self):
        # rotate dealer
        self.reset()
        for player in self.players_list:
            card1 = self.pack.top_card()
            card2 = self.pack.top_card()
            player.cards = [card1, card2]

    def print_face_up(self):
        print([str(card) for card in self.face_up_cards])

    def flop(self):
        for i in range(3):
            self.face_up_cards.append(self.pack.top_card())
        if self.verbose >= 1:
            self.print_face_up()

    def turn(self):
        self.face_up_cards.append(self.pack.top_card())
        if self.verbose >= 1:
            self.print_face_up()

    def river(self):
        self.face_up_cards.append(self.pack.top_card())
        if self.verbose >= 1:
            self.print_face_up()

    def take_bets(self):
        self.highest_bet = 0
        for player in self.players_list:
            bet = player.place_bet(self.face_up_cards)
            player.money -= bet # take bet
            self.money += bet # add to pot
            if self.verbose >= 1:
                print(f'{player.name} betted {bet}')
            self.highest_bet = max(self.highest_bet, bet)

    def get_matches(self):
        for player in self.players.values():
            match, amount = player.match(self.face_up_cards, self.highest_bet)
            if match:
                player.money -= amount  # take bet
                self.money += amount  # add to pot
                if self.verbose >= 1:
                    print(f'{player.name} matched with {amount} up to {self.highest_bet}')
            else:
                self.players_list.remove(player)
                if self.verbose >= 1:
                    print(f"{player.name} didn't match.  Kicked out.")
                    print(f"players remaining: {[player.name for player in self.players_list]}")

    def give_money_to_winner(self):
        hand_winners = winners([player.get_best_hand(self.face_up_cards) for player in self.players_list])
        if self.verbose >= 1:
            print(f"The winner(s) are: {[self.players_list[hand_winner].name for hand_winner in hand_winners]}")
        pot_split = self.money / len(hand_winners)
        for hand_winner in hand_winners:
            hand_winner_player = self.players_list[hand_winner]
            hand_winner_player.money += pot_split
            self.money -= pot_split
        assert abs(self.money) < 0.001 # allow rounding error
        self.money = 0

    def play_hand(self):
        assert all(player.money >= 0 for player in self.players_list)
        self.deal()
        # print player's cards
        if self.verbose >= 1:
            for player in self.players_list:
                print(f'{player.name}: {[str(card) for card in player.cards]}')

        self.flop()
        self.turn()
        self.river()
        # if verbose >= 1:
        #     print([[hands[i], j] for i, j in [evaluation(player.get_best_hand(table.face_up_cards)) for player in self.players]])
        self.take_bets()
        self.get_matches()
        self.give_money_to_winner()
        this_round_winner = winners([player.get_best_hand(self.face_up_cards) for player in self.players_list])
        if self.verbose >= 1:
            for player in self.players.values():
                print(f"{player.name} has {player.money}")
        self.reset()

if __name__ == "__main__":
    num_players = 5
    num_hands = 500
    initial_money = 100
    players = [AutomaticPlayer('louis', money=initial_money), AutomaticPlayer('bot', money=initial_money)]
    table = Table(players)

    num_experiments = 3000
    results = [[0]*num_players]

    for experiment in range(num_experiments):
        players = [RandomPlayer(f"Bot {bot_num}", initial_money) for bot_num in range(1, num_players)]
        players.append(AutomaticPlayer("Louis", initial_money))
        table = Table(players, verbose=1)
        for _ in range(num_hands):
            table.play_hand()
        results.append([player.money + results[experiment][index] for index, player in enumerate(players)])
    results = np.array(results)
    for i in range(num_players):
        plt.plot(results[:, i], label=table.players_list[i].name)
    plt.ylabel("Cumulative return")
    plt.xlabel("Number of experiments")
    plt.legend()
    plt.show()
    print(sum(results[-1]))
    print(num_experiments * (initial_money*num_players))

# formulation for matching:
# state: (cards on table, cards in hand, previous bet, money in hand, amount to match)
# action: whether to match (true or false)
# reward: score on that round

# formulation for betting:
# state: (cards on table, cards in hand, money in hand)
# action: how much to bet
# reward: score on that round