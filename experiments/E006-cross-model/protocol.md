# E006 · Cross-model readout of fixed memories

Repeat the E004 five-cell evaluation with Phi-3.5-mini-instruct
(Ollama phi3.5:3.8b, Q4_0 manifest digest
61819fb370a3c1a9be6694869331e5f85f867a079e9271d66cb223acb81d04ba).
Use all six seeds, both policies' Qwen-generated final memories, and
the same nine query instances per seed. All five label cells are
new calls for Phi, giving 60 calls. Reuse the exact E004 prompt body,
seed, temperature, context and generation cap. Omit the Qwen-specific
thinking option on Phi. Treat missing or invalid answers as zero
under the same exact verifier. Log JSON validity and token counts.
Reconstruct every prompt and score from the logs.

The primary comparison is whether the direction and location of
key-detour sensitivity agree across models on the same prompts.
Report the baseline and all five cells even if a model is near
the floor. If an arm starts near the floor, a small loss under
renaming is uninformative about invariance. Report all families,
six seed-level results, and the same factorial contrasts as E004.
The design changes the model that reads fixed memories. It cannot
show that Phi acquires memories in the same way as Qwen.
