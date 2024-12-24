from table import Table
from player import RandomPlayer, RLPlayer, AutomaticPlayer
import matplotlib.pyplot as plt
suit_values = {'hearts':0, 'diamonds':1, 'clubs':2, 'spades':3} # should do one hot encoding here

class Environment:
    def __init__(self, player, num_bots, initial_money, verbose=0, terminate=500):
        other_players = [RandomPlayer(f"Bot {i+1}", initial_money) for i in range(num_bots)]
        self.players = [player] + other_players
        self.verbose = verbose
        self.rl_player = player
        self.num_hands = 0
        self.table = None
        self.terminate = terminate

    def reset(self):
        self.table = Table(self.players, verbose=self.verbose)
        self.table.new_hand_deal()
        self.table.deal_table_cards()
        self.num_hands += 1
        # face_up_cards = [item for card in self.table.face_up_cards for item in [card.value, suit_values[card.suit]]]
        face_up_cards = self.table.face_up_cards
        # player_cards = [item for card in self.rl_player.cards for item in [card.value, suit_values[card.suit]]]
        player_cards = self.rl_player.cards
        player_money = self.rl_player.money
        state = [face_up_cards, player_cards, player_money]
        return state

    def step(self, bet, amount):
        previous_money = self.rl_player.money
        self.table.take_bets_rl(bet, amount)
        self.table.get_matches()
        self.table.give_money_to_winner()
        reward = self.rl_player.money - previous_money
        self.table.reset()
        self.num_hands += 1
        self.table.new_hand_deal()
        self.table.deal_table_cards()

        # face_up_cards = [item for card in self.table.face_up_cards for item in [card.value, suit_values[card.suit]]]
        face_up_cards = self.table.face_up_cards
        # player_cards = [item for card in self.rl_player.cards for item in [card.value, suit_values[card.suit]]]
        player_cards = self.rl_player.cards
        player_money = self.rl_player.money
        next_state = [face_up_cards, player_cards, player_money]
        terminated = False if self.num_hands < self.terminate else True

        return next_state, reward, terminated

if __name__ == "__main__":
    terminated = False
    total_reward = [0]
    money_per_player = 100
    rl_player = AutomaticPlayer('Louis', money_per_player)
    env = Environment(rl_player, 10, money_per_player, verbose=1)
    state = env.reset()
    # print([str(card) for player in env.table.players_list for card in player.cards])
    while not terminated:
        bet, amount = rl_player.place_bet(state[0], state[2])
        state, reward, terminated = env.step(bet, amount)
        total_reward.append(total_reward[-1] + reward)
    plt.plot(total_reward)
    plt.show()


# formulation for betting:
# state: (cards on table (suit, value, suit, value, ... ), cards in hand (same), money in hand (float))
# action: how much to bet
# reward: money won on that round

# formulation for matching:
# state: (cards on table, cards in hand, current bet, money in hand, amount to match)
# action: whether to match (true or false)
# reward: score on that round

