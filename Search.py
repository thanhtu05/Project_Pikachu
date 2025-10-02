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
        self.simulation_mode = False
        self.simulation_steps = []
        self.current_step = 0

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

    def start_simulation(self, start, goal, algo):
        """Bắt đầu chế độ simulation với thuật toán được chọn"""
        self.simulation_mode = True
        self.simulation_steps.clear()
        self.current_step = 0

        if algo == "DFS":
            self._simulate_dfs(start, goal)
        elif algo == "BFS":
            self._simulate_bfs(start, goal)
        elif algo == "UCS":
            self._simulate_ucs(start, goal)
        elif algo == "A*":
            self._simulate_astar(start, goal)

    def _simulate_dfs(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        stack = [(start, [start], 0)]
        visited = set()
        generated = set()

        while stack:
            (r, c), path, turns = stack.pop()
            self.stats['generated'] += 1
            generated.add((r, c))

            if self.simulation_mode:
                self.simulation_steps.append(("visit", (r, c), path.copy(), turns))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                self.simulation_steps.append(("goal", (r, c), path.copy(), turns))
                return

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        stack.append(((nr, nc), new_path, new_turns))
                        if self.simulation_mode:
                            self.simulation_steps.append(("expand", (nr, nc), new_path.copy(), new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        self.simulation_steps.append(("none", None, None, None))

    def _simulate_bfs(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        queue = deque([(start, [start], 0)])
        visited = set()
        generated = set()

        while queue:
            (r, c), path, turns = queue.popleft()
            self.stats['generated'] += 1
            generated.add((r, c))

            if self.simulation_mode:
                self.simulation_steps.append(("visit", (r, c), path.copy(), turns))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                self.simulation_steps.append(("goal", (r, c), path.copy(), turns))
                return

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        queue.append(((nr, nc), new_path, new_turns))
                        if self.simulation_mode:
                            self.simulation_steps.append(("expand", (nr, nc), new_path.copy(), new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        self.simulation_steps.append(("none", None, None, None))

    def _simulate_ucs(self, start, goal):
        start_time = time.time()
        self.stats = {'steps': 0, 'visited': 0, 'generated': 0, 'time_ms': 0}

        pq = [(0, start, [start], 0)]
        visited = set()
        generated = set()

        while pq:
            cost, (r, c), path, turns = heapq.heappop(pq)
            self.stats['generated'] += 1
            generated.add((r, c))

            if self.simulation_mode:
                self.simulation_steps.append(("visit", (r, c), path.copy(), turns))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                self.simulation_steps.append(("goal", (r, c), path.copy(), turns))
                return

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for nr, nc, dr, dc in self.neighbors(r, c):
                if self.board[nr][nc] == -1 or (nr, nc) == goal:
                    new_path = path + [(nr, nc)]
                    new_turns = self.count_turns(new_path)
                    if new_turns <= 2:
                        heapq.heappush(pq, (cost + 1, (nr, nc), new_path, new_turns))
                        if self.simulation_mode:
                            self.simulation_steps.append(("expand", (nr, nc), new_path.copy(), new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        self.simulation_steps.append(("none", None, None, None))

    def _simulate_astar(self, start, goal):
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

            if self.simulation_mode:
                self.simulation_steps.append(("visit", (r, c), path.copy(), turns))

            if (r, c) == goal and self.count_turns(path) <= 2:
                self.stats['steps'] = len(path) - 1
                self.stats['visited'] = len(visited)
                self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
                self.simulation_steps.append(("goal", (r, c), path.copy(), turns))
                return

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
                        if self.simulation_mode:
                            self.simulation_steps.append(("expand", (nr, nc), new_path.copy(), new_turns))

        self.stats['visited'] = len(visited)
        self.stats['time_ms'] = round((time.time() - start_time) * 1000, 1)
        self.simulation_steps.append(("none", None, None, None))

    def simulate_step(self):
        """Trả về bước tiếp theo trong quá trình simulation"""
        if self.current_step >= len(self.simulation_steps):
            return None
        step = self.simulation_steps[self.current_step]
        self.current_step += 1
        return step

    def reset_simulation(self):
        """Đặt lại simulation để bắt đầu lại"""
        self.simulation_mode = False
        self.simulation_steps.clear()
        self.current_step = 0

    def find_pair(self, algo):
        """Tìm một cặp ô có thể kết nối được"""
        coords = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:
                    coords.append((r, c))

        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                r1, c1 = coords[i]
                r2, c2 = coords[j]
                if self.board[r1][c1] == self.board[r2][c2]:
                    # Tạm thời tắt simulation mode để tìm đường đi nhanh
                    temp_simulation_mode = self.simulation_mode
                    self.simulation_mode = False

                    path = None
                    if algo == "DFS":
                        path = self.dfs((r1, c1), (r2, c2))
                    elif algo == "BFS":
                        path = self.bfs((r1, c1), (r2, c2))
                    elif algo == "UCS":
                        path = self.ucs((r1, c1), (r2, c2))
                    elif algo == "A*":
                        path = self.astar((r1, c1), (r2, c2))

                    # Khôi phục simulation mode
                    self.simulation_mode = temp_simulation_mode

                    if path and len(path) <= 6:  # Giới hạn độ dài đường đi
                        return (r1, c1), (r2, c2), path
        return None

    # Các phương thức cũ (DFS, BFS, UCS, A*) giờ chỉ dùng khi không simulation
    def dfs(self, start, goal):
        if self.simulation_mode:
            return None
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
        if self.simulation_mode:
            return None
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
        if self.simulation_mode:
            return None
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
        if self.simulation_mode:
            return None
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