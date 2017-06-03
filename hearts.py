from abc import ABCMeta, abstractmethod
from itertools import cycle
from random import shuffle
from pprint import pprint

class Card:
    SUITS = ['c', 'd', 's', 'h']
    RANKS = {12: 'A', 11: 'K', 10: 'Q', 9: 'J', 8: 'T'}

    def __init__(self, value, suit):
        if suit not in Card.SUITS or value not in range(0,13):
            raise ValueError('invalid suit or rank')
        self.value = value
        self.suit = suit

    def __str__(self):
        return (Card.RANKS[self.value] if self.value in Card.RANKS else str(self.value + 2)) + self.suit

    def __repr__(self):
        return str(self)

    @staticmethod
    def deck():
        return [Card(value, suit) for value in range(13) for suit in Card.SUITS]

class Player(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @abstractmethod
    def move(self, game):
        raise NotImplementedError

    @abstractmethod
    def pass_cards(self, game):
        raise NotImplementedError

class DumbPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def move(self, game):
        return game.round.hands[self][0]

    def pass_cards(self, game):
        return game.round.hands[self][:3]

class Game:
    def __init__(self, players):
        if len(players) != 4:
            raise ValueError('Game requires four players')
        self.players = players
        self.scores  = {player:0 for player in players}
        self.targets = cycle([self.left_targets(), self.right_targets(), self.cross_targets(), self.self_targets()])
        self.round = Round(players, next(self.targets))

    def left_targets(self):
        return {self.players[i]:self.players[i-1] for i in range(4)}

    def right_targets(self):
        return {self.players[i-1]:self.players[i] for i in range(4)}

    def cross_targets(self):
        return {self.players[i]:self.players[(i+2)%4] for i in range(4)}

    def self_targets(self):
        return {player:player for player in self.players}
        
# TODO: move out pass targets from round, all player logic should be invoked from Game
class Round:
    def __init__(self, players, pass_targets):
        if (len(players) != 4 or [player for player in players if player not in pass_targets] or 
            [player for player in players if player not in pass_targets.values()]):
            raise ValueError('Invalid inputs to round of Hearts')
        self.players = players
        self.pass_targets = pass_targets
        self.captured  = {player:[] for player in players}
        self.broken = False
        self.hands, self.active = self.initial_hands_and_player()
        self.pile = []

    def initial_hands_and_player(self):
        deck = Card.deck()
        shuffle(deck)
        cards = {self.players[i]:deck[13*i:13*(i+1)] for i in range(len(self.players))}
        first = [player for player in cards if [card for card in cards[player] if card.value == 0 and card.suit == Card.SUITS[0]]][0]
        return cards, first

    def is_complete(self):
        return not self.hands[self.active]

    def advance(self, card):
        self.cards[self.active].remove(card)
        self.pile.append((card, self.active))
        if len(self.pile) == len(self.players):
            capture = reduce(lambda a, b: b if b[0].suit == a[0].suit and b[0].value > a[0].value else a, self.pile)
            self.captured[capture[1]].append(capture[0])
            self.active = capture[1]

players = [DumbPlayer(name) for name in ['Alice', 'Bob', 'Charlie', 'Daniel']]
game = Game(players)
pprint(game.round.pass_targets)
pprint(game.round.hands)
pprint(game.round.active)
pprint(players[0].pass_cards(game))
pprint(players[0].move(game))