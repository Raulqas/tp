import pygame
import sys
import random
import math
from abc import ABC, abstractmethod

# --- Constants ---
SCREEN_SIZE = 450
GRID_SIZE = 3
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
LINE_WIDTH = 15
CIRCLE_WIDTH = 15
CROSS_WIDTH = 20
RADIUS = CELL_SIZE // 4
OFFSET = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

# --- Sounds ---
pygame.mixer.init()
MOVE_SOUND = pygame.mixer.Sound("move.wav")
WIN_SOUND = pygame.mixer.Sound("win.wav")

# --- Button class ---
class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                   self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# --- Game Logic ---

class TicTacToe:
    def __init__(self):
        self.board = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.current_winner = None

    def available_moves(self):
        return [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.board[r][c] is None]

    def make_move(self, row, col, player):
        if self.board[row][col] is None:
            self.board[row][col] = player
            pygame.mixer.Sound.play(MOVE_SOUND)
            if self.check_winner(row, col, player):
                pygame.mixer.Sound.play(WIN_SOUND)
                self.current_winner = player
            return True
        return False

    def check_winner(self, row, col, player):
        if all([self.board[row][c] == player for c in range(GRID_SIZE)]):
            return True
        if all([self.board[r][col] == player for r in range(GRID_SIZE)]):
            return True
        if row == col and all([self.board[i][i] == player for i in range(GRID_SIZE)]):
            return True
        if row + col == GRID_SIZE - 1 and all([self.board[i][GRID_SIZE - 1 - i] == player for i in range(GRID_SIZE)]):
            return True
        return False

    def empty_cells(self):
        return any(None in row for row in self.board)

    def is_full(self):
        return not self.empty_cells()

    def reset(self):
        self.board = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.current_winner = None

# --- Players ---

class Player(ABC):
    def __init__(self, symbol):
        self.symbol = symbol

    @abstractmethod
    def get_move(self, game):
        pass

class HumanPlayer(Player):
    def get_move(self, game):
        valid_square = False
        while not valid_square:
            move = input("Введите ход (строка, столбец): ")
            try:
                row, col = map(int, move.split(','))
                if (row, col) in game.available_moves():
                    valid_square = True
                else:
                    raise ValueError
            except ValueError:
                print("Неверный ход. Попробуйте снова.")
        return row, col

class AIPlayer(Player):
    def __init__(self, symbol, difficulty='hard'):
        super().__init__(symbol)
        self.difficulty = difficulty

    def get_move(self, game):
        if self.difficulty == 'easy':
            return random.choice(game.available_moves())
        else:
            if len(game.available_moves()) == GRID_SIZE * GRID_SIZE:
                return (1, 1)
            return self.minimax(game, self.symbol)['position']

    def minimax(self, game, player):
        max_player = self.symbol
        other_player = 'O' if player == 'X' else 'X'

        if game.current_winner == other_player:
            return {'position': None, 'score': 1 * (len(game.available_moves()) + 1) if other_player == max_player else -1 * (len(game.available_moves()) + 1)}
        elif not game.empty_cells():
            return {'position': None, 'score': 0}

        if player == max_player:
            best = {'position': None, 'score': -math.inf}
        else:
            best = {'position': None, 'score': math.inf}

        for possible_move in game.available_moves():
            row, col = possible_move
            game.make_move(row, col, player)
            sim_score = self.minimax(game, other_player)

            game.board[row][col] = None
            game.current_winner = None
            sim_score['position'] = (row, col)

            if player == max_player:
                if sim_score['score'] > best['score']:
                    best = sim_score
            else:
                if sim_score['score'] < best['score']:
                    best = sim_score

        return best

# --- Game Interface ---

class GameInterface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption('Крестики-Нолики')
        self.screen.fill(WHITE)
        self.game = TicTacToe()
        self.human = None
        self.ai = None
        self.player_symbol = 'X'
        self.ai_symbol = 'O'
        self.difficulty = 'easy'
        self.running = True
        self.main_menu()

    def main_menu(self):
        self.screen.fill(WHITE)
        font = pygame.font.Font(None, 50)
        title = font.render('Крестики-Нолики', True, BLACK)
        self.screen.blit(title, (SCREEN_SIZE // 2 - title.get_width() // 2, 30))

        button_width = 200
        button_height = 50

        self.easy_button = Button(SCREEN_SIZE // 2 - button_width // 2, 150, button_width, button_height, "Легко", GREEN, BLACK)
        self.hard_button = Button(SCREEN_SIZE // 2 - button_width // 2, 230, button_width, button_height, "Сложно", RED, BLACK)

        self.easy_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        pygame.display.update()

        self.wait_for_difficulty()

    def wait_for_difficulty(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.easy_button.is_clicked(event):
                    self.difficulty = 'easy'
                    waiting = False
                if self.hard_button.is_clicked(event):
                    self.difficulty = 'hard'
                    waiting = False

        self.choose_symbol()

    def choose_symbol(self):
        self.screen.fill(WHITE)
        font = pygame.font.Font(None, 50)
        text = font.render('Выберите символ', True, BLACK)
        self.screen.blit(text, (SCREEN_SIZE // 2 - text.get_width() // 2, 30))

        button_width = 200
        button_height = 50

        self.x_button = Button(SCREEN_SIZE // 2 - button_width // 2, 150, button_width, button_height, "Крестик", BLUE, WHITE)
        self.o_button = Button(SCREEN_SIZE // 2 - button_width // 2, 230, button_width, button_height, "Нолик", RED, WHITE)

        self.x_button.draw(self.screen)
        self.o_button.draw(self.screen)
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.x_button.is_clicked(event):
                    self.player_symbol = 'X'
                    self.ai_symbol = 'O'
                    waiting = False
                if self.o_button.is_clicked(event):
                    self.player_symbol = 'O'
                    self.ai_symbol = 'X'
                    waiting = False

        self.human = HumanPlayer(self.player_symbol)
        self.ai = AIPlayer(self.ai_symbol, difficulty=self.difficulty)
        self.draw_grid()

    def draw_grid(self):
        for row in range(1, GRID_SIZE):
            pygame.draw.line(self.screen, BLACK, (0, row * CELL_SIZE), (SCREEN_SIZE, row * CELL_SIZE), LINE_WIDTH)
            pygame.draw.line(self.screen, BLACK, (row * CELL_SIZE, 0), (row * CELL_SIZE, SCREEN_SIZE), LINE_WIDTH)

    def draw_figures(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.game.board[row][col] == 'X':
                    pygame.draw.line(self.screen, BLUE, (col * CELL_SIZE + OFFSET, row * CELL_SIZE + OFFSET),
                                     (col * CELL_SIZE + CELL_SIZE - OFFSET, row * CELL_SIZE + CELL_SIZE - OFFSET), CROSS_WIDTH)
                    pygame.draw.line(self.screen, BLUE, (col * CELL_SIZE + OFFSET, row * CELL_SIZE + CELL_SIZE - OFFSET),
                                     (col * CELL_SIZE + CELL_SIZE - OFFSET, row * CELL_SIZE + OFFSET), CROSS_WIDTH)
                elif self.game.board[row][col] == 'O':
                    pygame.draw.circle(self.screen, RED, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), RADIUS, CIRCLE_WIDTH)

    def animate_move(self, row, col, player):
        for size in range(0, RADIUS, 5):
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_figures()
            if player == 'O':
                pygame.draw.circle(self.screen, RED, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), size, CIRCLE_WIDTH)
            else:
                pygame.draw.line(self.screen, BLUE, (col * CELL_SIZE + OFFSET, row * CELL_SIZE + OFFSET),
                                 (col * CELL_SIZE + CELL_SIZE - OFFSET, row * CELL_SIZE + CELL_SIZE - OFFSET), size)
                pygame.draw.line(self.screen, BLUE, (col * CELL_SIZE + OFFSET, row * CELL_SIZE + CELL_SIZE - OFFSET),
                                 (col * CELL_SIZE + CELL_SIZE - OFFSET, row * CELL_SIZE + OFFSET), size)
            pygame.display.update()
            pygame.time.delay(50)

    def display_result(self, message):
        self.screen.fill(WHITE)
        font = pygame.font.Font(None, 50)
        result_text = font.render(message, True, BLACK)
        self.screen.blit(result_text, (SCREEN_SIZE // 2 - result_text.get_width() // 2, 30))

        button_width = 200
        button_height = 50

        self.restart_button = Button(SCREEN_SIZE // 2 - button_width // 2, 150, button_width, button_height, "Заново",
                                     GREEN, BLACK)
        self.main_menu_button = Button(SCREEN_SIZE // 2 - button_width // 2, 230, button_width, button_height,
                                       "Выйти в меню", GRAY, BLACK)

        self.restart_button.draw(self.screen)
        self.main_menu_button.draw(self.screen)
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.restart_button.is_clicked(event):
                    self.game.reset()
                    self.draw_grid()
                    self.draw_figures()  # Ensure that figures are drawn correctly after reset
                    pygame.display.update()
                    waiting = False
                if self.main_menu_button.is_clicked(event):
                    # Reset game state and return to main menu
                    self.game.reset()
                    self.human = None
                    self.ai = None
                    self.player_symbol = 'X'
                    self.ai_symbol = 'O'
                    self.difficulty = 'easy'
                    self.main_menu()  # Go back to the main menu
                    waiting = False

    def mainloop(self):
        player = self.player_symbol
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and player == self.player_symbol:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]

                    clicked_row = mouseY // CELL_SIZE
                    clicked_col = mouseX // CELL_SIZE

                    if self.game.make_move(clicked_row, clicked_col, player):
                        self.animate_move(clicked_row, clicked_col, player)
                        if self.game.current_winner:
                            self.display_result(f'{player} победил!')
                            player = self.player_symbol
                            continue
                        player = self.ai_symbol

            if player == self.ai_symbol and not self.game.is_full():
                row, col = self.ai.get_move(self.game)
                self.game.make_move(row, col, player)
                self.animate_move(row, col, player)
                if self.game.current_winner:
                    self.display_result(f'{player} победил!')
                    player = self.player_symbol
                    continue
                player = self.player_symbol

            if self.game.is_full() and not self.game.current_winner:
                self.display_result('Ничья!')
                player = self.player_symbol

            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_figures()
            pygame.display.update()

if __name__ == '__main__':
    game = GameInterface()
    game.mainloop()
