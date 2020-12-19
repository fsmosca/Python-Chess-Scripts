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


__version__ = 'v0.8.0'
__author__ = 'fsmosca'
__credits__ = ['rwbc']
__script_name__ = 'Eval and Time Game Plotter'
__goal__ = 'Read pgn file and save eval and time plot per game.'


import argparse
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import chess.pgn
from chess.engine import Mate


PLOT_BG_COLOR = '#D8DFDF'


class GameInfoPlotter:
    def __init__(self, input_pgn, width=6, height=4, min_eval_limit=-10,
                 max_eval_limit=10, dpi=200, tcec=False,
                 plot_eval_bg_color=PLOT_BG_COLOR,
                 plot_time_bg_color=PLOT_BG_COLOR,
                 white_line_color='white',
                 black_line_color='black'):
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

        x, y1, y2, t1, t2 = [], [], [], [], []
        for node in game.mainline():
            board = node.board()
            parent_node = node.parent
            parent_board = parent_node.board()
            comment = node.comment
            fmvn = parent_board.fullmove_number
            ply = parent_board.ply()

            if 'book' in comment.lower():
                eval = 0.0
                tv = 0.0
            else:
                if self.tcec:
                    # Mate score
                    value = comment.split('wv=')[1].split(',')[0]
                    if 'M' in value:
                        eval = 1000
                        eval = eval if parent_board.turn else -eval
                    else:
                        eval = float(comment.split('wv=')[1].split(',')[0])
                        eval = eval if parent_board.turn else -eval

                    # Get time
                    if 'book' in comment.lower():
                        tv = 0.0
                    else:
                        tv = int(comment.split('mt=')[1].split(',')[0])
                        tv = tv//1000

                # Cutechess
                else:
                    if '+M' in comment or '-M' in comment:
                        mate_num = int(comment.split('/')[0].split('M')[1])
                        eval = Mate(mate_num).score(mate_score=32000)
                        eval = (eval if '+M' in comment else -eval) / 100
                    elif comment == '':
                        eval = 0.0
                    else:
                        try:
                            eval = float(comment.split('/')[0])
                        except ValueError:
                            eval = 0.0

                    # Get time.
                    # +13.30/12 0.020s
                    if comment == '':
                        tv = 0.0
                    else:
                        try:
                            tv = float(comment.split()[1].split('s')[0])
                        except ValueError:
                            tv = 0.0

            # Black
            if ply % 2:
                # Positive eval is good for white while negative eval is good for black.
                y1.append(-eval)
                t1.append(tv)
            else:
                y2.append(eval)
                x.append(fmvn)

                t2.append(tv)

        fig, ax = plt.subplots(2, sharex=True, figsize=(self.fig_width, self.fig_height))
        plt.subplots_adjust(top=0.85, hspace=0.3)

        fig.suptitle(f'{wp} vs {bp}\n{ev}, {da}, Round: {rd}, {res}\n', fontsize=8)

        # Array should have the same size.
        if len(x) > len(y1):
            y1.append(y1[len(y1)-1])
            t1.append(0)
        if len(x) > len(y2):
            y2.append(y2[len(y2)-1])
            t2.append(0)

        line_width = 1.0
        ax[0].plot(x, y2, color=self.white_line_color, linewidth=line_width, label=f'{wp}')
        ax[0].plot(x, y1, color=self.black_line_color, linewidth=line_width, label=f'{bp}')

        ax[1].plot(x, t2, color=self.white_line_color, linewidth=line_width, label=f'{wp}')
        ax[1].plot(x, t1, color=self.black_line_color, linewidth=line_width, label=f'{bp}')

        ax[0].axhline(y=0.0, color='r', linestyle='-', linewidth=0.1)
        ax[1].axhline(y=0.0, color='r', linestyle='-', linewidth=0.1)

        plt.setp(ax[0].get_xticklabels(), fontsize=5)
        plt.setp(ax[0].get_yticklabels(), fontsize=5)

        plt.setp(ax[1].get_xticklabels(), fontsize=5)
        plt.setp(ax[1].get_yticklabels(), fontsize=5)

        ax[0].set_title('Evaluation', fontsize=8)
        ax[1].set_title('Elapse Time', fontsize=8)

        ax[0].set_ylabel('Score in pawn unit', fontsize=5)

        ax[1].set_xlabel('Move number', fontsize=5)
        ax[1].set_ylabel('movetime in sec', fontsize=5)

        ax[0].legend(loc='best')
        ax[1].legend(loc='best')

        miny1, miny2 = min(y1), min(y2)
        maxy1, maxy2 = max(y1), max(y2)
        miny = min(miny1, miny2)
        maxy = max(maxy1, maxy2)

        tick_spacing = self.get_tick_spacing(miny, maxy)
        ax[0].yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        # Set eval limit along y-axis.
        ax[0].set_ylim(max(self.min_eval, min(miny1, miny2) - 0.01), min(self.max_eval, max(maxy1, maxy2) + 0.01))

        for i in range(2):
            ax[i].grid(linewidth=0.1)

        tick_spacing = 1 + len(x) // 20
        ax[0].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

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
        black_line_color=args.black_line_color)

    a.run()


if __name__ == "__main__":
    main()
