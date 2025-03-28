from pythonmctsgobang.globals import *

def posIsValid(row, col) -> bool:
	return row >= 0 and row < BOARD_SIZE and col >= 0 and col < BOARD_SIZE


def checkWin(node) -> bool:
    """
    判断 node 所代表的状态是否是游戏的结束状态，即是否存在五子连珠。
    node.state 是一个列表，存储所有棋步，每个棋步包含 (x, y, color)。
    """
    # 构建棋盘（初始化为 0）
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    # 填充棋盘
    for p in node.state:
        board[p.x][p.y] = p.color

    # 方向数组：→、↘、↓、↙
    dx = [0, 1, 1, 1]
    dy = [1, 1, 0, -1]

    # 遍历棋盘上的每个点
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:  # 空位置跳过
                continue
            color = board[i][j]

            # 检查四个方向是否存在五连珠
            for k in range(4):
                # 确保整个 5 个连续点都在棋盘范围内
                if all(0 <= i + l * dx[k] < BOARD_SIZE and 0 <= j + l * dy[k] < BOARD_SIZE for l in range(5)):
                    # 检查 5 个点是否颜色一致
                    if all(board[i + l * dx[k]][j + l * dy[k]] == color for l in range(5)):
                        return True  # 发现五连珠，游戏结束
    return False  # 没有五连珠
