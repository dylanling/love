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
        sort_key = lambda card: (card.hearts_points(), card.value, ConservativePlayer.SUIT_ORDER.index(card.suit))
        moves = sorted([card for card in game.hands[self] if game.is_legal(card)], key=sort_key)
        logging.debug(str(self) + ' moving, current legal hand is: ' + format(moves))
        if not game.pile:
            return moves[0]
        non_capture_moves = [card for card in moves if card.suit is not game.pile[0][0].suit or card.value < game.pile[0][0].value]
        if non_capture_moves:
            return non_capture_moves[-1]
        return moves[0]

    def pass_cards(self, game, target_map):
        max_val_key = lambda card: (card.value, card.hearts_points(), ConservativePlayer.SUIT_ORDER.index(card.suit))
        return sorted(game.hands[self], key=max_val_key)[-3:]

class MoonShooter(ConservativePlayer):
    def move(self, game):
        players_with_points = [player for player in game.captured if sum(map(lambda c: c.hearts_points(), game.captured[player])) > 0]
        if not (len(players_with_points) is 0 or (len(players_with_points) is 1 and players_with_points[0] is self)):
            logging.debug('Not shooting moon due to players with points: ' + format(players_with_points))
            return super().move(game)
        sort_key = lambda card: (card.hearts_points(), card.value, ConservativePlayer.SUIT_ORDER.index(card.suit))
        moves = sorted([card for card in game.hands[self] if game.is_legal(card)], key=sort_key)
        logging.debug(str(self) + ' moving with moon shooting intention, current legal hand is: ' + format(moves))
        if not game.pile:
            return moves[-1]
        capture_moves = [card for card in moves if card.suit is game.pile[0][0].suit and card.value > game.pile[0][0].value]
        if capture_moves:
            if len(game.pile) is len(game.players) - 1:
                return capture_moves[0]
            return capture_moves[-1]
        return moves[0]

    def pass_cards(self, game, target_map):
        max_val_key = lambda card: (card.value, card.hearts_points(), ConservativePlayer.SUIT_ORDER.index(card.suit))
        return sorted(game.hands[self], key=max_val_key)[:3]

