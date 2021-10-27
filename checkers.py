import enum
import games

class CheckersSymbols(enum.Enum):
    man0 = "⚆"
    man1 = "⚈"
    king0 = "⚇"
    king1 = "⚉"


class Checkers(games.Game):
    def set_up_board(self):
        """
        Each player starts with men on every dark square within the three rows closest to that player's side. 
        The row closest to each player is called the kings row or crownhead. 
        The white player starts at the bottom of the board (rows 6-8 for a normal size board, see the figure).

        """
        player1 = []
        player2 = []
        for j in range(0,3):
            for k in range(self.board.size):
                #player1, white
                tile = self.board.tiles[self.board.size-1-j][k]
                if tile.color == games.COLORS[1]:
                    p = Man(self.board, games.COLORS[0], tile)
                    tile.occ = p
                    player1.append(p)

                #player2, black
                tile = self.board.tiles[j][k]
                if tile.color == games.COLORS[1]:
                    p = Man(self.board, games.COLORS[1], tile)
                    tile.occ = p
                    player2.append(p)
        
        self.players[0].pieces = player1
        self.players[1].pieces = player2
        #return [player1, player2]
    def gen_valid_moves(self,plyr):
        #force captures
        [moves, captures] = plyr.possible_moves()
        if not captures:
            return moves
        else:
            return captures
    def has_lost(self,plyr):
        for piece in plyr.pieces:
            if piece.pos is not None:
                return False
        return True
    def check_win(self):
        p1 = self.players[0]
        p2 = self.players[1]
        
        if self.has_lost(p1):
            return p2
        if self.has_lost(p2):
            return p1
        return False


class Checker(games.Piece):
    def possible_moves(self):
        return [self.find_moves(), self.find_jumps(self.pos)]
    def find_moves(self):
        res = []
        for dir in self.move_dir:
            row_dir = dir[0]
            col_dir = dir[1]
            adj_row = self.pos.row+row_dir
            adj_col = self.pos.col+col_dir

            tile_av = self.tile_available(adj_row, adj_col)
            if tile_av is not None: #if in range
                tile = tile_av[1]
                if tile_av[0]: #tile is not occupied
                    m = CheckersMove(self, self.pos, tile) #create move
                    if (adj_row == self.board.size-1 and row_dir == 1) or (adj_row == 0 and row_dir == -1) and type(self) is Man: #promotion
                        m.promotion = True
                    res += [m]
        return res
    def valid_jump(self, row, col, row_dir, col_dir, captured):
        p_row = row+row_dir
        p_col = col + col_dir
        j_col = p_col + col_dir
        j_row = p_row+row_dir

        p_av = self.tile_available(p_row, p_col)
        j_av = self.tile_available(j_row, j_col)
        #need to check that there is a free tile to land on within range and that there is an oppenent piece to be captured
        if p_av is not None and j_av is not None and not p_av[0] and (j_av[0] or j_av[1] is self.pos):
            cptrd = p_av[1].occ
            if cptrd.color != self.color and cptrd not in captured: #valid jump
                return [cptrd, j_av[1]]
        return []
    def find_jumps(self, tile, captured=[]):
        #check adjacent squares
        squares = []
        row_dir = None
        for t in self.move_dir:
            row_dir = t[0]
            squares.append(self.valid_jump(tile.row, tile.col, row_dir, t[1], captured))
        if not any(squares): #base case: no more jumps
            if not captured:
                return []
            else:
                m = CheckersMove(self, self.pos, tile, captured) #create move
                if (tile.row == self.board.size-1 and row_dir == 1) or (tile.row == 0 and row_dir == -1) and type(self) is Man: #promotion
                        m.promotion = True
                return [m]
        
        res = []
        for square in squares:
            if square:
                cap = captured + [square[0]] #add piece to captured
                res += self.find_jumps(square[1], cap) #look for more possible jumps in the sequence
               
        return res

class Man(Checker):
    def __init__(self, color, board, pos=None):
        super().__init__(color,board,pos)
        if self.color == games.COLORS[0]:
            row = -1
        else:
            row = 1
        self.move_dir = [[row, -1],[row, 1]]
        self.value = 1
    def __str__(self):
        if self.color == games.COLORS[0]:
            return CheckersSymbols.man0.value
        else:
            return CheckersSymbols.man1.value
class King(Checker):
    def __init__(self, color, board, pos=None):
        super().__init__(color,board,pos)
        self.move_dir = [[-1,-1],[-1,1],[1,-1],[1,1]]
        self.value = 2
    def __str__(self):
        if self.color == games.COLORS[0]:
            return CheckersSymbols.king0.value
        else:
            return CheckersSymbols.king1.value   
   
   
class CheckersMove(games.Move):
    def __repr__(self):
        if self.captured is None:
            return "basic move: "+repr(self.start)+"->"+repr(self.end)
        else:
            return "jump move: "+repr(self.start)+"->"+repr(self.end)+", capturing "+repr(self.captured)
    def promote_to(self):
        return King(self.piece.board, self.piece.color, self.piece.pos) #create king
