import sys
import copy
import random
import enum
from utility import convert_checker_coord, convert_matrix_coord

COLORS = ["white", "black"]

class Symbols(enum.Enum):
    tile0 = "◻"
    tile1 = "◼"
'''
class GameHistory():
    def __init__(self, game):
        self.game = game
        self.undo_stack = []
        self.redo_stack = []
    def get_state(self):
        return GameState(self.game)  
    def undo(self, gs):
        if self.undo_stack: #can undo
            last_turn = self.undo_stack.pop()
            self.redo_stack.append(last_turn)
            last_turn.copy_state(self.game)              
    def redo(self, gs):
        if self.redo_stack: #can redo
            next_turn = self.redo_stack.pop()
            self.undo_stack.append(next_turn)
            next_turn.copy_state(self.game)
    def next(self, gs):
        self.undo_stack.append(gs)
        self.redo_stack = [] #clear extra game states
'''
class History():
    def __init__(self, game, states=[]):
        self.game = game
        self.states = states        
    def add_state(self):
        g = GameState(self.game)
        self.states.append(g)
    def undo(self):
        if self.game.turn == 1: #cannot undo
            pass
        else:
            last_turn = self.states[self.game.turn-2]
            last_turn.copy_state(self.game)              
    def redo(self):
        if len(self.states) == self.game.turn: #cannot redo
            pass
        else:
            next_turn = self.states[self.game.turn]
            next_turn.copy_state(self.game)
    def next(self):
        if len(self.states) > self.game.turn: #clear extra game states
            self.states = self.states[:self.game.turn]

class GameState():
    def __init__(self, game):
        self.game = copy.deepcopy(game)
        self.turn = copy.copy(game.turn)
        self.board = copy.deepcopy(game.board)
        self.players = copy.deepcopy(game.players)
        self.draw_counter = copy.copy(game.draw_counter)
    def copy_state(self, game):
        game.turn = copy.copy(self.turn)
        game.board = copy.deepcopy(self.board)
        game.players = copy.deepcopy(self.players)
        game.draw_counter = copy.copy(self.draw_counter)
    def check_win(self):
        return self.game.check_win()
    def gen_valid_moves(self,plyr):
        return self.game.gen_valid_moves(plyr)

class Game():
    def __init__(self, p1_type="human", p2_type="human", size="8", history=False):
        self.turn = 1
        self.board = Board(int(size))
        self.players = self.make_players([p1_type, p2_type])
        self.set_up_board() #set up board and pieces
        self.draw_counter = 0

        if history == "history" and (p1_type == "human" or p2_type == "human"):
            history = History(self)
        self.history = history
    def set_up_board(self):
        raise NotImplementedError
    def make_players(self, types):
        res= []
        for i in range(0, 2):
            if types[i]  == "simple":
                p = Simple(COLORS[i], self, [])
            elif types[i] == "random":
                p = Random(COLORS[i], self, [])
            elif types[i] == "human":
                p = Human(COLORS[i], self, [])
            else:
                d = int(types[i][7])
                p = Minimax(COLORS[i],self, d, [])
            res.append(p)
        return res
    def start(self):
        print(self.board)
        while True:
            plyr = self.players[(self.turn-1)%2] #figure out whose turn it is
            print("Turn: "+str(self.turn)+", "+plyr.color) #display turn num, turn color
            
            #display history options
            if self.history: #add state at the start of current turn
                self.history.add_state()
                inp = input("undo, redo, or next\n")
                if inp == "undo":
                    self.history.undo()
                    print(self.board)
                    continue
                elif inp == "redo":
                    self.history.redo()
                    print(self.board)
                    continue
                elif inp == "next": 
                    self.history.next()
                else:
                    sys.exit()
            self.next_turn(plyr)
    def check_win(self):
        raise NotImplementedError
    def next_turn(self, plyr):
        #check if current player has lost
        winner = self.check_win()
        if winner:
            print(winner.color + " has won")
            sys.exit()

        #generate all valid moves for the current player
        moves = self.gen_valid_moves(plyr)

        #check for draw
        if not moves or self.draw_counter >= 50: 
            print("draw")
            sys.exit()

        #make move
        mv = plyr.choose_move(moves)
        mv.do(plyr)
        if mv.captured:
            self.draw_counter = 0
        else:
            self.draw_counter += 1       
        print(self.board)
            
        #increment turn
        self.turn += 1    
    def gen_valid_moves(self,plyr):
        raise NotImplementedError               


class Board():
    def __init__(self, size):
        self.size = size
        self.tiles = []
        self.make_tiles()
    def __str__(self):
        for i in range(0,self.size):
            row = self.tiles[i]
            print(i+1, end=' ')
            print(*row)
        print(" ", end='')
        for j in range(0,self.size):
            c = ord('a') + j
            print(' '+ chr(c), end ='')
        return ''
    def in_range(self, row, col): #check if in tile is in range
        if row >= 0 and col >= 0 and row < self.size and col < self.size:
            return True
        else:
            return False
    def make_tiles(self):
        for i in range(0, self.size):
            row = []
            for j in range(0,self.size):
                t = Tile(i,j)
                row.append(t)
            self.tiles.append(row)        

class Tile():
    def __init__(self, row, col):
        self.occ = None
        self.row = row
        self.col = col

        if (row+col)%2 == 0:
            self.color = COLORS[1]
        else:
            self.color = COLORS[0]    
    def __str__(self):
        if self.occ is None:
            if self.color == COLORS[0]:
                return Symbols.tile0.value
            else:
                return Symbols.tile1.value
        else:
            return str(self.occ)
    def __repr__(self):
        return convert_matrix_coord((self.row, self.col))


class Piece():
    def __init__(self, board, color=None, pos=None):
        self.color = color
        self.board = board
        self.pos = pos #a tile
        self.move_dir = []
    def __str__(self):
        raise NotImplementedError
    def __repr__(self):
        return repr(self.pos)
    def __eq__(self, p):
        if self.color == p.color and type(self) == type(p):
            if self.pos and p.pos and self.pos.row == p.pos.row and self.pos.col == p.pos.col:
                return True
        return False
    def tile_available(self, row, col):
        if type(self.board) != Board:
            print(str(type(self))+" "+repr(self.pos))
            
        if self.board.in_range(row,col):
            tile = self.board.tiles[row][col]
            if tile.occ is None:
                return [True, tile]
            else:
                return [False, tile]
        return None
    def possible_moves(self):
        raise NotImplementedError

class Player():
    def __init__(self, color, game, pieces=None):
        self.color = color
        self.game = game
        self.pieces = pieces
        self.score = 0
    def choose_move(self, moves):
        raise NotImplementedError
    def choose_random(self, moves):
        return moves[random.randint(0, len(moves)-1)]
    def possible_moves(self):
        moves = []
        captures = []
        for piece in self.pieces:
            if piece.pos is not None:
                [mvs, caps] = piece.possible_moves()
                moves.extend(mvs)
                captures.extend(caps)
        return [moves, captures]

class Human(Player):
    def choose_move(self, moves):
        while True: #repeat until a move is returned
            #get piece
            inp = input("Select a piece to move\n")
            coord = convert_checker_coord(inp)
            piece = self.game.board.tiles[coord[0]][coord[1]].occ
            
            if piece is None:
                print("no piece at that location")
            elif piece.color != self.color:
                print("that is not your piece")
            else: 
                #get valid moves for piece
                mvs = []
                for mv in moves:
                    if mv.piece is piece:
                        mvs.append(mv)
                #show move options
                if not mvs:
                    print("that piece cannot move")
                else:
                    for i in range(0, len(mvs)):
                        print(str(i)+": "+str(mvs[i]))
                    inp = input("Select a move by entering the corresponding index\n")
                    return mvs[int(inp)]
class Random(Player):
    def choose_move(self, moves):
        '''
        A random computer player will randomly choose a play fromthe set of allowed moves.
        
        '''
        res = self.choose_random(moves)
        print(res)
        return res
class Simple(Player):
    def choose_move(self,moves):
        '''
        A slightly more sophisticated simple computer player will take the 
        available move that captures the greatest total value of pieces. 
        '''
        #look for highest move value
        mvs = []
        val = 0
        for mv in moves:
            cur = mv.value
            if cur > val:
                val = cur
                mvs = [mv]
            elif cur == val:
                mvs.append(mv)
        res = self.choose_random(mvs)
        print(res)
        return res#break ties randomly
class Minimax(Player):
    def __init__(self, color, game,depth, pieces=None):
        super().__init__(color, game, pieces)
        self.depth = depth
    def choose_move(self, moves):
        gs = GameState(self.game)
        [val, mv] = self.minimax_search(gs, self.depth, 1000, -1000)      
        for move in moves:
            if mv == move:
                print(move)
                return move
    def evaluate(self, gs):
        p1 = gs.players[0]
        p2 = gs.players[1]

        if p1.color == self.color: 
            return [p1.score-p2.score, None]
        else:
            return [p2.score-p1.score, None]
    def perform_move(self, gs, mv, index):
        #create game
        g = type(gs.game)()
        gs.copy_state(g)
        
        #get current player
        plyr = g.players[index]

        #make move
        move = copy.deepcopy(mv)
        move.do(plyr)
        if mv.captured:
            g.draw_counter = 0
        else:
            g.draw_counter += 1
            
        #increment turn
        g.turn += 1
        res = GameState(g)
        return res
    def minimax_search(self, gs, d, min, max):
        if d == 0 or gs.check_win():
            return self.evaluate(gs)
        #figure out whose turn it is
        index = (gs.turn-1)%2
        plyr = gs.players[index] 

        best_mvs = []
        v = 0

        if plyr.color == self.color: #if our turn
            v = float('-inf')
            mvs = gs.gen_valid_moves(plyr)
            for mv in mvs:
                new_gs = self.perform_move(gs, mv, index)
                [v_new, asc] = self.minimax_search(new_gs, d-1, v, max)
                if v_new > v:
                    v = v_new
                    best_mvs = [mv] 
                elif v_new == v:
                    best_mvs += [mv]
                
                if v > max:
                    return [max, mv]
        else: #if opponents's turn, min node
            v = float('inf')
            mvs = gs.gen_valid_moves(plyr)
            for mv in mvs:
                new_gs = self.perform_move(gs, mv, index)
                [v_new, asc] = self.minimax_search(new_gs, d-1, min, v)
                if v_new < v:
                    v=v_new
                    best_mvs = [mv]
                elif v_new==v:
                    best_mvs += [mv]
                if v < min:
                    return [min, mv]
        best_mv = self.choose_random(best_mvs)
        return [v, best_mv]

class Move():
    def __init__(self, piece, start, end, captured=None, promotion=False):
        self.piece = piece
        self.start = start 
        self.end = end

        self.captured = captured
        self.promotion = promotion

        self.value = 0
        if self.captured:
            for piece in self.captured:
                self.value += piece.value
    def __repr__(self):
        raise NotImplementedError
    def __eq__(self, mv):
        if type(self.piece) == type(mv.piece) and self.start.row == mv.start.row and self.start.col == mv.start.col and self.end.row == mv.end.row and self.end.col == mv.end.col and self.promotion == mv.promotion:
            if (self.captured is None and mv.captured is None) or len(self.captured) == len(mv.captured):
                return True
        return False
    def do(self, plyr):
        #capture pieces
        if self.captured:
            for cap in self.captured:
                cap.pos.occ = None #clear tile
                cap.pos = None #remove piece from board
                plyr.score += cap.value #add to score

        #move piece
        self.start.occ = None #clear starting tile
        self.piece.pos = self.end #move piece
        self.end.occ = self.piece #update ending tile

        #promote piece
        if self.promotion:
            p = self.promote_to()

            self.piece.pos.occ = p #place promoted piece on tile
            self.piece.pos = None #remove old piece from board
            
            for pc in plyr.pieces:
                if pc == self.piece:
                    plyr.pieces.remove(pc)  #remove old piece from player's pieces
            plyr.pieces.append(p) #add promoted piece to player's pieces
    def promote_to(self):
        raise NotImplementedError
        
        


