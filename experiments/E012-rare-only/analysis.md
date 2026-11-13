# E012 · Matched rare-only results

All 36 Qwen3 calls passed replay. No outer JSON format failures occurred.
The adaptive arm solved 18/18 key detours, compared with 16/18 for the
balanced rare-only random control. Both arms solved 18/18 ungated cases
and 0/18 unreachable cases. The rare macro-accuracy difference is
+5.6 percentage points (18/36 versus 16/36). The six seed gaps, in correct
answers out of six, are [0, 0, 0, 0, 0, 2]. The two-sided exact sign-flip
sensitivity value is 1.0. The gain came entirely from seed 6206.
All 18 adaptive prompts and raw responses match the corresponding
historical E002 arm byte for byte.

Both arms attempted 12 rare supplements. The adaptive arm attempted
nine key detours and three unreachable tasks, admitting eight and zero,
respectively. The control attempted six of each, admitting six key
detours and zero unreachable tasks. Across final memories the adaptive
arm retained ten key detours and one unreachable example, compared with
eight and three for the control. Zero new unreachable admissions make
those retained examples survivors from initial memory.

The original E002 targeted-minus-mixture rare macro gap was 22.2 points.
The smaller E012 gap compares adaptation with a policy that spends the
same number of supplements on rare examples. The paired result provides
limited evidence for an advantage over this control. Five ties do not
establish equivalence, and the historical comparison does not decompose
the total gap into additive mechanisms. The holdout still uses the
original generator, which permits a fixed-path shortcut.
