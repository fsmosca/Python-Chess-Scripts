# EvalSwing

Read pgn and tabulate relevant minimum and maximum scores.

### Requirements
* Install python

* Intall dependent modules  
  * pip install chess
  * pip install pandas  
     On windows replace numpy version.  
     * pip uninstall numpy
     * pip install numpy==1.19.3

### Help

```python
usage: evalswing v0.1.0 [-h] --input INPUT [--min-depth MIN_DEPTH] [--tcec] [--lichess] [-v]

Read pgn file and print max/min eval of each engine per game.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input pgn filename (required).
  --min-depth MIN_DEPTH
                        Minimum depth to consider the eval, default=1.
  --tcec                Use this flag if pgn is from tcec, tested on s19-sf.
  --lichess             Use this flag if pgn is from lichess.
  -v, --version         show program's version number and exit

evalswing v0.1.0
```


### Command line
python evalswing.py --input TCEC_Season_19_-_Superfinal.pgn --tcec

### Sample output
```
   #                                   White                                   Black      Res WMaxMove WMaxEval  WMinMove  WMinEval  BMaxMove  BMaxEval BMinMove BMinEval
   1     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2        6     0.15        34      0.00         6     -0.00        9    -0.27
   2  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2        6     0.21        13      0.00        39      0.01        8    -0.07
   3     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2        9     0.34        40      0.06        29     -0.00       11    -0.64
   4  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2       13     0.76        39      0.00        45     -0.00        9    -0.32
   5     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183      1-0        -        -         5      0.43         6     -0.86        -        -
   6  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190      1-0        -        -         9      1.07         5     -0.43        -        -
   7     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2       35     0.11        10     -0.08         9      0.27       11       -0
   8  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2       23        0        10     -0.70        12      0.27       30       -0
   9     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2       45     0.01         5     -0.30        13      1.55       16       -0
  10  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2       52        0        30     -0.76       157      0.81      211     0.06
  11     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183      1-0        -        -         5      0.54        13     -0.90        -        -
  12  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190      1-0        -        -         5      0.99        10     -0.49        -        -
  13     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2       28     0.64        71      0.01        18     -0.00       24    -0.98
  14  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2       14      1.1        31      0.00        45     -0.05        6     -0.4
  15     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2       31     0.49        76      0.09        32     -0.00       11    -0.79
  16  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2       22      1.1        85      0.15        88     -0.05       22    -0.51
  17     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2       24     0.55        66      0.06        29     -0.00       25    -1.17
  18  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190      1-0        -        -         8      0.77         9     -0.39        -        -
  19     LCZero v0.26.3-rc1_T60.SV.JH.92-190  Stockfish 202009282242_nn-baeb9ef2d183  1/2-1/2        8     0.18        28     -0.01        11     -0.00        7    -0.32
  20  Stockfish 202009282242_nn-baeb9ef2d183     LCZero v0.26.3-rc1_T60.SV.JH.92-190  1/2-1/2       12     0.27        14      0.00        24      0.02        7    -0.18
  
  ...

```

