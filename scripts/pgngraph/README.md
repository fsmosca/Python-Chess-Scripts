# PGN Graph

Read pgn and plot eval and time in each game.

### Requirements
* Install python

* Intall dependent modules  
  * pip install chess
  * pip install matplotlib  
     On windows replace numpy version.  
     * pip uninstall numpy
     * pip install numpy==1.19.3

### Help

```python
Read pgn file and save eval and time plot per game.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input pgn filename (required).
  --figure-size-width FIGURE_SIZE_WIDTH
                        width length, default=6.
  --figure-size-height FIGURE_SIZE_HEIGHT
                        height length, default=4.
  --min-eval-limit MIN_EVAL_LIMIT
                        minimum eval limit along y-axis in pawn unit, default=-10.
  --max-eval-limit MAX_EVAL_LIMIT
                        minimum eval limit along y-axis in pawn unit, default=10.
  --min-move-limit MIN_MOVE_LIMIT
                        minimum move number limit along x-axis, default=None.
  --max-move-limit MAX_MOVE_LIMIT
                        maximum move number limit along x-axis, default=None.
  --dpi DPI             dots per in inch resolution, default=200.
  --plot-eval-bg-color PLOT_EVAL_BG_COLOR
                        Backgroud color of the eval plot, default=0.4.
  --plot-time-bg-color PLOT_TIME_BG_COLOR
                        Backgroud color of the time plot, default=0.4.
  --white-line-color WHITE_LINE_COLOR
                        The color of line for the white player, default=white.
  --black-line-color BLACK_LINE_COLOR
                        The color of line for the black player, default=black.
  --tcec                Use this flag if pgn is from tcec, tested on s19-sf.
  --lichess             Use this flag if pgn is from lichess.
  -v, --version         show program's version number and exit

pgngraph v0.24.0
```


### Command line
`python pgn_graph.py --input mygame.pgn`

