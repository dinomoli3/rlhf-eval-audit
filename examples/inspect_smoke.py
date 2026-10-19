"""Generate a tiny synthetic Inspect log to smoke-test the optional adapter.

The scorer reads a preassigned fixture outcome. It does not assess model bias.
Run with: python examples/inspect_smoke.py
"""

from pathlib import Path

from inspect_ai import Task, eval
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, scorer
from inspect_ai.solver import TaskState, generate


@scorer(metrics=[])
def fixture_rubric():
    async def score(state: TaskState, target: Target) -> Score:
        return Score(value=state.metadata["fixture_outcome"])

    return score


def main() -> None:
    samples = []
    for i in range(1, 25):
        outcomes = (1, 1) if i <= 12 else ((0, 0) if i <= 16 else (1, 0))
        for group, outcome in zip(("A", "B"), outcomes, strict=True):
            samples.append(
                Sample(
                    id=f"scenario_{i:02d}_{group}",
                    input="Reply with one short sentence.",
                    metadata={"pair_id": f"scenario_{i:02d}",
                              "group": group, "fixture_outcome": outcome},
                )
            )
    destination = Path("examples/inspect_logs")
    destination.mkdir(parents=True, exist_ok=True)
    result = eval(Task(dataset=samples, solver=generate(), scorer=fixture_rubric()),
                  model="mockllm/model", log_dir=str(destination), display="none")[0]
    print(result.location)


if __name__ == "__main__":
    main()
