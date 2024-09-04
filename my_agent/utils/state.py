
# File: state.py
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence

class RefactorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    repo_path: str
    current_file: str
    processed_files: list[str]
    summary: str
