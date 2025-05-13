#Các thư viện cần thiết
import pygame
import matplotlib.pyplot as plt
import sys
from PIL import Image
import os
import BFS
import a_star
import beam
import backtracking_fc
import q_learning  
import and_or_search  

#Khởi tạo Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((700, 700))
pygame.display.set_caption("Sokoban")
clock = pygame.time.Clock()
#Biến toàn cục
scene_state = "init"  # init, loading, executing, playing, end (Màn hình ban đầu là init)
algorithms = ["Breadth First Search", "A Star Search", "Beam Search", "Backtracking FC", "Q-Learning", "And-Or Search"] #Thuật toán để chọn
algorithm = algorithms[0]  # Thuật toán mặc định hiển thị ban đầu
map_number = 0
current_state = 0
state_length = 0    
found = False


#Tải hình ảnh
TILE_SIZE = 64  # Kích thước mỗi ô vuông
try:
    asset = 'Assets/'  # Đường dẫn đến thư mục chứa ảnh
    for file in os.listdir(asset):
        if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.gif'):
            background = pygame.image.load(os.path.join(asset, "900.jpg")) #Hình nền khởi động
            floor_img = pygame.image.load(os.path.join(asset, "164.jpg")).convert() #Nền đất
            box_img = pygame.image.load(os.path.join(asset, "box64.png")).convert_alpha() #Thùng hàng
            goal_img = pygame.image.load(os.path.join(asset, "hole64.png")).convert_alpha() #Đích
            player_img = pygame.image.load(os.path.join(asset, "player64.png")).convert_alpha() #Người chơi
            box_wall_img = pygame.image.load(os.path.join(asset, "364.png")).convert_alpha() #Tường
            arrow_left_img = pygame.image.load(os.path.join(asset, "56L.png")).convert_alpha() #Mũi tên trái để trang trí
            arrow_right_img = pygame.image.load(os.path.join(asset, "56R.png")).convert_alpha() #Mũi tên phải để trang trí
            loading_game_img = pygame.image.load(os.path.join(asset, "loading900.png")).convert_alpha() #Hình nền lúc tải game
            gif = Image.open(os.path.join(asset, "cat100.gif")) #gif mô phỏng load game
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    exit()

#Tải âm thanh
try:
    sound = 'Sound/'
    for file in os.listdir(sound):
        if file.endswith('.mp3') or file.endswith('.wav'):
            pygame.mixer.init()
            init = pygame.mixer.Sound(os.path.join(sound, "background.mp3")) #Nhạc nền
            loading = pygame.mixer.Sound(os.path.join(sound, "loading.mp3")) #Nhạc nền loading
            playing = pygame.mixer.Sound(os.path.join(sound, "playing.mp3")) #Nhạc nền lúc chạy animation
            change_algorithm = pygame.mixer.Sound(os.path.join(sound,"algorthm.wav")) #Âm thanh lúc đổi thuật toán
            click = pygame.mixer.Sound(os.path.join(sound, "arrowclick.wav")) #Âm thanh đổi map
    chanel = pygame.mixer.Channel(0)  # Tạo kênh âm thanh
except pygame.error as e:
    print(f"Error loading sound: {e}")
    pygame.quit()
    exit()
    
"""Quy ước:
# tường
" " khoảng trống
1 lỗ hỏng
P người chơi
@ thùng gỗ
"""
def load_all_maps(folder_path):
    """
    Đọc tất cả file .txt trong thư mục và trả về danh sách các bản đồ.
    Mỗi bản đồ là một list các dòng (str) từ nội dung file.
    """
    maps = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                maps.append(content.splitlines())
    return maps
map_path = 'Maps/' #Đường dẫn đến thư mục chứa bản đồ
maps = load_all_maps(map_path)

def load_checkpoints_from_folder(folder_path):
    """
    Đọc tất cả file trong folder checkpoint, trả về list các checkpoint.
    Mỗi checkpoint là một list các tuple (x, y) tương ứng với tọa độ của goal.
    """
    checkpoints = []

    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as f:
                points = []
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        x, y = map(int, parts)
                        points.append((x, y))
                checkpoints.append(points)
    return checkpoints
checkpoint_path = 'Checkpoints/' #Đường dẫn đến thư mục chứa các file checkpoint
checkpoints = load_checkpoints_from_folder(checkpoint_path)
def save_results_to_file(filename,results):
    with open(filename, 'a') as f:
        f.write("===== RESULTS =====\n")
        for algo_name, metrics in results.items():
            f.write(f"Algorithm: {algo_name}\n")
            for key, value in metrics.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

import tkinter as tk
from tkinter import scrolledtext
#Sử dụng tkinter làm cửa sổ hiển thị kết quả các thuật toán.
def show_result_window(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    result_window = tk.Tk()
    result_window.title("Kết quả so sánh thuật toán")
    result_window.geometry("500x400")

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both')
    text_area.insert(tk.END, content)
    text_area.configure(state='disabled')  # không cho sửa

    result_window.mainloop()

def render_map(map):
 
    tile_size = 64  
    bg_width = 700
    bg_height = 650

    width = len(map[0])
    height = len(map)

    # Tính tỉ lệ scale để map vừa nền
    scale_x = bg_width / (width * tile_size)
    scale_y = (bg_height - 250) / (height * tile_size)  # trừ phần trên là UI
    scale = min(scale_x, scale_y)

    # Căn giữa map
    total_map_width = width * tile_size * scale
    total_map_height = height * tile_size * scale
    offset_x = (bg_width - total_map_width) // 2
    offset_y = 240 + ((bg_height - 250 - total_map_height) // 2)

    for row in range(height):
        for col in range(width):
            tile = map[row][col]
            x = int(col * tile_size * scale + offset_x)
            y = int(row * tile_size * scale + offset_y)

            screen.blit(pygame.transform.scale(floor_img, (int(tile_size * scale), int(tile_size * scale))), (x, y))

            if tile == '#':
                screen.blit(pygame.transform.scale(box_wall_img, (int(tile_size * scale), int(tile_size * scale))), (x, y))
            elif tile == '@':
                screen.blit(pygame.transform.scale(box_img, (int(tile_size * scale), int(tile_size * scale))), (x, y))
            elif tile == '1':
                screen.blit(pygame.transform.scale(goal_img, (int(tile_size * scale), int(tile_size * scale))), (x, y))
            elif tile == 'P':
                screen.blit(pygame.transform.scale(player_img, (int(tile_size * scale), int(tile_size * scale))), (x, y))

# ==== Functions ====
def init_game(map_number):
    # Vẽ background
    #init.play(-1)# Phát nhạc nền
    #init.set_volume(0.5)# Giảm âm lượng nhạc nền
    screen.blit(background, (0, 0))

    # Title "Sokoban"
    # title_font = pygame.font.Font('C:/Users/Admin/Documents/Zalo Received Files/AIProject (2)/AIProject/Font/VT.ttf', 160)
    # title_text = title_font.render('Sokoban', True, (255, 215, 0))
    # title_rect = title_text.get_rect(center=(350, 80))
    # screen.blit(title_text, title_rect)

    # Description text
    # desc_font = pygame.font.Font('C:/Users/Admin/Documents/Zalo Received Files/AIProject (2)/AIProject/Font/VT.ttf', 40)
    # desc_text = desc_font.render('SELECT YOUR MAP!', True, (255, 255, 255))
    # desc_rect = desc_text.get_rect(center=(350, 195))
    # screen.blit(desc_text, desc_rect)

    # Level display
    map_font = pygame.font.SysFont('Font/Poppins-Regular.ttf', 25)
    map_text = map_font.render(f"Map. {map_number + 1}", True, (255, 0, 0))
    map_rect = map_text.get_rect(center=(350, 230))
    screen.blit(map_text, map_rect)
    render_map(maps[map_number])
    
    screen.blit(arrow_left_img, (10, 450))  # Mũi tên trái
    screen.blit(arrow_right_img, (650, 450))  # Mũi tên phải
    
    algorithm_font = pygame.font.SysFont('Font/Poppins-Regular.ttf', 40)
    algorithm_text = algorithm_font.render(f"{algorithm}", True, (255, 0, 0))
    algorithm_rect = algorithm_text.get_rect(center=(350, 660))
    screen.blit(algorithm_text, algorithm_rect)
def loading_game():
    #loading.play(-1)  # Phát nhạc loading
    frames = []
    start_time = pygame.time.get_ticks()  # Thời gian bắt đầu loading
    screen.blit(loading_game_img, (0, 0))  # Vẽ hình loading
    loading_width = 250
    loading_height = 25
    loading_x = (700 - loading_width) // 2 + 130
    loading_y = (700 - loading_height) // 2 + 320
    font = pygame.font.Font("Font/VT.ttf", 70)
    text = font.render("Are you ready?", True, (255, 0, 0))
    text_rect = text.get_rect(center=(360, 200))
    screen.blit(text, text_rect)
    for i in range(gif.n_frames):
        gif.seek(i)
        frame = gif.convert("RGBA")  # Chuyển đổi sang định dạng RGBA
        framee = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
        frames.append(framee)
    frame_rate = 10
    frame_count = 0
    clokc = pygame.time.Clock()
    running = True
    while running:
        screen.blit(loading_game_img, (0, 0))  # Vẽ hình loading
        screen.blit(frames[frame_count], (425, 590))  # Vẽ hình loading
        screen.blit(text, text_rect)
        if pygame.time.get_ticks() % frame_rate == 0:
            frame_count = (frame_count + 1) % len(frames)
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time < 3000:
            loading_progress = (elapsed_time / 3000) * loading_width
            pygame.draw.rect(screen, (255,230,255), (loading_x, loading_y, loading_width, loading_height))
            pygame.draw.rect(screen, (200,200,70), (loading_x, loading_y, loading_progress, loading_height))
        else:
            # Thanh loading đã đầy
            pygame.draw.rect(screen, (255,230,255), (loading_x, loading_y, loading_width, loading_height))
            pygame.draw.rect(screen, (200,200,70), (loading_x, loading_y, loading_width, loading_height))
            running = False  # Kết thúc vòng lặp loading
        pygame.display.flip()
        clokc.tick(60)  # FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.time.wait(100)  
def end_game(found, list_board):
    screen.blit(background, (0, 0))
    render_map(list_board)
    font = pygame.font.Font('Font/VT.ttf', 70)
    if found:
        text = font.render("YOU WIN!", True, (0, 128, 0))
    else:
        text = font.render("YOU LOSE!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(350, 350))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(1000)  # Chờ 1 giây trước khi thoát
    
from copy import deepcopy
# ==== Main Game Loop ====
running = True
while running:
    screen.fill((0, 0, 0))

    if scene_state == "init":
        init_game(map_number)
    elif scene_state == "loading":
        #init.stop()  # Dừng nhạc nền
        scene_state = "executing"
        loading_game()
        #loading.stop()  # Dừng nhạc loading
    elif scene_state == "executing":
        if algorithm == "Breadth First Search":
            grid = [list(row) for row in maps[map_number]]
            list_board, res = BFS.bfs(deepcopy(grid), checkpoints[map_number])
        elif algorithm == "A Star Search":
            grid = [list(row) for row in maps[map_number]]
            list_board, res = a_star.a_star(deepcopy(grid), checkpoints[map_number])
        elif algorithm == "Beam Search":
            grid = [list(row) for row in maps[map_number]]
            list_board, res = beam.beam_search(deepcopy(grid), checkpoints[map_number])
        elif algorithm == "Backtracking FC":  # Thêm điều kiện cho thuật toán mới
            grid = [list(row) for row in maps[map_number]]
            list_board, res = backtracking_fc.backtracking_fc(deepcopy(grid), checkpoints[map_number])
        elif algorithm == "Q-Learning":
            grid = [list(row) for row in maps[map_number]]
            list_board, res = q_learning.q_learning(deepcopy(grid), checkpoints[map_number])
        elif algorithm == "And-Or Search":
            grid = [list(row) for row in maps[map_number]]
            list_board, res = and_or_search.and_or_search(deepcopy(grid), checkpoints[map_number])
        if list_board:
            filename = f"Compare/{map_number + 1}.txt"
            save_results_to_file(filename, {f"{algorithm}": res})
            state_length = len(list_board)
            current_state = 0
            found = True
            scene_state = "playing"
        else:
            res["result"] = "No solution found."
            filename = f"Compare/{map_number + 1}.txt"
            save_results_to_file(filename, {f"{algorithm}": res})
            found = False
            state_length = 0
            current_state = 0
            scene_state = "end"
    elif scene_state == "playing":
        #playing.play(-1)
        if current_state < state_length:
            screen.blit(background, (0, 0))
            render_map(list_board[current_state])
            current_state += 1
            clock.tick(2)  # 2 FPS playback
        else:
            scene_state = "end"
    elif scene_state == "end":
        #playing.stop()
        if list_board:
            end_game(found, list_board[-1])
        else:
            end_game(found, maps[map_number])

    # ==== Event Handling ====
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and scene_state == "init":
                map_number = (map_number + 1) 
                chanel.play(click)  # Phát âm thanh click
                if map_number >= len(maps):
                    map_number = 0
                init_game(map_number)
            if event.key == pygame.K_LEFT and scene_state == "init":
                map_number = (map_number - 1) 
                chanel.play(click)
                if map_number < 0:
                    map_number = len(maps) - 1
                init_game(map_number)
            if event.key == pygame.K_SPACE and scene_state == "init":
                chanel.play(change_algorithm)
                algorithm = algorithms[(algorithms.index(algorithm) + 1) % len(algorithms)]
            if event.key == pygame.K_RETURN:
                if scene_state  == "init":
                    scene_state = "loading"
                elif scene_state == 'end':
                    scene_state = "init"
                    map_number = 0
                    found = False
                    current_state = 0
                    state_length = 0
                    list_board = []
                elif scene_state == 'playing':
                    scene_state = 'end'
            if event.key == pygame.K_ESCAPE:
                show_result_window(f"Compare/{map_number+1}.txt")
    pygame.display.flip()

pygame.quit()
sys.exit()
