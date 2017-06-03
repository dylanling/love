import logging

from players import DumbPlayer, ConservativePlayer
from hearts import Game

def main():
    logging.basicConfig(level=logging.INFO)
    players = [DumbPlayer(name) for name in ['Dummy1', 'Dummy2', 'Dummy3']] + [ConservativePlayer('Conservative1')]

    losses = {player:0 for player in players}

    for _ in range(100):
        game = Game(players)
        scores = game.play_game()
        for player in [player for player in scores if scores[player] >= 100]:
            losses[player] += 1

    logging.info('Losses: ' + format(losses))

if __name__ == '__main__':
    main()
