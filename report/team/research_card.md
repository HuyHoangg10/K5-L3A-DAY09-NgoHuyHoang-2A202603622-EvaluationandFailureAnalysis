# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 · Scaling |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research 2026, *Towards a Science of Scaling Agent Systems* (thư viện tham khảo slide 68–69); loại bằng chứng: benchmark có kiểm soát nhiều cấu hình agent |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Thêm agent/điều phối chỉ có lợi khi task chia song song được; với task tuần tự, overhead điều phối làm tăng chi phí mà không tăng (thậm chí giảm) độ chính xác |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận gốc đo trên LLM thật và các benchmark agent của paper; lab này dùng MockLLM cố định theo seed, 14 claim public, task claims chủ yếu tuần tự (đọc claim → đọc đơn → quote → ghi refund) |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Đổi A `workflow` → C `orchestrator` (thêm 1 investigator chỉ đọc): pass rate không tăng (giữ ~1.0) vì task tuần tự; cost/success tăng khoảng 50–100% do thêm tool call, handoff và model call soạn chữ |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool manifest v1.1, seed 11,22,33,44,55, `data/public_claims.jsonl` (14 claim), `config/pricing.yaml`, evaluator `lab8.benchmark`, SQLite mới cho mỗi trial. Biến duy nhất thay đổi: topology (workflow không investigator ↔ orchestrator + 1 investigator đọc) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: overhead điều phối (thêm bước, thêm chi phí) mà không thêm trial pass; handoff có thể làm lộ secret nếu không dùng allowlist. Đo bằng pass rate, pass^5, seed variance, cost/success, mean steps; leak kiểm bằng `tests/test_orchestrator_handoff.py` |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r1.json` (chạy trong `src/`)
- Run id / file report: `src/reports/ablation_r1.json` (140 trial); ví dụ `R-workflow-C-010-s11`, `R-orchestrator-C-010-s11`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Pass rate 1.000 → 1.000, pass^5 1.000 → 1.000, seed variance 0 → 0 (không cải thiện độ đúng). Cost/success 27.86 → 47.23 VND mô phỏng (+69.5%); tool call trung bình 2.79 → 4.64; model call trung bình 0 → 0.86; mean steps 0 → 5.36 (workflow không ghi event vào trace nên steps = 0, không phải số bước thật)
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
