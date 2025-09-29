from Board import Board
from Search import SearchAlgorithms
from UI import GameUI
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import Toplevel, ttk
from PIL import Image, ImageTk
import pygame
import json
import os


class PikachuGame:
    def __init__(self, root, rows=8, cols=12):  # Thêm tham số mặc định
        self.root = root
        self.root.title("Pikachu")
        self.rows, self.cols = rows, cols  # Sử dụng giá trị truyền vào
        self.cell_size = 60
        self.click_tolerance = 15  # Vùng click mở rộng xung quanh mỗi ô
        self.icons = self.load_icons("icons", 15)
        self.moves = 0
        self.time_elapsed = 0
        self.timer_running = False
        self.game_paused = False
        self.auto_running = False
        self.selected = []
        self.sound_enabled = True
        self.history_file = "history.json"
        self.highlighted_cells = []  # Danh sách các ô đang được highlight
        self.background_revealed = 0  # Số ô đã được xóa (để lộ background)
        self.fast_mode = False  # Chế độ tua nhanh

        pygame.mixer.init()
        self.sounds = {
            "bg": "sounds/bg_music.mp3",
            "select": "sounds/select.wav",
            "eat": "sounds/eat.wav",
            "win": "sounds/win.wav"
        }
        self.play_music_bg()

        self.board = Board(self.rows, self.cols, self.icons)
        self.ui = GameUI(root, self.rows, self.cols, self.cell_size)  # Sử dụng giao diện mới
        self.root.geometry("1000x1000")  # Đặt kích thước cửa sổ
        # board_width = self.cols * self.cell_size
        # board_height = self.rows * self.cell_size
        # ui_padding = 200
        # self.root.geometry(f"{board_width}x{board_height + ui_padding}")
        self.algorithms = SearchAlgorithms(self.board.board, self.rows, self.cols)

        self.ui.new_btn.config(command=self.new_game)
        self.ui.auto_btn.config(command=self.start_auto)
        self.ui.stop_btn.config(command=self.stop_game)
        self.ui.continue_btn.config(command=self.continue_game)
        self.ui.history_btn.config(command=self.show_history)
        self.ui.skip_btn.config(command=self.skip_current_pair)
        self.ui.fast_forward_btn.config(command=self.toggle_fast_mode)
        self.ui.canvas.bind("<Button-1>", self.on_canvas_click)
        self.ui.sound_var.trace("w", self.on_sound_toggle)

        self.image_ids = {}
        self.new_game()

    def play_music_bg(self):
        if self.sound_enabled:
            pygame.mixer.music.load(self.sounds["bg"])
            pygame.mixer.music.play(-1)

    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            pygame.mixer.Sound(self.sounds[name]).play()

    def on_sound_toggle(self, *args):
        self.sound_enabled = self.ui.sound_var.get()
        if not self.sound_enabled:
            pygame.mixer.music.stop()
        else:
            self.play_music_bg()

    def load_icons(self, folder, count):
        icons = {}
        for i in range(count):
            img = Image.open(f"{folder}/{i + 1}.png").resize((54, 54))
            icons[i] = ImageTk.PhotoImage(img)
        return icons

    def new_game(self):
        self.auto_running = False
        self.game_paused = False
        self.moves = 0
        self.time_elapsed = 0
        self.ui.moves_label.config(text="Moves: 0")
        self.ui.time_label.config(text="Time: 0s")
        self.selected = []
        self.clear_highlights()  # Clear highlights khi bắt đầu game mới
        self.background_revealed = 0  # Reset background revealed
        self.board.new_board()
        self.algorithms.board = self.board.board

        self.ui.canvas.delete("all")
        w, h = self.cols * self.cell_size, self.rows * self.cell_size
        for r in range(self.rows + 1):
            self.ui.canvas.create_line(0, r * self.cell_size, w, r * self.cell_size, fill="#ccc")
        for c in range(self.cols + 1):
            self.ui.canvas.create_line(c * self.cell_size, 0, c * self.cell_size, h, fill="#ccc")

        self.image_ids.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.cell_size + self.cell_size // 2
                y = r * self.cell_size + self.cell_size // 2
                icon = self.icons[self.board.board[r][c]]
                img_id = self.ui.canvas.create_image(x, y, image=icon)
                self.image_ids[(r, c)] = img_id

        # Reset background overlay
        if hasattr(self.ui, 'background_overlay'):
            self.ui.background_overlay.itemconfig(
                self.ui.overlay_rect,
                fill="#FFFFFF"
            )

        self.start_timer()

    def stop_game(self):
        self.game_paused = True
        self.stop_timer()
        self.auto_running = False

    def continue_game(self):
        if self.game_paused:
            self.game_paused = False
            self.start_timer()
            if self.ui.mode_var.get() == "Auto" and not self.auto_running:
                self.start_auto()

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def redraw_remaining_icons(self):
        # Update existing images or delete if removed
        for (r, c), img_id in list(self.image_ids.items()):
            if self.board.board[r][c] == -1:
                self.ui.canvas.delete(img_id)
                del self.image_ids[(r, c)]
            else:
                icon = self.icons[self.board.board[r][c]]
                self.ui.canvas.itemconfig(img_id, image=icon)

    def update_timer(self):
        if self.timer_running and not self.game_paused:
            self.ui.time_label.config(text=f"Time: {self.time_elapsed}s")
            self.time_elapsed += 1
            self.root.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def on_canvas_click(self, event):
        if self.game_paused:
            return
        if self.ui.mode_var.get() != "Manual":
            return

        # Tìm ô gần nhất với vùng click mở rộng
        clicked_cell = self.find_nearest_cell(event.x, event.y)
        if clicked_cell is None:
            return

        r, c = clicked_cell
        if self.board.board[r][c] != -1:
            # Clear previous highlights
            self.clear_highlights()

            # Add to selected and highlight
            self.selected.append((r, c))
            self.highlight_cell(r, c)
            self.play_sound("select")

            if len(self.selected) == 2:
                (r1, c1), (r2, c2) = self.selected
                if (r1, c1) == (r2, c2):
                    self.selected = []
                    self.clear_highlights()
                    return

                if self.board.board[r1][c1] == self.board.board[r2][c2]:
                    algo = self.ui.algo_var.get()
                    path = self.get_path((r1, c1), (r2, c2), algo)
                    if path:
                        self.draw_lightning(path)
                        self.root.after(350, lambda: self.remove_pair_and_check(r1, c1, r2, c2))
                    else:
                        self.selected = []
                        self.clear_highlights()
                else:
                    self.selected = []
                    self.clear_highlights()

    def find_nearest_cell(self, x, y):
        """Tìm ô gần nhất với vùng click mở rộng"""
        min_distance = float('inf')
        nearest_cell = None

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board.board[r][c] == -1:
                    continue

                # Tọa độ trung tâm của ô
                cell_center_x = c * self.cell_size + self.cell_size // 2
                cell_center_y = r * self.cell_size + self.cell_size // 2

                # Khoảng cách từ điểm click đến trung tâm ô
                distance = ((x - cell_center_x) ** 2 + (y - cell_center_y) ** 2) ** 0.5

                # Nếu khoảng cách nhỏ hơn tolerance và là khoảng cách nhỏ nhất
                if distance <= self.click_tolerance and distance < min_distance:
                    min_distance = distance
                    nearest_cell = (r, c)

        return nearest_cell

    def highlight_cell(self, r, c):
        """Highlight ô được chọn với hiệu ứng đậm và đẹp"""
        x1 = c * self.cell_size + 3
        y1 = r * self.cell_size + 3
        x2 = (c + 1) * self.cell_size - 3
        y2 = (r + 1) * self.cell_size - 3

        # Tạo highlight rectangle với gradient effect
        highlight_id = self.ui.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#FFE066",  # Màu vàng đẹp hơn
            outline="#FF6B35",  # Viền cam đậm
            width=4,
            stipple="gray25"  # Hiệu ứng trong suốt nhẹ hơn
        )

        # Tạo thêm một viền ngoài để tạo hiệu ứng 3D
        outer_highlight = self.ui.canvas.create_rectangle(
            x1 - 2, y1 - 2, x2 + 2, y2 + 2,
            outline="#FF6B35",
            width=2,
            fill=""
        )

        # Đưa highlight xuống dưới icon
        self.ui.canvas.tag_lower(highlight_id)
        self.ui.canvas.tag_lower(outer_highlight)

        # Lưu ID để có thể xóa sau
        self.highlighted_cells.extend([highlight_id, outer_highlight])

    def clear_highlights(self):
        """Xóa tất cả highlight"""
        for highlight_id in self.highlighted_cells:
            self.ui.canvas.delete(highlight_id)
        self.highlighted_cells.clear()

    def update_background_overlay(self):
        """Cập nhật background overlay để lộ dần background phía sau"""
        # Kiểm tra nếu overlay tồn tại
        if self.ui.background_overlay is None or self.ui.overlay_rect is None:
            return
            
        total_cells = self.rows * self.cols
        reveal_percentage = min(self.background_revealed / total_cells, 1.0)

        # Tính toán độ trong suốt dựa trên số ô đã xóa
        alpha = int(255 * (1 - reveal_percentage))

        # Cập nhật màu overlay với độ trong suốt
        # Tạo màu với alpha
        color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
        self.ui.background_overlay.itemconfig(
            self.ui.overlay_rect,
            fill=color
        )

    def get_path(self, start, goal, algo):
        if algo == "DFS":
            path = self.algorithms.dfs(start, goal)
        elif algo == "BFS":
            path = self.algorithms.bfs(start, goal)
        elif algo == "UCS":
            path = self.algorithms.ucs(start, goal)
        else:
            path = self.algorithms.astar(start, goal)

        # Kiểm tra giới hạn đường đi (mở rộng để ăn được 2 cặp ngoài biên)
        # Cho phép tối đa 6 điểm = 5 đường thẳng (4 góc rẽ) để có thể đi qua biên
        if path and len(path) > 6:  # 6 điểm = 5 đường thẳng
            return None

        # Lưu thống kê thuật toán
        self.current_algorithm_stats = self.algorithms.stats.copy()
        return path

    def find_pair(self, algo):
        coords = self.board.get_cells()
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                r1, c1 = coords[i]
                r2, c2 = coords[j]
                if self.board.board[r1][c1] == self.board.board[r2][c2]:
                    path = self.get_path((r1, c1), (r2, c2), algo)
                    if path:
                        return (r1, c1), (r2, c2), path
        return None

    def draw_lightning(self, path):
        coords = []
        prev_r, prev_c = None, None

        for i, (r, c) in enumerate(path):
            x = c * self.cell_size + self.cell_size // 2
            y = r * self.cell_size + self.cell_size // 2

            # Kiểm tra nếu có kết nối qua rìa ngoài
            if prev_r is not None and prev_c is not None:
                # Kết nối từ rìa trái sang rìa phải
                if prev_c == 0 and c == self.cols - 1:
                    # Vẽ đường cong qua rìa ngoài
                    mid_x = self.cols * self.cell_size + 50  # Điểm giữa bên ngoài
                    mid_y = (y + (prev_r * self.cell_size + self.cell_size // 2)) // 2
                    coords.append((mid_x, mid_y))
                # Kết nối từ rìa phải sang rìa trái
                elif prev_c == self.cols - 1 and c == 0:
                    # Vẽ đường cong qua rìa ngoài
                    mid_x = -50  # Điểm giữa bên ngoài
                    mid_y = (y + (prev_r * self.cell_size + self.cell_size // 2)) // 2
                    coords.append((mid_x, mid_y))
                # Kết nối từ rìa trên sang rìa dưới
                elif prev_r == 0 and r == self.rows - 1:
                    # Vẽ đường cong qua rìa ngoài
                    mid_x = (x + (prev_c * self.cell_size + self.cell_size // 2)) // 2
                    mid_y = self.rows * self.cell_size + 50  # Điểm giữa bên ngoài
                    coords.append((mid_x, mid_y))
                # Kết nối từ rìa dưới sang rìa trên
                elif prev_r == self.rows - 1 and r == 0:
                    # Vẽ đường cong qua rìa ngoài
                    mid_x = (x + (prev_c * self.cell_size + self.cell_size // 2)) // 2
                    mid_y = -50  # Điểm giữa bên ngoài
                    coords.append((mid_x, mid_y))

            coords.append((x, y))
            prev_r, prev_c = r, c

        flat = [v for xy in coords for v in xy]

        # Tạo hiệu ứng lightning đẹp hơn với gradient
        line = self.ui.canvas.create_line(
            *flat,
            fill="#FFD700",  # Màu vàng gold
            width=5,
            dash=(8, 4),
            capstyle="round",
            joinstyle="round"
        )

        # Tạo thêm một đường nền để tạo hiệu ứng glow
        glow_line = self.ui.canvas.create_line(
            *flat,
            fill="#FFA500",  # Màu cam
            width=8,
            dash=(8, 4),
            capstyle="round",
            joinstyle="round"
        )

        # Đưa glow xuống dưới line chính
        self.ui.canvas.tag_lower(glow_line)

        self.root.update()
        self.root.after(300, lambda: [self.ui.canvas.delete(line), self.ui.canvas.delete(glow_line)])

    def start_auto(self):
        if self.game_paused:
            return
        if self.ui.mode_var.get() != "Auto":
            return
        self.auto_running = True
        self.auto_play()

    def auto_play(self):
        if self.game_paused or not self.auto_running:
            return
        
        # Nếu đang ở chế độ nhanh, sử dụng auto_play_fast
        if self.fast_mode:
            self.auto_play_fast()
            return
            
        algo = self.ui.algo_var.get()
        pair = self.find_pair(algo)
        if not pair:
            # Không còn cặp hợp lệ, nếu còn ô -> reshuffle, nếu không -> win
            if self.board.get_cells():
                self.board.reshuffle_remaining()
                # vẽ lại toàn bộ các icon còn lại sau reshuffle
                for (r, c), img_id in list(self.image_ids.items()):
                    if self.board.board[r][c] == -1:
                        self.ui.canvas.delete(img_id)
                        del self.image_ids[(r, c)]
                    else:
                        x = c * self.cell_size + self.cell_size // 2
                        y = r * self.cell_size + self.cell_size // 2
                        icon = self.icons[self.board.board[r][c]]
                        self.ui.canvas.itemconfig(img_id, image=icon)
                self.algorithms.board = self.board.board
                self.root.after(300, self.auto_play)
                return
            else:
                self.win_game()
                return
        (r1, c1), (r2, c2), path = pair
        self.play_sound("select")
        self.draw_lightning(path)
        self.root.after(350, lambda: self.remove_pair_and_check(r1, c1, r2, c2, auto=True))

    def remove_pair_and_check(self, r1, c1, r2, c2, auto=False):
        self.board.remove_pair(r1, c1, r2, c2)
        
        # Kiểm tra và xóa image_ids nếu tồn tại
        if (r1, c1) in self.image_ids:
            self.ui.canvas.delete(self.image_ids[(r1, c1)])
            del self.image_ids[(r1, c1)]
        if (r2, c2) in self.image_ids:
            self.ui.canvas.delete(self.image_ids[(r2, c2)])
            del self.image_ids[(r2, c2)]
        self.play_sound("eat")
        self.moves += 1
        self.ui.moves_label.config(text=f"Moves: {self.moves}")
        self.selected = []
        self.clear_highlights()  # Clear highlights sau khi xóa cặp

        # Tăng số ô đã được xóa và cập nhật background overlay
        self.background_revealed += 2
        self.update_background_overlay()

        if not self.board.get_cells():
            self.win_game()
        elif auto:
            self.root.after(400, self.auto_play)

    def skip_current_pair(self):
        """Bỏ qua cặp hiện tại và tìm cặp khác (tua nhanh khi auto play)"""
        if self.game_paused:
            return
        
        # Clear selection hiện tại
        self.selected = []
        self.clear_highlights()
        
        # Nếu đang ở chế độ Auto, tìm cặp tiếp theo ngay lập tức
        if self.ui.mode_var.get() == "Auto" and self.auto_running:
            # Tua nhanh: bỏ qua tất cả delay và animation
            self.auto_play_fast()
        else:
            # Nếu ở chế độ Manual, chỉ clear selection
            pass

    def toggle_fast_mode(self):
        """Bật/tắt chế độ tua nhanh"""
        self.fast_mode = not self.fast_mode
        if self.fast_mode:
            self.ui.fast_forward_btn.config(text="⏩ Fast ON", bg="#27AE60")
            # Nếu đang auto play, chuyển sang chế độ nhanh
            if self.ui.mode_var.get() == "Auto" and self.auto_running:
                self.auto_play_fast()
        else:
            self.ui.fast_forward_btn.config(text="⏩ Fast", bg="#8E44AD")

    def auto_play_fast(self):
        """Auto play với tốc độ nhanh (bỏ qua animation)"""
        if self.game_paused or not self.auto_running:
            return
        algo = self.ui.algo_var.get()
        pair = self.find_pair(algo)
        if not pair:
            # Không còn cặp hợp lệ, nếu còn ô -> reshuffle, nếu không -> win
            if self.board.get_cells():
                self.board.reshuffle_remaining()
                # vẽ lại toàn bộ các icon còn lại sau reshuffle
                for (r, c), img_id in list(self.image_ids.items()):
                    if self.board.board[r][c] == -1:
                        self.ui.canvas.delete(img_id)
                        del self.image_ids[(r, c)]
                    else:
                        x = c * self.cell_size + self.cell_size // 2
                        y = r * self.cell_size + self.cell_size // 2
                        icon = self.icons[self.board.board[r][c]]
                        self.ui.canvas.itemconfig(img_id, image=icon)
                self.algorithms.board = self.board.board
                self.auto_play_fast()  # Tiếp tục với tốc độ nhanh
                return
            else:
                self.win_game()
                return
        (r1, c1), (r2, c2), path = pair
        # Bỏ qua sound và animation, xóa cặp ngay lập tức
        self.remove_pair_and_check_fast(r1, c1, r2, c2, auto=True)

    def remove_pair_and_check_fast(self, r1, c1, r2, c2, auto=False):
        """Xóa cặp nhanh không có animation"""
        self.board.remove_pair(r1, c1, r2, c2)
        
        # Kiểm tra và xóa image_ids nếu tồn tại
        if (r1, c1) in self.image_ids:
            self.ui.canvas.delete(self.image_ids[(r1, c1)])
            del self.image_ids[(r1, c1)]
        if (r2, c2) in self.image_ids:
            self.ui.canvas.delete(self.image_ids[(r2, c2)])
            del self.image_ids[(r2, c2)]
        
        # Bỏ qua sound
        # self.play_sound("eat")
        self.moves += 1
        self.ui.moves_label.config(text=f"Moves: {self.moves}")
        self.selected = []
        self.clear_highlights()

        # Tăng số ô đã được xóa và cập nhật background overlay
        self.background_revealed += 2
        self.update_background_overlay()

        if not self.board.get_cells():
            self.win_game()
        elif auto:
            # Tiếp tục auto play ngay lập tức
            self.auto_play_fast()

    def win_game(self):
        self.stop_timer()
        self.play_sound("win")
        self.save_history_entry()
        messagebox.showinfo("Chiến Thắng!", f"Bạn đã thắng!\nSố moves: {self.moves}\nThời gian: {self.time_elapsed}s")

    # ---------- History ----------
    def load_history(self):
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_history_entry(self):
        # Lấy thống kê thuật toán cuối cùng được sử dụng
        algo_stats = getattr(self, 'current_algorithm_stats', {
            'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0
        })

        entry = {
            "rows": self.rows,
            "cols": self.cols,
            "algo": self.ui.algo_var.get(),
            "mode": self.ui.mode_var.get(),
            "moves": self.moves,
            "time": self.time_elapsed,
            "steps": algo_stats.get('steps', 0),
            "visited": algo_stats.get('visited', 0),
            "generated": algo_stats.get('generated', 0),
            "time_ms": algo_stats.get('time_ms', 0)
        }
        history = self.load_history()
        history.append(entry)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def show_history(self):
        history = self.load_history()
        win = Toplevel(self.root)
        win.title("📊 Game History & Statistics")
        win.geometry("1200x700")
        win.configure(bg="#1a1a2e")
        win.resizable(True, True)

        # Đảm bảo cửa sổ history là modal và không ảnh hưởng đến game chính
        win.transient(self.root)
        win.grab_set()

        # Tạo gradient background
        self.create_gradient_background(win)

        # Tạo frame chính với hiệu ứng glassmorphism
        main_frame = tk.Frame(win, bg="#16213e", relief="flat", bd=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header với tiêu đề và thống kê tổng quan
        header_frame = tk.Frame(main_frame, bg="#0f3460", relief="raised", bd=2)
        header_frame.pack(fill="x", pady=(0, 15))

        # Tiêu đề chính
        title_label = tk.Label(
            header_frame,
            text="🎮 PIKACHU GAME HISTORY",
            font=("Arial", 20, "bold"),
            bg="#0f3460",
            fg="#e94560"
        )
        title_frame = tk.Frame(header_frame, bg="#0f3460")
        title_frame.pack(pady=15)
        title_label.pack()

        # Thống kê tổng quan
        stats_frame = tk.Frame(header_frame, bg="#0f3460")
        stats_frame.pack(pady=(0, 15))

        # Tính toán thống kê
        total_games = len(history)
        avg_moves = sum(h.get("moves", 0) for h in history) / max(total_games, 1)
        avg_time = sum(h.get("time", 0) for h in history) / max(total_games, 1)
        best_time = min((h.get("time", 999) for h in history), default=0)
        best_moves = min((h.get("moves", 999) for h in history), default=0)

        # Tạo các thẻ thống kê
        stats_data = [
            ("🎯 Total Games", f"{total_games}"),
            ("⚡ Avg Moves", f"{avg_moves:.1f}"),
            ("⏱️ Avg Time", f"{avg_time:.1f}s"),
            ("🏆 Best Time", f"{best_time}s"),
            ("🎪 Best Moves", f"{best_moves}")
        ]

        for i, (label, value) in enumerate(stats_data):
            stat_frame = tk.Frame(stats_frame, bg="#16213e", relief="raised", bd=1)
            stat_frame.grid(row=0, column=i, padx=10, pady=5, sticky="ew")

            tk.Label(stat_frame, text=label, font=("Arial", 9, "bold"),
                     bg="#16213e", fg="#e94560").pack()
            tk.Label(stat_frame, text=value, font=("Arial", 12, "bold"),
                     bg="#16213e", fg="#ffffff").pack()

        # Cấu hình grid weights
        for i in range(len(stats_data)):
            stats_frame.columnconfigure(i, weight=1)

        # Tạo notebook cho tabs với style tùy chỉnh
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 15))

        # Tạo Treeview với style đẹp hơn
        style = ttk.Style(win)
        style.theme_use('clam')

        # Cấu hình style cho notebook
        style.configure("TNotebook", background="#16213e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#0f3460", foreground="#ffffff",
                        padding=[20, 10], font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#e94560"), ("active", "#16213e")])

        # Tab 1: Bảng dữ liệu
        data_frame = tk.Frame(notebook, bg="#16213e", relief="raised", bd=2)
        notebook.add(data_frame, text="📊 Data Table")

        # Tab 2: Biểu đồ thống kê
        chart_frame = tk.Frame(notebook, bg="#16213e", relief="raised", bd=2)
        notebook.add(chart_frame, text="📈 Performance Charts")

        # Tạo biểu đồ thống kê
        self.create_performance_charts(chart_frame, history)

        # Thanh công cụ với các nút lọc
        toolbar_frame = tk.Frame(data_frame, bg="#0f3460", height=50)
        toolbar_frame.pack(fill="x", padx=10, pady=10)
        toolbar_frame.pack_propagate(False)

        # Nút lọc theo thuật toán
        tk.Label(toolbar_frame, text="Filter by Algorithm:", font=("Arial", 10, "bold"),
                 bg="#0f3460", fg="#ffffff").pack(side="left", padx=(0, 10))

        self.filter_algo_var = tk.StringVar(value="All")
        algo_filter = ttk.Combobox(toolbar_frame, textvariable=self.filter_algo_var,
                                   values=["All", "DFS", "BFS", "UCS", "A*"],
                                   state="readonly", width=10)
        algo_filter.pack(side="left", padx=(0, 20))

        # Nút sắp xếp
        tk.Label(toolbar_frame, text="Sort by:", font=("Arial", 10, "bold"),
                 bg="#0f3460", fg="#ffffff").pack(side="left", padx=(0, 10))

        self.sort_var = tk.StringVar(value="Time (Newest)")
        sort_combo = ttk.Combobox(toolbar_frame, textvariable=self.sort_var,
                                  values=["Time (Newest)", "Time (Oldest)", "Moves (Low)", "Moves (High)",
                                          "Algorithm", "Mode"],
                                  state="readonly", width=15)
        sort_combo.pack(side="left", padx=(0, 20))

        # Nút refresh
        refresh_btn = tk.Button(toolbar_frame, text="🔄 Refresh",
                                command=lambda: self.refresh_history_table(tree, history),
                                bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                                relief="raised", bd=2, cursor="hand2")
        refresh_btn.pack(side="left", padx=(0, 10))

        # Nút xóa lịch sử
        clear_btn = tk.Button(toolbar_frame, text="🗑️ Clear All", command=lambda: self.clear_history(win, tree),
                              bg="#e74c3c", fg="white", font=("Arial", 9, "bold"),
                              relief="raised", bd=2, cursor="hand2")
        clear_btn.pack(side="left", padx=(0, 10))

        # Nút xuất dữ liệu
        export_btn = tk.Button(toolbar_frame, text="📤 Export", command=lambda: self.export_history(history),
                               bg="#9b59b6", fg="white", font=("Arial", 9, "bold"),
                               relief="raised", bd=2, cursor="hand2")
        export_btn.pack(side="left")

        # Cấu hình style cho Treeview
        style.configure("Custom.Treeview",
                        background="#1a1a2e",
                        foreground="#ffffff",
                        fieldbackground="#1a1a2e",
                        font=("Arial", 10),
                        rowheight=30)
        style.configure("Custom.Treeview.Heading",
                        background="#e94560",
                        foreground="white",
                        font=("Arial", 11, "bold"),
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[('selected', '#0f3460')],
                  foreground=[('selected', '#ffffff')])

        # Tạo frame cho treeview và scrollbar
        tree_frame = tk.Frame(data_frame, bg="#16213e")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("#", "Algorithm", "Mode", "Moves", "Time (s)", "Steps", "Visited", "Generated", "Time (ms)")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12, style="Custom.Treeview")

        # Cấu hình cột với độ rộng phù hợp
        column_widths = {"#": 40, "Algorithm": 80, "Mode": 60, "Moves": 60, "Time (s)": 70,
                         "Steps": 60, "Visited": 70, "Generated": 80, "Time (ms)": 80}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=column_widths[c], anchor="center")

        # Thêm dữ liệu với màu sắc
        self.populate_history_table(tree, history)

        # Scrollbar tùy chỉnh
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview và scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Footer với các nút điều khiển
        footer_frame = tk.Frame(main_frame, bg="#0f3460", height=60)
        footer_frame.pack(fill="x")
        footer_frame.pack_propagate(False)

        # Nút đóng với style đẹp
        close_btn = tk.Button(
            footer_frame,
            text="✕ Close",
            command=win.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="raised",
            bd=3,
            cursor="hand2",
            width=12,
            height=2
        )
        close_btn.pack(side="right", padx=20, pady=15)

        # Lưu reference để có thể cập nhật
        self.history_window = win
        self.history_tree = tree
        self.history_data = history

        # Bind events
        algo_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_history(tree, history))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.sort_history(tree, history))

    def create_gradient_background(self, win):
        """Tạo background gradient đẹp cho cửa sổ history"""
        # Tạo canvas gradient với kích thước cố định
        canvas = tk.Canvas(win, width=1200, height=700, highlightthickness=0, bd=0)
        canvas.place(x=0, y=0)  # Đặt ở vị trí cố định

        # Gradient từ xanh (#1a1a2e) đến tím (#0f3460)
        start_color = (26, 26, 46)  # #1a1a2e
        end_color = (15, 52, 96)  # #0f3460

        for i in range(700):
            ratio = i / 700
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, 1200, i, fill=color)

        # Đưa canvas xuống dưới cùng để không che các widget khác
        canvas.lower("all")

        # Lưu canvas để không bị GC xoá
        win.background_canvas = canvas

    def populate_history_table(self, tree, history):
        """Điền dữ liệu vào bảng history"""
        # Xóa dữ liệu cũ
        for item in tree.get_children():
            tree.delete(item)

        # Thêm dữ liệu mới
        for i, h in enumerate(reversed(history), 1):
            values = (
                i,
                h.get("algo", "N/A"),
                h.get("mode", "N/A"),
                h.get("moves", 0),
                h.get("time", 0),
                h.get("steps", 0),
                h.get("visited", 0),
                h.get("generated", 0),
                f"{h.get('time_ms', 0):.1f}"
            )
            tree.insert("", "end", values=values)
        
        # Nếu không có dữ liệu, hiển thị thông báo
        if not history:
            tree.insert("", "end", values=("", "No data", "", "", "", "", "", "", ""))

    def filter_history(self, tree, history):
        """Lọc history theo thuật toán"""
        filter_algo = self.filter_algo_var.get()
        if filter_algo == "All":
            filtered_history = history
        else:
            filtered_history = [h for h in history if h.get("algo") == filter_algo]

        self.populate_history_table(tree, filtered_history)

    def sort_history(self, tree, history):
        """Sắp xếp history theo tiêu chí"""
        sort_by = self.sort_var.get()

        if sort_by == "Time (Newest)":
            sorted_history = sorted(history, key=lambda x: x.get("time", 0), reverse=True)
        elif sort_by == "Time (Oldest)":
            sorted_history = sorted(history, key=lambda x: x.get("time", 0))
        elif sort_by == "Moves (Low)":
            sorted_history = sorted(history, key=lambda x: x.get("moves", 0))
        elif sort_by == "Moves (High)":
            sorted_history = sorted(history, key=lambda x: x.get("moves", 0), reverse=True)
        elif sort_by == "Algorithm":
            sorted_history = sorted(history, key=lambda x: x.get("algo", ""))
        elif sort_by == "Mode":
            sorted_history = sorted(history, key=lambda x: x.get("mode", ""))
        else:
            sorted_history = history

        self.populate_history_table(tree, sorted_history)

    def refresh_history_table(self, tree, history):
        """Làm mới bảng history"""
        history = self.load_history()
        self.populate_history_table(tree, history)

    def clear_history(self, win, tree):
        """Xóa toàn bộ lịch sử"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
            try:
                with open(self.history_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                self.populate_history_table(tree, [])
                messagebox.showinfo("Success", "History cleared successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {str(e)}")

    def export_history(self, history):
        """Xuất lịch sử ra file CSV"""
        try:
            import csv
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export History"
            )

            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Algorithm', 'Mode', 'Moves', 'Time (s)', 'Steps', 'Visited', 'Generated',
                                  'Time (ms)']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for h in history:
                        writer.writerow({
                            'Algorithm': h.get("algo", "N/A"),
                            'Mode': h.get("mode", "N/A"),
                            'Moves': h.get("moves", 0),
                            'Time (s)': h.get("time", 0),
                            'Steps': h.get("steps", 0),
                            'Visited': h.get("visited", 0),
                            'Generated': h.get("generated", 0),
                            'Time (ms)': h.get("time_ms", 0)
                        })

                messagebox.showinfo("Success", f"History exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")

    def create_performance_charts(self, parent, history):
        """Tạo biểu đồ thống kê hiệu suất"""
        if not history:
            no_data_label = tk.Label(parent, text="No data available for charts",
                                     font=("Arial", 14, "bold"), bg="#16213e", fg="#e94560")
            no_data_label.pack(expand=True)
            return

        # Tạo canvas cho biểu đồ
        chart_canvas = tk.Canvas(parent, bg="#1a1a2e", highlightthickness=0)
        chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Tính toán dữ liệu cho biểu đồ
        algo_stats = {}
        for h in history:
            algo = h.get("algo", "Unknown")
            if algo not in algo_stats:
                algo_stats[algo] = {
                    "count": 0, "total_moves": 0, "total_time": 0,
                    "total_steps": 0, "total_visited": 0, "total_generated": 0
                }
            algo_stats[algo]["count"] += 1
            algo_stats[algo]["total_moves"] += h.get("moves", 0)
            algo_stats[algo]["total_time"] += h.get("time", 0)
            algo_stats[algo]["total_steps"] += h.get("steps", 0)
            algo_stats[algo]["total_visited"] += h.get("visited", 0)
            algo_stats[algo]["total_generated"] += h.get("generated", 0)

        # Vẽ biểu đồ cột cho số lần sử dụng thuật toán
        self.draw_bar_chart(chart_canvas, algo_stats, "Algorithm Usage", "count", 50, 50, 300, 200)

        # Vẽ biểu đồ cột cho thời gian trung bình
        self.draw_bar_chart(chart_canvas, algo_stats, "Average Time (s)", "total_time", 400, 50, 300, 200)

        # Vẽ biểu đồ cột cho số moves trung bình
        self.draw_bar_chart(chart_canvas, algo_stats, "Average Moves", "total_moves", 50, 300, 300, 200)

        # Vẽ biểu đồ cột cho hiệu suất thuật toán (steps)
        self.draw_bar_chart(chart_canvas, algo_stats, "Average Steps", "total_steps", 400, 300, 300, 200)

    def draw_bar_chart(self, canvas, data, title, metric, x, y, width, height):
        """Vẽ biểu đồ cột"""
        if not data:
            return

        # Màu sắc cho các cột
        colors = ["#e94560", "#27ae60", "#3498db", "#f39c12", "#9b59b6", "#e67e22"]

        # Tính toán giá trị
        algos = list(data.keys())
        values = []
        for algo in algos:
            if metric == "count":
                values.append(data[algo][metric])
            else:
                values.append(data[algo][metric] / max(data[algo]["count"], 1))

        if not values:
            return

        max_value = max(values)
        if max_value == 0:
            max_value = 1

        # Vẽ tiêu đề
        canvas.create_text(x + width // 2, y - 20, text=title, font=("Arial", 12, "bold"),
                           fill="#ffffff", anchor="center")

        # Vẽ trục Y
        canvas.create_line(x, y, x, y + height, fill="#ffffff", width=2)
        canvas.create_line(x, y + height, x + width, y + height, fill="#ffffff", width=2)

        # Vẽ các cột
        bar_width = width // len(algos) - 10
        for i, (algo, value) in enumerate(zip(algos, values)):
            bar_height = int((value / max_value) * height)
            bar_x = x + i * (bar_width + 10) + 5
            bar_y = y + height - bar_height

            # Vẽ cột
            canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, y + height,
                                    fill=colors[i % len(colors)], outline="#ffffff", width=1)

            # Vẽ nhãn thuật toán
            canvas.create_text(bar_x + bar_width // 2, y + height + 15, text=algo,
                               font=("Arial", 9), fill="#ffffff", anchor="center")

            # Vẽ giá trị
            canvas.create_text(bar_x + bar_width // 2, bar_y - 10, text=f"{value:.1f}",
                               font=("Arial", 8), fill="#ffffff", anchor="center")
