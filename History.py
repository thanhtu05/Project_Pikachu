#!/usr/bin/env python3
"""
Demo script để test giao diện history mới
"""

import tkinter as tk
from Game import PikachuGame
import json
import os

def main():
    root = tk.Tk()
    game = PikachuGame(root, rows=4, cols=4)  # Tạo game nhỏ để test

    # 🔹 Đảm bảo file history.json tồn tại và rỗng khi khởi động
    if not os.path.exists("history.json"):
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
    else:
        # Xóa dữ liệu cũ (nếu có), để chỉ lưu khi người chơi thực sự chơi
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    print("Demo History UI - Click 'History' button to see the new interface!")
    print("Features:")
    print("✅ Beautiful gradient background")
    print("✅ Statistics overview cards")
    print("✅ Enhanced data table with custom styling")
    print("✅ Filter and sort functionality")
    print("✅ Performance charts")
    print("✅ Export to CSV")
    print("✅ Clear history option")
    print("\n(Lịch sử hiện tại trống — sẽ chỉ được lưu khi bạn chơi thật!)")

    root.mainloop()


if __name__ == "__main__":
    main()
