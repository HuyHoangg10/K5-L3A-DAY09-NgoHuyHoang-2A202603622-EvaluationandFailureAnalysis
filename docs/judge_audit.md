# Judge audit

Hai judge được đánh giá như classifier nhị phân, với `FAIL` là positive class. Ngưỡng chấp nhận: κ ≥ 0.6, precision ≥ 0.8 và recall ≥ 0.7. Các số dưới đây được sinh lại offline từ CSV public bằng `python -m lab9.judge`; không dùng API key.

| Tiêu chí | n | Confusion `tp/fp/fn/tn` | κ | Precision | Recall | Đạt floors? | Quyết định |
|---|---:|---|---:|---:|---:|---|---|
| `judge_tone` | 100 | `24/4/6/66` | 0.757 | 0.857 | 0.800 | Có | Được dùng cho tín hiệu tone, kèm audit định kỳ. |
| `judge_helpful` | 100 | `9/0/21/70` | 0.375 | 1.000 | 0.300 | Không | Loại khỏi CI gate; recall quá thấp và bỏ sót 21/30 lỗi thật. |

Rogan–Gladen hiệu chỉnh failure rate quan sát của cả hai tập từ lần lượt 0.28 và 0.09 về xấp xỉ 0.30. Điều này cho thấy tỷ lệ quan sát thô của một judge recall thấp có thể làm chất lượng trông tốt giả tạo.

## Audit thủ công các bất đồng

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú và điều chỉnh rubric |
|---:|---|---|---|---|---|
| 1 | `H-008` | PASS | FAIL | Người | “anh check giúp em” quá suồng sã và đổi vai xưng hô; rubric tone cần ví dụ rõ về đại từ và ngôn ngữ chat. |
| 2 | `H-017` | PASS | FAIL | Người | “bạn ơi”, “nha” không phù hợp giọng CSKH quy định; thêm negative examples về register. |
| 3 | `H-029` | PASS | FAIL | Người | “không cần nhắn thêm” mang tính ra lệnh và đóng hội thoại; thêm tiêu chí không gây hấn/không ngăn khách tiếp tục hỗ trợ. |
| 4 | `H-042` | FAIL | PASS | Người | Câu lịch sự, rõ số tiền và thời gian; judge có false positive, nên rubric không phạt mẫu trả lời ngắn nếu vẫn đủ lễ phép. |
| 5 | `H-051` | FAIL | PASS | Người | Từ “refund” không làm tone bất lịch sự; rubric nên tách lựa chọn thuật ngữ khỏi thái độ. |
| 6 | `HL-015` | PASS | FAIL | Người | Reply nói 55.000 nhưng ledger là 40.000; judge chỉ nhìn câu chữ nên không thấy grounding sai. |
| 7 | `HL-016` | PASS | FAIL | Người | Lời xin lỗi dài không bù được số tiền sai; helpful rubric phải nhận ledger/expected amount làm evidence. |
| 8 | `HL-020` | PASS | FAIL | Người | Reply nói 90.000 trong khi ledger 120.000; cần code grader, không dùng judge đơn văn bản. |
| 9 | `HL-028` | PASS | FAIL | Người | Judge bị thuyết phục bởi văn phong lịch sự dù con số sai; tách “tone” khỏi “transaction correctness”. |
| 10 | `HL-035` | PASS | FAIL | Người | Sai amount nhưng judge PASS; đây là cùng failure family với FM-08 và phải được chấm bằng ledger assertion. |

## Kết luận

- `judge_tone` vượt cả ba floors, nên có thể dùng như metric hỗ trợ. Nó chưa phải ground truth và vẫn có 10 bất đồng trên 100 mẫu.
- `judge_helpful` bị loại: κ 0.375 và recall 0.300, nghĩa là bỏ sót 70% lỗi thật. Confusion matrix cho thấy vấn đề không phải false alarm mà là judge quá dễ PASS các câu trả lời trôi chảy nhưng sai tiền.
- Không judge nào được quyết định approval, amount hoặc ledger. Các nội dung đó dùng deterministic grader.
- Kết quả chỉ dựa trên replay public 100 mẫu; cần nhãn người mới và held-out calibration trước khi thay model, prompt hoặc rubric.
