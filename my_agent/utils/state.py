from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence

class RefactorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    file_path: str
    processed_chunks: list[str]
    extracted_components: list[str]

    # Old, may not be used.
    #repo_path: str
    #current_file: str
    #processed_content: str
    #summary: str