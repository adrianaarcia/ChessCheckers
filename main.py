import sys
from checkers import Checkers
from chess import Chess

if len(sys.argv) > 1 and sys.argv[1] == "checkers":
    g = Checkers(*sys.argv[2:])
elif len(sys.argv) < 5 or sys.argv[4] == "8":
    g = Chess(*sys.argv[2:])
else:
    sys.exit()

g.start()