# Rà soát trước khi đăng Zenodo, 15/11/2026

Người thực hiện: Claude (Anthropic), tiếp nối bản bàn giao của Codex. Đây
là rà soát có hỗ trợ AI do tác giả giao, chưa phải phản biện độc lập.
Không chạy thêm suy luận LLM. Không sửa dữ liệu thô hay aggregate đã lưu.

## Kết luận

**Đủ điều kiện đăng Zenodo dưới dạng exploratory audit preprint.** Chưa
đủ để gửi hội nghị như một bài thực nghiệm có kết luận khái quát. Bài
không chứng minh adaptive tốt hơn một policy có cùng ngân sách rare, và
bản thảo hiện nói rõ điều đó ngay trong abstract.

## Đã kiểm chứng lại

| Hạng mục | Kết quả |
| --- | --- |
| 18 nhóm kiểm tra của lần rà soát trước | 18/18 qua, 12 báo cáo JSON khớp bản lưu |
| E005, 3.150 cấu hình FIFO bằng số hữu tỉ | Qua |
| Lean 4.26.0, `lake build` và từng tệp với `-DwarningAsError=true` | 6 tệp qua, không `sorry`, 16 mệnh đề chỉ dùng `propext`, `Classical.choice`, `Quot.sound` |
| 76 con số trong bản thảo đối chiếu với dữ liệu lưu | Qua, script dừng nếu lệch |
| 4 bảng sinh từ script | Khớp từng byte |
| PDF | 18 trang, không cảnh báo LaTeX, không tham chiếu hỏng |
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
   commit bằng chứng `6c25fbf84ac2`.
10. **Thiếu Conclusion, danh sách đóng góp, bảng tóm tắt.** Đã thêm theo
    hướng dẫn ml-paper-writing.
11. **Tuyên bố về protocol.** Kiểm tra lịch sử git: E007 và E011 không
    có commit protocol riêng trước kết quả. Bản thảo ghi đúng như vậy.

## Điểm yếu còn lại, không sửa được bằng chỉnh sửa văn bản

- Sáu seed, một model tạo bộ nhớ, hai vòng cập nhật, đồ thị tổng hợp.
- Mọi follow-up dùng lại sáu seed cũ.
- Phân tích coverage là hậu nghiệm và không ngẫu nhiên hóa. Trên holdout
  gốc một đường cố định giải mọi truy vấn key-detour.
- Lợi thế adaptive trước balanced rare-only là hai câu ở một seed.
- Gemma chỉ đọc bộ nhớ do Qwen tạo.
- Chứng minh Lean xác nhận mô hình tham chiếu i.i.d., không xác nhận
  điểm số thực nghiệm.

## Việc chưa làm

Thí nghiệm xác nhận. Bản thiết kế nháp nằm ở
[E015](../../../experiments/E015-confirmatory/protocol-draft.md): khoảng
3.150 lượt gọi local, ước lượng 4–7 giờ với Qwen3 8B, chưa khóa và chưa
chạy. Có ba quyết định cần tác giả chọn trước khi khóa.

## Cần tác giả xem lại trước khi đăng

- Câu AI-use trong bản thảo hiện ghi cả OpenAI Codex và Anthropic Claude.
- Ngày bản thảo là 15/11/2026.
- Khi tạo bản ghi Zenodo, tải lên PDF và ZIP trong `artifacts/current/`.
