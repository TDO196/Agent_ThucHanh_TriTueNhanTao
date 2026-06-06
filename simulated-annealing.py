
import math
import random
import tkinter as tk
from tkinter import messagebox

# 8-PUZZLE - SIMULATED ANNEALING

MOVES = [
    ("Len", -1, 0, "↑"),
    ("Xuong", 1, 0, "↓"),
    ("Trai", 0, -1, "←"),
    ("Phai", 0, 1, "→"),
]

SPEED = 600
MAX_SA_ITERS = 1000
T_MIN = 1e-6


class Node:
    def __init__(self, state, parent=None, depth=0, move="START"):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.move = move


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle - Simulated Annealing")
        self.root.geometry("1280x720")
        self.root.minsize(1100, 650)

        # Theme giống file gốc
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

        self.selected_algo = "sa"
        self.is_auto_running = False
        self.step_count = 0
        self.all_steps = []
        self.step_index = 0
        self.after_id = None
        self.node_label_counter = 0
        self.rendered_cards = []

        self.start_vars = []
        self.goal_vars = []
        self.t_var = tk.StringVar(value="100")
        self.alpha_var = tk.StringVar(value="0.98")

        self.create_ui()
        self.create_default_grids()
        self.reset_all()
        self.select_algo()

    # UI
    def create_ui(self):
        self.root.grid_columnconfigure(0, minsize=230)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, minsize=300)
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
        self.btn_sa = self.make_button(self.left, "Simulated Annealing", self.select_algo, self.accent)

        self.section_title(self.left, "Tham số SA")
        param_frame = tk.Frame(self.left, bg=self.panel)
        param_frame.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(param_frame, text="T ban đầu", bg=self.panel, fg=self.muted, font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(param_frame, textvariable=self.t_var, width=10, justify="center", bg=self.tile_bg, fg=self.text,
                 insertbackground=self.text, relief="flat", font=("Consolas", 11, "bold")).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4, ipady=4)

        tk.Label(param_frame, text="alpha", bg=self.panel, fg=self.muted, font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(param_frame, textvariable=self.alpha_var, width=10, justify="center", bg=self.tile_bg, fg=self.text,
                 insertbackground=self.text, relief="flat", font=("Consolas", 11, "bold")).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4, ipady=4)
        param_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.left,
            text="Gợi ý tham số:\nT = 50 đến 500\nalpha = 0.95 đến 0.999\n\nT cao: dễ nhận bước xấu hơn.\nalpha gần 1: nguội chậm, tìm kỹ hơn.",
            bg=self.panel,
            fg=self.muted,
            justify="left",
            font=("Arial", 9),
        ).pack(fill="x", padx=12, pady=(4, 14))

        self.section_title(self.left, "Điều khiển")
        self.btn_auto = self.make_button(self.left, "Tự động", self.run_auto, self.accent)
        self.btn_step = self.make_button(self.left, "Từng bước", self.run_step, self.accent4)
        self.btn_reset = self.make_button(self.left, "Reset", self.reset_all, self.accent2)
        self.btn_clear = self.make_button(self.left, "Xóa log", self.clear_log, self.text)

        tk.Label(
            self.left,
            text="Cách dùng:\n1. Nhập START/GOAL\n2. Nhập T và alpha\n3. Bấm Tự động hoặc Từng bước",
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
            text="SIMULATED ANNEALING",
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

    def move_icon(self, move_name):
        mapping = {
            "Len": "↑",
            "Xuong": "↓",
            "Trai": "←",
            "Phai": "→",
            "START": "START",
        }
        return mapping.get(move_name, "?")

    def heuristic_puzzle(self, state, goal):
        # Manhattan distance
        total = 0
        for i, v in enumerate(state):
            if v != 0:
                gi = goal.index(v)
                total += abs(i // 3 - gi // 3) + abs(i % 3 - gi % 3)
        return total

    def inversion_count(self, arr):
        values = [x for x in arr if x != 0]
        inv = 0
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                if values[i] > values[j]:
                    inv += 1
        return inv

    def is_solvable(self, start, goal):
        # Với 8-puzzle 3x3, hai trạng thái cùng parity inversion thì giải được.
        return self.inversion_count(start) % 2 == self.inversion_count(goal) % 2

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

    def read_sa_params(self):
        try:
            t0 = float(self.t_var.get().strip())
            alpha = float(self.alpha_var.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi tham số", "T và alpha phải là số. Ví dụ: T=100, alpha=0.98")
            return None

        if t0 <= 0:
            messagebox.showerror("Lỗi tham số", "T phải lớn hơn 0.")
            return None
        if not (0 < alpha < 1):
            messagebox.showerror("Lỗi tham số", "alpha phải nằm trong khoảng 0 < alpha < 1.")
            return None
        return t0, alpha

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

    # RENDER
    def clear_vis(self):
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 1000, 400))
        self.canvas.create_text(
            420,
            180,
            text="Chọn Simulated Annealing rồi bấm chạy",
            fill=self.muted,
            font=("Consolas", 12),
            anchor="center",
        )

    def render_state_card(self, state, label, card_type="normal", changed_idx=None):
        if changed_idx is None:
            changed_idx = []

        all_items = self.canvas.find_all()
        if len(all_items) == 1:
            self.canvas.delete(all_items[0])

        card_index = len(getattr(self, "rendered_cards", []))
        x = 30 + card_index * 160
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
        total_width = x + 190
        self.canvas.configure(scrollregion=(0, 0, max(total_width, self.canvas.winfo_width()), 300))
        self.canvas.xview_moveto(1)

    def render_solution(self, path, best_h=None):
        if not path:
            if best_h is None:
                self.solution_label.config(text="Không tìm thấy đường đi")
            else:
                self.solution_label.config(text=f"Không tìm thấy GOAL. Trạng thái tốt nhất có h={best_h}.")
            return

        parts = []
        for idx, item in enumerate(path):
            if idx == 0:
                parts.append("START")
            else:
                parts.append(self.move_icon(item["move"]))
        moves = " ".join(parts)
        self.solution_label.config(text=f"Số bước di chuyển: {len(path) - 1} | {moves}")

    # SIMULATED ANNEALING
    def build_steps_sa(self, start, goal, t0, alpha):
        goal_key = self.state_key(goal)
        steps = []

        current = Node(start, None, 0, "START")
        h_cur = self.heuristic_puzzle(start, goal)
        best = current
        best_h = h_cur
        T = t0

        steps.append({
            "type": "expand",
            "state": start,
            "label": f"S0 h={h_cur}",
            "log": f"Khởi tạo Simulated Annealing. T={T:.6g}, alpha={alpha}, h(start)={h_cur}.",
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

        if not self.is_solvable(start, goal):
            steps.append({
                "type": "fail",
                "best_h": best_h,
                "log": "✗ START và GOAL khác parity inversion nên 8-puzzle này không thể giải được.",
            })
            return steps

        for itr in range(1, MAX_SA_ITERS + 1):
            if T < T_MIN:
                break

            children = self.get_children(current.state)
            child = random.choice(children)
            h_new = self.heuristic_puzzle(child["state"], goal)
            delta = h_new - h_cur

            if delta <= 0:
                prob = 1.0
                accept = True
                reason = "tốt hơn hoặc bằng"
            else:
                prob = math.exp(-delta / T)
                r = random.random()
                accept = r < prob
                reason = f"xấu hơn, P=exp(-{delta}/{T:.4g})={prob:.4f}, r={r:.4f}"

            changed = [i for i, v in enumerate(child["state"]) if v != current.state[i]]
            steps.append({
                "type": "gen",
                "state": child["state"],
                "label": f"Thử h={h_new}",
                "changed": changed,
                "log": f"Lặp {itr}: thử {child['state']} ({child['icon']}). h_cur={h_cur}, h_new={h_new}, Δ={delta}, T={T:.6g} → {reason}.",
            })

            if accept:
                current = Node(child["state"], current, current.depth + 1, child["move"])
                h_cur = h_new
                steps.append({
                    "type": "expand",
                    "state": current.state,
                    "label": f"Nhận h={h_cur}",
                    "changed": changed,
                    "log": f"  ✔ Chấp nhận trạng thái mới. h={h_cur}.",
                })

                if h_cur < best_h:
                    best = current
                    best_h = h_cur
                    steps.append({
                        "type": "dup",
                        "state": current.state,
                        "label": "Best",
                        "log": f"  ★ Cập nhật best: h_best={best_h}.",
                    })

                if self.state_key(current.state) == goal_key:
                    path = self.get_path(current)
                    steps.append({
                        "type": "goal",
                        "state": current.state,
                        "label": "GOAL!",
                        "changed": changed,
                        "path": path,
                        "log": f"✓ Tìm thấy GOAL ở lặp {itr}. Số bước path={len(path) - 1}.",
                    })
                    return steps
            else:
                steps.append({
                    "type": "dup",
                    "state": child["state"],
                    "label": "Reject",
                    "log": "  ✗ Không chấp nhận trạng thái này.",
                })

            T *= alpha

        best_path = self.get_path(best)
        steps.append({
            "type": "fail",
            "best_h": best_h,
            "best_path": best_path,
            "log": f"✗ SA dừng. Chưa tới GOAL sau tối đa {MAX_SA_ITERS} lặp hoặc T < {T_MIN}. Best h={best_h}.",
        })
        return steps

    def select_algo(self):
        if self.is_auto_running:
            return
        self.selected_algo = "sa"
        self.all_steps = []
        self.step_index = 0
        self.btn_sa.config(bg="#12303a", fg=self.accent)
        self.vis_title.config(text="SIMULATED ANNEALING")
        self.btn_auto.config(state="normal")
        self.btn_step.config(state="normal")
        self.log("Đã chọn: Simulated Annealing")

    def prepare(self):
        if self.is_auto_running:
            return False

        start = self.read_grid(self.start_vars)
        goal = self.read_grid(self.goal_vars)
        params = self.read_sa_params()

        if not self.validate_grid(start, "START"):
            return False
        if not self.validate_grid(goal, "GOAL"):
            return False
        if params is None:
            return False

        t0, alpha = params

        if self.state_key(start) == self.state_key(goal):
            messagebox.showinfo("Thông báo", "START và GOAL giống nhau.")
            return False

        if not self.all_steps:
            self.clear_log()
            self.canvas.delete("all")
            self.rendered_cards = []
            self.solution_label.config(text="Chưa có kết quả")
            self.node_label_counter = 0

            self.all_steps = self.build_steps_sa(start, goal, t0, alpha)
            self.step_index = 0

            self.log(f"Bắt đầu SIMULATED ANNEALING - Start: {start}")
            self.log(f"Goal: {goal}")
            self.log(f"Tham số: T={t0}, alpha={alpha}")
            self.render_state_card(start, "START", "current", [])
            self.step_index = 1

        return True

    def apply_step(self, step):
        if not step:
            return False

        self.log(step["log"])
        step_type = step["type"]

        if step_type == "expand":
            self.render_state_card(step["state"], step["label"], "current", step.get("changed", []))
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
            if "best_path" in step:
                self.render_solution(step.get("best_path", []), step.get("best_h"))
            else:
                self.render_solution([], step.get("best_h"))
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

        self.selected_algo = "sa"
        self.is_auto_running = False
        self.all_steps = []
        self.step_index = 0
        self.rendered_cards = []
        self.node_label_counter = 0

        self.btn_auto.config(state="normal")
        self.btn_step.config(state="normal")

        self.clear_log()
        self.clear_vis()
        self.solution_label.config(text="Chưa có kết quả")
        self.vis_title.config(text="SIMULATED ANNEALING")
        self.set_status("Sẵn sàng", "ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
