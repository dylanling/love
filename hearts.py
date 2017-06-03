import logging

from itertools import cycle
from functools import reduce
from random import shuffle
from pprint import pformat as format

from players import DumbPlayer, ConservativePlayer

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

    def hearts_points(self):
        if self.value is 10 and self.suit is 's':
            return 13
        return 1 if self.suit is 'h' else 0

    @staticmethod
    def deck():
        return [Card(value, suit) for value in range(13) for suit in Card.SUITS]

class Game:
    def __init__(self, players):
        if len(players) != 4:
            raise ValueError('Game requires four players')
        self.players = players
        self.scores  = {player:0 for player in players}
        self.targets = cycle([self.left_targets(), self.right_targets(), self.cross_targets(), self.self_targets()])
        # define these here so they are public to players
        self.captured  = {} # <Player, List<Card>>
        self.broken = False
        self.hands = {} # <Player, List<Card>>
        self.active = None
        self.pile = [] # <Tuple<Card, Player>>

    def left_targets(self):
        return {self.players[i]:self.players[i-1] for i in range(4)}

    def right_targets(self):
        return {self.players[i-1]:self.players[i] for i in range(4)}

    def cross_targets(self):
        return {self.players[i]:self.players[(i+2)%4] for i in range(4)}

    def self_targets(self):
        return {player:player for player in self.players}

    def fresh_hands(self):
        deck = Card.deck()
        shuffle(deck)
        return {self.players[i]:deck[(len(deck)//len(self.players))*i:(len(deck)//len(self.players))*(i+1)] for i in range(len(self.players))}

    def advance(self):
        card = self.active.move(self)
        logging.debug(str(self.active) + ' plays ' + str(card))
        if not self.broken and card.hearts_points() > 0:
            logging.debug('Hearts broken')
            self.broken = True
        self.hands[self.active].remove(card)
        self.pile.append((card, self.active))
        if len(self.pile) == len(self.players):
            logging.debug('Pile is :' + format(self.pile))
            capture = reduce(lambda a, b: b if b[0].suit == a[0].suit and b[0].value > a[0].value else a, self.pile)
            logging.debug('Capture is: ' + format(capture))
            self.captured[capture[1]] += [tup[0] for tup in self.pile]
            self.active = capture[1]
            self.pile = []
        else:
            self.active = self.players[self.players.index(self.active)-1]

    def is_legal(self, card):
        if self.pile:
            return card.suit is self.pile[0][0].suit or not [card for card in self.hands[self.active] if card.suit is self.pile[0][0].suit]
        else:
            if len(self.hands[self.active]) is 52 // len(self.hands):
                return card.suit is 'c' and card.value is 0
            return card.hearts_points() is 0 or (self.broken or not [card for card in self.hands[self.active] if card.hearts_points() is 0])

    def play_round(self, target_map):
        logging.debug('=== Beginning next round ===\nCurrent scores are:\n' + format(self.scores))
        
        self.captured  = {player:[] for player in self.players}
        self.hands = self.fresh_hands()
        self.pile = []
        self.broken = False

        logging.debug('Current hands before passing are:\n' + format(self.hands))

        passed = {player:player.pass_cards(self, target_map) for player in target_map}
        for player in passed:
            for card in passed[player]:
                self.hands[player].remove(card)
        for player in passed:
            self.hands[target_map[player]] += passed[player]

        self.active = [player for player in self.hands if [card for card in self.hands[player] if card.value == 0 and card.suit == Card.SUITS[0]]][0]

        logging.debug('Current hands after passing are:\n' + format(self.hands))

        while self.hands[self.active]:
            self.advance()

        self.update_points()

    def update_points(self):
        round_points = {player:sum(map(lambda c: c.hearts_points(), self.captured[player])) for player in self.captured}
        moon_shooter = [player for player in round_points if round_points[player] == 26]
        for player in self.scores:
            if not moon_shooter:
                self.scores[player] += round_points[player]
            elif moon_shooter and player is not moon_shooter[0]:
                self.scores[player] += 30

    def play_game(self):
        for target_map in self.targets:
            self.play_round(target_map)
            if [player for player in self.scores if self.scores[player] >= 100]:
                return self.scores

def main():
    logging.basicConfig(level=logging.INFO)
    players = [DumbPlayer(name) for name in ['Alice', 'Bob', 'Charlie']] + [ConservativePlayer('Daniel')]
    game = Game(players)
    logging.info('Scores: ' + format(game.play_game()))

if __name__ == '__main__':
    main()


