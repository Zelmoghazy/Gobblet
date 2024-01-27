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