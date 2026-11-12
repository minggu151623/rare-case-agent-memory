"""Run the fixed E001a offline fixture or the pinned local Ollama pilot."""

import argparse
from collections import Counter
import json
from pathlib import Path
from random import Random
from time import perf_counter
from urllib.request import ProxyHandler, Request, build_opener

from src.benchmark import FAMILIES, RARE, REFERENCE_WEIGHTS, make_pools
from src.planning import is_correct, shortest_path

MODEL = "qwen3:8b"
DIGEST = "500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41"
SEED = 4101
ROUNDS = 2
CAPACITY = 6
ARMS = ("self_selected", "random", "targeted")
RULES = (
    "Each task is a directed unit-cost graph. Traverse only listed edges in their "
    "direction. A locked edge (requires_key:true) needs the key. You acquire it "
    "permanently on first visiting key_at, including at the start. null means no key."
)


def oracle_answer(case):
    path = shortest_path(case.task)
    return {"unreachable": True} if path is None else {"path": list(path)}


def counts(cases):
    tally = Counter(case.family for case in cases)
    return {family: tally[family] for family in FAMILIES}


class Backend:
    def __init__(self, port, trace):
        self.trace = trace
        self.base = f"http://127.0.0.1:{port}" if port is not None else None
        self.opener = build_opener(ProxyHandler({}))
        if self.base:
            matches = [model for model in self.request("/api/tags")["models"]
                       if model["name"] == MODEL and model["digest"] == DIGEST]
            if not matches:
                raise ValueError(f"Expected installed {MODEL} digest {DIGEST}")
            self.version = self.request("/api/version")["version"]
        else:
            self.version = "fixture"

    def request(self, endpoint, payload=None):
        request = Request(
            self.base + endpoint,
            data=None if payload is None else json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with self.opener.open(request, timeout=120) as response:
            return json.load(response)

    def call(self, phase, arm, round_, cases, memory):
        output_format = "json"
        if phase == "proposal":
            allowed = [case.id for case in cases]
            instruction = (
                "Choose exactly three distinct IDs from the new tasks list, most useful first. "
                "The memory contains already solved examples for reference. Never select a "
                "memory ID. Allowed task IDs are " + ", ".join(allowed) + "."
            )
            output_format = {
                "type": "object",
                "properties": {"ids": {
                    "type": "array", "minItems": 3, "maxItems": 3,
                    "items": {"type": "string", "enum": allowed},
                }},
                "required": ["ids"],
                "additionalProperties": False,
            }
        else:
            instruction = (
                'Solve every task. Return {"answers":{"id":{"path":["start","...","goal"]}}}. '
                'Use {"unreachable":true} for an unreachable goal. Paths must be shortest.'
            )
        prompt = json.dumps({
            "memory": [
                {**case.prompt_record(), "solution": solution} for case, solution in memory
            ],
            "tasks": [case.prompt_record() for case in cases],
        }, separators=(",", ":"))
        start = perf_counter()
        if self.base:
            response = self.request("/api/chat", {
                "model": MODEL, "stream": False, "format": output_format, "think": False,
                "options": {"seed": SEED + round_, "temperature": 0, "num_ctx": 4096,
                            "num_predict": 384},
                "messages": [{"role": "system", "content": f"{RULES} {instruction}"},
                             {"role": "user", "content": prompt}],
            })
            raw = response["message"]["content"]
        elif phase == "proposal":
            preferred = sorted(cases, key=lambda case: FAMILIES.index(case.family))
            raw = json.dumps({"ids": [case.id for case in preferred[:3]]})
            response = {}
        else:
            raw = json.dumps({"answers": {case.id: oracle_answer(case) for case in cases}})
            response = {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        expected = "ids" if phase == "proposal" else "answers"
        expected_type = list if phase == "proposal" else dict
        valid = isinstance(parsed, dict) and isinstance(parsed.get(expected), expected_type)
        row = {"phase": phase, "arm": arm, "round": round_, "valid_format": valid,
               "prompt": prompt, "response": raw, "prompt_tokens": response.get("prompt_eval_count"),
               "output_tokens": response.get("eval_count"), "done_reason": response.get("done_reason")}
        if self.base:
            row["seconds"] = round(perf_counter() - start, 3)
        self.trace.write(json.dumps(row) + "\n")
        self.trace.flush()
        return parsed[expected] if valid else expected_type()


def evaluate(backend, arm, round_, holdout, memory):
    answers = backend.call("evaluation", arm, round_, holdout, memory)
    correct = [case for case in holdout if is_correct(case.task, answers.get(case.id))]
    return {"correct": counts(correct), "total": counts(holdout)}


def update(backend, arm, round_, menu, supplement, memory, rng):
    ids = backend.call("proposal", arm, round_, menu, memory)
    by_id = {case.id: case for case in menu}
    self_slots = 3 if arm == "self_selected" else 2
    selected = []
    seen = set()
    for id_ in ids[:self_slots]:
        if isinstance(id_, str) and id_ in by_id and id_ not in seen:
            selected.append(by_id[id_])
            seen.add(id_)
    external = None
    if arm != "self_selected":
        if arm == "random":
            family = rng.choices(FAMILIES, weights=REFERENCE_WEIGHTS)[0]
        else:
            frequency = counts(case for case, _ in memory)
            family = min(RARE, key=frequency.__getitem__)
        external = next(case for case in supplement if case.family == family)

    candidates = [*selected, external] if external else selected
    answers = backend.call("solve", arm, round_, candidates, memory)
    accepted = [(case, answers[case.id]) for case in candidates
                if is_correct(case.task, answers.get(case.id))]
    combined = memory + accepted
    updated = combined[-CAPACITY:]
    evicted = combined[:-CAPACITY]
    record = {
        "round": round_, "self_slots": self_slots, "invalid_self_slots": self_slots - len(selected),
        "selected": counts(selected), "supplement": external.family if external else None,
        "attempted": counts(candidates), "verified_and_admitted": counts(case for case, _ in accepted),
        "evicted": counts(case for case, _ in evicted),
        "retained": counts(case for case, _ in updated),
    }
    return updated, record


def run(port, output):
    initial, menus, supplements, holdout = make_pools(SEED, ROUNDS)
    initial_memory = [(case, oracle_answer(case)) for case in initial]
    output.mkdir(parents=True)
    with (output / "calls.jsonl").open("w") as trace:
        backend = Backend(port, trace)
        summary = {
            "backend": MODEL if port is not None else "oracle_fixture",
            "runtime_version": backend.version,
            "seed": SEED,
            "initial_memory": counts(initial),
            "initial_evaluation": evaluate(backend, "shared", 0, holdout, initial_memory),
            "arms": {},
        }
        rng = Random(SEED + 1)
        for arm in ARMS:
            memory = initial_memory.copy()
            summary["arms"][arm] = []
            for round_, (menu, supplement) in enumerate(zip(menus, supplements), start=1):
                memory, record = update(backend, arm, round_, menu, supplement, memory, rng)
                record["evaluation"] = evaluate(backend, arm, round_, holdout, memory)
                summary["arms"][arm].append(record)
    calls = [json.loads(line) for line in (output / "calls.jsonl").read_text().splitlines()]
    summary["calls"] = len(calls)
    summary["format_failures"] = sum(not call["valid_format"] for call in calls)
    for field in ("prompt_tokens", "output_tokens"):
        summary[field] = sum(call[field] or 0 for call in calls) if port is not None else None
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(output / "summary.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ollama-port", type=int, help="Local Ollama port. Omit for offline fixture.")
    parser.add_argument("--output", type=Path, required=True, help="New output directory.")
    args = parser.parse_args()
    run(args.ollama_port, args.output)


if __name__ == "__main__":
    main()
