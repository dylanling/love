import logging

from abc import ABCMeta, abstractmethod
from random import choice, sample
from functools import reduce
from pprint import pformat as format

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
    def move(self, game):
        logging.debug(str(self) + ' moving, current hand is: ' + format(game.hands[self]))
        return choice([card for card in game.hands[self] if game.is_legal(card)])

    def pass_cards(self, game, target_map):
        return sample(game.hands[self], 3)

class ConservativePlayer(Player):
    SUIT_ORDER = ['c', 'd', 's', 'h']

    def move(self, game):
        logging.debug(str(self) + ' moving, current hand is: ' + format(game.hands[self]))
        moves = ConservativePlayer.sorted_hand([card for card in game.hands[self] if game.is_legal(card)])
        logging.debug(str(self) + ' moving, current legal hand is: ' + format(moves))
        if not game.pile:
            return moves[0]
        non_capture_moves = [card for card in moves if card.suit is not game.pile[0][0].suit or card.value < game.pile[0][0].value]
        if non_capture_moves:
            return non_capture_moves[-1]
        return moves[0]

    def pass_cards(self, game, target_map):
        return ConservativePlayer.sorted_hand(game.hands[self])[:3]

    @staticmethod
    def sorted_hand(hand):
        sort_key = lambda card: (card.hearts_points(), card.value, ConservativePlayer.SUIT_ORDER.index(card.suit))
        return sorted(hand, key=sort_key)

