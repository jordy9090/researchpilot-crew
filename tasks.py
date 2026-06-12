from __future__ import annotations

from typing import Any

from agents import AGENT_NAMES


TASK_TYPES = ["auto", "wsdm_paper", "remind_mvp", "lab_meeting", "professor_outreach", "general"]

PATTERNS_USED = [
    "Multi-agent collaboration",
    "Prompt chaining",
    "Routing",
    "Tool use",
    "Reflection / critic-reviewer",
    "Memory management",
    "Guardrails / safety",
    "Exception handling and recovery",
    "Evaluation and monitoring",
]


def create_crewai_tasks(agent_map: dict[str, Any], user_input: str, task_type: str = "auto") -> list[Any]:
    try:
        from crewai import Task
    except Exception as exc:  # pragma: no cover - depends on optional live dependency
        raise RuntimeError(f"CrewAI Task is not available: {exc}") from exc

    triage = Task(
        description=(
            "Classify this raw research/startup idea dump into one route: "
            "wsdm_paper, remind_mvp, lab_meeting, professor_outreach, or general. "
            "Extract urgency, main goal, constraints, missing information, and recommended_route. "
            f"Requested task type: {task_type}. User input:\n{user_input}\n"
            "Return strict JSON compatible with TriageOutput."
        ),
        expected_output="TriageOutput JSON.",
        agent=agent_map["Intake & Triage Agent"],
    )
    question = Task(
        description=(
            "Using the triage result, create a researchable question, problem, gap, one-line idea, "
            "contribution candidates, and reviewer risks. Return strict JSON compatible with ResearchQuestionOutput."
        ),
        expected_output="ResearchQuestionOutput JSON.",
        agent=agent_map["Research Question Architect"],
        context=[triage],
    )
    literature = Task(
        description=(
            "Suggest related work areas, search queries, seed papers, and reading priority. "
            "Use the local paper database conceptually; do not invent exact bibliographic claims. "
            "Return strict JSON compatible with LiteratureOutput."
        ),
        expected_output="LiteratureOutput JSON.",
        agent=agent_map["Literature Scout"],
        context=[triage, question],
    )
    experiment = Task(
        description=(
            "Design datasets, baselines, metrics, ablations, a minimum viable experiment, and feasibility notes. "
            "Return strict JSON compatible with ExperimentPlanOutput."
        ),
        expected_output="ExperimentPlanOutput JSON.",
        agent=agent_map["Experiment Designer"],
        context=[triage, question, literature],
    )
    startup = Task(
        description=(
            "Connect the plan to Re:mind or a startup/MVP direction. Identify target users, pain points, "
            "MVP feature, validation questions, business value, and startup risks. "
            "Return strict JSON compatible with StartupValidationOutput."
        ),
        expected_output="StartupValidationOutput JSON.",
        agent=agent_map["Startup Validator"],
        context=[triage, question, experiment],
    )
    execution = Task(
        description=(
            "Create a focused 48-hour action plan, this-week TODO list, priority ranking, and do-not-do-today list. "
            "Return strict JSON compatible with ActionPlanOutput."
        ),
        expected_output="ActionPlanOutput JSON.",
        agent=agent_map["Execution Planner"],
        context=[triage, question, literature, experiment, startup],
    )
    review = Task(
        description=(
            "Critique the plan as a top-tier AI conference reviewer and advisor. Check novelty, feasibility, "
            "clarity, dataset risk, scope creep, evaluation quality, and vagueness. "
            "Return strict JSON compatible with ReviewOutput."
        ),
        expected_output="ReviewOutput JSON.",
        agent=agent_map["Harsh Reviewer"],
        context=[question, literature, experiment, startup, execution],
    )
    report = Task(
        description=(
            "Synthesize all prior outputs into a polished ResearchPilot brief, advisor update message, "
            "action plan summary, and run summary. Incorporate the harsh reviewer feedback. "
            "Return Markdown sections, not code."
        ),
        expected_output="Final Markdown strings for the user.",
        agent=agent_map["Report Writer"],
        context=[triage, question, literature, experiment, startup, execution, review],
    )
    return [triage, question, literature, experiment, startup, execution, review, report]


def expected_agent_names() -> list[str]:
    return list(AGENT_NAMES)
