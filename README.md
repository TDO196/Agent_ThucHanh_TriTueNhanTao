# Agent_ThucHanh_TriTueNhanTao

> Đồ án **Thực hành Trí tuệ nhân tạo** — bộ ứng dụng minh hoạ trực quan (Python + Tkinter) cho các **nhóm thuật toán tìm kiếm** theo Russell & Norvig, *Artificial Intelligence: A Modern Approach* (AIMA).

Mỗi bài toán là một chương trình độc lập, có **giao diện đồ hoạ**, **chạy từng bước hoặc tự động**, kèm **log diễn giải** để thấy rõ cách thuật toán hoạt động. Khởi đầu của môn học là *mô hình phản xạ đơn giản cho máy hút bụi*, sau đó mở rộng dần sang các nhóm thuật toán tìm kiếm khác.

---
Họ & Tên: Trần Hữu Thành Đô
---
## Mục lục
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Các bài tập chính](#các-bài-tập-chính)
  - [1. Cờ Caro — Tìm kiếm đối kháng](#1-cờ-caro--tìm-kiếm-đối-kháng)
  - [2. Máy hút bụi — Mù, có thông tin, cục bộ, môi trường phức tạp](#2-máy-hút-bụi)
  - [3. 8-Puzzle — Mù, có thông tin, cục bộ](#3-8-puzzle)
  - [4. Bài tập trong quá trình học](#4-bài-tập-trong-quá-trình-học)
- [Bản đồ nhóm thuật toán ↔ bài tập](#bản-đồ-nhóm-thuật-toán--bài-tập)
- [Yêu cầu & cách chạy](#yêu-cầu--cách-chạy)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Ghi chú về phạm vi áp dụng](#ghi-chú-về-phạm-vi-áp-dụng)
- [Tham khảo](#tham-khảo)

---

## Cấu trúc thư mục

```
Agent_ThucHanh_TriTueNhanTao/
├─ Co_Caro_<tim-kiem-doi-khang>/        # Tìm kiếm đối kháng (Cờ Caro / Tic-Tac-Toe)
│  ├─ minimax.py
│  ├─ alpha_beta.py
│  └─ expectimax.py
├─ Bai-Tap-Ca-Nhan_<may-hut-bui>/       # Bài cá nhân: Máy hút bụi
│  └─ giao-dien-may-hut-bui.py
├─ Bai-Tap-8-puzzle/                    # Bài 8-puzzle
│  └─ 8-puzzle.py
├─ Bai-Tap-Trong_Qua_Trinh_Hoc/         # Bài tập trên lớp & các bản nháp
│  ├─ Agent_May-Hut-Bui.ipynb
│  ├─ btvn.ipynb
│  ├─ btvn-15-5.ipynb
│  ├─ convert.py
│  ├─ convert (1).py
│  ├─ robot_hut_bui_co_noi_that.py
│  ├─ simulated-annealing.py
│  ├─ giao-dien-may-hut-bui.py
│  └─ giao-dien-thuat-toan.py
└─ README.md
```

---

## Các bài tập chính

### 1. Cờ Caro — Tìm kiếm đối kháng
📁 `Co_Caro_<tim-kiem-doi-khang>/`

Ba chương trình độc lập, cùng một trò chơi (người chơi **X** đi trước, máy **O** đi sau), khác nhau ở thuật toán ra quyết định:

| File | Thuật toán |
|------|------------|
| `minimax.py` | Minimax |
| `alpha_beta.py` | Alpha-Beta Pruning (kèm so sánh số nút với Minimax) |
| `expectimax.py` | Expectimax (đối thủ ngẫu nhiên) |

Tính năng chung:
- **Bàn cờ tùy chỉnh kích thước** 3×3 / 4×4 / 5×5 và **số ô liên tiếp để thắng (K)**.
- **Độ sâu AI**: *Tự động* hoặc cố định (2–5).
- **Khung "Tính toán của AI"**: số nút đã duyệt, độ sâu, đánh giá thế cờ, thời gian, **điểm của từng nước đi** (đánh dấu nước được chọn) và một câu nhận xét.
- Bàn **3×3 được duyệt toàn bộ cây trò chơi → tối ưu**. Bàn lớn hơn dùng **tìm kiếm cắt độ sâu + hàm lượng giá heuristic** (Heuristic Minimax / H-Minimax, AIMA §5.4) để bảo đảm phản hồi nhanh.
- `alpha_beta.py` minh hoạ rõ **số nhánh cắt tỉa** và **% tiết kiệm** so với Minimax; `expectimax.py` dùng **mô hình đối thủ 70% tối ưu / 30% ngẫu nhiên** với các **nút CHANCE**.

### 2. Máy hút bụi
📁 `Bai-Tap-Ca-Nhan_<may-hut-bui>/giao-dien-may-hut-bui.py`

Mô phỏng tác nhân máy hút bụi trên lưới (`0 = sạch`, `1 = bụi`, `2 = vật cản`; robot có vị trí riêng). Trạng thái = *(vị trí robot, tập ô còn bụi)*. Giao diện 3 cột: **bản đồ phòng**, **màn hình mô phỏng**, **log từng bước**. Đây là bài toán phủ **4 nhóm thuật toán hợp tự nhiên** với máy hút bụi:

- **Tìm kiếm mù**: BFS, DFS, IDS (đều có biến thể *Early / Late Goal Test*), UCS.
- **Tìm kiếm có thông tin**: A\*, Greedy Best-First, IDA\*, Sinh hàm heuristic.
- **Tìm kiếm cục bộ**: Hill-Climbing (đơn giản / ngẫu nhiên / dốc nhất) và *vấn đề của Hill-Climbing*, Local Beam Search, Simulated Annealing.
- **Tìm kiếm trong môi trường phức tạp**: AND-OR (môi trường thất thường), Sensorless (không quan sát), Quan sát một phần, Online Search (LRTA\*). *Máy hút bụi là ví dụ kinh điển của AIMA cho nhóm này.*

### 3. 8-Puzzle
📁 `Bai-Tap-8-puzzle/8-puzzle.py`

Trình giải 8-puzzle: nhập **START / GOAL**, **chọn thuật toán bằng menu thả xuống**, xem mô phỏng từng bước và đường đi cuối cùng. Heuristic mặc định là **khoảng cách Manhattan**. Các nhóm thuật toán **đúng chất 8-puzzle**:

- **Tìm kiếm mù**: BFS, DFS, IDS (Early / Late), UCS.
- **Tìm kiếm có thông tin**: A\*, Greedy Best-First, IDA\*, **Heuristic Functions Generation** — sinh heuristic từ bài toán *nới lỏng* và so sánh *số ô sai vị trí* với *khoảng cách Manhattan* về số nút mở rộng.
- **Tìm kiếm cục bộ**: Hill-Climbing (3 kiểu), Local Beam Search, Simulated Annealing.

> 8-puzzle là bài toán **một tác nhân, tất định, quan sát đầy đủ** nên *không* triển khai các nhóm môi trường phức tạp / CSP / đối kháng (sẽ phải gò ép không tự nhiên).

### 4. Bài tập trong quá trình học
📁 `Bai-Tap-Trong_Qua_Trinh_Hoc/`

Các bài làm trên lớp, bài tập về nhà và bản nháp trước khi hoàn thiện:

| File | Mô tả |
|------|-------|
| `Agent_May-Hut-Bui.ipynb` | Notebook: tác nhân phản xạ đơn giản cho máy hút bụi |
| `btvn.ipynb` | Bài tập về nhà: môi trường máy hút bụi có vật cản |
| `btvn-15-5.ipynb` | Bài tập về nhà (15/5): 8-puzzle với tìm kiếm theo hàng đợi |
| `convert.py`, `convert (1).py` | Tác nhân phản xạ đơn giản cho máy hút bụi (chạy console) |
| `robot_hut_bui_co_noi_that.py` | Tác nhân máy hút bụi có nội thất / vật cản (chạy console) |
| `simulated-annealing.py` | Bản 8-puzzle Simulated Annealing độc lập (giao diện riêng) |
| `giao-dien-may-hut-bui.py` | Bản giao diện máy hút bụi trước đó |
| `giao-dien-thuat-toan.py` | Bản giao diện 8-puzzle trước đó |
| `backtracking.py` | Tô màu bản đồ các phường ở TpHCM |

---

## Bản đồ nhóm thuật toán ↔ bài tập

| Nhóm thuật toán | Bài tập minh hoạ trong repo |
|-----------------|-----------------------------|
| Tìm kiếm mù — BFS, DFS, IDS, UCS | Máy hút bụi, 8-Puzzle |
| Tìm kiếm có thông tin — Best-First, A\*, IDA\*, sinh heuristic | Máy hút bụi, 8-Puzzle |
| Tìm kiếm cục bộ — Hill-Climbing, Local Beam, Simulated Annealing | Máy hút bụi, 8-Puzzle |
| Môi trường phức tạp — AND-OR, Sensorless, Quan sát một phần, Online | Máy hút bụi |
| Tìm kiếm đối kháng — Minimax, Alpha-Beta, Expectimax | Cờ Caro |
| Ràng buộc (CSP) — backtracking, min-conflicts, ràng buộc toàn cục… | *Không có app riêng trong repo* (xem [ghi chú](#ghi-chú-về-phạm-vi-áp-dụng)) |

---

## Yêu cầu & cách chạy

**Yêu cầu**
- Python **3.8+** có sẵn **Tkinter** (Windows/macOS thường đã kèm; Ubuntu/Debian cài thêm `sudo apt install python3-tk`).
- Không cần thư viện ngoài — chỉ dùng thư viện chuẩn (`tkinter`, `heapq`, `collections`, `math`, `random`).
- Mở các file `.ipynb` bằng Jupyter Notebook / JupyterLab / VS Code.

**Chạy các ứng dụng** (tên thư mục có ký tự `<` `>` nên cần đặt trong dấu nháy):

```bash
# 8-Puzzle
python "Bai-Tap-8-puzzle/8-puzzle.py"

# Máy hút bụi
python "Bai-Tap-Ca-Nhan_<may-hut-bui>/giao-dien-may-hut-bui.py"

# Cờ Caro (chạy từng file tùy thuật toán muốn xem)
python "Co_Caro_<tim-kiem-doi-khang>/minimax.py"
python "Co_Caro_<tim-kiem-doi-khang>/alpha_beta.py"
python "Co_Caro_<tim-kiem-doi-khang>/expectimax.py"

# 8-Puzzle Simulated Annealing (bản độc lập)
python "Bai-Tap-Trong_Qua_Trinh_Hoc/simulated-annealing.py"
```

**Cách dùng chung**: chọn thuật toán → nhập dữ liệu đầu vào (START/GOAL hoặc bản đồ phòng / bàn cờ) → bấm **Tự động** hoặc **Từng bước** và theo dõi mô phỏng + log.

---

## Công nghệ sử dụng
- **Ngôn ngữ**: Python 3
- **Giao diện**: Tkinter (`ttk`)
- **Cấu trúc dữ liệu tìm kiếm**: `collections.deque`, `heapq`
- **Notebook**: Jupyter

---

## Ghi chú về phạm vi áp dụng

Một nguyên tắc xuyên suốt đồ án: **chỉ áp dụng thuật toán khi nó thực sự phù hợp với bản chất bài toán**, thay vì gò ép cho đủ nhóm.

- **Máy hút bụi** và **8-puzzle** là bài toán *một tác nhân, tất định, quan sát đầy đủ* → hợp với tìm kiếm mù, có thông tin và cục bộ. Máy hút bụi thêm phần *môi trường phức tạp* (AND-OR, sensorless, quan sát một phần, online) đúng như ví dụ trong AIMA.
- **CSP** và **tìm kiếm đối kháng** *không* tự nhiên với hai bài toán trên (sẽ phải dựng đối thủ giả hoặc đổi sang bài toán khác như N-Hậu). Vì vậy chúng được tách riêng: **đối kháng** được minh hoạ bằng **Cờ Caro**; **CSP** không có ứng dụng riêng trong repo này.
- **Simulated Annealing** mang tính ngẫu nhiên: thường giải được các trạng thái dễ nhưng *có thể bị kẹt* ở các trạng thái khó — đây là đặc tính đúng của thuật toán, không phải lỗi.

---

## Tham khảo
- Stuart Russell & Peter Norvig — *Artificial Intelligence: A Modern Approach* (AIMA).

---

<sub>Đồ án học tập môn Trí tuệ nhân tạo · Repo: <a href="https://github.com/TDO196/Agent_ThucHanh_TriTueNhanTao">TDO196/Agent_ThucHanh_TriTueNhanTao</a></sub>
