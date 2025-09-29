import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 width=180, height=60, radius=30,
                 bg_color="#4F46E5", hover_color="#3730A3",
                 text_color="white", font=("Segoe UI", 14, "bold"),
                 shadow=True):
        super().__init__(parent,
                         borderwidth=0,
                         relief="flat",
                         highlightthickness=0,
                         bg=parent.cget("bg"))

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.radius = radius
        self.shadow = shadow
        self.text = text
        self.font = font

        self.is_pressed = False
        self.is_hovered = False

        self.configure(width=width, height=height)
        self.draw_button()

        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def draw_button(self):
        self.delete("all")

        # Shadow
        if self.shadow and not self.is_pressed:
            self.create_rounded_rect(
                4, 4, self.width + 4, self.height + 4,
                self.radius, fill="#d1d5db", outline=""
            )

        y_offset = 2 if self.is_pressed else 0
        current_color = self.hover_color if self.is_hovered else self.bg_color

        # Button body
        self.create_rounded_rect(
            0, y_offset, self.width, self.height + y_offset,
            self.radius, fill=current_color, outline=""
        )

        # Subtle border highlight (commented out as per your preference)
        # self.create_rounded_rect(
        #     0, y_offset, self.width, self.height + y_offset,
        #     self.radius, outline="#ffffff", width=1
        # )

        # Text
        self.create_text(
            self.width // 2, (self.height // 2) + y_offset,
            text=self.text, fill=self.text_color, font=self.font
        )

    def create_rounded_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_press(self, event):
        self.is_pressed = True
        self.draw_button()

    def _on_release(self, event):
        self.is_pressed = False
        self.draw_button()
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        self.configure(cursor="hand2")

    def _on_leave(self, event):
        self.is_hovered = False
        self.draw_button()
        self.configure(cursor="")

class ModernSplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Pikachu Game - Choose Your Level")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.center_window()

        # Use Canvas as the main background
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="#E5E7EB", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background image with error handling
        try:
            self.bg_image = Image.open("background/background.png").resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(400, 300, image=self.bg_photo)  # Center the background image
        except FileNotFoundError as e:
            print(f"Error loading background image: {e}")

        # Create semi-transparent white frames
        self.title_frame = self.create_transparent_frame(150, 20, 500, 100, radius=20)  # khung cho title
        self.level_frames = [
            self.create_transparent_frame(120, 160, 180, 200, radius=20),  # EASY
            self.create_transparent_frame(310, 160, 180, 200, radius=20),  # MEDIUM
            self.create_transparent_frame(500, 160, 180, 200, radius=20),  # HARD
        ]
        # self.footer_frame = self.create_transparent_frame(50, 500, 700, 70, radius=15)  # khung footer
        self.footer_frame = self.create_transparent_frame(150, 520, 530, 50, radius=15, alpha=140)

        self.create_title_section()
        self.create_level_selection()
        self.create_footer()

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")

    def create_transparent_frame(self, x, y, width, height, radius=25, alpha=120):
        # Tạo ảnh RGBA trong suốt
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Vẽ khung bo góc
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            fill=(255, 255, 255, alpha)
        )

        # Convert sang PhotoImage để Tkinter hiểu
        frame_img = ImageTk.PhotoImage(img)

        # Lưu reference để không bị xoá bởi GC
        if not hasattr(self, "_frame_cache"):
            self._frame_cache = []
        self._frame_cache.append(frame_img)

        # Đặt ảnh vào canvas
        self.canvas.create_image(x, y, anchor="nw", image=frame_img)

    def draw_text_with_outline(self, x, y, text, font,
                               fill="white", outline="black", outline_width=2):
        """Vẽ chữ có viền bằng cách vẽ nhiều lớp"""
        # Vẽ viền trước (dịch xung quanh)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    self.canvas.create_text(
                        x + dx, y + dy, text=text, font=font, fill=outline
                    )
        # Vẽ chữ chính đè lên
        self.canvas.create_text(x, y, text=text, font=font, fill=fill)


    def create_title_section(self):
        # Title có viền
        self.draw_text_with_outline(
            400, 50,
            text="⚡ PIKACHU GAME ⚡",
            font=("Segoe UI", 32, "bold"),
            fill="#FFFFFF",  # chữ trắng
            outline="#1E293B",  # viền xanh đậm
            outline_width=2
        )

        self.draw_text_with_outline(
            400, 90,
            text="Choose your difficulty level and start matching!",
            font=("Segoe UI", 16),
            fill="#F1F5F9",
            outline="#475569",
            outline_width=1
        )

    def create_level_selection(self):
        levels = [
            {"name": "EASY", "desc": "8x8 Grid", "color": "#10B981", "hover": "#059669", "rows": 8, "cols": 8},
            {"name": "MEDIUM", "desc": "8x12 Grid", "color": "#F59E0B", "hover": "#D97706", "rows": 8, "cols": 12},
            {"name": "HARD", "desc": "10x12 Grid", "color": "#EF4444", "hover": "#DC2626", "rows": 10, "cols": 12},
        ]

        positions = [(210, 180), (400, 180), (590, 180)]    #canh giữa
        start_x = 210
        for i, level in enumerate(levels):
            x_pos = start_x + i * 190  # Space buttons 200px apart
            y_pos = 230  # Vertical position

            # Add level name
            self.canvas.create_text(
                x_pos, y_pos,
                text=level["name"],
                font=("Segoe UI", 18, "bold"),
                fill="#1E293B"
            )
            # Add description
            self.canvas.create_text(
                x_pos, y_pos + 30,
                text=level["desc"],
                font=("Segoe UI", 12),
                fill="#475569",
                justify="center"
            )
            # Add button
            button = ModernButton(
                self.canvas,
                text="PLAY",
                command=lambda r=level["rows"], c=level["cols"]: self.start_game(r, c),
                width=160,
                height=50,
                bg_color=level["color"],
                hover_color=level["hover"],
                font=("Segoe UI", 12, "bold")
            )
            button_window = self.canvas.create_window(
                x_pos, y_pos + 70,  # Position below description
                window=button
            )

    def create_footer(self):
        self.draw_text_with_outline(
            400, 550,
            text="💡 Tip: Match identical Pikachu pairs by connecting them with a clear path!",
            font=("Segoe UI", 11),
            fill="#F1F5F9",
            outline="#475569",
            outline_width=1
        )


    def start_game(self, rows, cols):
        self.root.destroy()  # Close SplashScreen

        import tkinter as tk
        from Game import PikachuGame

        game_root = tk.Tk()
        game = PikachuGame(game_root, rows, cols)
        game_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernSplashScreen(root)
    root.mainloop()