# Phân tích sau khi gom dự án

Bản thảo được kiểm tra tại commit `12c21371d838fdd27e360aade4a7b7f371d861e6`. [Báo cáo rà soát ban đầu](../review-2026-11-15/REVIEW_VI.md) ghi chi tiết từng nhận định và nguồn tham khảo.

## Kiểm chứng

- Chạy lại 18 nhóm kiểm tra từ thư mục mới. Bốn bộ unit test có tổng cộng 15 test. Tất cả 12 báo cáo JSON khớp bản lưu và E005 khớp ở 3.150 cấu hình FIFO. [Kết quả từng bước](checks.json)
- Bộ chấm dùng relaxation trên không gian trạng thái đồng ý với bộ chấm của dự án ở cả 2.808 yêu cầu trả lời trong 408 bản ghi. Đây là số ghi nhận khi chấm, trong đó có truy vấn xuất hiện ở nhiều điều kiện. [Kết quả đối chiếu](independent_check.json)
- Kiểm tra lại Lean 4.26.0 trên năm tệp nguồn khớp từng byte với repo. Bảy định lý được in danh sách axiom và không dùng `sorryAx`. [Log build](lean-build.log) · [Log kiểm tra Lean](lean-check.log)
- Sáu tệp ZIP vượt qua kiểm tra toàn vẹn. Cả 179 tệp trong ZIP tái lập hiện tại khớp nội dung với các tệp tương ứng trong repo. Báo cáo và log của lần rà soát trước khớp checksum trong manifest.

Lần này dùng câu trả lời đã lưu và cache dependency Lean hiện có. Đánh giá về khả năng khái quát vẫn dựa trên các thí nghiệm cũ.

## Kết quả ảnh hưởng đến quyết định công bố

| Câu hỏi | Kết quả | Phạm vi |
| --- | --- | --- |
| Adaptive cải thiện so với lấy mẫu theo tần suất tham chiếu? | E002 có +22,2 điểm phần trăm rare macro. Mixture lấy 3/12 lượt bổ sung cho rare, adaptive lấy 12/12. | Chênh lệch gồm cả tác động của ngân sách rare và quy tắc chọn ví dụ. |
| Adaptive còn cải thiện khi cùng ngân sách rare? | E012 có +5,6 điểm rare macro. Sáu chênh lệch theo seed là `[0,0,0,0,0,2]` câu đúng trên sáu. | Bỏ seed 6206 thì chênh lệch quan sát bằng 0. E013 cũng dồn toàn bộ lợi thế trước balanced vào seed này. Đây là kiểm tra độ nhạy, chưa đủ để kết luận tương đương. |
| Hiệu ứng còn khi đổi đường đi? | E013 cho thấy adaptive giảm từ 18/18 xuống 7/18, balanced giảm từ 16/18 xuống 5/18. Đường cố định tốt nhất giảm từ 18/18 xuống 2/18. | Bộ nhớ đã được tạo bằng generator cũ. Bằng chứng cho thấy độ nhạy khi đổi holdout, trong phạm vi readout. |
| Gán nhãn chung làm thay đổi khoảng cách giữa hai policy? | E009 có trung bình +19,4 điểm. Bốn seed dương, hai seed âm. Phép đổi dấu hậu nghiệm cho p hai phía = 0,50. | Kết quả thăm dò trên generator gốc và comparator mixture. Kiểm tra đổi dấu phụ thuộc giả định sign exchangeability. |
| Lean củng cố phần nào? | Công thức xác suất vắng mặt của một family trong FIFO được kiểm tra với mô hình i.i.d. và trọng số cố định. | Cơ chế suy giảm coverage dưới các giả định đó có thể kiểm chứng. Hiệu quả thực nghiệm của adaptive là một câu hỏi riêng. |

Đóng góp hiện tại nằm ở quy trình audit và bằng chứng cho thấy một lợi thế quan sát được có thể thu hẹp khi thay comparator hoặc truy vấn. Có cơ sở công bố preprint dưới dạng nghiên cứu thăm dò sau khi chỉnh cách trình bày E009, cập nhật Related Work, ghi rõ giả định FIFO và dẫn tới repo trong PDF. Trước khi gửi full paper, tôi ưu tiên thí nghiệm kết hợp **cùng ngân sách rare, generator đa dạng ngay từ acquisition và biểu diễn được đối sánh** trên seed mới. Nếu có đủ tài nguyên, lặp acquisition trên mô hình thứ hai. [Thiết kế và tiêu chí nghiệm thu](../../../HANDOFF_NEXT_AGENT.md#9-việc-b-thiết-kế-thí-nghiệm-xác-nhận-ưu-tiên-cao-nhất)

## Chạy lại

Từ thư mục gốc của dự án:

```sh
python3 artifacts/review/reanalysis-2026-11-15/run_checks.py
python3 artifacts/review/reanalysis-2026-11-15/independent_check.py
```

Lệnh đầu ghi lại log trong thư mục phân tích này. Cả hai script xác định đường dẫn repo từ vị trí của chính chúng. Hướng dẫn Lean nằm trong [formal/README.md](../../../formal/README.md).
