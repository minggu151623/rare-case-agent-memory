# Rà soát mức sẵn sàng công bố, 15/11/2026

Bản được rà soát: `12c21371d838fdd27e360aade4a7b7f371d861e6`, **Auditing Rare-Case Coverage in LLM Agents with Iterative Example Memory**. Đây là một lần kiểm tra lại bởi Codex, không phải phản biện độc lập của người hoặc nhóm nghiên cứu khác. Không chạy thêm suy luận LLM, không thay đổi dữ liệu, không đăng bài.

## Kết luận

**Có cơ sở để công bố một preprint nghiên cứu thăm dò, sau một lượt chỉnh sửa ngắn về định vị, thống kê và khả năng truy cập bằng chứng. Chưa nên mô tả đây là một nghiên cứu đã chứng minh chính sách thích nghi tốt hơn một cách ổn định.**

Nếu nhắm workshop về đánh giá agent/memory, bài có một hướng phù hợp để phát triển, nhưng tôi khuyên bổ sung một thí nghiệm xác nhận trước khi gửi. Với một full paper đòi hỏi đóng góp thực nghiệm có khả năng khái quát cao, bằng chứng hiện còn mỏng. Đây là đánh giá chuyên môn của lần rà soát, không phải dự báo xác suất được nhận hay xác nhận đáp ứng quy định của một venue cụ thể.

Điểm mạnh là bằng chứng được lưu và có thể kiểm tra. Điểm yếu là độ rộng và tính xác nhận của kết quả. Số trang không giải quyết được điểm yếu này.

## Những gì thực sự đã kiểm tra

- Đọc toàn bộ `paper/main.tex`, các bảng được chèn, danh mục tài liệu, claim audit, hướng dẫn tái lập, trạng thái nghiên cứu và các protocol/kết quả liên quan.
- Chạy lại 18 nhóm kiểm tra. Bốn bộ unit test có tổng cộng 15 test, đều qua. Các báo cáo E002–E013 có lệnh tái lập đều chạy thành công; 12 đầu ra JSON so sánh bằng nội dung khớp bản lưu. E002 dựng lại 84 lượt gọi và các quyết định cập nhật bộ nhớ.
- E005 kiểm tra đúng 3.150 cấu hình bằng số hữu tỉ.
- Viết một bộ chấm kiểm tra riêng, dùng relaxation trên không gian trạng thái thay cho BFS của chương trình. Đối chiếu 2.808 câu trả lời được yêu cầu trong 408 bản ghi gọi mô hình của chín thí nghiệm: không có bất đồng với bộ chấm hiện tại. Câu trả lời thiếu cũng được tính. Những bản ghi này có cả truy vấn lặp lại, nên không phải 2.808 mẫu độc lập.
- Chạy `lake build` và kiểm tra lại từng tệp Lean bằng `lake env lean -DwarningAsError=true`. Năm tệp đều thành công. Mã nguồn và cấu hình trong checkout có bộ công cụ Lean khớp từng byte với repo được rà soát. Axiom của bảy định lý xuất ra chỉ có `propext`, `Classical.choice`, `Quot.sound`, không có `sorryAx`.
- Sinh lại hai bảng E012/E013, khớp từng byte với bản thảo.
- Kiểm tra các bản ghi sơ cấp của tài liệu hiện có và tìm thêm công trình gần chủ đề. Đây là tìm kiếm có mục tiêu, không phải systematic review chứng minh không tồn tại prior art.

Giới hạn: replay xác nhận tính nhất quán của dữ liệu lưu, không xác nhận độc lập việc thu thập ban đầu. Lần này không tải lại model để tái chạy inference, không dựng lại toàn bộ Mathlib từ nguồn, không biên dịch và duyệt lại bố cục PDF. Các dependency Lean hiện có được dùng để kiểm tra lại mã nguồn dự án. Không phát hiện lỗi chấm điểm hoặc lỗi chứng minh làm mất hiệu lực các con số đã kiểm tra.

Log và chương trình tái kiểm tra nằm cùng thư mục báo cáo: `checks.json`, `independent_check.json`, `lean-checks.json`, `table-checks.json`, `run_checks.py`, `independent_check.py`, cùng stdout/stderr của các bước.

## Đóng góp có thể bảo vệ hiện nay

1. **Một audit có kiểm soát về kết luận so sánh chính sách bộ nhớ.** So với mixture, adaptive đạt 18/18 thay vì 7/18 ở detour gốc; đối chứng có cùng ngân sách rare đạt 16/18. Trên truy vấn có chín đường tối ưu khác nhau, ba con số tương ứng là 7/18, 3/18 và 5/18. Đây là bằng chứng cụ thể rằng cách cấp ngân sách và xây dựng truy vấn ảnh hưởng mạnh đến cách diễn giải kết quả.
2. **Một phép so sánh giữ nguyên từng bản biểu diễn đồ thị, thay đổi cách chúng xuất hiện cùng nhau trong prompt.** E009 là phần thiết kế đáng giữ: nó loại bớt lời giải thích rằng một điều kiện vô tình nhận các đồ thị đã đổi nhãn dễ hơn. Tuy nhiên, bằng chứng định lượng hiện chỉ có tính mô tả trên sáu seed.
3. **Một artifact có thể kiểm chứng, gồm mô hình FIFO được formalize.** Lean xác nhận công thức hữu hạn, trường hợp không có admission, giới hạn và ngưỡng mất ví dụ ban đầu. Đây là đóng góp về độ tin cậy và khả năng kiểm tra; công thức binomial thinning và giới hạn `(1-q)^K` tự thân chưa cho thấy tính mới lý thuyết đáng kể.

Không được nâng các đóng góp trên thành: giải quyết model collapse; chứng minh LLM tự cải thiện bền vững; phát hiện lần đầu độ nhạy với nhãn; chứng minh adaptive vượt balanced; hoặc Lean xác nhận toàn bộ bài báo.

## Những điểm cần xử lý, theo mức ảnh hưởng

### 1. Kết quả E009 cần cách trình bày bất định rõ hơn

Vị trí: `paper/main.tex:517`, Abstract và đoạn thảo luận về matched exposure.

Các chênh lệch theo seed, tính bằng số câu đúng trên sáu câu, là `[3,6,-4,2,-1,1]`. Lần rà soát này tính thêm kiểm tra đổi dấu hai phía trên đủ 64 cấu hình: **p = 0.500**. Đây là phân tích hậu nghiệm theo giả định sign exchangeability, cùng loại phép nhạy cảm đã dùng ở các phần khác; không phải kiểm định ngẫu nhiên hóa được bảo đảm bởi thiết kế.

Điều này không chứng minh hiệu ứng bằng không. Tuy nhiên, nó cho thấy trung bình +19,4 điểm chưa tạo bằng chứng thống kê mạnh theo phép kiểm tra đó. Khoảng leave-one-seed-out 3,3–36,7 không phải khoảng tin cậy và việc các trung bình đó đều dương không thay thế được suy luận thống kê. Bản thảo đã gọi chúng là mô tả, nên đây là yêu cầu làm rõ thêm, không phải cáo buộc báo cáo sai.

Trước preprint: gọi E009 là exploratory/descriptive ngay trong Abstract; bổ sung phép nhạy cảm hậu nghiệm với nhãn rõ ràng hoặc giải thích trực tiếp rằng chưa có suy luận xác nhận. Không thêm p-value rồi tuyên bố không có hiệu ứng.

### 2. Ba đối chứng quan trọng chưa được kết hợp trong một thí nghiệm

E009 giữ nguyên từng bản rendering nhưng dùng bộ đồ thị ban đầu và comparator mixture. E012 cân bằng tổng ngân sách rare nhưng dùng holdout có shortcut. E013 thay đường tối ưu nhưng chưa làm matched-label comparison trên bộ đó và bộ nhớ vẫn được tạo từ generator cũ.

Vì vậy, chưa biết tương tác giữa chính sách và nhãn còn tồn tại khi đồng thời dùng đối chứng rare cân bằng và generator đa dạng. Các thí nghiệm hiện tại hữu ích riêng rẽ; ghép kết luận của chúng không tương đương đã kiểm tra thiết kế kết hợp. Đây là khoảng trống đáng ưu tiên nhất nếu muốn tăng đóng góp.

### 3. Hiệu quả thích nghi và khả năng khái quát còn hạn chế

E012 hơn balanced đúng hai câu, đều ở seed 6206; năm seed còn lại hòa. E013 giữ đúng khoảng cách này ở cùng seed. Frozen memory của E002 đã đạt 16/18 detour, bằng balanced. Không có bằng chứng rằng cần cập nhật thích nghi để đạt phần lớn điểm số trên holdout gốc.

Hai update round và sáu seed không đại diện cho hành vi dài hạn. Gemma E010 chỉ đọc bộ nhớ do Qwen tạo trên sáu câu; E006 bị thiếu câu trả lời nghiêm trọng. Đây không phải replication của toàn bộ quá trình tạo bộ nhớ trên mô hình thứ hai.

Không cần giấu kết quả yếu. Nên đặt trọng tâm là audit về độ vững của phép đánh giá, giữ kết luận superiority ở trạng thái chưa được xác nhận.

### 4. Tính mới cần được định vị hẹp hơn với literature mới

- [Xiong et al., How Memory Management Impacts LLM Agents](https://arxiv.org/html/2505.16067v2) đã khảo sát thêm/xóa bộ nhớ và dùng biến thể thay execution bằng ground truth. Vì thế oracle-memory comparison không phải đóng góp đầu tiên của bài này.
- [Lost in Serialization](https://arxiv.org/abs/2511.10234v3) đã nghiên cứu bất biến trước đổi nhãn và thay biểu diễn đồ thị. Điểm khác cần nhấn mạnh là **policy contrast** với các renderings được đối sánh, không phải phát hiện chung rằng graph LLM nhạy với nhãn.
- [What to Admit and How to Present](https://arxiv.org/html/2610.11188v1), tháng 10/2026, đã tách admission/presentation và có đối chứng matched admission budget trong một miền khác. “Tách selection khỏi presentation” hoặc “dùng matched budget” riêng lẻ không đủ làm tuyên bố mới. Bài đó xét thông tin đưa vào working context, còn nghiên cứu hiện tại xét ví dụ giải đúng được thêm vào FIFO và giữ lại; cần nói rõ khác biệt này.
- [Adaptive Memory Admission Control](https://arxiv.org/abs/2603.04549) là công trình liên quan đến quyết định admission trên LoCoMo. Không thể áp thẳng thuật toán đó làm baseline cho graph planning, nhưng nên phân biệt loại admission và mục tiêu của hai nghiên cứu.

Hai công trình cuối hiện chưa có trong bibliography. Nên thêm so sánh ngắn, tránh kéo dài Related Work bằng danh sách tên bài. Chưa đủ cơ sở tuyên bố đây là nghiên cứu đầu tiên làm tổ hợp hiện tại.

### 5. Những sửa nhỏ trước khi phát hành

- Section 4: ghi rõ `K ≥ 1`, `u,v ≥ 0`, `u+v ≤ 1`; phần ngưỡng thêm `0 < δ < 1`. Đây là làm tường minh miền áp dụng, không phải phát hiện công thức sai.
- Reproducibility: chèn đường dẫn repo và commit bất biến ngay trong PDF. Cụm “accompanying archive” không giúp người chỉ nhận được PDF tìm dữ liệu.
- Đồng bộ ngày bản thảo với bản phát hành. Cân nhắc trích dẫn Lean/Mathlib nếu phần formalization được quảng bá như một thành phần đóng góp.
- Tổ chức mở bài quanh hai kết quả audit và một artifact; bớt cảm giác liệt kê E002 đến E013. Có thể chuyển chi tiết chẩn đoán Gemma và vài bảng sang phụ lục. Không cần tăng số trang.

## Công việc bổ sung có giá trị nhất

### Ưu tiên 1: Một thí nghiệm xác nhận kết hợp

Câu hỏi: **Sau khi cân bằng ngân sách rare và loại shortcut của generator, cách gán nhãn giữa ví dụ và truy vấn còn làm thay đổi thứ hạng chính sách bộ nhớ không?**

Thiết kế đề xuất, chưa phải protocol đã khóa:

- Tách các seed và đồ thị mới khỏi E001–E013. Đa dạng đường tối ưu ngay trong acquisition và evaluation; kiểm tra baseline đường cố định trước khi chạy model.
- So adaptive với balanced rare-only; giữ frozen và empty làm mốc. Giữ cùng số lượt gọi, task slots, giới hạn token và scorer. Ghi cả thời gian/token thực dùng.
- Khi đo readout, giữ nguyên từng bộ nhớ và graph; đối sánh các renderings giữa shared/mixed conditions. Có điều kiện một query mỗi lần gọi để tách ảnh hưởng giữa các query trong batch. Phân biệt nhất quán nhãn trong memory với sự tương ứng memory–query nếu muốn nêu cơ chế.
- Lặp cả acquisition trên ít nhất hai model. Dùng cùng dạng giao diện trả lời và kiểm tra completeness trên bộ phát triển trước khi khóa thí nghiệm.
- Xác định trước interaction chính, đơn vị ghép cặp là seed, thước đo bất định và quy tắc dừng. Chọn số seed dựa vào độ chính xác cần đạt hoặc power cho hiệu ứng tối thiểu có ý nghĩa; không mặc định 12 hay 24 seed chắc chắn đủ và không chạy đến khi p < .05.

Nếu hiệu ứng còn: bài có bằng chứng vững hơn cho điều kiện mà kết luận về chính sách phụ thuộc biểu diễn. Nếu mất: đó là kết quả âm có giá trị, cho thấy một hiệu ứng audit ban đầu không bền sau các kiểm soát. Cả hai đều đáng báo cáo; không đặt mục tiêu buộc adaptive phải thắng.

### Ưu tiên 2: Thử một cơ chế giữ coverage và đo chi phí của nó

So FIFO với bảo vệ ví dụ cuối của từng family hoặc quota theo family, dưới cùng ngân sách. Đo mất coverage, độ cũ của ví dụ, held-out accuracy và tác động khi phân phối đổi. Đây là cách nối quan sát admission/eviction với một can thiệp có thể sử dụng.

Việc quota giữ được quota là hệ quả thiết kế, không phải phát hiện mới. Đóng góp chỉ mạnh hơn nếu xác định được khi nào bảo vệ coverage thực sự giúp readout, khi nào giữ ví dụ cũ gây hại, và so sánh được với những baseline hợp lý. Không nên thêm một policy đơn giản chỉ để có tên thuật toán mới.

### Ưu tiên 3: Mở rộng lý thuyết khi có câu hỏi thực nghiệm cụ thể

Có thể nghiên cứu bảo đảm khi admission phụ thuộc lịch sử hoặc khi có ràng buộc ngân sách. Nhưng một cận đơn giản từ xác suất focal có điều kiện thường chỉ là mở rộng kỹ thuật; formalize thêm chưa tự tạo tính mới đáng kể. Không áp dụng công thức i.i.d. cho adaptive bằng cách cắm pass rate trung bình vào.

Với mục tiêu nâng chất lượng chính bài này, ưu tiên thí nghiệm kết hợp ở trên trước việc mở rộng Lean.

## Quyết định khuyến nghị

Nếu muốn chia sẻ sớm: hoàn tất các sửa trình bày ở trên, công bố như **exploratory audit preprint**, nêu rõ sáu seed, phạm vi synthetic, kết quả âm và chưa có lợi thế adaptive được xác nhận.

Nếu muốn một bản thảo mạnh hơn trước khi gửi phản biện: thực hiện một thí nghiệm xác nhận có thiết kế kết hợp thay vì thêm nhiều chẩn đoán nhỏ trên sáu seed cũ. Những bổ sung đó có thể nâng giá trị khoa học; thêm trang hoặc thêm chứng minh cho cùng một mệnh đề thì không chắc.
