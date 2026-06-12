from __future__ import annotations

import argparse
from pathlib import Path

from crew_runner import run_research_pilot
from tools import BASE_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ResearchPilot Crew from the command line.")
    parser.add_argument("--input", type=str, help="Path to a text file containing the raw idea dump.")
    parser.add_argument("--text", type=str, help="Raw idea dump as a command-line string.")
    parser.add_argument("--mode", choices=["auto", "mock", "live"], default="auto")
    parser.add_argument(
        "--task-type",
        choices=["auto", "wsdm_paper", "remind_mvp", "lab_meeting", "professor_outreach", "general"],
        default="auto",
    )
    parser.add_argument("--output-dir", default="outputs", help="Directory where output files are saved.")
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> str:
    if args.input:
        path = Path(args.input)
        if not path.exists():
            path = BASE_DIR / args.input
        return path.read_text(encoding="utf-8")
    if args.text:
        return args.text
    return (BASE_DIR / "data" / "sample_inputs" / "wsdm_idea.txt").read_text(encoding="utf-8")


def main() -> None:
    args = parse_args()
    user_input = read_input(args)
    result = run_research_pilot(
        user_input=user_input,
        mode=args.mode,
        task_type=args.task_type,
        output_dir=args.output_dir,
    )
    print("ResearchPilot Crew run complete")
    print(f"Mode used: {result['mode_used']}")
    print(f"Task type: {result['task_type']}")
    print("Saved files:")
    for key, path in result["saved_files"].items():
        print(f"  - {key}: {path}")
    preview = result["research_brief"].replace("\n", " ")[:500]
    print("\nResearch brief preview:")
    print(preview + ("..." if len(result["research_brief"]) > 500 else ""))


if __name__ == "__main__":
    main()
