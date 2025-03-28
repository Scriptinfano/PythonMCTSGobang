import pygame
import sys
from pythonmctsgobang.globals import *
from pythonmctsgobang.publictool import posIsValid
from pythonmctsgobang.point import Point

# 初始化 pygame
pygame.init()

# 窗口参数
GRID_SIZE = 40  # 棋盘格子大小
BOARD_SIZE = 16  # 棋盘大小（16x16）
MARGIN = 50  # 边距
WINDOW_SIZE = GRID_SIZE * (BOARD_SIZE - 1) + 2 * MARGIN

# 颜色
CHESSBOARD_COLOR = (222, 184, 135)  # 棋盘颜色
GRID_COLOR = (0, 0, 0)  # 网格线颜色
HINT_COLOR = (100, 100, 100)  # 鼠标悬停提示点颜色
BLACK_CHESS = (0, 0, 0)  # 黑棋
WHITE_CHESS = (255, 255, 255)  # 白棋

# 创建窗口
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("五子棋人机对战")

# 记录棋盘状态，0 为空，1 为黑棋（人类），2 为白棋（AI）
board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
current_turn = 1  # 1：人类，2：AI

# 提示点坐标
hint_pos = None


def draw_board():
    screen.fill(CHESSBOARD_COLOR)
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, GRID_COLOR,
                         (MARGIN, MARGIN + i * GRID_SIZE),
                         (MARGIN + (BOARD_SIZE - 1) * GRID_SIZE, MARGIN + i * GRID_SIZE), 1)
        pygame.draw.line(screen, GRID_COLOR,
                         (MARGIN + i * GRID_SIZE, MARGIN),
                         (MARGIN + i * GRID_SIZE, MARGIN + (BOARD_SIZE - 1) * GRID_SIZE), 1)


def draw_pieces():
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 1:
                pygame.draw.circle(screen, BLACK_CHESS,
                                   (MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE), 15)
            elif board[i][j] == -1:
                pygame.draw.circle(screen, WHITE_CHESS,
                                   (MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE), 15)

def random_move():
    """
    随机落子策略
    """
    import random
    empty_pos = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if board[i][j] == 0]
    if empty_pos:
        return random.choice(empty_pos)
    return None
def ai_move():
    """
    AI 执行落子决策，你可以在这里调用 MCTS 代码
    """
    from pythonmctsgobang.mcts import MCTS
    from pythonmctsgobang.publictool import checkWin
    import copy

    # 生成当前状态的 state 数组
    current_state = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != 0:
                current_state.append(Point(board[i][j], i, j))

    # 运行 MCTS 选择最优落子点
    # mcts = MCTS()
    # best_move = mcts.iteration(current_state,-1)
    best_move = random_move()

    if best_move:
        board[best_move[0]][best_move[1]] = -1 #AI 落子
        return best_move[0], best_move[1]
    return None


def game_loop():
    global hint_pos, current_turn
    running = True
    while running:
        draw_board()
        draw_pieces()

        # 画鼠标悬停提示点
        if hint_pos:
            pygame.draw.circle(screen, HINT_COLOR, hint_pos, 5)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                col = round((x - MARGIN) / GRID_SIZE)
                row = round((y - MARGIN) / GRID_SIZE)
                if posIsValid(row, col):
                    hint_pos = (MARGIN + col * GRID_SIZE,
                                MARGIN + row * GRID_SIZE)
                else:
                    hint_pos = None
            elif event.type == pygame.MOUSEBUTTONDOWN and current_turn == 1:
                x, y = event.pos
                col = round((x - MARGIN) / GRID_SIZE)
                row = round((y - MARGIN) / GRID_SIZE)
                if posIsValid(row, col) and board[row][col] == 0:
                    board[row][col] = 1  # 人类落子
                    current_turn = 2
                    # AI 落子
                    ai_pos = ai_move()
                    if ai_pos:
                        current_turn = 1
    pygame.quit()
    sys.exit()
