from functools import lru_cache
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from my_agent.utils.state import RefactorState
from my_agent.utils.config import GraphConfig
import os

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        model = ChatAnthropic(temperature=0, model_name="claude-3-5-sonnet-20240620")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    return model

def generate_summary(state: RefactorState, config: GraphConfig) -> RefactorState:
    summary = ""
    model_name = config.get("model_name", "anthropic")  # Default to "anthropic" if not specified
    llm = _get_model(model_name)
    
    for root, dirs, files in os.walk(state["repo_path"]):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.css', '.py', '.java', '.c', '.cpp', '.h', '.hpp')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                prompt = PromptTemplate(
                    input_variables=["content"],
                    template="Summarize the changes made to this file:\n{content}\n"
                )
                chain = LLMChain(llm=llm, prompt=prompt)
                file_summary = chain.run(content=content)
                summary += f"Changes in {file_path}:\n{file_summary}\n\n"
    
    with open(os.path.join(state["repo_path"], 'REFACTOR_SUMMARY.md'), 'w') as f:
        f.write(summary)
    
    state["summary"] = summary
    return state