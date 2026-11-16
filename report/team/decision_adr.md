# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 4ffd95f
- Run id dẫn chứng: R-workflow-C-001-s22 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000 (src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 27.86 (src/reports/benchmark.json)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 (src/reports/benchmark.json, src/reports/hidden_selfcheck.json: 0 leak_suspect)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Viết 1 đoạn. So cùng corpus và cùng seed, không so với một lần chạy lẻ. 

Trên cùng 14 claim x 5 seed, cả 3 shape đều pass 1.0, và do đúng như nhau nên nhóm so tiếp chi phí: workflow 27.86, single 31.45, orchestrator 47.23 VND. Workflow ko gọi model, ít tự chủ nhất và vẫn đúng việc. Hidden test cũng cho kết quả giống nhau 100% - self check student_drop không có nhãn, cho cùng status và proposal trên 600 trial self check.

## Có đáng đổi lấy multi-agent không

Nếu pass nhỉnh hơn mà cost và variance cao hơn, nhóm giữ hay đổi? Điều kiện nào làm quyết định đảo lại?

Không đổi. Orchestrator đắt hơn ~70% nhưng không đúng hơn, swarm vừa đắt nhất, còn sai C-002 ở seed 55. Nhóm sẽ đổi theo điều kiện: ticket thật nhưng mơ hồ đến mức cần model hiểu ngôn ngữ và trích dữ kiện, hoặc các bước điều tra chạy song song được,rút ngắn critical path như kết quả tham khảo card R1 và pass rate cao đủ để bù chi phí.

## Trace và bằng chứng

Trace của nhóm ghi những event nào? Field nào cố ý **không** ghi, và vì sao? Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?

| Event | Payload | Vì sao an toàn |
|---|---|---|
| `claim` | `found`, `has_order_id` (True/False) | Không ghi ticket, `parent_secret`, `raw_headers` |
| `order` | `visible`, `reason` | Không ghi SĐT, địa chỉ, tên hàng, internal note |
| `quote` | `amount_vnd`, `reason`, `clause_ids` | Số do code tính, không có PII |
| `host` | `ok`, `reason` của `issue_refund` | Chỉ kết quả cổng duyệt |
| `crash` | `at` | Ghi trước khi `raise` lại `InjectedCrash` (không nuốt crash) |

Cố ý không ghi: ticket (dữ liệu người dùng, có thể chứa câu dẫn dắt); parent_secret, raw_headers (chứa thông tin khách hàng). Trace chỉ nhận data qua allowlist, nên tự chặn field mới thêm. Shape chỉ ghi trace run id nên scanner quét được toàn bộ output, test workflow trace đã kiểm 14 claim public ko bị lộ canary secret, header hay nguyên văn ticket. 


## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

Bộ public chỉ có 14 claim. Variance = 0 ở ba shape là do MockLLM cố định theo seed, không chứng minh độ ổn định với model thật. Bộ hidden `student_drop` không có nhãn nên chỉ kiểm được "chạy hết, trace sạch", không có pass rate; điểm hidden chính thức do giảng viên chấm. Cost là mô phỏng, không phải hóa đơn API.