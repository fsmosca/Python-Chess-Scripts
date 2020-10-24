#!/usr/bin/env python


"""
pc_0001.py

Remove nags by ply.


Setup:
  Install python 3.8 or newer


Requirements:
  python-chess==1.2.0
"""


__version__ = 'v0.1.0'
__script_name__ = 'pc_0001'


import argparse
import chess.pgn


def pc_0001(game, outfn, no_nag_ply=1):
    """
    Parse game, and create a new game with limited nags based on no_nag_ply.
    Save the new game in outfn.
    """
    my_game = chess.pgn.Game()
    my_node = my_game

    # Copy header.
    for k, v in game.headers.items():
        my_game.headers[k] = v

    for ply, node in enumerate(game.mainline()):
        game_move = node.move

        if ply + 1 < no_nag_ply:
            my_node = my_node.add_variation(game_move)
        else:
            my_node = my_node.add_variation(game_move, nags=node.nags)

    with open(outfn, 'a') as w:
        w.write(f'{my_game}\n\n')


def main():
    parser = argparse.ArgumentParser(
        prog='%s %s' % (__script_name__, __version__),
        description='Remove nags by ply.',
        epilog='%(prog)s')
    parser.add_argument('--input', required=True,
                        help='Input filename (required).')
    parser.add_argument('--output', required=False,
                        help='Output filename (not required).')
    parser.add_argument('--no-nag-ply', required=False, type=int,
                        help='Do not write nag if game ply is below this option value. Default=1.',
                        default=1)

    args = parser.parse_args()

    infn = args.input
    outfn = args.output

    if outfn is None:
        outfn = f'out_{infn}'

    with open(args.input) as pgnh:
        while True:
            game = chess.pgn.read_game(pgnh)
            if game is None:
                break

            pc_0001(game, outfn, args.no_nag_ply)


if __name__ == "__main__":
    main()
