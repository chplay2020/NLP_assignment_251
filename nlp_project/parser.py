import sys
from functools import lru_cache
import os

# Load grammar từ file grammar.txt
grammar = {}
START_SYMBOL = "CÂU"

# Đường dẫn tới file văn phạm sinh ra từ bước trước (đã có sẵn trong repo)
GRAMMAR_PATH = os.path.join("output", "grammar.txt")
if not os.path.exists(GRAMMAR_PATH):
    raise FileNotFoundError(f"Grammar file not found: {GRAMMAR_PATH}")

with open(GRAMMAR_PATH, "r", encoding="utf8") as f:
    for line in f:
        line = line.strip()
        # Bỏ qua dòng trống hoặc dòng chú thích bắt đầu bằng '#'
        if not line or line.startswith("#"):
            continue
        if "->" in line:
            # Mỗi luật có dạng: LEFT -> RHS1 | RHS2 | ...
            left, right = line.split("->", 1)
            left = left.strip()
            rights = [r.strip() for r in right.split("|")]
            # Lưu RHS dưới dạng danh sách token (tách theo khoảng trắng)
            grammar[left] = [r.split() for r in rights]


@lru_cache(maxsize=None)
def parse_at(symbol, pos, tokens_tuple):
    """
    Phân tích non-terminal hoặc terminal `symbol` bắt đầu từ vị trí `pos` trong dãy token.

    Tham số:
    - symbol: Tên non-terminal (VD: CÂU, NP, VP, ...) hoặc terminal ở dạng "từ_vựng" hoặc ký hiệu ε.
    - pos: Chỉ số token hiện tại (int).
    - tokens_tuple: Tuple bất biến của các token đầu vào (phục vụ cache).

    Trả về:
    - Danh sách các khả năng parse: mỗi phần tử là (end_pos, children)
      trong đó `end_pos` là chỉ số token kết thúc parse cho nhánh đó,
      `children` là danh sách node con dạng (name, subtree_list).

    Ghi chú:
    - Dùng `lru_cache` để lưu kết quả theo bộ (symbol, pos, tokens_tuple),
      giúp tránh đệ quy trùng lặp khi backtracking.
    """
    tokens = list(tokens_tuple)
    N = len(tokens)

    # Trường hợp đặc biệt: ký hiệu epsilon (không tiêu thụ token)
    if symbol == "ε":
        return [(pos, [])]

    results = []

    # Nếu `symbol` là terminal dạng "..." (ít gặp ở vế trái), kiểm tra khớp từ vựng
    if symbol.startswith('"') and symbol.endswith('"'):
        term = symbol.strip('"')
        if pos < N and tokens[pos] == term:
            return [(pos+1, [(term, [])])]
        else:
            return []

    # Nếu không phải terminal và không có luật cho `symbol` thì không mở rộng được
    rules = grammar.get(symbol, [])
    if not rules:
        return []

    for rule in rules:
        # `rule` là danh sách các thành phần: terminal ("..."), non-terminal hoặc ε
        # Mở rộng từ trái sang phải, duy trì tập các partial parse để backtracking đầy đủ.
        partials = [(pos, [])]  # (current_pos, children_so_far)

        for part in rule:
            new_partials = []

            # Thành phần epsilon: không tiêu thụ token, giữ nguyên children
            if part == "ε":
                for (curpos, curchildren) in partials:
                    new_partials.append((curpos, curchildren.copy()))
                partials = new_partials
                continue

            # Terminal: khớp đúng từ vựng tại vị trí hiện tại
            if part.startswith('"') and part.endswith('"'):
                term = part.strip('"')
                for (curpos, curchildren) in partials:
                    if curpos < N and tokens[curpos] == term:
                        cpy = curchildren.copy()
                        cpy.append((term, []))
                        new_partials.append((curpos + 1, cpy))
                partials = new_partials
                if not partials:
                    break  # rule này thất bại, chuyển sang rule khác
                continue

            # Non-terminal: gọi đệ quy và thử mọi khả năng parse trả về
            for (curpos, curchildren) in partials:
                subresults = parse_at(part, curpos, tokens_tuple)
                for (endpos, subtree) in subresults:
                    cpy = curchildren.copy()
                    cpy.append((part, subtree))
                    new_partials.append((endpos, cpy))

            partials = new_partials
            if not partials:
                break  # rule này thất bại

        # Sau khi xử lý hết các thành phần của rule, mọi partial còn lại là kết quả hợp lệ
        for (endpos, children) in partials:
            results.append((endpos, children))

    return results

def parse(tokens, symbol, pos=0):
    """
    Bao hàm tiện lợi gọi `parse_at` với cache.

    Tham số:
    - tokens: Danh sách chuỗi token (đã tách sẵn theo khoảng trắng).
    - symbol: Non-terminal gốc để phân tích (thường là `START_SYMBOL`).
    - pos: Vị trí bắt đầu trong danh sách token.

    Trả về danh sách (end_pos, children) giống `parse_at`.
    """
    tokens_tuple = tuple(tokens)
    return parse_at(symbol, pos, tokens_tuple)

def format_arrow(node):
    """
    Định dạng cây phân tích theo kiểu mũi tên.

    Tham số:
    - node: Bộ (name, children), trong đó children là danh sách node con.

    Ví dụ định dạng:
    (HỦY) → tôi muốn hủy (MÓN → (THỊT → gà rán)) trong đơn hàng
    """
    name, children = node

    # nút cuối (tên là một chuỗi cuối và không có children)
    if not children:
        return name

    # định dạng con
    formatted_children = [format_arrow(ch) for ch in children]

    # Nếu là non-terminal với một con duy nhất là terminal hoặc nhóm đơn, hiển thị mũi tên gọn
    if len(formatted_children) == 1:
        return f"({name} → {formatted_children[0]})"

    # Ngược lại nối các con với nhau bằng khoảng trắng
    joined = " ".join(formatted_children)
    return f"({name}) → {joined}"

def build_tree(sentence):
    """
    Xây dựng chuỗi biểu diễn cây phân tích cho một câu.

    - Tách câu thành token theo khoảng trắng.
    - Gọi `parse` từ ký hiệu bắt đầu `START_SYMBOL`.
    - Nếu có nhiều khả năng, chọn parse tiêu thụ dài nhất.
    - Trả về chuỗi định dạng bởi `format_arrow`.
    """
    tokens = sentence.strip().split()
    if not tokens:
        return "()"

    parsed = parse(tokens, START_SYMBOL, 0)

    if not parsed:
        # Tìm vị trí xa nhất có thể phân tích được
        best_progress = 0
        for sym in grammar.keys():
            res = parse(tokens, sym, 0)
            for endpos, _ in res:
                if endpos > best_progress:
                    best_progress = endpos
        
        if best_progress == 0:
            return "(Không thể phân tích câu)"
        else:
            return f"(Lỗi phân tích tại: {' '.join(tokens[best_progress:])})"

    # Chọn parse tiêu thụ nhiều token nhất (khớp dài nhất)
    parsed_sorted = sorted(parsed, key=lambda x: x[0], reverse=True)
    endpos, tree = parsed_sorted[0]

    # Nếu cây có một con duy nhất và con đó là non-terminal giống gốc, in gọn
    if len(tree) == 1:
        return format_arrow(tree[0])

    return format_arrow((START_SYMBOL, tree))


# Chạy trên sentences.txt và ghi kết quả vào parse-results.txt
IN_PATH = os.path.join("input", "sentences.txt")
OUT_PATH = os.path.join("output", "parse-results.txt")

if not os.path.exists(IN_PATH):
    raise FileNotFoundError(f"Input sentences file not found: {IN_PATH}")

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

with open(IN_PATH, "r", encoding="utf8") as f:
    sentences = f.read().splitlines()

with open(OUT_PATH, "w", encoding="utf8") as out:
    for s in sentences:
        out.write(build_tree(s) + "\n")