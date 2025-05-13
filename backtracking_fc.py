import time
from needed_function import find_player, state_key, is_goal_state, next_states, heuristic, is_stuck, find_boxes
import copy

def backtracking_fc(initial_grid, goals, max_depth=120):  # Tăng từ 80 lên 120
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

    initial_state = (initial_grid, player_pos, [copy.deepcopy(initial_grid)])
    visited = {state_key(initial_grid, player_pos)}
    expanded_nodes = [0]
    generated_nodes = [1]

    def backtrack(state, depth):
        if time.time() - start_time > 30:  # Giới hạn 10 giây
            print("Timeout: Dừng Backtracking FC sau 10 giây")
            return None
        grid, player_pos, states = state
        expanded_nodes[0] += 1

        if is_goal_state(grid, goals):
            return states

        if depth >= max_depth:
            return None

        successors = []
        for new_grid, new_player_pos, new_states in next_states(grid, player_pos, states, goals):
            new_key = state_key(new_grid, new_player_pos)
            if new_key in visited:
                continue

            new_boxes = find_boxes(new_grid)
            if is_stuck(new_grid, new_boxes, goals):
                continue

            h = heuristic(new_grid, new_boxes, goals)
            successors.append((h, new_grid, new_player_pos, new_states))
            generated_nodes[0] += 1

        successors.sort(key=lambda x: x[0])

        for _, new_grid, new_player_pos, new_states in successors:
            new_key = state_key(new_grid, new_player_pos)
            visited.add(new_key)
            result = backtrack((new_grid, new_player_pos, new_states), depth + 1)
            visited.remove(new_key)
            if result is not None:
                return result

        return None

    result = backtrack(initial_state, 0)
    end_time = time.time()

    if result is not None:
        info = {
            "expanded": expanded_nodes[0],
            "generated": generated_nodes[0],
            "time": round(end_time - start_time, 4),
            "depth": len(result) - 1
        }
        print(f"Tìm thấy lời giải sau {len(result) - 1} bước")
        return result, info
    else:
        info = {
            "expanded": expanded_nodes[0],
            "generated": generated_nodes[0],
            "time": round(end_time - start_time, 4),
            "depth": 0,
            "result": "No solution found."
        }
        print("Không tìm thấy lời giải")
        return None, info