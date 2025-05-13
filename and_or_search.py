import copy
import time
from needed_function import find_player, state_key, is_goal_state, next_states, find_boxes, heuristic, is_stuck

def and_or_search(initial_grid, goals, max_depth=100):
    """
    Giải Sokoban bằng And-Or Search.
    Input:
        - initial_grid: list[list[str]] - bản đồ ban đầu.
        - goals: list[tuple[int, int]] - vị trí đích.
        - max_depth: int - giới hạn độ sâu tìm kiếm.
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

    # Khởi tạo
    expanded_nodes = [0]  # Dùng list để cập nhật trong hàm đệ quy
    generated_nodes = [1]
    visited = set()  # Lưu các trạng thái đã thăm

    def solve_or(grid, player_pos, states, g, depth):
        """
        Hàm xử lý node OR: chọn hành động tốt nhất từ trạng thái hiện tại.
        """
        nonlocal expanded_nodes, generated_nodes
        expanded_nodes[0] += 1

        if depth > max_depth:
            return None

        if is_goal_state(grid, goals):
            return states

        key = state_key(grid, player_pos)
        if key in visited:
            return None

        visited.add(key)
        # Lấy các trạng thái con
        successors = next_states(grid, player_pos, states, goals)
        # Sắp xếp theo heuristic để ưu tiên trạng thái tiềm năng
        successor_list = []
        for new_grid, new_player_pos, new_states in successors:
            new_boxes = find_boxes(new_grid)
            if is_stuck(new_grid, new_boxes, goals):
                continue  # Bỏ qua trạng thái kẹt
            new_h = heuristic(new_grid, new_boxes, goals)
            new_g = g + 1
            new_f = new_g + new_h
            successor_list.append((new_f, new_g, new_grid, new_player_pos, new_states))
            generated_nodes[0] += 1

        # Thử từng trạng thái con (node AND)
        successor_list.sort(key=lambda x: x[0])  # Sắp xếp theo f(n)
        for f, new_g, new_grid, new_player_pos, new_states in successor_list:
            result = solve_and(new_grid, new_player_pos, new_states, new_g, depth + 1)
            if result is not None:
                return result
        return None

    def solve_and(grid, player_pos, states, g, depth):
        """
        Hàm xử lý node AND: giải quyết trạng thái con.
        Trong Sokoban, mỗi hành động dẫn đến 1 trạng thái, nên node AND đơn giản.
        """
        return solve_or(grid, player_pos, states, g, depth)

    # Chạy thuật toán
    result = solve_or(initial_grid, player_pos, [copy.deepcopy(initial_grid)], 0, 0)
    end_time = time.time()
    info = {
        "expanded": expanded_nodes[0],
        "generated": generated_nodes[0],
        "time": round(end_time - start_time, 4),
        "depth": len(result) - 1 if result else 0,
        "result": "Solution found." if result else "No solution found."
    }

    if result:
        print(f"Tìm thấy lời giải sau {len(result) - 1} bước")
        return result, info
    else:
        print("Không tìm thấy lời giải")
        return None, info