import argparse
from colorMap import ColorMap

parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar='N', type=str, nargs=1, help='an input filename')
parser.add_argument('--increment', help="color range assigned incrementally for full range in input value set",
                    action="store_true")
parser.add_argument('--truncate', help="color range assigned incrementally, but only for values in input set",
                    action="store_true")
parser.add_argument('--outputfile', help="specify an SVG output filename")
parser.add_argument('--low', help="specify the 'low' color in gradient either as color name (e.g. 'red') or hex value")
parser.add_argument('--high', help="specify the 'high' color in gradient")
parser.add_argument('--medium', help="specify the 'medium' color in the gradient")
args = parser.parse_args()

my_map = ColorMap(
    args.input_file[0],
    increment=args.increment,
    truncate=args.truncate,
    low=args.low,
    medium=args.medium,
    high=args.high,
    output=args.outputfile
)

my_map.color_states()