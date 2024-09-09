import logging
from functools import lru_cache
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.messages import AIMessage

#from my_agent.utils.summary import generate_summary
from my_agent.utils.tools import tools

from my_agent.utils.config import GraphConfig

from langgraph.prebuilt import ToolNode
from my_agent.utils.state import RefactorState
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    logger.info(f"Getting model: {model_name}")
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        model = ChatAnthropic(temperature=0, model_name="claude-3-5-sonnet-20240620")
    else:
        logger.error(f"Unsupported model type: {model_name}")
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    logger.debug(f"Model {model_name} initialized and tools bound")
    return model

def generate_summary(state: RefactorState, config: GraphConfig) -> RefactorState:
    logger.info("Starting summary generation")
    summary = ""
    model_name = config.get("model_name", "anthropic")  # Default to "anthropic" if not specified
    llm = _get_model(model_name)
    
    for root, dirs, files in os.walk(state["repo_path"]):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.css')):
                file_path = os.path.join(root, file)
                logger.debug(f"Processing file: {file_path}")
                with open(file_path, 'r') as f:
                    content = f.read()
                prompt = PromptTemplate(
                    input_variables=["content"],
                    template="Summarize the changes made to this file:\n{content}\n"
                )
                chain = LLMChain(llm=llm, prompt=prompt)
                file_summary = chain.run(content=content)
                summary += f"Changes in {file_path}:\n{file_summary}\n\n"
    
    summary_path = os.path.join(state["repo_path"], 'REFACTOR_SUMMARY.md')
    with open(summary_path, 'w') as f:
        f.write(summary)
    logger.info(f"Summary written to {summary_path}")
    
    state["summary"] = summary
    return state

def should_continue(state):
    logger.debug("Checking if process should continue")
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls'):
        if not last_message.tool_calls:
            logger.info("No more tool calls, ending process")
            return "end"
        else:
            logger.info("Continuing process")
            return "continue"
    else:
        logger.info("Last message is not an AIMessage with tool_calls, continuing process")
        return "continue"

system_prompt = """You are a code refactoring assistant. Your task is to help refactor and optimize a single file.
Use the available tools to process the file, extract components, and optimize the structure."""

def call_model(state, config):
    logger.info("Calling model")
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    model_name = config.get("model_name", "anthropic")  # Default to "anthropic" if not specified
    model = _get_model(model_name)
    logger.debug(f"Invoking model with {len(messages)} messages")
    response = model.invoke(messages)
    logger.debug("Model response received")
    return {"messages": [response]}

tool_node = ToolNode(tools)
logger.info("ToolNode initialized with available tools")