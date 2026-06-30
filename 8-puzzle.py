

# https://github.com/TDO196/Agent_ThucHanh_TriTueNhanTao



import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq


# 8-PUZZLE giao diện 


MOVES = [
    ("Len", -1, 0, "↑"),
    ("Xuong", 1, 0, "↓"),
    ("Trai", 0, -1, "←"),
    ("Phai", 0, 1, "→"),
]

SPEED = 600
MAX_NODES = 500
MAX_NODES_IDS = 2000
MAX_DEPTH_IDS = 30


class Node:
    def __init__(self, state, parent=None, depth=0, move="START"):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.move = move


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle - bài tập trí tuệ nhân tạo")
        self.root.geometry("1280x720")
        self.root.minsize(1100, 650)

        # Theme
        self.bg = "#fef3b5"
        self.panel = "#ffffff"
        self.border = "#2a2a45"
        self.accent = "#ffffff"
        self.accent2 = "#ffffff"
        self.accent3 = "#ffffff"
        self.accent4 = "#ffffff"
        self.text = "#e8e8f0"
        self.muted = "#000000"
        self.tile_bg = "#1e1e35"

        self.root.configure(bg=self.bg)

        self.selected_algo = None
        self.is_auto_running = False
        self.step_count = 0
        self.all_steps = []
        self.step_index = 0
        self.after_id = None
        self.node_label_counter = 0

        self.start_vars = []
        self.goal_vars = []

        self.create_ui()
        self.create_default_grids()
        self.reset_all()

   
    # UI
    
    def create_ui(self):
        self.root.grid_columnconfigure(0, minsize=220)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, minsize=290)
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
        return lbl

    def make_button(self, parent, text, command, accent=None):
        fg = accent or self.text
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.tile_bg,
            fg=fg,
            activebackground="#1a1a35",
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=10,
            pady=9,
            anchor="w",
        )
        btn.pack(fill="x", padx=12, pady=4)
        return btn

    def build_left_panel(self):
        self.section_title(self.left, "Thuật toán")

        self.algo_name_to_key = {
            "BFS - Late Goal Test": "bfs",
            "BFS - Early Goal Test": "bfs-e",
            "DFS - Late Goal Test": "dfs",
            "DFS - Early Goal Test": "dfs-e",
            "IDS - Late Goal Test": "ids",
            "IDS - Early Goal Test": "ids-e",
            "UCS - Uniform Cost Search": "ucs",
            "A* Search": "astar",
            "Greedy Best-First Search": "greedy",
            "IDA* Search": "idastar",
            "Heuristic Functions Generation": "heuristic_gen",
            "HC - Leo dốc đơn giản": "hc_simple",
            "HC - Leo dốc ngẫu nhiên": "hc_random",
            "HC - Dốc nhất (Steepest)": "hc_steepest",
            "Local Beam Search": "local_beam",
            "Simulated Annealing": "simulated_annealing",
        }

        algo_frame = tk.Frame(self.left, bg=self.panel)
        algo_frame.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(
            algo_frame,
            text="Chọn thuật toán:",
            bg=self.panel,
            fg=self.muted,
            font=("Arial", 9, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.algo_var = tk.StringVar(value="")
        self.algo_menu = ttk.Combobox(
            algo_frame,
            textvariable=self.algo_var,
            values=list(self.algo_name_to_key.keys()),
            state="readonly",
            font=("Arial", 10),
        )
        self.algo_menu.pack(fill="x")
        self.algo_menu.bind("<<ComboboxSelected>>", self.on_algo_selected)

        # Giữ dict rỗng để tương thích các hàm cũ (đã bỏ các nút thuật toán riêng).
        self.algo_buttons = {}

        self.section_title(self.left, "Điều khiển")

        self.btn_auto = self.make_button(self.left, "Tự động", self.run_auto, self.accent)
        self.btn_step = self.make_button(self.left, "Từng bước", self.run_step, self.accent4)
        self.btn_reset = self.make_button(self.left, "Reset", self.reset_all, self.accent2)
        self.btn_clear = self.make_button(self.left, "Xóa log", self.clear_log, self.text)

        tk.Label(
            self.left,
            text="Gợi ý:\n1. Chọn thuật toán\n2. Nhập START/GOAL\n3. Bấm Tự động hoặc Từng bước",
            bg=self.panel,
            fg=self.muted,
            justify="left",
            font=("Arial", 9),
        ).pack(fill="x", padx=12, pady=20)

    def build_center_panel(self):
        input_frame = tk.Frame(self.center, bg=self.bg)
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)

        self.start_box = self.make_grid_box(input_frame, "START")
        self.start_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.goal_box = self.make_grid_box(input_frame, "GOAL")
        self.goal_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))

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
            bg="#222235",
            fg=self.muted,
            font=("Consolas", 9),
            padx=10,
            pady=3,
        )
        self.status_label.pack(side="right", padx=12, pady=8)

        canvas_holder = tk.Frame(vis_frame, bg=self.panel)
        canvas_holder.grid(row=1, column=0, sticky="nsew")
        canvas_holder.grid_rowconfigure(0, weight=1)
        canvas_holder.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_holder, bg=self.panel, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.h_scroll = tk.Scrollbar(canvas_holder, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.h_scroll.set)

        self.solution_frame = tk.Frame(self.center, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        self.solution_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        tk.Label(
            self.solution_frame,
            text="GIẢI PHÁP CUỐI CÙNG - CHUỖI CÁC BƯỚC",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 2))

        self.solution_label = tk.Label(
            self.solution_frame,
            text="Chưa có kết quả",
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 10),
            anchor="w",
            justify="left",
            wraplength=760,
        )
        self.solution_label.pack(fill="x", padx=12, pady=(0, 8))

    def make_grid_box(self, parent, title):
        outer = tk.Frame(parent, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        tk.Label(
            outer,
            text=title.upper(),
            bg=self.panel,
            fg=self.muted,
            font=("Consolas", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 4))

        grid = tk.Frame(outer, bg=self.panel)
        grid.pack(padx=12, pady=(0, 10), anchor="w")
        outer.grid_widget = grid
        return outer

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

    def create_default_grids(self):
        start_default = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        goal_default = [1, 2, 3, 4, 5, 6, 7, 8, 0]

        self.start_vars = self.create_grid_inputs(self.start_box.grid_widget, start_default)
        self.goal_vars = self.create_grid_inputs(self.goal_box.grid_widget, goal_default)

    def create_grid_inputs(self, parent, values):
        vars_list = []
        for i, value in enumerate(values):
            var = tk.StringVar(value=str(value))
            entry = tk.Entry(
                parent,
                textvariable=var,
                width=3,
                justify="center",
                bg=self.tile_bg,
                fg=self.text,
                insertbackground=self.text,
                relief="flat",
                font=("Consolas", 16, "bold"),
            )
            entry.grid(row=i // 3, column=i % 3, padx=3, pady=3, ipady=6)

            def validate_var(*args, v=var):
                raw = v.get()
                cleaned = "".join(ch for ch in raw if ch in "012345678")
                if len(cleaned) > 1:
                    cleaned = cleaned[-1]
                if raw != cleaned:
                    v.set(cleaned)

            var.trace_add("write", validate_var)
            vars_list.append(var)
        return vars_list

   
    # PUZZLE HELPERS
 

    def state_key(self, arr):
        return ",".join(map(str, arr))

    def blank_pos(self, arr):
        return arr.index(0)

    def to_rc(self, idx):
        return idx // 3, idx % 3

    def to_idx(self, r, c):
        return r * 3 + c

    def get_children(self, arr):
        children = []
        bi = self.blank_pos(arr)
        br, bc = self.to_rc(bi)

        for name, dr, dc, icon in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr <= 2 and 0 <= nc <= 2:
                ni = self.to_idx(nr, nc)
                next_state = arr[:]
                next_state[bi], next_state[ni] = next_state[ni], next_state[bi]
                children.append({"state": next_state, "move": name, "icon": icon})
        return children

    def get_path(self, node):
        path = []
        cur = node
        while cur:
            path.insert(0, {"state": cur.state, "move": cur.move})
            cur = cur.parent
        return path

    def next_node_label(self):
        n = self.node_label_counter
        self.node_label_counter += 1
        if n < 26:
            return chr(65 + n)
        return chr(65 + n // 26 - 1) + chr(65 + n % 26)

    def move_icon(self, move_name):
        mapping = {
            "Len": "↑",
            "Xuong": "↓",
            "Trai": "←",
            "Phai": "→",
            "START": "START",
        }
        return mapping.get(move_name, "?")

  
    # READ / VALIDATE


    def read_grid(self, vars_list):
        arr = []
        for v in vars_list:
            text = v.get().strip()
            arr.append(int(text) if text != "" else 0)
        return arr

    def validate_grid(self, arr, name):
        if sorted(arr) != list(range(9)):
            messagebox.showerror("Lỗi dữ liệu", f"{name}: Phải chứa đủ các số từ 0 đến 8, không trùng số.")
            return False
        return True

   
    # LOG / STATUS


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
            "ready": (self.muted, "#222235"),
            "running": (self.accent, "#102b34"),
            "done": (self.accent3, "#183020"),
            "fail": (self.accent2, "#341616"),
        }
        fg, bg = colors.get(kind, colors["ready"])
        self.status_label.config(text=text, fg=fg, bg=bg)

    # ===========================
    # RENDER
    # ===========================

    def clear_vis(self):
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 1000, 400))
        self.canvas.create_text(
            420,
            180,
            fill=self.muted,
            font=("Consolas", 12),
            anchor="center",
        )

    def render_state_card(self, state, label, card_type="normal", changed_idx=None):
        if changed_idx is None:
            changed_idx = []

        # Remove placeholder if present
        all_items = self.canvas.find_all()
        if len(all_items) == 1:
            self.canvas.delete(all_items[0])

        card_index = len(getattr(self, "rendered_cards", []))
        x = 30 + card_index * 150
        y = 45

        if card_index > 0:
            self.canvas.create_text(x - 28, y + 72, text="→", fill=self.muted, font=("Arial", 18, "bold"))

        label_color = self.accent if card_type == "current" else self.accent3 if card_type == "goal" else self.muted
        border_color = self.accent if card_type == "current" else self.accent3 if card_type == "goal" else self.border

        self.canvas.create_text(x + 50, y - 18, text=label, fill=label_color, font=("Consolas", 9, "bold"))

        cell = 32
        gap = 4
        grid_x = x
        grid_y = y

        self.canvas.create_rectangle(
            grid_x - 6,
            grid_y - 6,
            grid_x + 3 * cell + 2 * gap + 6,
            grid_y + 3 * cell + 2 * gap + 6,
            outline=border_color,
            width=2,
            fill=self.tile_bg,
        )

        for idx, value in enumerate(state):
            r, c = idx // 3, idx % 3
            x1 = grid_x + c * (cell + gap)
            y1 = grid_y + r * (cell + gap)
            x2 = x1 + cell
            y2 = y1 + cell

            if value == 0:
                fill = self.tile_bg
                outline = self.tile_bg
                txt = ""
            elif card_type == "goal":
                fill = "#213a28"
                outline = self.accent3
                txt = str(value)
            elif idx in changed_idx:
                fill = "#113642"
                outline = self.accent
                txt = str(value)
            else:
                fill = "#252540"
                outline = "#353560"
                txt = str(value)

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline)
            self.canvas.create_text(
                (x1 + x2) // 2,
                (y1 + y2) // 2,
                text=txt,
                fill=self.text,
                font=("Consolas", 13, "bold"),
            )

        self.rendered_cards.append(True)
        total_width = x + 180
        self.canvas.configure(scrollregion=(0, 0, max(total_width, self.canvas.winfo_width()), 300))
        self.canvas.xview_moveto(1)

    def render_solution(self, path):
        if not path:
            self.solution_label.config(text="Không tìm thấy đường đi")
            return

        parts = []
        for idx, item in enumerate(path):
            if idx == 0:
                parts.append("START")
            else:
                parts.append(self.move_icon(item["move"]))
        moves = " ".join(parts)
        self.solution_label.config(text=f"Số bước di chuyển: {len(path) - 1} | {moves}")

 
    # BUILD STEPS


    def build_steps(self, algo, start, goal):
        if algo.startswith("ids"):
            return self.build_steps_ids(algo, start, goal)
        if algo == "ucs":
            return self.build_steps_ucs(start, goal)
        if algo == "astar":
            return self.build_steps_astar(start, goal)
        if algo == "greedy":
            return self.build_steps_greedy(start, goal)
        if algo == "idastar":
            return self.build_steps_idastar(start, goal)
        if algo == "hc_simple":
            return self.build_steps_hc_simple(start, goal)
        if algo == "hc_random":
            return self.build_steps_hc_random(start, goal)
        if algo == "hc_steepest":
            return self.build_steps_hc_steepest(start, goal)
        if algo == "local_beam":
            return self.build_steps_local_beam(start, goal)
        if algo == "heuristic_gen":
            return self.build_steps_heuristic_gen(start, goal)
        if algo == "simulated_annealing":
            return self.build_steps_simulated_annealing(start, goal)

        goal_key = self.state_key(goal)
        steps = []
        is_early = algo.endswith("-e")
        is_bfs = algo.startswith("bfs")

        start_node = Node(start, None, 0, "START")
        frontier = deque([start_node]) if is_bfs else [start_node]
        visited = set()
        label_map = {self.state_key(start): "S0"}

        steps.append({
            "type": "expand",
            "state": start,
            "label": "S0",
            "log": "Khởi tạo. Đưa START (S0) vào " + ("hàng đợi." if is_bfs else "stack."),
        })

        if is_early and self.state_key(start) == goal_key:
            steps.append({
                "type": "goal",
                "state": start,
                "label": "GOAL!",
                "path": [{"state": start, "move": "START"}],
                "log": "START chính là GOAL.",
            })
            return steps

        visited.add(self.state_key(start))
        gen_count = 0
        exp_count = 0

        while frontier and gen_count < MAX_NODES:
            node = frontier.popleft() if is_bfs else frontier.pop()
            exp_count += 1
            node_label = label_map.get(self.state_key(node.state), f"N{exp_count}")

            if not is_early and self.state_key(node.state) == goal_key:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "state": node.state,
                    "label": node_label + " = GOAL",
                    "path": path,
                    "log": f"✓ Tìm thấy GOAL = {node_label}. Độ sâu: {node.depth}.",
                })
                return steps

            steps.append({
                "type": "expand",
                "state": node.state,
                "label": "Xét " + node_label,
                "log": f"Xét node {node_label} {node.state} - Độ sâu {node.depth}.",
            })

            children = self.get_children(node.state)
            for child in children:
                gen_count += 1
                ck = self.state_key(child["state"])

                changed = []
                for i, v in enumerate(child["state"]):
                    if v != node.state[i]:
                        changed.append(i)

                if is_early and ck == goal_key:
                    child_label = self.next_node_label()
                    label_map[ck] = child_label
                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    path = self.get_path(child_node)

                    steps.append({
                        "type": "goal",
                        "state": child["state"],
                        "label": child_label + " = GOAL!",
                        "changed": changed,
                        "path": path,
                        "log": f"✓ Sinh ra GOAL = {child_label} ({child['icon']}). Độ sâu: {node.depth + 1}.",
                    })
                    return steps

                if ck in visited:
                    dup_label = label_map.get(ck, "?")
                    steps.append({
                        "type": "dup",
                        "state": child["state"],
                        "label": "Dup",
                        "changed": changed,
                        "log": f"  Sinh {child['state']} ({child['icon']}) - TRÙNG với {dup_label}, bỏ qua.",
                    })
                else:
                    child_label = self.next_node_label()
                    label_map[ck] = child_label
                    visited.add(ck)
                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    frontier.append(child_node)

                    steps.append({
                        "type": "gen",
                        "state": child["state"],
                        "label": child_label,
                        "changed": changed,
                        "log": f"  Sinh {child_label} {child['state']} ({child['icon']}) → " + ("hàng đợi." if is_bfs else "stack."),
                    })

        steps.append({
            "type": "fail",
            "log": f"✗ Không tìm thấy lời giải sau {exp_count} node xét.",
        })
        return steps

    def build_steps_ids(self, algo, start, goal):
        """
        IDS = lặp DFS có giới hạn độ sâu tăng dần từ 0 đến MAX_DEPTH_IDS.

        Mỗi lần lặp:
          - Bước "iter": xóa canvas, reset card, vẽ lại S0 từ đầu.
          - Chạy DLS (Depth-Limited Search) bằng stack.
          - Dùng visited riêng cho từng lần lặp (tránh chu trình trong lần đó).

        Late  (ids):   kiểm tra goal khi lấy node ra khỏi stack.
        Early (ids-e): kiểm tra goal ngay khi sinh node con.
        """
        is_early  = algo.endswith("-e")
        goal_key  = self.state_key(goal)
        start_key = self.state_key(start)
        steps     = []

        # ── Bước 0: khởi tạo — bị prepare() bỏ qua (step_index=1),
        #    chỉ dùng để log dòng đầu tiên qua prepare().
        algo_name = "IDS - " + ("Early" if is_early else "Late") + " Goal Test"
        steps.append({
            "type":  "expand",
            "state": start,
            "label": "S0",
            "log":   f"Khởi tạo {algo_name}. Đưa START (S0) vào stack.",
        })

        # Early: kiểm tra ngay trạng thái đầu
        if is_early and start_key == goal_key:
            steps.append({
                "type":  "goal",
                "state": start,
                "label": "GOAL!",
                "path":  [{"state": start, "move": "START"}],
                "log":   "START chính là GOAL.",
            })
            return steps

        total_expanded = 0

        for depth_limit in range(MAX_DEPTH_IDS + 1):

            # ── Tiêu đề lần lặp: xóa canvas, vẽ lại S0 ──────────────────
            steps.append({
                "type":        "iter",
                "state":       start,
                "depth_limit": depth_limit,
                "log":         f"── Lặp IDS #{depth_limit}: giới hạn độ sâu = {depth_limit} ──",
            })

            start_node = Node(start, None, 0, "START")
            stack      = [start_node]
            visited    = {start_key}
            label_map  = {start_key: "S0"}
            exp_count  = 0

            while stack:
                if total_expanded >= MAX_NODES_IDS:
                    steps.append({
                        "type": "fail",
                        "log":  f"✗ Đã xét {total_expanded} node, vượt giới hạn {MAX_NODES_IDS}. Dừng.",
                    })
                    return steps

                node = stack.pop()
                exp_count     += 1
                total_expanded += 1
                node_key   = self.state_key(node.state)
                node_label = label_map.get(node_key, f"N{exp_count}")

                steps.append({
                    "type":  "expand",
                    "state": node.state,
                    "label": node_label,
                    "log":   f"Xét {node_label} {node.state} - Độ sâu {node.depth}/{depth_limit}.",
                })

                # ── Late Goal Test ────────────────────────────────────────
                if not is_early and node_key == goal_key:
                    path = self.get_path(node)
                    steps.append({
                        "type":  "goal",
                        "state": node.state,
                        "label": node_label + " = GOAL",
                        "path":  path,
                        "log":   (
                            f"✓ Tìm thấy GOAL = {node_label}. "
                            f"Độ sâu: {node.depth} (lặp #{depth_limit}). "
                            f"Tổng node đã xét: {total_expanded}."
                        ),
                    })
                    return steps

                # Cắt tỉa: đạt giới hạn độ sâud
                if node.depth >= depth_limit:
                    steps.append({
                        "type":  "dup",
                        "state": node.state,
                        "label": "✂",
                        "log":   f"  Độ sâu {node.depth} đạt giới hạn {depth_limit}.",
                    })
                    continue

                # ── Sinh node con ─────────────────────────────────────────
                children = self.get_children(node.state)
                for child in children:
                    ck = self.state_key(child["state"])
                    changed = [i for i, v in enumerate(child["state"]) if v != node.state[i]]

                    # Early Goal Test: kiểm tra ngay khi sinh ra
                    if is_early and ck == goal_key:
                        child_label = self.next_node_label()
                        label_map[ck] = child_label
                        child_node = Node(child["state"], node, node.depth + 1, child["move"])
                        path = self.get_path(child_node)

                        steps.append({
                            "type":    "gen",
                            "state":   child["state"],
                            "label":   child_label,
                            "changed": changed,
                            "log":     f"  Sinh {child_label} {child['state']} ({child['icon']}) → stack.",
                        })
                        steps.append({
                            "type":    "goal",
                            "state":   child["state"],
                            "label":   child_label + " = GOAL!",
                            "changed": changed,
                            "path":    path,
                            "log":     (
                                f"✓ Sinh ra GOAL = {child_label} ({child['icon']}). "
                                f"Độ sâu: {node.depth + 1} (lặp #{depth_limit}). "
                                f"Tổng node đã xét: {total_expanded}."
                            ),
                        })
                        return steps

                    if ck in visited:
                        dup_label = label_map.get(ck, "?")
                        steps.append({
                            "type":    "dup",
                            "state":   child["state"],
                            "label":   "Dup",
                            "changed": changed,
                            "log":     f"  Sinh {child['state']} ({child['icon']}) - TRÙNG với {dup_label}, bỏ qua.",
                        })
                    else:
                        child_label = self.next_node_label()
                        label_map[ck] = child_label
                        visited.add(ck)
                        child_node = Node(child["state"], node, node.depth + 1, child["move"])
                        stack.append(child_node)

                        steps.append({
                            "type":    "gen",
                            "state":   child["state"],
                            "label":   child_label,
                            "changed": changed,
                            "log":     f"  Sinh {child_label} {child['state']} ({child['icon']}) → stack.",
                        })

        steps.append({
            "type": "fail",
            "log":  (
                f"✗ Không tìm thấy lời giải sau khi thử đến độ sâu {MAX_DEPTH_IDS}. "
                f"Tổng node đã xét: {total_expanded}."
            ),
        })
        return steps

    # ===========================
    # HEURISTIC
    # ===========================

    def heuristic_puzzle(self, state, goal):
        """
        Manhattan distance: tổng khoảng cách Manhattan của từng ô về vị trí đúng.
        Admissible + Consistent → A* tối ưu với closed set.
        """
        total = 0
        for i, v in enumerate(state):
            if v != 0:
                gi = goal.index(v)
                total += abs(i // 3 - gi // 3) + abs(i % 3 - gi % 3)
        return total

    # ===========================
    # UCS
    # ===========================

    def build_steps_ucs(self, start, goal):
        """
        UCS - Uniform Cost Search:
        - Priority queue theo g (chi phí thực, mỗi hành động = 1).
        - Sinh hết node con, đưa tất cả vào hàng đợi, rồi chọn node có g nhỏ nhất.
        - Chỉ Late Goal Test → đảm bảo đường đi tối ưu.
        - Closed set: trạng thái pop lần đầu là tối ưu.
        """
        goal_key = self.state_key(goal)
        steps = []

        start_node = Node(start, None, 0, "START")
        counter = 0
        heap = [(0, counter, start_node)]
        visited = set()
        label_map = {self.state_key(start): "S0"}
        expanded = 0

        steps.append({
            "type": "expand",
            "state": start,
            "label": "S0",
            "log": "Khởi tạo UCS. Đưa START (S0) vào hàng đợi ưu tiên (g=0).",
        })

        while heap and expanded < MAX_NODES:
            g, _, node = heapq.heappop(heap)
            key = self.state_key(node.state)

            if key in visited:
                continue
            visited.add(key)
            expanded += 1

            node_label = label_map.get(key, f"N{expanded}")

            # Late Goal Test
            if key == goal_key:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "state": node.state,
                    "label": node_label + " = GOAL",
                    "path": path,
                    "log": (
                        f"✓ Tìm thấy GOAL = {node_label}. "
                        f"Chi phí tối ưu g={g}. Độ sâu: {node.depth}."
                    ),
                })
                return steps

            steps.append({
                "type": "expand",
                "state": node.state,
                "label": "Xét " + node_label,
                "log": f"Xét {node_label} {node.state} - g={g}, Độ sâu {node.depth}.",
            })

            # Sinh hết node con rồi đưa vào hàng đợi
            for child in self.get_children(node.state):
                ck = self.state_key(child["state"])
                changed = [i for i, v in enumerate(child["state"]) if v != node.state[i]]
                new_g = g + 1

                if ck in visited:
                    dup_label = label_map.get(ck, "?")
                    steps.append({
                        "type": "dup",
                        "state": child["state"],
                        "label": "Dup",
                        "changed": changed,
                        "log": f"  {child['state']} ({child['icon']}) - TRÙNG với {dup_label} (đã xét tối ưu), bỏ qua.",
                    })
                else:
                    child_label = label_map.get(ck)
                    if not child_label:
                        child_label = self.next_node_label()
                        label_map[ck] = child_label

                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    counter += 1
                    heapq.heappush(heap, (new_g, counter, child_node))

                    steps.append({
                        "type": "gen",
                        "state": child["state"],
                        "label": child_label,
                        "changed": changed,
                        "log": f"  Sinh {child_label} {child['state']} ({child['icon']}) → g={new_g}.",
                    })

        steps.append({
            "type": "fail",
            "log": f"✗ Không tìm thấy sau {expanded} node.",
        })
        return steps

    # ===========================
    # A* SEARCH
    # ===========================

    def build_steps_astar(self, start, goal):
        """
        A* Search: f = g + h (Manhattan distance).
        - g = chi phí thực (số bước đã đi).
        - h = Manhattan distance → admissible + consistent.
        - Closed set hợp lệ nhờ h consistent.
        - Late Goal Test → đảm bảo tối ưu.
        """
        goal_key = self.state_key(goal)
        steps = []

        start_node = Node(start, None, 0, "START")
        h_start = self.heuristic_puzzle(start, goal)
        f_start = 0 + h_start
        counter = 0
        heap = [(f_start, counter, start_node)]
        visited = set()
        label_map = {self.state_key(start): "S0"}
        expanded = 0

        steps.append({
            "type": "expand",
            "state": start,
            "label": "S0",
            "log": (
                f"Khởi tạo A*. g=0, h={h_start} (Manhattan), f={f_start}. "
                f"Đưa START (S0) vào hàng đợi ưu tiên."
            ),
        })

        while heap and expanded < MAX_NODES:
            f, _, node = heapq.heappop(heap)
            key = self.state_key(node.state)

            if key in visited:
                continue
            visited.add(key)
            expanded += 1

            g = node.depth
            h = self.heuristic_puzzle(node.state, goal)
            node_label = label_map.get(key, f"N{expanded}")

            # Late Goal Test
            if key == goal_key:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "state": node.state,
                    "label": node_label + " = GOAL",
                    "path": path,
                    "log": (
                        f"✓ Tìm thấy GOAL = {node_label}. "
                        f"g={g}, h={h}, f={g+h}. Độ sâu: {node.depth}."
                    ),
                })
                return steps

            steps.append({
                "type": "expand",
                "state": node.state,
                "label": "Xét " + node_label,
                "log": f"Xét {node_label} {node.state} - g={g}, h={h}, f={g+h}.",
            })

            for child in self.get_children(node.state):
                ck = self.state_key(child["state"])
                changed = [i for i, v in enumerate(child["state"]) if v != node.state[i]]

                if ck in visited:
                    dup_label = label_map.get(ck, "?")
                    steps.append({
                        "type": "dup",
                        "state": child["state"],
                        "label": "Dup",
                        "changed": changed,
                        "log": f"  {child['state']} ({child['icon']}) - TRÙNG với {dup_label} (đã xét tối ưu), bỏ qua.",
                    })
                else:
                    child_g = g + 1
                    child_h = self.heuristic_puzzle(child["state"], goal)
                    child_f = child_g + child_h

                    child_label = label_map.get(ck)
                    if not child_label:
                        child_label = self.next_node_label()
                        label_map[ck] = child_label

                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    counter += 1
                    heapq.heappush(heap, (child_f, counter, child_node))

                    steps.append({
                        "type": "gen",
                        "state": child["state"],
                        "label": child_label,
                        "changed": changed,
                        "log": (
                            f"  Sinh {child_label} {child['state']} ({child['icon']}) "
                            f"→ g={child_g}, h={child_h}, f={child_f}."
                        ),
                    })

        steps.append({
            "type": "fail",
            "log": f"✗ Không tìm thấy sau {expanded} node.",
        })
        return steps

    # ===========================
    # GREEDY BEST-FIRST SEARCH
    # ===========================

    def build_steps_greedy(self, start, goal):
        """
        Greedy Best-First Search: f = h (chỉ dùng heuristic, không quan tâm g).
        - h = Manhattan distance.
        - Nhanh nhưng KHÔNG đảm bảo tối ưu.
        - Late Goal Test + Closed Set.
        """
        goal_key = self.state_key(goal)
        steps = []

        start_node = Node(start, None, 0, "START")
        h_start = self.heuristic_puzzle(start, goal)
        counter = 0
        heap = [(h_start, counter, start_node)]
        visited = set()
        label_map = {self.state_key(start): "S0"}
        expanded = 0

        steps.append({
            "type": "expand",
            "state": start,
            "label": "S0",
            "log": (
                f"Khởi tạo Greedy Best-First. h={h_start} (Manhattan). "
                f"Đưa START (S0) vào hàng đợi."
            ),
        })

        while heap and expanded < MAX_NODES:
            h_val, _, node = heapq.heappop(heap)
            key = self.state_key(node.state)

            if key in visited:
                continue
            visited.add(key)
            expanded += 1

            node_label = label_map.get(key, f"N{expanded}")

            # Late Goal Test
            if key == goal_key:
                path = self.get_path(node)
                steps.append({
                    "type": "goal",
                    "state": node.state,
                    "label": node_label + " = GOAL",
                    "path": path,
                    "log": (
                        f"✓ Tìm thấy GOAL = {node_label}. "
                        f"Greedy không đảm bảo tối ưu. Độ sâu: {node.depth}."
                    ),
                })
                return steps

            steps.append({
                "type": "expand",
                "state": node.state,
                "label": "Xét " + node_label,
                "log": f"Xét {node_label} {node.state} - h={h_val} (Greedy).",
            })

            for child in self.get_children(node.state):
                ck = self.state_key(child["state"])
                changed = [i for i, v in enumerate(child["state"]) if v != node.state[i]]

                if ck in visited:
                    dup_label = label_map.get(ck, "?")
                    steps.append({
                        "type": "dup",
                        "state": child["state"],
                        "label": "Dup",
                        "changed": changed,
                        "log": f"  {child['state']} ({child['icon']}) - TRÙNG với {dup_label}, bỏ qua.",
                    })
                else:
                    child_h = self.heuristic_puzzle(child["state"], goal)

                    child_label = label_map.get(ck)
                    if not child_label:
                        child_label = self.next_node_label()
                        label_map[ck] = child_label

                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    counter += 1
                    heapq.heappush(heap, (child_h, counter, child_node))

                    steps.append({
                        "type": "gen",
                        "state": child["state"],
                        "label": child_label,
                        "changed": changed,
                        "log": f"  Sinh {child_label} {child['state']} ({child['icon']}) → h={child_h}.",
                    })

        steps.append({
            "type": "fail",
            "log": f"✗ Không tìm thấy sau {expanded} node.",
        })
        return steps

    # ===========================
    # IDA* SEARCH
    # ===========================

    def build_steps_idastar(self, start, goal):
        """
        IDA* (Iterative Deepening A*):
        - Tăng dần ngưỡng f = g + h (bắt đầu từ h(start)).
        - Mỗi lần lặp: DFS giới hạn bởi ngưỡng f thay vì độ sâu.
        - Tối ưu nếu h admissible. Tiết kiệm bộ nhớ hơn A*.
        - Late Goal Test.
        """
        goal_key = self.state_key(goal)
        steps = []

        h0 = self.heuristic_puzzle(start, goal)
        steps.append({
            "type":  "expand",
            "state": start,
            "label": "S0",
            "log":   f"Khởi tạo IDA*. h(start)={h0}. Ngưỡng f ban đầu = {h0}.",
        })

        threshold = h0
        total_expanded = 0
        MAX_IDA = 2000

        while threshold <= 100 and total_expanded < MAX_IDA:
            # ── Tiêu đề lần lặp ──────────────────────────────────────────
            steps.append({
                "type":        "iter",
                "state":       start,
                "depth_limit": threshold,
                "log":         f"── Lặp IDA*: ngưỡng f = {threshold} ──",
            })

            start_node = Node(start, None, 0, "START")
            stack = [(start_node, 0)]       # (node, g)
            next_threshold = float("inf")
            label_counter_backup = self.node_label_counter
            self.node_label_counter = 0
            label_map = {self.state_key(start): "S0"}

            found = False
            while stack:
                if total_expanded >= MAX_IDA:
                    steps.append({
                        "type": "fail",
                        "log":  f"✗ Đã xét {total_expanded} node, vượt giới hạn {MAX_IDA}. Dừng.",
                    })
                    return steps

                node, g = stack.pop()
                node_key   = self.state_key(node.state)
                node_label = label_map.get(node_key, f"N{total_expanded}")
                h = self.heuristic_puzzle(node.state, goal)
                f = g + h
                total_expanded += 1

                steps.append({
                    "type":  "expand",
                    "state": node.state,
                    "label": node_label,
                    "log":   f"Xét {node_label} {node.state} g={g}, h={h}, f={f} (ngưỡng={threshold}).",
                })

                if node_key == goal_key:
                    path = self.get_path(node)
                    steps.append({
                        "type":  "goal",
                        "state": node.state,
                        "label": node_label + " = GOAL",
                        "path":  path,
                        "log":   f"✓ Tìm thấy GOAL! g={g}, h={h}, f={f}. Tổng node xét: {total_expanded}.",
                    })
                    return steps

                if f > threshold:
                    if f < next_threshold:
                        next_threshold = f
                    steps.append({
                        "type":  "dup",
                        "state": node.state,
                        "label": "✂f",
                        "log":   f"  Cắt: f={f} > ngưỡng={threshold}. next_threshold={next_threshold}.",
                    })
                    continue

                children = self.get_children(node.state)
                # push đảo ngược để xét thứ tự đúng
                for child in reversed(children):
                    ck = self.state_key(child["state"])
                    changed = [i for i, v in enumerate(child["state"]) if v != node.state[i]]
                    child_label = label_map.get(ck)
                    if not child_label:
                        child_label = self.next_node_label()
                        label_map[ck] = child_label
                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    stack.append((child_node, g + 1))
                    steps.append({
                        "type":    "gen",
                        "state":   child["state"],
                        "label":   child_label,
                        "changed": changed,
                        "log":     f"  Sinh {child_label} {child['state']} ({child['icon']}) → stack.",
                    })

            if next_threshold == float("inf"):
                break
            threshold = next_threshold

        steps.append({
            "type": "fail",
            "log":  f"✗ IDA* không tìm thấy sau {total_expanded} node.",
        })
        return steps

    # ===========================
    # HILL-CLIMBING — ĐƠN GIẢN
    # ===========================

    def build_steps_hc_simple(self, start, goal):
        """
        Hill-Climbing đơn giản (Simple Hill-Climbing):
        - Chọn node con ĐẦU TIÊN có h < h(current).
        - Không backtrack. Dừng khi không cải thiện (local optimum / plateau).
        - Không đảm bảo tìm thấy lời giải tối ưu.
        """
        goal_key  = self.state_key(goal)
        steps     = []
        MAX_HC    = 500

        steps.append({
            "type":  "expand",
            "state": start,
            "label": "S0",
            "log":   f"Khởi tạo HC Đơn giản. h(start)={self.heuristic_puzzle(start, goal)}.",
        })

        current = Node(start, None, 0, "START")
        h_cur   = self.heuristic_puzzle(start, goal)
        itr     = 0
        visited = {self.state_key(start)}

        while itr < MAX_HC:
            itr += 1
            cur_key = self.state_key(current.state)

            if cur_key == goal_key:
                path = self.get_path(current)
                steps.append({
                    "type":  "goal",
                    "state": current.state,
                    "label": "GOAL!",
                    "path":  path,
                    "log":   f"✓ Tìm thấy GOAL! h=0. Bước thứ {itr}.",
                })
                return steps

            children = self.get_children(current.state)
            moved    = False

            for child in children:
                ck = self.state_key(child["state"])
                h_child = self.heuristic_puzzle(child["state"], goal)
                changed  = [i for i, v in enumerate(child["state"]) if v != current.state[i]]

                steps.append({
                    "type":    "gen",
                    "state":   child["state"],
                    "label":   f"h={h_child}",
                    "changed": changed,
                    "log":     f"  Kiểm tra {child['state']} ({child['icon']}) h={h_child} vs h_cur={h_cur}.",
                })

                if h_child < h_cur and ck not in visited:
                    child_node = Node(child["state"], current, current.depth + 1, child["move"])
                    steps.append({
                        "type":  "expand",
                        "state": child["state"],
                        "label": f"Chọn h={h_child}",
                        "log":   f"  ✔ Chọn ngay node đầu tiên tốt hơn: h {h_cur}→{h_child}. Bước {itr}.",
                    })
                    visited.add(ck)
                    current = child_node
                    h_cur   = h_child
                    moved   = True
                    break

            if not moved:
                steps.append({
                    "type": "fail",
                    "log":  f"✗ HC Đơn giản bị kẹt tại local optimum h={h_cur}. Không tìm được lời giải.",
                })
                return steps

        steps.append({"type": "fail", "log": f"✗ HC Đơn giản vượt giới hạn {MAX_HC} bước."})
        return steps

    # ===========================
    # HILL-CLIMBING — NGẪU NHIÊN
    # ===========================

    def build_steps_hc_random(self, start, goal):
        """
        Hill-Climbing ngẫu nhiên (Stochastic Hill-Climbing):
        - Tập hợp tất cả node con có h < h(current).
        - Chọn ngẫu nhiên MỘT trong số các node tốt hơn đó.
        - Khác HC đơn giản: không phải luôn chọn node đầu tiên.
        """
        import random
        goal_key  = self.state_key(goal)
        steps     = []
        MAX_HC    = 500

        h_start = self.heuristic_puzzle(start, goal)
        steps.append({
            "type":  "expand",
            "state": start,
            "label": "S0",
            "log":   f"Khởi tạo HC Ngẫu nhiên. h(start)={h_start}.",
        })

        current = Node(start, None, 0, "START")
        h_cur   = h_start
        itr     = 0
        visited = {self.state_key(start)}

        while itr < MAX_HC:
            itr += 1
            cur_key = self.state_key(current.state)

            if cur_key == goal_key:
                path = self.get_path(current)
                steps.append({
                    "type":  "goal",
                    "state": current.state,
                    "label": "GOAL!",
                    "path":  path,
                    "log":   f"✓ Tìm thấy GOAL! h=0. Bước thứ {itr}.",
                })
                return steps

            children   = self.get_children(current.state)
            better     = []

            for child in children:
                ck      = self.state_key(child["state"])
                h_child = self.heuristic_puzzle(child["state"], goal)
                changed  = [i for i, v in enumerate(child["state"]) if v != current.state[i]]
                steps.append({
                    "type":    "gen",
                    "state":   child["state"],
                    "label":   f"h={h_child}",
                    "changed": changed,
                    "log":     f"  Đánh giá {child['state']} ({child['icon']}) h={h_child}.",
                })
                if h_child < h_cur and ck not in visited:
                    better.append((child, h_child, ck))

            if not better:
                steps.append({
                    "type": "fail",
                    "log":  f"✗ HC Ngẫu nhiên bị kẹt tại local optimum h={h_cur}. Không tìm được lời giải.",
                })
                return steps

            chosen_child, chosen_h, chosen_k = random.choice(better)
            child_node = Node(chosen_child["state"], current, current.depth + 1, chosen_child["move"])
            changed = [i for i, v in enumerate(chosen_child["state"]) if v != current.state[i]]
            steps.append({
                "type":    "expand",
                "state":   chosen_child["state"],
                "label":   f"Chọn ngẫu h={chosen_h}",
                "changed": changed,
                "log":     f"  🎲 Chọn ngẫu nhiên từ {len(better)} node tốt hơn: {chosen_child['state']} h={chosen_h}. Bước {itr}.",
            })
            visited.add(chosen_k)
            current = child_node
            h_cur   = chosen_h

        steps.append({"type": "fail", "log": f"✗ HC Ngẫu nhiên vượt giới hạn {MAX_HC} bước."})
        return steps

    # ===========================
    # HILL-CLIMBING — DỐC NHẤT
    # ===========================

    def build_steps_hc_steepest(self, start, goal):
        """
        Steepest-Ascent Hill-Climbing (Dốc nhất):
        - Xét TẤT CẢ node con, chọn node có h NHỎ NHẤT (tốt nhất).
        - Chỉ di chuyển nếu h_best < h_current (không đi ngang / đi lên).
        - Không đảm bảo tối ưu toàn cục.
        """
        goal_key  = self.state_key(goal)
        steps     = []
        MAX_HC    = 500

        h_start = self.heuristic_puzzle(start, goal)
        steps.append({
            "type":  "expand",
            "state": start,
            "label": "S0",
            "log":   f"Khởi tạo HC Dốc nhất. h(start)={h_start}.",
        })

        current = Node(start, None, 0, "START")
        h_cur   = h_start
        itr     = 0
        visited = {self.state_key(start)}

        while itr < MAX_HC:
            itr += 1
            cur_key = self.state_key(current.state)

            if cur_key == goal_key:
                path = self.get_path(current)
                steps.append({
                    "type":  "goal",
                    "state": current.state,
                    "label": "GOAL!",
                    "path":  path,
                    "log":   f"✓ Tìm thấy GOAL! h=0. Bước thứ {itr}.",
                })
                return steps

            children    = self.get_children(current.state)
            best_child  = None
            best_h      = h_cur
            best_ck     = None

            for child in children:
                ck      = self.state_key(child["state"])
                h_child = self.heuristic_puzzle(child["state"], goal)
                changed  = [i for i, v in enumerate(child["state"]) if v != current.state[i]]
                steps.append({
                    "type":    "gen",
                    "state":   child["state"],
                    "label":   f"h={h_child}",
                    "changed": changed,
                    "log":     f"  Đánh giá {child['state']} ({child['icon']}) h={h_child}.",
                })
                if h_child < best_h and ck not in visited:
                    best_h     = h_child
                    best_child = child
                    best_ck    = ck

            if best_child is None:
                steps.append({
                    "type": "fail",
                    "log":  f"✗ HC Dốc nhất bị kẹt tại local optimum h={h_cur}. Không tìm được lời giải.",
                })
                return steps

            child_node = Node(best_child["state"], current, current.depth + 1, best_child["move"])
            changed    = [i for i, v in enumerate(best_child["state"]) if v != current.state[i]]
            steps.append({
                "type":    "expand",
                "state":   best_child["state"],
                "label":   f"Best h={best_h}",
                "changed": changed,
                "log":     f"  ↑ Chọn node TỐT NHẤT trong tất cả: {best_child['state']} h={best_h} (h_cur={h_cur}). Bước {itr}.",
            })
            visited.add(best_ck)
            current = child_node
            h_cur   = best_h

        steps.append({"type": "fail", "log": f"✗ HC Dốc nhất vượt giới hạn {MAX_HC} bước."})
        return steps


    # ===========================
    # LOCAL BEAM SEARCH
    # ===========================

    def build_steps_local_beam(self, start, goal):
        """
        Local Beam Search:
        - Giữ đồng thời k trạng thái tốt nhất (beam).
        - Mỗi vòng sinh con từ toàn bộ beam, rồi chọn k node có h nhỏ nhất.
        - h = Manhattan distance; không đảm bảo tối ưu như A*.
        """
        goal_key = self.state_key(goal)
        steps = []
        BEAM_WIDTH = 3
        MAX_BEAM_ITERS = 500

        h_start = self.heuristic_puzzle(start, goal)
        start_node = Node(start, None, 0, "START")
        beam = [start_node]
        visited = {self.state_key(start)}
        label_map = {self.state_key(start): "S0"}

        steps.append({
            "type": "expand",
            "state": start,
            "label": "S0",
            "log": f"Khởi tạo Local Beam Search. k={BEAM_WIDTH}. h(start)={h_start}.",
        })

        if self.state_key(start) == goal_key:
            steps.append({
                "type": "goal",
                "state": start,
                "label": "GOAL!",
                "path": [{"state": start, "move": "START"}],
                "log": "START chính là GOAL.",
            })
            return steps

        expanded = 0
        for itr in range(1, MAX_BEAM_ITERS + 1):
            beam_info = ", ".join(
                f"{label_map.get(self.state_key(node.state), '?')}/h={self.heuristic_puzzle(node.state, goal)}"
                for node in beam
            )
            steps.append({
                "type": "dup",
                "state": beam[0].state,
                "label": "Beam",
                "log": f"── Beam vòng {itr}: {len(beam)} trạng thái đang xét [{beam_info}] ──",
            })

            candidates = []
            for node in beam:
                expanded += 1
                node_key = self.state_key(node.state)
                node_label = label_map.get(node_key, "?")
                h_cur = self.heuristic_puzzle(node.state, goal)

                steps.append({
                    "type": "expand",
                    "state": node.state,
                    "label": f"Xét {node_label}",
                    "log": f"Xét beam node {node_label} {node.state} - h={h_cur}, độ sâu {node.depth}.",
                })

                if node_key == goal_key:
                    path = self.get_path(node)
                    steps.append({
                        "type": "goal",
                        "state": node.state,
                        "label": node_label + " = GOAL",
                        "path": path,
                        "log": f"✓ Local Beam Search tìm thấy GOAL sau {expanded} node. Độ sâu: {node.depth}.",
                    })
                    return steps

                for child in self.get_children(node.state):
                    ck = self.state_key(child["state"])
                    h_child = self.heuristic_puzzle(child["state"], goal)
                    changed = [i for i, v in enumerate(child["state"]) if v != node.state[i]]

                    if ck in visited:
                        dup_label = label_map.get(ck, "?")
                        steps.append({
                            "type": "dup",
                            "state": child["state"],
                            "label": "Dup",
                            "changed": changed,
                            "log": f"  Bỏ qua trùng {child['state']} ({child['icon']}) với {dup_label}, h={h_child}.",
                        })
                        continue

                    child_label = self.next_node_label()
                    label_map[ck] = child_label
                    visited.add(ck)
                    child_node = Node(child["state"], node, node.depth + 1, child["move"])
                    candidates.append((h_child, child_node.depth, child_label, child_node, changed))

                    steps.append({
                        "type": "gen",
                        "state": child["state"],
                        "label": f"{child_label} h={h_child}",
                        "changed": changed,
                        "log": f"  Sinh ứng viên {child_label} {child['state']} ({child['icon']}) h={h_child}.",
                    })

                    if ck == goal_key:
                        path = self.get_path(child_node)
                        steps.append({
                            "type": "goal",
                            "state": child["state"],
                            "label": child_label + " = GOAL!",
                            "changed": changed,
                            "path": path,
                            "log": f"✓ Local Beam Search sinh ra GOAL = {child_label}. Độ sâu: {child_node.depth}.",
                        })
                        return steps

            if not candidates:
                steps.append({
                    "type": "fail",
                    "log": "✗ Local Beam Search dừng: không còn ứng viên mới để mở rộng.",
                })
                return steps

            candidates.sort(key=lambda item: (item[0], item[1]))
            chosen = candidates[:BEAM_WIDTH]
            beam = [child_node for _, _, _, child_node, _ in chosen]
            chosen_info = ", ".join(f"{label}/h={h}" for h, _, label, _, _ in chosen)
            best_h, _, best_label, best_node, best_changed = chosen[0]

            steps.append({
                "type": "expand",
                "state": best_node.state,
                "label": f"Beam: {chosen_info}",
                "changed": best_changed,
                "log": f"  Chọn {len(beam)} node tốt nhất cho beam kế tiếp: {chosen_info}.",
            })

            if expanded >= MAX_NODES_IDS:
                steps.append({
                    "type": "fail",
                    "log": f"✗ Local Beam Search vượt giới hạn {MAX_NODES_IDS} node.",
                })
                return steps

        steps.append({
            "type": "fail",
            "log": f"✗ Local Beam Search vượt giới hạn {MAX_BEAM_ITERS} vòng lặp.",
        })
        return steps

   

    # ===========================
    # CHỌN THUẬT TOÁN TỪ DROPDOWN
    # ===========================

    def on_algo_selected(self, event):
        selection = self.algo_var.get()
        key = self.algo_name_to_key.get(selection)
        if key:
            self.select_algo(key)

    # ===========================
    # HEURISTIC FUNCTIONS GENERATION (A* với h1 vs h2)
    # ===========================

    def _misplaced(self, state, goal):
        """h1 = số ô (khác trống) đang sai vị trí (bài toán nới lỏng)."""
        return sum(1 for i, v in enumerate(state) if v != 0 and v != goal[i])

    def _astar_run(self, start, goal, hfunc):
        """Chạy A* (f = g + h) không tạo bước; trả về (số node mở rộng, path hoặc None)."""
        goal_key = self.state_key(goal)
        counter = 0
        heap = [(hfunc(start, goal), counter, Node(start, None, 0, "START"))]
        visited = set()
        expanded = 0
        CAP = 100000
        while heap and expanded < CAP:
            f, _, node = heapq.heappop(heap)
            key = self.state_key(node.state)
            if key in visited:
                continue
            visited.add(key)
            expanded += 1
            if key == goal_key:
                return expanded, self.get_path(node)
            g = node.depth + 1
            for child in self.get_children(node.state):
                ck = self.state_key(child["state"])
                if ck in visited:
                    continue
                counter += 1
                heapq.heappush(
                    heap,
                    (g + hfunc(child["state"], goal), counter,
                     Node(child["state"], node, node.depth + 1, child["move"])),
                )
        return expanded, None

    def build_steps_heuristic_gen(self, start, goal):
        """
        Sinh hàm heuristic từ bài toán NỚI LỎNG (Russell & Norvig, ví dụ 8-puzzle):
          - h1 = số ô sai vị trí (nới lỏng: ô được phép nhảy tới bất kỳ đâu).
          - h2 = tổng khoảng cách Manhattan (nới lỏng: ô đi 1 bước bất kỳ hướng).
        Cả hai đều admissible; h2(n) >= h1(n) nên h2 "trội" hơn -> A* dùng h2
        mở rộng ít node hơn mà vẫn cho lời giải tối ưu.
        """
        steps = []
        h1 = self._misplaced(start, goal)
        h2 = self.heuristic_puzzle(start, goal)

        steps.append({
            "type": "expand",
            "state": start,
            "label": "S0",
            "log": (
                "Sinh heuristic từ bài toán nới lỏng:\n"
                "  • h1 = số ô sai vị trí.\n"
                "  • h2 = tổng khoảng cách Manhattan.\n"
                f"  Tại START: h1={h1}, h2={h2} (h2 >= h1 nên h2 trội hơn)."
            ),
        })

        n1, path1 = self._astar_run(start, goal, self._misplaced)
        steps.append({
            "type": "expand",
            "state": start,
            "label": f"A* + h1 ({n1} nút)",
            "log": (
                f"A* dùng h1 (số ô sai vị trí): mở rộng {n1} node"
                + (f", lời giải tối ưu {len(path1) - 1} bước." if path1
                   else ", không tìm thấy trong giới hạn.")
            ),
        })

        n2, path2 = self._astar_run(start, goal, self.heuristic_puzzle)
        steps.append({
            "type": "expand",
            "state": start,
            "label": f"A* + h2 ({n2} nút)",
            "log": (
                f"A* dùng h2 (Manhattan): mở rộng {n2} node"
                + (f", lời giải tối ưu {len(path2) - 1} bước." if path2
                   else ", không tìm thấy trong giới hạn.")
            ),
        })

        if path1 and path2:
            verdict = ("h2 mở ÍT node hơn h1" if n2 < n1
                       else "h2 mở bằng h1" if n2 == n1
                       else "bất thường: h1 ít node hơn")
            steps.append({
                "type": "expand",
                "state": start,
                "label": "So sánh",
                "log": (
                    f"So sánh: h1 -> {n1} node, h2 -> {n2} node ({verdict}). "
                    f"Cả hai cho cùng độ dài tối ưu {len(path2) - 1} bước; heuristic "
                    f"được sinh tốt hơn (h2) giúp A* hiệu quả hơn mà vẫn tối ưu."
                ),
            })
            steps.append({
                "type": "goal",
                "state": path2[-1]["state"],
                "label": "GOAL (A* + Manhattan)",
                "path": path2,
                "log": f"✓ Lời giải tối ưu {len(path2) - 1} bước (đường đi của A* với h2).",
            })
        else:
            steps.append({
                "type": "fail",
                "log": "✗ Không giải được trong giới hạn node.",
            })
        return steps

    # ===========================
    # SIMULATED ANNEALING
    # ===========================

    def build_steps_simulated_annealing(self, start, goal):
        """
        Simulated Annealing trên 8-puzzle:
          - "Năng lượng" = h (Manhattan). Mỗi vòng chọn NGẪU NHIÊN một láng giềng.
          - Tốt hơn (Δ<=0): luôn nhận. Xấu hơn: nhận với xác suất exp(-Δ/T).
          - Nhiệt độ T giảm dần (làm nguội) -> dần hết chấp nhận nước xấu.
          - SA KHÔNG đảm bảo tìm ra lời giải (có thể nguội mà chưa tới đích).
        Ghi chú: chỉ hiển thị chi tiết DETAIL vòng đầu cho gọn; sau đó chạy nền.
        """
        import math, random
        steps = []
        T0, COOLING, T_MIN, MAX_ITERS, DETAIL = 1.0, 0.999, 0.0005, 10000, 50

        h_cur = self.heuristic_puzzle(start, goal)
        steps.append({
            "type": "expand", "state": start, "label": "S0",
            "log": f"Khởi tạo Simulated Annealing. h(start)={h_cur}. T0={T0}, làm nguội x{COOLING}.",
        })
        if h_cur == 0:
            steps.append({
                "type": "goal", "state": start, "label": "GOAL!",
                "path": [{"state": start, "move": "START"}], "log": "START đã là GOAL.",
            })
            return steps

        current = Node(start, None, 0, "START")
        T = T0
        itr = 0
        noted = False
        while itr < MAX_ITERS and T > T_MIN:
            itr += 1
            child = random.choice(self.get_children(current.state))
            changed = [i for i, v in enumerate(child["state"]) if v != current.state[i]]
            h_child = self.heuristic_puzzle(child["state"], goal)
            delta = h_child - h_cur

            if delta <= 0:
                accept, why = True, f"Δ={delta}<=0 -> nhận"
            else:
                p = math.exp(-delta / T)
                r = random.random()
                accept = r < p
                why = f"Δ={delta}>0, T={T:.2f}, P={p:.2f}, rnd={r:.2f} -> {'nhận' if accept else 'từ chối'}"

            show = itr <= DETAIL
            if accept:
                current = Node(child["state"], current, current.depth + 1, child["move"])
                h_cur = h_child
                if show:
                    steps.append({
                        "type": "gen", "state": child["state"],
                        "label": f"{child['icon']} h={h_child}", "changed": changed,
                        "log": f"  Vòng {itr}: {child['icon']} h={h_child}. {why}. T<-{T * COOLING:.2f}.",
                    })
                if h_cur == 0:
                    steps.append({
                        "type": "goal", "state": current.state, "label": "GOAL!",
                        "path": self.get_path(current),
                        "log": f"✓ Đạt đích sau {itr} vòng (h=0). Đường đi: {current.depth} bước.",
                    })
                    return steps
            else:
                if show:
                    steps.append({
                        "type": "dup", "state": child["state"], "label": "từ chối",
                        "log": f"  Vòng {itr}: {child['icon']} h={h_child}. {why}. Giữ nguyên. T<-{T * COOLING:.2f}.",
                    })
            if not show and not noted:
                noted = True
                steps.append({
                    "type": "dup",
                    "log": f"  ... (tiếp tục chạy nền sau {DETAIL} vòng đầu, không hiển thị từng vòng) ...",
                })
            T *= COOLING

        steps.append({
            "type": "fail",
            "log": f"✗ SA dừng sau {itr} vòng (đã nguội), chưa tới đích. h hiện tại={h_cur}. (SA không đảm bảo có lời giải.)",
        })
        return steps



    def select_algo(self, name):
        if self.is_auto_running:
            return

        self.selected_algo = name
        self.all_steps = []
        self.step_index = 0

        for algo, btn in self.algo_buttons.items():
            if algo == name:
                btn.config(bg="#12303a", fg=self.accent)
            else:
                btn.config(bg=self.tile_bg)

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
            "heuristic_gen": "Heuristic Functions Generation",
            "simulated_annealing": "Simulated Annealing",
        }
        self.vis_title.config(text=names[name].upper())
        self.btn_auto.config(state="normal")
        self.btn_step.config(state="normal")
        self.log("Đã chọn: " + names[name])

    def prepare(self):
        if self.is_auto_running:
            return False

        if not self.selected_algo:
            messagebox.showwarning("Thiếu thuật toán", "Bạn hãy chọn BFS, DFS hoặc IDS trước.")
            return False

        start = self.read_grid(self.start_vars)
        goal = self.read_grid(self.goal_vars)

        if not self.validate_grid(start, "START"):
            return False
        if not self.validate_grid(goal, "GOAL"):
            return False

        if self.state_key(start) == self.state_key(goal):
            messagebox.showinfo("Thông báo", "START và GOAL giống nhau.")
            return False

        if not self.all_steps:
            self.clear_log()
            self.canvas.delete("all")
            self.rendered_cards = []
            self.solution_label.config(text="Chưa có kết quả")
            self.node_label_counter = 0

            self.all_steps = self.build_steps(self.selected_algo, start, goal)
            self.step_index = 0

            self.log(f"Bắt đầu {self.selected_algo.upper()} - Start: {start}")
            self.log(f"Goal: {goal}")
            self.render_state_card(start, "START", "current", [])
            self.step_index = 1

        return True

    def apply_step(self, step):
        if not step:
            return False

        self.log(step["log"])

        step_type = step["type"]

        if step_type == "iter":
            # Xóa canvas, reset card list, vẽ lại S0 cho lần lặp IDS mới
            self.canvas.delete("all")
            self.rendered_cards = []
            self.node_label_counter = 0
            self.render_state_card(step["state"], "S0", "current", [])
        elif step_type == "expand":
            self.render_state_card(step["state"], step["label"], "current", [])
        elif step_type == "gen":
            self.render_state_card(step["state"], step["label"], "normal", step.get("changed", []))
        elif step_type == "dup":
            pass
        elif step_type == "goal":
            self.render_state_card(step["state"], step["label"], "goal", step.get("changed", []))
            self.render_solution(step.get("path", []))
            self.log(f"Tổng: {len(step.get('path', [])) - 1} di chuyển.")
            self.finish_run()
            self.set_status("✓ Hoàn tất", "done")
            return False
        elif step_type == "fail":
            self.render_solution([])
            self.finish_run()
            self.set_status("✗ Không tìm thấy", "fail")
            return False

        return True

    def run_auto(self):
        if not self.prepare():
            return

        self.is_auto_running = True
        self.set_status("⚙ Đang chạy...", "running")
        self.btn_auto.config(state="disabled")
        self.btn_step.config(state="disabled")

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

        self.set_status("⚙ Đang chạy từng bước", "running")

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

    def reset_all(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.selected_algo = None
        self.is_auto_running = False
        self.all_steps = []
        self.step_index = 0
        self.rendered_cards = []
        self.node_label_counter = 0

        self.algo_var.set("")
        self.algo_menu.set("")

        for btn in self.algo_buttons.values():
            btn.config(bg=self.tile_bg)

        self.btn_auto.config(state="disabled")
        self.btn_step.config(state="disabled")

        self.clear_log()
        self.clear_vis()
        self.solution_label.config(text="Chưa có kết quả")
        self.vis_title.config(text="MÀN HÌNH MÔ PHỎNG")
        self.set_status("Sẵn sàng", "ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
