from __future__ import annotations

from copy import deepcopy
from typing import Any


AGENT_SPECS: list[dict[str, Any]] = [
    {
        "name": "Intake & Triage Agent",
        "role": "Classifies raw idea dumps and chooses the route for the workflow.",
        "goal": "Extract task type, urgency, main goal, constraints, missing information, and recommended route.",
        "backstory": "A research project manager who quickly turns ambiguous notes into a usable execution brief.",
        "expected_output": "TriageOutput JSON with task_type, urgency, main_goal, constraints, missing_info, and recommended_route.",
        "patterns": ["Routing", "Guardrails / safety", "Prompt chaining"],
    },
    {
        "name": "Research Question Architect",
        "role": "Converts messy ideas into a researchable question and contribution frame.",
        "goal": "Produce the problem, gap, core research question, one-line idea, contributions, and reviewer risks.",
        "backstory": "A senior AI/NLP researcher who knows how to turn a vague system idea into a paper-shaped claim.",
        "expected_output": "ResearchQuestionOutput JSON with problem framing and contribution candidates.",
        "patterns": ["Prompt chaining", "Multi-agent collaboration"],
    },
    {
        "name": "Literature Scout",
        "role": "Suggests related work directions, search queries, and seed papers from a local database.",
        "goal": "Use local paper search to ground the research brief in concrete reading directions.",
        "backstory": "A focused literature review assistant that prefers targeted search queries over random paper hoarding.",
        "expected_output": "LiteratureOutput JSON with related_work_areas, search_queries, seed_papers, and reading_priority.",
        "patterns": ["Tool use", "Exception handling and recovery"],
    },
    {
        "name": "Experiment Designer",
        "role": "Designs datasets, baselines, metrics, ablations, and feasibility plan.",
        "goal": "Turn the research question into an evaluable minimum viable experiment.",
        "backstory": "An empirical ML engineer who worries about datasets, baselines, metrics, and scope before writing code.",
        "expected_output": "ExperimentPlanOutput JSON with datasets, baselines, metrics, ablations, MVE, and feasibility notes.",
        "patterns": ["Prompt chaining", "Guardrails / safety"],
    },
    {
        "name": "Startup Validator",
        "role": "Connects the research plan to Re:mind or a startup/MVP validation direction.",
        "goal": "Identify target users, pain points, MVP feature, validation questions, business value, and startup risks.",
        "backstory": "A pragmatic product researcher who keeps the system tied to real counselor workflow pain.",
        "expected_output": "StartupValidationOutput JSON with MVP validation plan.",
        "patterns": ["Multi-agent collaboration", "Routing"],
    },
    {
        "name": "Execution Planner",
        "role": "Creates a 48-hour action plan, this-week TODO list, priority ranking, and do-not-do list.",
        "goal": "Convert the research and startup plan into a focused next-action schedule.",
        "backstory": "A ruthless execution coach who reduces scope until the next two days are actually doable.",
        "expected_output": "ActionPlanOutput JSON with today, tomorrow, this_week, priority_ranking, and do_not_do_today.",
        "patterns": ["Tool use", "Guardrails / safety", "Evaluation and monitoring"],
    },
    {
        "name": "Harsh Reviewer",
        "role": "Critiques the generated plan from a top-tier AI conference reviewer and advisor perspective.",
        "goal": "Check novelty, feasibility, clarity, evaluation risk, dataset risk, and vagueness.",
        "backstory": "A tough but useful reviewer who points at the one weakness that could sink the project.",
        "expected_output": "ReviewOutput JSON with scores, main weakness, required revision, and acceptance potential.",
        "patterns": ["Reflection / critic-reviewer", "Guardrails / safety"],
    },
    {
        "name": "Report Writer",
        "role": "Synthesizes all prior outputs into polished Markdown, advisor message, action plan, and run summary.",
        "goal": "Produce TA-inspectable files and a directly useful research-to-action brief.",
        "backstory": "A concise technical writer who turns agent outputs into a readable report without hiding warnings.",
        "expected_output": "Markdown strings for research_brief, advisor_message, action_plan_markdown, and run_summary.",
        "patterns": ["Prompt chaining", "Reflection / critic-reviewer", "Evaluation and monitoring"],
    },
]


AGENT_NAMES = [spec["name"] for spec in AGENT_SPECS]


def get_agent_specs() -> list[dict[str, Any]]:
    return deepcopy(AGENT_SPECS)


def create_crewai_agents() -> dict[str, Any]:
    try:
        from crewai import Agent
    except Exception as exc:  # pragma: no cover - depends on optional live dependency
        raise RuntimeError(f"CrewAI is not available: {exc}") from exc

    crew_agents: dict[str, Any] = {}
    for spec in AGENT_SPECS:
        crew_agents[spec["name"]] = Agent(
            role=spec["role"],
            goal=spec["goal"],
            backstory=(
                f"{spec['backstory']}\n"
                f"Expected output responsibility: {spec['expected_output']}\n"
                f"Agentic patterns: {', '.join(spec['patterns'])}."
            ),
            verbose=False,
            allow_delegation=False,
        )
    return crew_agents
