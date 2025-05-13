import heapq
import copy
from pympler import asizeof
from needed_function import find_player, state_key, is_goal_state, next_states, find_boxes, heuristic
import time
def a_star(initial_grid, goals):
    """
    Giải Sokoban bằng A*, trả về danh sách trạng thái.
    Input: initial_grid (list[list[str]]), goals (list[tuple]).
    Output: list[list[list[str]]] hoặc None.
    """
    start_time = time.time()
    expanded_nodes = 0
    generated_nodes = 1
    player_pos = find_player(initial_grid)
    if not player_pos:
        print("Không tìm thấy người chơi")
        return None

    # Hàng đợi ưu tiên: (f(n), g(n), grid, player_pos, states)
    # f(n) = g(n) + h(n), g(n) là số bước, h(n) là heuristic
    initial_boxes = find_boxes(initial_grid)
    initial_h = heuristic(initial_grid,initial_boxes, goals)
    initial_g = 0
    initial_f = initial_g + initial_h
    initial_state = (initial_f, initial_g, initial_grid, player_pos, [copy.deepcopy(initial_grid)])

    heap = [initial_state]
    heapq.heapify(heap)
    visited = {state_key(initial_grid, player_pos)}

    while heap:
        f, g, grid, player_pos, states = heapq.heappop(heap)
        expanded_nodes += 1
        if is_goal_state(grid, goals):
            end_time = time.time()
            info = {
                "expanded": expanded_nodes,
                "generated": generated_nodes,
                "time": round(end_time - start_time, 4),
                "depth": g
            }
            print(f"Tìm thấy lời giải sau {g} bước")
            return states, info

        for new_grid, new_player_pos, new_states in next_states(grid, player_pos, states, goals):
            new_key = state_key(new_grid, new_player_pos)
            if new_key not in visited:
                visited.add(new_key)
                generated_nodes += 1
                new_g = g + 1
                new_boxes = find_boxes(new_grid)
                new_h = heuristic(new_grid, new_boxes, goals)
                new_f = new_g + new_h
                heapq.heappush(heap, (new_f, new_g, new_grid, new_player_pos, new_states))

    print("Không tìm thấy lời giải")
    end_time = time.time()
    info = {
                "expanded": expanded_nodes,
                "generated": generated_nodes,
                "time": round(end_time - start_time, 4),
                "depth": 0
            }
    return None, info