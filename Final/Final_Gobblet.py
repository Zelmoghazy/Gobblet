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