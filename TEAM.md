# Team

## Thông tin nhóm

- Tên nhóm: ClaudeUltra
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-ClaudeUltra-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/minhiuss/K5-L3A-DAY08-ClaudeUltra-FromWorkflowsToAgents.git , nhánh main, commit 4ffd95f

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đỗ Minh Hiếu | 2A202603402 |       | minhiuss | Leader |
|   2 | Ngô Huy Hoàng | 2A202603622 |nhh51204@gmail.com       | HuyHoangg10 | Thanh vien |
|   3 | Nguyễn Văn Nhi | 2A202603697 |       | nguyenvannhi242 | Thanh vien |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Hoàng | single | aa73e65, 491d597 | test_single_agent.py |
| Nhi | orchestrator, handoff, crash | 3a3e563, deb1170, 89ab2bc, d59dea0 | test_orchestrator_handoff.py |
| Hiếu | workflow, benchmark, report | da9b8f2, 4ffd95f, 1e3ff52 | test_workflow_trace.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603697_NguyenVanNhi

### Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`): orchestrator + investigator chỉ đọc.
- Handoff giữa orchestrator và investigator, và ranh giới bảo mật của trace (hạng mục C5).
- Test chống lộ secret / PII cho orchestrator.
- Crash suite (M3): sinh `src/reports/crash.json`.
- Phiếu nghiên cứu `report/team/research_card.md` (R1 · Scaling) và ablation đi kèm.

### Đóng góp cụ thể

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

### Bằng chứng

- Ma trận student cho orchestrator: `python -m pytest -q -m student -o addopts= -k orchestrator` → `62 passed`.
- Cổng host sau khi thêm test: `python -m pytest -q` → `78 passed`.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
- `src/reports/benchmark.json` (shape `orchestrator`): pass rate 1.000, pass^5 1.000, seed variance 0, cost/success 47.23 VND mô phỏng; run id ví dụ `R-orchestrator-C-010-s11`.
- Ablation R1 (`src/reports/ablation_r1.json`): workflow → orchestrator, pass rate 1.000 → 1.000, cost/success 27.86 → 47.23 VND (+69.5%), tool call trung bình 2.79 → 4.64.
- `python -m lab8.check_submission`: `shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`; `reports/crash.json: 20/20`; `research_card.md: đã điền đủ`.
- Pull request: PR #2 (orchestrator), PR #3 (test, crash.json, research card) trên repo nhóm `minhiuss/K5-L3A-DAY08-ClaudeUltra-FromWorkflowsToAgents`.

## 2A202603622_NgoHuyHoang

### Phần việc phụ trách

- Họ tên: Ngô Huy Hoàng
- MSSV: 2A202603622

### Đóng góp cụ thể

- Hoàn thiện `src/lab8/shapes/single.py`.
- Không sử dụng số ngày trễ do khách ghi trong ticket để tính tiền. Dữ liệu order trong hệ thống vẫn là nguồn chính.
- Không cho agent gọi tool ghi tiền trong vòng ReAct.
- Giới hạn vòng lặp ở 8 bước.
- Truyền `crash_at` xuống `issue_refund` để kiểm tra khả năng resume sau crash.
- Trace chỉ ghi hành động và kết quả đã được rút gọn, không ghi ticket thô, secret hoặc dữ liệu cá nhân.
- Thêm hai test cho Single Agent:
  - `test_single_uses_structured_order_instead_of_ticket_delay`
  - `test_single_trace_contains_no_raw_ticket`
- Chạy crash suite và benchmark bằng lệnh chính thức của đề.

### Bằng chứng

- Commit Single Agent: [`aa73e65`](https://github.com/minhiuss/K5-L3A-DAY08-ClaudeUltra-FromWorkflowsToAgents/commit/aa73e65410d6d9d0233a7c87eb061961716e1d78)
- Commit benchmark và crash report: [`491d597`](https://github.com/minhiuss/K5-L3A-DAY08-ClaudeUltra-FromWorkflowsToAgents/commit/491d597)
- File test: `src/tests/test_single_agent.py`
- Single Agent: 62/62 test public pass.
- Toàn bộ public matrix sau khi merge: 248 test pass.
- Crash safety: 20/20.
- Benchmark của Single Agent:
  - Pass rate: 1.000
  - Pass^5: 1.000
  - Seed variance: 0
  - Cost per success: khoảng 31.45 VND mô phỏng
  - Mean steps: khoảng 4.64
- Run id dẫn chứng: `R-single-C-001-s11`

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
