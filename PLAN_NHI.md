# Phân công và kế hoạch — nhánh `nhi`

## 1. Đề bài tóm tắt (phần liên quan tới chia việc)

- 5 mốc M0 → M4 (CP1 → CP5 trong `CHECKPOINTS.md`), 8 hạng mục chấm C1–C8 (`RUBRIC.md`).
- Ba must-pass cho shape nhóm chọn: không refund khi thiếu approval hợp lệ; không lộ `CANARY_SECRET_*`; crash `20/20`.
- Không sửa: `metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`, JSON trong `src/reports/`.
  Grader hidden chỉ lấy `shapes/workflow.py`, `single.py`, `orchestrator.py` và `src/bonus/` từ repo nhóm.
- C8: **mỗi người phải có commit kỹ thuật + ít nhất một test** ghi trong bảng đóng góp `TEAM.md`.

## 2. Hiện trạng (trên `main`, commit `da9b8f2`)

| Mốc | Trạng thái |
| --- | --- |
| M0 | `TEAM.md` / bảng đóng góp còn trống |
| M1 | `workflow.py` đã viết; `single.py`, `orchestrator.py` vẫn là stub `not_implemented` |
| M2 | Chưa có handoff, chưa rà ledger/crash cho từng shape |
| M3 | Chưa có `src/reports/crash.json` |
| M4 | Chưa có `src/reports/benchmark.json`, ADR trống |
| Báo cáo | `decision_adr.md`, `research_card.md`, bảng đóng góp còn trống |

## 3. Phân công (3 người)

| Người | Phần chính (song song, M1–M2) | Sau khi đủ 3 shape (M3–M4) |
| --- | --- | --- |
| Minh Hiếu | Hoàn thiện `workflow.py` (trace event, flush trace khi `InjectedCrash`), phụ trách Policy (T01–T14) | Tích hợp các nhánh, điền `TEAM.md` / bảng đóng góp, chạy `check_submission` |
| Hoàng | `single.py` (vòng ReAct ≤ 8 bước, model chỉ có tool đọc), test Single Agent | Chạy benchmark 4 shape × 5 seed, điền `decision_adr.md` |
| **Nguyễn Văn Nhi** | `orchestrator.py`, handoff, test chống lộ secret | Chạy crash suite → `reports/crash.json`, hoàn thiện `research_card.md` |

Lý do không giao riêng M3/M4 ngay: benchmark và hidden self-check cần đủ ba shape của M1.
Mỗi người làm trên nhánh riêng, chỉ sửa file của mình để tránh conflict; Minh Hiếu merge vào `main`.

## 4. Kế hoạch của Nhi (nhánh `nhi`)

Mọi lệnh chạy trong `src/`.

### Bước 0 — môi trường (M0)
- Tạo venv, `pip install -r requirements.txt`.
- `python -m lab8.smoke` → `lab8.smoke pass`; `python -m pytest -q` xanh.
- Đọc `docs/business_rules.md`, `docs/contracts.md`, `src/lab8/shapes/swarm_reference.py` (mẫu gần nhất với orchestrator).

### Bước 1 — `src/lab8/shapes/orchestrator.py` (M1, C1)
Luồng `_run(conn, claim_id, seed, crash_at)`:
1. `Budget()`, `Trace(make_run_id("orchestrator", claim_id, seed))`.
2. `get_claim_view` (không `SELECT *`). Không có claim → `failed` / `unknown_claim`.
   Thiếu `order_id` → `needs_info`, `proposal_amount=0`, không đụng ledger.
3. Dựng handoff bằng `make_handoff(request_id=f"REQ-{claim_id}", claim_id=..., task="quote_claim",
   facts={}, allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"])`.
   **Không** đưa ticket, `parent_secret`, header hay claim row vào `facts`.
4. `trace.add("handoff", safe_dump(handoff))` — chỉ ghi handoff đã sanitize, không ghi parent context.
5. `run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])`.
6. `lookup_order` không visible → `escalated` (chỉ ghi `reason` vào trace).
7. Lấy quote từ `compute_compensation` của investigator (tính trên order row, **bỏ qua delay ghi trong ticket**).
   Quote ≤ 0 → `denied`, `proposal_amount=0`, không gọi `issue_refund`.
8. Quote > 0 → `issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`.
   `except InjectedCrash: trace.add("crash"...); trace.write(); raise` (không nuốt crash).
   `ok=False` → `failed` nếu `conflict`, ngược lại `denied` (proposal = quote đầy đủ). `ok=True` → `resolved`.
9. Mọi nhánh return qua `finish()` → trace luôn được ghi đúng contract v1.
10. (Tùy chọn) MockLLM `complete(..., purpose="draft")` chỉ để soạn chữ; model không chọn số tiền.

Kiểm tra: `python -m pytest -q -m student -o addopts= -k orchestrator` → **62 passed**.

### Bước 2 — handoff, ledger, crash cho orchestrator (M2, C3 + C5)
- T11 (gọi lại cùng claim → 1 dòng ledger), T12 (crash rồi resume → 1 refund, 1 audit `refund_committed`) xanh.
- Rà trace trong `src/traces/` của C-010 (claim có canary): không có `CANARY_SECRET_`, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.
- Cổng host `python -m pytest -q` vẫn xanh.

### Bước 3 — test chống lộ secret (C5, C8)
Thêm `src/tests/test_orchestrator_handoff.py`:
- Chạy orchestrator trên claim có canary → không có `CANARY_SECRET_` trong `RunResult` và trong mọi file `<run_id>*` ở thư mục trace.
- Event `handoff` trong trace chỉ có key thuộc `ALLOWED_FIELDS`, `allowed_tools` ⊆ `READONLY_TOOLS`, không chứa ticket.
- Gọi lại cùng claim 2 lần → đúng 1 refund (idempotency trên shape C).
- Ticket chứa "ignore policy" / delay giả → quote vẫn theo order row.

### Bước 4 — crash suite (M3, C3)
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`. Không sửa tay JSON.
- Commit `src/reports/crash.json` (sinh bằng công cụ).

### Bước 5 — `report/team/research_card.md` (M4, C6)
- Đề xuất chọn **R1 · Scaling** (hoặc R3) vì ablation dễ chạy với orchestrator: chỉ thay số/loại investigator tool,
  giữ nguyên MockLLM, tool, seed `11,22,33,44,55`, corpus `data/public_claims.jsonl`, bảng giá.
- Điền đủ 7 dòng cột "Nhóm điền" và mục "Kết quả ablation" bằng lệnh + run id + số liệu thật lấy từ report.
- Chờ benchmark của Hoàng để đối chiếu số liệu; không bịa số.

### Bước 6 — bàn giao
- Mở PR `nhi` → `main`; gửi Minh Hiếu commit hash + tên test để điền bảng đóng góp.
- Copy `report/team/MSSV_HoTen.md` → `report/team/<MSSV>_NguyenVanNhi.md`, ghi phần việc, công cụ AI đã dùng và cách tự kiểm.

## 5. Checklist của Nhi

- [ ] Smoke + `pytest -q` xanh trên máy
- [ ] `orchestrator.py` qua 62 test student
- [ ] T11, T12 xanh cho orchestrator
- [ ] `src/tests/test_orchestrator_handoff.py` xanh
- [ ] `src/reports/crash.json` = `20/20`
- [ ] `research_card.md` điền đủ, có số liệu thật
- [ ] Báo cáo cá nhân `report/team/<MSSV>_NguyenVanNhi.md`
- [ ] PR vào `main`, gửi commit/test cho Minh Hiếu
