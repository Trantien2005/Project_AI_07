import copy
import random
import time
import numpy as np
from needed_function import find_player, state_key, is_goal_state, next_states, find_boxes, heuristic, MOVES, is_stuck

def q_learning(initial_grid, goals, episodes=5000, alpha=0.1, gamma=0.95, epsilon=0.2):
    """
    Giải Sokoban bằng Q-learning.
    Input:
        - initial_grid: list[list[str]] - bản đồ ban đầu.
        - goals: list[tuple[int, int]] - vị trí đích.
        - episodes: int - số lần thử nghiệm.
        - alpha: float - learning rate.
        - gamma: float - discount factor.
        - epsilon: float - exploration rate.
    Output:
        - tuple (list trạng thái dẫn đến goal, dict thông tin) hoặc (None, dict thông tin).
    """
    start_time = time.time()
    player_pos = find_player(initial_grid)
    if not player_pos:
        print("Không tìm thấy người chơi")
        return None, {
            "expanded": 0,
            "generated": 0,
            "time": 0.0,
            "depth": 0,
            "result": "No player found."
        }

    # Khởi tạo Q-table
    q_table = {}
    actions = list(MOVES.keys())  # ['U', 'D', 'L', 'R']
    expanded_nodes = 0
    generated_nodes = 1
    max_depth = 0

    def get_q_value(state, action):
        return q_table.get((state, action), 0.0)

    def choose_action(state, epsilon):
        if random.random() < epsilon:
            return random.choice(actions)
        q_values = [get_q_value(state, a) for a in actions]
        max_q = max(q_values)
        max_actions = [a for a, q in zip(actions, q_values) if q == max_q]
        return random.choice(max_actions)

    # Training loop
    solution_states = None
    for episode in range(episodes):
        if episode % 1000 == 0:
            print(f"Đang huấn luyện episode {episode}/{episodes}")
        grid = copy.deepcopy(initial_grid)
        player_pos = find_player(grid)
        states = [copy.deepcopy(grid)]
        step = 0
        max_steps = 1000  # Tăng giới hạn bước mỗi episode

        while step < max_steps:
            state = state_key(grid, player_pos)
            action = choose_action(state, epsilon)
            expanded_nodes += 1

            # Thực hiện hành động
            result = next_states(grid, player_pos, states, goals)
            move_dict = {}
            for ng, np, ns in result:
                for direction in MOVES:
                    if make_move(grid, player_pos, direction, goals) == (ng, np):
                        dx, dy = MOVES[direction]
                        move_dict[dx * 1000 + dy] = (ng, np, ns)

            dx, dy = MOVES[action]
            move_key = dx * 1000 + dy
            if move_key in move_dict:
                new_grid, new_player_pos, new_states = move_dict[move_key]
                new_boxes = find_boxes(new_grid)
                if is_stuck(new_grid, new_boxes, goals):
                    reward = -50  # Phạt nặng nếu kẹt
                else:
                    reward = -1  # Phạt nhẹ cho mỗi bước
                    generated_nodes += 1
            else:
                # Hành động không hợp lệ
                reward = -10
                new_grid = grid
                new_player_pos = player_pos
                new_states = states

            # Tính reward bổ sung dựa trên heuristic
            if is_goal_state(new_grid, goals):
                reward = 100
                solution_states = new_states
                print(f"Tìm thấy lời giải ở episode {episode} sau {len(new_states)-1} bước")
                break
            else:
                new_boxes = find_boxes(new_grid)
                h = heuristic(new_grid, new_boxes, goals)
                reward += -h * 0.01  # Khuyến khích giảm heuristic

            # Cập nhật Q-table
            new_state = state_key(new_grid, new_player_pos)
            next_q_values = [get_q_value(new_state, a) for a in actions]
            q_table[(state, action)] = get_q_value(state, action) + alpha * (
                reward + gamma * max(next_q_values) - get_q_value(state, action)
            )

            # Cập nhật trạng thái
            grid = new_grid
            player_pos = new_player_pos
            states = new_states
            step += 1
            max_depth = max(max_depth, len(states) - 1)

            # Giảm epsilon để giảm exploration
            epsilon = max(0.01, epsilon * 0.995)

        if solution_states:
            break

    end_time = time.time()
    info = {
        "expanded": expanded_nodes,
        "generated": generated_nodes,
        "time": round(end_time - start_time, 4),
        "depth": len(solution_states) - 1 if solution_states else 0,
        "episodes": episodes,
        "result": "Solution found." if solution_states else "No solution found."
    }

    if solution_states:
        print(f"Tìm thấy lời giải sau {len(solution_states) - 1} bước")
        return solution_states, info
    else:
        print("Không tìm thấy lời giải sau {} episodes".format(episodes))
        return None, info

def make_move(grid, player_pos, direction, goals):
    """
    Helper function to simulate a move (copied from needed_function for internal use).
    """
    x, y = player_pos
    dx, dy = MOVES[direction]
    nx, ny = x + dx, y + dy

    if nx < 0 or ny < 0 or nx >= len(grid) or ny >= len(grid[0]) or grid[nx][ny] == '#':
        return None

    new_grid = copy.deepcopy(grid)
    if new_grid[nx][ny] == '@':
        nnx, nny = nx + dx, ny + dy
        if nnx < 0 or nny < 0 or nnx >= len(grid) or nny >= len(grid[0]) or new_grid[nnx][nny] in ['#', '@']:
            return None
        new_grid[nnx][nny] = '@'
        new_grid[nx][ny] = 'P'
    else:
        new_grid[nx][ny] = 'P'

    new_grid[x][y] = '1' if (x, y) in goals else ' '
    return new_grid, (nx, ny)