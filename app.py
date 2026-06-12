from __future__ import annotations

from pathlib import Path

import streamlit as st

from crew_runner import run_research_pilot
from tools import BASE_DIR


SAMPLE_DIR = BASE_DIR / "data" / "sample_inputs"


def load_sample(name: str) -> str:
    return (SAMPLE_DIR / name).read_text(encoding="utf-8")


st.set_page_config(page_title="ResearchPilot Crew", layout="wide")

st.title("ResearchPilot Crew")
st.caption("Turn messy research/startup ideas into an execution-ready plan.")

with st.sidebar:
    mode = st.selectbox("Mode", ["auto", "mock", "live"], index=1)
    task_type = st.selectbox(
        "Task type",
        ["auto", "wsdm_paper", "remind_mvp", "lab_meeting", "professor_outreach", "general"],
    )
    output_dir = st.text_input("Output directory", value="outputs")
    if st.button("Load WSDM sample"):
        st.session_state["idea_text"] = load_sample("wsdm_idea.txt")
    if st.button("Load Re:mind MVP sample"):
        st.session_state["idea_text"] = load_sample("remind_mvp.txt")

if "idea_text" not in st.session_state:
    st.session_state["idea_text"] = load_sample("wsdm_idea.txt")

idea_text = st.text_area(
    "Raw idea dump",
    key="idea_text",
    height=260,
    placeholder="Paste a messy research or startup idea here.",
)

if st.button("Run ResearchPilot", type="primary"):
    with st.spinner("Running 8-agent ResearchPilot workflow..."):
        result = run_research_pilot(
            user_input=idea_text,
            mode=mode,
            task_type=task_type,
            output_dir=output_dir,
        )
    st.success(f"Run complete. Mode: {result['mode_used']} | Task type: {result['task_type']}")
    st.write("Saved files:", result["saved_files"])

    tab_brief, tab_action, tab_advisor, tab_agents, tab_log = st.tabs(
        ["Research Brief", "Action Plan", "Advisor Message", "Agent Outputs", "Run Log"]
    )
    with tab_brief:
        st.markdown(result["research_brief"])
    with tab_action:
        st.json(result["action_plan"])
    with tab_advisor:
        st.markdown(result["advisor_message"])
    with tab_agents:
        st.json(result["agent_outputs"])
    with tab_log:
        st.json(result["run_log"])
