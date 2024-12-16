from cards import Pack
from player import Player
from evaluator import winner, evaluation, values

hands = {value: key for key, value in values.items()}

class Table:
    def __init__(self, players):
        self.pack = Pack()
        self.pack.shuffle()
        self.players = players
        self.face_up_cards = []

    def deal(self):
        for player in self.players:
            card1 = self.pack.top_card()
            card2 = self.pack.top_card()
            player.cards = [card1, card2]

    def print_face_up(self):
        print([str(card) for card in self.face_up_cards])

    def flop(self):
        for i in range(3):
            self.face_up_cards.append(self.pack.top_card())
        self.print_face_up()

    def turn(self):
        self.face_up_cards.append(self.pack.top_card())
        self.print_face_up()

    def river(self):
        self.face_up_cards.append(self.pack.top_card())
        self.print_face_up()

if __name__ == "__main__":
    num_players = 5
    players = [Player() for i in range(num_players)]
    table = Table(players)
    table.deal()

    for player in table.players:
        print([str(card) for card in player.cards])

    table.flop()
    table.turn()
    table.river()
    this_round_winner = winner(players, table.face_up_cards)

    print([[hands[i], j] for i, j in [evaluation(player.get_best_hand(table.face_up_cards)) for player in players]])
    print(f'Player {this_round_winner+1} wins!')


