from __future__ import annotations

import json
from pathlib import Path

from crew_runner import run_research_pilot
from tools import BASE_DIR


EXPECTED_OUTPUTS = [
    "research_brief.md",
    "advisor_message.md",
    "action_plan.json",
    "agent_outputs.json",
    "run_log.json",
]


def main() -> None:
    sample_path = BASE_DIR / "data" / "sample_inputs" / "wsdm_idea.txt"
    memory_path = BASE_DIR / "data" / "project_memory.json"
    original_memory = memory_path.read_text(encoding="utf-8") if memory_path.exists() else '{"memories": []}'

    user_input = sample_path.read_text(encoding="utf-8")
    try:
        result = run_research_pilot(
            user_input=user_input,
            mode="mock",
            task_type="auto",
            output_dir="outputs",
        )

        assert result["mode_used"] == "mock", f"Expected mock mode, got {result['mode_used']!r}"
        assert result["task_type"], "Expected a non-empty task_type"

        agent_outputs = result["agent_outputs"]
        assert len(agent_outputs) >= 8, f"Expected at least 8 agent outputs, got {len(agent_outputs)}"
        assert "Report Writer" in agent_outputs, "Expected Report Writer output"

        run_log = result["run_log"]
        assert run_log["completeness_score"] >= 6, (
            f"Expected completeness_score >= 6, got {run_log['completeness_score']}"
        )

        output_dir = BASE_DIR / "outputs"
        missing_files = [name for name in EXPECTED_OUTPUTS if not (output_dir / name).exists()]
        assert not missing_files, f"Missing expected output files: {missing_files}"

        # Confirm generated JSON files are valid and inspectable.
        for filename in ["action_plan.json", "agent_outputs.json", "run_log.json"]:
            with (output_dir / filename).open("r", encoding="utf-8") as file:
                json.load(file)
    finally:
        memory_path.write_text(original_memory, encoding="utf-8")

    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
