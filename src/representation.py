"""E004 factorial attribution of graph-label sensitivity."""

import argparse
import hashlib
import json
from pathlib import Path
from random import Random

from src.admission import study_pools
from src.admission_audit import read_calls
from src.pilot import Backend
from src.planning import is_correct
from src.transfer import NODES, flatten, parse_answers, rename, rename_with_labels, score

ARMS = ("random_model", "targeted_model")
CELLS = ("original", "memory_only", "query_only", "independent_both", "shared_map")
FRESH = ("memory_only", "query_only", "shared_map")


GEMMA_HASHES = {
    "model.safetensors": "2bce06d8373d9edec745c66bafd8d3965eb04a2efa2b229bca9078241ea05e6b",
    "config.json": "18521c2237729a659a3b821eeb706f088e46518d8698f8e357df7bf7300e7041",
    "tokenizer.json": "cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f",
    "chat_template.jinja": "55572b8d3c8342044e25874c73fe5234b661fa0a57a57f6ef75b58e03d7d959a",
}


def verify_gemma_files(directory):
    for name, expected in GEMMA_HASHES.items():
        with (directory / name).open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        if digest != expected:
            raise ValueError(f"Unexpected Gemma file hash: {name}")


class GemmaBackend(Backend):
    model = "rare-case-gemma-e4b"
    thinking_options = {}

    def connect(self):
        ids = {row["id"] for row in self.request("/v1/models")["data"]}
        if self.model not in ids:
            raise ValueError(f"Missing local LM Studio model {self.model}")
        return "LM Studio"

    def complete(self, payload):
        options = payload["options"]
        result = self.request("/v1/chat/completions", {
            "model": self.model,
            "messages": payload["messages"],
            "stream": False,
            "temperature": options["temperature"],
            "seed": options["seed"],
            "max_tokens": options["num_predict"],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "json_object", "schema": {"type": "object"}},
            },
        })
        choice = result["choices"][0]
        message = choice["message"]
        usage = result["usage"]
        return {
            "message": {"content": message.get("content") or ""},
            "prompt_eval_count": usage["prompt_tokens"],
            "eval_count": usage["completion_tokens"],
            "done_reason": choice["finish_reason"],
            "reasoning_present": bool(message.get("reasoning_content")),
        }


def shared_labels(seed):
    rng = Random(seed + 410000)
    while True:
        permuted = rng.sample(list(NODES), len(NODES))
        if all(a != b for a, b in zip(NODES, permuted)):
            return dict(zip(NODES, permuted))


def rename_memory(memory, transform):
    renamed = []
    for case, answer in memory:
        new_case, labels = transform(case)
        mapped = {"path": [labels[node] for node in answer["path"]]} if "path" in answer else answer
        if not is_correct(new_case.task, mapped):
            raise ValueError(f"Renaming changed solution semantics for {case.id}")
        renamed.append((new_case, mapped))
    return renamed


def prompts(seed, pools, original_rows):
    original = pools[-1]
    source_cases = {case.id: case for case in flatten(pools)}
    label_map = shared_labels(seed)
    independently_renamed = [rename(case, seed)[0] for case in original]
    shared_queries = [rename_with_labels(case, label_map) for case in original]
    result = {}
    for row in original_rows:
        arm = row["arm"]
        if (row["phase"], row["round"]) != ("evaluation", 2) or arm not in ARMS:
            continue
        memory = []
        for example in json.loads(row["prompt"])["memory"]:
            case = source_cases[example["id"]]
            answer = example["solution"]
            if not is_correct(case.task, answer):
                raise ValueError(f"Invalid original example for {case.id}")
            memory.append((case, answer))
        independent_memory = rename_memory(memory, lambda case: rename(case, seed))
        shared_memory = rename_memory(
            memory, lambda case: (rename_with_labels(case, label_map), label_map),
        )
        result[arm] = {
            "original": (original, memory),
            "memory_only": (original, independent_memory),
            "query_only": (independently_renamed, memory),
            "independent_both": (independently_renamed, independent_memory),
            "shared_map": (shared_queries, shared_memory),
        }
    if set(result) != set(ARMS):
        raise ValueError(f"Missing archived final memories for seed {seed}")
    return result


def read_seed(source, seed):
    return read_calls(source / str(seed))


def run(source, output, port, *, backend_type=Backend, cells=FRESH):
    output.mkdir(parents=True)
    with (output / "calls.jsonl").open("w") as trace:
        backend = backend_type(port, trace)
        for seed, pools in study_pools().items():
            cells_by_arm = prompts(seed, pools, read_seed(source, seed))
            records = {}
            for arm in ARMS:
                records[arm] = {}
                for cell in cells:
                    cases, memory = cells_by_arm[arm][cell]
                    answers = backend.call(
                        "evaluation", f"{seed}/{arm}/{cell}", 2, cases, memory, sampling_seed=seed,
                    )
                    records[arm][cell] = score(
                        cases, [is_correct(case.task, answers.get(case.id)) for case in cases],
                    )
            (output / f"{seed}.json").write_text(json.dumps(records, indent=2) + "\n")
            print(f"Seed {seed} complete", flush=True)


def score_call(row, cases, memory):
    expected = {
        "tasks": [case.prompt_record() for case in cases],
        "memory": [{**case.prompt_record(), "solution": answer} for case, answer in memory],
    }
    if json.loads(row["prompt"]) != json.loads(json.dumps(expected)):
        raise ValueError(f"Prompt mismatch for {row['arm']}")
    if row["output_tokens"] is not None and (
        row["output_tokens"] > 384 or row["prompt_tokens"] + row["output_tokens"] > 4096
    ):
        raise ValueError(f"Token budget exceeded for {row['arm']}")
    answers = parse_answers(row["response"])
    return score(cases, [is_correct(case.task, answers.get(case.id)) for case in cases])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ollama-port", type=int)
    parser.add_argument("--gemma-model-dir", type=Path, help="Run all five E006 cells on Gemma.")
    parser.add_argument("--lmstudio-port", type=int, default=1234)
    args = parser.parse_args()
    if args.gemma_model_dir:
        verify_gemma_files(args.gemma_model_dir)
        run(args.source, args.output, args.lmstudio_port, backend_type=GemmaBackend, cells=CELLS)
    else:
        run(args.source, args.output, args.ollama_port)
