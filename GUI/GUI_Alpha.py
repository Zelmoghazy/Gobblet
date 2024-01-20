import pygame
import sys
import math
from collections import defaultdict
# from engine.gobblet_engine.gobblet_engine import GobbletEngine
# from engine.gobblet_engine.gobblet_ai_bot import GobbletAIBot
# from engine.gobblet_engine.utils.action import Action

# engine = GobbletEngine(whose_turn=1)
# ai = GobbletAIBot()

# action = ai.getNextAction(engine.getGameState())
# engine.step(action.getBoardType(), 
#             action.getX1(), 
#             action.getY1, 
#             action.getY1, 0)


# engine.getGameState()

# engine.step(0, 0, 0, 0, 0)

pygame.init()

# Colors
black  = (0, 0, 0)
white  = (255, 255, 255)

# Positions
WIDTH, HEIGHT = 800, 800
LEFT_MARGIN = 200
RIGHT_MARGIN = 200
CONTROL_PANEL = 300

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
Background_Img = pygame.image.load("Images\\Board.png")
Background_Img = pygame.transform.scale(Background_Img, (WIDTH + LEFT_MARGIN*2 + CONTROL_PANEL, HEIGHT))

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
active_player='white'

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

# Restart Button
restart_button_rect = pygame.Rect(WIDTH + RIGHT_MARGIN * 2 + 50, HEIGHT - HEIGHT + 50, 200, 50)
restart_button_color = (255, 165, 0) 
restart_button_text = font.render("Restart Game", True, 'black')
 
#Cirlce Class============================================================
class Circle:
    def __init__(self, color, center, radius,num):
        self.num = num    #id
        self.color = color
        self.rect = pygame.Rect(center[0] - radius, center[1] - radius, 2 * radius, 2 * radius)
        self.center = center
        self.radius = radius 

    def draw(self, screen):
        pygame.draw.circle(screen,self.color,self.rect.center,self.rect.width)

    def __eq__(self, other):
        if isinstance(other, Circle):
            return self.num == other.num
        return False

#Class for Move
class Move:
    def __init__(self, from_row, from_col, to_row, to_col,score,flag):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.score = score
        self.flag = flag    # Either 0 for board or 1 for side stack (initialized with piece move and rewritten)

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

def main():
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

        # Draw Restart Button
        pygame.draw.rect(screen, restart_button_color, restart_button_rect)
        screen.blit(restart_button_text, (restart_button_rect.x + 10, restart_button_rect.y + 10))

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
                    

        # Events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_button_rect.collidepoint(mouse_pos):
                        # Restart the game
                        circle_map.clear()
                        circles.clear()
                        illegal = False
                        game_over = False
                        active_player = 'white'
                        game = Game()             
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
                    # Switch Active Player
                    if active_player == 'white':
                        active_player = 'black'
                    else:
                        active_player = 'white'

                    active_circle = None
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
                
        pygame.display.flip()

main()