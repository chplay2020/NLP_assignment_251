import random

# Nạp văn phạm tiếng Việt từ file grammar.txt (dạng `A -> B C | "từ" | ε`)
grammar = {}
START_SYMBOL = "CÂU"

with open("output/grammar.txt", "r", encoding="utf8") as f:
    for line in f:
        if "->" in line:
            left, right = line.split("->")
            left = left.strip()
            rights = [r.strip() for r in right.split("|")]
            grammar.setdefault(left, []).extend(rights)

def is_terminal(symbol):
    """Kiểm tra xem ký hiệu có phải terminal dạng '...' hay không."""
    return symbol.startswith('"')

def expand(symbol):
    """
    Mở rộng một ký hiệu theo văn phạm.
    - Nếu là terminal: trả về chính từ vựng (bỏ dấu nháy).
    - Nếu là ε: trả về chuỗi rỗng.
    - Nếu là non-terminal: chọn ngẫu nhiên một vế phải và mở rộng đệ quy.
    Trả về: danh sách từ đã mở rộng theo thứ tự.
    """
    if is_terminal(symbol):
        return [symbol.strip('"')]
    if symbol == "ε":
        return [""]
    rules = grammar.get(symbol, [])
    chosen = random.choice(rules)
    result = []
    for part in chosen.split():
        result += expand(part)
    return result

def generate_sentence():
    """Sinh một câu ngẫu nhiên bắt đầu từ ký hiệu `START_SYMBOL`."""
    words = expand(START_SYMBOL)
    return " ".join([w for w in words if w != ""])  # loại bỏ phần ε rỗng

with open("output/samples.txt", "w", encoding="utf8") as g:
    # Sinh 10.000 câu mẫu
    for i in range(10000):
        g.write(generate_sentence() + "\n")

print("Đã sinh 10.000 câu mẫu vào file output/samples.txt")