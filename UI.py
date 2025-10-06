import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GameUI:
    def __init__(self, root, rows, cols, cell_size, game):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.game = game

        # Load ảnh background
        self.bg_image = Image.open("background/backgroundmain.png")
        self.bg_image = self.bg_image.resize((1000, 1000))  # Điều chỉnh kích thước phù hợp
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Tạo canvas làm nền chính
        self.bg_canvas = tk.Canvas(self.root, width=1000, height=700, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        # Vẽ ảnh nền
        self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # --- Overlay (dùng để làm mờ nền khi Stop) ---
        self.background_overlay = None
        self.overlay_rect = None

        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel",
                        font=("Arial", 12, "bold"),
                        background="",
                        foreground="#2C3E50")
        style.configure("TCombobox",
                        font=("Arial", 10),
                        fieldbackground="#ECF0F1",
                        background="")
        style.configure("TCheckbutton",
                        font=("Arial", 10),
                        background="",
                        foreground="#2C3E50")

        # Labels
        self.moves_label = tk.Label(
            self.bg_canvas,
            text="Cost: 0",
            fg="#E74C3C",
            bg="#FFFFFF",
            font=("Arial", 12, "bold")
        )
        self.moves_label_window = self.bg_canvas.create_window(100, 20, window=self.moves_label, anchor="nw")

        self.bg_canvas.tag_raise(self.moves_label_window)

        self.time_label = tk.Label(
            self.bg_canvas,
            text="Time: 0s",
            fg="#27AE60",
            bg="#FFFFFF",
            font=("Arial", 12, "bold")
        )
        self.time_label_window = self.bg_canvas.create_window(200, 20, window=self.time_label, anchor="nw")
        self.bg_canvas.tag_raise(self.time_label_window)

        # Sound toggle
        self.sound_var = tk.BooleanVar(value=True)
        style = ttk.Style()
        style.configure("MyCheck.TCheckbutton",
                        background="#FFFFFF",
                        foreground="#2C3E50")
        self.sound_toggle = ttk.Checkbutton(
            self.bg_canvas,
            text="🔊 Sound",
            variable=self.sound_var,
            command=self.toggle_sound,
            style="MyCheck.TCheckbutton",
            width=12
        )
        self.sound_toggle_window = self.bg_canvas.create_window(350, 20, window=self.sound_toggle, anchor="nw")

        # Mode selection
        self.mode_var = tk.StringVar(value="Manual")
        self.mode_menu = ttk.Combobox(
            self.bg_canvas,
            textvariable=self.mode_var,
            values=["Manual", "Auto"],
            state="readonly",
            width=10
        )
        self.mode_menu_window = self.bg_canvas.create_window(470, 20, window=self.mode_menu, anchor="nw")

        # Algorithm selection
        self.algo_var = tk.StringVar(value="DFS")
        self.algo_menu = ttk.Combobox(
            self.bg_canvas,
            textvariable=self.algo_var,
            values=["DFS", "BFS", "UCS", "A*"],
            state="readonly",
            width=8
        )
        self.algo_menu_window = self.bg_canvas.create_window(570, 20, window=self.algo_menu, anchor="nw")

        # Button style
        button_style = {
            "width": 12,
            "height": 2,
            "font": ("Arial", 10, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2"
        }
        button_count = 5
        button_width = 12 * 8 + 4
        total_available_width = 1000 - 200
        button_spacing = (total_available_width - (button_count * button_width)) // (button_count + 1)
        start_x = 100

        self.new_btn = tk.Button(
            self.bg_canvas,
            text="🆕 New Game",
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",
            activeforeground="white",
            **button_style
        )
        self.new_btn_window = self.bg_canvas.create_window(start_x, 60, window=self.new_btn, anchor="nw")

        self.auto_btn = tk.Button(
            self.bg_canvas,
            text="▶️ Start Auto",
            bg="#27AE60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            **button_style
        )
        self.auto_btn_window = self.bg_canvas.create_window(start_x + button_spacing + button_width, 60, window=self.auto_btn, anchor="nw")

        self.stop_btn = tk.Button(
            self.bg_canvas,
            text="⏹️ Stop",
            bg="#E74C3C",
            fg="white",
            activebackground="#C0392B",
            activeforeground="white",
            command=self.pause_game,
            **button_style
        )
        self.stop_btn_window = self.bg_canvas.create_window(start_x + 2 * (button_spacing + button_width), 60, window=self.stop_btn, anchor="nw")

        self.continue_btn = tk.Button(
            self.bg_canvas,
            text="▶️ Continue",
            bg="#F39C12",
            fg="white",
            activebackground="#E67E22",
            activeforeground="white",
            command=self.resume_game,
            **button_style
        )
        self.continue_btn_window = self.bg_canvas.create_window(start_x + 3 * (button_spacing + button_width), 60, window=self.continue_btn, anchor="nw")

        self.history_btn = tk.Button(
            self.bg_canvas,
            text="📊 History",
            bg="#9B59B6",
            fg="white",
            activebackground="#8E44AD",
            activeforeground="white",
            **button_style
        )
        self.history_btn_window = self.bg_canvas.create_window(start_x + 4 * (button_spacing + button_width), 60, window=self.history_btn, anchor="nw")

        #nút Home
        self.home_btn = tk.Button(
            self.bg_canvas,
            text="🏠 Home",
            bg="#27AE60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            **button_style
        )

        self.home_btn_window = self.bg_canvas.create_window(
            start_x + 5 * (button_spacing + button_width), 60,  # Vị trí cuối cùng
            window=self.home_btn,
            anchor="nw"
        )

        # --- Bàn cờ ---
        w, h = self.cols * self.cell_size, self.rows * self.cell_size
        self.canvas = tk.Canvas(
            self.bg_canvas,
            width=w,
            height=h,
            bg="#F8F9FA",
            borderwidth=3,
            relief="ridge",
            highlightthickness=2,
            highlightbackground="#BDC3C7"
        )
        self.canvas_window = self.bg_canvas.create_window(500, 150, window=self.canvas, anchor="n")

        # Tag để đảm bảo bàn cờ nằm trên overlay
        self.canvas.addtag_all("game_board")
        # Đưa các widget lên trên background
        self.bg_canvas.tag_raise(self.moves_label_window)
        self.bg_canvas.tag_raise(self.time_label_window)
        self.bg_canvas.tag_raise(self.sound_toggle_window)
        self.bg_canvas.tag_raise(self.mode_menu_window)
        self.bg_canvas.tag_raise(self.algo_menu_window)
        self.bg_canvas.tag_raise(self.new_btn_window)
        self.bg_canvas.tag_raise(self.auto_btn_window)
        self.bg_canvas.tag_raise(self.stop_btn_window)
        self.bg_canvas.tag_raise(self.continue_btn_window)
        self.bg_canvas.tag_raise(self.history_btn_window)
        self.bg_canvas.tag_raise(self.canvas_window)

        # Vẽ lưới
        for r in range(self.rows + 1):
            self.canvas.create_line(
                0, r * self.cell_size, w, r * self.cell_size,
                fill="#D5DBDB",
                width=1
            )
        for c in range(self.cols + 1):
            self.canvas.create_line(
                c * self.cell_size, 0, c * self.cell_size, h,
                fill="#D5DBDB",
                width=1
            )

    def toggle_sound(self):
        state = self.sound_var.get()
        self.sound_toggle.config(text="🔊 Sound" if state else "🔇 Sound")

    def pause_game(self):
        """Hiệu ứng mờ nền khi Stop"""
        if self.background_overlay is not None:
            self.background_overlay.lift()
            self.background_overlay.itemconfig(self.overlay_rect, fill="black")
            self.background_overlay.itemconfig(self.overlay_rect, stipple="gray50")  # giả lập alpha

    def resume_game(self):
        """Xoá overlay khi Continue"""
        if self.background_overlay is not None:
            self.background_overlay.lower()
            self.background_overlay.itemconfig(self.overlay_rect, fill="")
            self.background_overlay.itemconfig(self.overlay_rect, stipple="")


if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root, 4, 4, 100)
    root.mainloop()