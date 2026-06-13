from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from agents import AGENT_NAMES, create_crewai_agents
from memory_store import append_memory_entry
from mock_engine import report_writer, run_mock_agents
from schemas import (
    ActionPlanOutput,
    ExperimentPlanOutput,
    FinalOutput,
    LiteratureOutput,
    ResearchQuestionOutput,
    ReviewOutput,
    RunLog,
    StartupValidationOutput,
    TriageOutput,
    model_to_dict,
)
from tasks import PATTERNS_USED, create_crewai_tasks
from tools import detect_scope_creep, save_json, save_markdown


VALID_MODES = {"auto", "mock", "live"}
VALID_TASK_TYPES = {"auto", "wsdm_paper", "remind_mvp", "lab_meeting", "professor_outreach", "general"}


SCHEMA_BY_AGENT = {
    "Intake & Triage Agent": TriageOutput,
    "Research Question Architect": ResearchQuestionOutput,
    "Literature Scout": LiteratureOutput,
    "Experiment Designer": ExperimentPlanOutput,
    "Startup Validator": StartupValidationOutput,
    "Execution Planner": ActionPlanOutput,
    "Harsh Reviewer": ReviewOutput,
}


def run_research_pilot(
    user_input: str,
    mode: str = "auto",
    task_type: str = "auto",
    output_dir: str = "outputs",
) -> dict[str, Any]:
    """
    Runs the ResearchPilot Crew workflow.

    Args:
        user_input: Raw research/startup idea dump.
        mode: "auto", "mock", or "live".
              "auto" uses live only when API key exists, otherwise mock.
        task_type: "auto", "wsdm_paper", "remind_mvp", "lab_meeting",
                   "professor_outreach", or "general".
        output_dir: Directory where outputs are saved.

    Returns:
        dict with:
        - mode_used
        - task_type
        - research_brief
        - advisor_message
        - action_plan
        - agent_outputs
        - saved_files
        - run_log
    """
    mode_requested = mode if mode in VALID_MODES else "auto"
    task_type_requested = task_type if task_type in VALID_TASK_TYPES else "auto"
    warnings: list[str] = []
    fallback_used = False
    user_input = (user_input or "").strip()

    _load_dotenv_if_available()
    _disable_crewai_tracing_by_default()

    if len(user_input) < 10:
        warnings.append(
            "Input is empty or too short. Try data/sample_inputs/wsdm_idea.txt or provide a longer idea dump."
        )
        return _empty_result(mode_requested, task_type_requested, output_dir, warnings)

    should_try_live = _should_try_live(mode_requested)
    if mode_requested == "live" and not os.getenv("OPENAI_API_KEY"):
        warnings.append("OPENAI_API_KEY missing. Fallback to mock mode.")
        fallback_used = True
        should_try_live = False
    elif mode_requested == "auto" and not os.getenv("OPENAI_API_KEY"):
        warnings.append("No OPENAI_API_KEY detected; auto mode selected deterministic mock mode.")

    mode_used = "mock"
    live_raw_outputs: dict[str, str] = {}
    if should_try_live:
        try:
            live_raw_outputs = _run_live_crewai(user_input, task_type_requested)
            mode_used = "live"
        except Exception as exc:  # pragma: no cover - live path depends on optional APIs
            warnings.append("Live mode failed. Fallback to mock mode.")
            warnings.append(f"Live failure detail: {type(exc).__name__}: {exc}")
            fallback_used = True
            mode_used = "mock"

    agent_outputs = run_mock_agents(user_input, task_type_requested)
    if live_raw_outputs:
        for agent_name, raw_output in live_raw_outputs.items():
            if agent_name in agent_outputs:
                agent_outputs[agent_name]["live_crewai_output"] = raw_output
        warnings.append("Live CrewAI executed; deterministic schema normalizer preserved inspectable output files.")

    agent_outputs = _validate_agent_outputs(agent_outputs, warnings)
    task_type_used = agent_outputs["Intake & Triage Agent"]["task_type"]
    action_plan = agent_outputs["Execution Planner"]

    warnings.extend(detect_scope_creep(user_input, action_plan))
    _apply_guardrails(user_input, task_type_used, action_plan, warnings)
    agent_outputs["Execution Planner"] = action_plan

    report_output = report_writer(user_input, agent_outputs, warnings)
    agent_outputs["Report Writer"] = report_output

    advisor_message = report_output["advisor_message"]
    research_brief = report_output["research_brief"]
    completeness_score = _completeness_score(agent_outputs, advisor_message)
    number_of_todos = _count_todos(action_plan)

    try:
        append_memory_entry(
            {
                "task_type": task_type_used,
                "main_goal": agent_outputs["Intake & Triage Agent"]["main_goal"],
                "core_research_question": agent_outputs["Research Question Architect"]["core_research_question"],
                "warnings": warnings,
                "summary": report_output["run_summary"],
            }
        )
    except Exception as exc:
        warnings.append(f"Memory save failed but run continued: {type(exc).__name__}: {exc}")

    saved_files = _save_outputs(
        output_dir=output_dir,
        research_brief=research_brief,
        advisor_message=advisor_message,
        action_plan=action_plan,
        agent_outputs=agent_outputs,
        warnings=warnings,
        mode_requested=mode_requested,
        mode_used=mode_used,
        task_type_used=task_type_used,
        fallback_used=fallback_used,
        completeness_score=completeness_score,
        number_of_todos=number_of_todos,
    )

    run_log = _build_run_log(
        mode_requested,
        mode_used,
        task_type_used,
        warnings,
        fallback_used,
        completeness_score,
        number_of_todos,
        saved_files,
    )

    return model_to_dict(
        FinalOutput(
            mode_used=mode_used,
            task_type=task_type_used,
            research_brief=research_brief,
            advisor_message=advisor_message,
            action_plan=action_plan,
            agent_outputs=agent_outputs,
            saved_files=saved_files,
            run_log=run_log,
        )
    )


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        return


def _disable_crewai_tracing_by_default() -> None:
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")


def _should_try_live(mode_requested: str) -> bool:
    if os.getenv("USE_STUB") == "1":
        return False
    if mode_requested == "live":
        return True
    return mode_requested == "auto" and bool(os.getenv("OPENAI_API_KEY"))


def _run_live_crewai(user_input: str, task_type: str) -> dict[str, str]:
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
    try:
        from crewai import Crew, Process
    except Exception as exc:  # pragma: no cover - depends on optional live dependency
        raise RuntimeError(f"CrewAI is not installed or importable: {exc}") from exc

    crew_agents = create_crewai_agents()
    crew_tasks = create_crewai_tasks(crew_agents, user_input, task_type)
    crew = Crew(
        agents=list(crew_agents.values()),
        tasks=crew_tasks,
        process=Process.sequential,
        verbose=False,
    )
    crew.kickoff()

    outputs: dict[str, str] = {}
    for agent_name, task in zip(AGENT_NAMES, crew_tasks):
        raw = getattr(task, "output", None)
        outputs[agent_name] = str(raw) if raw is not None else ""
    return outputs


def _validate_agent_outputs(agent_outputs: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    validated: dict[str, Any] = {}
    for agent_name, schema in SCHEMA_BY_AGENT.items():
        data = agent_outputs.get(agent_name, {})
        try:
            validated[agent_name] = model_to_dict(schema(**data))
        except Exception as exc:
            warnings.append(f"{agent_name} validation failed and safe defaults were used: {type(exc).__name__}.")
            validated[agent_name] = data
    return validated


def _apply_guardrails(
    user_input: str,
    task_type_used: str,
    action_plan: dict[str, Any],
    warnings: list[str],
) -> None:
    lowered = user_input.lower()
    if task_type_used == "wsdm_paper" and not any(
        word in lowered for word in ["dataset", "data", "psycheval", "esconv", "records"]
    ):
        warning = "Dataset uncertainty detected. First action should be dataset decision."
        if warning not in warnings:
            warnings.append(warning)

    today = action_plan.get("today", [])
    if isinstance(today, list) and len(today) > 5:
        warning = "Too many TODOs detected. Today's plan was compressed to the top 3 actions."
        if warning not in warnings:
            warnings.append(warning)

    if any("compressed to the top 3 actions" in warning for warning in warnings):
        action_plan["today"] = list(today)[:3]


def _completeness_score(agent_outputs: dict[str, Any], advisor_message: str) -> int:
    research = agent_outputs.get("Research Question Architect", {})
    literature = agent_outputs.get("Literature Scout", {})
    experiment = agent_outputs.get("Experiment Designer", {})
    startup = agent_outputs.get("Startup Validator", {})
    action = agent_outputs.get("Execution Planner", {})
    review = agent_outputs.get("Harsh Reviewer", {})

    checks = [
        bool(research.get("core_research_question")),
        bool(research.get("contribution_candidates")),
        bool(literature.get("related_work_areas") or literature.get("seed_papers")),
        bool(experiment.get("datasets") and experiment.get("metrics")),
        bool(startup.get("mvp_feature") or startup.get("business_value")),
        bool(action.get("today") or action.get("tomorrow") or action.get("this_week")),
        bool(advisor_message),
        bool(review.get("main_weakness") and review.get("required_revision")),
    ]
    return sum(1 for check in checks if check)


def _count_todos(action_plan: dict[str, Any]) -> int:
    return sum(len(action_plan.get(key, [])) for key in ["today", "tomorrow", "this_week"])


def _build_run_log(
    mode_requested: str,
    mode_used: str,
    task_type_used: str,
    warnings: list[str],
    fallback_used: bool,
    completeness_score: int,
    number_of_todos: int,
    saved_files: dict[str, str],
) -> dict[str, Any]:
    return model_to_dict(
        RunLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            mode_requested=mode_requested,
            mode_used=mode_used,
            task_type=task_type_used,
            agents_run=AGENT_NAMES,
            patterns_used=PATTERNS_USED,
            warnings=warnings,
            fallback_used=fallback_used,
            completeness_score=completeness_score,
            number_of_todos=number_of_todos,
            saved_files=saved_files,
        )
    )


def _save_outputs(
    output_dir: str,
    research_brief: str,
    advisor_message: str,
    action_plan: dict[str, Any],
    agent_outputs: dict[str, Any],
    warnings: list[str],
    mode_requested: str,
    mode_used: str,
    task_type_used: str,
    fallback_used: bool,
    completeness_score: int,
    number_of_todos: int,
) -> dict[str, str]:
    saved_files: dict[str, str] = {}

    def save_file(key: str, saver, filename: str, payload) -> None:
        try:
            saved_files[key] = saver(filename, payload, output_dir)
        except Exception as exc:
            message = f"Saving {filename} failed: {type(exc).__name__}: {exc}"
            warnings.append(message)
            saved_files[key] = f"ERROR: {message}"

    save_file("research_brief", save_markdown, "research_brief.md", research_brief)
    save_file("advisor_message", save_markdown, "advisor_message.md", advisor_message)
    save_file("action_plan", save_json, "action_plan.json", action_plan)
    save_file("agent_outputs", save_json, "agent_outputs.json", agent_outputs)

    saved_files["run_log"] = "pending"
    run_log = _build_run_log(
        mode_requested,
        mode_used,
        task_type_used,
        warnings,
        fallback_used,
        completeness_score,
        number_of_todos,
        saved_files,
    )
    try:
        saved_files["run_log"] = save_json("run_log.json", run_log, output_dir)
        run_log["saved_files"] = saved_files
        save_json("run_log.json", run_log, output_dir)
    except Exception as exc:
        message = f"Saving run_log.json failed: {type(exc).__name__}: {exc}"
        warnings.append(message)
        saved_files["run_log"] = f"ERROR: {message}"

    return saved_files


def _empty_result(
    mode_requested: str,
    task_type_requested: str,
    output_dir: str,
    warnings: list[str],
) -> dict[str, Any]:
    task_type_used = "general" if task_type_requested == "auto" else task_type_requested
    mode_used = "mock"
    action_plan = {
        "today": ["Open data/sample_inputs/wsdm_idea.txt or paste a longer idea dump."],
        "tomorrow": [],
        "this_week": [],
        "priority_ranking": [],
        "do_not_do_today": ["Do not evaluate the project from an empty input."],
    }
    research_brief = (
        "# ResearchPilot Brief\n\n"
        "The input was empty or too short to run the full agent workflow.\n\n"
        "Try this command:\n\n"
        "```bash\n"
        "python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt\n"
        "```\n"
    )
    advisor_message = "Please provide a longer research or startup idea dump before sending an advisor update."
    agent_outputs: dict[str, Any] = {}
    saved_files = _save_outputs(
        output_dir,
        research_brief,
        advisor_message,
        action_plan,
        agent_outputs,
        warnings,
        mode_requested,
        mode_used,
        task_type_used,
        fallback_used=False,
        completeness_score=0,
        number_of_todos=_count_todos(action_plan),
    )
    run_log = _build_run_log(
        mode_requested,
        mode_used,
        task_type_used,
        warnings,
        False,
        0,
        _count_todos(action_plan),
        saved_files,
    )
    return model_to_dict(
        FinalOutput(
            mode_used=mode_used,
            task_type=task_type_used,
            research_brief=research_brief,
            advisor_message=advisor_message,
            action_plan=action_plan,
            agent_outputs=agent_outputs,
            saved_files=saved_files,
            run_log=run_log,
        )
    )
