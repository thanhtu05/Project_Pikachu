import random

class Board:
    def __init__(self, rows, cols, icons):
        self.rows = rows
        self.cols = cols
        self.icons = icons
        self.board = []

    def new_board(self):
        total = self.rows * self.cols
        icons = [i % len(self.icons) for i in range(total // 2)] * 2
        random.shuffle(icons)
        self.board = [[icons.pop() for _ in range(self.cols)] for _ in range(self.rows)]
        return self.board

    def remove_pair(self, r1, c1, r2, c2):
        self.board[r1][c1] = self.board[r2][c2] = -1

    def get_cells(self):
        coords = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:
                    coords.append((r, c))
        return coords

    def reshuffle_remaining(self):
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