# Báo cáo cá nhân — 2A202603622_NgoHuyHoang

## 1. Thông tin thành viên

- Họ tên: Ngô Huy Hoàng
- MSSV: 2A202603622
- GitHub: HuyHoangg10

## 2. Phần việc phụ trách

Em phụ trách Shape B — Single Agent và hỗ trợ phần đánh giá kết quả.

Trong `single.py`, em dùng vòng ReAct với giới hạn tối đa 8 bước. Agent chỉ được chọn các tool đọc để lấy claim, kiểm tra order và tính mức bồi thường. Việc tính tiền vẫn do `compute_compensation` thực hiện, còn ghi refund phải đi qua `durability.issue_refund` sau khi vòng lặp kết thúc.

Em cũng chạy crash suite và benchmark để tạo hai file kết quả bắt buộc của nhóm.

## 3. Đóng góp cụ thể

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

## 4. Bằng chứng

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

## 5. Công cụ AI đã dùng

Em dùng Codex để hỗ trợ đọc README, business rules và contract, sau đó triển khai Single Agent, viết test và kiểm tra kết quả chạy.

Code được kiểm tra lại bằng test host, ma trận test public, crash suite và benchmark chính thức của đề. Hai file JSON kết quả được sinh trực tiếp từ chương trình và không chỉnh sửa thủ công.

## 6. Tự đánh giá

Sau phần này em hiểu rõ hơn ranh giới giữa model và code trong một agent. Model có thể lựa chọn bước đọc tiếp theo, nhưng không nên tự tính tiền hoặc tự ghi refund. Những thao tác có ảnh hưởng thật vẫn cần được kiểm soát bởi policy và code của host.

Kết quả public của Single Agent ổn định qua 5 seed, nhưng chi phí mô phỏng vẫn cao hơn Workflow. Vì vậy em thấy không nên chọn kiến trúc tự chủ hơn nếu Workflow đã giải quyết tốt cùng một bài toán. Kết luận này vẫn cần được đối chiếu thêm với bộ hidden và các tình huống thực tế phức tạp hơn.
