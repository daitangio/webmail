- Project written in flask

# How to setup

Setup a vscode dev container using the provided Dockerfile.
Create a .devcontainer/.devcontainer.env with your DEEPSEEK_API_KEY: for security reason this file is never commited


Ensure you have everything you need with 

    python -m venv .venv
    . .venv/bin/activate
    pip install -e ".[dev]"    

python3 -m pytest tests/test_delete.py