# Báo cáo cá nhân — 2A202603697_NguyenVanNhi

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Nhi
- MSSV: 2A202603697
- Email: nguyenvannhi224@gmail.com
- GitHub: nguyenvannhi242 (tên tác giả commit: `hagasei`)

## 2. Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`): orchestrator + investigator chỉ đọc.
- Handoff giữa orchestrator và investigator, và ranh giới bảo mật của trace (hạng mục C5).
- Test chống lộ secret / PII cho orchestrator.
- Crash suite (M3): sinh `src/reports/crash.json`.
- Phiếu nghiên cứu `report/team/research_card.md` (R1 · Scaling) và ablation đi kèm.

## 3. Đóng góp cụ thể

**Commit chính** (nhánh `nhi`, đã merge vào `main` qua PR #2 và PR #3):

| Commit | Nội dung |
| --- | --- |
| `3a3e563` | Cài shape C `orchestrator` |
| `deb1170` | Thêm `src/tests/test_orchestrator_handoff.py` (22 test) |
| `89ab2bc` | Thêm `src/reports/crash.json` sinh bằng `lab8.crash_test` |
| `d59dea0` | Điền research card R1 và `src/reports/ablation_r1.json` |
| `91de08f` | Gỡ file kế hoạch cá nhân khỏi repo |

**Test đã thêm:** `src/tests/test_orchestrator_handoff.py`

- `test_orchestrator_leaks_no_secret_or_pii` (14 claim public): không có `CANARY_SECRET_`, `parent_secret`, header, SĐT, địa chỉ, ghi chú nội bộ hay nguyên văn ticket trong `RunResult` và mọi file `<run_id>*` cạnh trace.
- `test_handoff_in_trace_is_allowlisted_and_read_only`: handoff trong trace chỉ có field thuộc `ALLOWED_FIELDS`, `facts` thuộc `FACT_KEYS`, tool chỉ thuộc `READONLY_TOOLS`.
- `test_ticket_text_never_changes_the_quote` (C-002 seed 55, C-006, C-009): số ngày trễ hay câu "ignore policy" trong ticket không đổi được quote.
- `test_rerun_same_claim_keeps_one_refund`: gọi lại cùng claim vẫn một dòng ledger, một audit `refund_committed`.
- `test_crash_propagates_then_resume_gives_one_refund` (3 điểm crash): `InjectedCrash` được ném ra, chạy lại ra đúng một refund.

**Quyết định kỹ thuật:**

1. **`facts` của handoff để trống.** Ticket là dữ liệu người dùng, không phải nguồn sự thật; investigator tự đọc đơn bằng `lookup_order` theo `principal_id`. Như vậy không có đường nào để ticket hay `parent_secret` đi qua ranh giới.
2. **Investigator chỉ có 3 tool đọc** (`lookup_order`, `lookup_policy`, `compute_compensation`). `make_handoff` từ chối mọi tool ghi, nên investigator không thể gọi `issue_refund`.
3. **Tiền do code tính.** Quote lấy từ `compute_compensation` trên order row; MockLLM chỉ được gọi để soạn chữ trả lời, và prompt chỉ chứa số tiền đề xuất, không chứa ticket.
4. **Truyền quote đầy đủ vào `durability.issue_refund`** cùng `crash_at`. Host tự trừ phần đã hoàn của đơn (T13, T14); nếu shape tự trừ thì host trừ hai lần.
5. **Không nuốt `InjectedCrash`:** ghi event `crash` vào trace, `trace.write()`, rồi ném lại, để T12 thấy crash thật và trace vẫn tồn tại.
6. **Trace chỉ ghi field an toàn:** handoff đã sanitize, `order_id`, `status`, `delay_days`, `shipping_fee_vnd`, `carrier`, quote và kết quả host. Cố ý **không** ghi claim row, ticket, SĐT, địa chỉ, tên hàng, ghi chú nội bộ.
7. **Mọi nhánh return đi qua `finish()`** nên trace luôn được ghi đúng Trace contract v1, kể cả `needs_info`, `escalated`, `failed`.

## 4. Bằng chứng

- Ma trận student cho orchestrator: `python -m pytest -q -m student -o addopts= -k orchestrator` → `62 passed`.
- Cổng host sau khi thêm test: `python -m pytest -q` → `78 passed`.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
- `src/reports/benchmark.json` (shape `orchestrator`): pass rate 1.000, pass^5 1.000, seed variance 0, cost/success 47.23 VND mô phỏng; run id ví dụ `R-orchestrator-C-010-s11`.
- Ablation R1 (`src/reports/ablation_r1.json`): workflow → orchestrator, pass rate 1.000 → 1.000, cost/success 27.86 → 47.23 VND (+69.5%), tool call trung bình 2.79 → 4.64.
- `python -m lab8.check_submission`: `shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`; `reports/crash.json: 20/20`; `research_card.md: đã điền đủ`.
- Pull request: PR #2 (orchestrator), PR #3 (test, crash.json, research card) trên repo nhóm `minhiuss/K5-L3A-DAY08-ClaudeUltra-FromWorkflowsToAgents`.

## 5. Công cụ AI đã dùng

- **Claude Code (Claude Opus 5.5):** đọc đề và chia việc, gợi ý code `orchestrator.py`, viết test chống lộ secret, điền research card, soạn mô tả PR và báo cáo này.
- **Cách tự kiểm tra:**
  - Chạy lại ma trận student (`62 passed` cho orchestrator) và cổng host sau mỗi thay đổi.
  - Đọc trace trong `src/traces/` của claim có canary (C-005, C-010) để chắc không có secret / PII.
  - Mọi số liệu trong research card và báo cáo đều lấy từ file do `lab8.benchmark` / `lab8.crash_test` sinh ra, không sửa tay JSON. Chạy lại benchmark và đối chiếu: số của 4 shape khớp với `reports/benchmark.json`.
  - Đối chiếu từng quyết định với `docs/contracts.md` và `docs/business_rules.md` (quote đầy đủ, không bắt `InjectedCrash`, trace contract v1).

## 6. Tự đánh giá

- **Làm được:** shape C qua đủ 62 test student và 12/12 claim public; handoff đúng allowlist, investigator không có tool ghi; có 22 test riêng cho ranh giới bảo mật, idempotency và crash; crash suite 20/20; research card có ablation chạy được và số liệu lấy từ report.
- **Hạn chế:**
  - Orchestrator tốn hơn workflow ~70% chi phí mô phỏng mà không tăng pass rate, nên không phải shape nhóm nên chọn cho task tuần tự này — đúng như ablation R1 cho thấy.
  - Kết luận chỉ đúng trên MockLLM và 14 claim public; latency là `unavailable`.
  - Dòng SOURCE trong research card còn thiếu URL paper.
  - Số bước của workflow trong ablation bằng 0 vì `workflow.py` chưa ghi event vào trace, nên so sánh "steps" giữa A và C chưa công bằng.
- **Nếu làm lại:** thêm `lookup_refund_history` cho investigator và đo xem có giảm số lần host từ chối ở T13 không; thử tách nhiều investigator để kiểm tra trực tiếp giả thuyết scaling của R1.
