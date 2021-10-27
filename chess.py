import enum
import games

class ChessSymbols(enum.Enum):
    pawn0 = u"♙"
    pawn1 = u"♟"
    bishop0 = u"♗"
    bishop1 = u"♝"
    knight0 = u"♘"
    knight1 = u"♞"
    rook0 = u"♖"
    rook1 = u"♜"
    queen0 = u"♕"
    queen1 = u"♛"
    king0 = u"♔"
    king1 = u"♚"


class Chess(games.Game):
    def add_to_board(self, piece, plyr_num, tile):
        piece.color = games.COLORS[plyr_num]
        piece.pos = tile
        tile.occ = piece
        self.players[plyr_num].pieces.append(piece)
    def set_up_board(self):
        #add pawns
        for i in range(0, 8):
            self.add_to_board(Pawn(self.board), 0, self.board.tiles[6][i])
            self.add_to_board(Pawn(self.board), 1, self.board.tiles[1][i])

        for i in range(0,2):
            if i == 0:
                row = 7
            else:
                row = 0
            #add rooks, knights bishops
            for j in range(0,2):
                self.add_to_board(Rook(self.board), i, self.board.tiles[row][0+(7*j)])
                self.add_to_board(Knight(self.board), i, self.board.tiles[row][1+(5*j)])
                self.add_to_board(Bishop(self.board), i, self.board.tiles[row][2+(3*j)])
            #add king, queen
            self.add_to_board(Queen(self.board), i, self.board.tiles[row][3])
            self.add_to_board(King(self.board), i, self.board.tiles[row][4])
    def gen_valid_moves(self,plyr):
        [moves, captures] = plyr.possible_moves()
        return moves + captures
    def check_win(self):
        p1 = self.players[0]
        p2 = self.players[1]
        if p1.score >= 100:
            return p1
        if p2.score >= 100:
            return p2
        return False


class Chesser(games.Piece):
    def valid_move(self, tile_av):
        if tile_av is not None: #in range
            tile = tile_av[1]
            if tile.occ is None or tile.occ.color!=self.color: #not occupied by own piece
                m = ChessMove(self, self.pos, tile)
                if tile.occ is not None:
                    m.captured = [tile.occ]
                return m      
        return []
    def check_move_in_dir(self, dir):
        row_dir = dir[0]
        col_dir = dir[1]
        adj_row = self.pos.row + row_dir
        adj_col = self.pos.col + col_dir
        tile_av = self.tile_available(adj_row, adj_col)

        return self.valid_move(tile_av)
    def find_moves(self, dir):
        mvs = []
        cps = []
        res = self.check_move_in_dir(dir)
        if res:
            if res.captured:
                cps += [res]
            else:
                mvs += [res]
        return [mvs, cps]
    def possible_moves(self):
        moves = []
        caps = []
        for dir in self.move_dir:
            [mvs, cps] = self.find_moves(dir)
            moves += mvs
            caps += cps
        return [moves, caps]


class Pawn(Chesser):
    def __init__(self, board, color=None, pos=None):
        super().__init__(board, color, pos)
        self.value = 1
        self.move_dir = []
    def __str__(self):
        if self.color == games.COLORS[0]:
            return ChessSymbols.pawn0.value
        else:
            return ChessSymbols.pawn1.value
    def set_move_dir(self):
        if self.color == games.COLORS[0]:
            row = -1
        else:
            row = 1
        self.move_dir = [[row, 0]]
        if self.is_first_turn():
            self.move_dir.append([row*2,0])
    def is_first_turn(self):
        if (self.color == games.COLORS[0] and self.pos.row == 6) or (self.color == games.COLORS[1] and self.pos.row == 1):
            return True
        return False
    def valid_move(self, tile_av):
        if tile_av is not None and tile_av[0]: #in range and tile is not occupied by any piece
            tile = tile_av[1]
            m=ChessMove(self,self.pos,tile)
            if (tile.row == self.board.size-1 and self.color == games.COLORS[1]) or (tile.row == 0 and self.color == games.COLORS[0]): #promotion
                m.promotion = True
            return m
        return []
    def valid_cap(self, col_dir):
        res = []
        row = self.pos.row+self.move_dir[0][0]
        tile_av = self.tile_available(row, self.pos.col+ col_dir)

        if tile_av is not None and not tile_av[0]:  #tile in range
            tile = tile_av[1]
            if tile.occ.color != self.color: #and occupied by opponent piece
                m = ChessMove(self, self.pos, tile, [tile.occ])
                if (tile.row == self.board.size-1 and self.move_dir == 1) or (tile.row == 0 and self.move_dir == -1): #promotion
                    m.promotion = True
                res += [m]
        return res
    def find_caps(self):
        return self.valid_cap(-1) + self.valid_cap(-1)           
    def possible_moves(self):
        self.set_move_dir()
        moves = []
        caps = []
        for dir in self.move_dir:
            [mvs, cps] = self.find_moves(dir)
            moves += mvs
            caps += cps
        caps += self.find_caps()
        return [moves, caps]

class Knight(Chesser):
    def __init__(self, board, color=None, pos=None):
        super().__init__(board, color, pos)
        self.value = 3
        self.move_dir = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]]
    def __str__(self):
        if self.color == games.COLORS[0]:
            return ChessSymbols.knight0.value
        else:
            return ChessSymbols.knight1.value
class King(Chesser):
    def __init__(self, board, color=None, pos=None):
        super().__init__(board, color, pos)
        self.value = 100
        self.move_dir = [[-1,-1],[-1, 0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
    def __str__(self):
        if self.color == games.COLORS[0]:
            return ChessSymbols.king0.value
        else:
            return ChessSymbols.king1.value     

class DynamicChesser(Chesser):
    def find_moves(self, dir):
        mvs = []
        cps = []
        i = 1
        while True:
            spc = [x*int(i) for x in dir]
            res = self.check_move_in_dir(spc)
            if res:
                if res.captured:
                    cps += [res]
                    break
                else:
                    mvs += [res]
                    i=i+1
            else:
                break
        return [mvs, cps]
class Bishop(DynamicChesser):
    def __init__(self, board, color=None, pos=None):
        super().__init__(board, color, pos)
        self.value = 3
        self.move_dir = [[-1,-1],[-1,1],[1,-1],[1,1]]
    def __str__(self):
        if self.color == games.COLORS[0]:
            return ChessSymbols.bishop0.value
        else:
            return ChessSymbols.bishop1.value
class Rook(DynamicChesser):
    def __init__(self, board, color=None, pos=None):
        super().__init__(board, color, pos)
        self.value = 5
        self.move_dir = [[-1,0],[0,-1],[0,1],[1,0]]
    def __str__(self):
        if self.color == games.COLORS[0]:
            return ChessSymbols.rook0.value
        else:
            return ChessSymbols.rook1.value        
class Queen(DynamicChesser):
    def __init__(self, board, color=None, pos=None):
        super().__init__(board, color, pos)
        self.value = 9
        self.move_dir = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
    def __str__(self):
        if self.color == games.COLORS[0]:
            return ChessSymbols.queen0.value
        else:
            return ChessSymbols.queen1.value
    def possible_moves(self):
        return super().possible_moves()

class ChessMove(games.Move):
    def __repr__(self):
        return "move: "+repr(self.start)+"->"+repr(self.end)
    def promote_to(self):
        return Queen(self.piece.board, self.piece.color, self.piece.pos) #create queen


#clean up the pawn class