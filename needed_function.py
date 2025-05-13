from collections import deque
import copy

# Định nghĩa hướng di chuyển
MOVES = {
    'U': (-1, 0),  # Lên
    'D': (1, 0),   # Xuống
    'L': (0, -1),  # Trái
    'R': (0, 1)    # Phải
}
def heuristic(grid, boxes, goals):
    """
    Ước lượng chi phí từ trạng thái hiện tại đến mục tiêu.
    Input: boxes (list[tuple]), goals (list[tuple]).
    Output: float (tổng khoảng cách Manhattan tối thiểu).
    """
    if not boxes or not goals:
        return 0
    penalty = 0
    total_distance = 0
    used_goals = set()
    # Tính khoảng cách Manhattan tối thiểu từ mỗi thùng đến goal gần nhất
    for box in boxes:
        min_distance = float('inf')
        best_goal = None
        for goal in goals:
            if goal in used_goals:
                continue
            distance = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            if distance < min_distance:
                min_distance = distance
                best_goal = goal
        if best_goal:
            used_goals.add(best_goal)
            total_distance += min_distance
    return total_distance + penalty

# 1. Tìm vị trí người chơi
def find_player(grid):
    """
    Tìm tọa độ (x, y) của 'P' trong lưới.
    Input: grid (list[list[str]]).
    Output: tuple (x, y) hoặc None nếu không tìm thấy.
    """
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == 'P':
                return i, j
    return None

# 2. Tìm vị trí các thùng
def find_boxes(grid):
    """
    Tìm tất cả tọa độ của '@' trong lưới.
    Input: grid (list[list[str]]).
    Output: list[tuple] chứa các (x, y).
    """
    boxes = []
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == '@':
                boxes.append((i, j))
    return boxes

# 3. Kiểm tra trạng thái thắng
def is_goal_state(grid, goals):
    """
    Kiểm tra xem tất cả goal trong goals có chứa '@' không.
    Input: grid (list[list[str]]), goals (list[tuple]).
    Output: bool (True nếu thắng).
    """
    for x, y in goals:
        if grid[x][y] != '@':
            return False
    return True

# 4. Tạo khóa trạng thái
def state_key(grid, player_pos):
    """
    Tạo khóa duy nhất cho trạng thái (lưới + vị trí người chơi).
    Input: grid (list[list[str]]), player_pos (tuple).
    Output: str.
    """
    # Chỉ lấy các hàng/cột có ký tự liên quan để giảm kích thước
    grid_str = ''.join(''.join(cell for cell in row) for row in grid)
    return f"{grid_str}|{player_pos[0]},{player_pos[1]}"

# 5. Kiểm tra di chuyển hợp lệ
def can_move(grid, x, y, direction):
    """
    Kiểm tra xem người chơi tại (x, y) có thể di chuyển theo direction không.
    Input: grid, x, y (vị trí người chơi), direction ('U', 'D', 'L', 'R').
    Output: bool.
    """
    dx, dy = MOVES[direction]
    nx, ny = x + dx, y + dy

    # Kiểm tra biên
    if nx < 0 or ny < 0 or nx >= len(grid) or ny >= len(grid[0]):
        return False
    
    # Kiểm tra tường
    if grid[nx][ny] == '#':
        return False

    # Kiểm tra đẩy thùng
    if grid[nx][ny] == '@':
        nnx, nny = nx + dx, ny + dy
        if nnx < 0 or nny < 0 or nnx >= len(grid) or nny >= len(grid[0]):
            return False
        if grid[nnx][nny] in ['#', '@']:
            return False
    return True

# 6. Thực hiện di chuyển
def make_move(grid, player_pos, direction, goals):
    """
    Thực hiện di chuyển và trả về lưới mới.
    Input: grid, direction ('U', 'D', 'L', 'R'), goals (list[tuple]).
    Output: tuple (new_grid, new_player_pos) hoặc None nếu không hợp lệ.
    """
    x, y = player_pos

    if not can_move(grid, x, y, direction):
        return None

    new_grid = copy.deepcopy(grid)
    dx, dy = MOVES[direction]
    nx, ny = x + dx, y + dy

    # Nếu đẩy thùng
    if new_grid[nx][ny] == '@':
        nnx, nny = nx + dx, ny + dy
        new_grid[nnx][nny] = '@'
        new_grid[nx][ny] = 'P'
    else:
        new_grid[nx][ny] = 'P'

    # Cập nhật vị trí cũ của người chơi
    new_grid[x][y] = '1' if (x, y) in goals else ' '

    return new_grid, (nx, ny)
def is_stuck(grid, boxes, goals):
    """
    Kiểm tra thùng có kẹt ở góc không    
    Input: grid (list[list[str]]), boxes (list[tuple]), goals (list[tuple]).
    """
    rows, cols = len(grid), len(grid[0])

    for box in boxes:
        x, y = box

        # Nếu box đang ở goal thì bỏ qua
        if (x, y) in goals:
            continue

        wall_up = (x-1 < 0) or grid[x-1][y] == '#'
        wall_down = (x+1 >= rows) or grid[x+1][y] == '#'
        wall_left = (y-1 < 0) or grid[x][y-1] == '#'
        wall_right = (y+1 >= cols) or grid[x][y+1] == '#'

        # 1. Corner deadlock
        if (wall_up and wall_left) or (wall_up and wall_right) or \
           (wall_down and wall_left) or (wall_down and wall_right):
            return True
    return False
# 7. Tạo trạng thái kế tiếp
def next_states(grid, player_pos, prev_states, goals):
    """
    Tạo tất cả trạng thái kế tiếp từ trạng thái hiện tại.
    Input: grid, player_pos (tuple), prev_states (list), goals (list[tuple]).
    Output: list[tuple(grid, player_pos, states)].
    """
    successors = []
    for direction in MOVES:
        result = make_move(grid,player_pos, direction, goals)
        if result:
            new_grid, new_player_pos = result
            new_boxes = find_boxes(new_grid)
            if new_boxes != find_boxes(grid) and is_stuck(new_grid, new_boxes, goals):
                continue
            new_states = prev_states + [new_grid]
            successors.append((new_grid, new_player_pos, new_states))
    return successors


