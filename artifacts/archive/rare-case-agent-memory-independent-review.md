# Yêu cầu phản biện độc lập bản thảo cs.AI

Hãy phản biện bản thảo *Auditing Rare-Case Coverage in LLM Agents with Iterative Example Memory* như một reviewer trước khi tác giả đăng preprint. Tôi cần đánh giá về độ mới, độ vững của bằng chứng và phạm vi kết luận. Hãy nêu thẳng nếu đóng góp quá hẹp, kết quả chủ yếu lặp lại công trình trước, hoặc thí nghiệm chưa phân biệt được các cách giải thích cạnh tranh. Đánh giá số trang theo lượng nội dung cần để hiểu, kiểm tra và tái lập bài.

## Tài liệu cần gửi cùng file này

| Tệp | Nội dung |
| --- | --- |
| rare-case-agent-memory-extended.pdf | Bản thảo 12 trang, gồm phụ lục và tài liệu tham khảo |
| rare-case-agent-memory-extended-reproducibility.zip | LaTeX, mã Python, protocol, phản hồi gốc, số liệu tổng hợp và hướng dẫn tái lập |

Hai tệp trên tương ứng với commit [dfe206205f6d5f957e0fa7402a37e9cd0e1ea483](https://github.com/minggu151623/rare-case-agent-memory/commit/dfe206205f6d5f957e0fa7402a37e9cd0e1ea483). Repo GitHub là private. ZIP đủ để kiểm tra nội dung chính khi không có quyền truy cập repo. Mọi đường dẫn dưới đây tính từ thư mục **rare-case-agent-memory** sau khi giải nén.

Đọc PDF và tự ghi lại đóng góp chính, nghi vấn và đánh giá sơ bộ trước khi mở phần tổng hợp bên dưới hoặc file tự phản biện của nhóm. Đối chiếu số liệu với dữ liệu gốc, protocol và mã chấm. Sau khi hình thành nhận định riêng, có thể đọc **paper/claim-audit.md** và **findings.md** để xem nhóm đã ghi nhận những giới hạn nào. Nếu chỉ đọc được PDF hoặc không chạy được mã, hãy nói rõ phần nào chỉ kiểm tra được ở mức văn bản.

<details>
<summary>Bản đồ công việc và bằng chứng để đối chiếu sau lượt đọc đầu</summary>

### Câu hỏi và thiết lập

Bài nghiên cứu bộ nhớ ví dụ của agent LLM giữ nguyên trọng số. Mỗi ví dụ là một bài lập kế hoạch trên đồ thị có hướng và lời giải. Bộ giải chính xác tìm đường đi ngắn nhất trên trạng thái *(đỉnh, đã có chìa khóa)*, rồi kiểm tra đường đi hợp lệ hoặc xác nhận bài vô nghiệm. Bộ nhớ có giới hạn và loại ví dụ cũ theo FIFO. Phân tích tách tỷ lệ **thử giải, giải đúng, đưa vào bộ nhớ, giữ lại và giải đúng bài mới** theo từng họ bài.

### Các phần đã thực hiện

Các kết quả dưới đây lấy từ báo cáo của nhóm. Reviewer nên tái tính các con số quyết định nhận định của mình.

| Mốc | Việc đã làm và kết quả được báo cáo | Bằng chứng |
| --- | --- | --- |
| E000–E001 | Kiểm tra bộ giải và bộ chấm. Pilot đầu phát hiện model chọn nhầm ID từ bộ nhớ. Pilot sửa schema cho thấy cả 7 lượt thử giải bài vô nghiệm đều sai, và ví dụ vô nghiệm cũ bị loại khỏi cả ba bộ nhớ. | **experiments/E000-oracle-smoke/analysis.md**, **experiments/E001-memory-coverage/analysis.md** |
| E002 | Thiết kế ghép cặp 2×2 trên sáu seed, gồm chọn ngẫu nhiên hoặc có chủ đích, kết hợp lời giải model hoặc lời giải chuẩn cho ví dụ bổ sung. Lời giải chuẩn giúp nhánh có chủ đích giữ thêm trung bình 0,67 ví dụ vô nghiệm, còn cả hai nhánh có chủ đích đều đạt 0/18 trên họ này. Nhánh có chủ đích dùng lời giải model tăng 22,2 điểm phần trăm trên điểm trung bình hai họ hiếm so với ngẫu nhiên, với kết quả ngược chiều giữa hai họ. | **experiments/E002-admission/** |
| E003 | Giữ bộ nhớ đã tạo, đổi nhãn đỉnh của cả ví dụ và đề. Nhánh có chủ đích giảm từ 18/18 xuống 1/18 trên bài đi vòng lấy chìa khóa. Trên mẫu đồ thị mới, nhánh có chủ đích đạt 9/18 và ngẫu nhiên đạt 10/18. | **experiments/E003-transfer/** |
| E004 | Tách đổi nhãn trong ví dụ và trong đề bằng thiết kế 2×2. Điểm nhánh có chủ đích lần lượt là 18/18 ở gốc, 3/18 khi chỉ đổi ví dụ, 2/18 khi chỉ đổi đề, 1/18 khi đổi độc lập cả hai. Thêm đối chứng dùng chung một phép hoán vị, cho kết quả 12/18 ở nhánh có chủ đích và 2/18 ở nhánh ngẫu nhiên. | **experiments/E004-representation/** |
| E005 | Suy ra xác suất vắng mặt của một họ bài trong bộ nhớ FIFO khi các lượt thử độc lập, cùng phân phối và bộ nhớ ban đầu đầy. Đối chiếu công thức với 3.150 trường hợp bằng số hữu tỉ. | **experiments/E005-fifo-null/**, mệnh đề và chứng minh trong PDF |
| E006, E010 | Gemma 4 E4B đọc bộ nhớ đã tạo bằng Qwen. Với chín câu mỗi lượt, cả 60 phản hồi Gemma chỉ chứa ID câu đầu. Khi hỏi từng bài, model trả đủ 36 đáp án. Nhánh có chủ đích đạt 4/6 với nhãn gốc, 0/6 khi đổi nhãn độc lập và 3/6 khi dùng chung phép đổi nhãn. Nhánh ngẫu nhiên đạt 1/6 ở cả ba điều kiện. Có thay đổi model, backend và grammar đầu ra giữa Qwen và Gemma. Việc chọn Gemma thay Phi sau lỗi tải và sửa grammar sau một lượt chẩn đoán được ghi trong amendment. | **experiments/E006-cross-model/**, **experiments/E010-single-query/** |
| E007 | Phân loại lỗi sau khi đổi nhãn. Trong 17 câu đi vòng của nhánh có chủ đích từng đúng rồi sai, có 8 lỗi qua cạnh khóa quá sớm, 7 lỗi dùng cạnh không tồn tại, 2 lỗi sai đầu mút và 0 trường hợp lặp nguyên chuỗi đường đi cũ. | **experiments/E007-error-audit/** |
| E008 | Áp dụng đổi nhãn độc lập ngay từ lúc tạo và cập nhật bộ nhớ. Nhánh có chủ đích đạt 2/18 và ngẫu nhiên đạt 3/18 trên bài đi vòng. | **experiments/E008-end-to-end/** |
| E009 | Giữ đúng hai dạng hiển thị của từng đồ thị ở cả hai điều kiện. Điều kiện chung dùng một phép đổi nhãn cho cả prompt, điều kiện trộn luân phiên hai phép. Chênh lệch giữa có chủ đích và ngẫu nhiên trên bài đi vòng là +10/36 khi dùng chung và +3/36 khi trộn. Hiệu số là +7/36, tức +19,4 điểm phần trăm. Hiệu số theo seed đổi dấu ở 2/6 seed. Mẫu số 36 là 18 đồ thị, mỗi đồ thị xuất hiện hai lần. | **experiments/E009-matched-labels/** |

</details>

## Các câu hỏi phản biện

1. **Độ mới.** Tự xác định phát biểu mới nhất mà bài thực sự chứng minh. Đọc *Lost in Serialization* về đổi nhãn đồ thị và Xiong et al. về cập nhật bộ nhớ bằng lời giải chuẩn. Tìm thêm công trình gần hơn về few-shot graph reasoning, tính nhất quán giữa ví dụ và truy vấn, hoặc chọn ví dụ. Đối chiếu thiết kế và kết quả cụ thể. Việc chưa tìm thấy một bài trùng khớp chưa đủ để xác nhận tính nguyên gốc. [Herbst et al.](https://arxiv.org/abs/2511.10234v3) · [Xiong et al.](https://arxiv.org/html/2505.16067v2)
2. **Tái lập và thống kê.** Tính lại các bảng và chênh lệch chính. Kiểm tra mẫu số, đơn vị ghép cặp, cách chấm câu thiếu, thứ tự các lượt, và nguy cơ dùng lại đề giữ kín trong bộ nhớ. Các thí nghiệm nối tiếp dùng lại nhiều seed, đồ thị và bộ nhớ. Chỉ rõ kết luận nào là khám phá sau khi xem kết quả, và đâu là bằng chứng từ dữ liệu mới. Kiểm tra giả định của phép sign-flip E002.
3. **E004 và E009 có cô lập được điều cần đo không?** Kiểm tra phép đổi nhãn có giữ cạnh, khóa, vai trò đỉnh, đáp án và thứ tự không. Trong E009, xác nhận mỗi đồ thị có cùng hai dạng hiển thị ở cả hai điều kiện. Sau đó xem những yếu tố nào vẫn thay đổi cùng lúc, ví dụ vị trí đồ thị và tương ứng nhãn giữa bộ nhớ và đề. Thử tìm một cách giải thích thay thế phù hợp với kết quả theo từng seed.
4. **Thiết kế bộ sinh.** Kiểm tra việc loại đồ thị đẳng cấu có đủ để loại lối tắt theo mẫu đường đi hay không. Đánh giá khác biệt giữa họ vô nghiệm và các họ có nghiệm, gồm độ khó và dạng câu trả lời. E003 đổi cấu trúc đồng thời lấy mẫu đề mới, còn E008 có thể thay đổi chính các ví dụ được nhận vào. Hãy xác định mỗi phép so sánh hỗ trợ kết luận nào.
5. **Gemma.** Đánh giá riêng việc trả đủ đáp án và giải đúng. Kiểm tra cách chọn sáu bài trong E010 và mức độ so sánh được với Qwen khi số bài mỗi prompt, grammar và backend khác nhau. Có thể gọi đây là bằng chứng cùng chiều đến mức nào?
6. **Mệnh đề FIFO.** Tự kiểm tra chứng minh, gồm các biên như không có lượt được nhận, họ đã vắng ở trạng thái đầu, hoặc số lượt được nhận ít hơn sức chứa. Đánh giá giá trị giải thích của mệnh đề và liệu phần lý thuyết có tạo thêm đóng góp ngoài một phép tính tham chiếu theo giả định độc lập.
7. **Bản thảo.** So sánh tiêu đề, abstract, discussion và limitations với bằng chứng. Trích nguyên câu cần sửa cùng trang hoặc mục. Đề xuất thí nghiệm hoặc phân tích bổ sung khi nó phân biệt được hai cách giải thích cụ thể. Nếu có thể sửa bằng cách thu hẹp câu chữ, hãy nêu chính xác cách sửa.

## Chạy lại từ ZIP

Xem **paper/README.md** để có lệnh biên dịch PDF và toàn bộ lệnh tái lập. Các kiểm tra dưới đây cần Python 3.10+ và dùng phản hồi đã lưu. Chạy lại suy luận là một phép kiểm tra khác, phụ thuộc vào model, backend và cấu hình tương ứng.

~~~
a=experiments/E002-admission/results/qwen3-8b
b=experiments/E003-transfer/results/qwen3-8b
g=experiments/E006-cross-model/results/gemma-e4b

python3 -m src.admission_audit "$a"
python3 -m src.admission_report "$a"
python3 -m src.transfer_report "$a" "$b"
python3 -m src.representation_report "$a" "$b" experiments/E004-representation/results/qwen3-8b
python3 experiments/E005-fifo-null/verify.py
python3 -m src.representation_report "$a" "$b" "$g" --cross-model
python3 -m src.gemma_diagnostics "$g"
python3 -m src.path_errors "$a" "$b"
python3 -m src.end_to_end experiments/E008-end-to-end/results/qwen3-8b --audit
python3 -m src.matched_labels "$a" experiments/E009-matched-labels/results/qwen3-8b --audit
python3 -m src.gemma_diagnostics experiments/E010-single-query/results/gemma-e4b --source "$a"
~~~

So sánh đầu ra JSON với **results/aggregate.json** của từng thí nghiệm, và đầu ra kiểm tra số ID được trả về của E006 với **results/completeness.json**. E005 in số trường hợp kiểm tra. Khi phân tích phát hiện nào quan trọng, mở thêm protocol và trace của đúng thí nghiệm đó. ZIP chứa snapshot nguồn. Kiểm tra thứ tự commit bằng Git nếu có quyền truy cập.

## Báo cáo phản biện mong muốn

Trả lời bằng tiếng Việt, giữ nguyên tên kỹ thuật và trích đoạn tiếng Anh cần thiết.

1. **Đóng góp thực sự** trong 2–4 câu theo cách reviewer hiểu bài.
2. **Quyết định** chọn một trong ba mức *đủ để đăng preprint phạm vi hẹp*, *sửa trước khi đăng*, hoặc *cần thêm bằng chứng thực nghiệm*. Nêu lý do chính và mức tự tin.
3. **Phát hiện theo mức độ** gồm nghiêm trọng, lớn và nhỏ. Với mỗi phát hiện ghi vị trí, bằng chứng đã xem, ảnh hưởng đến kết luận và thay đổi cần thiết.
4. **Ma trận tuyên bố và bằng chứng** cho 3–5 tuyên bố chính. Đánh dấu *được hỗ trợ*, *cần thu hẹp* hoặc *thiếu bằng chứng*, kèm phạm vi reviewer chấp nhận.
5. **Một việc có giá trị nhất trước khi đăng.** Nếu đề xuất thí nghiệm, nêu đối chứng, đơn vị so sánh, chỉ số và kết quả nào sẽ khiến reviewer đổi nhận định.
6. **Phạm vi kiểm chứng.** Liệt kê lệnh đã chạy, số liệu đã tự tính và các nguồn đã đọc. Ghi riêng phần chỉ dựa trên bản thảo hoặc tài liệu chưa tiếp cận được.
