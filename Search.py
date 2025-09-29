from collections import deque
import heapq
import time


class SearchAlgorithms:
    def __init__(self, board, rows, cols):
        self.board = board
        self.rows = rows
        self.cols = cols
        self.stats = {
            'steps': 0,
            'visited': 0,
            'generated': 0,
            'time_ms': 0
        }

    # def neighbors(self, r, c):
    #     # Neighbors trong board
    #     for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
    #         nr, nc = r + dr, c + dc
    #         if 0 <= nr < self.rows and 0 <= nc < self.cols:
    #             yield nr, nc, dr, dc
    #
    #     # Kết nối qua rìa ngoài - có thể đi từ rìa này sang rìa kia
    #     # Kết nối từ rìa trái sang rìa phải
    #     if c == 0:  # Ở cột đầu tiên
    #         for nr in range(self.rows):
    #             if self.board[nr][self.cols - 1] == -1:  # Cột cuối cùng trống
    #                 yield nr, self.cols - 1, 0, self.cols - 1
    #
    #     # Kết nối từ rìa phải sang rìa trái
    #     if c == self.cols - 1:  # Ở cột cuối cùng
    #         for nr in range(self.rows):
    #             if self.board[nr][0] == -1:  # Cột đầu tiên trống
    #                 yield nr, 0, 0, -self.cols + 1
    #
    #     # Kết nối từ rìa trên sang rìa dưới
    #     if r == 0:  # Ở hàng đầu tiên
    #         for nc in range(self.cols):
    #             if self.board[self.rows - 1][nc] == -1:  # Hàng cuối cùng trống
    #                 yield self.rows - 1, nc, self.rows - 1, 0
    #
    #     # Kết nối từ rìa dưới sang rìa trên
    #     if r == self.rows - 1:  # Ở hàng cuối cùng
    #         for nc in range(self.cols):
    #             if self.board[0][nc] == -1:  # Hàng đầu tiên trống
    #                 yield 0, nc, -self.rows + 1, 0

    def neighbors(self, r, c):
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                yield nr, nc, dr, dc

    def count_turns(self, path):
        if len(path) < 3:
            return 0
        turns = 0
        for i in range(1, len(path) - 1):
            prev = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
            next_ = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
            if prev != next_:
                turns += 1
        return turns

    def dfs(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        stack = [(start, [start], 0)]
        visited = set()
        generated = set()

        while stack:
            (r, c), path, turns = stack.pop()
            self.stats['generated'] += 1
            generated.add((r, c))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                return path

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        stack.append(((nr, nc), new_path, new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        return None

    def bfs(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        queue = deque([(start, [start], 0)])
        visited = set()
        generated = set()

        while queue:
            (r, c), path, turns = queue.popleft()
            self.stats['generated'] += 1
            generated.add((r, c))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                return path

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        queue.append(((nr, nc), new_path, new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        return None

    def ucs(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        pq = [(0, start, [start], 0)]
        visited = set()
        generated = set()

        while pq:
            cost, (r, c), path, turns = heapq.heappop(pq)
            self.stats['generated'] += 1
            generated.add((r, c))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                return path

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        heapq.heappush(pq, (cost + 1, (nr, nc), new_path, new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        return None

    def astar(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        pq = [(h(start, goal), 0, start, [start], 0)]
        visited = set()
        generated = set()

        while pq:
            f, g, (r, c), path, turns = heapq.heappop(pq)
            self.stats['generated'] += 1
            generated.add((r, c))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                return path

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        new_g = g + 1
                        heapq.heappush(pq, (new_g + h((nr, nc), goal), new_g, (nr, nc), new_path, new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        return None
