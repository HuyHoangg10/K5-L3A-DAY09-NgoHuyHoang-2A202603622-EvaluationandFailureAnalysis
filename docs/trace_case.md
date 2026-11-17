# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case đã phân tích

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`; run ID `R-seeded_regression-C-002-s11` |
| Triệu chứng | `DbFactKept` và Lab 8 grader fail. Ledger ghi refund 20.000 VND, trong khi nhãn đúng là 0; reply cũng nói đã hoàn 20.000 VND. |
| Bước sai đầu tiên | Event **3**, `model_override`, payload `{"delay_days": 5}`. |
| Vì sao là bước *đầu tiên* | Event 1 handoff đúng allowlist. Event 2 investigator đọc đúng DB: `O-202.delay_days = 2`. Sai lệch chỉ xuất hiện khi event 3 thay dữ kiện DB bằng con số 5 ngày trong ticket. |
| Failure mode | `FM-03` — `ticket_trust`: tin nội dung ticket hơn sự thật trong DB. |
| Đối chứng | `fixed C-002@11` (`R-fixed-C-002-s11`) không có `model_override`; event 3 là quote `amount_vnd=0`, ledger giữ 0 và status `denied`. |
| Regression test | `test_ticket_claim_never_overrides_database_fact` trong `tests/test_lab9_trace_regression.py`: `DbFactKept` phải fail trên `seeded_regression`, pass trên `fixed`, đồng thời hai ledger phải khác nhau. Bộ Core đã chạy **15 passed**. |
| Chưa chắc chắn | Trace chứng minh dữ kiện bị thay và hậu quả trên ledger, nhưng không chứng minh được quá trình suy luận nội bộ ngoài các event đã ghi. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
