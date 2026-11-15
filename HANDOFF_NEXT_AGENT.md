# Bàn giao cho agent tiếp theo: củng cố bài nghiên cứu về rare-case memory

Ngày bàn giao: **15/11/2026**.

## 0. Cập nhật sau phiên rà soát trước khi đăng (15/11/2026)

Phần này ghi trạng thái mới nhất. Các mục 1–13 bên dưới là bản bàn giao
gốc và được giữ nguyên để đối chiếu.

- **Việc A đã xong.** Bản thảo, PDF và ZIP mới nằm ở `artifacts/current/`.
  Chi tiết: [báo cáo rà soát](artifacts/review/publication-audit-2026-11-15/REVIEW_VI.md)
  và [claim audit](paper/claim-audit.md#november-15-publication-audit).
- **E014 đã chạy** (phân tích hậu nghiệm, offline): p sign-flip của E009
  là 0,50; bộ nhớ còn ví dụ key-detour đúng 80/87, đã mất đúng 9/39;
  42 quỹ đạo khớp bổ đề FIFO trong Lean. Script cũng kiểm 76 con số của
  bản thảo. [Kết quả](experiments/E014-publication-audit/analysis.md)
- **Lean đã mở rộng**: chuẩn hóa, giá trị trong [0,1], ngưỡng
  proposal-share, hai ví dụ số. 16 mệnh đề, không `sorry`.
- **Việc B đã xong.** [E015](experiments/E015-confirmatory/protocol.md)
  được khóa và commit trước mọi lượt gọi trên 30 seed mới (7101–7130),
  rồi chạy đủ 2.790 lượt gọi Qwen3 8B local trên Ollama 0.40.16.
  [Kết quả](experiments/E015-confirmatory/analysis.md) là **âm**:
  - Câu hỏi chính (retention): frozen 55/90, mixture 51/90 trên
    key-detour, +4,4 điểm, khoảng bootstrap −5,6 đến +13,3, sign-flip
    0,51. Không được xác nhận, dù mixture chỉ giữ ví dụ key-detour ở
    6/30 seed. Bộ nhớ rỗng đạt 53/90.
  - Adaptive so với balanced rare-only: −1,7 điểm (Holm 0,51).
  - Tương tác nhãn: −5,0 điểm (Holm 0,36). Hướng của E009 không lặp lại.
  - Mô tả: ví dụ lưu chỉ giúp khi nó chứa đúng đường tối ưu của truy
    vấn (29/32, so với 116/208 và 129/210). Unreachable 0/450.
  - 90 quỹ đạo mới khớp bổ đề FIFO (tổng 132).
- Bản thảo đã thu hẹp kết luận retention về holdout gốc và báo cáo kết
  quả âm ở abstract, Results, Discussion, Conclusion. Hai script kiểm
  76 + 44 con số.
- Bằng chứng của bản thảo cố định ở commit `7df0cbdbc499`. SHA trong
  mục 2 là của bản trước.
- Khuyến nghị: đăng Zenodo như audit preprint có thí nghiệm xác nhận
  với kết quả âm. Tác giả tự đăng. Tệp phát hành:
  `artifacts/current/rare-case-agent-memory-audit-confirmatory.pdf` và
  `...-audit-confirmatory-reproducibility.zip`.
- Giấy phép do tác giả chọn ngày 16/11/2026: MIT cho mã, CC BY 4.0 cho
  bài, dữ liệu và tài liệu ([LICENSE](LICENSE)). Chọn cùng giấy phép
  khi tạo bản ghi Zenodo.
- Việc còn mở: chạy lại bộ sinh gốc trên seed mới để tách ảnh hưởng của
  bộ sinh khỏi số vòng và định dạng readout; model thứ hai; quy tắc
  phân bổ có tính đến tỉ lệ admission.

## 1. Nhiệm vụ

Tiếp tục từ bản thảo hiện tại để làm rõ đóng góp, sửa những thiếu sót được chỉ ra trong lần rà soát cuối và thiết kế một thí nghiệm xác nhận có giá trị. Không bắt đầu lại dự án. Không tối ưu công việc để adaptive nhất thiết phải thắng.

Ưu tiên khoa học: kiểm tra liệu kết luận so sánh chính sách bộ nhớ còn tồn tại khi đồng thời cân bằng ngân sách rare, loại shortcut của bộ sinh đồ thị và đối sánh biểu diễn giữa các điều kiện.

Tài liệu này là bàn giao trạng thái và đề xuất công việc. Các thí nghiệm mới bên dưới **chưa chạy, chưa có kết quả, chưa có protocol được khóa**. Không diễn đạt đề xuất thành đóng góp đã đạt được.

## 2. Đúng dự án và đúng phiên bản

- Tên bài: **Auditing Rare-Case Coverage in LLM Agents with Iterative Example Memory**.
- Repo làm việc: `/Users/mac/Documents/ChatGPT/rare-case-agent-memory`.
- GitHub: https://github.com/minggu151623/rare-case-agent-memory
- Commit đã rà soát: `12c21371d838fdd27e360aade4a7b7f371d861e6`.
- SHA-256 của `paper/main.tex` ở lần rà soát: `be60685e2412820399a3ec933ff5c4226153be41d2dec4d6fe30aeaf66b5879f`.
- Thư mục `/Users/mac/Documents/ChatGPT/research_vibing` là dự án bài trước. Desktop có thể đang mở nhầm thư mục đó; không sửa bài trước.
- Khi bắt đầu, kiểm tra HEAD, working tree và `AGENTS.md`. Nếu repo đã có thay đổi mới, đọc chúng trước, không reset hay ghi đè công việc của người khác.

Bài nghiên cứu mô hình **giữ nguyên trọng số**, chỉ cập nhật bộ nhớ ví dụ trong prompt. Đây không phải nghiên cứu huấn luyện đệ quy trọng số hoặc tái lập trực tiếp model collapse.

## 3. Đọc theo thứ tự

Các đường dẫn tương đối sau tính từ repo hiện tại:

1. `AGENTS.md`, `research-state.yaml`, `findings.md`, `research-log.md`.
2. `paper/main.tex`, các bảng được `input`, `paper/claim-audit.md`.
3. `paper/README.md`, `formal/README.md`, `formal/protocol.md`.
4. Protocol và analysis của E002, E009, E011, E012, E013.
5. Báo cáo rà soát mới và log, theo mục 4.

Mã quan trọng: `src/planning.py` là oracle/scorer; `src/admission.py` và `src/admission_audit.py` quản lý/replay acquisition; `src/matched_labels.py` là E009; `src/rare_only.py` là E012; `src/diverse_paths.py` là E013.

## 4. Báo cáo rà soát và bằng chứng bàn giao

Báo cáo chi tiết:

[Báo cáo ngày 15/11/2026](artifacts/review/review-2026-11-15/REVIEW_VI.md)

Bundle kiểm tra:

[Gói log lần rà soát đầu](artifacts/review/rare-case-review-2026-11-15.zip)

Cùng thư mục báo cáo có `checks.json`, `independent_check.json`, `lean-checks.json`, `table-checks.json`, `manifest.json`, hai chương trình kiểm tra và stdout/stderr.

Các tệp review này được tạo cục bộ, **không nằm trong commit đã rà soát và chưa được push cùng lần rà soát**. Nếu làm trên máy khác, cần chuyển bundle hoặc tái kiểm tra từ repo; các số quan trọng được ghi lại bên dưới. Bản script gốc được lưu cùng log. Dùng [bản kiểm tra với đường dẫn tương đối](artifacts/review/reanalysis-2026-11-15/) để chạy lại từ bất kỳ bản clone nào có thư mục artifacts đã gom.

PDF có Lean đã được tạo ở phiên trước:

[PDF có Lean](artifacts/archive/rare-case-agent-memory-with-lean.pdf)

Đọc nguồn LaTeX làm chuẩn; nếu sửa nguồn, phải tạo và kiểm tra PDF mới, không giao lại PDF cũ.

Xem [phân tích sau khi gom dự án](artifacts/review/reanalysis-2026-11-15/ANALYSIS.md) để đọc kết quả chạy lại và ưu tiên nghiên cứu.

## 5. Trạng thái xác minh

Lần rà soát 15/11/2026 đã:

- Chạy 18 nhóm kiểm tra thành công, gồm 15 unit test trong bốn bộ test.
- Tái tạo 12 báo cáo JSON, khớp nội dung bản lưu.
- Replay 84 lượt gọi của E002, gồm prompt, memory, admission, eviction và điểm.
- Kiểm tra 3.150 cấu hình FIFO bằng phép tính hữu tỉ của E005.
- Viết một bộ chấm riêng dùng relaxation trên không gian trạng thái, đối chiếu 2.808 câu trả lời được yêu cầu trong 408 bản ghi của chín thí nghiệm; không tìm thấy bất đồng với scorer hiện tại.
- Chạy `lake build` rồi kiểm tra lại cả năm tệp Lean bằng `-DwarningAsError=true`. Bảy định lý xuất ra không có `sorryAx`; chỉ dùng `propext`, `Classical.choice`, `Quot.sound`.
- Xác nhận mã nguồn/cấu hình formal trong checkout có toolchain khớp từng byte với repo.
- Sinh lại hai bảng E012/E013, khớp từng byte.

Không suy ra 2.808 câu trả lời là 2.808 mẫu độc lập: nhiều truy vấn được lặp giữa điều kiện. Không có inference mới trong lần rà soát. Replay không tự xác nhận độc lập quá trình thu thập ban đầu. Lần này không biên dịch lại PDF hoặc dựng lại toàn bộ dependency Mathlib. Đây là review của Codex, chưa phải peer review độc lập và không có chứng nhận ARA Seal.

## 6. Kết quả phải giữ nguyên khi diễn giải

| Bằng chứng | Kết quả | Giới hạn |
| --- | --- | --- |
| E002 | Adaptive 18/18 detour, mixture 7/18; rare macro gap +22,2 điểm | Hai policy dùng lượng rare supplements khác nhau; holdout có shortcut |
| Frozen baseline E002 | 16/18 detour | Phần lớn điểm số gốc đã có khi không cập nhật memory |
| E012 | Adaptive 18/18, balanced rare-only 16/18; cả hai 0/18 unreachable | Rare macro gap +5,6 điểm chỉ từ seed 6206; sign-flip p=1 |
| E013 | Detour varied: adaptive 7/18, balanced 5/18, mixture 3/18 | Bộ nhớ được tạo trên generator cũ; hai rare-only arm cùng mất 11 câu đúng |
| Fixed-path diagnostic | Một đường cố định đúng 18/18 ở generator gốc, tốt nhất 2/18 ở varied set | Không chứng minh model thực sự dùng shortcut đó |
| E009 | Shared-minus-mixed policy-gap difference +19,4 điểm | Sáu seed; hai seed đảo dấu; comparator vẫn là mixture và generator vẫn là bản gốc |
| E010 | Gemma trả đủ câu khi hỏi từng câu riêng | Chỉ sáu detour, đọc memory của Qwen; không phải replication acquisition |
| Lean | Chứng minh FIFO full positive-capacity, công thức hữu hạn, zero-admission, giới hạn | Xác suất dùng i.i.d. với weights cố định; không chứng minh held-out accuracy hoặc tính mới |

Điểm mới của lần rà soát: E009 có các chênh lệch theo seed `[3, 6, -4, 2, -1, 1]`, đơn vị là số câu đúng trên sáu câu. Liệt kê đủ 64 cách đổi dấu cho **p hai phía = 0,500**. Phải ghi đây là phân tích hậu nghiệm theo giả định sign exchangeability. Không gọi nó là kiểm định được thiết kế ngẫu nhiên hóa bảo đảm; không suy ra không có hiệu ứng.

Khoảng leave-one-seed-out 3,3–36,7 điểm không phải confidence interval. Các follow-up dùng lại sáu seed cũ, không phải những replication độc lập.

## 7. Đánh giá mức sẵn sàng

- Có cơ sở công bố **exploratory audit preprint**, sau chỉnh sửa trình bày và định vị.
- Chưa có bằng chứng vững cho adaptive superiority trước balanced rare-only.
- Với full paper nhắm đóng góp thực nghiệm khái quát, nên bổ sung một thí nghiệm xác nhận. Không hứa tỷ lệ được nhận hay tự suy diễn venue.
- Đóng góp có thể bảo vệ: audit có kiểm soát về cách budget/generator/representation ảnh hưởng policy contrast; thiết kế matched-rendering; artifact kiểm chứng được với Lean.
- Không quảng bá là giải quyết model collapse, chứng minh self-improvement bền vững, phát hiện đầu tiên label sensitivity, hoặc định lý FIFO có tính mới lớn chỉ vì được formalize.

## 8. Việc A: chỉnh bản thảo bằng bằng chứng hiện có

1. Làm rõ E009 là exploratory/descriptive ngay trong Abstract và Results. Bổ sung phân tích p=0,500 với nhãn hậu nghiệm và giả định, hoặc trình bày rõ chưa có xác nhận thống kê; đồng bộ claim audit.
2. Nêu rõ E009/E012/E013 chưa kết hợp ba kiểm soát trong cùng một thiết kế. Không ghép các kết quả riêng thành bằng chứng đã loại hết confounders.
3. Related Work cần đọc và đối chiếu thêm các nguồn sau, xác minh lại trước khi đưa BibTeX vào bài:
   - https://arxiv.org/html/2505.16067v2 — đã có ground-truth/error-free memory comparison.
   - https://arxiv.org/abs/2511.10234v3 — đã có nghiên cứu graph representation invariance.
   - https://arxiv.org/html/2610.11188v1 — tách admission/presentation, có matched admission budget ở miền khác.
   - https://arxiv.org/abs/2603.04549 — adaptive memory admission trên LoCoMo.
4. Phân biệt admission vào persistent FIFO với selection của recalled information đưa vào working context. Không coi các bài trên là giống hệt nghiên cứu này chỉ vì trùng thuật ngữ.
5. Section 4 ghi rõ `K ≥ 1`, `u,v ≥ 0`, `u+v ≤ 1`; đoạn threshold ghi `0 < δ < 1`.
6. Chèn link repo/commit bất biến vào PDF, cập nhật ngày bản thảo khi thực sự phát hành bản mới. Cân nhắc trích dẫn Lean/Mathlib.
7. Tổ chức câu chuyện quanh các kết quả audit chính; có thể chuyển một số chi tiết chẩn đoán sang phụ lục. Không kéo dài bài chỉ để tăng số trang.

Nghiệm thu A: mọi con số truy ngược được tới log; bảng tái tạo được; citations có nguồn; bản PDF mới biên dịch thành công và được kiểm tra bố cục. Không thay đổi kết quả gốc để phù hợp narrative.

## 9. Việc B: thiết kế thí nghiệm xác nhận ưu tiên cao nhất

**Câu hỏi:** Khi cùng ngân sách rare và không còn một đường cố định giải hầu hết holdout, sự nhất quán nhãn giữa các ví dụ và truy vấn còn làm thay đổi kết quả so sánh chính sách bộ nhớ không?

Đây là đề xuất, cần agent hoàn thiện thành protocol. Có thể dùng E014 nếu ID đó còn trống; kiểm tra trước khi tạo.

### Thiết kế tối thiểu cần giải quyết

- Seed, acquisition graphs và holdout mới, tách khỏi E001–E013. Đa dạng đường tối ưu ngay từ acquisition, không chỉ thay holdout của memory cũ.
- So adaptive với balanced rare-only. Thêm frozen và empty làm mốc để biết updating có ích hơn không cập nhật hay không.
- Ghép cặp initial memory, task pools và ngân sách giữa policy. Quy định rõ số round, capacity, số tasks, giới hạn output/context; báo cả token và thời gian thực dùng.
- Giữ memory và graph cố định khi so representation. Giữ nguyên tập rendered forms của từng graph giữa shared/mixed conditions; đổi thứ tự chạy có kiểm soát.
- Dùng từng query riêng trong điều kiện chính hoặc một ablation được khóa để loại ảnh hưởng query-query trong batch. E009 cũ thay cả nhất quán trong memory, trong query batch và giữa hai phần; không tái tuyên bố đã tách cơ chế khi chưa làm được.
- Với single-query evaluation, định nghĩa lại phép đối sánh một cách tường minh: query được hiển thị dưới cùng các maps qua repetitions; memory graphs cũng giữ cùng marginal exposures. Kiểm tra bằng code rằng điều kiện này đúng.
- Lặp cả acquisition lẫn readout trên ít nhất hai model nếu nguồn lực cho phép. Đọc memory do Qwen tạo bằng model khác không đủ điều kiện này.
- Kiểm tra output schema/completeness trên development fixtures riêng trước khi khóa. Không sửa prompt sau khi nhìn kết quả chính rồi tiếp tục gộp số liệu.

### Thống kê và quy tắc thực hiện

- Chọn một primary interaction/contrast trước; tách secondary/exploratory outcomes.
- Dùng seed/trajectory làm đơn vị ghép cặp. Không coi các maps hay queries chung memory là quan sát độc lập.
- Chọn số seed theo độ chính xác mong muốn hoặc power cho mức hiệu ứng có ý nghĩa. Không mặc định một con số như 12 hoặc 24 chắc chắn đủ.
- Khóa cách tính uncertainty, xử lý missing answers, transport failures/retries, và quy tắc dừng. Nếu có nhiều kiểm định xác nhận, định nghĩa family và cách xử lý multiplicity.
- Không dừng hoặc mở rộng mẫu chỉ vì p-value vừa đạt/chưa đạt ngưỡng.
- Chạy kiểm tra CPU, solver độc lập, split isolation, constant-path baselines và matched exposures trước inference.
- Theo `AGENTS.md`, commit protocol đã hoàn chỉnh **trước khi sinh kết quả**. Commit protocol là bản ghi thời điểm thiết kế, không tự tương đương preregistration bên thứ ba.
- Lưu raw request/response, snapshot model, runtime, decoding, seeds, token usage và lỗi. Không đưa holdout hoặc output của holdout vào memory.
- Nếu hiệu ứng biến mất, báo cáo đúng kết quả âm. Nếu còn, giới hạn claim theo generator/model/conditions đã kiểm tra.

Trước khi chạy, báo kế hoạch số calls và ước lượng tài nguyên. Ưu tiên inference local và model có sẵn. Không tự mua API/compute hoặc tải model lớn khi chưa rõ dung lượng và phạm vi được người dùng giao.

Nghiệm thu B: protocol được khóa; dữ liệu không rò rỉ; có replay offline và raw traces; matched exposures được kiểm tra; primary contrast có bất định theo seed; negative outcomes và deviations được lưu; claim audit phản ánh kết quả thực.

## 10. Các hướng khác, chỉ làm khi có lý do

- So FIFO với policy bảo vệ ví dụ cuối/quota theo family, đo cả coverage, độ cũ, accuracy và distribution shift. Việc quota giữ được quota là hệ quả thiết kế, chưa phải đóng góp mới. Giá trị nằm ở trade-off và tác động tới readout.
- Mở rộng lý thuyết sang admission phụ thuộc lịch sử chỉ khi có giả định và câu hỏi cụ thể. Không dùng pass rate trung bình để áp công thức i.i.d. cho adaptive. Một cận đơn giản hoặc nhiều dòng Lean hơn chưa đảm bảo tăng tính mới.
- Không triển khai mọi hướng cùng lúc. Việc B là ưu tiên trước hai hướng này.

## 11. Cách chạy kiểm chứng hiện có

Chạy từ repo, theo hướng dẫn đầy đủ trong `paper/README.md`:

```sh
python3 -m unittest discover -s experiments/E000-oracle-smoke
python3 -m unittest discover -s experiments/E001-memory-coverage
python3 -m unittest discover -s experiments/E002-admission
python3 -m unittest discover -s experiments/E013-diverse-paths
python3 experiments/E005-fifo-null/verify.py
python3 -m experiments.E011-manuscript-audit.check

python3 -m src.admission_audit experiments/E002-admission/results/qwen3-8b
python3 -m src.matched_labels experiments/E002-admission/results/qwen3-8b experiments/E009-matched-labels/results/qwen3-8b --audit
python3 -m src.rare_only experiments/E012-rare-only/results/qwen3-8b --audit
python3 -m src.diverse_paths experiments/E002-admission/results/qwen3-8b experiments/E012-rare-only/results/qwen3-8b experiments/E013-diverse-paths/results/qwen3-8b --audit
```

Các lệnh `--audit` tính lại từ dữ liệu lưu, không chạy LLM mới. So nội dung JSON với aggregates đã lưu; exit code 0 riêng lẻ chưa thay cho so sánh này.

Lean: đọc `formal/README.md`. Toolchain là Lean 4.26.0, Mathlib khóa trong manifest. Các lệnh chính, chạy trong `formal/` sau khi dependency sẵn sàng:

```sh
lake build
lake env lean -DwarningAsError=true FifoCoverage.lean
```

Máy hiện tại từng dùng checkout `/tmp/rare-case-lean` và toolchain `/tmp/rare-lean-tools/lean-4.26.0-darwin_aarch64/bin`. Đây là cache tạm có thể mất; không coi là nguồn chuẩn và không sửa chỉ bản `/tmp` rồi quên chuyển thay đổi về repo. Nếu dùng cache, xác nhận source khớp commit đang kiểm tra.

## 12. Skill/workflow và giới hạn quyền

Repo đã áp dụng Orchestra Research AI-research-SKILLs tại revision `773a52944ba4747a18bd4ae9ade53fff041adcbc`:

- `autoresearch`: tổ chức trạng thái, protocol, thí nghiệm và nhật ký.
- `creative-thinking-for-research`: dùng ở giai đoạn hình thành bài; không phải bằng chứng rằng lần review cuối đã chạy lại toàn bộ skill này.
- `ml-paper-writing`: hướng dẫn viết/rà soát claim, narrative và citations, được tham khảo trong lần rà soát cuối. Bản cache local: `/tmp/rare-case-ml-paper-writing.md`; nguồn pinned được dẫn trong `AGENTS.md`.

Đọc hướng dẫn áp dụng trước khi tiếp tục. Không tuyên bố đã thực hiện ARA Level 2: dự án không được xác nhận đạt prerequisite cho quy trình đó. User yêu cầu bàn giao cho agent khác không đồng nghĩa phải tự spawn nhiều agent; làm theo phạm vi và khả năng của phiên tiếp theo.

Các yêu cầu của tác giả:

- Người dùng tự đăng Zenodo. Không upload, publish, submit thay họ.
- Khi commit, cả author và committer phải là **TRAN VU BAO MINH <213340851+minggu151623@users.noreply.github.com>**. Kiểm tra commit thực tế; không chỉ dựa vào `git config`. Không thêm Codex/Claude co-author.
- Không rewrite lịch sử hoặc force-push chỉ để thêm công việc mới. Theo dõi phạm vi push được người dùng giao trong phiên thực hiện.
- Giữ raw traces, protocol và câu lệnh replay để agent/người khác kiểm tra.
- Phân biệt đề xuất, kết quả đã chạy, kiểm tra offline và replication thực sự. Không công bố “đã kiểm chứng độc lập” chỉ vì agent tạo bài cũng tự kiểm tra lại bài.

## 13. Những gì agent tiếp theo cần bàn giao

1. Bản thảo và PDF cập nhật; danh sách claim đã sửa cùng lý do.
2. Nếu làm thí nghiệm mới: protocol, implementation, raw traces, aggregate, analysis và lệnh replay.
3. `research-state.yaml`, `findings.md`, `research-log.md`, `paper/claim-audit.md` được đồng bộ.
4. Báo cáo cái gì chạy thành công, cái gì còn chưa kiểm tra, kết quả âm và giới hạn.
5. Khuyến nghị công bố dựa trên bằng chứng mới, không dựa vào số trang hay số thí nghiệm.

Bước đầu tiên hợp lý: xác nhận repo/commit, đọc report, tái tính E009 p=0,500, hoàn tất Việc A và viết protocol Việc B. Chỉ chạy thí nghiệm sau khi thiết kế, nguồn lực và tiêu chí phân tích đã cụ thể.
