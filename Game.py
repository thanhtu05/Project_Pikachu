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
from WinScreen import WinScreen
import hashlib


class PikachuGame:
    def __init__(self, root, rows=8, cols=12):  # Thêm tham số mặc định
        self.root = root
        self.root.title("GAME PIKACHU")
        self.rows, self.cols = rows, cols
        self.cell_size = 60
        self.click_tolerance = 15  # Vùng click mở rộng xung quanh mỗi ô
        self.icons = self.load_icons("icons", 15)
        self.cost = 0
        self.time_elapsed = 0
        self.timer_running = False
        self.game_paused = False
        self.auto_running = False
        # Milliseconds between auto simulation steps; lower = faster
        self.auto_delay_ms = 0
        self.selected = []
        self.sound_enabled = True
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
        self.highlighted_cells = []  # Danh sách các ô đang được highlight
        self.background_revealed = 0
        self.initial_board = None   #lưu bảng ban đầu

        self.simulation_highlights = []  # Lưu các highlight trong simulation
        self.game_won = False  #trạng thái thắng
        self.total_visited = 0  # Tổng số ô đã thăm
        self.total_generated = 0  # Tổng số ô được tạo
        self.reshuffle_count = 0  # Số lần reshuffle trong game

        pygame.mixer.init()
        self.sounds = {
            "bg": "sounds/bg_music.mp3",
            "select": "sounds/select.wav",
            "eat": "sounds/eat.wav",
            "win": "sounds/win.wav"
        }
        self.play_music_bg()

        self.board = Board(self.rows, self.cols, self.icons)
        self.initial_board = [row[:] for row in self.board.board]
        self.ui = GameUI(root, self.rows, self.cols, self.cell_size, self)
        self.root.geometry("1000x1000")
        self.algorithms = SearchAlgorithms(self.board.board, self.rows, self.cols)
        # Enable debug diagnostics to print neighbor-generation stats (set to False to disable)
        try:
            self.algorithms.debug = True
            print("[DEBUG] SearchAlgorithms debug enabled")
        except Exception:
            pass
        self.bg_canvas = self.ui.canvas
        self.ui.new_btn.config(command=self.new_game)
        # Ensure clicking Hint triggers a suggested next move (previously Start Auto)
        # Hint button removed from UI; keep backward-compatible auto wiring
        try:
            if hasattr(self.ui, 'auto_btn'):
                self.ui.auto_btn.config(command=self.handle_start_auto_click)
        except Exception:
            pass
        self.ui.home_btn.config(command=self.go_to_splash_screen)
        # Connect skip button (if present)
        try:
            self.ui.skip_btn.config(command=self.skip_simulation)
        except Exception:
            pass
        self.ui.stop_btn.config(command=self.stop_game)
        self.ui.continue_btn.config(command=self.continue_game)
        self.ui.history_btn.config(command=self.show_history)
        self.ui.canvas.bind("<Button-1>", self.on_canvas_click)
        self.ui.sound_var.trace("w", self.on_sound_toggle)

        self.image_ids = {}
        self.new_game()

        # Timer fields: use UI.time_limit / UI.remaining_time as source of truth for countdown
        self._timer_after_id = None
        

    def handle_start_auto_click(self):
        """Switch to Auto mode and start the auto simulation."""
        try:
            # Stop any running auto first
            if self.auto_running:
                self.stop_game()
                print(f"[DEBUG] Stopped previous auto before starting new one")
            
            # Force mode to Auto to avoid early return in start_auto
            if hasattr(self.ui, 'mode_var'):
                self.ui.mode_var.set("Auto")
            # Start the timer when auto starts
            if not self.timer_running:
                self.start_timer()
            self.start_auto()
        except Exception:
            pass

    def show_hint(self):
        """Highlight a suggested pair (next move) without removing it.
        Uses current algorithm to find a pair and draws a temporary highlight.
        """
        try:
            algo = self.ui.algo_var.get() if hasattr(self.ui, 'algo_var') else 'DFS'
            pair = self.find_pair(algo)
            if not pair:
                # If no pair found, flash a message on canvas
                try:
                    mid_x = (self.cols * self.cell_size) // 2
                    mid_y = (self.rows * self.cell_size) // 2
                    msg_id = self.ui.canvas.create_text(mid_x, mid_y, text="No Hint Available", fill="#E74C3C", font=("Arial", 16, "bold"))
                    self.root.after(1200, lambda: self.ui.canvas.delete(msg_id))
                except Exception:
                    pass
                return

            (r1, c1), (r2, c2), path = pair

            # Draw a temporary highlight rectangle around both cells
            x1 = c1 * self.cell_size + 3
            y1 = r1 * self.cell_size + 3
            x2 = (c1 + 1) * self.cell_size - 3
            y2 = (r1 + 1) * self.cell_size - 3
            id1 = self.ui.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF00", width=4)

            x1b = c2 * self.cell_size + 3
            y1b = r2 * self.cell_size + 3
            x2b = (c2 + 1) * self.cell_size - 3
            y2b = (r2 + 1) * self.cell_size - 3
            id2 = self.ui.canvas.create_rectangle(x1b, y1b, x2b, y2b, outline="#00FF00", width=4)

            # Also draw a temporary path line if available
            if path and len(path) >= 2:
                coords = []
                for (r, c) in path:
                    coords.extend([c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2])
                line_id = self.ui.canvas.create_line(*coords, fill="#00FF00", width=3, dash=(6, 4))
            else:
                line_id = None

            # Remove highlights after short delay
            def _clear_hint():
                try:
                    self.ui.canvas.delete(id1)
                except Exception:
                    pass
                try:
                    self.ui.canvas.delete(id2)
                except Exception:
                    pass
                if line_id:
                    try:
                        self.ui.canvas.delete(line_id)
                    except Exception:
                        pass

            self.root.after(1200, _clear_hint)
        except Exception:
            pass
    
    def on_algo_change(self, algo_value):
        """Called when algorithm is changed - stop auto if running"""
        if self.auto_running:
            self.stop_game()
            print(f"[DEBUG] Auto stopped due to algorithm change to: {algo_value}")
    
    def on_mode_change(self, mode_value):
        """Called when mode is changed - stop auto if running"""
        if self.auto_running:
            self.stop_game()
            print(f"[DEBUG] Auto stopped due to mode change to: {mode_value}")

    def go_to_splash_screen(self):
        """Quay về giao diện SplashScreen và dừng trò chơi hiện tại."""
        # Stop timers and simulation, then destroy the Tk window and return to the
        # original pygame-based splash screen that the app starts with.
        try:
            self.stop_timer()
        except Exception:
            pass
        self.auto_running = False
        self.game_paused = True
        # Destroy the current Tkinter root before launching pygame splash
        try:
            self.root.destroy()
        except Exception:
            pass

        # Launch the Pygame splash screen (the same entrypoint used by Main.py)
        try:
            import SplashScreen
            splash = SplashScreen.PygameSplashScreen()
            splash.run()
        except Exception as e:
            # Fallback: if Pygame splash cannot be launched, fall back to the
            # ModernSplashScreen Tkinter variant so Home still returns to a menu.
            try:
                print(f"Error launching Pygame splash: {e}. Falling back to ModernSplashScreen.")
                splash_root = tk.Tk()
                splash_screen = SplashScreen.ModernSplashScreen(splash_root)
                splash_screen.show()
                splash_root.mainloop()
            except Exception:
                pass

    def clear_simulation_highlights(self):
        """Xóa tất cả highlight của simulation"""
        for highlight_id in self.simulation_highlights:
            self.ui.canvas.delete(highlight_id)
        self.simulation_highlights.clear()

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

    def new_game(self, restore_initial=False):
        """Khởi tạo game mới - reset cả simulation"""
        self.auto_running = False
        self.game_paused = False
        self.game_won = False  # Reset game won flag
        self.cost = 0
        self.time_elapsed = 0
        self.ui.update_moves(0)
        self.ui.update_time("0s")
        # Reset countdown UI and stop any running timer
        try:
            if hasattr(self.ui, 'reset_countdown'):
                self.ui.reset_countdown()
            else:
                # Fallback: set remaining_time to ui.time_limit
                if hasattr(self.ui, 'time_limit'):
                    self.ui.set_remaining_time(self.ui.time_limit)
        except Exception:
            pass
        try:
            self.stop_timer()
        except Exception:
            pass
        self.selected = []
        self.clear_highlights()
        self.clear_simulation_highlights()
        self.background_revealed = 0
        self.board.new_board()
        self.algorithms.board = self.board.board
        self.algorithms.reset_simulation()



        # Disable skip by default when starting a new game
        try:
            self.set_skip_enabled(False)
        except Exception:
            pass
        self.background_revealed = 0
        # Reset reshuffle counter for new game
        self.reshuffle_count = 0

        if restore_initial and hasattr(self, 'initial_board'):
            self.board.board = [row[:] for row in self.initial_board]
            print("Restored initial board:", self.board.board)  # Debug
        else:
            self.board.new_board()
            self.initial_board = [row[:] for row in self.board.board]  # Cập nhật bảng ban đầu

        self.algorithms.board = self.board.board
        self.algorithms.reset_simulation()

        # Vẽ lại bảng
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

        self.update_background_overlay()
    # Don't auto start here - timer will begin when Auto is started or on first manual match
        
    # Don't auto start - user must click "Start Auto" button manually or make first manual match

    def stop_game(self):
        """Dừng trò chơi và chế độ tự động"""
        self.auto_running = False
        # Cancel any auto-simulation timer
        try:
            # remember whether auto was running so Continue can resume it
            self._was_auto_running = getattr(self, 'auto_running', False)
            if hasattr(self, 'auto_timer') and self.auto_timer:
                self.root.after_cancel(self.auto_timer)
                self.auto_timer = None
        except Exception:
            pass

        # Pause the countdown timer too so Continue can resume it
        try:
            self.stop_timer()
        except Exception:
            pass

        self.game_paused = True

    def continue_game(self):
        if self.game_paused:
            self.game_paused = False
            self.start_timer()
            # Resume auto if it was running before stop
            try:
                if getattr(self, '_was_auto_running', False) and not self.auto_running:
                    self.start_auto()
            except Exception:
                pass

    def start_timer(self):
        if self.timer_running:
            return
        self.timer_running = True
        try:
            if hasattr(self.ui, 'start_countdown'):
                self.ui.start_countdown()
        except Exception:
            pass
        # schedule first tick
        try:
            if hasattr(self, '_timer_after_id') and self._timer_after_id:
                self.root.after_cancel(self._timer_after_id)
        except Exception:
            pass
        self._timer_after_id = self.root.after(1000, self.update_timer)

    def redraw_remaining_icons(self):
        # Update existing images or delete if removed
        for (r, c), img_id in list(self.image_ids.items()):
            if self.board.board[r][c] == -1:
                self.ui.canvas.delete(img_id)
                del self.image_ids[(r, c)]
            else:
                icon = self.icons[self.board.board[r][c]]
                self.ui.canvas.itemconfig(img_id, image=icon)

    # def update_timer(self):
    #     if self.timer_running and not self.game_paused:
    #         self.ui.update_time(f"{self.time_elapsed}s")
    #         self.time_elapsed += 1
    #         try:
    #             self._timer_after_id = self.root.after(1000, self.update_timer)
    #         except Exception:
    #             pass
    #     # Time label is now handled by pill system
    def update_timer(self):
        """Tick handler called every second while timer_running.
        Updates elapsed time and decrements UI countdown.
        """
        try:
            if not self.timer_running or self.game_paused or self.game_won:
                return

            # Increase elapsed time
            self.time_elapsed += 1

            # Update UI elapsed time pill
            try:
                self.ui.update_time(f"{self.time_elapsed}s")
            except Exception:
                pass

            # Decrement UI countdown if available
            try:
                current_remaining = getattr(self.ui, 'remaining_time', None)
                if current_remaining is None:
                    # If UI doesn't expose remaining_time, nothing to do
                    pass
                else:
                    new_remaining = max(int(current_remaining) - 1, 0)
                    try:
                        self.ui.set_remaining_time(new_remaining)
                    except Exception:
                        # fallback: directly set attribute and render
                        try:
                            self.ui.remaining_time = new_remaining
                            self.ui.update_time_bar_tk()
                        except Exception:
                            pass

                    # If countdown reached zero -> time up
                    if new_remaining <= 0:
                        self.stop_timer()
                        try:
                            self.on_time_up()
                        except Exception:
                            pass
                        return

            except Exception:
                pass

            # schedule next tick
            try:
                self._timer_after_id = self.root.after(1000, self.update_timer)
            except Exception:
                self._timer_after_id = None
        except Exception:
            pass

    def stop_timer(self):
        self.timer_running = False
        try:
            if hasattr(self, '_timer_after_id') and self._timer_after_id:
                self.root.after_cancel(self._timer_after_id)
                self._timer_after_id = None
        except Exception:
            pass
        try:
            if hasattr(self.ui, 'stop_countdown'):
                self.ui.stop_countdown()
        except Exception:
            pass

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
                        self.root.after(350, lambda: self.remove_pair_and_check(r1, c1, r2, c2, path))
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
        
        # Thêm hiệu ứng fade mượt mà hơn
        if reveal_percentage > 0:
            # Tạo hiệu ứng gradient fade
            try:
                # Xóa overlay cũ nếu có
                for item in self.ui.background_overlay.find_all():
                    if item != self.ui.overlay_rect:
                        self.ui.background_overlay.delete(item)
                
                # Tạo gradient fade từ trong ra ngoài
                center_x, center_y = self.cols * self.cell_size // 2, self.rows * self.cell_size // 2
                max_radius = max(self.cols * self.cell_size, self.rows * self.cell_size) // 2
                
                # Tạo các vòng tròn đồng tâm với độ trong suốt giảm dần
                for i in range(10):
                    radius = int(max_radius * (1 - reveal_percentage) * (i + 1) / 10)
                    if radius > 0:
                        alpha_val = int(alpha * (10 - i) / 10)
                        color = f"#{alpha_val:02x}{alpha_val:02x}{alpha_val:02x}"
                        self.ui.background_overlay.create_oval(
                            center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            fill=color, outline=""
                        )
            except Exception:
                pass

    def get_path(self, start, goal, algo):
        """Lấy đường đi - dùng phương thức thông thường (không simulation) khi người dùng chơi"""
        # Tạm thời tắt simulation mode để tìm đường đi nhanh
        temp_simulation_mode = self.algorithms.simulation_mode
        self.algorithms.simulation_mode = False

        path = self.algorithms.dfs(start, goal)
    
        # Khôi phục simulation mode
        self.algorithms.simulation_mode = temp_simulation_mode


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
        # delete lightning effect after a short time depending on auto speed
        delay_del = max(20, int(self.auto_delay_ms // 2))
        self.root.after(delay_del, lambda: [self.ui.canvas.delete(line), self.ui.canvas.delete(glow_line)])

    def start_auto(self):
        print(f"[DEBUG] start_auto called - game_paused: {self.game_paused}, game_won: {self.game_won}, mode: {self.ui.mode_var.get()}")
        if self.game_paused or self.game_won:
            print(f"[DEBUG] start_auto blocked - game_paused: {self.game_paused}, game_won: {self.game_won}")
            return
        if self.ui.mode_var.get() != "Auto":
            print(f"[DEBUG] start_auto blocked - mode is not Auto: {self.ui.mode_var.get()}")
            return

        print(f"[DEBUG] start_auto proceeding...")
        self.auto_running = True
        self.algorithms.simulation_mode = True
        self.simulate_auto_step()
        try:
            self.set_skip_enabled(True)
        except Exception:
            pass

    def simulate_auto_step(self):
        if self.game_paused or not self.auto_running or self.game_won:
            return

        step = self.algorithms.simulate_step()
        if step:
            action, pos, path, turns = step
            if action == "visit":
                if pos:
                    r, c = pos
                    self.highlight_visited_cell(r, c)

            elif action == "expand":
                if path and len(path) > 1:
                    self.draw_temporary_path(path)

            elif action == "goal":
                if path and len(path) >= 2:
                    r1, c1 = path[0]
                    r2, c2 = path[-1]
                    self.draw_final_path(path)
                    # wait a bit (configurable) then remove the pair
                    self.root.after(max(20, int(self.auto_delay_ms)), lambda: self.remove_pair_and_check(r1, c1, r2, c2, path, auto=True))
                    return

            elif action == "none":
                self.show_no_path_message()
                self.root.after(1500, self.continue_auto_play)
                return

            delay = max(10, int(self.auto_delay_ms))
            self.auto_timer = self.root.after(delay, self.simulate_auto_step)
        else:
            self.algorithms.reset_simulation()
            self.clear_highlights()
            self.clear_simulation_highlights()
            try:
                self.set_skip_enabled(False)
            except Exception:
                pass
            self.root.after(max(20, int(self.auto_delay_ms // 2)), self.continue_auto_play)

    def set_skip_enabled(self, enabled: bool):
        """Enable or disable the Skip button if available."""
        try:
            if hasattr(self.ui, 'skip_btn'):
                self.ui.skip_btn.config(state='normal' if enabled else 'disabled')
        except Exception:
            pass

    def skip_simulation(self):
        """Skip forward: fast-forward the simulation to the next 'goal' step or end."""
        was_sim = getattr(self.algorithms, 'simulation_mode', False)
        self.algorithms.simulation_mode = True
        try:
            while True:
                step = self.algorithms.simulate_step()
                if not step:
                    break
                action, pos, path, turns = step
                if action == 'visit' or action == 'expand':
                    continue
                if action == 'goal':
                    if path and len(path) >= 2:
                        r1, c1 = path[0]
                        r2, c2 = path[-1]
                        self.remove_pair_and_check(r1, c1, r2, c2, path, auto=False)
                        if not self.board.get_cells():
                            break
                elif action == 'none':
                    break
        finally:
            self.algorithms.simulation_mode = was_sim
            try:
                self.algorithms.reset_simulation()
            except Exception:
                pass
            self.clear_simulation_highlights()
            self.clear_highlights()
            try:
                self.set_skip_enabled(False)
            except Exception:
                pass

    def show_no_path_message(self):
        """Hiển thị thông báo không tìm thấy đường đi"""
        message_id = self.ui.canvas.create_text(
            self.cols * self.cell_size // 2,
            self.rows * self.cell_size // 2,
            text="No Path Found!",
            fill="#E74C3C",
            font=("Arial", 16, "bold")
        )
        self.root.after(1500, lambda: self.ui.canvas.delete(message_id))

    def draw_final_path(self, path):
        """Vẽ đường đi cuối cùng tìm thấy"""
        coords = []
        for r, c in path:
            x = c * self.cell_size + self.cell_size // 2
            y = r * self.cell_size + self.cell_size // 2
            coords.extend([x, y])

        if len(coords) >= 4:
            line = self.ui.canvas.create_line(
                *coords,
                fill="#27AE60",  # Màu xanh lá
                width=4,
                capstyle="round"
            )
            # Giữ đường đi cuối cùng cho đến khi xóa cặp
            self.simulation_highlights.append(line)

    def highlight_visited_cell(self, r, c):
        """Tô sáng ô đang được thăm trong simulation (màu vàng)"""
        x1 = c * self.cell_size + 5
        y1 = r * self.cell_size + 5
        x2 = (c + 1) * self.cell_size - 5
        y2 = (r + 1) * self.cell_size - 5

        highlight_id = self.ui.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#FFD700",  # Màu vàng
            outline="#FFA500",
            width=2,
            stipple="gray50"
        )
        # Tự động xóa sau 200ms
        self.root.after(200, lambda: self.ui.canvas.delete(highlight_id))

    def draw_temporary_path(self, path):
        """Vẽ đường đi tạm thời trong simulation"""
        coords = []
        for r, c in path:
            x = c * self.cell_size + self.cell_size // 2
            y = r * self.cell_size + self.cell_size // 2
            coords.extend([x, y])

        if len(coords) >= 4:
            line = self.ui.canvas.create_line(
                *coords,
                fill="#3498DB",  # Màu xanh dương
                width=3,
                dash=(4, 2),
                capstyle="round"
            )
            # Tự động xóa sau 200ms
            self.root.after(200, lambda: self.ui.canvas.delete(line))

    def continue_auto_play(self):
        if not self.auto_running or self.game_won:
            return
        algo = self.ui.algo_var.get()
        pair = self.find_pair(algo)
        if pair:
            (r1, c1), (r2, c2), path = pair
            self.algorithms.start_simulation((r1, c1), (r2, c2), algo)
            self.simulate_auto_step()
        else:
            remaining_cells = self.board.get_cells()
            print(f"Remaining cells after pair search: {remaining_cells}")
            if remaining_cells:
                self.board.reshuffle_remaining()
                # Track reshuffle count for history
                self.reshuffle_count += 1
                self.redraw_remaining_icons()
                self.algorithms.board = self.board.board
                # Tính lại visited và generated sau reshuffle (nếu cần)
                temp_simulation_mode = self.algorithms.simulation_mode
                self.algorithms.simulation_mode = True
                pair = self.find_pair(algo)
                if pair:
                    (r1, c1), (r2, c2), path = pair
                    self.algorithms.start_simulation((r1, c1), (r2, c2), algo)
                    while True:
                        step = self.algorithms.simulate_step()
                        if not step or step[0] == "goal":
                            break
                    self.total_visited += self.algorithms.stats.get('visited', 0)
                    self.total_generated += self.algorithms.stats.get('generated', 0)
                self.algorithms.simulation_mode = temp_simulation_mode
                self.algorithms.reset_simulation()
                self.root.after(1000, self.continue_auto_play)
            else:
                self.win_game()

    def auto_play(self):
        if self.game_paused or not self.auto_running:
            return


        algo = self.ui.algo_var.get()
        pair = self.find_pair(algo)
        if not pair:
            # Không còn cặp hợp lệ, nếu còn ô -> reshuffle, nếu không -> win
            if self.board.get_cells():
                self.board.reshuffle_remaining()
                # Track reshuffle count for history
                self.reshuffle_count += 1
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
        self.root.after(350, lambda: self.remove_pair_and_check(r1, c1, r2, c2, path, auto=True))

    def remove_pair_and_check(self, r1, c1, r2, c2, path=None, auto=False):
        if self.game_won:
            return

        self.board.remove_pair(r1, c1, r2, c2)
        self.clear_simulation_highlights()
        if (r1, c1) in self.image_ids:
            self.ui.canvas.delete(self.image_ids[(r1, c1)])
            del self.image_ids[(r1, c1)]
        if (r2, c2) in self.image_ids:
            self.ui.canvas.delete(self.image_ids[(r2, c2)])
            del self.image_ids[(r2, c2)]
        self.play_sound("eat")
        path_length = len(path) - 1 if path and len(path) > 1 else 1
        self.update_cost(path_length)
        self.selected = []
        self.clear_highlights()
        self.background_revealed += 2
        self.update_background_overlay()

        # Cập nhật tổng visited và generated
        if auto:
            # Lấy từ simulate_auto_step
            current_stats = getattr(self.algorithms, 'stats', {'visited': 0, 'generated': 0})
        else:
            # Tính lại cho chế độ thủ công bằng cách chạy mô phỏng tạm thời
            temp_simulation_mode = self.algorithms.simulation_mode
            self.algorithms.simulation_mode = True
            self.algorithms.start_simulation((r1, c1), (r2, c2), self.ui.algo_var.get())
            while True:
                step = self.algorithms.simulate_step()
                if not step or step[0] == "goal":
                    break
            current_stats = self.algorithms.stats.copy()
            self.algorithms.simulation_mode = temp_simulation_mode
            self.algorithms.reset_simulation()

        self.total_visited += current_stats.get('visited', 0)
        self.total_generated += current_stats.get('generated', 0)

        if not self.board.get_cells() and not self.game_won:
            self.win_game()
        elif auto and not self.game_won:
            self.root.after(400, self.continue_auto_play)
        else:
            # For manual mode, if timer not running start it when the first successful pair is removed
            if not auto and not self.timer_running:
                try:
                    self.start_timer()
                except Exception:
                    pass

    def update_cost(self, path_length):
        """Cập nhật cost dựa trên chiều dài đường đi."""
        self.cost += path_length
        self.ui.update_moves(self.cost)

    def win_game(self):
        if self.game_won:
            return
        self.game_won = True
        self.auto_running = False
        self.stop_timer()
        self.play_sound("win")
        self.save_history_entry()
        self.win_screen = WinScreen(self.root, self, self.cost, self.time_elapsed)
        self.win_screen.show()
        #self.root.after_cancel(self._timer_after_id) if hasattr(self, '_timer_after_id') else None
        # ✅ Dừng timer an toàn
        if hasattr(self, '_timer_after_id') and self._timer_after_id is not None:
            try:
                self.root.after_cancel(self._timer_after_id)
            except Exception:
                pass
            self._timer_after_id = None

        if hasattr(self, 'auto_timer'):
            self.root.after_cancel(self.auto_timer)

    def set_auto_delay_ms(self, ms: int):
        """Set the delay (in milliseconds) between auto simulation steps. Lower = faster."""
        try:
            self.auto_delay_ms = max(10, int(ms))
            print(f"[DEBUG] auto_delay_ms set to {self.auto_delay_ms}ms")
        except Exception:
            pass

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
        algo_stats = getattr(self, 'current_algorithm_stats', {
            'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0
        })
        try:
            state_str = json.dumps(self.initial_board, sort_keys=True)
        except Exception:
            state_str = str(self.initial_board)
        state_key = hashlib.md5(state_str.encode('utf-8')).hexdigest()

        history = self.load_history()
        existing_states = {}
        max_state_id = 0
        for h in history:
            sk = h.get('state_key')
            sid = h.get('state', 0)
            if sk and sid:
                existing_states[sk] = sid
                if sid > max_state_id:
                    max_state_id = sid

        if state_key in existing_states:
            state_id = existing_states[state_key]
        else:
            state_id = max_state_id + 1 if max_state_id else 1

        mode_val = self.ui.mode_var.get() if hasattr(self, 'ui') else 'Manual'
        if mode_val == 'Manual':
            algo_val = 'Manual'
            steps_val = 0
            visited_val = 0
            generated_val = 0
            time_ms_val = 0
        else:
            algo_val = self.ui.algo_var.get() if hasattr(self, 'ui') else ''
            steps_val = algo_stats.get('steps', 0)
            # Sử dụng tổng thay vì giá trị riêng lẻ
            visited_val = self.total_visited
            generated_val = self.total_generated
            time_ms_val = algo_stats.get('time_ms', 0)

        # Store only minimal fields for history as requested: score (cost), time, and state id/key
        entry = {
            "cost": self.cost,
            "time": self.time_elapsed,
            "state_key": state_key,
            "state": state_id
        }
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
        avg_time = sum(h.get("time", 0) for h in history) / max(total_games, 1)
        best_time = min((h.get("time", 999) for h in history), default=0)
        # Prefer 'cost' field; fallback to 'moves' for backward compatibility
        best_cost = min((h.get("cost", h.get("moves", 999)) for h in history), default=0)

        # Tạo các thẻ thống kê (đã loại bỏ Avg Moves theo yêu cầu)
        stats_data = [
            ("🎯 Total Games", f"{total_games}"),
            ("⏱️ Avg Time", f"{avg_time:.1f}s"),
            ("🏆 Best Time", f"{best_time}s"),
            ("🎪 Best Score", f"{best_cost}")
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
        # Small debug label to show how many history entries were loaded and the file used
        debug_label = tk.Label(header_frame, text=f"History file: {self.history_file} | Entries: {len(history)}",
                       font=("Arial", 9), bg="#0f3460", fg="#ffffff")
        debug_label.pack(side="right", padx=10)
        self.create_performance_charts(chart_frame, history)

        # Thanh công cụ với các nút lọc
        toolbar_frame = tk.Frame(data_frame, bg="#0f3460", height=50)
        toolbar_frame.pack(fill="x", padx=10, pady=10)
        toolbar_frame.pack_propagate(False)


    # Filter by algorithm removed

        # Nút sắp xếp
        tk.Label(toolbar_frame, text="Sort by:", font=("Arial", 10, "bold"),
                 bg="#0f3460", fg="#ffffff").pack(side="left", padx=(0, 10))

        self.sort_var = tk.StringVar(value="Time (Shortest)")
        sort_combo = ttk.Combobox(toolbar_frame, textvariable=self.sort_var,
                  values=[
                      "Time (Shortest)", "Time (Longest)",
                      "State (Nearest)", "State (Farthest)",
                      "Score (Highest)", "Score (Lowest)"
                  ],
                  state="readonly", width=18)
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
        # Simplified data table: only Score and Time as requested
        cols = ("#", "Score", "Time (s)")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12, style="Custom.Treeview")

        # Configure columns (only Score and Time)
        column_widths = {"#": 60, "Score": 120, "Time (s)": 120}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=column_widths.get(c, 100), anchor="center")

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

        # Bind sort event only
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
        # We only display Score and Time. 'Score' uses 'cost' (fallback to 'moves').
        for i, h in enumerate(reversed(history), 1):
            score = h.get("cost", h.get("moves", 0))
            time_val = h.get("time", 0)
            values = (i, score, time_val)
            tree.insert("", "end", values=values)

        # Nếu không có dữ liệu, hiển thị thông báo
        if not history:
            # Insert a single-row message matching the simplified columns
            tree.insert("", "end", values=("", "No data", ""))

    def filter_history(self, tree, history):
        # Filter by algorithm removed; no-op
        pass

    def sort_history(self, tree, history):
        """Sắp xếp history theo tiêu chí"""
        sort_by = self.sort_var.get()
        if sort_by == "Time (Shortest)":
            sorted_history = sorted(history, key=lambda x: x.get("time", 0))
        elif sort_by == "Time (Longest)":
            sorted_history = sorted(history, key=lambda x: x.get("time", 0), reverse=True)
        elif sort_by == "State (Nearest)":
            sorted_history = sorted(history, key=lambda x: x.get("state", 0))
        elif sort_by == "State (Farthest)":
            sorted_history = sorted(history, key=lambda x: x.get("state", 0), reverse=True)
        elif sort_by == "Score (Highest)":
            sorted_history = sorted(history, key=lambda x: x.get("cost", x.get("moves", 0)), reverse=True)
        elif sort_by == "Score (Lowest)":
            sorted_history = sorted(history, key=lambda x: x.get("cost", x.get("moves", 0)))
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
                    # Only export Score and Time as requested
                    fieldnames = ['Score', 'Time (s)']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for h in history:
                        writer.writerow({
                            'Score': h.get("cost", h.get("moves", 0)),
                            'Time (s)': h.get("time", 0)
                        })

                messagebox.showinfo("Success", f"History exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")

    def create_performance_charts(self, parent, history):
        """Create a performance chart using matplotlib embedded into Tkinter.
        Shows score (cost) over games (time axis using the saved time value as label).
        If matplotlib is not available, show a friendly fallback message.
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception:
            no_lib_label = tk.Label(parent, text="matplotlib not available — install matplotlib to see charts",
                                    font=("Arial", 12), bg="#16213e", fg="#e94560")
            no_lib_label.pack(expand=True, pady=20)
            return

        if not history:
            no_data_label = tk.Label(parent, text="No data available for charts",
                                     font=("Arial", 14, "bold"), bg="#16213e", fg="#e94560")
            no_data_label.pack(expand=True)
            return

        # Prefer using integer `state` values on the x axis when they exist in history.
        # Each history entry may include a numeric 'state' id; if present, we sort by that
        # and plot Score vs state. Otherwise fall back to simple indexed games (oldest->newest).
        state_tuples = []
        for h in history:
            s = h.get('state')
            try:
                s_int = int(s)
            except Exception:
                s_int = None
            if s_int is not None:
                state_tuples.append((s_int, h.get('cost', h.get('moves', 0)), h.get('time', 0)))

        if state_tuples:
            # sort by state id (ascending)
            state_tuples.sort(key=lambda t: t[0])
            x = [t[0] for t in state_tuples]
            scores = [t[1] for t in state_tuples]
            times = [t[2] for t in state_tuples]
            xlabel = 'State (integer id)'
        else:
            # Fallback: use game index (oldest -> newest)
            scores = [h.get('cost', h.get('moves', 0)) for h in history]
            times = [h.get('time', 0) for h in history]
            scores = list(reversed(scores))
            times = list(reversed(times))
            x = list(range(1, len(scores) + 1))
            xlabel = 'Game (oldest → newest)'

        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        ax.plot(x, scores, marker='o', linestyle='-', color='#e94560', label='Score (cost)')
        ax.set_title('Performance Over States')
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Score (cost)')
        ax.grid(True, linestyle='--', alpha=0.4)

        # Optional secondary axis for time values as annotations
        for xi, sc, t in zip(x, scores, times):
            ax.annotate(f"{t}s", (xi, sc), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, color='#333')

        # If x are integer states, set integer ticks for readability (limit count)
        try:
            if all(isinstance(xi, int) for xi in x):
                if len(x) <= 30:
                    ax.set_xticks(x)
                else:
                    # too many ticks -> choose a subsample
                    step = max(1, len(x) // 20)
                    ax.set_xticks(x[::step])
        except Exception:
            pass

        # Embed into Tkinter
        canvas_fig = FigureCanvasTkAgg(fig, master=parent)
        canvas_fig.draw()
        widget = canvas_fig.get_tk_widget()
        widget.pack(fill='both', expand=True, padx=10, pady=10)

        # Keep reference so it doesn't get garbage collected
        parent._mpl_fig = fig
        parent._mpl_canvas = canvas_fig

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