# E006 amendment · Cached Gemma instead of Phi

Phi was chosen before inference. Its model transfer failed with a
disk-space error, and no Phi experiment call was made. Use the existing
Gemma 4 E4B MLX 4-bit installation instead, served by LM Studio over
loopback. This avoids another download. The cached package is
deadbydawn101/gemma-4-E4B-mlx-4bit. Pin the following SHA-256 hashes:

- model.safetensors: 2bce06d8373d9edec745c66bafd8d3965eb04a2efa2b229bca9078241ea05e6b
- config.json: 18521c2237729a659a3b821eeb706f088e46518d8698f8e357df7bf7300e7041
- tokenizer.json: cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f
- chat_template.jinja: 55572b8d3c8342044e25874c73fe5234b661fa0a57a57f6ef75b58e03d7d959a

The five cells, six seeds, two policies, and 60-call denominator
remain unchanged. Use the exact Qwen system and user prompt bodies,
temperature zero, seed plus two, and a 384-token cap. Load Gemma with
a 4096-token context. LM Studio uses an object-only JSON grammar
through its OpenAI-compatible endpoint, rather than Ollama's JSON
mode. Record any separately returned reasoning as presence or absence
and preserve raw answer strings. Keep LM Studio's chat-template
behavior fixed across cells. Model, quantization, and inference backend
differ from Qwen, so the comparison tests portability across these
two configured systems. Treat baseline floor effects as inconclusive.
