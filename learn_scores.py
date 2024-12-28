import numpy as np
from generator import generate_royal_flush, generate_flush, generate_four_of_a_kind, generate_full_house, generate_high_card, generate_pair, generate_straight, generate_straight_flush, generate_three_of_a_kind, generate_two_pair
from environment import suit_values
from evaluator import evaluation
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# generate data
num_datapoints = 100000
X = []
y=[]

def generate_all():
    high_card = generate_high_card()
    pair = generate_pair()
    two_pair = generate_two_pair()
    three_of_a_kind = generate_three_of_a_kind()
    straight = generate_straight()
    flush = generate_flush()
    full_house = generate_full_house()
    four_of_a_kind = generate_four_of_a_kind()
    straight_flush = generate_straight_flush()
    royal_flush = generate_royal_flush()
    return high_card, pair, two_pair, three_of_a_kind, straight, flush, full_house, four_of_a_kind, straight_flush, royal_flush

for _ in range(num_datapoints):
    (high_card, pair, two_pair, three_of_a_kind, straight, flush,
     full_house, four_of_a_kind, straight_flush, royal_flush) \
        = generate_all()
    for cards in [high_card, pair, two_pair, three_of_a_kind, straight, flush, full_house, four_of_a_kind, straight_flush, royal_flush]:

        x = [item for card in cards for item in [card.value, suit_values[card.suit]]]
        X.append(x)
        score = evaluation(cards)
        # diff_len = 6 - len(score)
        # for i in range(diff_len):
        #     score.append(0)
        y.append(score[0])

X = np.array(X)
y = np.array(y)
print(y)
print(X)

model = MLPClassifier(hidden_layer_sizes=(30, 30), learning_rate_init = 0.001, n_iter_no_change=40, verbose=True, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)
model.fit(X_train, y_train)
preds = model.predict(X_test)
accuracy = accuracy_score(preds, y_test)
print(accuracy)

(high_card, pair, two_pair, three_of_a_kind, straight, flush,
 full_house, four_of_a_kind, straight_flush, royal_flush)\
    = generate_all()

for cards in [high_card, pair, two_pair, three_of_a_kind, straight, flush, full_house, four_of_a_kind, straight_flush, royal_flush]:
    test = np.array([[item for card in cards for item in [card.value, suit_values[card.suit]]]])
    print(model.predict(test))


