# https://github.com/TDO196/Agent_ThucHanh_TriTueNhanTao/tree/main
import random

# Giá trị ô:
# 0 = sạch, 1 = bẩn, 2 = nội thất (obstacle)

CLEAN     = 0
DIRTY     = 1
FURNITURE = 2


def possible_move(x, y, grid, m, n):
    """Trả về các hướng hợp lệ (không ra ngoài biên, không đi vào nội thất)."""
    moves = []

    if x > 0          and grid[x - 1][y] != FURNITURE: moves.append("UP")
    if x < m - 1      and grid[x + 1][y] != FURNITURE: moves.append("DOWN")
    if y > 0          and grid[x][y - 1] != FURNITURE: moves.append("LEFT")
    if y < n - 1      and grid[x][y + 1] != FURNITURE: moves.append("RIGHT")

    return moves


def agent(x, y, grid, m, n):
    """
    Robot quan sát ô hiện tại:
      - Nếu bẩn → dọn sạch (ở lại).
      - Nếu sạch → chọn hướng đi ngẫu nhiên trong các hướng hợp lệ.
    Trả về (action, trạng_thái_mới_của_ô).
    """
    state_value = grid[x][y]

    if state_value == DIRTY:
        # Hành động: dọn sạch, ở tại chỗ
        return "CLEAN", CLEAN

    # Ô sạch → di chuyển
    moves = possible_move(x, y, grid, m, n)
    if not moves:
        # Robot bị kẹt (bốn phía đều là nội thất) → đứng yên
        return "STAY", state_value

    action = random.choice(moves)
    return action, state_value


def move_agent(x, y, action):
    if action == "UP":    x -= 1
    elif action == "DOWN":  x += 1
    elif action == "LEFT":  y -= 1
    elif action == "RIGHT": y += 1
    # "CLEAN" hoặc "STAY" → không di chuyển
    return x, y


def print_grid(grid, x, y):
    symbols = {CLEAN: ".", DIRTY: "*", FURNITURE: "#"}
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if i == x and j == y:
                print("A", end=" ")
            else:
                print(symbols.get(grid[i][j], "?"), end=" ")
        print()
    print("  (A=robot  .=sạch  *=bẩn  #=nội thất)\n")


# ── Khởi tạo ──────────────────────────────────────────────
m, n = 4, 4
FURNITURE_RATIO = 0.20   # ~20% ô là nội thất

grid = []
for i in range(m):
    row = []
    for j in range(n):
        r = random.random()
        if r < FURNITURE_RATIO:
            row.append(FURNITURE)
        elif r < FURNITURE_RATIO + 0.45:
            row.append(DIRTY)
        else:
            row.append(CLEAN)
    grid.append(row)

# Chọn vị trí xuất phát không phải nội thất
free_cells = [(i, j) for i in range(m) for j in range(n) if grid[i][j] != FURNITURE]
x, y = random.choice(free_cells)

steps = 30

print("=== Lưới ban đầu ===")
print_grid(grid, x, y)

# ── Vòng lặp mô phỏng ─────────────────────────────────────
for step in range(steps):
    print(f"--- Bước {step + 1} ---")

    action, new_state = agent(x, y, grid, m, n)
    grid[x][y] = new_state

    print(f"Vị trí : ({x}, {y})")
    print(f"Trạng thái ô: {'bẩn' if new_state == DIRTY else 'sạch'}")
    print(f"Hành động   : {action}")
    print_grid(grid, x, y)

    x, y = move_agent(x, y, action)

print("=== Lưới cuối cùng ===")
print_grid(grid, x, y)

dirty_left = sum(grid[i][j] == DIRTY for i in range(m) for j in range(n))
print(f"Số ô bẩn còn lại: {dirty_left}")
