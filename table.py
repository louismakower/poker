from cards import Pack
from player import Player, AutomaticPlayer, RandomPlayer, RLPlayer
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
        self.rotation_order = players[:]
        self.players_dict = {player.name: player for player in players}
        self.face_up_cards = []
        self.money = 0
        self.verbose = verbose
        self.highest_bet = 0

    def reset(self):
        self.pack = Pack()
        self.pack.shuffle()
        self.face_up_cards = []
        self.players_list = list(self.players_dict.values())

    def new_hand_deal(self):
        self.reset()
        # rotate order
        self.rotate_players()

        for player in self.players_list:
            card1 = self.pack.top_card()
            card2 = self.pack.top_card()
            player.cards = [card1, card2]

    def rotate_players(self):
        self.rotation_order.append(self.rotation_order.pop(0))
        self.players_list = [player for player in self.rotation_order]

    def print_face_up(self):
        print([str(card) for card in self.face_up_cards])

    def deal_table_cards(self):
        self.flop()
        self.turn()
        self.river()

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
        remove_players = []
        for player in self.players_list:
            bet, amount = player.place_bet(self.face_up_cards, self.highest_bet)
            if bet:
                player.money -= amount # take bet
                self.money += amount # add to pot
                self.highest_bet = max(self.highest_bet, amount)
                if self.verbose >= 1:
                    print(f'{player.name} betted {amount:.2f}')
            else:
                remove_players.append(player)
                if self.verbose >= 1:
                    print(f"{player.name} didn't bet.  Kicked out")

        for player in remove_players:
            self.players_list.remove(player)

        if self.verbose >= 1:
            print(f"Players remaining: {[player.name for player in self.players_list]}")

    def get_matches(self):
        remove_players = []
        for player in self.players_list:
            match, amount = player.match(self.face_up_cards, self.highest_bet)
            if match:
                player.money -= amount  # take bet
                self.money += amount  # add to pot
                if self.verbose >= 1 and amount > 0:
                    print(f'{player.name} matched with {amount:.2f} up to {self.highest_bet:.2f}')
            else:
                remove_players.append(player)
                if self.verbose >= 1:
                    print(f"{player.name} didn't match.  Kicked out.")


        for player in remove_players:
            self.players_list.remove(player)
        if self.verbose >= 1:
            print(f"Players remaining: {[player.name for player in self.players_list]}")

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
        self.new_hand_deal()
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
            for player in self.players_dict.values():
                print(f"{player.name} has {player.money}")
        self.reset()

    def take_bets_rl(self, rl_bet, rl_amount):
        self.highest_bet = 0
        remove_players = []
        for player in self.players_list:
            if isinstance(player, RLPlayer):
                bet, amount = rl_bet, rl_amount
            else:
                bet, amount = player.place_bet(self.face_up_cards, self.highest_bet)

            if bet and amount >= self.highest_bet:
                player.money -= amount # take bet
                self.money += amount # add to pot
                self.highest_bet = max(self.highest_bet, amount)
                if self.verbose >= 1:
                    print(f'{player.name} betted {amount:.2f}')
            else:
                remove_players.append(player)
                if self.verbose >= 1:
                    print(f"{player.name} didn't bet.  Kicked out")

        for player in remove_players:
            self.players_list.remove(player)

        if self.verbose >= 1:
            print(f"Players remaining: {[player.name for player in self.players_list]}")

def run_experiment():
    num_players = 4
    num_hands = 10
    initial_money = 100

    num_experiments = 100
    results = [[0] * num_players]

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
    print(num_experiments * (initial_money * num_players))

if __name__ == "__main__":
    run_experiment()


    # initial_money = 100
    # num_players = 4
    # players = [RandomPlayer(f"Bot {bot_num}", initial_money) for bot_num in range(1, num_players)]
    # players.append(AutomaticPlayer("Louis", initial_money))
    # table = Table(players, verbose=1)
    # for _ in range(50):
    #     print("*"*40)
    #     table.new_hand_deal()
    #     if table.verbose >= 1:
    #         for player in table.players_list:
    #             print(f'{player.name}: {[str(card) for card in player.cards]}')
    #
    #     table.flop()
    #     table.turn()
    #     table.river()
    #     table.take_bets()
    #     table.get_matches()
    #     table.give_money_to_winner()
    #     if table.verbose >= 1:
    #         for player in table.players_dict.values():
    #             print(f"{player.name} has {player.money}")

