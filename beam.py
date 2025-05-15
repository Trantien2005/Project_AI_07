import heapq
import copy
import time
from needed_function import find_player, state_key, is_goal_state, next_states, find_boxes, heuristic

def beam_search(initial_grid, goals, beam_width=100):
    """
    Giải Sokoban bằng Beam Search.
    Input:
        - initial_grid: list[list[str]] - bản đồ ban đầu.
        - goals: list[tuple[int, int]] - vị trí đích.
        - beam_width: int - số lượng node được giữ lại mỗi tầng.
    Output:
        - tuple (list trạng thái dẫn đến goal, dict thông tin) hoặc (None, dict thông tin).
    """
    start_time = time.time()
    expanded_nodes = 0
    generated_nodes = 1
    max_depth = 0  # Theo dõi độ sâu lớn nhất đạt được

    player_pos = find_player(initial_grid)
    if not player_pos:
        print("Không tìm thấy người chơi")
        return None, {
            "expanded": 0,
            "generated": 0,
            "time": 0.0,
            "depth": 0,
            "beam_width": beam_width,
            "result": "No player found."
        }

    initial_boxes = find_boxes(initial_grid)
    initial_h = heuristic(initial_grid, initial_boxes, goals)
    initial_state = (initial_h, 0, initial_grid, player_pos, [copy.deepcopy(initial_grid)])
    
    current_level = [initial_state]
    visited = {state_key(initial_grid, player_pos)}

    while current_level:
        next_level = []

        # Mở rộng các node ở tầng hiện tại
        for h, g, grid, player_pos, states in current_level:
            expanded_nodes += 1
            if is_goal_state(grid, goals):
                end_time = time.time()
                info = {
                    "expanded": expanded_nodes,
                    "generated": generated_nodes,
                    "time": round(end_time - start_time, 4),
                    "depth": g,
                    "beam_width": beam_width
                }
                print(f"Tìm thấy lời giải sau {g} bước")
                return states, info

            for new_grid, new_player_pos, new_states in next_states(grid, player_pos, states, goals):
                new_key = state_key(new_grid, new_player_pos)
                if new_key not in visited:
                    visited.add(new_key)
                    new_g = g + 1
                    new_boxes = find_boxes(new_grid)
                    new_h = heuristic(new_grid, new_boxes, goals)
                    next_level.append((new_h, new_g, new_grid, new_player_pos, new_states))
                    generated_nodes += 1

            # Cập nhật độ sâu lớn nhất
            max_depth = max(max_depth, g)

        # Chọn beam_width trạng thái tốt nhất cho tầng tiếp theo
        current_level = heapq.nsmallest(beam_width, next_level, key=lambda x: x[0])
    
    # Nếu không tìm thấy lời giải, trả về info với thông tin thống kê
    end_time = time.time()
    info = {
        "expanded": expanded_nodes,
        "generated": generated_nodes,
        "time": round(end_time - start_time, 4),
        "depth": max_depth,
        "beam_width": beam_width,
        "result": "No solution found."
    }
    print("Không tìm thấy lời giải")
    return None, info