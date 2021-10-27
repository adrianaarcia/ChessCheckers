# Example board
"""
1 ⚈ ◻ ⚈ ◻ ⚈ ◻ ⚈ ◻
2 ◻ ⚈ ◻ ⚈ ◻ ⚈ ◻ ⚈
3 ⚈ ◻ ⚈ ◻ ⚈ ◻ ⚈ ◻
4 ◻ ◼ ◻ ◼ ◻ ◼ ◻ ◼
5 ◼ ◻ ◼ ◻ ◼ ◻ ◼ ◻
6 ◻ ⚆ ◻ ⚆ ◻ ⚆ ◻ ⚆
7 ⚆ ◻ ⚆ ◻ ⚆ ◻ ⚆ ◻
8 ◻ ⚆ ◻ ⚆ ◻ ⚆ ◻ ⚆
  a b c d e f g h
"""
# Checker symbols
# ⛀
# ⛁
# ⛂
# ⛃
# ⚆
# ⚇
# ⚈
# ⚉
# the piece with 2 dots is a "king", and the single dot is a "man"
# these are unicode symbols


# Code for translating coordinates like b5<->(4, 1)
def convert_checker_coord(coord):
    col = coord[:1]
    row = coord[1:]
    col = ord(col) - 96
    row = int(row)
    return (row - 1, col - 1)

def convert_matrix_coord(coord):
    row, col = coord
    return chr(col + 96 + 1) + str(row + 1)


