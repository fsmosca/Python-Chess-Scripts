#!/usr/bin/env python


"""
evalswing.py

Read pgn file and print max/min eval of each engine per game.


Setup:
  Install python 3.8 or newer


Requirements:
  chess==1.3.1
    pip install chess


Usage:
    python evalswing.py --input mygame.pgn
"""


__version__ = 'v0.2.0'
__author__ = 'fsmosca'
__credits__ = ['rwbc']
__script_name__ = 'evalswing'
__goal__ = 'Read pgn file and print max/min eval of each engine per game.'


import argparse
import time
from typing import List, Set, Dict, Tuple, Optional

import chess.pgn
from chess.engine import Mate
import pandas as pd


class EvalSwing:
    def __init__(self, input_pgn, min_depth=1, tcec=False, lichess=False,
                 spov=True):
        self.input_pgn = input_pgn
        self.min_depth = min_depth
        self.tcec = tcec
        self.lichess = lichess
        self.spov = spov

        self.num = []
        self.wnames = []
        self.bnames = []

        self.w_min_eval = []
        self.w_max_eval = []

        self.b_min_eval = []
        self.b_max_eval = []

        self.res = []

        self.w_mi_min = []
        self.w_mi_max = []

        self.b_mi_min = []
        self.b_mi_max = []

    def get_eval(
            self,
            board,
            comment: str,
            turn: bool,
            ply: int,
            black_eval: List[float],
            white_eval: List[float]
    ) -> float:
        """
        Returns move_eval with SPOV in pawn unit.
        """
        move_eval = None

        if 'book' in comment.lower():
            return move_eval

        if comment == '':
            if ply % 2:
                if len(black_eval):
                    move_eval = black_eval[-1]
            else:
                if len(white_eval):
                    move_eval = white_eval[-1]

            return move_eval

        if self.tcec:
            value = comment.split('wv=')[1].split(',')[0]
            depth = int(comment.split('d=')[1].split(',')[0])
            if 'M' in value:
                mate_num = int(value.split('M')[1])

                # Todo: Get mate score of Lc0.
                move_eval = Mate(mate_num).score(mate_score=32000) / 100

                move_eval = move_eval if turn else -move_eval
            else:
                move_eval = float(comment.split('wv=')[1].split(',')[0])
                move_eval = move_eval if turn else -move_eval

            if depth < self.min_depth:
                move_eval = None

        elif self.lichess:
            # Lichess eval is wpov.
            # [%eval -1.49] [%clk 0:15:10]
            # { [%eval #2] [%clk 0:13:18] }
            # [%clk 0:00:03], comment without eval
            if '[%eval ' in comment:
                split_eval = comment.split('%eval ')[1].split(']')[0]
                if '#' in split_eval:
                    mate_num = int(split_eval.split('#')[1])
                    move_eval = Mate(mate_num).score(mate_score=32000) / 100
                else:
                    move_eval = float(split_eval)
                move_eval = spov_score(move_eval, turn)
            else:
                # [%clk 0:00:03], comment without eval, game is over
                if board.is_check():
                    move_eval = Mate(0).score(mate_score=32000) / 100
                elif board.is_game_over():
                    move_eval = 0.0
                else:
                    move_eval = 0.0

        # Cutechess, winboard, shredder
        else:
            if len(comment.split()) == 1:
                # No eval/depth comment, just time.
                if not '/' in comment:
                    move_eval = None  # Set to zero if no history.
                    if ply % 2:
                        if len(black_eval):
                            move_eval = black_eval[-1]
                            if move_eval is not None:
                                move_eval = spov_score(move_eval, turn)
                    else:
                        if len(white_eval):
                            move_eval = white_eval[-1]
                            if move_eval is not None:
                                move_eval = spov_score(move_eval, turn)
                else:
                    depth = int(comment.split()[0].split('/')[1])
                    if depth >= self.min_depth:
                        move_eval = float(comment.split('/')[0])
            elif '+M' in comment or '-M' in comment:
                mate_num = int(comment.split('/')[0].split('M')[1])
                move_eval = Mate(mate_num).score(mate_score=32000)
                move_eval = (move_eval if '+M' in comment else -move_eval) / 100
            else:
                # Not {White mates}
                if '/' in comment:
                    try:
                        depth = int(comment.split()[0].split('/')[1])
                    except ValueError:
                        print(comment)
                        raise
                    if depth >= self.min_depth:
                        move_eval = float(comment.split('/')[0])

            if not self.spov:
                move_eval = spov_score(move_eval, turn)

        return move_eval

    def move_index(self, values, val, is_min=True):
        for i, n in enumerate(values):
            if n == val:
                return i

        return -1

    def evaluate(self, game, outputfn, cnt):
        """
        Read game get eval in the move comment and plot it.
        """
        ev = game.headers['Event']
        da = game.headers['Date']
        rd = game.headers['Round']
        wp = game.headers['White']
        bp = game.headers['Black']
        res = game.headers['Result']

        move_num, b_eval, w_eval = [], [], []
        for node in game.mainline():
            board = node.board()
            parent_node = node.parent
            parent_board = parent_node.board()
            comment = node.comment
            fmvn = parent_board.fullmove_number
            ply = parent_board.ply()

            move_eval = self.get_eval(board, comment, parent_board.turn, ply, b_eval, w_eval)

            # Side POV
            # Black
            if ply % 2:
                if move_eval is None:
                    b_eval.append(None)
                else:
                    b_eval.append(move_eval)
            # White
            else:
                w_eval.append(move_eval)
                move_num.append(fmvn)

        self.num.append(cnt)

        self.wnames.append(wp)
        self.bnames.append(bp)

        if res == '1-0':
            try:
                minv = min(x for x in w_eval if x is not None)
            except ValueError:
                minv = 0

            self.w_min_eval.append(minv)
            self.w_max_eval.append('-')

            mimin = self.move_index(w_eval, minv, is_min=True) + 1
            self.w_mi_min.append(mimin)
            self.w_mi_max.append('-')

        elif res == '0-1':
            try:
                maxv = max(x for x in w_eval if x is not None)
            except ValueError:
                maxv = 0

            self.w_max_eval.append(maxv)
            self.w_min_eval.append('-')

            mimax = self.move_index(w_eval, maxv, is_min=False) + 1
            self.w_mi_min.append('-')
            self.w_mi_max.append(mimax)
        else:
            try:
                minv = min(x for x in w_eval if x is not None)
            except ValueError:
                minv = 0

            try:
                maxv = max(x for x in w_eval if x is not None)
            except ValueError:
                maxv = 0

            mimin = self.move_index(w_eval, minv, is_min=True) + 1
            mimax = self.move_index(w_eval, maxv, is_min=False) + 1

            self.w_min_eval.append(minv)
            self.w_max_eval.append(maxv)

            self.w_mi_min.append(mimin)
            self.w_mi_max.append(mimax)

        if res == '0-1':
            try:
                minv = min(x for x in b_eval if x is not None)
            except ValueError:
                minv = 0

            self.b_min_eval.append(minv)
            self.b_max_eval.append('-')

            mimin = self.move_index(b_eval, minv, is_min=True) + 1
            self.b_mi_min.append(mimin)
            self.b_mi_max.append('-')

        elif res == '1-0':
            try:
                maxv = max(x for x in b_eval if x is not None)
            except ValueError:
                maxv = 0

            self.b_max_eval.append(maxv)
            self.b_min_eval.append('-')

            mimax = self.move_index(b_eval, maxv, is_min=False) + 1
            self.b_mi_min.append('-')
            self.b_mi_max.append(mimax)
        else:
            try:
                minv = min(x for x in b_eval if x is not None)
            except ValueError:
                minv = 0

            try:
                maxv = max(x for x in b_eval if x is not None)
            except ValueError:
                maxv = 0

            mimin = self.move_index(b_eval, minv, is_min=True) + 1
            mimax = self.move_index(b_eval, maxv, is_min=False) + 1

            self.b_min_eval.append(minv)
            self.b_max_eval.append(maxv)

            self.b_mi_min.append(mimin)
            self.b_mi_max.append(mimax)

        self.res.append(res)

        data = {'#': self.num, 'White': self.wnames, 'Black': self.bnames, 'Res': self.res,
                'WMaxMove': self.w_mi_max, 'WMaxEval': self.w_max_eval, 'WMinMove': self.w_mi_min, 'WMinEval': self.w_min_eval,
                'BMaxMove': self.b_mi_max, 'BMaxEval': self.b_max_eval, 'BMinMove': self.b_mi_min, 'BMinEval': self.b_min_eval}
        df = pd.DataFrame(data)

        return df

    def run(self):
        start_time = time.perf_counter()
        cnt = 0
        df = None

        with open(self.input_pgn) as pgn:
            while True:
                game = chess.pgn.read_game(pgn)
                if game is None:
                    break

                cnt += 1
                output = f'{self.input_pgn[0:-4]}_{cnt}.png'

                print(f'game: {cnt}')

                df = self.evaluate(game, output, cnt)

        if df is not None:
            print(df.to_string(index=False))

        print(f'Done {self.input_pgn}, Elapse (sec): {time.perf_counter() - start_time:0.3f}')


def spov_score(wpov_score, stm):
    return wpov_score if stm else -wpov_score


def main():
    parser = argparse.ArgumentParser(
        prog='%s %s' % (__script_name__, __version__),
        description=__goal__, epilog='%(prog)s')
    parser.add_argument('--input', required=True, type=str,
                        help='Input pgn filename (required).')
    parser.add_argument('--min-depth',
                        required=False, type=int,
                        default=1,
                        help='Minimum depth to consider the eval, default=1.')
    parser.add_argument('--tcec',
                        action='store_true',
                        help='Use this flag if pgn is from tcec, tested on s19-sf.')
    parser.add_argument('--lichess',
                        action='store_true',
                        help='Use this flag if pgn is from lichess.')
    parser.add_argument('--wpov',
                        action='store_true',
                        help='Use this flag if scores in the game are in wpov.')
    parser.add_argument('-v', '--version', action='version',
                        version=f'{__version__}')

    args = parser.parse_args()
    spov = False if args.wpov else True

    a = EvalSwing(
        args.input,
        min_depth = args.min_depth,
        tcec=args.tcec,
        lichess=args.lichess,
        spov=spov)

    a.run()


if __name__ == "__main__":
    main()
