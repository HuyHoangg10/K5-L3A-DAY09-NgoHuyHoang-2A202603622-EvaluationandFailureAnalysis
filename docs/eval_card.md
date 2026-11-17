# Eval card — LogiX-VN refund agent

## 1. Phạm vi và phiên bản

- Eval owner: Ngô Huy Hoàng (`2A202603622`).
- Hệ thống: refund agent của Lab 8, chạy offline bằng `MockLLM`.
- Core eval set: v1, 14 item × 5 seed (70 trajectory), SHA `d4d0f81a72e0`.
- Advanced eval set: v2, 28 item × 5 seed (140 trajectory), SHA `59d3ff981b63`.
- Metric specs: `config/metric_spec.yaml` v1.0 và `config/metric_spec_v2.yaml` v2.0.
- Seeds: `11/22/33/44/55`.
- Nhãn nằm riêng trong `labels_v1.json` và `labels_v2.json`; eval item không chứa đáp án.
- Code/grader commit: được ghi bằng commit chứa file này trong lịch sử Git.

## 2. Metric và gate Core

| Metric | Ngưỡng | Blocking |
|---|---:|---|
| `approval_bypass` | = 0 | Có |
| `secret_leak` | = 0 | Có |
| `db_fact_kept` | ≥ 0.95 | Không |
| `refund_amount_correct` | ≥ 0.95 và không giảm có ý nghĩa | Có |
| `reply_ledger_match` | ≥ 0.95 và không giảm có ý nghĩa | Có |
| `pass_rate` | ≥ 0.85 và không giảm có ý nghĩa | Có |
| `pass_5` | ≥ 0.80 | Không |
| `cost_per_success` | tăng không quá 10% | Không |

“Không giảm có ý nghĩa” được kiểm tra bằng paired bootstrap 1.000 lần, CI 95%, RNG 2027. Metric bị chặn khi toàn bộ CI của Δ (PR − baseline) nằm dưới 0 hoặc không đạt floor.

## 3. Kết quả Core

| Metric | Baseline `E-swarm-20261117-d4d0` | Fixed `E-fixed-20261117-d4d0` | Regression `E-seeded_regression-20261117-d4d0` |
|---|---:|---:|---:|
| `approval_bypass` | 0 | 0 | 0 |
| `secret_leak` | 0 | 0 | 0 |
| `db_fact_kept` | 0.9857 | 1.0000 | 0.9286 |
| `refund_amount_correct` | 0.9857 | 1.0000 | 0.7857 |
| `reply_ledger_match` | 1.0000 | 1.0000 | 0.7857 |
| `pass_rate` | 0.9857 | 1.0000 | 0.7143 |
| `pass_5` | 0.9286 | 1.0000 | 0.7143 |
| `cost_per_success` | 49.5670 | 48.7157 | 81.2020 |

Fixed được merge (exit 0). Các CI chính: `refund_amount_correct` Δ +0.014, CI `[+0.000, +0.043]`; `reply_ledger_match` Δ +0.000, CI `[+0.000, +0.000]`; `pass_rate` Δ +0.014, CI `[+0.000, +0.043]`.

Seeded regression bị chặn (exit 1): `refund_amount_correct` Δ −0.200, CI `[−0.414, +0.000]`; `reply_ledger_match` Δ −0.214, CI `[−0.429, +0.000]`; `pass_rate` Δ −0.271, CI `[−0.500, −0.057]`.

## 4. Judge calibration

| Judge | n | TP/FP/FN/TN | κ | Precision | Recall | Quyết định |
|---|---:|---|---:|---:|---:|---|
| `judge_tone` | 100 | 24/4/6/66 | 0.757 | 0.857 | 0.800 | Đạt floor; chỉ dùng làm tín hiệu tone. |
| `judge_helpful` | 100 | 9/0/21/70 | 0.375 | 1.000 | 0.300 | Loại khỏi CI gate do bỏ sót 70% lỗi thật. |

Tiền, approval, ledger và authorization luôn dùng deterministic code grader. Chi tiết 10 ca bất đồng ở `docs/judge_audit.md`.

## 5. Failure evidence

- Taxonomy gồm FM-01 đến FM-09: `docs/failure_taxonomy.md`.
- Trace case và bước sai đầu tiên: `docs/trace_case.md`.
- Regression test: `tests/test_lab9_trace_regression.py`.
- Grader Core bắt 100% trace lỗi được gieo và có 0 false alarm trên shape `fixed`.

## 6. Advanced M5–M7

Baseline v2 `E-swarm-20261117-59d3`: `pass_rate=0.9786`, `pass_hat_5=0.8929`, `refund_amount_correct=0.9786`, `reply_ledger_match=1.0`, `cost_per_success=50.8077`.

- A/A test: mọi delta bằng 0.
- Mutation test: 3/3 regression bị chặn; `fixed` và `honest_refactor` được merge; 0 false alarm.
- Slice regression bị chặn theo slice `money_movement`/`adversarial` dù aggregate có thể che khuất lỗi.
- Bốn trap đều bị chặn: evaluator error thành NaN, thiếu row, cherry-pick seed và nới threshold.
- Integrity gate kiểm tra số row, đủ `item × seed`, duplicate, finite metric, evaluator failure, tag slice và threshold ratchet.

## 7. Vận hành gate

Gate owner là eval owner. Khi gate exit 1, không merge; phải đọc metric/slice bị chặn, trace liên quan, sửa code hoặc grader, sinh report bằng script rồi chạy lại. Không sửa tay JSON trong `reports/`. Waiver chỉ được dùng khi có phê duyệt của giảng viên/technical owner và lý do được ghi lại.

## 8. Giới hạn và khi tăng version

- `MockLLM` không đại diện đầy đủ cho model thật hoặc traffic người dùng.
- v1 chỉ có 14 item nên CI còn rộng; v2 vẫn là adversarial pack tổng hợp.
- Judge được replay từ CSV công khai, chưa có calibration held-out mới.
- Cost là proxy của harness, không phải hóa đơn production.
- Tăng eval-set version khi thêm/sửa item, label hoặc adversarial pack; tạo baseline mới.
- Tăng metric-spec version khi đổi metric, floor, slice hoặc logic gate; threshold cùng version chỉ được siết chặt.
