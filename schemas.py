from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TriageOutput(BaseModel):
    task_type: str
    urgency: str
    main_goal: str
    constraints: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    recommended_route: str


class ResearchQuestionOutput(BaseModel):
    problem: str
    gap: str
    core_research_question: str
    one_line_idea: str
    contribution_candidates: list[str] = Field(default_factory=list)
    reviewer_risks: list[str] = Field(default_factory=list)


class LiteratureOutput(BaseModel):
    related_work_areas: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    seed_papers: list[dict[str, Any]] = Field(default_factory=list)
    reading_priority: list[str] = Field(default_factory=list)


class ExperimentPlanOutput(BaseModel):
    datasets: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    ablations: list[str] = Field(default_factory=list)
    minimum_viable_experiment: str
    feasibility_notes: list[str] = Field(default_factory=list)


class StartupValidationOutput(BaseModel):
    target_users: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    mvp_feature: str
    validation_questions: list[str] = Field(default_factory=list)
    business_value: str
    startup_risks: list[str] = Field(default_factory=list)


class ActionPlanOutput(BaseModel):
    today: list[str] = Field(default_factory=list)
    tomorrow: list[str] = Field(default_factory=list)
    this_week: list[str] = Field(default_factory=list)
    priority_ranking: list[dict[str, Any]] = Field(default_factory=list)
    do_not_do_today: list[str] = Field(default_factory=list)


class ReviewOutput(BaseModel):
    novelty_score: int = Field(ge=1, le=5)
    feasibility_score: int = Field(ge=1, le=5)
    clarity_score: int = Field(ge=1, le=5)
    main_weakness: str
    required_revision: str
    acceptance_potential: str


class FinalOutput(BaseModel):
    mode_used: str
    task_type: str
    research_brief: str
    advisor_message: str
    action_plan: dict[str, Any]
    agent_outputs: dict[str, Any]
    saved_files: dict[str, str] = Field(default_factory=dict)
    run_log: dict[str, Any] = Field(default_factory=dict)


class RunLog(BaseModel):
    timestamp: str
    mode_requested: str
    mode_used: str
    task_type: str
    agents_run: list[str] = Field(default_factory=list)
    patterns_used: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    completeness_score: int = Field(ge=0, le=8)
    number_of_todos: int = 0
    saved_files: dict[str, str] = Field(default_factory=dict)


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
