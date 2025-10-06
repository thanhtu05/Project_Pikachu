import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from SplashScreen import ModernButton

class WinScreen:
    def __init__(self, root, game, cost, time_elapsed):  # Thay moves bằng cost
        self.root = root
        self.game = game
        self.cost = cost  # Thay moves bằng cost
        self.time_elapsed = time_elapsed
        self._frame_cache = []

        self.win = tk.Toplevel(root)
        self.win.title("Victory!")
        self.win.geometry("600x400")
        self.win.resizable(False, False)
        self.win.transient(root)
        self.win.grab_set()

        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.win.winfo_screenheight() // 2) - (400 // 2)
        self.win.geometry(f"600x400+{x}+{y}")

        self.canvas = tk.Canvas(self.win, width=600, height=400, bg="#E5E7EB", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            self.bg_image = Image.open("background/win_background.png").resize((600, 400))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(300, 200, image=self.bg_photo)
        except FileNotFoundError:
            pass

        self.content_frame = self.create_transparent_frame(100, 50, 400, 300, radius=20, alpha=180)

        self.canvas.create_text(
            300, 100,
            text="🎉 CHÚC MỪNG BẠN ĐÃ THẮNG! 🎉",
            font=("Segoe UI", 24, "bold"),
            fill="#FFFFFF",
            justify="center"
        )

        self.canvas.create_text(
            300, 160,
            text=f"Cost: {cost}\nThời gian: {time_elapsed}s",  # Thay "Số nước đi" bằng "Cost"
            font=("Segoe UI", 14),
            fill="#2C3E50",
            justify="center"
        )

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
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=(255, 255, 255, alpha))
        frame_img = ImageTk.PhotoImage(img)
        self._frame_cache.append(frame_img)
        return self.canvas.create_image(x, y, anchor="nw", image=frame_img)

    def start_new_game(self):
        self.win.destroy()
        self.game.new_game()

    def restart_game(self):
        self.win.destroy()
        self.game.new_game(restore_initial=True)

    def show(self):
        self.win.deiconify()

    def close(self):
        self.win.destroy()