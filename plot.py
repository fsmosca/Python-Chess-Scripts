#!/usr/bin/env python


"""
plot.py

Read pgn file and save time and eval plots per game.


Setup:
  Install python 3.8 or newer


Requirements:
  chess==1.3.1
    pip install chess


Usage:
    python plot.py --input mygame.pgn
"""


__version__ = 'v0.15.0'
__author__ = 'fsmosca'
__credits__ = ['rwbc']
__script_name__ = 'Eval and Time Game Plotter'
__goal__ = 'Read pgn file and save eval and time plot per game.'


import argparse
import time
from typing import List, Set, Dict, Tuple, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import chess.pgn
from chess.engine import Mate


PLOT_BG_COLOR = '0.4'  # Gray shades, 0 to 1, 0 is darker.


class GameInfoPlotter:
    def __init__(self, input_pgn, width=6, height=4, min_eval_limit=-10,
                 max_eval_limit=10, dpi=200, tcec=False,
                 plot_eval_bg_color=PLOT_BG_COLOR,
                 plot_time_bg_color=PLOT_BG_COLOR,
                 white_line_color='white',
                 black_line_color='black',
                 min_move_limit=None,
                 max_move_limit=None):
        self.input_pgn = input_pgn
        self.fig_width = width
        self.fig_height = height
        self.min_eval = min_eval_limit
        self.max_eval = max_eval_limit
        self.dpi = dpi
        self.tcec = tcec
        self.plot_eval_bg_color = plot_eval_bg_color
        self.plot_time_bg_color = plot_time_bg_color
        self.white_line_color = white_line_color
        self.black_line_color =black_line_color
        self.min_move_limit = min_move_limit
        self.max_move_limit = max_move_limit

        plt.rc('legend', **{'fontsize': 6})

    def get_tick_spacing(self, miny, maxy):
        tick_spacing = 0.05
        y_abs = max(abs(miny), abs(maxy))

        if y_abs >= 4:
            tick_spacing = 1
        elif y_abs >= 2:
            tick_spacing = 0.5
        elif y_abs >= 1:
            tick_spacing = 0.25
        elif y_abs >= 0.5:
            tick_spacing = 0.1

        return tick_spacing

    def get_eval(
            self,
            comment: str,
            turn: bool,
            ply: int,
            black_eval: List[float],
            white_eval: List[float]
    ) -> float:
        """
        Returns move_eval with SPOV in pawn unit.
        """
        move_eval = 0.0

        if 'book' in comment.lower():
            return move_eval

        if comment == '':
            if ply % 2:
                move_eval = -black_eval[-1]
            else:
                move_eval = white_eval[-1]
            return move_eval

        if self.tcec:
            value = comment.split('wv=')[1].split(',')[0]
            if 'M' in value:
                mate_num = int(value.split('M')[1])

                # Todo: Get mate score of Lc0.
                move_eval = Mate(mate_num).score(mate_score=32000) / 100

                move_eval = move_eval if turn else -move_eval
            else:
                move_eval = float(comment.split('wv=')[1].split(',')[0])
                move_eval = move_eval if turn else -move_eval

        # Cutechess
        else:
            # No eval/depth comment, just time.
            if len(comment.split()) == 1:
                value = comment.split('s')[0]
                # {0}
                try:
                    if ply % 2:
                        move_eval = -black_eval[-1]
                    else:
                        move_eval = white_eval[-1]
                except ValueError:
                    pass
            elif '+M' in comment or '-M' in comment:
                mate_num = int(comment.split('/')[0].split('M')[1])
                move_eval = Mate(mate_num).score(mate_score=32000)
                move_eval = (move_eval if '+M' in comment else -move_eval) / 100
            else:
                # Not {White mates}
                if '/' in comment:
                    move_eval = float(comment.split('/')[0])

        return move_eval

    def get_time(self, comment):
        """
        Brackets are not included when reading comment below.

        {+13.30/12 0.020s}
        {0}
        {0.001}
        {0.002}
        """
        elapse_sec = 0.0

        if 'book' in comment.lower():
            return elapse_sec

        if comment == '':
            return elapse_sec

        # If pgn file file is from TCEC.
        if self.tcec:
            elapse_sec = int(comment.split('mt=')[1].split(',')[0])
            elapse_sec = elapse_sec // 1000

        # Cutechess
        else:
            # One part split, {0} or {0.001}, assume it is time.
            if len(comment.split()) == 1:
                value = comment.split('s')[0]
                try:
                    elapse_sec = float(value)
                except ValueError:
                    pass
            # Two parts split, {+13.30/12 0.020s}, eval/depth time
            else:
                # Not {White mates}
                if '/' in comment:
                    elapse_sec = float(comment.split()[1].split('s')[0])

        return elapse_sec

    def plotter(self, game, outputfn):
        """
        Read game get eval in the move comment and plot it.
        """
        ev = game.headers['Event']
        da = game.headers['Date']
        rd = game.headers['Round']
        wp = game.headers['White']
        bp = game.headers['Black']
        res = game.headers['Result']

        move_num, b_eval, w_eval, b_time, w_time = [], [], [], [], []
        for node in game.mainline():
            board = node.board()
            parent_node = node.parent
            parent_board = parent_node.board()
            comment = node.comment
            fmvn = parent_board.fullmove_number
            ply = parent_board.ply()

            move_eval = self.get_eval(comment, parent_board.turn, ply, b_eval, w_eval)
            time_elapse_sec = self.get_time(comment)

            # Black
            if ply % 2:
                # Positive eval is good for white while negative eval is good for black.
                b_eval.append(-move_eval)
                b_time.append(time_elapse_sec)
            else:
                w_eval.append(move_eval)
                move_num.append(fmvn)

                w_time.append(time_elapse_sec)

        fig, ax = plt.subplots(2, sharex=True, figsize=(self.fig_width, self.fig_height))

        plt.text(x=0.5, y=0.94, s=f"{wp} vs {bp}", fontsize=8, ha="center", transform=fig.transFigure)
        plt.text(x=0.5, y=0.91, s=f"{ev}, {da}, Round: {rd}, {res}", fontsize=6, ha="center", transform=fig.transFigure)

        plt.subplots_adjust(top=0.84, hspace=0.3)

        # Array should have the same size.
        if len(move_num) > len(b_eval):
            b_eval.append(b_eval[len(b_eval)-1])
            b_time.append(0)
        if len(move_num) > len(w_eval):
            w_eval.append(w_eval[len(w_eval)-1])
            w_time.append(0)

        line_width = 1.0
        ax[0].plot(move_num, w_eval, color=self.white_line_color, linewidth=line_width, label=f'{wp}')
        ax[0].plot(move_num, b_eval, color=self.black_line_color, linewidth=line_width, label=f'{bp}')

        ax[1].plot(move_num, w_time, color=self.white_line_color, linewidth=line_width, label=f'{wp}')
        ax[1].plot(move_num, b_time, color=self.black_line_color, linewidth=line_width, label=f'{bp}')

        ax[0].axhline(y=0.0, color='r', linestyle='-', linewidth=0.1)
        ax[1].axhline(y=0.0, color='r', linestyle='-', linewidth=0.1)

        plt.setp(ax[0].get_xticklabels(), fontsize=5)
        plt.setp(ax[0].get_yticklabels(), fontsize=5)

        plt.setp(ax[1].get_xticklabels(), fontsize=5)
        plt.setp(ax[1].get_yticklabels(), fontsize=5)

        ax[0].set_title('Evaluation', fontsize=7)
        ax[1].set_title('Elapse Time', fontsize=7)

        ax[0].set_ylabel('Score in pawn unit', fontsize=5)

        ax[1].set_xlabel('Move number', fontsize=5)
        ax[1].set_ylabel('movetime in sec', fontsize=5)

        ax[0].legend(loc='best')
        ax[1].legend(loc='best')

        miny1, miny2 = min(b_eval), min(w_eval)
        maxy1, maxy2 = max(b_eval), max(w_eval)
        miny = min(miny1, miny2)
        maxy = max(maxy1, maxy2)

        tick_spacing = self.get_tick_spacing(miny, maxy)
        ax[0].yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # Set eval limit along y-axis.
        ax[0].set_ylim(max(self.min_eval, min(miny1, miny2) - 0.01), min(self.max_eval, max(maxy1, maxy2) + 0.01))

        # Set limits along x-axis for move numbers
        if self.min_move_limit is None:
            xmin = min(move_num) - 1
        else:
            xmin = self.min_move_limit - 1
        if self.max_move_limit is None:
            xmax = len(move_num) + 1
        else:
            xmax = self.max_move_limit + 1

        xrange = min(max(move_num), xmax) - max(min(move_num), xmin)
        ax[0].set_xlim(max(min(move_num), xmin), min(max(move_num), xmax))
        ax[0].set_xticks(range(max(min(move_num), xmin), min(max(move_num), xmax), 1 + xrange//20))

        for i in range(2):
            ax[i].grid(linewidth=0.1)

        ax[0].set_facecolor(self.plot_eval_bg_color)
        ax[1].set_facecolor(self.plot_time_bg_color)

        plt.savefig(outputfn, dpi=self.dpi)
        # plt.show()

        plt.close()


    def run(self):
        start_time = time.perf_counter()
        cnt = 0

        with open(self.input_pgn) as pgn:
            while True:
                game = chess.pgn.read_game(pgn)
                if game is None:
                    break

                cnt += 1
                output = f'{self.input_pgn[0:-4]}_{cnt}.png'

                print(f'game: {cnt}')

                self.plotter(game, output)

        print(f'Done {self.input_pgn}, Elapse (sec): {time.perf_counter() - start_time:0.3f}')


def main():
    parser = argparse.ArgumentParser(
        prog='%s %s' % (__script_name__, __version__),
        description=__goal__, epilog='%(prog)s')
    parser.add_argument('--input', required=True, type=str,
                        help='Input pgn filename (required).')
    parser.add_argument('--figure-size-width',
                        required=False, type=int,
                        default=6,
                        help='width length, default=6.')
    parser.add_argument('--figure-size-height',
                        required=False, type=int,
                        default=4,
                        help='height length, default=4.')
    parser.add_argument('--min-eval-limit',
                        required=False, type=int,
                        default=-10,
                        help='minimum eval limit along y-axis in pawn unit, default=-10.')
    parser.add_argument('--max-eval-limit',
                        required=False, type=int,
                        default=10,
                        help='minimum eval limit along y-axis in pawn unit, default=10.')
    parser.add_argument('--min-move-limit',
                        required=False, type=int,
                        default=None,
                        help='minimum move number limit along x-axis, default=None.')
    parser.add_argument('--max-move-limit',
                        required=False, type=int,
                        default=None,
                        help='maximum move number limit along x-axis, default=None.')
    parser.add_argument('--dpi',
                        required=False, type=int,
                        default=200,
                        help='dots per in inch resolution, default=200.')
    parser.add_argument('--plot-eval-bg-color',
                        required=False, type=str,
                        default=PLOT_BG_COLOR,
                        help=f'Backgroud color of the eval plot, default={PLOT_BG_COLOR}.')
    parser.add_argument('--plot-time-bg-color',
                        required=False, type=str,
                        default=PLOT_BG_COLOR,
                        help=f'Backgroud color of the time plot, default={PLOT_BG_COLOR}.')
    parser.add_argument('--white-line-color',
                        required=False, type=str,
                        default='white',
                        help='The color of line for the white player, default=white.')
    parser.add_argument('--black-line-color',
                        required=False, type=str,
                        default='black',
                        help='The color of line for the black player, default=black.')
    parser.add_argument('--tcec',
                        action='store_true',
                        help='Use this flag if pgn is from tcec, tested on s19-sf.')
    parser.add_argument('-v', '--version', action='version',
                        version=f'{__version__}')

    args = parser.parse_args()

    a = GameInfoPlotter(
        args.input,
        width=args.figure_size_width,
        height=args.figure_size_height,
        min_eval_limit=args.min_eval_limit,
        max_eval_limit=args.max_eval_limit,
        dpi=args.dpi,
        tcec=args.tcec,
        plot_eval_bg_color=args.plot_eval_bg_color,
        plot_time_bg_color=args.plot_time_bg_color,
        white_line_color=args.white_line_color,
        black_line_color=args.black_line_color,
        min_move_limit=args.min_move_limit,
        max_move_limit=args.max_move_limit)

    a.run()


if __name__ == "__main__":
    main()
