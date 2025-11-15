import sys
from functools import lru_cache
import os

START_SYMBOL = "CÂU"


# Tải văn phạm
grammar = {}
GRAMMAR_PATH = os.path.join("output", "grammar.txt")
if not os.path.exists(GRAMMAR_PATH):
    raise FileNotFoundError(f"Không tìm thấy file văn phạm: {GRAMMAR_PATH}")

with open(GRAMMAR_PATH, "r", encoding="utf8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "->" in line:
            left, right = line.split("->", 1)
            left = left.strip()
            rights = [r.strip() for r in right.split("|")]
            grammar[left] = [r.split() for r in rights]


# Bộ phân tích cú pháp với ghi nhớ
@lru_cache(maxsize=None)
def parse_at(symbol, pos, tokens_tuple):
    tokens = list(tokens_tuple)
    N = len(tokens)

    # epsilon
    if symbol == "ε":
        return [(pos, [])]

    results = []

    # ký hiệu kết thúc
    if symbol.startswith('"') and symbol.endswith('"'):
        term = symbol.strip('"')
        if pos < N and tokens[pos] == term:
            return [(pos + 1, [(term, [])])]
        return []

    # ký hiệu không kết thúc
    rules = grammar.get(symbol, [])
    if not rules:
        return []

    for rule in rules:
        partials = [(pos, [])]

        for part in rule:
            new_partials = []

            # epsilon
            if part == "ε":
                for (p, kids) in partials:
                    new_partials.append((p, kids.copy()))
                partials = new_partials
                continue

            # ký hiệu kết thúc trong dấu ngoặc kép
            if part.startswith('"') and part.endswith('"'):
                term = part.strip('"')
                for (p, kids) in partials:
                    if p < N and tokens[p] == term:
                        cpy = kids.copy()
                        cpy.append((term, []))
                        new_partials.append((p + 1, cpy))
                partials = new_partials
                if not partials:
                    break
                continue

            # ký hiệu không kết thúc
            for (p, kids) in partials:
                subres = parse_at(part, p, tokens_tuple)
                for (endp, subtree) in subres:
                    cpy = kids.copy()
                    cpy.append((part, subtree))
                    new_partials.append((endp, cpy))

            partials = new_partials
            if not partials:
                break

        for (endp, kids) in partials:
            results.append((endp, kids))

    return results

def parse(tokens, symbol=START_SYMBOL, pos=0):
    return parse_at(symbol, pos, tuple(tokens))


# Định dạng cây ASCII
def format_ascii_tree(node, prefix=""):
    """
    node: (tên, các con)
    prefix: chuỗi để căn chỉnh
    returns: biểu diễn chuỗi của cây
    """
    name, children = node
    if not children:
        return f"{prefix}{name}"
    
    lines = [f"{prefix}{name}"]
    for i, child in enumerate(children):
        if i == len(children) - 1:
            child_prefix = prefix + "└── "
            sub_prefix = prefix + "    "
        else:
            child_prefix = prefix + "├── "
            sub_prefix = prefix + "│   "
        lines.append(format_ascii_tree(child, child_prefix))
        # Sửa lỗi thụt lề cho các cháu
        if child[1]:
            # thêm đệ quy với sub_prefix đã cập nhật
            lines[-1] = lines[-1].replace(child_prefix, child_prefix)
    return "\n".join(lines)

# Xây dựng cây
def build_tree(sentence):
    tokens = sentence.strip().split()
    if not tokens:
        return "()"

    results = parse(tokens, START_SYMBOL, 0)
    if not results:
        return "()"

    # chọn phân tích cú pháp tiêu thụ nhiều token nhất
    results = sorted(results, key=lambda x: x[0], reverse=True)
    endpos, tree = results[0]

    if endpos != len(tokens):
        return "()"

    root = (START_SYMBOL, tree)
    return format_ascii_tree(root)

# Xử lý sentences.txt -> parse-results.txt
IN_PATH = os.path.join("input", "sentences.txt")
OUT_PATH = os.path.join("output", "parse-results.txt")

if not os.path.exists(IN_PATH):
    raise FileNotFoundError(f"Không tìm thấy file câu đầu vào: {IN_PATH}")

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

with open(IN_PATH, "r", encoding="utf8") as f:
    sentences = f.read().splitlines()

with open(OUT_PATH, "w", encoding="utf8") as out:
    for s in sentences:
        out.write(build_tree(s) + "\n\n")