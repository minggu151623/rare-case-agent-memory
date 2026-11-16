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
| 76 + 50 con số trong bản thảo đối chiếu với dữ liệu lưu | Qua, hai script dừng nếu lệch |
| 4 bảng sinh từ script | Khớp từng byte |
| PDF | 23 trang, không cảnh báo LaTeX, không tham chiếu hỏng |
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

## Rà soát bản cuối theo skill ml-paper-writing

Áp dụng bản skill đã ghim (Orchestra Research, commit `773a5294`) lên
bản thảo sau E015. Skill yêu cầu tác giả xác nhận câu đóng góp; tác giả
đã ủy quyền nên quyết định được ghi lại ở đây.

**Câu đóng góp (một câu).** Một audit theo từng family cho thấy khoảng
cách giữa hai chính sách bộ nhớ là do giữ lại một đáp án chép được, và
một thí nghiệm xác nhận khóa trước cho thấy coverage đi đúng mô hình
FIFO đã kiểm bằng Lean nhưng độ chính xác không đi theo coverage.

| Hạng mục của skill | Trạng thái | Việc đã làm ở bản này |
| --- | --- | --- |
| Narrative: What / Why / So what rõ ở cuối Introduction | Đạt | Thêm bullet đóng góp về thí nghiệm xác nhận; đoạn cuối Introduction tách phần exploratory và confirmatory |
| Abstract: nêu kết quả ngay, có con số nổi bật | Đạt sau sửa | Viết lại, đưa kết luận âm lên câu thứ ba, còn khoảng 270 từ |
| "Figure 1": kết quả chính ở trang đầu | Đạt sau sửa | Bảng E015 chuyển lên cạnh Bảng 1 trong Introduction |
| 2–4 bullet đóng góp | Đạt | 4 bullet |
| Mỗi thí nghiệm nêu claim được kiểm | Đạt | Đoạn thiết kế E015 nêu contrast chính, tiêu chí quyết định, hai contrast phụ |
| Error bar kèm phương pháp, số lần chạy, kiểm định | Đạt sau sửa | Ghi rõ bootstrap percentile 10.000 lần theo seed, sign-flip chính xác, Holm cho hai contrast phụ |
| Hạ tầng tính toán, thời gian | Đạt sau sửa | Ghi 2.790 lượt gọi, 2,8 giờ, Apple M1 Pro, Ollama 0.40.16 |
| Seed và cách đặt | Đạt | Seed 7101–7130, hai seed giao diện 7001–7002 |
| Related work theo chủ đề, không bịa trích dẫn | Đạt | Bản này không thêm trích dẫn; 4 trích dẫn thêm trước đó lấy từ arXiv/doi.org |
| Limitations | Đạt | Thêm giới hạn của E015: một model, null chỉ trong khoảng tin cậy, đổi ba yếu tố cùng lúc |
| Giả định trước định lý | Đạt | Section 4 ghi `K ≥ 1`, `u, v ≥ 0`, `u + v ≤ 1`; 16 mệnh đề Lean |
| Thuật ngữ nhất quán | Đạt có ghi chú | random/targeted và reference-mixture/adaptive được giải thích một lần ở Section 5 |
| Bảng booktabs, cột số căn phải | Đạt | Bảng sinh từ script, khớp từng byte |
| Từ đệm, hedging | Đạt | Không còn "very", "quite", "essentially"... trong nguồn |
| Checklist kiểu NeurIPS: claim khớp bằng chứng, tái lập, mã mở | Đạt | 120 con số được script đối chiếu; replay offline khớp từng byte |
| Checklist: giấy phép tài sản | Đạt sau sửa | Tác giả chọn MIT + CC BY 4.0; bản thảo ghi giấy phép của Qwen3, Lean, Mathlib |

**Chấm theo bốn tiêu chí reviewer của skill.**

- *Quality:* vững trong phạm vi. Claim khớp bằng chứng, có đối chứng
  frozen/empty, có thí nghiệm khóa trước, kết quả âm được báo cáo thẳng.
- *Clarity:* tốt; tái lập được từ trace mà không cần chạy model.
- *Significance:* hạn chế. Một model 8B, đồ thị tổng hợp sáu đỉnh, bộ nhớ
  sáu ô. Kết quả chính là null.
- *Originality:* vừa phải. Từng đối chứng đã có ở công trình trước; cái
  mới là audit một khoảng cách chính sách kèm mô hình FIFO kiểm bằng Lean
  và phép thử xác nhận.

Ước lượng trên thang NeurIPS 6 điểm: khoảng 3 (borderline reject) ở hội
nghị chính, phù hợp hơn với workshop về agent memory/evaluation hoặc
preprint. Với Zenodo, không có rào cản nào còn lại về nội dung.

## Quyết định đã chốt thay tác giả (theo ủy quyền)

- **Câu AI-use: giữ nguyên.** Câu ghi OpenAI Codex và Anthropic Claude
  hỗ trợ thiết kế, cài đặt, phân tích, chứng minh, rà soát và viết. Đây
  là mô tả đúng sự thật về cách bài được làm; bỏ hay làm nhẹ đi sẽ sai.
- **Ngày bản thảo: 16/11/2026**, ngày chốt bản này. E015 chạy ngày 15/11.
- **Tên tệp phát hành: đổi** thành
  `rare-case-agent-memory-audit-confirmatory.pdf` và
  `rare-case-agent-memory-audit-confirmatory-reproducibility.zip`, vì
  bài không còn thuần exploratory. Bản trước E015 nằm ở `artifacts/archive/`.
- **Tiêu đề bài: giữ.** "Auditing Rare-Case Coverage..." vẫn đúng với
  nội dung.

## Checklist 16 mục và checklist chung của skill

Lấy nguyên văn từ `references/checklists.md` và
`references/reviewer-guidelines.md` của skill đã ghim, rồi điền cho bản
thảo này.

| # | Mục | Trả lời | Căn cứ |
| --- | --- | --- | --- |
| 1 | Claim ở abstract/intro khớp kết quả | Có | 120 con số được hai script đối chiếu; abstract nêu kết quả âm |
| 2 | Có mục Limitations | Có | Section 8, gồm giới hạn của E015 |
| 3 | Giả định và chứng minh đầy đủ | Có | Mệnh đề 1 có chứng minh trong bài; 16 mệnh đề Lean, không `sorry` |
| 4 | Tuyên bố tái lập | Có | Mục Reproducibility, link repo, commit bằng chứng |
| 5 | Lệnh chạy, môi trường, dữ liệu | Có sau sửa | Lệnh trong README; bản thảo ghi Python 3.10+, chỉ thư viện chuẩn |
| 6 | Chi tiết thí nghiệm | Có | Seed, digest model, nhiệt độ 0, context 4096, 384 token; không huấn luyện nên không có split/hyperparameter search |
| 7 | Ý nghĩa thống kê | Có | Khoảng bootstrap 10.000 lần theo seed, sign-flip chính xác, Holm; số seed ghi rõ |
| 8 | Tài nguyên tính toán | Có | Apple M1 Pro, 2.790 lượt gọi, 2,8 giờ cho E015 |
| 9 | Quy tắc đạo đức | Có | Không có dữ liệu người, không có sai lệch |
| 10 | Broader impacts | Có sau sửa | Thêm đoạn Broader impact |
| 11 | Safeguards | Không áp dụng | Không phát hành model hay dữ liệu thu thập |
| 12 | Giấy phép tài sản đã dùng | Có sau sửa | Qwen3, Lean 4, Mathlib: Apache 2.0 (đọc từ bản cài local); Gemma theo điều khoản của nhà phát hành |
| 13 | Tài liệu cho tài sản mới | Có sau sửa | LICENSE: MIT cho mã, CC BY 4.0 cho bài và dữ liệu, do tác giả chọn |
| 14 | Human subjects | Không áp dụng | |
| 15 | IRB | Không áp dụng | |
| 16 | Khai báo LLM | Có | LLM là đối tượng nghiên cứu; câu AI-use ghi cả việc hỗ trợ viết và phân tích |

Checklist chung: abstract khoảng 270 từ (trong giới hạn 250–300); mọi
bảng, hình có caption tự đủ; PDF biên dịch không lỗi, không tham chiếu
hỏng; trích dẫn đều resolve. Các mục về template hội nghị, giới hạn
trang và ẩn danh không áp dụng cho preprint Zenodo.

**Mô phỏng reviewer theo cấu trúc của skill.**

- *Tóm tắt:* bài audit một khoảng cách giữa hai chính sách cập nhật bộ
  nhớ, rồi kiểm định cách đọc của chính nó bằng một thí nghiệm khóa trước.
- *Điểm mạnh:* đối chứng frozen/empty/matched-budget; protocol commit
  trước kết quả; kết quả âm báo cáo thẳng; mô hình FIFO kiểm bằng Lean và
  khớp 132 quỹ đạo; replay offline từng byte.
- *Điểm yếu:* một model nhỏ, miền tổng hợp; E015 đổi ba yếu tố cùng lúc;
  khoảng tin cậy còn rộng (tới +13 điểm); phân tích theo đường đi là quan
  sát; family unreachable chạm sàn nên không phân biệt được chính sách.
- *Câu hỏi reviewer sẽ hỏi:* khoảng cách E002 có lặp lại trên seed mới
  với bộ sinh gốc không; kết quả có giữ với model biết trả lời
  "unreachable" không.
- *Khuyến nghị:* borderline reject (3/6) ở hội nghị chính vì
  significance; chấp nhận được ở workshop; đăng preprint được.

## Việc của tác giả

- Tác giả tự tạo bản ghi Zenodo, tải PDF và ZIP trong
  `artifacts/current/`, và chọn giấy phép CC BY 4.0 trên Zenodo.

## Phản biện độc lập (16/11/2026)

Một agent khác, không có ngữ cảnh của phiên rà soát và chỉ được đọc,
đã phản biện bản thảo theo `reviewer-guidelines.md` và `checklists.md`
của skill ml-paper-writing. Nguyên văn:
[INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md). Đây vẫn là phản biện bằng
AI, chưa phải phản biện của con người.

Kết quả của reviewer: 24 con số được tính lại từ dữ liệu, 23 khớp, 1
lệch ("eight" phải là "seven"); phân tích E015 khớp protocol đã khóa,
không có sai lệch chưa khai báo; `lake build` qua, không `sorry`; điểm
Quality 3/4, Clarity 2/4, Significance 2/4, Originality 2/4; tổng 3/6
(borderline reject) cho hội nghị chính; **Zenodo: được, sau khi sửa
bốn điểm bắt buộc.**

| Điểm của reviewer | Loại | Xử lý |
| --- | --- | --- |
| Cách giải thích "reusable answer" viết chắc hơn mức mô tả cho phép | Bắt buộc | Đổi tiêu đề đoạn Discussion, gọi là giả thuyết, bỏ "helped" ở abstract, làm mềm Conclusion |
| "Eight" giá trị mô tả, thực tế là bảy | Bắt buộc | Sửa trong bản thảo và `analysis.md`; thêm vào script kiểm |
| FIFO conformance bị trình bày như phát hiện thực nghiệm | Bắt buộc | Ghi rõ đây là kiểm tra cài đặt; bỏ khỏi "main result"; dùng "audited" |
| Family unreachable và Q2 chạm sàn | Bắt buộc | Ghi ở abstract và tại Q2 (−3,3 điểm key-detour) |
| Đối chứng cùng truy vấn cho path split | Tùy chọn | Thêm: bộ nhớ rỗng đạt 20/32 trên cùng truy vấn (được 11, mất 2); nhóm còn lại 117/208 |
| Độ lệch chuẩn của contrast chính | Tùy chọn | Thêm 0,82 và effect 0,16 |
| Hai nghĩa của "42" | Tùy chọn | Tách rõ |
| Frozen − empty cũng null | Tùy chọn | Thêm vào Discussion |
| Trích commit | Tùy chọn | Ghi rõ commit cố định trace và aggregate |
| Thêm một hình kết quả | Tùy chọn | Đã thêm Hình 1 (coverage so với độ chính xác, E002 và E015), sinh từ dữ liệu lưu bằng `paper/coverage_figure.py` |
| Chuyển E003–E010 xuống phụ lục | Tùy chọn | Đã chuyển thiết kế và kết quả của E003, E004, E006, E007, E008, E010 sang Phụ lục B; thân bài giữ một đoạn tóm tắt |
| Mở rộng related work | Tùy chọn | Thêm 5 trích dẫn (Reflexion, ExpeL, Voyager, Liu et al. 2021, Min et al. 2022); BibTeX lấy từ arXiv, đã đọc abstract |
| Bảng 2 nằm ở Introduction | Nhỏ | Đưa về mục Results; Introduction dùng Hình 1 |
| Lỗi nối câu giữa dòng trong nguồn | Nhỏ | Đã ngắt lại các dòng dài |

Các câu hỏi reviewer nêu mà dữ liệu hiện có không trả lời được: bộ sinh
gốc trên seed mới với readout một truy vấn; công suất của sign-flip với
13/30 seed hòa. Về câu hỏi 3: tương tác nhãn được hạ xuống thứ cấp khi
khóa protocol, trước khi so sánh bất kỳ bộ nhớ nào trên seed phát triển
(protocol ghi chỉ xem giao diện).

## Phản biện độc lập, vòng hai (16/11/2026)

Cùng reviewer chấm lại bản đã sửa:
[INDEPENDENT_REVIEW_ROUND2.md](INDEPENDENT_REVIEW_ROUND2.md). Kết luận:
ba script kiểm khớp từng byte; 20 giá trị của Hình 1 khớp dữ liệu; việc
chuyển sang phụ lục không làm mất kết quả nào; Clarity tăng từ 2/4 lên
3/4; tổng vẫn 3/6 vì phạm vi nghiên cứu không đổi; **Zenodo: sẵn sàng
sau hai câu sửa.**

| Điểm vòng hai | Loại | Xử lý |
| --- | --- | --- |
| Bullet đóng góp còn viết "helped" theo nghĩa nhân quả | Bắt buộc | Đổi thành "Descriptively, accuracy was higher when…" |
| Mô phỏng công suất giả định câu trả lời độc lập, trái với dữ liệu | Bắt buộc | Ghi rõ giả định cho độ lệch chuẩn 1,2 so với 0,82 quan sát, nên là ước lượng thận trọng; thêm mô phỏng thứ hai có tương quan theo truy vấn (87% ở 15 điểm, 44% ở 10 điểm) và đối chiếu với câu về cỡ mẫu |
| "therefore depends" quá mạnh | Khuyến nghị | Đổi thành "consistent with" |
| Không nêu tên hai nhánh ở tóm tắt E008; thiếu kết quả fresh-motif | Khuyến nghị | Đã thêm |
| "only" và thiếu "post hoc" ở Conclusion | Khuyến nghị | Đã sửa |
| Commit về sau có thêm phân tích dẫn xuất | Khuyến nghị | Đã ghi |
| Abstract dài, chưa nêu frozen − empty | Khuyến nghị | Viết lại, khoảng 255 từ (trước là 287), có nêu |
| Hình 1 thiếu mẫu số | Khuyến nghị | Thêm vào caption |
| Trích bản đã xuất bản của 5 tài liệu mới | Khuyến nghị | Không làm: bản ghi arXiv là nguồn gốc đã kiểm; thông tin hội nghị chưa lấy được từ bản ghi chính thức nên không ghi theo trí nhớ |
| Chữ "Agents" trong tiêu đề | Khuyến nghị | Giữ: hệ thống tự giải bài, tự kiểm và tự cập nhật bộ nhớ qua nhiều vòng; giới hạn một model, prompt không trạng thái đã ghi ở Limitations |

Sau các sửa này không còn điểm bắt buộc nào của reviewer để ngỏ.

## Phản biện độc lập, vòng ba (16/11/2026): kết luận cuối

[INDEPENDENT_REVIEW_ROUND3.md](INDEPENDENT_REVIEW_ROUND3.md). Reviewer
chấm bản ở commit `b42ede3`: ba script kiểm khớp từng byte, mọi con số
trong abstract khớp dữ liệu, hai điểm bắt buộc của vòng hai đã đóng,
không tìm thấy overclaim hay lỗi số nào cần sửa.

**Kết luận về Zenodo: READY — no required fixes.**

Điểm: Quality 3/4, Clarity 3/4, Significance 2/4, Originality 2/4, tổng
3/6 (borderline reject) cho hội nghị chính. Điểm tổng phản ánh phạm vi
nghiên cứu, không phải lỗi.

Sau báo cáo này chỉ sửa một câu ở Limitations theo đúng ghi chú không
bắt buộc của reviewer: thêm "at zero gap" và ghi rằng công suất phụ
thuộc dạng tương quan giả định.

Điểm yếu còn lại, không chặn việc đăng và không sửa được bằng chỉnh
văn bản: phạm vi hẹp (một model 8B, đồ thị tổng hợp); E015 đổi ba yếu
tố cùng lúc và bộ nhớ đóng băng gần như không hơn bộ nhớ rỗng; giả
thuyết "chép lại đường đi" dựa trên 32 câu quan sát; family unreachable
chạm sàn; hai cách gọi tên chính sách và các mã E còn trong bài; thời
điểm khóa protocol dựa vào commit, không phải đăng ký bên thứ ba.

## Thí nghiệm với model thứ hai, E016 (16/11/2026)

Thêm sau vòng phản biện thứ ba để xử lý giới hạn "chỉ một model" mà cả
ba vòng đều nêu. [Protocol](../../../experiments/E016-second-model/protocol.md)
khóa và commit trước khi chạy; [kết quả](../../../experiments/E016-second-model/analysis.md).
Gemma 4 E4B tự tạo và tự đọc bộ nhớ trên đúng 30 seed của E015, 2.430
lượt gọi, 1,15 giờ, không sai lệch nào so với protocol.

| Câu hỏi | Gemma 4 E4B | Qwen3 8B (E015) |
| --- | --- | --- |
| Chính: frozen − mixture, key-detour | 47/90 so với 55/90; −8,9 điểm; sign-flip 0,24. Không xác nhận | 55/90 so với 51/90; +4,4 điểm; 0,51. Không xác nhận |
| Phụ: adaptive − balanced, rare | +1,7 điểm; 0,38. Không xác lập | −1,7 điểm; 0,51. Không xác lập |
| Trả lời "unreachable" cho bài được hỏi | 0 lần trên 660 bài | 0 lần |

Hai model đồng ý ở kết luận chính (không xác nhận retention, không có
lợi thế adaptive) và ngược dấu ở thứ tự các chính sách, đúng như kỳ
vọng nếu các chính sách không khác nhau về độ chính xác trên các bài
này. Mọi so sánh với bộ nhớ rỗng của Gemma phụ thuộc quy tắc chấm đã
chốt trong protocol (48/90 theo quy tắc đó, 4/90 theo quy tắc chặt).

Phần này được đưa vào bản thảo sau bản mà reviewer vòng ba đã chấm, nên
cần một vòng chấm riêng (xem mục tiếp theo).

## Phản biện độc lập, vòng bốn: riêng cho E016 (16/11/2026)

[INDEPENDENT_REVIEW_ROUND4.md](INDEPENDENT_REVIEW_ROUND4.md). Reviewer
mới, chạy trên model khác với ba vòng trước, chấm bản ở commit
`87937d4`. Nó tự viết bộ kiểm đường đi và quy tắc chấm riêng rồi tính
lại từ trace thô: mọi con số của E016 khớp; protocol được commit trước
kết quả; mã phân tích không đổi sau khi khóa. Điểm vẫn 3/6 cho hội nghị
chính. **Zenodo: READY AFTER FIXES, ba điểm bắt buộc.**

| Điểm vòng bốn | Loại | Xử lý |
| --- | --- | --- |
| Bài viết "quy tắc chấm chỉ ảnh hưởng bộ nhớ rỗng" và "hai contrast giống hệt dưới cả hai quy tắc" là sai: quy tắc còn chấm 3 lượt giải (một bài ungated ở vòng 1 của seed 7125, được nhận vào bộ nhớ ở cả ba nhánh) và 2 câu ungated của bộ nhớ đóng băng | Bắt buộc | Viết lại đúng sự thật trong bài và `analysis.md`; thêm `strict_rule.py`; **chạy lại seed 7125 với quy tắc chặt ở cả acquisition lẫn readout (81 lượt gọi mới)**: hiệu chính vẫn +2, hiệu phụ vẫn 0, nên hai contrast không đổi; script kiểm thêm 3 con số |
| Commit cố định trace đã cũ, chưa gồm E016 | Bắt buộc | Ghi hai commit: `7df0cbdbc499` cho E001–E015, `9c26ca535178` cho E016 |
| Câu Limitations về "thí nghiệm Gemma" mâu thuẫn với E016 | Bắt buộc | Đổi thành "các thí nghiệm đọc E006 và E010" |
| Hai chỗ còn viết như chỉ có một model | Không bắt buộc | Đã sửa |
| Một câu nghiêng về đọc hai null ngược dấu là "tương đương" | Không bắt buộc | Thay bằng câu nói rõ điều đó không chứng minh tương đương |
| Abstract không nói path split là của Qwen3 | Không bắt buộc | Đã thêm |
| Phụ lục thiếu: đã đọc bốn câu trả lời và đã chạy report trên seed thử | Không bắt buộc | Đã thêm |
| Thiếu runtime và quantization của E016 trong thân bài | Không bắt buộc | Đã thêm |
| Trace không có dấu thời gian thực; hai model nhỏ; unreachable chạm sàn | Không sửa được | Đã ghi trong Limitations |

Sau các sửa này không còn điểm bắt buộc nào để ngỏ. Bản sau khi sửa
chưa được chấm thêm một vòng nữa.
