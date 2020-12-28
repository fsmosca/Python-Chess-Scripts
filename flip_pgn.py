# -*- coding: utf-8 -*-
"""
Read games in pgn file and flip the moves. Save to file
the flipped game.

Requirements:
    python-chess
        pip install chess
"""


import argparse

import chess.pgn


tags_to_swap = ['White', 'Black', 'Result', 'WhiteElo', 'BlackElo',
                'WhiteFideId', 'BlackFideId', 'WhiteTitle', 'BlackTitle']


def swap_tags(game, fgame):
    """
    Swap some header tags.
    """
    fgame.headers['White'] = game.headers.get('Black', '?')
    fgame.headers['Black'] = game.headers.get('White', '?')

    if game.headers['Result'] == '1-0':
        fgame.headers['Result'] = '0-1'
    elif game.headers['Result'] == '0-1':
        fgame.headers['Result'] = '1-0'
    else:
        fgame.headers['Result'] = game.headers.get('Result', '*')

    fgame.headers['WhiteElo'] = game.headers.get('BlackElo', '?')
    fgame.headers['BlackElo'] = game.headers.get('WhiteElo', '?')

    fgame.headers['WhiteFideId'] = game.headers.get('BlackFideId', '?')
    fgame.headers['BlackFideId'] = game.headers.get('WhiteFideId', '?')

    fgame.headers['WhiteTitle'] = game.headers.get('BlackTitle', '?')
    fgame.headers['BlackTitle'] = game.headers.get('WhiteTitle', '?')

    # Update tags.
    for k, v in game.headers.items():
        if k in tags_to_swap:
            continue
        fgame.headers[k] = v

    return fgame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, type=str,
                        help='Input pgn filename.')
    parser.add_argument('--output', required=False,
                        help='Output pgn filename. If not specified'
                             ' it will be written in out_<input>.pgn')

    args = parser.parse_args()

    pgninfn = args.input
    pgnoutfn = args.output

    if pgnoutfn is None:
        pgnoutfn = f'out_{pgninfn}'
    
    with open(pgninfn) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            
            root_board = game.board()
            fb = root_board.mirror()
            
            for node in game.mainline():
                move = node.move

                # Flip the move.
                from_sq = chess.Move.from_uci(str(move)).from_square
                to_sq = chess.Move.from_uci(str(move)).to_square
                promo_pc = chess.Move.from_uci(str(move)).promotion
                
                from_sq_mirror = chess.square_mirror(from_sq)
                to_sq_mirror = chess.square_mirror(to_sq)

                # Save the flipped move.
                fb.push(chess.Move(from_sq_mirror, to_sq_mirror, promotion=promo_pc))

            # Convert the flipped board into a game.
            fgame = chess.pgn.Game().from_board(fb)

            fgame = swap_tags(game, fgame)

            # Save to file.
            with open(pgnoutfn, 'a') as f:
                f.write(f'{fgame}\n\n')
            

if __name__ == '__main__':
    main()
