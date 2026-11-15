# Rà soát trước khi đăng Zenodo, 15/11/2026

Người thực hiện: Claude (Anthropic), tiếp nối bản bàn giao của Codex. Đây
là rà soát có hỗ trợ AI do tác giả giao, chưa phải phản biện độc lập.
Phần rà soát ban đầu không chạy suy luận LLM. Sau đó thí nghiệm xác nhận
E015 được khóa protocol rồi chạy trên Qwen3 8B local (xem mục cuối).
Không sửa dữ liệu thô hay aggregate đã lưu.

## Kết luận

**Đủ điều kiện đăng Zenodo dưới dạng audit preprint có thí nghiệm xác
nhận với kết quả âm.** Bài không chứng minh adaptive tốt hơn một policy
có cùng ngân sách rare, và thí nghiệm xác nhận E015 không xác nhận cách
đọc "khoảng cách là do giữ được coverage". Bản thảo nói rõ cả hai điều
ngay trong abstract. Giá trị của bài nằm ở phương pháp audit, mô hình
FIFO được kiểm bằng Lean, và việc tự kiểm định rồi bác bỏ cách đọc hậu
nghiệm của chính mình. Bài chưa đủ để gửi hội nghị như một bài có kết
luận thực nghiệm khái quát: một model, một miền đồ thị tổng hợp.

## Đã kiểm chứng lại

| Hạng mục | Kết quả |
| --- | --- |
| 18 nhóm kiểm tra của lần rà soát trước | 18/18 qua, 12 báo cáo JSON khớp bản lưu |
| E005, 3.150 cấu hình FIFO bằng số hữu tỉ | Qua |
| Lean 4.26.0, `lake build` và từng tệp với `-DwarningAsError=true` | 6 tệp qua, không `sorry`, 16 mệnh đề chỉ dùng `propext`, `Classical.choice`, `Quot.sound` |
| 76 + 37 con số trong bản thảo đối chiếu với dữ liệu lưu | Qua, hai script dừng nếu lệch |
| 4 bảng sinh từ script | Khớp từng byte |
| PDF | 21 trang, không cảnh báo LaTeX, không tham chiếu hỏng |
| E015: 9 test, replay 30 seed khớp aggregate từng byte | Qua |
| 4 tài liệu tham khảo mới | Lấy BibTeX từ arXiv và doi.org, đã đọc abstract |

Log Lean: [lean-check.log](lean-check.log).

## Lỗ hổng tìm thấy và cách xử lý

1. **Diễn giải sai trọng tâm của kết quả chính.** Bản cũ trình bày
   adaptive 18/18 so với mixture 7/18 như một mức cải thiện. Bộ nhớ
   không cập nhật đã đạt 16/18 và bộ nhớ rỗng đạt 7/18. Mixture đánh
   mất ví dụ key-detour ở 4/6 seed rồi rơi về mức bộ nhớ rỗng. Phân
   tích hậu nghiệm E014: bộ nhớ còn ví dụ key-detour trả lời đúng 80/87,
   bộ nhớ đã mất trả lời đúng 9/39. Bản thảo được viết lại quanh ý
   này: khoảng cách chủ yếu là giữ được coverage.
2. **Con số 3/18 unreachable của mixture gây hiểu nhầm.** Cả ba câu
   đúng nằm ở seed 6204, nơi model trả lời "unreachable" cho cả sáu
   truy vấn rare, gồm ba câu key-detour sai. Đã ghi rõ.
3. **E009 thiếu thước đo bất định.** Đã thêm giá trị sign-flip hậu
   nghiệm 0,50 trên 64 cách đổi dấu và gọi kết quả là exploratory ở
   abstract, Results và Discussion.
4. **Lean chưa phủ hết Section 4.** Bản cũ không chứng minh trọng số
   là một phân phối xác suất và không chứng minh ngưỡng proposal-share.
   Đã thêm 8 định lý: chuẩn hóa, giá trị nằm trong [0,1], ngưỡng, và
   hai ví dụ số trong bài.
5. **Lean và mã Python chưa được nối với nhau.** Đã replay bổ đề
   `foldl_admit_absent_iff` trên 42 quỹ đạo cập nhật đã lưu: 126 phép
   kiểm, 0 lệch. Cả 32 lần mất một family rare đều không có admission
   mới của family đó.
6. **Giả định của mệnh đề chưa tường minh.** Đã ghi `K ≥ 1`,
   `u, v ≥ 0`, `u + v ≤ 1`, `0 < δ < 1`, `p ∈ [0, 1]`.
7. **Ba đối chứng chưa kết hợp.** Đã thêm một đoạn Discussion nói rõ
   E009, E012, E013 mỗi cái đổi một yếu tố và không được ghép kết luận.
8. **Định vị với literature.** Đã thêm Liu & Ding (2610.11188) và
   Zhang et al. (2603.04549), và ghi rõ ground-truth memory, matched
   budget, label permutation đều đã có ở công trình trước.
9. **Người chỉ có PDF không tìm được dữ liệu.** Đã chèn link repo và
   commit bằng chứng (hiện là `7df0cbdbc499`).
10. **Thiếu Conclusion, danh sách đóng góp, bảng tóm tắt.** Đã thêm theo
    hướng dẫn ml-paper-writing.
11. **Tuyên bố về protocol.** Kiểm tra lịch sử git: E007 và E011 không
    có commit protocol riêng trước kết quả. Bản thảo ghi đúng như vậy.

## Điểm yếu còn lại, không sửa được bằng chỉnh sửa văn bản

- Phần exploratory: sáu seed, hai vòng cập nhật; E003–E013 dùng lại sáu
  seed đó. Phần xác nhận: 30 seed mới nhưng vẫn một model, đồ thị tổng hợp.
- E015 đổi cùng lúc bộ sinh, số vòng và định dạng readout nên không chỉ
  ra yếu tố nào làm mất khoảng cách.
- Phân tích coverage là hậu nghiệm và không ngẫu nhiên hóa. Trên holdout
  gốc một đường cố định giải mọi truy vấn key-detour.
- Lợi thế adaptive trước balanced rare-only là hai câu ở một seed.
- Gemma chỉ đọc bộ nhớ do Qwen tạo.
- Chứng minh Lean xác nhận mô hình tham chiếu i.i.d., không xác nhận
  điểm số thực nghiệm.

## Thí nghiệm xác nhận E015 (đã chạy)

[Protocol](../../../experiments/E015-confirmatory/protocol.md) được khóa
và commit trước mọi lượt gọi; [kết quả](../../../experiments/E015-confirmatory/analysis.md).
30 seed mới, 4 vòng cập nhật, đường key-detour đa dạng ở mọi pool, mỗi
lượt gọi một truy vấn, 2.790 lượt gọi, 2,84 giờ.

| Câu hỏi | Kết quả |
| --- | --- |
| Chính: frozen − mixture, key-detour | 55/90 so với 51/90; +4,4 điểm; khoảng −5,6 đến +13,3; sign-flip 0,51. **Không xác nhận** |
| Phụ: adaptive − balanced, rare | −1,7 điểm; Holm 0,51. Không xác lập |
| Phụ: tương tác nhãn | −5,0 điểm; Holm 0,36. Không xác lập, hướng E009 không lặp lại |

Mixture chỉ giữ ví dụ key-detour ở 6/30 seed nhưng độ chính xác không
giảm; bộ nhớ rỗng đạt 53/90. Ví dụ lưu giúp khi chứa đúng đường tối ưu
của truy vấn (29/32) và không giúp khi chứa đường khác (116/208, so với
129/210 khi không có ví dụ). Unreachable: 0/450 đúng, 0/208 được nhận
vào bộ nhớ, model không lần nào trả lời "unreachable". Quy tắc adaptive
vì thế dồn 84/120 supplement vào family mà model không giải được.

Sai lệch đã ghi: Ollama tự cập nhật lên 0.40.16 trước lượt gọi đầu
(Amendment 1); một câu trả lời ở phần nhãn chạm giới hạn token và bị
chấm sai theo protocol.

## Cần tác giả xem lại trước khi đăng

- Câu AI-use trong bản thảo hiện ghi cả OpenAI Codex và Anthropic Claude.
- Ngày bản thảo là 15/11/2026.
- Khi tạo bản ghi Zenodo, tải lên PDF và ZIP trong `artifacts/current/`.
