import logging

from players import DumbPlayer, ConservativePlayer, MoonShooter
from hearts import Game

def main():
    logging.basicConfig(level=logging.INFO)
    players = [
        ConservativePlayer('Conservative1'),
        ConservativePlayer('Conservative2'),
        ConservativePlayer('Conservative3'),
        MoonShooter('MoonShooter1')
    ]

    losses = {player:0 for player in players}
    num_games = 100

    for _ in range(num_games):
        game = Game(players)
        scores = game.play_game()
        for player in [player for player in scores if scores[player] >= 100]:
            losses[player] += 1

    losses = {player:str((losses[player] / num_games) * 100) + '%' for player in losses}

    logging.info('Games ending in 100+ points: ' + format(losses))

if __name__ == '__main__':
    main()
