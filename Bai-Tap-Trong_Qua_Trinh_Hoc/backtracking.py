
import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# DỮ LIỆU BẢN ĐỒ TP.HCM (quận/huyện + vị trí gần đúng + giáp ranh)
# ============================================================
# key: mã ngắn hiển thị trong node
# name: tên đầy đủ (dùng cho log/giải pháp)
# pos: (x, y) toạ độ gần đúng trên bản đồ (Bắc ở trên)

DISTRICTS = {
    "Q1":     {"name": "Quận 1",      "pos": (470, 380)},
    "Q3":     {"name": "Quận 3",      "pos": (425, 360)},
    "Q4":     {"name": "Quận 4",      "pos": (460, 430)},
    "Q5":     {"name": "Quận 5",      "pos": (360, 415)},
    "Q6":     {"name": "Quận 6",      "pos": (270, 410)},
    "Q7":     {"name": "Quận 7",      "pos": (485, 480)},
    "Q8":     {"name": "Quận 8",      "pos": (320, 465)},
    "Q10":    {"name": "Quận 10",     "pos": (370, 365)},
    "Q11":    {"name": "Quận 11",     "pos": (310, 365)},
    "Q12":    {"name": "Quận 12",     "pos": (330, 160)},
    "BTh":    {"name": "Bình Thạnh",  "pos": (450, 290)},
    "PNh":    {"name": "Phú Nhuận",   "pos": (400, 320)},
    "GVap":   {"name": "Gò Vấp",      "pos": (320, 250)},
    "TBinh":  {"name": "Tân Bình",    "pos": (360, 310)},
    "TPhu":   {"name": "Tân Phú",     "pos": (265, 300)},
    "BTan":   {"name": "Bình Tân",    "pos": (180, 350)},
    "TDuc":   {"name": "TP Thủ Đức",  "pos": (560, 190)},
    "CChi":   {"name": "Củ Chi",      "pos": (110, 70)},
    "HMon":   {"name": "Hóc Môn",     "pos": (230, 120)},
    "BChanh": {"name": "Bình Chánh",  "pos": (200, 485)},
    "NBe":    {"name": "Nhà Bè",      "pos": (430, 560)},
    "CGio":   {"name": "Cần Giờ",     "pos": (600, 600)},
}

# Danh sách cạnh (giáp ranh) - chỉ ghi 1 chiều, code sẽ tự đối xứng
EDGES = [
    ("Q1", "Q3"), ("Q1", "Q4"), ("Q1", "Q5"), ("Q1", "BTh"), ("Q1", "TDuc"),
    ("Q3", "Q10"), ("Q3", "TBinh"), ("Q3", "PNh"),
    ("Q4", "Q7"), ("Q4", "Q8"),
    ("Q5", "Q6"), ("Q5", "Q8"), ("Q5", "Q10"), ("Q5", "Q11"),
    ("Q6", "Q8"), ("Q6", "Q11"), ("Q6", "BTan"), ("Q6", "TPhu"),
    ("Q7", "Q8"), ("Q7", "NBe"), ("Q7", "BChanh"), ("Q7", "TDuc"),
    ("Q8", "BChanh"), ("Q8", "BTan"),
    ("Q10", "Q11"), ("Q10", "TBinh"),
    ("Q11", "TBinh"), ("Q11", "TPhu"),
    ("Q12", "GVap"), ("Q12", "TBinh"), ("Q12", "TPhu"),
    ("Q12", "HMon"), ("Q12", "TDuc"), ("Q12", "BTan"),
    ("BTh", "PNh"), ("BTh", "GVap"), ("BTh", "TDuc"),
    ("PNh", "TBinh"), ("PNh", "GVap"),
    ("GVap", "TBinh"),
    ("TBinh", "TPhu"),
    ("TPhu", "BTan"),
    ("BTan", "BChanh"), ("BTan", "HMon"),
    ("CChi", "HMon"),
    ("HMon", "BChanh"),
    ("BChanh", "NBe"),
    ("NBe", "CGio"),
]

# Thứ tự duyệt biến cố định (dùng cho backtracking thuần)
ORDER = list(DISTRICTS.keys())


def build_adjacency():
    """Tạo danh sách kề đối xứng từ EDGES."""
    adj = {k: set() for k in DISTRICTS}
    for a, b in EDGES:
        adj[a].add(b)
        adj[b].add(a)
    return {k: sorted(v) for k, v in adj.items()}


ADJ = build_adjacency()

# Bảng màu (1..6). index 0 không dùng.
PALETTE = {1: "#e74c3c", 2: "#27ae60", 3: "#2980b9",
           4: "#f1c40f", 5: "#8e44ad", 6: "#e67e22"}
CNAME = {1: "Đỏ", 2: "Xanh lá", 3: "Xanh dương",
         4: "Vàng", 5: "Tím", 6: "Cam"}
# Màu chữ trên node tuỳ nền (vàng nền sáng -> chữ đen)
DARK_TEXT_COLORS = {4}
UNCOLORED = "#ced6e0"


def dname(key):
    return DISTRICTS[key]["name"]


def cname(c):
    return CNAME.get(c, f"Màu {c}")


# ============================================================
# BỘ GIẢI BACKTRACKING (thuần logic, không phụ thuộc giao diện)
# Mỗi bước trả về 1 dict mô tả trạng thái để giao diện vẽ lại.
# ============================================================
class ColoringSolver:
    def __init__(self, adj, order):
        self.adj = adj
        self.order = order

    def legal_values(self, d, assignment, k):
        """Các màu còn hợp lệ cho d dựa trên các láng giềng đã gán."""
        used = {assignment[n] for n in self.adj[d] if n in assignment}
        return [c for c in range(1, k + 1) if c not in used]

    def first_conflict(self, d, color, assignment):
        """Trả về láng giềng đầu tiên trùng màu, hoặc None nếu hợp lệ."""
        for n in self.adj[d]:
            if assignment.get(n) == color:
                return n
        return None

    def solve(self, k, use_mrv=False, use_degree=False,
              use_fc=False, use_lcv=False):
        """Sinh toàn bộ danh sách bước cho thuật toán đã chọn."""
        steps = []
        assignment = {}
        domains = {d: list(range(1, k + 1)) for d in self.order}

        def snap():
            return dict(assignment)

        def snap_dom():
            return {d: list(domains[d]) for d in self.order}

        # ---- Chọn biến tiếp theo ----
        def select_var():
            unassigned = [d for d in self.order if d not in assignment]
            if not use_mrv:
                return unassigned[0], "thứ tự cố định"
            # MRV: ít giá trị hợp lệ nhất
            def remaining(d):
                return len(domains[d]) if use_fc else len(self.legal_values(d, assignment, k))
            def degree(d):
                return sum(1 for n in self.adj[d] if n not in assignment)
            if use_degree:
                chosen = min(unassigned,
                             key=lambda d: (remaining(d), -degree(d), self.order.index(d)))
                why = f"MRV={remaining(chosen)} màu, bậc={degree(chosen)}"
            else:
                chosen = min(unassigned,
                             key=lambda d: (remaining(d), self.order.index(d)))
                why = f"MRV={remaining(chosen)} màu còn lại"
            return chosen, why

        # ---- Sắp xếp thứ tự thử màu ----
        def order_values(d):
            vals = list(domains[d]) if use_fc else self.legal_values(d, assignment, k)
            if use_lcv:
                def constrain(c):
                    return sum(1 for n in self.adj[d]
                               if n not in assignment and c in domains[n])
                vals = sorted(vals, key=constrain)
            return vals

        # ---- Forward checking: cắt màu khỏi domain láng giềng ----
        def forward_check(d, color):
            removed = {}
            empty_at = None
            for n in self.adj[d]:
                if n not in assignment and color in domains[n]:
                    domains[n].remove(color)
                    removed.setdefault(n, []).append(color)
                    if not domains[n]:
                        empty_at = n
            return empty_at, removed

        def restore(removed):
            for n, cols in removed.items():
                for c in cols:
                    domains[n].append(c)
                domains[n].sort()

        # ---- Đệ quy backtracking ----
        def bt():
            if len(assignment) == len(self.order):
                steps.append({
                    "type": "solution",
                    "assignment": snap(), "current": None, "current_color": None,
                    "log": f"✓ HOÀN TẤT! Đã tô màu hợp lệ toàn bộ {len(self.order)} đơn vị.",
                })
                return True

            d, why = select_var()
            steps.append({
                "type": "select",
                "assignment": snap(), "current": d, "current_color": None,
                "log": f"→ Chọn biến: {dname(d)} ({why}).",
            })

            for color in order_values(d):
                steps.append({
                    "type": "try",
                    "assignment": snap(), "current": d, "current_color": color,
                    "log": f"   Thử {dname(d)} = {cname(color)} ...",
                })

                conflict = self.first_conflict(d, color, assignment)
                if conflict is not None:
                    steps.append({
                        "type": "conflict",
                        "assignment": snap(), "current": d, "current_color": color,
                        "conflict_with": conflict,
                        "log": f"   ✗ {cname(color)} trùng {dname(conflict)} (kề bên) → loại.",
                    })
                    continue

                # Gán thử
                assignment[d] = color
                steps.append({
                    "type": "assign",
                    "assignment": snap(), "current": d, "current_color": color,
                    "log": f"   ✓ Gán {dname(d)} = {cname(color)}.",
                })

                fc_ok = True
                removed = {}
                if use_fc:
                    empty_at, removed = forward_check(d, color)
                    if empty_at is None:
                        steps.append({
                            "type": "fc",
                            "assignment": snap(), "domains": snap_dom(),
                            "current": d, "current_color": color,
                            "log": f"   FC: cắt {cname(color)} khỏi domain láng giềng.",
                        })
                    else:
                        fc_ok = False
                        steps.append({
                            "type": "fc_fail",
                            "assignment": snap(), "domains": snap_dom(),
                            "current": d, "current_color": color,
                            "conflict_with": empty_at,
                            "log": f"   ⚠ FC: domain của {dname(empty_at)} rỗng → gán này thất bại.",
                        })

                if fc_ok and bt():
                    return True

                # Quay lui
                if use_fc:
                    restore(removed)
                del assignment[d]
                steps.append({
                    "type": "backtrack",
                    "assignment": snap(), "current": d, "current_color": None,
                    "log": f"   ↩ Quay lui: bỏ màu của {dname(d)}.",
                })

            steps.append({
                "type": "deadend",
                "assignment": snap(), "current": d, "current_color": None,
                "log": f"   ⊘ {dname(d)} hết màu hợp lệ → lùi về biến trước đó.",
            })
            return False

        ok = bt()
        if not ok:
            steps.append({
                "type": "fail",
                "assignment": {}, "current": None, "current_color": None,
                "log": f"✗ KHÔNG thể tô bản đồ với {k} màu. Hãy tăng số màu.",
            })
        return steps


# ============================================================
# GIAO DIỆN (giữ form của file 8-Puzzle)
# ============================================================
SPEED = 350  # ms giữa các bước khi chạy Tự động


class ColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backtracking - Tô màu bản đồ TP.HCM (CSP)")
        self.root.geometry("1280x760")
        self.root.minsize(1120, 680)

        # Theme (lấy tông từ file mẫu)
        self.bg = "#fef3b5"
        self.panel = "#ffffff"
        self.border = "#2a2a45"
        self.accent = "#1f6feb"
        self.accent2 = "#c0392b"
        self.accent3 = "#1e7d34"
        self.accent4 = "#8e44ad"
        self.text = "#1d1d2b"
        self.muted = "#444455"
        self.tile_bg = "#22243a"
        self.tile_text = "#e8e8f0"

        self.root.configure(bg=self.bg)

        self.solver = ColoringSolver(ADJ, ORDER)

        self.selected_algo = None
        self.is_auto_running = False
        self.step_count = 0
        self.all_steps = []
        self.step_index = 0
        self.after_id = None
        self.num_colors = tk.IntVar(value=4)

        self.create_ui()
        self.reset_all()

    # ---------- UI ----------
    def create_ui(self):
        self.root.grid_columnconfigure(0, minsize=240)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, minsize=300)
        self.root.grid_rowconfigure(0, weight=1)

        self.left = tk.Frame(self.root, bg=self.panel,
                             highlightbackground=self.border, highlightthickness=1)
        self.left.grid(row=0, column=0, sticky="nsew")

        self.center = tk.Frame(self.root, bg=self.bg)
        self.center.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.center.grid_rowconfigure(1, weight=1)
        self.center.grid_columnconfigure(0, weight=1)

        self.right = tk.Frame(self.root, bg=self.panel,
                              highlightbackground=self.border, highlightthickness=1)
        self.right.grid(row=0, column=2, sticky="nsew")
        self.right.grid_rowconfigure(1, weight=1)

        self.build_left_panel()
        self.build_center_panel()
        self.build_right_panel()

    def section_title(self, parent, text):
        tk.Label(parent, text=text.upper(), bg=self.panel, fg=self.muted,
                 font=("Consolas", 9, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(14, 6))

    def make_button(self, parent, text, command, accent=None):
        fg = accent or self.tile_text
        btn = tk.Button(parent, text=text, command=command,
                        bg=self.tile_bg, fg=fg,
                        activebackground="#15172a", activeforeground=fg,
                        relief="flat", bd=0, font=("Arial", 10, "bold"),
                        cursor="hand2", padx=10, pady=9, anchor="w")
        btn.pack(fill="x", padx=12, pady=4)
        return btn

    def build_left_panel(self):
        self.section_title(self.left, "Thuật toán Backtracking")

        self.btn_plain = self.make_button(
            self.left, "1. Backtracking thuần",
            lambda: self.select_algo("plain"), self.accent)
        self.btn_fc = self.make_button(
            self.left, "2. BT + Forward Checking",
            lambda: self.select_algo("fc"), self.accent3)
        self.btn_mrv = self.make_button(
            self.left, "3. BT + MRV",
            lambda: self.select_algo("mrv"), self.accent4)
        self.btn_mrv_deg = self.make_button(
            self.left, "4. BT + MRV + Degree",
            lambda: self.select_algo("mrv_deg"), self.accent4)
        self.btn_full = self.make_button(
            self.left, "5. BT đầy đủ (MRV+Deg+FC+LCV)",
            lambda: self.select_algo("full"), self.accent2)

        self.algo_buttons = {
            "plain": self.btn_plain,
            "fc": self.btn_fc,
            "mrv": self.btn_mrv,
            "mrv_deg": self.btn_mrv_deg,
            "full": self.btn_full,
        }

        self.section_title(self.left, "Số màu (K)")
        ctrl = tk.Frame(self.left, bg=self.panel)
        ctrl.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(ctrl, text="K =", bg=self.panel, fg=self.text,
                 font=("Consolas", 11, "bold")).pack(side="left")
        sp = tk.Spinbox(ctrl, from_=2, to=6, width=4, textvariable=self.num_colors,
                        font=("Consolas", 12, "bold"), justify="center",
                        command=self.on_color_change)
        sp.pack(side="left", padx=8)
        self.num_colors.trace_add("write", lambda *a: self.on_color_change())

        self.section_title(self.left, "Điều khiển")
        self.btn_auto = self.make_button(self.left, "▶ Tự động", self.run_auto, self.accent)
        self.btn_step = self.make_button(self.left, "⏭ Từng bước", self.run_step, self.accent4)
        self.btn_reset = self.make_button(self.left, "↺ Reset", self.reset_all, self.accent2)
        self.btn_clear = self.make_button(self.left, "🗑 Xóa log", self.clear_log, self.tile_text)

        tk.Label(self.left,
                 text=("Gợi ý:\n"
                       "1. Chọn 1 thuật toán\n"
                       "2. Chọn số màu K\n"
                       "3. Bấm Tự động / Từng bước\n\n"
                       "Thử K=3 để thấy quay lui\n"
                       "nhiều (và có thể thất bại)."),
                 bg=self.panel, fg=self.muted, justify="left",
                 font=("Arial", 9)).pack(fill="x", padx=12, pady=18)

    def build_center_panel(self):
        # Hàng trên: tiêu đề + trạng thái + chú giải màu
        top = tk.Frame(self.center, bg=self.panel,
                       highlightbackground=self.border, highlightthickness=1)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        head = tk.Frame(top, bg=self.panel)
        head.pack(fill="x")
        self.vis_title = tk.Label(head, text="BẢN ĐỒ TP. HỒ CHÍ MINH",
                                  bg=self.panel, fg=self.muted,
                                  font=("Consolas", 10, "bold"), anchor="w")
        self.vis_title.pack(side="left", padx=12, pady=8)
        self.status_label = tk.Label(head, text="Sẵn sàng", bg="#e9e9f2", fg=self.muted,
                                     font=("Consolas", 9), padx=10, pady=3)
        self.status_label.pack(side="right", padx=12, pady=8)

        self.legend = tk.Frame(top, bg=self.panel)
        self.legend.pack(fill="x", padx=12, pady=(0, 8))
        self.build_legend()

        # Khung canvas bản đồ
        vis = tk.Frame(self.center, bg=self.panel,
                       highlightbackground=self.border, highlightthickness=1)
        vis.grid(row=1, column=0, sticky="nsew")
        vis.grid_rowconfigure(0, weight=1)
        vis.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(vis, bg=self.panel, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.current_step = None
        self.canvas.bind("<Configure>", lambda e: self.draw_map(self.current_step))

        # Khung giải pháp
        sol = tk.Frame(self.center, bg=self.panel,
                       highlightbackground=self.border, highlightthickness=1)
        sol.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        tk.Label(sol, text="KẾT QUẢ TÔ MÀU", bg=self.panel, fg=self.muted,
                 font=("Consolas", 9, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(8, 2))
        self.solution_label = tk.Label(sol, text="Chưa có kết quả", bg=self.panel,
                                       fg=self.muted, font=("Consolas", 10),
                                       anchor="w", justify="left", wraplength=720)
        self.solution_label.pack(fill="x", padx=12, pady=(0, 8))

    def build_legend(self):
        for w in self.legend.winfo_children():
            w.destroy()
        k = self.num_colors.get()
        tk.Label(self.legend, text="Màu:", bg=self.panel, fg=self.muted,
                 font=("Consolas", 9, "bold")).pack(side="left", padx=(0, 6))
        for c in range(1, k + 1):
            tk.Label(self.legend, text="  ", bg=PALETTE[c]).pack(side="left", padx=(6, 2))
            tk.Label(self.legend, text=cname(c), bg=self.panel, fg=self.text,
                     font=("Consolas", 9)).pack(side="left")

    def build_right_panel(self):
        head = tk.Frame(self.right, bg=self.panel)
        head.grid(row=0, column=0, sticky="ew")
        tk.Label(head, text="LOG TỪNG BƯỚC", bg=self.panel, fg=self.muted,
                 font=("Consolas", 9, "bold")).pack(side="left", padx=12, pady=10)
        self.step_label = tk.Label(head, text="0 bước", bg=self.panel, fg=self.muted,
                                   font=("Consolas", 9))
        self.step_label.pack(side="right", padx=12, pady=10)

        self.log_box = tk.Text(self.right, bg="#fbfbff", fg=self.text,
                               insertbackground=self.text, relief="flat", bd=0,
                               width=34, height=10,
                               font=("Consolas", 9), wrap="word")
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.log_box.config(state="disabled")

    # ---------- LOG / STATUS ----------
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
            "ready": (self.muted, "#e9e9f2"),
            "running": ("#ffffff", "#1f6feb"),
            "done": ("#ffffff", "#1e7d34"),
            "fail": ("#ffffff", "#c0392b"),
        }
        fg, bg = colors.get(kind, colors["ready"])
        self.status_label.config(text=text, fg=fg, bg=bg)

    # ---------- VẼ BẢN ĐỒ ----------
    def text_color_for(self, c):
        return "#000000" if c in DARK_TEXT_COLORS else "#ffffff"

    def fit_transform(self):
        """Tính hàm biến đổi toạ độ để bản đồ vừa khít canvas hiện tại."""
        xs = [p["pos"][0] for p in DISTRICTS.values()]
        ys = [p["pos"][1] for p in DISTRICTS.values()]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        dx = (maxx - minx) or 1
        dy = (maxy - miny) or 1
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50:
            w = 700
        if h < 50:
            h = 560
        margin = 45
        scale = min((w - 2 * margin) / dx, (h - 2 * margin) / dy)
        ox = (w - dx * scale) / 2
        oy = (h - dy * scale) / 2

        def tf(pos):
            return (ox + (pos[0] - minx) * scale,
                    oy + (pos[1] - miny) * scale)
        return tf

    def draw_map(self, step=None):
        self.current_step = step
        self.canvas.delete("all")
        tf = self.fit_transform()
        assignment = step["assignment"] if step else {}
        current = step["current"] if step else None
        current_color = step["current_color"] if step else None
        stype = step["type"] if step else None
        conflict_with = step.get("conflict_with") if step else None

        # Vẽ cạnh trước
        drawn = set()
        for a in ADJ:
            ax, ay = tf(DISTRICTS[a]["pos"])
            for b in ADJ[a]:
                if (b, a) in drawn:
                    continue
                drawn.add((a, b))
                bx, by = tf(DISTRICTS[b]["pos"])
                hot = (current is not None and conflict_with is not None and
                       {a, b} == {current, conflict_with})
                self.canvas.create_line(
                    ax, ay, bx, by,
                    fill=("#c0392b" if hot else "#b8c0cc"),
                    width=(3 if hot else 1))

        # Vẽ node
        R = 24
        for key in DISTRICTS:
            x, y = tf(DISTRICTS[key]["pos"])
            assigned = assignment.get(key)

            fill = UNCOLORED
            txt_color = "#2a2a45"
            outline = "#8a93a3"
            width = 1

            if assigned:
                fill = PALETTE[assigned]
                txt_color = self.text_color_for(assigned)

            # Node đang xét
            if key == current:
                if stype in ("try",):
                    fill = PALETTE[current_color]
                    txt_color = self.text_color_for(current_color)
                    outline = "#1f6feb"; width = 4
                elif stype == "assign":
                    outline = "#1e7d34"; width = 4
                elif stype in ("conflict", "fc_fail"):
                    fill = PALETTE[current_color] if current_color else UNCOLORED
                    txt_color = self.text_color_for(current_color) if current_color else "#2a2a45"
                    outline = "#c0392b"; width = 4
                elif stype in ("backtrack", "deadend"):
                    fill = UNCOLORED
                    txt_color = "#2a2a45"
                    outline = "#c0392b"; width = 3
                elif stype in ("select", "fc"):
                    outline = "#1f6feb"; width = 4

            # node trùng màu (đối tượng gây xung đột)
            if conflict_with is not None and key == conflict_with:
                outline = "#c0392b"; width = 4

            self.canvas.create_oval(x - R, y - R, x + R, y + R,
                                    fill=fill, outline=outline, width=width)
            self.canvas.create_text(x, y, text=key, fill=txt_color,
                                    font=("Consolas", 8, "bold"))

    # ---------- CHỌN THUẬT TOÁN ----------
    ALGO_NAMES = {
        "plain":   "Backtracking thuần",
        "fc":      "Backtracking + Forward Checking",
        "mrv":     "Backtracking + MRV",
        "mrv_deg": "Backtracking + MRV + Degree",
        "full":    "Backtracking đầy đủ (MRV+Degree+FC+LCV)",
    }

    def select_algo(self, name):
        if self.is_auto_running:
            return
        self.selected_algo = name
        self.all_steps = []
        self.step_index = 0
        for algo, btn in self.algo_buttons.items():
            btn.config(bg="#123" if algo == name else self.tile_bg)
        self.algo_buttons[name].config(bg="#12303a")
        self.vis_title.config(text=self.ALGO_NAMES[name].upper())
        self.btn_auto.config(state="normal")
        self.btn_step.config(state="normal")
        self.log("Đã chọn: " + self.ALGO_NAMES[name])

    def on_color_change(self):
        # Đổi K thì reset chuỗi bước, vẽ lại chú giải + bản đồ rỗng
        try:
            k = self.num_colors.get()
        except tk.TclError:
            return
        self.all_steps = []
        self.step_index = 0
        self.build_legend()
        self.draw_map(None)
        if self.selected_algo:
            self.btn_auto.config(state="normal")
            self.btn_step.config(state="normal")

    def algo_config(self, name):
        return {
            "plain":   dict(use_mrv=False, use_degree=False, use_fc=False, use_lcv=False),
            "fc":      dict(use_mrv=False, use_degree=False, use_fc=True,  use_lcv=False),
            "mrv":     dict(use_mrv=True,  use_degree=False, use_fc=False, use_lcv=False),
            "mrv_deg": dict(use_mrv=True,  use_degree=True,  use_fc=False, use_lcv=False),
            "full":    dict(use_mrv=True,  use_degree=True,  use_fc=True,  use_lcv=True),
        }[name]

    # ---------- CHẠY ----------
    def prepare(self):
        if self.is_auto_running:
            return False
        if not self.selected_algo:
            messagebox.showwarning("Thiếu thuật toán", "Bạn hãy chọn một thuật toán Backtracking trước.")
            return False
        if not self.all_steps:
            k = self.num_colors.get()
            self.clear_log()
            self.solution_label.config(text="Chưa có kết quả")
            cfg = self.algo_config(self.selected_algo)
            self.all_steps = self.solver.solve(k, **cfg)
            self.step_index = 0
            self.log(f"Bắt đầu {self.ALGO_NAMES[self.selected_algo]} với K={k} màu.")
            self.draw_map(None)
        return True

    def apply_step(self, step):
        self.log(step["log"])
        self.draw_map(step)
        stype = step["type"]
        if stype == "solution":
            self.render_solution(step["assignment"])
            self.finish_run()
            self.set_status("✓ Hoàn tất", "done")
            return False
        if stype == "fail":
            self.solution_label.config(text="✗ Không tìm được cách tô với số màu hiện tại.")
            self.finish_run()
            self.set_status("✗ Thất bại", "fail")
            return False
        return True

    def render_solution(self, assignment):
        parts = [f"{dname(k)}={cname(c)}" for k, c in assignment.items()]
        used = len(set(assignment.values()))
        self.solution_label.config(
            text=f"Số màu dùng: {used} | " + ", ".join(parts))

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
        self.set_status("⚙ Chạy từng bước", "running")
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
        for btn in self.algo_buttons.values():
            btn.config(bg=self.tile_bg)
        self.btn_auto.config(state="disabled")
        self.btn_step.config(state="disabled")
        self.clear_log()
        self.build_legend()
        self.draw_map(None)
        self.solution_label.config(text="Chưa có kết quả")
        self.vis_title.config(text="BẢN ĐỒ TP. HỒ CHÍ MINH")
        self.set_status("Sẵn sàng", "ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = ColoringApp(root)
    root.mainloop()
