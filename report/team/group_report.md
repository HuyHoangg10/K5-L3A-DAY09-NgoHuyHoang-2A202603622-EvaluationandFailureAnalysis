# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: ClaudeUltra
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 4ffd95f

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

Bài toán yêu cầu xử lý claim hoàn phí vận chuyển trên 4 architecture, chọn arch ít tự chủ nhất mà vẫn đúng dựa trên chỉ số cùng claim, cùng seed, cùng bảng giá. Nhóm thống nhất ticket là userdata, order row và policy là source of truth, tính tiền qua compute compensation, host durability issue refund ghi mức refund. 

Chia việc: Hiếu (workflow, benchmark, báo cáo nhóm), Hoàng (single agent, benchmark và crash report), Nhi (orchestrator, handoff, test bảo mật, crash suite, research card). 

Thứ tự: đọc swarm tham chiếu → workflow làm baseline → single và orchestrator song song → crash suite → benchmark 4 shape × 5 seed → self-check hidden → ADR.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

- **Workflow (A):** đọc claim qua `get_claim_view` → thiếu `order_id` thì `needs_info` → `lookup_order` theo `principal_id`, không thấy thì `escalated` → `compute_compensation` từ order row → quote 0 thì `denied` (không gọi host) → quote > 0 thì gọi `issue_refund` với quote đầy đủ và `crash_at`. Không gọi model.
- **Single (B):** vòng ReAct `run_react` tối đa 8 bước; `decide` chỉ chọn tool đọc, không gọi được tool ghi; sau vòng lặp, host ghi refund. Không dùng số ngày trong ticket.
- **Orchestrator (C):** dựng handoff bằng `make_handoff` với `facts` rỗng và 3 tool đọc; investigator chạy qua `run_readonly_investigators`; orchestrator quote từ order view rồi gọi host.

Ranh giới code / model: lọc theo principal, policy hiện hành, tính tiền, approval, idempotency, trần theo đơn đều do code và host; model chỉ soạn câu trả lời. Handoff được sanitize bằng allowlist (`ALLOWED_FIELDS`, `FACT_KEYS`, `READONLY_TOOLS`), không bằng LLM tóm tắt. Trace chỉ ghi field đã qua allowlist (chi tiết event trong `decision_adr.md`).

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

| Shape | Pass | Pass^5 | Variance | Cost/success (VND) | Model calls TB | Steps TB |
|---|---:|---:|---:|---:|---:|---:|
| workflow | 1.000 | 1.000 | 0 | **27.86** | 0 | 3.43 |
| single | 1.000 | 1.000 | 0 | 31.45 (+13%) | 4.64 | 4.64 |
| orchestrator | 1.000 | 1.000 | 0 | 47.23 (+70%) | 0.86 | 5.36 |
| swarm | 0.986 | 0.929 | 0.0008 | 49.57 (+78%) | 3.00 | 2.80 |

Crash safety 20/20 (`src/reports/crash.json`). Self-check `student_drop` (`src/reports/hidden_selfcheck.json`): 600 trial (3 shape × 40 claim × 5 seed), 0 error, 0 leak_suspect, ba shape cùng status ở mọi trial.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

Workflow dính AttributeError do nhầm add_tool, steps ban đầu bằng 0 vì trace rỗng. Sửa bằng cách gán đúng biến và thêm trace vào code, chạy lại test và confirm pass và cost không đổi, chỉ step 3.43 

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

Chỉ có 14 claim public; variance 0 là do MockLLM cố định theo seed; bộ hidden tự kiểm không có nhãn. Kết luận "workflow đủ tốt" có thể đảo nếu dùng model thật với ticket mơ hồ, nếu dữ kiện phải trích từ văn bản tự do thay vì bảng có cấu trúc, hoặc nếu các bước điều tra chạy song song được. Hướng cải thiện: thêm claim đối kháng tự viết (ticket nói dối, nhiều con số), đo latency mô phỏng theo critical path, thử verifier bằng code cho swarm (bonus B3).

## 8. Tài liệu tham khảo

Research Card R1