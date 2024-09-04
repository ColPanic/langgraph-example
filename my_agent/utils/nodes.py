# File: nodes.py
from functools import lru_cache
from langchain_community.chat_models import ChatAnthropic
from langchain_community.chat_models import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4")
    elif model_name == "anthropic":
        model = ChatAnthropic(temperature=0, model_name="claude-3-5-sonnet-20240620")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

system_prompt = """You are a code refactoring assistant. Your task is to help refactor and optimize large codebases.
Use the available tools to set up repositories, process files, optimize structure, and generate summaries."""

def call_model(state, config):
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    model_name = config["model_name"]
    model = _get_model(model_name)
    response = model.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)