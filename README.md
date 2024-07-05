# Election Analysis

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

This a project for youtube video about LLM who analyse political program.
The project is still in progress.

# How to run ?
You need to create a .env file with 
```
POLITICAL_PARTI='nFP'
PDF_ROOT = "data/raw/"
TXT_ROOT = "data/raw/"

# all model can be change with ollama pckg
MODEL_GRADER = "phi3:medium" 
YAML_GRADER_PATH = "/prompts/grader_prompt.yaml"

MODEL_CRITICS = "nous-hermes2:10.7b"
YAML_CRITICS_PATH = "/prompts/criticer_prompt.yaml"

MODEL_QUERY_RAG_REWRITER = "phi3:3.8b"
YAML_QUERY_RAG_REWRITER_PATH = "/prompts/q_rewrite_rag_prompt.yaml"

MODEL_QUERY_WEB_REWRITER = "phi3:3.8b"
YAML_QUERY_WEB_REWRITER_PATH = "/prompts/q_rewrite_websearch_prompt.yaml"

MODEL_GENERATOR = "nous-hermes2:10.7b"
YAML_GENERATOR_PATH = "/prompts/generate_prompt.yaml"

MODEL_SUMMARY = "openhermes"
YAML_SUMMARY_PATH = "/prompts/resume_prompt.yaml"

MODEL_RESUME_WEBSEARCH = "nous-hermes2:10.7b"
YAML_RESUME_WEB_PATH = "/prompts/resume_websearch_prompt.yaml"
```

use 
Create env with : 
```
poetry shell 
```
Run streamlit chatbot with:
```
poetry run streamlit run election_analysis/chat_app.py
```

## Version
v0.1

## Project Organization

```
├── README.md          <- The top-level README for developers using this project.
├── data
│   └── raw            <- The original, immutable data dump.
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for election_analysis
│                         and configuration for tools like black
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
└── election_analysis                <- Source code for use in this project.

```

--------

