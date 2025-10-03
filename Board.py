import random

class Board:
    def __init__(self, rows, cols, icons):
        self.rows = rows
        self.cols = cols
        self.icons = icons
        self.board = []  # Khởi tạo danh sách rỗng, sẽ được điền trong new_board
        self.initial_board = None  # Lưu trạng thái ban đầu

    def new_board(self):
        """Tạo bảng mới với các cặp biểu tượng ngẫu nhiên."""
        total = self.rows * self.cols
        if total % 2 != 0:
            raise ValueError("Số ô phải là số chẵn để tạo cặp biểu tượng.")
        # Tạo danh sách biểu tượng, mỗi biểu tượng xuất hiện 2 lần
        icons = [i % len(self.icons) for i in range(total // 2)] * 2
        random.shuffle(icons)
        # Tạo bảng 2D
        self.board = [icons[i:i + self.cols] for i in range(0, len(icons), self.cols)]
        # Đảm bảo kích thước đúng bằng cách thêm hàng rỗng nếu cần
        while len(self.board) < self.rows:
            self.board.append([-1] * self.cols)
        # Cắt hoặc điền -1 nếu vượt quá
        for i in range(self.rows):
            self.board[i] = self.board[i][:self.cols]
            if len(self.board[i]) < self.cols:
                self.board[i].extend([-1] * (self.cols - len(self.board[i])))
        # Lưu trạng thái ban đầu nếu chưa có
        if self.initial_board is None:
            self.initial_board = [row[:] for row in self.board]
        return self.board

    def restore_initial(self):
        """Khôi phục bảng về trạng thái ban đầu."""
        if self.initial_board is not None:
            self.board = [row[:] for row in self.initial_board]  # Sao chép lại bảng ban đầu

    def remove_pair(self, r1, c1, r2, c2):
        """Xóa cặp ô được chọn."""
        if (0 <= r1 < self.rows and 0 <= c1 < self.cols and
            0 <= r2 < self.rows and 0 <= c2 < self.cols):
            self.board[r1][c1] = self.board[r2][c2] = -1

    def get_cells(self):
        """Lấy danh sách các ô chưa bị xóa."""
        coords = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:
                    coords.append((r, c))
        return coords

    def reshuffle_remaining(self):
        """Xáo trộn lại các ô còn lại."""
        remaining_positions = []
        remaining_values = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:
                    remaining_positions.append((r, c))
                    remaining_values.append(self.board[r][c])
        if not remaining_positions:
            return
        random.shuffle(remaining_values)
        for idx, (r, c) in enumerate(remaining_positions):
            self.board[r][c] = remaining_values[idx]