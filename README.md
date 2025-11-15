# NLP Assignment 251

Dự án nhỏ về văn phạm và phân tích cú pháp tiếng Việt. Mục tiêu:
- Sinh câu ngẫu nhiên từ văn phạm đã cho.
- Phân tích cú pháp các câu đầu vào để xuất cây phân tích dạng mũi tên.

Thư mục chính:
- `parser.py`: Trình phân tích cú pháp đọc văn phạm từ `output/grammar.txt`, đọc câu từ `input/sentences.txt` và ghi kết quả cây phân tích vào `output/parse-results.txt`.
- `sample_generator.py`: Trình sinh câu ngẫu nhiên dựa trên văn phạm, ghi 10.000 câu vào `output/samples.txt`.
- `sentences.txt`: Danh sách câu đầu vào (mỗi dòng một câu, tách từ bằng khoảng trắng).
- `grammar.txt`: Văn phạm ở dạng chuẩn `LEFT -> RHS1 | RHS2 | ...` (terminal đặt trong dấu nháy đôi "...").
- `parse-results.txt`: Kết quả cây phân tích (sinh bởi `parser.py`).
- `samples.txt`: Các câu mẫu sinh ngẫu nhiên (sinh bởi `sample_generator.py`).

Yêu cầu môi trường:
- Python 3.8+ (không dùng thư viện ngoài).
- Hệ điều hành Windows (hướng dẫn dưới đây dùng PowerShell).

Hướng dẫn chạy nhanh:
1) Chạy bộ sinh câu mẫu

```powershell
python "nlp_project/sample_generator.py"
```

- Kết quả: tạo `nlp_project/output/samples.txt` chứa 10.000 câu ngẫu nhiên.

2) Chạy bộ phân tích cú pháp

```powershell
python "nlp_project/parser.py"
```

- Đầu vào: `sentences.txt` (mỗi dòng một câu; các từ phải khớp với terminal trong văn phạm, viết đúng dấu/chuẩn như trong `grammar.txt`).
- Kết quả: ghi `parse-results.txt`, mỗi dòng là cây phân tích tương ứng với câu đầu vào.

Chỉnh sửa dữ liệu đầu vào:
- Cập nhật file `sentences.txt` để thêm/bớt câu cần phân tích.
- Nếu chỉnh văn phạm, sửa `grammar.txt`. Terminal phải đặt trong dấu nháy đôi, ví dụ: `"tôi"`.

Ghi chú triển khai (tóm tắt):
- `parser.py` dùng backtracking có memoization (`lru_cache`) để parse văn phạm có ε; chọn lời giải tiêu thụ nhiều token nhất.
- `sample_generator.py` mở rộng top-down: gặp terminal thì trả về từ vựng, gặp non-terminal thì chọn ngẫu nhiên một vế phải để đệ quy.

Liên hệ mã nguồn:
- Các đoạn mã đã được chú thích trực tiếp trong file để thuận tiện theo dõi logic từng bước.