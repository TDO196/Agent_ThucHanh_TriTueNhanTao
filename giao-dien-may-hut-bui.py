

# https://github.com/TDO196/Agent_ThucHanh_TriTueNhanTao



import tkinter as tk
from tkinter import messagebox
from collections import deque
import copy
import heapq


# VACUUM CLEANER VISUALIZER - TKINTER
# 0 = sạch, 1 = bụi, 2 = nội thất/vật cản
# Máy hút bụi có vị trí riêng: hàng/cột


ROWS = 5
COLS = 5
SPEED = 600
MAX_STATES = 3000
MAX_DEPTH_IDS = 50

MOVES = [
    ("Lên", -1, 0, "↑"),
    ("Xuống", 1, 0, "↓"),
    ("Trái", 0, -1, "←"),
    ("Phải", 0, 1, "→"),
]


class Node:
    def __init__(self, grid, pos, parent=None, action="START", depth=0):
        self.grid = grid
        self.pos = pos
        self.parent = parent
        self.action = action
        self.depth = depth


class VacuumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng máy hút bụi - BFS/DFS/IDS/UCS/A*/Greedy")
        self.root.geometry("1050x680")
        self.root.minsize(850, 560)

        # Theme
        self.bg = "#f0db9b"          # nền chính
        self.panel = "#ffffff"       # nền các khung
        self.border = "#767676"      # viền
        self.accent = "#1f77b4"      # màu chọn/chạy
        self.accent2 = "#d9534f"     # reset/cảnh báo
        self.accent3 = "#2e8b57"     # hoàn tất
        self.accent4 = "#d98c00"     # từng bước
        self.text = "#000000"        # chữ chính
        self.muted = "#000000"       # chữ phụ
        self.cell_clean = "#f2f2f2"  # ô sạch
        self.cell_dirty = "#491d1d"  # ô bụi
        self.cell_wall = "#5e5e5e"   # nội thất/vật cản
        self.agent_color = "#4aa3df" # máy hút bụi

        self.root.configure(bg=self.bg)
        try:
            self.root.state("zoomed")  # Mở toàn màn hình trên Windows để tránh bị khuất.
        except tk.TclError:
            pass

        self.selected_algo = None
        self.is_auto_running = False
        self.after_id = None
        self.step_count = 0

        self.all_steps = []
        self.step_index = 0

        self.grid_vars = []
        self.agent_row_var = tk.StringVar(value="0")
        self.agent_col_var = tk.StringVar(value="0")

        self.create_ui()
        self.set_default_map()
        self.reset_runtime()
        self.draw_current_input()

   
    # UI


    def create_ui(self):
        self.root.grid_columnconfigure(0, minsize=180)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, minsize=240)
        self.root.grid_rowconfigure(0, weight=1)

        self.left = tk.Frame(self.root, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        self.left.grid(row=0, column=0, sticky="nsew")

        self.center = tk.Frame(self.root, bg=self.bg)
        self.center.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.center.grid_rowconfigure(1, weight=1)
        self.center.grid_columnconfigure(0, weight=1)

        self.right = tk.Frame(self.root, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        self.right.grid(row=0, column=2, sticky="nsew")
        self.right.grid_rowconfigure(1, weight=1)

        self.build_left_panel()
        self.build_center_panel()
        self.build_right_panel()

    def section_title(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text.upper(),
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9, "bold"),
            anchor="w",
        )
        lbl.pack(fill="x", padx=12, pady=(14, 6))

    def make_button(self, parent, text, command, accent=None):
        fg = accent or self.text
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg="#eeeeee",
            fg=fg,
            activebackground="#dddddd",
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=9,
            anchor="w",
        )
        btn.pack(fill="x", padx=12, pady=4)
        return btn

    def build_left_panel(self):
        self.section_title(self.left, "Thuật toán")

        self.btn_bfs = self.make_button(self.left, "BFS - Late Goal Test", lambda: self.select_algo("bfs"), self.accent)
        self.btn_bfs_e = self.make_button(self.left, "BFS - Early Goal Test", lambda: self.select_algo("bfs-e"), self.accent3)
        self.btn_dfs = self.make_button(self.left, "DFS - Late Goal Test", lambda: self.select_algo("dfs"), self.accent2)
        self.btn_dfs_e = self.make_button(self.left, "DFS - Early Goal Test", lambda: self.select_algo("dfs-e"), self.accent3)
        self.btn_ids = self.make_button(self.left, "IDS - Late Goal Test", lambda: self.select_algo("ids"), self.accent)
        self.btn_ids_e = self.make_button(self.left, "IDS - Early Goal Test", lambda: self.select_algo("ids-e"), self.accent3)
        self.btn_ucs = self.make_button(self.left, "UCS", lambda: self.select_algo("ucs"), self.accent)
        self.btn_astar = self.make_button(self.left, "A* Search", lambda: self.select_algo("astar"), self.accent2)
        self.btn_greedy = self.make_button(self.left, "Greedy Best-First", lambda: self.select_algo("greedy"), self.accent4)
        self.btn_idastar = self.make_button(self.left, "IDA* Search", lambda: self.select_algo("idastar"), self.accent2)
        self.btn_hc_simple = self.make_button(self.left, "HC - Leo dốc đơn giản", lambda: self.select_algo("hc_simple"), self.accent4)
        self.btn_hc_random = self.make_button(self.left, "HC - Leo dốc ngẫu nhiên", lambda: self.select_algo("hc_random"), self.accent4)
        self.btn_hc_steepest = self.make_button(self.left, "HC - Dốc nhất", lambda: self.select_algo("hc_steepest"), self.accent4)
        self.btn_lbs = self.make_button(self.left, "Local Beam Search", lambda: self.select_algo("local_beam"), self.accent4)

        self.algo_buttons = {
            "bfs":         self.btn_bfs,
            "bfs-e":       self.btn_bfs_e,
            "dfs":         self.btn_dfs,
            "dfs-e":       self.btn_dfs_e,
            "ids":         self.btn_ids,
            "ids-e":       self.btn_ids_e,
            "ucs":         self.btn_ucs,
            "astar":       self.btn_astar,
            "greedy":      self.btn_greedy,
            "idastar":     self.btn_idastar,
            "hc_simple":   self.btn_hc_simple,
            "hc_random":   self.btn_hc_random,
            "hc_steepest": self.btn_hc_steepest,
            "local_beam":  self.btn_lbs,
        }

        self.section_title(self.left, "Điều khiển")

        self.btn_auto = self.make_button(self.left, "Tự động", self.run_auto, self.accent)
        self.btn_step = self.make_button(self.left, "Từng bước", self.run_step, self.accent4)
        self.btn_show_result = self.make_button(self.left, "Hiển thị kết quả", self.show_result_now, self.accent3)
        self.btn_reset = self.make_button(self.left, "Reset", self.reset_all, self.accent2)
        self.btn_clear = self.make_button(self.left, "Xóa log", self.clear_log)

        tk.Label(
            self.left,
            text="Quy ước:\n0 = sạch\n1 = bụi\n2 = nội thất/vật cản\n\nLate: kiểm tra khi lấy ra xét.\nEarly: kiểm tra khi sinh ra.\nMục tiêu: hút hết bụi.\n\nIDS tăng dần giới hạn\nđộ sâu từ 0 → MAX.\n\nUCS: ưu tiên chi phí thấp\n(sinh hết, chọn min g).\nA*: f = g + h\nh = số ô bụi còn lại.\nGreedy: f = h (không\nđảm bảo tối ưu).",
            bg=self.panel,
            fg=self.muted,
            justify="left",
            font=("Arial", 9),
        ).pack(fill="x", padx=12, pady=20)

    def build_center_panel(self):
        input_panel = tk.Frame(self.center, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        input_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_panel.grid_columnconfigure(1, weight=1)

        tk.Label(
            input_panel,
            text="BẢN ĐỒ PHÒNG - nhập 0/1/2",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9, "bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="ew", padx=12, pady=(8, 4))

        grid_frame = tk.Frame(input_panel, bg=self.panel)
        grid_frame.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        self.grid_vars = []
        for r in range(ROWS):
            row_vars = []
            for c in range(COLS):
                var = tk.StringVar(value="0")
                entry = tk.Entry(
                    grid_frame,
                    textvariable=var,
                    width=3,
                    justify="center",
                    bg=self.cell_clean,
                    fg=self.text,
                    insertbackground=self.text,
                    relief="flat",
                    font=("Consolas", 14, "bold"),
                )
                entry.grid(row=r, column=c, padx=3, pady=3, ipady=5)

                def validate(*args, v=var, e=entry):
                    raw = v.get()
                    cleaned = "".join(ch for ch in raw if ch in "012")
                    if len(cleaned) > 1:
                        cleaned = cleaned[-1]
                    if raw != cleaned:
                        v.set(cleaned)
                    self.color_entry(e, cleaned)

                var.trace_add("write", validate)
                row_vars.append(var)
            self.grid_vars.append(row_vars)

        pos_frame = tk.Frame(input_panel, bg=self.panel)
        pos_frame.grid(row=1, column=1, padx=20, sticky="nw")

        tk.Label(pos_frame, text="Vị trí máy hút bụi", bg=self.panel, fg=self.text, font=("Arial", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        tk.Label(pos_frame, text="Hàng:", bg=self.panel, fg=self.muted, font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        tk.Entry(pos_frame, textvariable=self.agent_row_var, width=5, justify="center", bg="#ffffff", fg=self.text, insertbackground=self.text, relief="flat", font=("Consolas", 12)).grid(row=1, column=1, padx=6, pady=3)

        tk.Label(pos_frame, text="Cột:", bg=self.panel, fg=self.muted, font=("Arial", 10)).grid(row=2, column=0, sticky="w")
        tk.Entry(pos_frame, textvariable=self.agent_col_var, width=5, justify="center", bg="#ffffff", fg=self.text, insertbackground=self.text, relief="flat", font=("Consolas", 12)).grid(row=2, column=1, padx=6, pady=3)


        vis_frame = tk.Frame(self.center, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        vis_frame.grid(row=1, column=0, sticky="nsew")
        vis_frame.grid_rowconfigure(1, weight=1)
        vis_frame.grid_columnconfigure(0, weight=1)

        header = tk.Frame(vis_frame, bg=self.panel)
        header.grid(row=0, column=0, sticky="ew")

        self.vis_title = tk.Label(
            header,
            text="MÀN HÌNH MÔ PHỎNG",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 10, "bold"),
            anchor="w",
        )
        self.vis_title.pack(side="left", padx=12, pady=8)

        self.status_label = tk.Label(
            header,
            text="Sẵn sàng",
            bg="#eeeeee",
            fg=self.muted,
            font=("Consolas", 9),
            padx=10,
            pady=3,
        )
        self.status_label.pack(side="right", padx=12, pady=8)

        self.canvas = tk.Canvas(vis_frame, bg=self.panel, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        result_frame = tk.Frame(self.center, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        result_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        tk.Label(
            result_frame,
            text="KẾT QUẢ",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 2))

        self.result_label = tk.Label(
            result_frame,
            text="Chưa có kết quả",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 10),
            anchor="w",
            justify="left",
            wraplength=520,
        )
        self.result_label.pack(fill="x", padx=12, pady=(0, 8))

    def build_right_panel(self):
        header = tk.Frame(self.right, bg=self.panel)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(
            header,
            text="LOG TỪNG BƯỚC",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9, "bold"),
        ).pack(side="left", padx=12, pady=10)

        self.step_label = tk.Label(
            header,
            text="0 bước",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9),
        )
        self.step_label.pack(side="right", padx=12, pady=10)

        self.log_box = tk.Text(
            self.right,
            bg=self.panel,
            fg=self.muted,
            insertbackground=self.text,
            relief="flat",
            bd=0,
            font=("Consolas", 9),
            wrap="word",
        )
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.log_box.config(state="disabled")

    def color_entry(self, entry, value):
        if value == "1":
            entry.config(bg=self.cell_dirty, fg="#ffffff")
        elif value == "2":
            entry.config(bg=self.cell_wall, fg="#ffffff")
        else:
            entry.config(bg=self.cell_clean, fg=self.text)


    # DATA
  

    def set_default_map(self):
        default_grid = [
            [0, 1, 0, 0, 2],
            [0, 0, 2, 0, 0],
            [1, 0, 0, 0, 1],
            [0, 2, 0, 0, 0],
            [0, 0, 1, 2, 0],
        ]

        for r in range(ROWS):
            for c in range(COLS):
                self.grid_vars[r][c].set(str(default_grid[r][c]))

        self.agent_row_var.set("0")
        self.agent_col_var.set("0")

    def read_grid(self):
        grid = []
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                text = self.grid_vars[r][c].get().strip()
                row.append(int(text) if text != "" else 0)
            grid.append(row)
        return grid

    def read_agent_pos(self):
        try:
            r = int(self.agent_row_var.get())
            c = int(self.agent_col_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Vị trí máy hút bụi phải là số.")
            return None

        if not (0 <= r < ROWS and 0 <= c < COLS):
            messagebox.showerror("Lỗi", f"Vị trí phải nằm trong khoảng hàng 0-{ROWS-1}, cột 0-{COLS-1}.")
            return None

        return (r, c)

    def validate_input(self, grid, pos):
        if grid[pos[0]][pos[1]] == 2:
            messagebox.showerror("Lỗi", "Máy hút bụi không thể bắt đầu trên ô nội thất/vật cản.")
            return False
        return True

  
    # STATE HELPERS
  

    def grid_key(self, grid):
        return tuple(tuple(row) for row in grid)

    def state_key(self, grid, pos):
        return (self.grid_key(grid), pos)

    def count_dirty(self, grid):
        return sum(1 for row in grid for cell in row if cell == 1)

    def clone_grid(self, grid):
        return [row[:] for row in grid]

    def get_path(self, node):
        path = []
        cur = node
        while cur:
            path.insert(0, cur)
            cur = cur.parent
        return path

    def get_children(self, node):
        children = []
        r, c = node.pos

        # Nếu ô hiện tại có bụi, hành động ưu tiên là hút bụi.
        if node.grid[r][c] == 1:
            new_grid = self.clone_grid(node.grid)
            new_grid[r][c] = 0
            children.append(Node(new_grid, node.pos, node, "Hút bụi", node.depth + 1))
            return children

        for name, dr, dc, icon in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and node.grid[nr][nc] != 2:
                children.append(Node(self.clone_grid(node.grid), (nr, nc), node, f"Đi {name} {icon}", node.depth + 1))

        return children

  
    # SEARCH


    def build_steps(self, algo, start_grid, start_pos):
        if algo.startswith("ids"):
            return self.build_steps_ids(algo, start_grid, start_pos)
        if algo == "ucs":
            return self.build_steps_ucs(start_grid, start_pos)
        if algo == "astar":
            return self.build_steps_astar(start_grid, start_pos)
        if algo == "greedy":
            return self.build_steps_greedy(start_grid, start_pos)
        if algo == "idastar":
            return self.build_steps_idastar(start_grid, start_pos)
        if algo == "hc_simple":
            return self.build_steps_hc_simple(start_grid, start_pos)
        if algo == "hc_random":
            return self.build_steps_hc_random(start_grid, start_pos)
        if algo == "hc_steepest":
            return self.build_steps_hc_steepest(start_grid, start_pos)
        if algo == "local_beam":
            return self.build_steps_local_beam(start_grid, start_pos)

        steps = []

        is_early = algo.endswith("-e")
        is_bfs = algo.startswith("bfs")

        start_node = Node(start_grid, start_pos, None, "START", 0)
        frontier = deque([start_node]) if is_bfs else [start_node]
        visited = set([self.state_key(start_grid, start_pos)])
        expanded = 0

        algo_name = ("BFS" if is_bfs else "DFS") + (" - Early Goal Test" if is_early else " - Late Goal Test")

        steps.append({
            "type": "start",
            "node": start_node,
            "log": f"Khởi tạo {algo_name}. Máy hút bụi tại {start_pos}. Số ô bụi: {self.count_dirty(start_grid)}.",
        })

        # Early Goal Test: kiểm tra mục tiêu ngay khi trạng thái được tạo ra.
        if is_early and self.count_dirty(start_grid) == 0:
            steps.append({
                "type": "goal",
                "node": start_node,
                "path": [start_node],
                "log": "✓ START đã là trạng thái mục tiêu vì không còn bụi.",
            })
            return steps

        while frontier and expanded < MAX_STATES:
            node = frontier.popleft() if is_bfs else frontier.pop()
            expanded += 1

            dirty_left = self.count_dirty(node.grid)

            steps.append({
                "type": "visit",
                "node": node,
                "log": f"Xét trạng thái độ sâu {node.depth}, vị trí {node.pos}, còn {dirty_left} ô bụi.",
            })

            # Late Goal Test: chỉ kiểm tra mục tiêu khi lấy trạng thái ra để xét.
            if not is_early and dirty_left == 0:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "node": node,
                    "path": path,
                    "log": f"✓ Hoàn tất theo Late Goal Test! Đã hút sạch toàn bộ bụi sau {len(path)-1} hành động.",
                })
                return steps

            for child in self.get_children(node):
                key = self.state_key(child.grid, child.pos)

                if key in visited:
                    steps.append({
                        "type": "dup",
                        "node": child,
                        "log": f"  Bỏ qua trạng thái trùng: {child.action}, vị trí {child.pos}.",
                    })
                    continue

                visited.add(key)

                # Early Goal Test: kiểm tra ngay lúc vừa sinh trạng thái mới.
                if is_early and self.count_dirty(child.grid) == 0:
                    path = self.get_path(child)
                    steps.append({
                        "type": "gen",
                        "node": child,
                        "log": f"  Sinh trạng thái mới: {child.action}, vị trí {child.pos}, còn 0 ô bụi.",
                    })
                    steps.append({
                        "type": "goal",
                        "node": child,
                        "path": path,
                        "log": f"✓ Hoàn tất theo Early Goal Test! Trạng thái vừa sinh ra đã sạch bụi sau {len(path)-1} hành động.",
                    })
                    return steps

                frontier.append(child)

                steps.append({
                    "type": "gen",
                    "node": child,
                    "log": f"  Sinh trạng thái mới: {child.action}, vị trí {child.pos}, còn {self.count_dirty(child.grid)} ô bụi.",
                })

        steps.append({
            "type": "fail",
            "node": None,
            "log": "✗ Không tìm thấy cách hút sạch bụi trong giới hạn trạng thái.",
        })
        return steps

    def build_steps_ids(self, algo, start_grid, start_pos):
        """
        Iterative Deepening Search (IDS):
        - Chạy DFS có giới hạn độ sâu, tăng dần từ 0 đến MAX_DEPTH_IDS.
        - Mỗi lần lặp: khởi tạo lại visited để tránh chu trình trong lần lặp đó.
        - Late  (ids):   kiểm tra goal khi lấy node ra xét.
        - Early (ids-e): kiểm tra goal ngay khi sinh node con ra.
        """
        steps = []
        is_early = algo.endswith("-e")
        algo_name = "IDS" + (" - Early Goal Test" if is_early else " - Late Goal Test")

        start_node = Node(start_grid, start_pos, None, "START", 0)

        steps.append({
            "type": "start",
            "node": start_node,
            "log": (
                f"Khởi tạo {algo_name}. "
                f"Máy hút bụi tại {start_pos}. "
                f"Số ô bụi: {self.count_dirty(start_grid)}."
            ),
        })

        # Early Goal Test: kiểm tra ngay trạng thái đầu
        if is_early and self.count_dirty(start_grid) == 0:
            steps.append({
                "type": "goal",
                "node": start_node,
                "path": [start_node],
                "log": "✓ START đã là trạng thái mục tiêu vì không còn bụi.",
            })
            return steps

        total_expanded = 0

        for depth_limit in range(MAX_DEPTH_IDS + 1):

            # ── Tiêu đề lần lặp ──────────────────────────────────────────
            steps.append({
                "type": "iter",
                "node": start_node,
                "log": f"── Lặp IDS #{depth_limit}: giới hạn độ sâu = {depth_limit} ──",
            })

            # Mỗi lần lặp khởi tạo lại stack và visited
            stack = [start_node]
            visited = {self.state_key(start_grid, start_pos)}

            while stack:
                if total_expanded >= MAX_STATES:
                    steps.append({
                        "type": "fail",
                        "node": None,
                        "log": f"✗ Đã vượt giới hạn {MAX_STATES} trạng thái. Dừng.",
                    })
                    return steps

                node = stack.pop()
                total_expanded += 1
                dirty_left = self.count_dirty(node.grid)

                steps.append({
                    "type": "visit",
                    "node": node,
                    "log": (
                        f"  Xét: độ sâu {node.depth}/{depth_limit}, "
                        f"vị trí {node.pos}, còn {dirty_left} ô bụi."
                    ),
                })

                # ── Late Goal Test ────────────────────────────────────────
                if not is_early and dirty_left == 0:
                    path = self.get_path(node)
                    steps.append({
                        "type": "goal",
                        "node": node,
                        "path": path,
                        "log": (
                            f"✓ Tìm thấy! Late Goal Test tại độ sâu {node.depth} "
                            f"(lần lặp #{depth_limit}). "
                            f"{len(path)-1} hành động. "
                            f"Tổng node đã xét: {total_expanded}."
                        ),
                    })
                    return steps

                # Cắt tỉa nếu đạt giới hạn độ sâu
                if node.depth >= depth_limit:
                    steps.append({
                        "type": "dup",
                        "node": node,
                        "log": (
                            f"    Độ sâu {node.depth} "
                            f"đã đạt giới hạn {depth_limit}."
                        ),
                    })
                    continue

                # Sinh node con
                for child in self.get_children(node):
                    key = self.state_key(child.grid, child.pos)

                    if key in visited:
                        steps.append({
                            "type": "dup",
                            "node": child,
                            "log": (
                                f"    Bỏ qua trùng: {child.action}, "
                                f"vị trí {child.pos}."
                            ),
                        })
                        continue

                    visited.add(key)

                    # ── Early Goal Test ───────────────────────────────────
                    if is_early and self.count_dirty(child.grid) == 0:
                        path = self.get_path(child)
                        steps.append({
                            "type": "gen",
                            "node": child,
                            "log": (
                                f"    Sinh: {child.action}, "
                                f"vị trí {child.pos}, còn 0 ô bụi."
                            ),
                        })
                        steps.append({
                            "type": "goal",
                            "node": child,
                            "path": path,
                            "log": (
                                f"✓ Tìm thấy! Early Goal Test tại độ sâu {child.depth} "
                                f"(lần lặp #{depth_limit}). "
                                f"{len(path)-1} hành động. "
                                f"Tổng node đã xét: {total_expanded}."
                            ),
                        })
                        return steps

                    # Cho vào stack để xét sau
                    stack.append(child)
                    steps.append({
                        "type": "gen",
                        "node": child,
                        "log": (
                            f"    Sinh: {child.action}, "
                            f"vị trí {child.pos}, "
                            f"còn {self.count_dirty(child.grid)} ô bụi."
                        ),
                    })

        steps.append({
            "type": "fail",
            "node": None,
            "log": (
                f"✗ Không tìm thấy sau khi thử đến độ sâu {MAX_DEPTH_IDS}. "
                f"Tổng node đã xét: {total_expanded}."
            ),
        })
        return steps

    # ===========================
    # HEURISTIC
    # ===========================

    def heuristic_vacuum(self, grid):
        """
        Heuristic admissible: số ô bụi còn lại.
        Mỗi ô bụi cần ít nhất 1 hành động 'Hút bụi' → không bao giờ đánh giá cao hơn thực tế.
        Consistent: di chuyển không đổi h; hút bụi giảm h đúng 1 = chi phí hành động.
        """
        return self.count_dirty(grid)

    # ===========================
    # UCS
    # ===========================

    def build_steps_ucs(self, start_grid, start_pos):
        """
        UCS - Uniform Cost Search:
        - Dùng priority queue theo g (chi phí thực, mỗi hành động = 1).
        - Sinh hết node con rồi đưa vào hàng đợi, sau đó chọn node có g nhỏ nhất.
        - Chỉ Late Goal Test (đảm bảo đường đi tối ưu).
        - Closed set: một trạng thái chỉ xét 1 lần (lần đầu pop = chi phí tối ưu).
        """
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        counter = 0
        heap = [(0, counter, start_node)]
        visited = set()

        steps.append({
            "type": "start",
            "node": start_node,
            "log": (
                f"Khởi tạo UCS. Máy hút bụi tại {start_pos}. "
                f"Số ô bụi: {self.count_dirty(start_grid)}. "
                f"Đưa START vào hàng đợi ưu tiên (g=0)."
            ),
        })

        expanded = 0
        while heap and expanded < MAX_STATES:
            g, _, node = heapq.heappop(heap)
            key = self.state_key(node.grid, node.pos)

            if key in visited:
                continue
            visited.add(key)
            expanded += 1

            dirty_left = self.count_dirty(node.grid)

            steps.append({
                "type": "visit",
                "node": node,
                "log": f"Xét: g={g}, vị trí {node.pos}, còn {dirty_left} ô bụi.",
            })

            # Late Goal Test
            if dirty_left == 0:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "node": node,
                    "path": path,
                    "log": (
                        f"✓ Hoàn tất! UCS tìm thấy sau {expanded} node. "
                        f"Chi phí tối ưu g={g}. {len(path)-1} hành động."
                    ),
                })
                return steps

            # Sinh hết node con, đưa tất cả vào hàng đợi ưu tiên
            for child in self.get_children(node):
                child_key = self.state_key(child.grid, child.pos)
                if child_key in visited:
                    steps.append({
                        "type": "dup",
                        "node": child,
                        "log": f"  Bỏ qua trùng (đã xét tối ưu): {child.action}, vị trí {child.pos}.",
                    })
                    continue

                child_g = g + 1
                counter += 1
                heapq.heappush(heap, (child_g, counter, child))
                steps.append({
                    "type": "gen",
                    "node": child,
                    "log": (
                        f"  Sinh: {child.action}, vị trí {child.pos}, "
                        f"g={child_g}, còn {self.count_dirty(child.grid)} ô bụi → hàng đợi ưu tiên."
                    ),
                })

        steps.append({
            "type": "fail",
            "node": None,
            "log": f"✗ Không tìm thấy sau {expanded} node.",
        })
        return steps

    # ===========================
    # A* SEARCH
    # ===========================

    def build_steps_astar(self, start_grid, start_pos):
        """
        A* Search: f = g + h.
        - g = chi phí thực (số hành động đã thực hiện).
        - h = số ô bụi còn lại (admissible + consistent).
        - Closed set: tối ưu nhờ h consistent.
        - Late Goal Test.
        """
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        h_start = self.heuristic_vacuum(start_grid)
        f_start = 0 + h_start
        counter = 0
        heap = [(f_start, counter, start_node)]
        visited = set()

        steps.append({
            "type": "start",
            "node": start_node,
            "log": (
                f"Khởi tạo A*. Máy hút bụi tại {start_pos}. "
                f"Số ô bụi: {self.count_dirty(start_grid)}. "
                f"g=0, h={h_start}, f={f_start}."
            ),
        })

        expanded = 0
        while heap and expanded < MAX_STATES:
            f, _, node = heapq.heappop(heap)
            key = self.state_key(node.grid, node.pos)

            if key in visited:
                continue
            visited.add(key)
            expanded += 1

            g = node.depth
            h = self.heuristic_vacuum(node.grid)
            dirty_left = self.count_dirty(node.grid)

            steps.append({
                "type": "visit",
                "node": node,
                "log": f"Xét: g={g}, h={h}, f={g+h}, vị trí {node.pos}, còn {dirty_left} ô bụi.",
            })

            # Late Goal Test
            if dirty_left == 0:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "node": node,
                    "path": path,
                    "log": (
                        f"✓ Hoàn tất! A* tìm thấy sau {expanded} node. "
                        f"Chi phí tối ưu g={g}. {len(path)-1} hành động."
                    ),
                })
                return steps

            for child in self.get_children(node):
                child_key = self.state_key(child.grid, child.pos)
                if child_key in visited:
                    steps.append({
                        "type": "dup",
                        "node": child,
                        "log": f"  Bỏ qua trùng (đã xét tối ưu): {child.action}, vị trí {child.pos}.",
                    })
                    continue

                child_g = g + 1
                child_h = self.heuristic_vacuum(child.grid)
                child_f = child_g + child_h
                counter += 1
                heapq.heappush(heap, (child_f, counter, child))
                steps.append({
                    "type": "gen",
                    "node": child,
                    "log": (
                        f"  Sinh: {child.action}, vị trí {child.pos}, "
                        f"g={child_g}, h={child_h}, f={child_f}."
                    ),
                })

        steps.append({
            "type": "fail",
            "node": None,
            "log": f"✗ Không tìm thấy sau {expanded} node.",
        })
        return steps

    # ===========================
    # GREEDY BEST-FIRST SEARCH
    # ===========================

    def build_steps_greedy(self, start_grid, start_pos):
        """
        Greedy Best-First Search: f = h (chỉ dùng heuristic, không quan tâm g).
        - h = số ô bụi còn lại.
        - Nhanh nhưng KHÔNG đảm bảo đường đi tối ưu.
        - Late Goal Test + Closed Set.
        """
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        h_start = self.heuristic_vacuum(start_grid)
        counter = 0
        heap = [(h_start, counter, start_node)]
        visited = set()

        steps.append({
            "type": "start",
            "node": start_node,
            "log": (
                f"Khởi tạo Greedy Best-First. Máy hút bụi tại {start_pos}. "
                f"Số ô bụi: {self.count_dirty(start_grid)}. h={h_start}."
            ),
        })

        expanded = 0
        while heap and expanded < MAX_STATES:
            h_val, _, node = heapq.heappop(heap)
            key = self.state_key(node.grid, node.pos)

            if key in visited:
                continue
            visited.add(key)
            expanded += 1

            dirty_left = self.count_dirty(node.grid)

            steps.append({
                "type": "visit",
                "node": node,
                "log": f"Xét: h={h_val}, vị trí {node.pos}, còn {dirty_left} ô bụi.",
            })

            # Late Goal Test
            if dirty_left == 0:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "node": node,
                    "path": path,
                    "log": (
                        f"✓ Hoàn tất! Greedy tìm thấy sau {expanded} node. "
                        f"{len(path)-1} hành động. (Không đảm bảo tối ưu)"
                    ),
                })
                return steps

            for child in self.get_children(node):
                child_key = self.state_key(child.grid, child.pos)
                if child_key in visited:
                    steps.append({
                        "type": "dup",
                        "node": child,
                        "log": f"  Bỏ qua trùng: {child.action}, vị trí {child.pos}.",
                    })
                    continue

                child_h = self.heuristic_vacuum(child.grid)
                counter += 1
                heapq.heappush(heap, (child_h, counter, child))
                steps.append({
                    "type": "gen",
                    "node": child,
                    "log": (
                        f"  Sinh: {child.action}, vị trí {child.pos}, "
                        f"h={child_h}, còn {self.count_dirty(child.grid)} ô bụi."
                    ),
                })

        steps.append({
            "type": "fail",
            "node": None,
            "log": f"✗ Không tìm thấy sau {expanded} node.",
        })
        return steps

    # ===========================
    # IDA* SEARCH
    # ===========================

    def build_steps_idastar(self, start_grid, start_pos):
        """
        IDA* (Iterative Deepening A*):
        - Tăng dần ngưỡng f = g + h (h = số ô bụi còn lại).
        - Mỗi lần lặp: DFS cắt tỉa khi f > ngưỡng.
        - Tối ưu, tiết kiệm bộ nhớ hơn A*.
        """
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        h0 = self.heuristic_vacuum(start_grid)

        steps.append({
            "type": "start",
            "node": start_node,
            "log":  f"Khởi tạo IDA*. Máy hút bụi tại {start_pos}. h={h0}. Ngưỡng f ban đầu={h0}.",
        })

        if h0 == 0:
            steps.append({
                "type": "goal", "node": start_node, "path": [start_node],
                "log":  "✓ START đã là mục tiêu.",
            })
            return steps

        threshold      = h0
        total_expanded = 0
        MAX_IDA        = 3000

        while threshold <= 200 and total_expanded < MAX_IDA:
            steps.append({
                "type": "iter",
                "node": start_node,
                "log":  f"── Lặp IDA*: ngưỡng f = {threshold} ──",
            })

            stack          = [(start_node, 0)]
            next_threshold = float("inf")
            visited        = set()

            while stack:
                if total_expanded >= MAX_IDA:
                    steps.append({"type": "fail", "node": None,
                                  "log": f"✗ Vượt giới hạn {MAX_IDA} node."})
                    return steps

                node, g = stack.pop()
                key     = self.state_key(node.grid, node.pos)
                if key in visited:
                    continue
                visited.add(key)
                total_expanded += 1

                h   = self.heuristic_vacuum(node.grid)
                f   = g + h
                dirty_left = self.count_dirty(node.grid)

                steps.append({
                    "type": "visit",
                    "node": node,
                    "log":  f"  Xét: g={g}, h={h}, f={f} (ngưỡng={threshold}), vị trí {node.pos}, bụi còn {dirty_left}.",
                })

                if dirty_left == 0:
                    path = self.get_path(node)
                    steps.append({
                        "type": "goal", "node": node, "path": path,
                        "log":  f"✓ Hoàn tất! IDA* tìm thấy: g={g}, f={f}. Tổng node: {total_expanded}.",
                    })
                    return steps

                if f > threshold:
                    if f < next_threshold:
                        next_threshold = f
                    steps.append({
                        "type": "dup", "node": node,
                        "log":  f"  Cắt: f={f} > ngưỡng={threshold}.",
                    })
                    continue

                for child in self.get_children(node):
                    child_key = self.state_key(child.grid, child.pos)
                    if child_key not in visited:
                        stack.append((child, g + 1))
                        steps.append({
                            "type": "gen", "node": child,
                            "log":  f"  Sinh: {child.action}, vị trí {child.pos}, g={g+1}, h={self.heuristic_vacuum(child.grid)}.",
                        })

            if next_threshold == float("inf"):
                break
            threshold = next_threshold

        steps.append({"type": "fail", "node": None,
                      "log":  f"✗ IDA* không tìm thấy sau {total_expanded} node."})
        return steps

    # ===========================
    # HILL-CLIMBING — ĐƠN GIẢN
    # ===========================

    def build_steps_hc_simple(self, start_grid, start_pos):
        """
        Simple Hill-Climbing:
        - Chọn node con ĐẦU TIÊN có h < h(current).
        - Không backtrack. Dừng nếu không cải thiện.
        """
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        h_cur = self.heuristic_vacuum(start_grid)
        MAX_HC = 500

        steps.append({
            "type": "start", "node": start_node,
            "log":  f"Khởi tạo HC Đơn giản. Tại {start_pos}. h={h_cur} (số ô bụi).",
        })

        current = start_node
        itr     = 0
        visited = {self.state_key(start_grid, start_pos)}

        while itr < MAX_HC:
            itr += 1
            if self.count_dirty(current.grid) == 0:
                path = self.get_path(current)
                steps.append({
                    "type": "goal", "node": current, "path": path,
                    "log":  f"✓ HC Đơn giản: hút sạch tất cả bụi! Bước {itr}. {len(path)-1} hành động.",
                })
                return steps

            children = self.get_children(current)
            moved    = False

            for child in children:
                key     = self.state_key(child.grid, child.pos)
                h_child = self.heuristic_vacuum(child.grid)
                steps.append({
                    "type": "gen", "node": child,
                    "log":  f"  Kiểm tra: {child.action}, vị trí {child.pos}, h={h_child} vs h_cur={h_cur}.",
                })
                if h_child < h_cur and key not in visited:
                    steps.append({
                        "type": "visit", "node": child,
                        "log":  f"  ✔ Chọn ngay node đầu tiên tốt hơn: {child.action}, h {h_cur}→{h_child}.",
                    })
                    visited.add(key)
                    current = child
                    h_cur   = h_child
                    moved   = True
                    break

            if not moved:
                steps.append({
                    "type": "fail", "node": None,
                    "log":  f"✗ HC Đơn giản bị kẹt: h={h_cur}, vị trí {current.pos}. Không thể cải thiện.",
                })
                return steps

        steps.append({"type": "fail", "node": None,
                      "log": f"✗ HC Đơn giản vượt giới hạn {MAX_HC} bước."})
        return steps

    # ===========================
    # HILL-CLIMBING — NGẪU NHIÊN
    # ===========================

    def build_steps_hc_random(self, start_grid, start_pos):
        """
        Stochastic Hill-Climbing (Ngẫu nhiên):
        - Tập hợp tất cả con có h < h(current), chọn NGẪU NHIÊN một node.
        - Tăng đa dạng khám phá so với HC đơn giản.
        """
        import random
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        h_cur = self.heuristic_vacuum(start_grid)
        MAX_HC = 500

        steps.append({
            "type": "start", "node": start_node,
            "log":  f"Khởi tạo HC Ngẫu nhiên. Tại {start_pos}. h={h_cur}.",
        })

        current = start_node
        itr     = 0
        visited = {self.state_key(start_grid, start_pos)}

        while itr < MAX_HC:
            itr += 1
            if self.count_dirty(current.grid) == 0:
                path = self.get_path(current)
                steps.append({
                    "type": "goal", "node": current, "path": path,
                    "log":  f"✓ HC Ngẫu nhiên: hút sạch bụi! Bước {itr}. {len(path)-1} hành động.",
                })
                return steps

            children = self.get_children(current)
            better   = []

            for child in children:
                key     = self.state_key(child.grid, child.pos)
                h_child = self.heuristic_vacuum(child.grid)
                steps.append({
                    "type": "gen", "node": child,
                    "log":  f"  Đánh giá: {child.action}, vị trí {child.pos}, h={h_child}.",
                })
                if h_child < h_cur and key not in visited:
                    better.append((child, h_child, key))

            if not better:
                steps.append({
                    "type": "fail", "node": None,
                    "log":  f"✗ HC Ngẫu nhiên bị kẹt: h={h_cur}. Không có node tốt hơn.",
                })
                return steps

            chosen, chosen_h, chosen_key = random.choice(better)
            steps.append({
                "type": "visit", "node": chosen,
                "log":  f"  🎲 Chọn ngẫu nhiên từ {len(better)} node tốt hơn: {chosen.action}, h {h_cur}→{chosen_h}.",
            })
            visited.add(chosen_key)
            current = chosen
            h_cur   = chosen_h

        steps.append({"type": "fail", "node": None,
                      "log": f"✗ HC Ngẫu nhiên vượt giới hạn {MAX_HC} bước."})
        return steps

    # ===========================
    # HILL-CLIMBING — DỐC NHẤT
    # ===========================

    def build_steps_hc_steepest(self, start_grid, start_pos):
        """
        Steepest-Ascent Hill-Climbing (Dốc nhất):
        - Xét TẤT CẢ node con, chọn node có h NHỎ NHẤT.
        - Chỉ di chuyển nếu h_best < h_current.
        """
        steps = []
        start_node = Node(start_grid, start_pos, None, "START", 0)
        h_cur = self.heuristic_vacuum(start_grid)
        MAX_HC = 500

        steps.append({
            "type": "start", "node": start_node,
            "log":  f"Khởi tạo HC Dốc nhất. Tại {start_pos}. h={h_cur}.",
        })

        current = start_node
        itr     = 0
        visited = {self.state_key(start_grid, start_pos)}

        while itr < MAX_HC:
            itr += 1
            if self.count_dirty(current.grid) == 0:
                path = self.get_path(current)
                steps.append({
                    "type": "goal", "node": current, "path": path,
                    "log":  f"✓ HC Dốc nhất: hút sạch bụi! Bước {itr}. {len(path)-1} hành động.",
                })
                return steps

            children      = self.get_children(current)
            best_child    = None
            best_h        = h_cur
            best_key      = None

            for child in children:
                key     = self.state_key(child.grid, child.pos)
                h_child = self.heuristic_vacuum(child.grid)
                steps.append({
                    "type": "gen", "node": child,
                    "log":  f"  Đánh giá: {child.action}, vị trí {child.pos}, h={h_child}.",
                })
                if h_child < best_h and key not in visited:
                    best_h     = h_child
                    best_child = child
                    best_key   = key

            if best_child is None:
                steps.append({
                    "type": "fail", "node": None,
                    "log":  f"✗ HC Dốc nhất bị kẹt tại local optimum h={h_cur}. Vị trí {current.pos}.",
                })
                return steps

            steps.append({
                "type": "visit", "node": best_child,
                "log":  f"  ↑ Chọn TỐT NHẤT: {best_child.action}, vị trí {best_child.pos}, h {h_cur}→{best_h}.",
            })
            visited.add(best_key)
            current = best_child
            h_cur   = best_h

        steps.append({"type": "fail", "node": None,
                      "log": f"✗ HC Dốc nhất vượt giới hạn {MAX_HC} bước."})
        return steps


    # ===========================
    # LOCAL BEAM SEARCH
    # ===========================

    def build_steps_local_beam(self, start_grid, start_pos):
        """
        Local Beam Search:
        - Giữ đồng thời k trạng thái tốt nhất (beam).
        - Mỗi vòng sinh con từ toàn bộ beam, rồi chọn k node có h nhỏ nhất.
        - h = số ô bụi còn lại; không đảm bảo tối ưu nhưng thường thoát kẹt tốt hơn HC.
        """
        steps = []
        BEAM_WIDTH = 3
        MAX_BEAM_ITERS = 500

        start_node = Node(start_grid, start_pos, None, "START", 0)
        h_start = self.heuristic_vacuum(start_grid)
        beam = [start_node]
        visited = {self.state_key(start_grid, start_pos)}

        steps.append({
            "type": "start",
            "node": start_node,
            "log": (
                f"Khởi tạo Local Beam Search. k={BEAM_WIDTH}. "
                f"Máy hút bụi tại {start_pos}. h(start)={h_start}."
            ),
        })

        if self.count_dirty(start_grid) == 0:
            steps.append({
                "type": "goal",
                "node": start_node,
                "path": [start_node],
                "log": "✓ START đã là trạng thái mục tiêu vì không còn bụi.",
            })
            return steps

        expanded = 0
        for itr in range(1, MAX_BEAM_ITERS + 1):
            beam_info = ", ".join(
                f"{node.pos}/h={self.heuristic_vacuum(node.grid)}" for node in beam
            )
            steps.append({
                "type": "iter",
                "node": beam[0],
                "log": f"── Beam vòng {itr}: {len(beam)} trạng thái đang xét [{beam_info}] ──",
            })

            candidates = []
            for node in beam:
                expanded += 1
                dirty_left = self.count_dirty(node.grid)
                steps.append({
                    "type": "visit",
                    "node": node,
                    "log": f"Xét beam node: độ sâu {node.depth}, vị trí {node.pos}, còn {dirty_left} ô bụi.",
                })

                if dirty_left == 0:
                    path = self.get_path(node)
                    steps.append({
                        "type": "goal",
                        "node": node,
                        "path": path,
                        "log": f"✓ Local Beam Search tìm thấy lời giải sau {expanded} node. {len(path)-1} hành động.",
                    })
                    return steps

                for child in self.get_children(node):
                    key = self.state_key(child.grid, child.pos)
                    h_child = self.heuristic_vacuum(child.grid)

                    if key in visited:
                        steps.append({
                            "type": "dup",
                            "node": child,
                            "log": f"  Bỏ qua trùng: {child.action}, vị trí {child.pos}, h={h_child}.",
                        })
                        continue

                    visited.add(key)
                    candidates.append((h_child, child.depth, child))
                    steps.append({
                        "type": "gen",
                        "node": child,
                        "log": f"  Sinh ứng viên: {child.action}, vị trí {child.pos}, h={h_child}.",
                    })

                    if h_child == 0:
                        path = self.get_path(child)
                        steps.append({
                            "type": "goal",
                            "node": child,
                            "path": path,
                            "log": f"✓ Local Beam Search sinh ra trạng thái sạch bụi. {len(path)-1} hành động.",
                        })
                        return steps

            if not candidates:
                steps.append({
                    "type": "fail",
                    "node": None,
                    "log": "✗ Local Beam Search dừng: không còn ứng viên mới để mở rộng.",
                })
                return steps

            candidates.sort(key=lambda item: (item[0], item[1]))
            beam = [child for _, _, child in candidates[:BEAM_WIDTH]]
            chosen_info = ", ".join(
                f"{child.action}@{child.pos}/h={h}" for h, _, child in candidates[:BEAM_WIDTH]
            )
            steps.append({
                "type": "visit",
                "node": beam[0],
                "log": f"  Chọn {len(beam)} ứng viên tốt nhất cho beam kế tiếp: {chosen_info}.",
            })

            if expanded >= MAX_STATES:
                steps.append({
                    "type": "fail",
                    "node": None,
                    "log": f"✗ Local Beam Search vượt giới hạn {MAX_STATES} node.",
                })
                return steps

        steps.append({
            "type": "fail",
            "node": None,
            "log": f"✗ Local Beam Search vượt giới hạn {MAX_BEAM_ITERS} vòng lặp.",
        })
        return steps

  

    def clear_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            390,
            210,
            text="",
            fill=self.muted,
            font=("Consolas", 12),
            anchor="center",
        )

    def draw_grid(self, grid, pos, title=""):
        self.canvas.delete("all")

        # Lấy kích thước thật của canvas để tự co theo màn hình nhỏ.
        self.canvas.update_idletasks()
        w = max(self.canvas.winfo_width(), 320)
        h = max(self.canvas.winfo_height(), 260)

        # Trừ ít lề hơn để bản đồ không bị khuất khi cửa sổ nhỏ.
        cell_size = min((w - 40) // COLS, (h - 90) // ROWS, 70)
        cell_size = max(cell_size, 36)

        grid_width = cell_size * COLS
        start_x = max((w - grid_width) // 2, 10)
        start_y = 25

        # Không vẽ tiêu đề trên bản đồ để giao diện gọn và tự nhiên hơn.

        for r in range(ROWS):
            for c in range(COLS):
                x1 = start_x + c * cell_size
                y1 = start_y + r * cell_size
                x2 = x1 + cell_size - 4
                y2 = y1 + cell_size - 4

                value = grid[r][c]
                if value == 2:
                    fill = self.cell_wall
                    label = "2"
                    label_color = self.text
                elif value == 1:
                    fill = self.cell_dirty
                    label = "1"
                    label_color = self.text
                else:
                    fill = self.cell_clean
                    label = "0"
                    label_color = self.muted

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=self.border, width=2)
                self.canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=label,
                    fill=label_color,
                    font=("Consolas", 18, "bold"),
                )

                if (r, c) == pos:
                    self.canvas.create_oval(
                        x1 + 13,
                        y1 + 13,
                        x2 - 13,
                        y2 - 13,
                        fill=self.agent_color,
                        outline="#333333",
                        width=2,
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text="V",
                        fill=self.text,
                        font=("Arial", 18, "bold"),
                    )

        legend_y = min(start_y + ROWS * cell_size + 20, h - 18)
        legend = "0 = sạch    1 = bụi    2 = nội thất/vật cản    V = máy hút bụi"
        self.canvas.create_text(w // 2, legend_y, text=legend, fill=self.muted, font=("Consolas", 10))

    def draw_current_input(self):
        grid = self.read_grid()
        pos = self.read_agent_pos()
        if pos is not None:
            self.draw_grid(grid, pos, "Bản đồ hiện tại")

    def render_result(self, path):
        if not path:
            self.result_label.config(text="Không tìm thấy kết quả.")
            return

        actions = []
        for node in path[1:]:
            actions.append(node.action)

        self.result_label.config(
            text=f"Số hành động: {len(actions)} | " + " | ".join(actions)
        )

    # ===========================
    # LOG / STATUS
    # ===========================

    def log(self, msg):
        self.step_count += 1
        self.step_label.config(text=f"{self.step_count} bước")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{self.step_count}] {msg}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def clear_log(self):
        self.step_count = 0
        self.step_label.config(text="0 bước")
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def set_status(self, text, kind="ready"):
        colors = {
            "ready": (self.muted, "#eeeeee"),
            "running": (self.accent, "#e7f3ff"),
            "done": (self.accent3, "#e8f5e9"),
            "fail": (self.accent2, "#fdecea"),
        }
        fg, bg = colors.get(kind, colors["ready"])
        self.status_label.config(text=text, fg=fg, bg=bg)

    # ===========================
    # CONTROL
    # ===========================

    def select_algo(self, name):
        if self.is_auto_running:
            return

        self.selected_algo = name
        self.all_steps = []
        self.step_index = 0

        for algo, btn in self.algo_buttons.items():
            if algo == name:
                btn.config(bg="#d9edf7", fg=self.accent)
            else:
                btn.config(bg="#eeeeee")

        names = {
            "bfs":         "BFS - Late Goal Test",
            "bfs-e":       "BFS - Early Goal Test",
            "dfs":         "DFS - Late Goal Test",
            "dfs-e":       "DFS - Early Goal Test",
            "ids":         "IDS - Late Goal Test",
            "ids-e":       "IDS - Early Goal Test",
            "ucs":         "UCS - Uniform Cost Search",
            "astar":       "A* Search",
            "greedy":      "Greedy Best-First Search",
            "idastar":     "IDA* Search",
            "hc_simple":   "HC - Leo dốc đơn giản",
            "hc_random":   "HC - Leo dốc ngẫu nhiên",
            "hc_steepest": "HC - Dốc nhất (Steepest-Ascent)",
            "local_beam":  "Local Beam Search",
        }
        display_name = names[name]
        self.vis_title.config(text=display_name.upper())
        self.btn_auto.config(state="normal")
        self.btn_step.config(state="normal")
        self.btn_show_result.config(state="normal")
        self.log("Đã chọn: " + display_name)

    def prepare(self):
        if self.is_auto_running:
            return False

        if not self.selected_algo:
            messagebox.showwarning("Thiếu thuật toán", "Bạn hãy chọn BFS hoặc DFS trước.")
            return False

        grid = self.read_grid()
        pos = self.read_agent_pos()
        if pos is None:
            return False

        if not self.validate_input(grid, pos):
            return False

        if self.count_dirty(grid) == 0:
            messagebox.showinfo("Thông báo", "Bản đồ không có bụi để hút.")
            return False

        if not self.all_steps:
            self.clear_log()
            self.result_label.config(text="Chưa có kết quả")

            self.all_steps = self.build_steps(self.selected_algo, grid, pos)
            self.step_index = 0

            self.log(f"Bắt đầu {self.selected_algo.upper()}. Vị trí đầu: {pos}.")
            self.draw_grid(grid, pos, "START")
            self.step_index = 1

        return True

    def apply_step(self, step):
        if not step:
            return False

        self.log(step["log"])

        step_type = step["type"]

        if step_type in ("start", "visit", "gen"):
            node = step["node"]
            self.draw_grid(node.grid, node.pos, f"{step_type.upper()} - {node.action}")
        elif step_type in ("dup", "iter"):
            pass
        elif step_type == "goal":
            node = step["node"]
            self.draw_grid(node.grid, node.pos, "GOAL - ĐÃ HÚT SẠCH")
            self.render_result(step.get("path", []))
            self.finish_run()
            self.set_status("✓ Hoàn tất", "done")
            return False
        elif step_type == "fail":
            self.render_result([])
            self.finish_run()
            self.set_status("✗ Không tìm thấy", "fail")
            return False

        return True

    def show_result_now(self):
        """
        Chạy thuật toán ngay lập tức, không delay animation.
        Hàm này sẽ:
        - Tạo toàn bộ các bước
        - Ghi toàn bộ log
        - Hiển thị trạng thái kết quả cuối cùng
        - Hiển thị chuỗi hành động
        """
        if self.is_auto_running:
            return

        if not self.prepare():
            return

        self.set_status("⚡ Đang hiển thị kết quả...", "running")
        self.btn_auto.config(state="disabled")
        self.btn_step.config(state="disabled")
        self.btn_show_result.config(state="disabled")

        # Chạy hết các bước còn lại ngay lập tức.
        while self.step_index < len(self.all_steps):
            step = self.all_steps[self.step_index]
            self.step_index += 1

            self.log(step["log"])
            step_type = step["type"]

            if step_type == "goal":
                node = step["node"]
                self.draw_grid(node.grid, node.pos, "GOAL - ĐÃ HÚT SẠCH")
                self.render_result(step.get("path", []))
                self.set_status("✓ Hoàn tất", "done")
                self.finish_run()
                return

            if step_type == "fail":
                self.render_result([])
                self.set_status("✗ Không tìm thấy", "fail")
                self.finish_run()
                return

        self.finish_run()

    def run_auto(self):
        if not self.prepare():
            return

        self.is_auto_running = True
        self.set_status("Đang chạy...", "running")
        self.btn_auto.config(state="disabled")
        self.btn_step.config(state="disabled")
        self.btn_show_result.config(state="disabled")

        def tick():
            if self.step_index >= len(self.all_steps):
                self.finish_run()
                return

            cont = self.apply_step(self.all_steps[self.step_index])
            self.step_index += 1

            if cont:
                self.after_id = self.root.after(SPEED, tick)

        tick()

    def run_step(self):
        if self.is_auto_running:
            return

        if not self.prepare():
            return

        self.set_status("Đang chạy từng bước", "running")

        if self.step_index >= len(self.all_steps):
            self.finish_run()
            return

        cont = self.apply_step(self.all_steps[self.step_index])
        self.step_index += 1

        if not cont:
            self.btn_step.config(state="disabled")

    def finish_run(self):
        self.is_auto_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.btn_auto.config(state="normal")
        self.btn_step.config(state="disabled")
        self.btn_show_result.config(state="normal" if self.selected_algo else "disabled")

    def reset_runtime(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.selected_algo = None
        self.is_auto_running = False
        self.all_steps = []
        self.step_index = 0

        for btn in self.algo_buttons.values():
            btn.config(bg="#eeeeee")

        self.btn_auto.config(state="disabled")
        self.btn_step.config(state="disabled")
        self.btn_show_result.config(state="disabled")

        self.clear_log()
        self.clear_canvas()
        self.result_label.config(text="Chưa có kết quả")
        self.vis_title.config(text="MÀN HÌNH MÔ PHỎNG")
        self.set_status("Sẵn sàng", "ready")

    def reset_all(self):
        self.reset_runtime()
        self.draw_current_input()


if __name__ == "__main__":
    root = tk.Tk()
    app = VacuumApp(root)
    root.mainloop()
