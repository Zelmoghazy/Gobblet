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

class Board:
    def __init__(self) -> None:
        self.board = np.zeros((ROWS, COLS), dtype=Square)
        self.side_stack = np.zeros((3, 2), dtype=Square)

        self.side_stack[0][0] = Square(Gobblet_Stack([gw11, gw21, gw31, gw41]))
        self.side_stack[1][0] = Square(Gobblet_Stack([gw12, gw22, gw32, gw42]))
        self.side_stack[2][0] = Square(Gobblet_Stack([gw13, gw23, gw33, gw43]))
        
        self.side_stack[0][1] = Square(Gobblet_Stack([gb11, gb21, gb31, gb41]))
        self.side_stack[1][1] = Square(Gobblet_Stack([gb12, gb22, gb32, gb42]))
        self.side_stack[2][1] = Square(Gobblet_Stack([gb13, gb23, gb33, gb43]))

        # self.squares = np.zeros((ROWS, COLS))
        # self.empty_squares = self.squares
        # self.marked_squares = 0
    def Move(Move move):
        # Move inside the board
        if(move.flag == 0):
            self.board[move.to_row][move.to_col].add_piece(self.board[move.from_row][move.from_col].top_piece())
            self.board[move.from_row][move.from_col].remove_piece()
        # Move from the side stack
        if (move.flag == 1):
            self.board[move.to_row][move.to_col].add_piece(self.side_stack[move.from_row][move.from_col].top_piece())
            self.side_stack[move.from_row][move.from_col].remove_piece()

    def max_side_stack(self,player):
        max = 0
        row = 0
        for i in range(3):
            if(self.side_stack[i][player].top_piece().size > max):
                max = self.side_stack[i][player].top_piece().size
                row = i
        return max,row

    # Unmove previous move
    def Unmove(Move move):
        # Move inside the board
        if(move.flag == 0):
            self.board[move.from_row][move.from_col].add_piece(self.board[move.to_row][move.to_col].top_piece())
            self.board[move.to_row][move.to_col].remove_piece()
        # Move from the side stack
        if (move.flag == 1):
            self.side_stack[move.from_row][move.from_col].add_piece(self.board[move.to_row][move.to_col].top_piece())
            self.board[move.to_row][move.to_col].remove_piece()

    def final_state(self):
        # check rows
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] == self.squares[row][3] != 0:
                return self.squares[row][0]
                # append color
                # append rows score to a variable
                # append each gobblet size score variable
        
        # check columns
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] == self.squares[3][col] != 0:
                return self.squares[0][col]
                # append color
                # append columns score to a variable
                # append each gobblet size score variable
        # check diagonals
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] == self.squares[3][3] != 0:
            return self.squares[0][0]
        if self.squares[0][3] == self.squares[1][2] == self.squares[2][1] == self.squares[3][0] != 0:
            return self.squares[0][3]
        # check draw
        if self.is_full():
            return 3
        # game is not over
        # return sum of scores
        return 0


    def mark_square(self, row, col, player):
        self.squares[row][col] = player
        self.marked_squares += 1

    def unmark_square(self, row, col):
        self.squares[row][col] = 0
        self.marked_squares -= 1

    def get_empty_squares(self):
        # Loop in Side stack for an empty square
        # return empty_squares and all player pieces on board and opponent pieces on board
        # first pick the smallest player piece and loop on opponent pieces on board
        # if the opponent piece is smaller than the player piece then mark it as a possible move
        # def get_available_squares(self,player,)

        # Loop in Board for an empty square or a square with a smaller piece
        empty_squares = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_square(row, col):
                    empty_squares.append((row, col))
        return empty_squares

    def get_score(self,move,player):
        size = move.score
        score = 0
        # check rows
        string = ''
        for row in range(ROWS):
            string.clear()
            for col in range(COLS):
                if(move.to_row == row and move.to_col == col):
                    if(player == 1):
                        string.append('w')
                        score += size
                    else:
                        string.append('b')
                        score -= size
                string.append(self.squares[row][col].color)
                if(self.squares[row][col].color == player):
                    score += self.squares[row][col].size
                else:
                    score -= self.squares[row][col].size
            score += hashmap[string]
        # check columns
        for col in range(COLS):
            string.clear()
            for row in range(ROWS):
                if(move.to_row == row and move.to_col == col):
                    if(player == 1):
                        string.append('w')
                        score += size
                    else:
                        string.append('b')
                        score -= size
                string.append(self.squares[row][col].color)
                if(self.squares[row][col].color == player):
                    score += self.squares[row][col].size
                else:
                    score -= self.squares[row][col].size
            score += hashmap[string]
        # check diagonals
        string.clear()
        for i in range(ROWS):
            if(move.to_row == row and move.to_col == row):
                if(player == 1):
                    string.append('w')
                    score += size
                else:
                    string.append('b')
                    score -= size
            string.append(self.squares[i][i].color)
            if(self.squares[i][i].color == player):
                score += self.squares[i][i].size
            else:
                score -= self.squares[i][i].size
        score += hashmap[string]
        string.clear()

        for i in range(ROWS):
            if(move.to_row == row and move.to_col == ROWS-row):
                if(player == 1):
                    string.append('w')
                    score += size
                else:
                    string.append('b')
                    score -= size
            string.append(self.squares[i][ROWS-i].color)
            if(self.squares[i][ROWS-i].color == player):
                score += self.squares[i][ROWS-i].size
            else:
                score -= self.squares[i][ROWS-i].size
        score += hashmap[string]
        return score
    
        # append color
        # append rows score to a variable
        # append each gobblet size score variable

    def getAvailableMoves(self,player):
        # Loop in Side stack for an empty square
        # return empty_squares and all player pieces on board and opponent pieces on board
        # first pick the smallest player piece and loop on opponent pieces on board
        # if the opponent piece is smaller than the player piece then mark it as a possible move
        # def get_available_squares(self,player,)

        # Loop in Board for an empty square or a square with a smaller piece

        # First check for empty squares on board 
        moves = []

        max,side_row =  self.max_side_stack(player)
  
        for row in range(ROWS):      
            for col in range(COLS):
                if self.board[row][col].is_empty():
                    move = Move(side_row,player,row,col,max,1)
                    get_score(move,player)
                    moves.append()
        # First check if side stack is not empty
        # if not empty then check for empty squares in
    def empty_square(self, row, col):
        return self.squares[row][col] == 0

    def is_full(self):
        return self.marked_squares == ROWS * COLS   
    
    def is_empty(self):
        return self.marked_squares == 0 


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

class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.AI = AI()
        self.player = 1
        self.game_mode = 'AI'
        self.running = True
        self.show_lines()

    def show_lines(self):
        for i in range(ROWS):
            pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE),LINE_WIDTH)
        for j in range(COLS):
            pygame.draw.line(screen, LINE_COLOR, (j * SQUARE_SIZE, 0), (j * SQUARE_SIZE, HEIGHT),LINE_WIDTH)

    def next_turn(self):
        self.player = (self.player % 2) + 1


    def make_move(self, row, col):
        self.board.mark_square(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()
    
    def draw_fig(self, row, col):
        centre = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
        if self.player == 1:
            pygame.draw.circle(screen, CIRCLE_COLOR,centre, CIRCLE_RADIUS, CIRCLE_WIDTH)
        elif self.player == 2:
            start_desc = (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE - SQUARE_SIZE//4)
            end_desc = (col * SQUARE_SIZE + SQUARE_SIZE - SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4)

            start_asc = (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4)
            end_asc = (col * SQUARE_SIZE + SQUARE_SIZE - SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE - SQUARE_SIZE//4)

            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)

def main():
    game = Game()
    board = game.board
    ai = game.AI

    while game.running == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                if(board.empty_square(row, col) == True):
                    game.make_move(row, col)

                print(game.board.squares)
                print(game.player)
        
        if game.game_mode == 'AI' and game.player == ai.player:
            pygame.display.update()
            row,col = ai.evaluate(board)
            game.make_move(row, col)


        if game.board.final_state() != 0:
            if game.board.final_state() == 3:
                print("Draw")
            elif game.board.final_state() == 1:
                print("Player 1 wins")      
            elif game.board.final_state() == 2:
                print("Player 2 wins")
            game.running = False
        pygame.display.update()
    

if __name__ == "__main__":
    main()