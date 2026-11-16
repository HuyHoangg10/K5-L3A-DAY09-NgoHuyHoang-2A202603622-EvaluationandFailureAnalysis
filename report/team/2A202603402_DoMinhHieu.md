# Báo cáo cá nhân — 2A202603402_DoMinhHieu

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Đỗ Minh Hiếu
- MSSV: 2A202603402
- Email: mhieudo11102@gmail.com
- GitHub: https://github.com/minhiuss

## 2. Phần việc phụ trách

Shape, module hoặc phần báo cáo bạn phụ trách.

Workflow + Benchmark + viết team report 

## 3. Đóng góp cụ thể

Commit chính (hash), test đã thêm hoặc sửa, quyết định kỹ thuật bạn đưa ra.

| Commit | Nội dung |
| --- | --- |
| `da9b8f2` | Shape A `workflow.py`: các bước cố định, tiền do `compute_compensation`, host ghi qua `issue_refund` |
| `4ffd95f` | Thêm trace allowlist cho workflow (claim/order/quote/host/crash); chạy lại benchmark; self-check hidden |
| `1e3ff52` | `src/tests/test_workflow_trace.py` (16 test) |

**Test đã thêm:** `tests/test_workflow_trace.py`: trace có event và chỉ thuộc allowlist, không lộ secret/ticket trên 14 claim; C-002 seed 55 vẫn `denied`; crash được ghi trace rồi ném lại.

**Quyết định kỹ thuật:**
1. Workflow không gọi MockLLM: không cần model để quyết định, giảm cost (27.86 VND/success, thấp nhất).
2. Truyền quote đầy đủ vào `issue_refund`, để host tự trừ phần đã hoàn (T13, T14).
3. Không nuốt `InjectedCrash`: ghi event `crash`, `trace.write()`, rồi `raise` lại.
4. Trace chỉ ghi True/False, lý do và số tiền, không ghi ticket hay row thô.
5. Đề xuất chọn `workflow` trong ADR dựa trên benchmark cùng corpus, cùng seed.


## 4. Bằng chứng

Link commit, tên test, run id hoặc trích đoạn report liên quan.

- `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed.
- `python -m pytest -q tests/test_workflow_trace.py` → 16 passed.
- `src/reports/benchmark.json` (workflow): pass 1.000, pass^5 1.000, variance 0, cost/success 27.86 VND, steps 3.43; run id `R-workflow-C-001-s22`.
- Benchmark chạy độc lập với Hoàng: 280/280 trial giống hệt.
- `src/reports/hidden_selfcheck.json`: 600 trial, 0 error, 0 leak_suspect.

## 5. Công cụ AI đã dùng

Công cụ, dùng vào việc gì, và bạn đã tự kiểm tra kết quả thế nào (xem [RULES.md](../../RULES.md)).

Dùng Claude để clone/pull/push, gợi ý, giải thích khái niệm, var/param, cấu trúc bài lab và các dòng code có sẵn; gợi ý cách viết report và thêm trace và test, kiểm tra source, tạo test sau đó tự kiểm tra lại bằng pytest (16 passed). Kiểm tra bằng chạy `python -m pytest -q` (cổng host), ma trận student `-k workflow`, `tests/test_workflow_trace.py`, `python -m lab8.check_submission`; đối chiếu số trong báo cáo với `src/reports/*.json`. Không dùng AI để bịa số liệu; không dùng nhãn hidden của giảng viên. 

## 6. Tự đánh giá

Hoàn thành workflow đúng 62/62 test và là shape được chọn. Điểm yếu: lúc đầu chưa vững (gọi method trên nhầm object, gõ sai status) và chưa biết SQL; đã khắc phục bằng cách đọc traceback từ dưới lên và dùng các hàm tool có sẵn thay vì tự viết SQL. Lần sau sẽ viết test sớm hơn, ngay khi viết shape.
