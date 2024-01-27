import pygame
import math
from collections import defaultdict
import copy
import random
import time
import sys
import math
import numpy as np
from timeout_decorator import timeout

'''
Pattern based heuristic calculation
'''
Heuristic = {
    'wwww': 10000000,
    'xwww': 30000,
    'wxww': 30000,
    'wwxw': 30000,
    'wwwx': 30000,
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
    'wbxw': 1000,
    'wbwx': 1000,
    'bxww': 1000,
    'bwxw': 1000,
    'bwwx': 1000,
    'xxxx': 0,
    'xxwb': 0,
    'xxbw': 0,
    'xwxb': 0,
    'xwbx': 0,
    'xbxw': 0,
    'xbwx': 0,
    'wxxb': 0,
    'wxbx': 0,
    'wwbb': 0,
    'wbxx': 0,
    'wbwb': 0,
    'wbbw': 0,
    'bxxw': 0,
    'bxxw': 0,
    'bxwx': 0,
    'bwxx': 0,
    'bwwb': 0,
    'bwbw': 0,
    'bbww': 0,
    'xxxb': -1000,
    'xxbx': -1000,
    'xwbb': -1000,
    'xbxx': -1000,
    'xbwb': -1000,
    'xbbw': -1000,
    'wxbb': -1000,
    'wbxb': -1000,
    'wbbx': -1000,
    'bxxx': -1000,
    'bxwb': -1000,
    'bxbw': -1000,
    'bwxb': -1000,
    'bwbx': -1000,
    'bbxw': -1000,
    'bbwx': -1000,
    'xxbb': -2000,
    'xbxb': -2000,
    'xbbx': -2000,
    'wbbb': -2000,
    'bxxb': -2000,
    'bxbx': -2000,
    'bwbb': -2000,
    'bbxx': -2000,
    'bbwb': -2000,
    'bbbw': -2000,
    'xbbb': -30000,
    'bxbb': -30000,
    'bbxb': -30000,
    'bbbx': -30000,
    'bbbb': -10000000
}


pygame.init()

def make_GUI_Move(move:Move):
    nearest_centerx = LEFT_MARGIN + (move.to_col * CELL_SIZE) + CELL_SIZE//2
    nearest_centery = (move.to_row * CELL_SIZE) + CELL_SIZE//2

    if move.flag == 1:
        active_circle_old_x = (LEFT_MARGIN+WIDTH+CELL_SIZE//2) if move.from_col else (CELL_SIZE*0.5)
        active_circle_old_y =  ((move.from_row * CELL_SIZE) + 3 * CELL_SIZE//2) if move.from_col else ((move.from_row * CELL_SIZE) + CELL_SIZE//2)
        for circle in circles:
            if circle.rect.centerx == active_circle_old_x and circle.rect.centery == active_circle_old_y and circle.rect.width == 20*move.size:
                circle_map[(nearest_centerx,nearest_centery)].append(circles[circle.num])
                circle.rect.centerx = nearest_centerx
                circle.rect.centery = nearest_centery
    elif move.flag == 0:
            active_circle_old_x = LEFT_MARGIN + (move.from_col * CELL_SIZE) + CELL_SIZE//2
            active_circle_old_y = (move.from_row * CELL_SIZE) + CELL_SIZE//2
            #Update Board
            id = circle_map[(active_circle_old_x,active_circle_old_y)][-1].num
            circle_map[(active_circle_old_x,active_circle_old_y)].pop()    
            circle_map[(nearest_centerx,nearest_centery)].append(circles[id])
            circles[id].rect.centerx = nearest_centerx
            circles[id].rect.centery = nearest_centery


'''
Each gobblet on board is completely represented by its color and size
'''
class Gobblet:
    def __init__(self, color, size):
        self.color = color
        self.size = size
    def __str__(self) -> str:
        return self.color + " " + self.size

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




#Class for Move
'''
Encapsulate all move information including the potential score if this move was applied
Can be used to communicate with the GUI representation keeping each state seperate and 
only communicate through moves, if both moves are consistent the states should be in sync
'''
class Move:
    def __init__(self, from_row, from_col, to_row, to_col,score,flag,size=0):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.score = score
        self.flag = flag    # Either 0 for board or 1 for side stack (initialized with piece move and rewritten)
        self.size = score
    def __str__(self) -> str:
        return str(self.from_row) + " " + str(self.from_col) + " " + str(self.to_row) + " " + str(self.to_col) + " " + str(self.score) + " " + str(self.flag)


'''
Main class represent the entire board, consists of :
- side_stack : initialized with all the pieces
- board : represents the actual playing board
'''  
class Board:
    def __init__(self) -> None:
        self.board      = np.zeros((ROWS, COLS), dtype=Gobblet_Stack)
        self.side_stack = np.zeros((3, 2),       dtype=Gobblet_Stack)

        for row in range(ROWS):
            for col in range(COLS):
                self.board[row][col] = Gobblet_Stack([Gobblet("x", 0)])

        # side_stack[][0] -> black
        # side_stack[][1] -> white
        self.side_stack[0][1] = Gobblet_Stack([Gobblet("x", 0),gw11, gw21, gw31, gw41])
        self.side_stack[1][1] = Gobblet_Stack([Gobblet("x", 0),gw12, gw22, gw32, gw42])
        self.side_stack[2][1] = Gobblet_Stack([Gobblet("x", 0),gw13, gw23, gw33, gw43])
        
        self.side_stack[0][0] = Gobblet_Stack([Gobblet("x", 0),gb11, gb21, gb31, gb41])
        self.side_stack[1][0] = Gobblet_Stack([Gobblet("x", 0),gb12, gb22, gb32, gb42])
        self.side_stack[2][0] = Gobblet_Stack([Gobblet("x", 0),gb13, gb23, gb33, gb43])


    # print(board)
    def __str__(self) -> str:
        string = ""
        for row in range(ROWS):
            for col in range(COLS):
                size = str(self.board[row][col].get_top_size())
                string += '[' + self.board[row][col].get_top_color() + size + ']' + "\t"
            string += "\n"
        return string

    # Apply a move to the board
    def Move(self,move):
        # Move inside the board
        if(move.flag == 0):
            self.board[move.to_row][move.to_col].add_piece(self.board[move.from_row][move.from_col].get_top())
            self.board[move.from_row][move.from_col].remove_piece()
        # Move from the side stack
        # from_col here represents the player
        if (move.flag == 1):
            self.board[move.to_row][move.to_col].add_piece(self.side_stack[move.from_row][move.from_col].get_top())
            self.side_stack[move.from_row][move.from_col].remove_piece()

    # Get the maximum piece int the sidestack
    # returns the size and the row number
    def max_side_stack(self,player):
        max = 0 # Apply only maximum piece in side stack
        row = 0 # from which sidestack row
        for i in range(3): # only three sidestack rows
            if(self.side_stack[i][player].get_top_size() > max):
                max = self.side_stack[i][player].get_top_size()
                row = i
        return max,row

    # Get all current player pieces on board
    # returns the coordinates and size of each piece
    def player_pieces_on_board(self,player):
        coordinates = []
        for row in range(ROWS):
            for col in range(COLS):
                if(self.board[row][col].get_top_color() == player_color[player]):
                    coordinates.append((row, col,self.board[row][col].get_top_size()))
        return coordinates

    # Unmove previous move used when constructing the same level in tree
    def Unmove(self,move):
        # Move inside the board
        if(move.flag == 0):
            self.board[move.from_row][move.from_col].add_piece(self.board[move.to_row][move.to_col].get_top())
            self.board[move.to_row][move.to_col].remove_piece()
        # Move from the side stack
        if (move.flag == 1):
            self.side_stack[move.from_row][move.from_col].add_piece(self.board[move.to_row][move.to_col].get_top())
            self.board[move.to_row][move.to_col].remove_piece()


    # Iterate over each row, column and diagonal to get the score of the board if a move is applied
    # used in move ordering and as an evaluation function at maximum depth
    def get_score(self,move,player):
        size = move.score # size of next move piece
        score = 0

        string = ''

        # check rows
        # Remember to check for empty squares
        for row in range(ROWS):
            string = ""
            for col in range(COLS):
                if(move.to_row == row and move.to_col == col):
                    if(player == 1):
                        string += ('w')
                        score += size_score[size] # maximizer
                    else:
                        string += ('b')
                        score -= size_score[size] # minimizer
                else:
                    top = None
                    # flag = 0 -> move inside board
                    # Simulate the move on the board
                    if(move.flag == 0 and move.from_row == row and move.from_col == col):
                        top = self.board[row][col].get_top() # save top piece
                        self.board[row][col].remove_piece()  # pop top piece
                    # w : white piece
                    # b : black piece
                    # x : empty square    
                    string += (self.board[row][col].get_top_color())
                    if(self.board[row][col].get_top_color() == player_color[player]):
                        score += size_score[self.board[row][col].get_top_size()]
                    else:
                        score -= size_score[self.board[row][col].get_top_size()]
                    # return the piece to the board
                    if(top != None):
                        self.board[row][col].add_piece(top)
            score += Heuristic[string]

        # check columns
        for col in range(COLS):
            string = ""
            for row in range(ROWS):
                if(move.to_row == row and move.to_col == col):
                    if(player == 1):
                        string += ('w')
                        score += size_score[size]
                    else:
                        string += ('b')
                        score -= size_score[size]
                else:
                    top = None
                    # flag = 0 -> move inside board
                    if(move.flag == 0 and move.from_row == row and move.from_col == col):
                        top = self.board[row][col].get_top()
                        self.board[row][col].remove_piece()
                    string += (self.board[row][col].get_top_color())
                    if(self.board[row][col].get_top_color() == player):
                        score += size_score[self.board[row][col].get_top_size()]
                    else:
                        score -= size_score[self.board[row][col].get_top_size()]
                        
                    if(top != None):
                        self.board[row][col].add_piece(top)
            score += Heuristic[string]

        string = ""

        # check diagonals
        for i in range(ROWS):
            if(move.to_row == i and move.to_col == i):
                if(player == 1):
                    string += ('w')
                    score += size_score[size]
                else:
                    string += ('b')
                    score -= size_score[size]
            else:
                top = None
                # flag = 0 -> move inside board
                if(move.flag == 0 and move.from_row == i and move.from_col == i):
                    top = self.board[i][i].get_top()
                    self.board[i][i].remove_piece()
                string += (self.board[i][i].get_top_color())
                if(self.board[i][i].get_top_color() == player_color[player]):
                    score += size_score[self.board[i][i].get_top_size()]
                else:
                    score -= size_score[self.board[i][i].get_top_size()]
                if(top != None):
                    self.board[i][i].add_piece(top)
        score += Heuristic[string]

        string = ""

        for i in range(ROWS):
            if(move.to_row == i and move.to_col == ROWS-i-1):
                if(player == 1):
                    string += ('w')
                    score += size_score[size]
                else:
                    string += ('b')
                    score -= size_score[size]
            else:
                top = None
                # flag = 0 -> move inside board
                if(move.flag == 0 and move.from_row == i and move.from_col == ROWS-i-1):
                    top = self.board[i][ROWS-i-1].get_top()
                    self.board[i][ROWS-i-1].remove_piece()
                string += (self.board[i][ROWS-i-1].get_top_color())
                if(self.board[i][ROWS-i-1].get_top_color() == player_color[player]):
                    score += size_score[self.board[i][ROWS-i-1].get_top_size()]
                else:
                    score -= size_score[self.board[i][ROWS-i-1].get_top_size()]
                if(top != None):
                    self.board[i][ROWS-i-1].add_piece(top)
        score += Heuristic[string]

        return score
    

    '''
From Gobblet rules : If you put a new gobblet in play, you must place it on an empty square.
However, there is one exception to this rule:
- if your opponent already has 3 gobblets in a row on the board, you may gobble up 1 of the 3 pieces 
    in the line with a gobblet taken directly from one  of your external stacks.

This function is used to do this check in order to decide whether you can play from side stack 
to a non-empty square directly or not
'''
def get_three_in_a_row(self,player,row,col):
    # check rows
    # Remember to check for empty squares
    if(self.board[row][1].get_top_color() == self.board[row][2].get_top_color() and self.board[row][2].get_top_color() != player_color[player]):
        if(self.board[row][0].get_top_color() == self.board[row][1].get_top_color()):
            return True
        elif(self.board[row][3].get_top_color() == self.board[row][2].get_top_color()):
            return True


    if(self.board[1][col].get_top_color() == self.board[2][col].get_top_color() and self.board[2][col].get_top_color() != player_color[player]):
        if(self.board[0][col].get_top_color() == self.board[1][col].get_top_color()):
            return True
        elif(self.board[3][col].get_top_color() == self.board[2][col].get_top_color()):
            return True

    if (row == col) :
        if(self.board[1][1].get_top_color() == self.board[2][2].get_top_color() and self.board[2][2].get_top_color() != player_color[player]):
            if(self.board[0][0].get_top_color() == self.board[1][1].get_top_color()):
                return True
            elif(self.board[2][2].get_top_color() == self.board[3][3].get_top_color()):
                return True

    if(row == ROWS-col):
        if(self.board[1][2].get_top_color() == self.board[2][1].get_top_color() and self.board[2][1].get_top_color() != player_color[player]):
            if(self.board[0][3].get_top_color() == self.board[1][2].get_top_color()):
                return True
        if(self.board[1][2].get_top_color() == self.board[2][1].get_top_color()):
            if(self.board[2][1] == self.board[3][0].get_top_color()):
                return True



# Returns all possible moves of player from a certain state
# 1 - From the sidestack to an empty square on the board
# 2 - From board to either empty square on board or a smaller piece
# 3 - From sidestack to board, only if 3 of opponents pieces are in row
def getAvailableMoves(self,player):
    moves = []

    # get maximum piece in side stack and its size
    max,side_row = self.max_side_stack(player)

    # get all player pieces on board
    player_pieces_on_board = self.player_pieces_on_board(player) 

    for row in range(ROWS):      
        for col in range(COLS):
            if self.board[row][col].is_empty():
                # Make move from side stack to an empty square 
                move = Move(side_row,player,row,col,max,1)
                move.score = self.get_score(move,player)
                moves.append(move)
                # Make move from board to an empty square
                for piece in player_pieces_on_board:
                    move = Move(piece[0],piece[1],row,col,piece[2],0)
                    move.score = self.get_score(move,player)
                    moves.append(move)
            # Make move to a smaller piece
            # Optimization: check only for opponent pieces on board
            elif self.board[row][col].get_top_color() != player_color[player]:
                # only if its row or column or diagonal contains three pieces from opponent
                # its legal to gobble from external stack to board
                # otherwise its only allowed to be place on an empty square
                if(self.board[row][col].get_top_size() < max and self.get_three_in_a_row(player,row,col)):
                    move = Move(side_row,player,row,col,max,1)
                    move.score = self.get_score(move,player)
                    moves.append(move)
                for piece in player_pieces_on_board:
                    if(self.board[row][col].get_top_size() < piece[2]):
                        move = Move(piece[0],piece[1],row,col,piece[2],0)
                        move.score = self.get_score(move,player)
                        moves.append(move)
    return moves

'''
Each square on board is represented as a stack
each stack is initialized with a dummy gobblet of color 'x' 
and size = 0, this is required for easy score calculation later
'''
class Gobblet_Stack:
    def __init__(self, Gobblet_Stack) -> None:
        self.stack = list(Gobblet_Stack)
    def __str__(self) -> str:
        str=""
        for i in range(len(self.stack)):
            str += str(self.stack[i]) + " "
        return str
    def add_piece(self, piece):
        self.stack.append(piece)
    def remove_piece(self):
        self.stack.pop()
    def is_empty(self):
        return self.stack[-1].color == "x"
    def is_full(self):
        return len(self.stack) == 5
    def get_top(self):
        return self.stack[-1]
    def get_stack_size(self):
        return len(self.stack)
    def get_top_size(self):
        return self.stack[-1].size
    def get_top_color(self):
        return self.stack[-1].color
    

class AI:
    def __init__(self, level, player) -> None:
        self.level  =  level
        self.player =  player

    def random_element_first_quarter(my_array):
        first_quarter_start = 0
        first_quarter_end = len(my_array) // 4
        return random.choice(my_array[first_quarter_start:first_quarter_end])

    def random_move(self, board, Maximizing=True):
        available_moves = board.getAvailableMoves(self.player)
        available_moves.sort(key=lambda x: x.score, reverse=self.player)
        if len(available_moves) > 10 :
            return available_moves[random.randint(0, 5)]
        else :
            return available_moves[0]

    def minimax(self, board, maximizing,depth=3):
        if maximizing:
            max_eval  = -math.inf
            best_move = None
            # get all available moves
            available_moves = board.getAvailableMoves(self.player)
            # move ordering based on heuristics
            available_moves.sort(key=lambda x: x.score, reverse=True)

            if depth == 1:
                return available_moves[0]
            # for each move in available moves
            for move in available_moves:
                if(move.score > 9000000):
                    best_move = move
                    break
                board.Move(move)
                evaluated_move = self.minimax(board,False,depth-1)
                board.Unmove(move)
                if evaluated_move.score > max_eval:
                    max_eval = evaluated_move.score
                    best_move = move
            return best_move
        #---------------------------------------------------------------------
        else:
            min_eval = math.inf
            best_move = None

            available_moves = board.getAvailableMoves((self.player + 1) % 2)
            available_moves.sort(key=lambda x: x.score)
            if depth == 1:
                return available_moves[0]
            for move in available_moves:
                if(move.score < -9000000):
                    best_move = move
                    break

                # temp_board = copy.deepcopy(board)
                board.Move(move)
                evaluated_move = self.minimax(board, True,depth-1)
                board.Unmove(move)
                if evaluated_move.score < min_eval:
                    min_eval = evaluated_move.score
                    best_move = move           
            return best_move
    
    def minimax_alpha_beta(self, board, maximizing, alpha, beta, depth=7):
        if maximizing:
            max_eval = -math.inf
            available_moves = board.getAvailableMoves(self.player)
            available_moves.sort(key=lambda x: x.score,reverse=True)
            best_move = available_moves[0]

            # print(board)

            if depth == 1:
                return available_moves[0]

            for move in available_moves:
                if(move.score > 9000000):
                    best_move = move
                    break
                # temp_board = copy.deepcopy(board)
                board.Move(move)
                evaluated_move = self.minimax_alpha_beta(board, False, alpha, beta, depth-1)
                board.Unmove(move)
                if evaluated_move.score > max_eval:
                    max_eval = evaluated_move.score
                    best_move = move
                alpha = max(alpha, evaluated_move.score)
                if beta <= alpha:
                    break
            return best_move
        else:
            min_eval = math.inf

            available_moves = board.getAvailableMoves((self.player + 1) % 2)
            available_moves.sort(key=lambda x: x.score)
            best_move = available_moves[0]

            # print(board)

            if depth == 1:
                return available_moves[0]

            for move in available_moves:
                # temp_board = copy.deepcopy(board)
                if(move.score < -9000000):
                    best_move = move
                    break
                board.Move(move)
                evaluated_move = self.minimax_alpha_beta(board, True, alpha, beta, depth-1)
                board.Unmove(move)
                if evaluated_move.score < min_eval:
                    min_eval = evaluated_move.score
                    best_move = move
                beta = min(beta, evaluated_move.score)
                if beta <= alpha:
                    break
            return best_move

    # set a timer for the function and explore the tree as much as possible
    # start with depth 2 and increase it by 1 every time until the timer is up
    # use transposition table to cache already seen scores
    # return the best move found
    @timeout(60)  # Set the timeout to 60 seconds.
    def minimax_alpha_beta_iterative(self, board, time_limit, depth=0):
        while True:
            try:
                move = self.minimax_alpha_beta(board, True, -math.inf, math.inf, depth + 1)
            except TimeoutError:
                print("Function timed out")
                break
        return move

    def evaluate(self, board, maximizer = True):
        if self.level == 0:
            move = self.random_move(board)
        elif(self.level == 1):
            # move = self.minimax(board,True,3)
            move = self.minimax_alpha_beta(board,maximizer,-math.inf,math.inf,2)
        else :
            move = self.minimax_alpha_beta(board,maximizer,-math.inf,math.inf,3)
        return move

class Logic:
    def __init__(self,level,player, level_2 = 0) -> None:
        self.board = Board()
        self.player = player
        self.AI = AI(level,player)
        self.AI_2 = AI(level_2, (player+1)%2)
        self.game_mode = 'AI'
        self.running = True

    def next_turn(self):
        self.player = ((self.player + 1) % 2)

    def make_move(self,move):
        self.board.Move(move)
        self.next_turn()    


#Game Options

h_v_h = True
h_v_ai = False
ai_v_ai = False
# Colors
black  = (0, 0, 0)
white  = (255, 255, 255)

# Positions
WIDTH, HEIGHT = 800, 800
LEFT_MARGIN = 200
RIGHT_MARGIN = 200
CONTROL_PANEL = 300

AI_PLAYER = 1
AI_PLAYER_2 = 0
AI_DIFFICULTY = 1
AI_DIFFICULTY_2 = 1

# Grid
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
LINE_WIDTH = 10

#Create Screen
screen = pygame.display.set_mode((LEFT_MARGIN+WIDTH+RIGHT_MARGIN+CONTROL_PANEL,HEIGHT))
pygame.display.set_caption("Gobblet")
icon = pygame.image.load("Images\\Icon.png")
pygame.display.set_icon(icon)

#Add Background Image
Menu_BG = pygame.image.load("Images\\Menu_BG.png")
Menu_BG = pygame.transform.scale(Menu_BG, (WIDTH + LEFT_MARGIN*2 + CONTROL_PANEL, HEIGHT))
Options_BG = pygame.image.load("Images\\options.png")
Options_BG = pygame.transform.scale(Options_BG, (WIDTH + LEFT_MARGIN*2 + CONTROL_PANEL, HEIGHT))
Background_Img = pygame.image.load("Images\\Board.png")
Background_Img = pygame.transform.scale(Background_Img, (WIDTH + LEFT_MARGIN*2 + CONTROL_PANEL, HEIGHT))
checked = pygame.image.load("Images\\mark.png")
checked = pygame.transform.scale(checked, (40, 40))

# Center to snap pieces
centers = []
side_centers = []
# Pieces
circles = []
circle_map = defaultdict(list)

#Moves
Moves =[]

active_circle = None
active_circle_old_x = None
active_circle_old_y = None
active_player='black'

# Text
font = pygame.font.Font(None, 40)
text_box = font.render("Text Box", True, 'white')   
text = font.render("Illegal Move !!!!", True, 'red') 
white_turn = font.render("White Player Turn", True, 'red') 
black_turn = font.render("Black Player Turn", True, 'red')
white_win = font.render("White Wins!", True, 'green')
black_win = font.render("Black Wins!", True, 'green')
w_turn = font.render("White turn", True, 'white')
b_turn = font.render("black turn", True, 'white')


 
#Cirlce Class============================================================
class Circle:
    def __init__(self, color, center, radius,num):
        self.num = num    #id
        self.color = color
        self.rect = pygame.Rect(center[0] - radius, center[1] - radius, 2 * radius, 2 * radius)
        self.center = center
        self.radius = radius
        self.num = num

    def draw(self, screen):
        pygame.draw.circle(screen,self.color,self.rect.center,self.rect.width)

    def __eq__(self, other):
        if isinstance(other, Circle):
            return self.num == other.num
        return False

 #Class for Game Initialization========================================== 
class Game:
    def __init__(self) -> None: # Constructor
        self.guide_lines()
        self.winner = None

    def guide_lines(self):
        pos = 0
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                center_x = i * CELL_SIZE + LEFT_MARGIN + CELL_SIZE // 2
                center_y = j * CELL_SIZE + CELL_SIZE // 2
                centers.append((center_x,center_y,pos))
                pos += 1
        num = 0

        for i in range(GRID_SIZE-1):
            for j in range(GRID_SIZE):
                white_circle = Circle("white", (GRID_SIZE * CELL_SIZE + LEFT_MARGIN + CELL_SIZE // 2, i * CELL_SIZE + 1.5*CELL_SIZE), (j + 1) * 10,num)
                circles.append(white_circle)
                side_centers.append(white_circle.center)
                num += 1
                black_circle = Circle("black", (RIGHT_MARGIN // 2, i * CELL_SIZE + 0.5*CELL_SIZE), (j + 1) * 10,num)
                circles.append(black_circle)
                side_centers.append(black_circle.center)
                num += 1
        circles.sort(key=lambda circle: circle.rect.width)
        for idx, circle in enumerate(circles):
            circle.num = idx
            idx+=1
        # Winning combinations
        self.winning_combinations = []
        self.rule = []
        for i in range(GRID_SIZE):
            # Horizontal
            self.winning_combinations.append([(i * CELL_SIZE + LEFT_MARGIN + CELL_SIZE // 2, j * CELL_SIZE + CELL_SIZE // 2) for j in range(GRID_SIZE)])
            # Vertical
            self.winning_combinations.append([(j * CELL_SIZE + LEFT_MARGIN + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2) for j in range(GRID_SIZE)])
        # Diagonal from top-left to bottom-right
        self.winning_combinations.append([(j * CELL_SIZE + LEFT_MARGIN + CELL_SIZE // 2, j * CELL_SIZE + CELL_SIZE // 2) for j in range(GRID_SIZE)])
        # Diagonal from top-right to bottom-left
        self.winning_combinations.append([(j * CELL_SIZE + LEFT_MARGIN + CELL_SIZE // 2, (GRID_SIZE - 1 - j) * CELL_SIZE + CELL_SIZE // 2) for j in range(GRID_SIZE)])


class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

def get_font_title(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("Fonts/ARCADE.TTF", size)

def H_vs_H():
    screen.fill("black")
    game = Game() 
    illegal = False
    game_over = False
    rule = False # Gobble up one of the 3 pieces in a row to prevent the opponent to win 
    while True:
        global active_circle
        global active_player
        
        #Change Background Image
        screen.blit(Background_Img, (0, 0))

        #Add Text Box Title
        screen.blit(text_box, (WIDTH + RIGHT_MARGIN*2 + 10, HEIGHT - 270))

        MENU_MOUSE_POS = pygame.mouse.get_pos()
        RESTART_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1350, 150), 
                        text_input="RESTART", font=get_font_title(70), base_color="yellow", hovering_color="green")
        MENU_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1350, 250), 
                        text_input="MENU", font=get_font_title(70), base_color="yellow", hovering_color="green")

        #Display Player Turn
        if active_player == 'white':
            screen.blit(w_turn, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 400))
        if active_player == 'black':
            screen.blit(b_turn, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 400))

        # Draw all circles
        for circle in circles:
            circle.draw(screen)

       # Illegal Play
        if illegal:
            screen.blit(text, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
            if(active_player == 'white'):
                screen.blit(white_turn,(WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 150))
            else:
                screen.blit(black_turn,(WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 150))

        #Check for winner
        if not illegal:
            for combo in game.winning_combinations:
                color_count = {'white': 0, 'black': 0}
                consecutive = []
                for center in combo:
                    if circle_map[center]:
                        color_count[circle_map[center][-1].color] += 1
                        consecutive.append(circle_map[center][-1].color)
                    else :
                        consecutive.append('')
                if color_count['white'] == GRID_SIZE:
                    screen.blit(white_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                    game_over = True
                elif color_count['white'] == GRID_SIZE-1 and consecutive[1] == 'white' and consecutive[2] == 'white':
                    if combo not in game.rule:
                        game.rule.append(combo)
                        #print("in combo")
                    
                elif color_count['black'] == GRID_SIZE:
                    screen.blit(black_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                    game_over = True
                elif color_count['black'] == GRID_SIZE-1 and consecutive[1] == 'black' and consecutive[2] == 'black':
                     if combo not in game.rule:
                        game.rule.append(combo)
                        #print("in combo")
                    
        for button in [RESTART_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)  
        # Events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if RESTART_BUTTON.checkForInput(mouse_pos):
                        # Restart the game
                        circle_map.clear()
                        circles.clear()
                        illegal = False
                        game_over = False
                        active_player = 'black'
                        game = Game()           
                        continue
                    if MENU_BUTTON.checkForInput(mouse_pos):
                        circles.clear()
                        circle_map.clear()
                        illegal = False
                        game_over = False
                        active_player = 'black'                                  
                        Main_Menu()
                    
                    for circle in circles:
                        if circle.rect.collidepoint(event.pos) and game_over == False:
                            top_circle = circle
                            if(circle_map[top_circle.rect.center]):
                                top_circle = circle_map[top_circle.rect.center][-1]

                            if(top_circle.color != active_player):
                                illegal=True
                                break
                            active_circle_old_x = top_circle.rect.centerx
                            active_circle_old_y = top_circle.rect.centery
                            active_circle = top_circle.num

            if event.type == pygame.MOUSEMOTION:
                if active_circle is not None:
                    circles[active_circle].rect.move_ip(event.rel)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and active_circle is not None:
                    # Find the nearest center
                    dragged_rect = circles[active_circle].rect
                    nearest_center = min(centers, key=lambda center: math.dist((dragged_rect.centerx, dragged_rect.centery), (center[0],center[1])))
                    # Compare dragged and placed pieces
                    overlapping_circle = next((circle for circle in circles if circle.rect.centerx == nearest_center[0] and circle.rect.centery == nearest_center[1] and circle.rect.width >= dragged_rect.width), None)
                    
                    old_center = (active_circle_old_x, active_circle_old_y)

                    for com in game.rule:
                        for center in com:
                            if (nearest_center[0],nearest_center[1]) == center:
                                rule = True

                    if overlapping_circle is not None:
                        # Revert Old Positions
                        dragged_rect.centerx = active_circle_old_x
                        dragged_rect.centery = active_circle_old_y
                        
                    elif old_center in side_centers and circle_map[(nearest_center[0],nearest_center[1])] != [] and not rule:
                        # Revert Old Positions
                        dragged_rect.centerx = active_circle_old_x
                        dragged_rect.centery = active_circle_old_y
                        #print("not in rule")
                    else:                        
                        # Snap the dragged rectangle to the nearest center
                        dragged_rect.centerx = nearest_center[0]
                        dragged_rect.centery = nearest_center[1]

                        # Update board
                        circle_map[(nearest_center[0],nearest_center[1])].append(circles[active_circle])

                        if circle_map[(active_circle_old_x,active_circle_old_y)]:
                            circle_map[(active_circle_old_x,active_circle_old_y)].pop()

                        illegal = False
                        #print("in rule")

                        if old_center in side_centers: 
                            flag = 1 
                            move = Move( active_circle_old_y//CELL_SIZE if active_player == 'black' else (active_circle_old_y-CELL_SIZE)//CELL_SIZE,
                                         0 if active_player == 'black' else 1,
                                    (nearest_center[1]- CELL_SIZE//2) // CELL_SIZE,
                                    (nearest_center[0]-LEFT_MARGIN- CELL_SIZE//2) // CELL_SIZE,
                                    dragged_rect.width//20,
                                    flag)  
                        else:
                            flag = 0
                            move = Move((active_circle_old_y- CELL_SIZE//2) // CELL_SIZE ,
                                    (active_circle_old_x-LEFT_MARGIN- CELL_SIZE//2) // CELL_SIZE,
                                    (nearest_center[1]- CELL_SIZE//2) // CELL_SIZE,
                                    (nearest_center[0]-LEFT_MARGIN- CELL_SIZE//2) // CELL_SIZE,
                                    dragged_rect.width//20,
                                    flag)  
                            
                        if active_player == 'white':
                            active_player = 'black'
                        else:
                            active_player = 'white'

                    game.rule = []
                    rule = False
                    

                    active_circle = None
        
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        pygame.display.flip()
def H_vs_AI():
    screen.fill("black")
    game = Game() 
    logic = Logic(AI_DIFFICULTY,AI_PLAYER)
    logic_board = logic.board
    ai = logic.AI

    illegal = False
    game_over = False
    rule = False # Gobble up one of the 3 pieces in a row to prevent the opponent to win 

    while True:
        global active_circle
        global active_player
        
        #Change Background Image
        screen.blit(Background_Img, (0, 0))

        #Add Text Box Title
        screen.blit(text_box, (WIDTH + RIGHT_MARGIN*2 + 10, HEIGHT - 270))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        RESTART_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1350, 150), 
                        text_input="RESTART", font=get_font_title(70), base_color="yellow", hovering_color="green")
        MENU_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1350, 250), 
                        text_input="MENU", font=get_font_title(70), base_color="yellow", hovering_color="green")


        #Display Player Turn
        if active_player == 'white':
            screen.blit(w_turn, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 400))
        if active_player == 'black':
            screen.blit(b_turn, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 400))

        # Draw all circles
        for circle in circles:
            circle.draw(screen)

       # Illegal Play
        if illegal:
            screen.blit(text, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
            if(active_player == 'white'):
                screen.blit(white_turn,(WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 150))
            else:
                screen.blit(black_turn,(WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 150))

        #Check for winner
        if not illegal:
            for combo in game.winning_combinations:
                color_count = {'white': 0, 'black': 0}
                consecutive = []
                for center in combo:
                    if circle_map[center]:
                        color_count[circle_map[center][-1].color] += 1
                        consecutive.append(circle_map[center][-1].color)
                    else :
                        consecutive.append('')
                if color_count['white'] == GRID_SIZE:
                    screen.blit(white_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                    game_over = True
                elif color_count['white'] == GRID_SIZE-1 and consecutive[1] == 'white' and consecutive[2] == 'white':
                    if combo not in game.rule:
                        game.rule.append(combo)
                        #print("in combo")
                    
                elif color_count['black'] == GRID_SIZE:
                    screen.blit(black_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                    game_over = True
                elif color_count['black'] == GRID_SIZE-1 and consecutive[1] == 'black' and consecutive[2] == 'black':
                     if combo not in game.rule:
                        game.rule.append(combo)
                        #print("in combo")
                    
        for button in [RESTART_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)  
        # Events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if RESTART_BUTTON.checkForInput(mouse_pos):
                        # Restart the game
                        circle_map.clear()
                        circles.clear()
                        illegal = False
                        game_over = False
                        active_player = 'black'
                        game = Game()
                        logic = Logic(AI_DIFFICULTY,AI_PLAYER)
                        logic_board = logic.board
                        ai = logic.AI              
                        continue
                    if MENU_BUTTON.checkForInput(mouse_pos):
                        circles.clear()
                        circle_map.clear()
                        illegal = False
                        game_over = False
                        active_player = 'black'
                        logic = Logic(AI_DIFFICULTY,AI_PLAYER)
                        logic_board = logic.board
                        ai = logic.AI
                        Main_Menu()              
                        continue
                    
                    for circle in circles:
                        if circle.rect.collidepoint(event.pos) and game_over == False:
                            top_circle = circle
                            if(circle_map[top_circle.rect.center]):
                                top_circle = circle_map[top_circle.rect.center][-1]

                            if(top_circle.color != active_player):
                                illegal=True
                                break
                            active_circle_old_x = top_circle.rect.centerx
                            active_circle_old_y = top_circle.rect.centery
                            active_circle = top_circle.num

            if event.type == pygame.MOUSEMOTION:
                if active_circle is not None:
                    circles[active_circle].rect.move_ip(event.rel)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and active_circle is not None:
                    # Find the nearest center
                    dragged_rect = circles[active_circle].rect
                    nearest_center = min(centers, key=lambda center: math.dist((dragged_rect.centerx, dragged_rect.centery), (center[0],center[1])))
                    # Compare dragged and placed pieces
                    overlapping_circle = next((circle for circle in circles if circle.rect.centerx == nearest_center[0] and circle.rect.centery == nearest_center[1] and circle.rect.width >= dragged_rect.width), None)
                    
                    old_center = (active_circle_old_x, active_circle_old_y)

                    for com in game.rule:
                        for center in com:
                            if (nearest_center[0],nearest_center[1]) == center:
                                rule = True

                    if overlapping_circle is not None:
                        # Revert Old Positions
                        dragged_rect.centerx = active_circle_old_x
                        dragged_rect.centery = active_circle_old_y
                        
                    elif old_center in side_centers and circle_map[(nearest_center[0],nearest_center[1])] != [] and not rule:
                        # Revert Old Positions
                        dragged_rect.centerx = active_circle_old_x
                        dragged_rect.centery = active_circle_old_y
                        #print("not in rule")
                    else:                        
                        # Snap the dragged rectangle to the nearest center
                        dragged_rect.centerx = nearest_center[0]
                        dragged_rect.centery = nearest_center[1]

                        # Update board
                        circle_map[(nearest_center[0],nearest_center[1])].append(circles[active_circle])

                        if circle_map[(active_circle_old_x,active_circle_old_y)]:
                            circle_map[(active_circle_old_x,active_circle_old_y)].pop()

                        illegal = False
                        #print("in rule")
                        move = None
                        if old_center in side_centers: 
                            flag = 1 
                            move = Move( active_circle_old_y//CELL_SIZE if active_player == 'black' else (active_circle_old_y-CELL_SIZE)//CELL_SIZE,
                                         0 if active_player == 'black' else 1,
                                    (nearest_center[1]- CELL_SIZE//2) // CELL_SIZE,
                                    (nearest_center[0]-LEFT_MARGIN- CELL_SIZE//2) // CELL_SIZE,
                                    dragged_rect.width//20,
                                    flag)  
                        else:
                            flag = 0
                            move = Move((active_circle_old_y- CELL_SIZE//2) // CELL_SIZE ,
                                    (active_circle_old_x-LEFT_MARGIN- CELL_SIZE//2) // CELL_SIZE,
                                    (nearest_center[1]- CELL_SIZE//2) // CELL_SIZE,
                                    (nearest_center[0]-LEFT_MARGIN- CELL_SIZE//2) // CELL_SIZE,
                                    dragged_rect.width//20,
                                    flag)  

                        
                        #Check for winner
                        if not illegal:
                            for combo in game.winning_combinations:
                                color_count = {'white': 0, 'black': 0}
                                consecutive = []
                                for center in combo:
                                    if circle_map[center]:
                                        color_count[circle_map[center][-1].color] += 1
                                        consecutive.append(circle_map[center][-1].color)
                                    else :
                                        consecutive.append('')
                                if color_count['white'] == GRID_SIZE:
                                    screen.blit(white_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                                    game_over = True
                                elif color_count['white'] == GRID_SIZE-1 and consecutive[1] == 'white' and consecutive[2] == 'white':
                                    if combo not in game.rule:
                                        game.rule.append(combo)
                                        #print("in combo")
                                    
                                elif color_count['black'] == GRID_SIZE:
                                    screen.blit(black_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                                    game_over = True
                                elif color_count['black'] == GRID_SIZE-1 and consecutive[1] == 'black' and consecutive[2] == 'black':
                                    if combo not in game.rule:
                                        game.rule.append(combo)
                                        #print("in combo")                        
                        
                        
                        
                        
                        
                        # Player move
                        logic.make_move(move)
                        # Switch Active Player
                        if active_player == 'white':
                            active_player = 'black'
                        else:
                            active_player = 'white'

                        # AI Player
                        if not game_over:
                            ai_move = ai.evaluate(logic_board)
                            logic.make_move(ai_move)
                            make_GUI_Move(ai_move)
       

                        # Switch Active Player
                        if active_player == 'white':
                            active_player = 'black'
                        else:
                            active_player = 'white'

                        #print(
                        #   move.from_row,
                        #    move.from_col,
                        #    move.to_row,
                        #    move.to_col,
                        #    move.score,
                        #    move.flag
                        #)

                    game.rule = []
                    rule = False

                    active_circle = None
        
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        pygame.display.flip()

def AI_vs_AI():
    screen.fill("black")
    game = Game() 
    logic = Logic(AI_DIFFICULTY,AI_PLAYER)
    logic_board = logic.board
    ai = logic.AI
    ai_2 = logic.AI_2

    illegal = False
    game_over = False
    rule = False # Gobble up one of the 3 pieces in a row to prevent the opponent to win 
    
    while True:
        global active_circle
        global active_player
        #Change Background Image
        screen.blit(Background_Img, (0, 0))

        #Add Text Box Title
        screen.blit(text_box, (WIDTH + RIGHT_MARGIN*2 + 10, HEIGHT - 270))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        RESTART_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1350, 150), 
                        text_input="RESTART", font=get_font_title(70), base_color="yellow", hovering_color="green")
        MENU_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1350, 250), 
                        text_input="MENU", font=get_font_title(70), base_color="yellow", hovering_color="green")


        #Display Player Turn
        if active_player == 'white':
            screen.blit(w_turn, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 400))
        if active_player == 'black':
            screen.blit(b_turn, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 400))

        # Draw all circles
        for circle in circles:
            circle.draw(screen)

       # Illegal Play
        if illegal:
            screen.blit(text, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
            if(active_player == 'white'):
                screen.blit(white_turn,(WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 150))
            else:
                screen.blit(black_turn,(WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 150))

        #Check for winner
        if not illegal:
            for combo in game.winning_combinations:
                color_count = {'white': 0, 'black': 0}
                consecutive = []
                for center in combo:
                    if circle_map[center]:
                        color_count[circle_map[center][-1].color] += 1
                        consecutive.append(circle_map[center][-1].color)
                    else :
                        consecutive.append('')
                if color_count['white'] == GRID_SIZE:
                    screen.blit(white_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                    game_over = True
                elif color_count['white'] == GRID_SIZE-1 and consecutive[1] == 'white' and consecutive[2] == 'white':
                    if combo not in game.rule:
                        game.rule.append(combo)
                        #print("in combo")
                    
                elif color_count['black'] == GRID_SIZE:
                    screen.blit(black_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                    game_over = True
                elif color_count['black'] == GRID_SIZE-1 and consecutive[1] == 'black' and consecutive[2] == 'black':
                     if combo not in game.rule:
                        game.rule.append(combo)
                        #print("in combo")
                    
        for button in [RESTART_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)  
        # Events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if RESTART_BUTTON.checkForInput(mouse_pos):
                        # Restart the game
                        circle_map.clear()
                        circles.clear()
                        illegal = False
                        game_over = False
                        active_player = 'black'
                        game = Game()
                        logic = Logic(AI_DIFFICULTY,AI_PLAYER)
                        logic_board = logic.board
                        ai = logic.AI              
                        
                    if MENU_BUTTON.checkForInput(mouse_pos):
                        circles.clear()
                        circle_map.clear()
                        illegal = False
                        game_over = False
                        active_player = 'black'
                        logic = Logic(AI_DIFFICULTY,AI_PLAYER)
                        logic_board = logic.board
                        ai = logic.AI
                        Main_Menu()              

                    game.rule = []
                    rule = False

                    active_circle = None
        
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        #Check for winner
        if not illegal:
            for combo in game.winning_combinations:
                color_count = {'white': 0, 'black': 0}
                consecutive = []
                for center in combo:
                    if circle_map[center]:
                        color_count[circle_map[center][-1].color] += 1
                        consecutive.append(circle_map[center][-1].color)
                    else :
                        consecutive.append('')
                        if color_count['white'] == GRID_SIZE:
                            screen.blit(white_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                            game_over = True
                        elif color_count['white'] == GRID_SIZE-1 and consecutive[1] == 'white' and consecutive[2] == 'white':
                            if combo not in game.rule:
                                game.rule.append(combo)
                                    
                        elif color_count['black'] == GRID_SIZE:
                            screen.blit(black_win, (WIDTH + RIGHT_MARGIN*2 + 20, HEIGHT - 200))
                            game_over = True
                        elif color_count['black'] == GRID_SIZE-1 and consecutive[1] == 'black' and consecutive[2] == 'black':
                            if combo not in game.rule:
                                game.rule.append(combo)
                                                            
            # AI Player              
            if not game_over and active_player == "black":
                ai_move = ai.evaluate(logic_board, True)
                logic.make_move(ai_move)
                make_GUI_Move(ai_move)           

             # AI Player                                
            if not game_over and active_player == "white":                          
                ai_move = ai_2.evaluate(logic_board, True)
                logic.make_move(ai_move)
                make_GUI_Move(ai_move)
            if not game_over:
                if active_player == 'white':
                    active_player = 'black'
                else:
                    active_player = 'white'                    
                         
                  
        pygame.display.flip()        
def options():
    global AI_DIFFICULTY
    global AI_DIFFICULTY_2
    global h_v_h
    global h_v_ai
    global ai_v_ai
    while True:
        screen.fill("black")
        if AI_DIFFICULTY == 0:
            if h_v_h:
                screen.blit(Options_BG, (0, 0))
                screen.blit(checked, (250, 270))
                screen.blit(checked, (1300, 270))
            elif h_v_ai:
                screen.blit(Options_BG, (0, 0))
                screen.blit(checked, (250, 270))
                screen.blit(checked, (1320, 380))
            else:
                if AI_DIFFICULTY_2 == 0:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (250, 270))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (730, 270))
                elif AI_DIFFICULTY_2 == 1:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (250, 270))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (800, 380))
                elif AI_DIFFICULTY_2 == 2:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (250, 270))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (730, 490))                     

                
        elif AI_DIFFICULTY == 1:
            if h_v_h:
                screen.blit(Options_BG, (0, 0))
                screen.blit(checked, (320, 380))
                screen.blit(checked, (1300, 270))
            elif h_v_ai:
                screen.blit(Options_BG, (0, 0))
                screen.blit(checked, (320, 380))
                screen.blit(checked, (1320, 380))
            else:
                if AI_DIFFICULTY_2 == 0:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (320, 380))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (730, 270))
                elif AI_DIFFICULTY_2 == 1:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (320, 380))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (800, 380))
                elif AI_DIFFICULTY_2 == 2:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (320, 380))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (730, 490))   

        elif AI_DIFFICULTY == 2:
            if h_v_h:
                screen.blit(Options_BG, (0, 0))
                screen.blit(checked, (250, 490))
                screen.blit(checked, (1300, 270))
            elif h_v_ai:
                screen.blit(Options_BG, (0, 0))
                screen.blit(checked, (250, 490))
                screen.blit(checked, (1320, 380))
            else:
                if AI_DIFFICULTY_2 == 0:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (250, 490))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (730, 270))
                elif AI_DIFFICULTY_2 == 1:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (250, 490))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (800, 380))
                elif AI_DIFFICULTY_2 == 2:
                    screen.blit(Options_BG, (0, 0))
                    screen.blit(checked, (250, 490))
                    screen.blit(checked, (1340, 490))
                    screen.blit(checked, (730, 490))      
        

        
        Difficulty_txt = get_font_title(70).render("-Difficulty A1", True, "white")
        screen.blit(Difficulty_txt,(50, 170))
        Difficulty_txt = get_font_title(70).render("-Difficulty A2", True, "white")
        screen.blit(Difficulty_txt,(500, 170))
        Mode_txt = get_font_title(70).render("-Mode", True, "white")
        screen.blit(Mode_txt,(1000, 170))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font_title(200).render("Options", True, "white")
        MENU_RECT = MENU_TEXT.get_rect(center=(340, 100))

        EASY_BUTTON_1 = Button(image=pygame.image.load("Images/Rect.png"), pos=(170, 300), 
                            text_input="EASY", font=get_font_title(70), base_color="yellow", hovering_color="green")
        HARD_BUTTON_1 = Button(image=pygame.image.load("Images/Rect.png"), pos=(170, 520), 
                            text_input="HARD", font=get_font_title(70), base_color="yellow", hovering_color="green")
        MED_BUTTON_1 = Button(image=pygame.image.load("Images/Rect.png"), pos=(200, 410), 
                            text_input="MEDIUM", font=get_font_title(70), base_color="yellow", hovering_color="green")
        EASY_BUTTON_2 = Button(image=pygame.image.load("Images/Rect.png"), pos=(640, 300), 
                            text_input="EASY", font=get_font_title(70), base_color="yellow", hovering_color="green")
        HARD_BUTTON_2 = Button(image=pygame.image.load("Images/Rect.png"), pos=(640, 520), 
                            text_input="HARD", font=get_font_title(70), base_color="yellow", hovering_color="green")
        MED_BUTTON_2 = Button(image=pygame.image.load("Images/Rect.png"), pos=(670, 410), 
                            text_input="MEDIUM", font=get_font_title(70), base_color="yellow", hovering_color="green")                 
        HVH_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1150, 300), 
                            text_input="H vs H", font=get_font_title(70), base_color="yellow", hovering_color="green")
        HVAI_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1170, 410), 
                            text_input="H vs AI", font=get_font_title(70), base_color="yellow", hovering_color="green")   
        AIVAI_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(1190, 520), 
                            text_input="AI vs AI", font=get_font_title(70), base_color="yellow", hovering_color="green") 
        BACK_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(200, 650), 
                            text_input="BACK", font=get_font_title(70), base_color="yellow", hovering_color="green")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [EASY_BUTTON_1, HARD_BUTTON_1, BACK_BUTTON, HVH_BUTTON, HVAI_BUTTON, AIVAI_BUTTON, MED_BUTTON_1,EASY_BUTTON_2, HARD_BUTTON_2, MED_BUTTON_2]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EASY_BUTTON_1.checkForInput(MENU_MOUSE_POS):
                    AI_DIFFICULTY = 0
                if HARD_BUTTON_1.checkForInput(MENU_MOUSE_POS):
                    AI_DIFFICULTY = 2
                if MED_BUTTON_1.checkForInput(MENU_MOUSE_POS):
                    AI_DIFFICULTY = 1
                if EASY_BUTTON_2.checkForInput(MENU_MOUSE_POS):
                    AI_DIFFICULTY_2 = 0
                if HARD_BUTTON_2.checkForInput(MENU_MOUSE_POS):
                    AI_DIFFICULTY_2 = 2
                if MED_BUTTON_2.checkForInput(MENU_MOUSE_POS):
                    AI_DIFFICULTY_2 = 1
                if HVH_BUTTON.checkForInput(MENU_MOUSE_POS):
                    h_v_h = True
                    h_v_ai = False
                    ai_v_ai = False
                if HVAI_BUTTON.checkForInput(MENU_MOUSE_POS):
                    h_v_h = False
                    h_v_ai = True
                    ai_v_ai = False
                if AIVAI_BUTTON.checkForInput(MENU_MOUSE_POS):
                    h_v_h = False
                    h_v_ai = False
                    ai_v_ai = True
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Main_Menu()

        pygame.display.update()    

def Main_Menu():
    while True:
        screen.blit(Menu_BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font_title(200).render("Gobblet!", True, "white")
        MENU_RECT = MENU_TEXT.get_rect(center=(400, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(250, 250), 
                            text_input="PLAY", font=get_font_title(100), base_color="yellow", hovering_color="green")
        OPTIONS_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(320, 400), 
                            text_input="OPTIONS", font=get_font_title(100), base_color="yellow", hovering_color="green")
        QUIT_BUTTON = Button(image=pygame.image.load("Images/Rect.png"), pos=(250, 550), 
                            text_input="QUIT", font=get_font_title(100), base_color="yellow", hovering_color="green")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    if h_v_h:
                        H_vs_H()
                    elif h_v_ai:
                        H_vs_AI()
                    else:
                        AI_vs_AI()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

 
Main_Menu()


