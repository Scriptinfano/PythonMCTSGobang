import pygame
import sys
from pythonmctsgobang.globals import *
from pythonmctsgobang.publictool import posIsValid, checkWin
from pythonmctsgobang.point import Point
from pythonmctsgobang.mcts import MCTS,Node

# 以下全局代码将在模块被首次调用时全部执行
# 初始化 pygame
pygame.init()
# 创建窗口
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("五子棋人机对战")
# 记录棋盘状态，0 为空，1 为黑棋（人类），-1 为白棋（AI）
board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
current_turn = 1  # 1：人类，-1：AI
# 提示点坐标
hint_pos = None
root=None #MCTS树的根节点
def board_to_state(board: list) -> list:
    """将棋盘状态转换为 state 数组"""
    state = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != 0:
                state.append(Point(board[i][j], i, j))
    return state

def draw_board():
    """绘制棋盘"""
    screen.fill(CHESSBOARD_COLOR)
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen, GRID_COLOR,
                         (MARGIN, MARGIN + i * GRID_SIZE),
                         (MARGIN + (BOARD_SIZE - 1) * GRID_SIZE, MARGIN + i * GRID_SIZE), 1)
        pygame.draw.line(screen, GRID_COLOR,
                         (MARGIN + i * GRID_SIZE, MARGIN),
                         (MARGIN + i * GRID_SIZE, MARGIN + (BOARD_SIZE - 1) * GRID_SIZE), 1)


def draw_pieces():
    """绘制棋子"""
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 1:
                pygame.draw.circle(screen, BLACK_CHESS,
                                   (MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE), 15)
            elif board[i][j] == -1:
                pygame.draw.circle(screen, WHITE_CHESS,
                                   (MARGIN + j * GRID_SIZE, MARGIN + i * GRID_SIZE), 15)


def random_move():
    """随机落子策略"""
    import random
    empty_pos = [(i, j) for i in range(BOARD_SIZE)
                 for j in range(BOARD_SIZE) if board[i][j] == 0]
    if empty_pos:
        return random.choice(empty_pos)
    return None


def ai_move():
    global root
    """AI 执行落子决策（此处用随机策略，你可以换成 MCTS）"""
    # 生成当前状态的 state 数组
    current_state = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != 0:
                current_state.append(Point(board[i][j], i, j))

    # 运行 MCTS 选择最优落子点
    mcts = MCTS()
    best_move,newRoot = mcts.iteration(current_state,-1,root)
    newRoot.nowColor=-1
    newRoot.parent=None
    newRoot.state=board_to_state(board)
    # TODO newRoot.children 不确定是否更新
    root=newRoot #更新根节点，下一次调用iteration时，将从新根节点开始
    if best_move:
        board[best_move.x][best_move.y] = -1  # AI 落子
        return best_move
    else:
        node=Node(current_state,None,-1)
        s=node.getPossibleMoves()
        # 随机返回set集合s中的一个元素
        randmove=s.pop()
        while board[randmove[0]][randmove[1]]!=0:
            randmove=s.pop()
        board[randmove[0]][randmove[1]]=-1
        return s.pop() if s else None

def check_winner():
    """检查是否有人获胜"""
    class Node:
        """创建一个临时 Node 结构，用于 checkWin()"""
        def __init__(self, state):
            self.state = state
    # 转换当前棋盘状态为 `state` 格式
    current_state = board_to_state(board)
    node = Node(current_state)
    # 调用 checkWin() 判断是否有胜者
    if checkWin(node):
        return True
    return False


def show_winner_dialog(winner):
    """弹出提示框显示胜者"""
    pygame.time.delay(500)  # 等待 500ms，避免误触
    font_path = "/System/Library/Fonts/Supplemental/Songti.ttc"  # 确保路径正确
    font = pygame.font.Font(font_path, 40)
    message = "你赢了！" if winner == 1 else "AI 赢了！"

    # 绘制半透明遮罩
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    overlay.set_alpha(180)  # 设置透明度
    overlay.fill((50, 50, 50))  # 灰色背景
    screen.blit(overlay, (0, 0))

    # 绘制文本
    text_surface = font.render(message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(
        center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 20))
    screen.blit(text_surface, text_rect)

    # 绘制按钮
    button_rect = pygame.Rect(WINDOW_SIZE // 2 - 50,
                              WINDOW_SIZE // 2 + 20, 100, 40)
    pygame.draw.rect(screen, (200, 0, 0), button_rect)
    button_text = font.render("确定", True, (255, 255, 255))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

    pygame.display.flip()

    # 等待玩家点击按钮
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False


def reset_game():
    """重新初始化游戏"""
    global board, current_turn,root
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    root=None
    
    current_turn = 1


def game_loop():
    """游戏主循环"""
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
                if posIsValid(row, col,board_to_state(board)):
                    hint_pos = (MARGIN + col * GRID_SIZE,
                                MARGIN + row * GRID_SIZE)
                else:
                    hint_pos = None
            elif event.type == pygame.MOUSEBUTTONDOWN and current_turn == 1:
                x, y = event.pos
                col = round((x - MARGIN) / GRID_SIZE)
                row = round((y - MARGIN) / GRID_SIZE)
                if posIsValid(row, col,board_to_state(board)) and board[row][col] == 0:
                    board[row][col] = 1  # 人类落子
                    if check_winner():
                        show_winner_dialog(1)
                        reset_game()
                        continue

                    current_turn = -1  # AI 回合
                    ai_pos = ai_move()
                    if ai_pos and check_winner():
                        show_winner_dialog(-1)
                        reset_game()
                        continue

                    current_turn = 1  # 轮到人类
    pygame.quit()
    sys.exit()