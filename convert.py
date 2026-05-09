#https://github.com/TDO196/Agent_ThucHanh_TriTueNhanTao/tree/main
import random

def possible_move(x, y, m, n):
    move = []

    if x > 0:
        move.append("UP")
    if x < m - 1:
        move.append("DOWN")
    if y > 0:
        move.append("LEFT")
    if y < n - 1:
        move.append("RIGHT")

    return move


def agent(x, y, state_value, m, n):
    move = possible_move(x, y, m, n)

    if state_value == 1:
        state_value = 0

    action = random.choice(move)
    return action, state_value


def move_agent(x, y, action):
    if action == "UP":
        x -= 1
    elif action == "DOWN":
        x += 1
    elif action == "LEFT":
        y -= 1
    elif action == "RIGHT":
        y += 1

    return x, y


def print_grid(grid, x, y):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if i == x and j == y:
                print("A", end=" ")
            else:
                print(grid[i][j], end=" ")
        print()
    print()


m = 3
n = 3

# Random vị trí bẩn/sạch ban đầu
grid = []
for i in range(m):
    row = []
    for j in range(n):
        row.append(random.choice([0, 1]))
    grid.append(row)

# Random vị trí bắt đầu của agent
x = random.randint(0, m - 1)
y = random.randint(0, n - 1)

steps = 30

print("Initial grid:")
print_grid(grid, x, y)

for step in range(steps):
    print("Step", step + 1)

    state_value = grid[x][y]

    action, new_state = agent(x, y, state_value, m, n)
    grid[x][y] = new_state

    print("Position:", x, y)
    print("State:", state_value)
    print("Action:", action)
    print_grid(grid, x, y)

    x, y = move_agent(x, y, action)

print("Final grid:")
print_grid(grid, x, y)
