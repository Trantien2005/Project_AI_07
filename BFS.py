from needed_function import find_player, state_key, is_goal_state, next_states
from collections import deque
import copy
import time
def bfs(initial_grid, goals):
    """
    Giải Sokoban bằng BFS, trả về danh sách trạng thái.
    Input: initial_grid (list[list[str]]), goals (list[tuple]).
    Output: list[list[list[str]]] hoặc None.
    """
    start_time = time.time()
    player_pos = find_player(initial_grid)
    if not player_pos:
        print("Không tìm thấy người chơi")
        return None

    initial_state = (initial_grid, player_pos, [copy.deepcopy(initial_grid)])
    queue = deque([initial_state])
    visited = {state_key(initial_grid, player_pos)}
    expanded_nodes = 0
    generated_nodes = 1
    while queue:
        grid, player_pos, states = queue.popleft()
        expanded_nodes += 1

        if is_goal_state(grid, goals):
            end_time = time.time()
            info = {
                "expanded": expanded_nodes,
                "generated": generated_nodes,
                "time": round(end_time - start_time, 4),
                "depth": len(states) - 1
            }
            print(f"Tìm thấy lời giải sau {len(states) - 1} bước")
            return states, info

        for new_grid, new_player_pos, new_states in next_states(grid, player_pos, states, goals):
            key = state_key(new_grid, new_player_pos)
            if key not in visited:
                visited.add(key)
                queue.append((new_grid, new_player_pos, new_states))
                generated_nodes += 1

    print("Không tìm thấy lời giải")
    end_time = time.time()
    info = {
                "expanded": expanded_nodes,
                "generated": generated_nodes,
                "time": round(end_time - start_time, 4),
                "depth": 0
            }
    return None, info
