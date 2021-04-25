import pygame
import os
import sys
import random
from math import inf
import numpy as np
pygame.font.init()


WIDTH, HEIGHT = 500, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('tic tac toe')

FPS = 60

active_color = (59, 91, 219)
idle_color = (26, 50, 145) 


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


x_img = pygame.transform.scale(pygame.image.load(resource_path(os.path.join('assets', 'x.png'))), (WIDTH//3, HEIGHT//3))
o_img = pygame.transform.scale(pygame.image.load(resource_path(os.path.join('assets', 'o.png'))), (WIDTH//3, HEIGHT//3))


win_font = pygame.font.SysFont('impact', 90)


button_font = pygame.font.SysFont('impact', 20)
class Button():
    def __init__(self, x, y, w, h, text: str, funct:callable =lambda: print('undefined function')):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.y = y
        self.x = x
        self.w = w
        self.h = h
        self.funct = funct
    
    def draw(self, color=(26, 50, 145), wind=win):
        pygame.draw.rect(wind, color, self.rect)
        draw_text = button_font.render(self.text, 1, (255, 255, 255))
        wind.blit(draw_text, (self.x + self.w//2 - draw_text.get_width()//2, self.y + self.h//2 - draw_text.get_height()//2)) 


class Case():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, WIDTH//3, HEIGHT//3)


class Board():
    def __init__(self, a=np.array([[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]])):
        self.array = a  # 0: O, 1: X, -1: Empty

    def count_empty(self):
        s = 0
        for i in self.array:
            for j in i:
                if j == -1:
                    s += 1
        return s

    def game_over(self):
        return self.count_empty() == 0 or self.check_win() != -1

    def empty_cases(self):
        em = []
        for row, i in enumerate(self.array):
            for col, c in enumerate(i):
                if c == -1:
                    em.append((row, col))
        
        return em
    
    def make_move(self, coordinates: tuple, turn: int):  # turn: 0/1
        if self.array[coordinates[0]][coordinates[1]] == -1:
            new_array = np.copy(self.array)
            new_array[coordinates[0]][coordinates[1]] = turn
            return new_array
        else:
            print(self.array, '   ', coordinates)
            raise IndexError('Case already full')
    
    def child_boards(self, turn):
        children = []
        for i in self.empty_cases():
            children.append(Board(a=self.make_move(i, turn)))
        return children

    def check_win(self):    # Returns -1: No winner/ 0: O wins/ 1: X wins
        
        for i in self.array:
            if i[0] != -1 and i[0] == i[1] == i[2]:
                return i[0]
        
        for c in range(3):
            columns = [i[c] for i in self.array]
            if columns[0] != -1 and columns[0] == columns[1] == columns[2]:
                return columns[0]
        
        if self.array[0][0] != -1 and self.array[0][0] == self.array[1][1] == self.array[2][2]:
            return self.array[0][0]
        
        if self.array[0][2] != -1 and self.array[0][2] == self.array[1][1] == self.array[2][0]:
            return self.array[0][2]
        
        return -1

    def __repr__(self):
        for r in self.array:
            s = ''
            for c in r:
                if c == 1:
                    s+='X\t'
                elif c == 0:
                    s+='O\t'
                else:
                    s+=' \t'
            print(s)
        return ''


class GameBoard(Board):
    def __init__(self):
        self.array = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]
        w = WIDTH//3
        h = HEIGHT//3
        self.cases = [[Case(0, 0), Case(w, 0), Case(2*w, 0)], [Case(0, h), Case(w, h), Case(2*w, h)],
                        [Case(0, 2*h), Case(w, 2*h), Case(2*w, 2*h)]]

    def fill(self, coordinates: tuple, turn: int):
        if self.array[coordinates[0]][coordinates[1]] == -1:
            self.array[coordinates[0]][coordinates[1]] = turn
            c = self.cases[coordinates[0]][coordinates[1]]
            img = x_img if turn == 1 else o_img
            
            win.blit(img, (c.x, c.y))
            draw_borders()
            self.cases[coordinates[0]][coordinates[1]] = None

        else:
            raise IndexError('Case already full')


class RandomPlayer():
    def __init__(self) -> None:
        pass

    def play(self, board):
        return random.choice(board.empty_cases())


class AiPlayer():
    def __init__(self, turn) -> None:
        self.turn = turn

    def play(self, board):
        virtual_board = Board(a=board.array)
        
        return change_boards(self.minimax(virtual_board, 0, -inf, inf, True), board)

    def minimax(self, state: Board, depth, alpha, beta, maximizingPlayer):

        if state.game_over():
            return static_evaluation(state, self.turn)
        
        if maximizingPlayer:
            maxEval = -inf
            
            for child in state.child_boards(self.turn): 
                eval = self.minimax(child, depth+1, alpha, beta, False)
                if eval > maxEval:
                    maxEval = eval
                    bestMove = child
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            if depth == 0:
                return bestMove
            return maxEval

        else:
            minEval = inf

            for child in state.child_boards(1-self.turn):                
                eval = self.minimax(child, depth+1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval


def change_boards(b1: Board, b2: Board):
    for row, r in enumerate(b1.array):
        for col, c in enumerate(b1.array):
            if b1.array[row][col] != b2.array[row][col]:
                return (row, col)
    raise ValueError('No change found')


def static_evaluation(board: Board, turn):
    if not board.game_over():
        raise ValueError('Game not over')
    
    if board.check_win() == 1 - turn:
        a = -1
    elif board.check_win() == -1:
        return 0
    elif board.check_win() == turn:
        a = 1
    
    return a*(board.count_empty() + 1)


bw = 2
borders = [pygame.Rect(WIDTH//3-bw, 0, bw, HEIGHT), pygame.Rect(WIDTH*2//3, 0, bw, HEIGHT),
             pygame.Rect(0, HEIGHT//3-bw, WIDTH, bw), pygame.Rect(0, HEIGHT*2//3, WIDTH, bw)]
def draw_borders():
    for b in borders:
        pygame.draw.rect(win, (0, 0, 0), b)
    pygame.display.update()


def handle_click(mx, my, click, board, turn):
    if not click:
        return False

    for row, i in enumerate(board.cases):
        for col, c in enumerate(i):
            if c is not None:
                r = c.rect
            else:
                continue
            if r.collidepoint((mx, my)):
                try:
                    board.fill((row, col), turn)
                    return True
                except IndexError:
                    return False
    return False


def draw_result(result):
    if result == 1:
        text = 'X Wins'
    elif result == 0:
        text = 'O Wins'
    else:
        text = 'yassine rbe7'

    pygame.display.set_caption(text)
    
    draw_text = win_font.render(text, 1, (0, 0, 0))
    win.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(5000)
    main_menu()


def draw_turn(turn):
    text = 'X\'s turn' if turn == 1 else 'O\'s turn'
    pygame.display.set_caption(text)
    

def main():  
    global p2, ai_p, random_p  
    pygame.display.set_caption('tic tac toe')

    turn = random.randint(0, 1)

    if random_p:
        player = RandomPlayer()
    elif ai_p:
        player = AiPlayer(1 - turn)


    clock = pygame.time.Clock()
    win.fill((255, 255, 255))
    draw_borders()

    board = GameBoard()

    click = False

    draw_turn(turn)

    run = True
    while run:
        clock.tick(FPS)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            else:
                click = False

        change = handle_click(mx, my, click, board, turn)
        if change:
            k = board.check_win()
            if k in [0, 1]:
                draw_result(k)
            elif board.game_over():
                draw_result(-1)
            
            turn = 1 - turn
            draw_turn(turn)
        
            if random_p or ai_p:
                board.fill(player.play(board), turn)

                k = board.check_win()
                if k in [0, 1]:
                    draw_result(k)
                elif board.game_over():
                    draw_result(-1)
                
                turn = 1 - turn
                draw_turn(turn)


def draw_menu(buttons, mx, my, click, enter):
    global current
    win.fill((255, 255, 255))

    i = 0
    for b in buttons:
        r = b.rect
        if r.collidepoint((mx, my)):
            current = -1
            b.draw(active_color)
            if click:
                b.funct()
                click = False
                return False
        elif i == current:
            b.draw(active_color)
            if enter:
                b.funct()
                click = False
                return False
        else:
            b.draw(idle_color)
        i += 1

    pygame.display.update()
    return True


random_p = False
ai_p = False
p2 = False
def random_player():
    global random_p
    random_p = True
    main()

def ai_player():
    global ai_p
    ai_p = True
    main()
 
def p2_player():
    global p2
    p2 = True
    main()


button_size = (200, 50)
button_spacing = 20
button_y_init = 100
current = -1
def main_menu():
    global current, random_p, ai_p, p2
    random_p = False
    ai_p = False
    p2 = False
    current = -1
    clock = pygame.time.Clock()
    pygame.display.set_caption('tic tac toe')

    buttons = [Button(WIDTH//2-button_size[0]//2, button_y_init, button_size[0], button_size[1], 'P1 vs P2', p2_player),
     Button(WIDTH//2-button_size[0]//2, button_y_init+button_size[1]+button_spacing, button_size[0], button_size[1], 'P1 vs COM', random_player),
     Button(WIDTH//2-button_size[0]//2, button_y_init+(button_size[1]+button_spacing)*2, button_size[0], button_size[1], 'P1 vs AI', ai_player),
     Button(WIDTH//2-button_size[0]//2, button_y_init+(button_size[1]+button_spacing)*3, button_size[0], button_size[1], 'Exit', pygame.quit)]
    run = True

    while run:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        enter = False
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            else:
                click = False

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_z]:
                    current -= 1
                    if current < 0:
                        current = len(buttons) - 1
                
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    current += 1
                    if current >= len(buttons):
                        current = 0

                if event.key == pygame.K_RETURN:
                    enter = True    
        
        run = draw_menu(buttons, mx, my, click, enter)



if __name__ == '__main__':
    main_menu()

