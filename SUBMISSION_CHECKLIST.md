# Submission Checklist

## Homework #2: ResearchPilot Crew

Framework: CrewAI

Recommended run command:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_lab_key_here
export USE_STUB=0
python main.py --mode live --input data/sample_inputs/wsdm_idea.txt
```

Streamlit demo:

```bash
streamlit run app.py
```

Submitted files:

- source code
- `README.md`
- `REPORT.md`
- sample input files
- sample outputs
- `smoke_test.py`

API keys:

- No API keys are included.
- `.env` is ignored by git.
- `.env.example` contains empty placeholders only.

Expected outputs:

- `outputs/research_brief.md`
- `outputs/advisor_message.md`
- `outputs/action_plan.json`
- `outputs/agent_outputs.json`
- `outputs/run_log.json`
