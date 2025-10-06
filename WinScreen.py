import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from SplashScreen import ModernButton

class WinScreen:
    def __init__(self, root, game, cost, time_elapsed):
        self.root = root
        self.game = game
        self.cost = cost
        self.time_elapsed = time_elapsed
        self._frame_cache = []

        # Tạo cửa sổ mới
        self.win = tk.Toplevel(root)
        self.win.title("Victory!")
        self.win.geometry("600x400")
        self.win.resizable(False, False)
        self.win.transient(root)
        self.win.grab_set()  # Ngăn tương tác với cửa sổ khác

        # Center the window
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.win.winfo_screenheight() // 2) - (400 // 2)
        self.win.geometry(f"600x400+{x}+{y}")

        # Tạo canvas làm nền
        self.canvas = tk.Canvas(self.win, width=600, height=400, bg="#E5E7EB", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background image (tùy chọn, nếu có)
        try:
            self.bg_image = Image.open("background/win_background.png").resize((600, 400))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(300, 200, image=self.bg_photo)
        except FileNotFoundError:
            pass  # Bỏ qua nếu không có ảnh

        # Tạo frame trong suốt cho nội dung
        self.content_frame = self.create_transparent_frame(100, 50, 400, 300, radius=20, alpha=180)

        # Tiêu đề
        self.canvas.create_text(
            300, 100,
            text="🎉 CHÚC MỪNG BẠN ĐÃ THẮNG! 🎉",
            font=("Segoe UI", 24, "bold"),
            fill="#000000",
            justify="center"
        )

        # Thông tin số nước đi và thời gian
        self.canvas.create_text(
            300, 160,
            text=f"Cost: {cost}\nThời gian: {time_elapsed}s",
            font=("Segoe UI", 14),
            fill="#2C3E50",
            justify="center"
        )

        # Nút New Game
        self.new_game_btn = ModernButton(
            self.canvas,
            text="🆕 New Game",
            command=self.start_new_game,
            width=150,
            height=50,
            bg_color="#3498DB",
            hover_color="#2980B9",
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            radius=20
        )
        self.canvas.create_window(200, 250, window=self.new_game_btn, anchor="center")

        # Nút Restart
        self.restart_btn = ModernButton(
            self.canvas,
            text="🔄 Restart",
            command=self.restart_game,
            width=150,
            height=50,
            bg_color="#F39C12",
            hover_color="#E67E22",
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            radius=20
        )
        self.canvas.create_window(400, 250, window=self.restart_btn, anchor="center")

    def create_transparent_frame(self, x, y, width, height, radius=25, alpha=120):
        """Tạo frame trong suốt với góc bo."""
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=(255, 255, 255, alpha))
        frame_img = ImageTk.PhotoImage(img)
        self._frame_cache.append(frame_img)  # Lưu reference để tránh bị GC
        return self.canvas.create_image(x, y, anchor="nw", image=frame_img)

    def start_new_game(self):
        """Bắt đầu trò chơi mới và đóng cửa sổ chiến thắng."""
        self.win.destroy()
        self.game.new_game()  # Tạo bảng mới ngẫu nhiên

    def restart_game(self):
        """Khởi động lại level hiện tại với bảng ban đầu và đóng cửa sổ chiến thắng."""
        self.win.destroy()
        self.game.new_game(restore_initial=True)  # Khôi phục bảng ban đầu

    def show(self):
        """Hiển thị cửa sổ chiến thắng."""
        self.win.deiconify()

    def close(self):
        """Đóng cửa sổ chiến thắng."""
        self.win.destroy()