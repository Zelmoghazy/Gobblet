import copy
import random
import sys
import pygame
import numpy as np

WIDTH  = 600
HEIGHT = 600
ROWS = 4
COLS = 4
SQUARE_SIZE = WIDTH // COLS
LINE_WIDTH   = 15
CIRCLE_WIDTH = 15
CIRCLE_RADIUS = SQUARE_SIZE // 2 - CIRCLE_WIDTH 
CROSS_WIDTH = 25

BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gobblet")
screen.fill(BG_COLOR)

counter = 0

hashmap = {
    'wwww': 100000, 
    'xwww': 3000,
    'wxww': 3000,
    'wwxw': 3000,
    'wwwx': 3000,
    'xxww': 2000, 
    'xwxw': 2000,
    'xwwx': 2000,
    'wxxw': 2000,
    'wxwx': 2000,
    'wwxx': 2000,
    'wwwb': 2000,
    'wwbw': 2000,
    'wbww': 2000,
    'bwww': 2000,
    'xxxw': 1000,
    'xxwx': 1000,
    'xwxx': 1000,
    'xwwb': 1000,
    'xwbw': 1000,
    'xbww': 1000,
    'wxxx': 1000,
    'wxwb': 1000,
    'wxbw': 1000,
    'wwxb': 1000,
    'wwbx': 1000,
    'wbxw': 1000
}

class Move:
    def __init__(self, from_row, from_col, to_row, to_col,score,flag) -> None:
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.flag = flag
        self.score = score

class Gobblet_Stack:
    def __init__(self, Gobblet_Stack) -> None:
        self.stack = list()
        self.stack = Gobblet_Stack
    def __str__(self) -> str:
        str=""
        for i in range(len(self.stack)):
            str += str(self.stack[i]) + " "
        return str
    def add_piece(self, piece):
        self.stack.append(piece)
    def remove_piece(self):
        self.stack.pop()
    def top_piece(self):
        return self.stack[-1]
    def is_empty(self):
        return len(self.stack) == 0
    def is_full(self):
        return len(self.stack) == 4
    def get_top(self):
        return self.stack[-1]
    
class Gobblet:
    def __init__(self, color, size):
        self.color = color
        self.size = size
    def __str__(self) -> str:
        return self.color + " " + self.size
    def __eq__(self, other):
        return self.color == other.color and self.size == other.size

class Square:
    # add gobblet stack in each square
    def __init__(self, Gobblet_Stack) -> None:
        self.stack = Gobblet_Stack
    def __str__(self) -> str:
        return str(self.stack)
    def add_piece(self, piece):
        self.stack.add_piece(piece)
    def remove_piece(self):
        self.stack.remove_piece()
    def top_piece(self):    
        return self.stack.top_piece()
    def is_empty(self):
        return self.stack.is_empty()
    def is_full(self):
        return self.stack.is_full()
    def get_top(self):
        return self.stack.get_top()
    def get_stack(self):
        return self.stack

gw11 = Gobblet("w", 1)
gw12 = Gobblet("w", 1)
gw13 = Gobblet("w", 1)

gw21 = Gobblet("w", 2)
gw22 = Gobblet("w", 2)
gw23 = Gobblet("w", 2)

gw31 = Gobblet("w", 3)
gw32 = Gobblet("w", 3)
gw33 = Gobblet("w", 3)

gw41 = Gobblet("w", 4)
gw42 = Gobblet("w", 4)
gw43 = Gobblet("w", 4)

gb11 = Gobblet("b", 1)
gb12 = Gobblet("b", 1)
gb13 = Gobblet("b", 1)

gb21 = Gobblet("b", 2)
gb22 = Gobblet("b", 2)
gb23 = Gobblet("b", 2)

gb31 = Gobblet("b", 3)
gb32 = Gobblet("b", 3)
gb33 = Gobblet("b", 3)

gb41 = Gobblet("b", 4)  
gb42 = Gobblet("b", 4)
gb43 = Gobblet("b", 4)

class AI:
    def __init__(self, level=1, player=2) -> None:
        self.level = level
        self.player = player

    def random_move(self, board):   
        empty_squares = board.get_empty_squares()
        index = random.randrange(0, len(empty_squares))
        return empty_squares[index]

    def minimax(self, board, maximizing,depth=3):
        global counter
        counter += 1
        # return score
        case = board.final_state()

        if case == 1:
            return 1, None
        elif case == 2:
            return -1, None  
        elif case == 3:
            return 0, None

        if depth == 0:
            return 0, None

        if maximizing:
            max_eval  = -100
            best_move = None
            # get all available moves
            empty_squares = board.get_empty_squares()
            # move ordering based on heuristics
            empty_square.sort()

            # for each move in available moves
            for (row, col) in empty_squares:
                # temp_board = copy.deepcopy(board)
                board.mark_square(row, col,1)
                eval = self.minimax(board, False,depth-1)[0]
                board.unmark_square(row, col)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
            # for every player piece from array 
            # find all availiable squares and loop on them and mark the square with the piece
            # swap_square(playerpiece(row,col),square(row,col))
            return max_eval, best_move
        #---------------------------------------------------------------------
        else:
            min_eval = 100
            best_move = None
            empty_squares = board.get_empty_squares()

            for (row, col) in empty_squares:
                # temp_board = copy.deepcopy(board)
                board.mark_square(row, col, self.player)
                eval = self.minimax(board, True,depth-1)[0]
                board.unmark_square(row, col)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)           
            return min_eval, best_move

    def minimax_alpha_beta(self, board, maximizing, alpha, beta, depth=7):
        global counter
        counter += 1
        case = board.final_state()

        if case == 1:
            return 1, None
        elif case == 2:
            return -1, None  
        elif case == 3:
            return 0, None

        if depth == 0 :
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_squares = board.get_empty_squares()

            for (row, col) in empty_squares:
                # temp_board = copy.deepcopy(board)
                board.mark_square(row, col,1)
                eval = self.minimax_alpha_beta(board, False, alpha, beta, depth-1)[0]
                board.unmark_square(row, col)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = 100
            best_move = None
            empty_squares = board.get_empty_squares()

            for (row, col) in empty_squares:
                # temp_board = copy.deepcopy(board)
                board.mark_square(row, col, self.player)
                eval = self.minimax_alpha_beta(board, True, alpha, beta, depth-1)[0]
                board.unmark_square(row, col)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
    def minimax_alpha_beta_iterative(self, board, maximizing, alpha, beta, depth=7):
        # set a timer for the function and explore the tree as much as possible start with depth 2 and increase it by 1 every time until the timer is up
        # return the best move found
        pass
        

    def evaluate(self, board):
        if self.level == 0:
            move = self.random_move(board)
        else:
            # eval,move = self.minimax(board,False,5)
            eval,move = self.minimax_alpha_beta(board,False,-100,100,9)
            print(counter)
        return move