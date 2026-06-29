# =============================================================================
# CỜ CARO N×N (Tic-Tac-Toe / Gomoku thu nhỏ) — Thuật toán ALPHA-BETA PRUNING
# =============================================================================
# - Cải tiến từ Minimax bằng cách cắt tỉa các nhánh không cần thiết.
# - Bàn cờ tùy chỉnh kích thước (3×3, 4×4, 5×5) và số ô liên tiếp để thắng (K).
# - Người chơi: X (đi trước) | AI: O (đi sau).
# - 3×3: duyệt TOÀN BỘ cây trò chơi (kết quả tối ưu).
# - Bàn lớn hơn: tìm kiếm CẮT ĐỘ SÂU + hàm lượng giá heuristic
#   (Heuristic Alpha-Beta, Russell & Norvig - mục 5.4).
# =============================================================================

import tkinter as tk
from tkinter import font as tkfont
import time

# =============================================================================
# BẢNG MÀU (TÔNG SÁNG)
# =============================================================================
BG          = "#f4f5f7"
CARD_BG     = "#ffffff"
GRID_BG     = "#d8dde3"
CELL_BG     = "#ffffff"
CELL_HOVER  = "#eef2ff"
BORDER      = "#e5e7eb"
SEP         = "#eef1f5"
SEG_BG      = "#eef1f5"
TEXT_MAIN   = "#1f2937"
TEXT_SUB    = "#6b7280"
ACCENT      = "#2563eb"
ACCENT_DARK = "#1d4ed8"
X_COLOR     = "#ef4444"
O_COLOR     = "#2563eb"
GOOD        = "#16a34a"
WARN        = "#d97706"
DANGER      = "#dc2626"
WIN_BG      = "#dcfce7"
WIN_FG      = "#15803d"
DRAW_BG     = "#fef3c7"
DRAW_FG     = "#92400e"

HUMAN = 'X'
AI = 'O'

CELL_METRICS = {3: (96, 40), 4: (80, 34), 5: (66, 28)}
GAP = 4

WIN_SCORE = 10000
WEIGHTS = {1: 1, 2: 4, 3: 16, 4: 64}
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

# Độ sâu mặc định ("Tự động") cho bàn lớn — cân bằng giữa độ mạnh và tốc độ.
# (3×3 luôn duyệt toàn bộ; bàn lớn giới hạn độ sâu để giữ phản hồi nhanh.)
BASE_LIMIT = {3: 9, 4: 4, 5: 3}


# =============================================================================
# HÀM TRẠNG THÁI BÀN CỜ (TỔNG QUÁT N×N)
# =============================================================================

def get_empty_cells(board):
    """Danh sách ô trống (hàng, cột)."""
    n = len(board)
    return [(r, c) for r in range(n) for c in range(n) if board[r][c] == '']


def is_full(board):
    """Bàn cờ đã đầy chưa."""
    return all(cell != '' for row in board for cell in row)


def made_k_in_row(board, r, c, k):
    """Kiểm tra nhanh: nước vừa đặt tại (r, c) có tạo K ô liên tiếp không."""
    n = len(board)
    player = board[r][c]
    if player == '':
        return False
    for dr, dc in DIRECTIONS:
        count = 1
        rr, cc = r + dr, c + dc
        while 0 <= rr < n and 0 <= cc < n and board[rr][cc] == player:
            count += 1
            rr += dr
            cc += dc
        rr, cc = r - dr, c - dc
        while 0 <= rr < n and 0 <= cc < n and board[rr][cc] == player:
            count += 1
            rr -= dr
            cc -= dc
        if count >= k:
            return True
    return False


def get_winner_line(board, k):
    """Tìm đường thắng (K ô liên tiếp) -> danh sách tọa độ, hoặc None."""
    n = len(board)
    for r in range(n):
        for c in range(n):
            p = board[r][c]
            if p == '':
                continue
            for dr, dc in DIRECTIONS:
                cells = [(r, c)]
                rr, cc = r + dr, c + dc
                while 0 <= rr < n and 0 <= cc < n and board[rr][cc] == p:
                    cells.append((rr, cc))
                    if len(cells) == k:
                        return cells
                    rr += dr
                    cc += dc
    return None


def check_winner(board, k):
    """Trả về 'X' / 'O' nếu có người thắng, ngược lại None."""
    line = get_winner_line(board, k)
    if line:
        r, c = line[0]
        return board[r][c]
    return None


def heuristic(board, k):
    """
    Hàm lượng giá cho thế cờ CHƯA kết thúc (dùng khi đã cắt độ sâu).
        > 0  => có lợi cho AI (O)
        < 0  => có lợi cho người chơi (X)
    """
    n = len(board)
    score = 0
    for r in range(n):
        for c in range(n):
            for dr, dc in DIRECTIONS:
                er = r + (k - 1) * dr
                ec = c + (k - 1) * dc
                if not (0 <= er < n and 0 <= ec < n):
                    continue
                ai_count = 0
                hu_count = 0
                for i in range(k):
                    v = board[r + i * dr][c + i * dc]
                    if v == AI:
                        ai_count += 1
                    elif v == HUMAN:
                        hu_count += 1
                if ai_count > 0 and hu_count > 0:
                    continue
                if ai_count > 0:
                    score += WEIGHTS.get(ai_count, 0)
                elif hu_count > 0:
                    score -= WEIGHTS.get(hu_count, 0)
    return score


# =============================================================================
# MINIMAX THUẦN (chạy cùng độ sâu, KHÔNG cắt tỉa — chỉ để so sánh số nút)
# =============================================================================

WIN_K = 3
DEPTH_LIMIT = 9
minimax_nodes = 0  # Bộ đếm nút cho Minimax thuần


def minimax_pure(board, depth, is_maximizing, last):
    """Minimax thuần (không cắt tỉa) - chỉ để đếm số nút so sánh."""
    global minimax_nodes
    minimax_nodes += 1

    if last is not None:
        lr, lc = last
        if made_k_in_row(board, lr, lc, WIN_K):
            return WIN_SCORE - depth if board[lr][lc] == AI else -WIN_SCORE + depth

    cells = get_empty_cells(board)
    if not cells:
        return 0
    if depth >= DEPTH_LIMIT:
        return heuristic(board, WIN_K)

    if is_maximizing:
        best = float('-inf')
        for (r, c) in cells:
            board[r][c] = AI
            best = max(best, minimax_pure(board, depth + 1, False, (r, c)))
            board[r][c] = ''
        return best
    else:
        best = float('inf')
        for (r, c) in cells:
            board[r][c] = HUMAN
            best = min(best, minimax_pure(board, depth + 1, True, (r, c)))
            board[r][c] = ''
        return best


# =============================================================================
# THUẬT TOÁN ALPHA-BETA PRUNING
# =============================================================================

ab_nodes_explored = 0
ab_pruned_branches = 0


def alpha_beta(board, depth, alpha, beta, is_maximizing, last):
    """
    Thuật toán Alpha-Beta Pruning - cải tiến từ Minimax.

    Nguyên lý:
        - Alpha: giá trị tốt nhất Maximizer (AI) đã tìm được
        - Beta: giá trị tốt nhất Minimizer (Người chơi) đã tìm được
        - Cắt tỉa khi alpha >= beta (nhánh không thể tốt hơn)

    Tham số:
        board, depth, alpha, beta, is_maximizing như mô tả ở trên
        last: (r, c) của nước vừa đặt để tới trạng thái này (None nếu chưa có)

    Trả về:
        Điểm đánh giá tốt nhất cho trạng thái hiện tại
    """
    global ab_nodes_explored, ab_pruned_branches
    ab_nodes_explored += 1

    # Trường hợp cơ sở: kết thúc / cắt độ sâu
    if last is not None:
        lr, lc = last
        if made_k_in_row(board, lr, lc, WIN_K):
            return WIN_SCORE - depth if board[lr][lc] == AI else -WIN_SCORE + depth

    cells = get_empty_cells(board)
    if not cells:
        return 0
    if depth >= DEPTH_LIMIT:
        return heuristic(board, WIN_K)

    if is_maximizing:
        # Lượt AI: tìm nước đi có điểm CAO NHẤT
        best_score = float('-inf')
        for (row, col) in cells:
            board[row][col] = AI
            current = alpha_beta(board, depth + 1, alpha, beta, False, (row, col))
            board[row][col] = ''
            best_score = max(best_score, current)
            alpha = max(alpha, best_score)
            if alpha >= beta:                 # CẮT TỈA BETA
                ab_pruned_branches += 1
                break
        return best_score
    else:
        # Lượt Người chơi: tìm nước đi có điểm THẤP NHẤT
        best_score = float('inf')
        for (row, col) in cells:
            board[row][col] = HUMAN
            current = alpha_beta(board, depth + 1, alpha, beta, True, (row, col))
            board[row][col] = ''
            best_score = min(best_score, current)
            beta = min(beta, best_score)
            if alpha >= beta:                 # CẮT TỈA ALPHA
                ab_pruned_branches += 1
                break
        return best_score


def best_move(board, k, limit):
    """
    Tìm nước đi tốt nhất cho AI bằng Alpha-Beta Pruning.
    Đồng thời chạy Minimax thuần (cùng độ sâu) để so sánh số nút.

    Trả về:
        move, best_score,
        ab_nodes, pruned, mm_nodes,
        depth_used,
        move_scores: [((r, c), điểm), ...] cho MỌI nước đi gốc
    """
    global ab_nodes_explored, ab_pruned_branches, minimax_nodes, WIN_K, DEPTH_LIMIT
    WIN_K = k
    DEPTH_LIMIT = limit
    ab_nodes_explored = 0
    ab_pruned_branches = 0
    minimax_nodes = 0

    # Chạy Alpha-Beta cho từng nước đi gốc (cửa sổ mới -> điểm chính xác từng nước)
    move_scores = []
    for (row, col) in get_empty_cells(board):
        board[row][col] = AI
        score = alpha_beta(board, 1, float('-inf'), float('inf'), False, (row, col))
        board[row][col] = ''
        move_scores.append(((row, col), score))

    # Chạy Minimax thuần cùng độ sâu để đếm số nút (so sánh hiệu suất)
    for (row, col) in get_empty_cells(board):
        board[row][col] = AI
        minimax_pure(board, 1, False, (row, col))
        board[row][col] = ''

    if not move_scores:
        return None, 0, ab_nodes_explored, ab_pruned_branches, minimax_nodes, limit, []

    best = move_scores[0]
    for ms in move_scores[1:]:
        if ms[1] > best[1]:
            best = ms

    return (best[0], best[1], ab_nodes_explored, ab_pruned_branches,
            minimax_nodes, limit, move_scores)


# =============================================================================
# GIAO DIỆN TKINTER (TÔNG SÁNG, TỐI GIẢN)
# =============================================================================

class CoCaRoAlphaBeta:
    """Giao diện Cờ Caro với AI Alpha-Beta Pruning, bàn cờ tùy chỉnh kích thước."""

    ALGO_NAME = "Alpha-Beta Pruning"

    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro — Alpha-Beta Pruning")
        self.root.configure(bg=BG)

        self.N = 3
        self.K = 3
        self.depth_setting = "Auto"

        self.board = self._new_board()
        self.cells = []
        self._grid_n = 0
        self.game_over = False

        self.title_font  = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.sub_font    = tkfont.Font(family="Segoe UI", size=11)
        self.status_font = tkfont.Font(family="Segoe UI", size=15)
        self.card_font   = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.label_font  = tkfont.Font(family="Segoe UI", size=11)
        self.value_font  = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.small_font  = tkfont.Font(family="Segoe UI", size=10)
        self.seg_font    = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.btn_font    = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.mono_font   = tkfont.Font(family="Consolas", size=10)
        self.mono_bold   = tkfont.Font(family="Consolas", size=10, weight="bold")

        self._build_ui()
        self._build_settings()
        self._build_board()
        self._reset_panel()
        self._resize()

    def _new_board(self):
        return [['' for _ in range(self.N)] for _ in range(self.N)]

    # -------------------------------------------------------------------------
    # DỰNG GIAO DIỆN
    # -------------------------------------------------------------------------

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(pady=(22, 4))
        self.title_label = tk.Label(header, text="", font=self.title_font,
                                    fg=TEXT_MAIN, bg=BG)
        self.title_label.pack()
        self.sub_label = tk.Label(header, text="", font=self.sub_font,
                                  fg=TEXT_SUB, bg=BG)
        self.sub_label.pack(pady=(2, 0))

        content = tk.Frame(self.root, bg=BG)
        content.pack(padx=22, pady=(10, 18), fill="both", expand=True)

        self.left = tk.Frame(content, bg=BG)
        self.left.grid(row=0, column=0, sticky="n", padx=(0, 16))
        self.right = tk.Frame(content, bg=BG)
        self.right.grid(row=0, column=1, sticky="n")

        self.settings_card = tk.Frame(self.left, bg=CARD_BG,
                                      highlightbackground=BORDER, highlightthickness=1)
        self.settings_card.pack(fill="x")

        self.status_label = tk.Label(self.left, text="Lượt của bạn — đánh X",
                                     font=self.status_font, fg=TEXT_MAIN, bg=BG)
        self.status_label.pack(pady=(14, 8))

        self.board_frame = tk.Frame(self.left, bg=GRID_BG,
                                    highlightbackground=BORDER, highlightthickness=1)
        self.board_frame.pack()

        self.reset_btn = tk.Button(
            self.left, text="Ván mới", font=self.btn_font,
            bg=ACCENT, fg="white",
            activebackground=ACCENT_DARK, activeforeground="white",
            relief="flat", bd=0, highlightthickness=0,
            cursor="hand2", padx=28, pady=9,
            command=self._reset_game
        )
        self.reset_btn.pack(pady=(14, 0))
        self.reset_btn.bind("<Enter>", lambda e: self.reset_btn.config(bg=ACCENT_DARK))
        self.reset_btn.bind("<Leave>", lambda e: self.reset_btn.config(bg=ACCENT))

        self._build_ai_panel()
        self._update_header()

    def _build_ai_panel(self):
        panel = tk.Frame(self.right, bg=CARD_BG,
                         highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        panel.grid_columnconfigure(0, weight=1)

        tk.Label(panel, text=f"Tính toán của AI — {self.ALGO_NAME}",
                 font=self.card_font, fg=TEXT_MAIN, bg=CARD_BG, anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(14, 8))

        # Các chỉ số (riêng cho Alpha-Beta)
        self.v_ab     = self._metric_row(panel, "Nút duyệt (Alpha-Beta)", 1)
        self.v_mm     = self._metric_row(panel, "Nút duyệt (Minimax)", 2)
        self.v_pruned = self._metric_row(panel, "Nhánh đã cắt tỉa", 3)
        self.v_savings = self._metric_row(panel, "Tiết kiệm so với Minimax", 4,
                                          fg=GOOD)
        self.v_depth  = self._metric_row(panel, "Độ sâu tìm kiếm", 5)
        self.v_score  = self._metric_row(panel, "Đánh giá thế cờ", 6)
        self.v_time   = self._metric_row(panel, "Thời gian suy nghĩ", 7)

        tk.Frame(panel, bg=SEP, height=1).grid(
            row=8, column=0, columnspan=2, sticky="ew", padx=18, pady=(10, 8))

        tk.Label(panel, text="Đánh giá từng nước đi (xếp theo điểm)",
                 font=self.small_font, fg=TEXT_SUB, bg=CARD_BG, anchor="w").grid(
            row=9, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 6))

        text_wrap = tk.Frame(panel, bg=CARD_BG)
        text_wrap.grid(row=10, column=0, columnspan=2, sticky="ew", padx=18)
        self.think_text = tk.Text(text_wrap, height=8, width=26,
                                  font=self.mono_font, bg="#fbfcfe", fg=TEXT_MAIN,
                                  relief="flat", highlightbackground=BORDER,
                                  highlightthickness=1, padx=10, pady=8, wrap="none",
                                  cursor="arrow")
        scroll = tk.Scrollbar(text_wrap, command=self.think_text.yview)
        self.think_text.configure(yscrollcommand=scroll.set)
        self.think_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.think_text.tag_config("chosen", foreground=ACCENT, font=self.mono_bold)
        self.think_text.tag_config("win",  foreground=GOOD)
        self.think_text.tag_config("lose", foreground=DANGER)
        self.think_text.tag_config("pos",  foreground=TEXT_MAIN)
        self.think_text.tag_config("neg",  foreground=TEXT_SUB)
        self.think_text.tag_config("zero", foreground=TEXT_SUB)

        self.reason_label = tk.Label(panel, text="", font=self.small_font,
                                     fg=TEXT_SUB, bg=CARD_BG, anchor="w",
                                     justify="left", wraplength=300)
        self.reason_label.grid(row=11, column=0, columnspan=2, sticky="w",
                               padx=18, pady=(8, 16))

    def _metric_row(self, parent, label, r, fg=TEXT_MAIN):
        tk.Label(parent, text=label, font=self.label_font, fg=TEXT_SUB,
                 bg=CARD_BG, anchor="w").grid(row=r, column=0, sticky="w",
                                              padx=(18, 8), pady=4)
        value = tk.Label(parent, text="—", font=self.value_font, fg=fg,
                         bg=CARD_BG, anchor="e")
        value.grid(row=r, column=1, sticky="e", padx=(8, 18), pady=4)
        return value

    # -------------------------------------------------------------------------
    # KHU VỰC CÀI ĐẶT
    # -------------------------------------------------------------------------

    def _build_settings(self):
        for w in self.settings_card.winfo_children():
            w.destroy()

        tk.Label(self.settings_card, text="Cài đặt ván cờ", font=self.card_font,
                 fg=TEXT_MAIN, bg=CARD_BG, anchor="w").pack(
            fill="x", padx=16, pady=(12, 8))

        self._segment_row("Kích thước bàn",
                          [("3×3", 3), ("4×4", 4), ("5×5", 5)],
                          self.N, self._set_size)

        k_options = [(f"{i} ô", i) for i in range(3, self.N + 1)]
        self._segment_row("Điều kiện thắng", k_options, self.K, self._set_k)

        self._segment_row("Độ sâu AI",
                          [("Tự động", "Auto"), ("2", 2), ("3", 3), ("4", 4), ("5", 5)],
                          self.depth_setting, self._set_depth)

        tk.Frame(self.settings_card, bg=CARD_BG, height=6).pack()

    def _segment_row(self, label, options, current, on_select):
        row = tk.Frame(self.settings_card, bg=CARD_BG)
        row.pack(fill="x", padx=16, pady=(2, 8))
        tk.Label(row, text=label, font=self.small_font, fg=TEXT_SUB,
                 bg=CARD_BG, anchor="w").pack(anchor="w", pady=(0, 4))
        seg = tk.Frame(row, bg=CARD_BG)
        seg.pack(anchor="w")
        for (lbl, val) in options:
            active = (val == current)
            b = tk.Label(seg, text=lbl, font=self.seg_font,
                         bg=(ACCENT if active else SEG_BG),
                         fg=("white" if active else TEXT_SUB),
                         padx=12, pady=5, cursor="hand2")
            b.pack(side="left", padx=(0, 6))
            b.bind("<Button-1>", lambda e, v=val: on_select(v))
            if not active:
                b.bind("<Enter>", lambda e, w=b: w.config(bg="#e2e6ec"))
                b.bind("<Leave>", lambda e, w=b: w.config(bg=SEG_BG))

    def _set_size(self, n):
        if n == self.N:
            return
        self.N = n
        if self.K > n:
            self.K = n
        self.board = self._new_board()
        self.game_over = False
        self._build_settings()
        self._build_board()
        self._reset_panel()
        self._update_header()
        self.status_label.config(text="Lượt của bạn — đánh X", fg=TEXT_MAIN)
        self._resize()

    def _set_k(self, k):
        if k == self.K:
            return
        self.K = k
        self._build_settings()
        self._update_header()
        self._reset_game()

    def _set_depth(self, d):
        if d == self.depth_setting:
            return
        self.depth_setting = d
        self._build_settings()

    def _update_header(self):
        self.title_label.config(text=f"Cờ Caro {self.N}×{self.N}")
        self.sub_label.config(
            text=f"Thuật toán {self.ALGO_NAME} · cần {self.K} ô liên tiếp để thắng")

    # -------------------------------------------------------------------------
    # BÀN CỜ
    # -------------------------------------------------------------------------

    def _build_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        cell_px, font_px = CELL_METRICS[self.N]
        cell_font = tkfont.Font(family="Segoe UI", size=font_px, weight="bold")
        self.cells = [[None] * self.N for _ in range(self.N)]

        for r in range(self.N):
            for c in range(self.N):
                holder = tk.Frame(self.board_frame, width=cell_px, height=cell_px,
                                  bg=CELL_BG)
                holder.grid(row=r, column=c, padx=GAP, pady=GAP)
                holder.grid_propagate(False)
                lbl = tk.Label(holder, text="", font=cell_font,
                               bg=CELL_BG, fg=TEXT_MAIN, cursor="hand2")
                lbl.place(x=0, y=0, relwidth=1, relheight=1)
                lbl.bind("<Button-1>", lambda e, rr=r, cc=c: self._on_click(rr, cc))
                lbl.bind("<Enter>", lambda e, rr=r, cc=c: self._hover_enter(rr, cc))
                lbl.bind("<Leave>", lambda e, rr=r, cc=c: self._hover_leave(rr, cc))
                self.cells[r][c] = lbl

        self._grid_n = self.N

    def _resize(self):
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = min(w, sw)
        h = min(h, sh - 40)
        x = max((sw - w) // 2, 0)
        y = max((sh - h) // 2, 0)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # -------------------------------------------------------------------------
    # XỬ LÝ SỰ KIỆN
    # -------------------------------------------------------------------------

    def _hover_enter(self, r, c):
        if self.board[r][c] == '' and not self.game_over:
            self.cells[r][c].config(bg=CELL_HOVER)

    def _hover_leave(self, r, c):
        if self.board[r][c] == '' and not self.game_over:
            self.cells[r][c].config(bg=CELL_BG)

    def _on_click(self, r, c):
        if self.game_over or self.board[r][c] != '':
            return
        self.board[r][c] = HUMAN
        self.cells[r][c].config(text="X", fg=X_COLOR, bg=CELL_BG, cursor="arrow")

        if self._check_game_over():
            return

        self.status_label.config(text="AI đang suy nghĩ…", fg=WARN)
        self.root.update()
        self.root.after(50, self._ai_move)

    def _ai_move(self):
        if self.game_over:
            return
        start = time.time()
        (move, score, ab_nodes, pruned, mm_nodes,
         depth_used, move_scores) = best_move(self.board, self.K, self._limit())
        elapsed = (time.time() - start) * 1000

        if move is not None:
            r, c = move
            self.board[r][c] = AI
            self.cells[r][c].config(text="O", fg=O_COLOR, bg=CELL_BG, cursor="arrow")

            if mm_nodes > 0:
                savings = (1 - ab_nodes / mm_nodes) * 100
                savings_text = f"{savings:.1f}%"
            else:
                savings_text = "—"

            self.v_ab.config(text=f"{ab_nodes:,}")
            self.v_mm.config(text=f"{mm_nodes:,}")
            self.v_pruned.config(text=f"{pruned:,}")
            self.v_savings.config(text=savings_text)
            self.v_depth.config(text=str(depth_used))
            text, color = self._format_score(score)
            self.v_score.config(text=text, fg=color)
            self.v_time.config(text=f"{elapsed:.1f} ms")

            self._render_thinking(move_scores, move, score, depth_used)

        if not self._check_game_over():
            self.status_label.config(text="Lượt của bạn — đánh X", fg=TEXT_MAIN)

    def _check_game_over(self):
        winner = check_winner(self.board, self.K)
        line = get_winner_line(self.board, self.K)

        if winner == HUMAN:
            self.game_over = True
            self.status_label.config(text="Bạn thắng!", fg=GOOD)
            if line:
                self._highlight_winner(line)
            return True
        if winner == AI:
            self.game_over = True
            self.status_label.config(text="AI thắng!", fg=DANGER)
            if line:
                self._highlight_winner(line)
            return True
        if is_full(self.board):
            self.game_over = True
            self.status_label.config(text="Hòa!", fg=DRAW_FG)
            self._highlight_draw()
            return True
        return False

    def _highlight_winner(self, line):
        for (r, c) in line:
            self.cells[r][c].config(bg=WIN_BG, fg=WIN_FG)

    def _highlight_draw(self):
        for r in range(self.N):
            for c in range(self.N):
                if self.board[r][c] == '':
                    self.cells[r][c].config(bg=DRAW_BG)

    def _reset_game(self):
        self.board = self._new_board()
        self.game_over = False
        for r in range(self.N):
            for c in range(self.N):
                self.cells[r][c].config(text="", bg=CELL_BG, fg=TEXT_MAIN,
                                        cursor="hand2")
        self.status_label.config(text="Lượt của bạn — đánh X", fg=TEXT_MAIN)
        self._reset_panel()

    # -------------------------------------------------------------------------
    # HIỂN THỊ TÍNH TOÁN CỦA AI
    # -------------------------------------------------------------------------

    def _limit(self):
        empties = len(get_empty_cells(self.board))
        if self.depth_setting != "Auto":
            return min(int(self.depth_setting), empties)
        if empties <= 7:
            return empties
        return BASE_LIMIT.get(self.N, empties)

    def _score_label(self, s):
        if s > WIN_SCORE - 1000:
            return "thắng"
        if s < -(WIN_SCORE - 1000):
            return "thua"
        return f"{s:+d}"

    def _format_score(self, s):
        if s > WIN_SCORE - 1000:
            return "AI sắp thắng", GOOD
        if s < -(WIN_SCORE - 1000):
            return "AI có nguy cơ thua", DANGER
        if s > 0:
            return f"+{s} (AI nhỉnh hơn)", TEXT_MAIN
        if s < 0:
            return f"{s} (bạn nhỉnh hơn)", TEXT_MAIN
        return "0 (cân bằng)", TEXT_MAIN

    def _reasoning(self, best_score, depth_used):
        if best_score > WIN_SCORE - 1000:
            msg = "AI tìm được nước đi dẫn tới thắng chắc chắn."
        elif best_score < -(WIN_SCORE - 1000):
            msg = "Mọi nước đi đều dẫn tới thua nếu bạn chơi tối ưu; AI chọn nước trì hoãn lâu nhất."
        elif best_score > 0:
            msg = "AI đang chiếm ưu thế."
        elif best_score < 0:
            msg = "Bạn đang chiếm ưu thế."
        else:
            msg = "Thế cờ đang cân bằng."
        if self.N == 3:
            msg += " Bàn 3×3 được duyệt toàn bộ, cắt tỉa không làm sai kết quả tối ưu."
        else:
            msg += (f" Bàn {self.N}×{self.N} dùng cắt độ sâu (lượng giá ở độ sâu "
                    f"{depth_used}).")
        return msg

    def _render_thinking(self, move_scores, chosen, best_score, depth_used):
        txt = self.think_text
        txt.config(state="normal")
        txt.delete("1.0", "end")
        for (mv, s) in sorted(move_scores, key=lambda x: -x[1]):
            mark = "  ← chọn" if mv == chosen else ""
            line = f"({mv[0]},{mv[1]})   {self._score_label(s)}{mark}\n"
            if mv == chosen:
                tag = "chosen"
            elif s > WIN_SCORE - 1000:
                tag = "win"
            elif s < -(WIN_SCORE - 1000):
                tag = "lose"
            elif s > 0:
                tag = "pos"
            elif s < 0:
                tag = "neg"
            else:
                tag = "zero"
            txt.insert("end", line, tag)
        txt.config(state="disabled")
        self.reason_label.config(text=self._reasoning(best_score, depth_used))

    def _reset_panel(self):
        for v in (self.v_ab, self.v_mm, self.v_pruned, self.v_depth,
                  self.v_score, self.v_time):
            v.config(text="—", fg=TEXT_MAIN)
        self.v_savings.config(text="—", fg=GOOD)
        self.think_text.config(state="normal")
        self.think_text.delete("1.0", "end")
        self.think_text.insert("end", "Chưa có nước đi nào.\n", "zero")
        self.think_text.config(state="disabled")
        self.reason_label.config(
            text="AI sẽ phân tích và hiển thị điểm của từng nước đi tại đây.")


# =============================================================================
# CHẠY CHƯƠNG TRÌNH
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CoCaRoAlphaBeta(root)
    root.mainloop()
