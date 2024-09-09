import logging
from langchain.tools import Tool
from git import Repo
from my_agent.utils.state import RefactorState
from my_agent.utils.config import GraphConfig
from my_agent.utils.summary import generate_summary
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_repo(state: RefactorState, config: GraphConfig) -> RefactorState:
    logger.info("Setting up repository")
    repo_url = state.get("repo_url")
    logger.debug(f"Cloning repository from {repo_url}")
    repo = Repo.clone_from(repo_url, "./temp_repo")
    new_branch = repo.create_head("refactor-branch")
    new_branch.checkout()
    state["repo_path"] = "./temp_repo"
    logger.info(f"Repository set up at {state['repo_path']}")
    return state

def read_file_in_chunks(file_path: str, chunk_size: int = 4000) -> list[str]:
    logger.info(f"Reading file in chunks: {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    logger.debug(f"File split into {len(chunks)} chunks")
    return chunks

def write_file(file_path: str, content: str):
    logger.info(f"Writing file: {file_path}")
    with open(file_path, 'w') as file:
        file.write(content)
    logger.debug(f"File written successfully: {file_path}")

def process_file(file_path: str) -> str:
    logger.info(f"Processing file: {file_path}")
    chunks = read_file_in_chunks(file_path)
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Here you would typically send the chunk to an LLM for processing
        # For this example, we'll just add a comment
        processed_chunk = f"// Processed chunk {i}\n" + chunk
        processed_chunks.append(processed_chunk)
    
    processed_content = "".join(processed_chunks)
    write_file(file_path, processed_content)
    logger.info(f"Finished processing file: {file_path}")
    return f"Processed file {file_path}"

def extract_components(file_path: str) -> str:
    logger.info(f"Extracting components from file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Simple regex to find React components (this is a basic example and might need refinement)
    component_regex = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{[^}]*}'
    components = re.findall(component_regex, content)
    logger.debug(f"Found {len(components)} components")
    
    for component in components:
        component_content = re.search(f'const\s+{component}\s*=.*?}}', content, re.DOTALL)
        if component_content:
            new_file_path = os.path.join(os.path.dirname(file_path), f"{component}.js")
            logger.debug(f"Creating new file for component: {new_file_path}")
            with open(new_file_path, 'w') as new_file:
                new_file.write(component_content.group())
            content = content.replace(component_content.group(), f"import {component} from './{component}';")
    
    write_file(file_path, content)
    logger.info(f"Finished extracting components from {file_path}")
    return f"Extracted components from {file_path}"

def optimize_structure(file_path: str) -> str:
    logger.info(f"Optimizing structure for file: {file_path}")
    # This is a placeholder for more complex optimization logic
    logger.debug("Optimization logic not implemented yet")
    return f"Optimized structure for {file_path}"

tools = [
    Tool(name="ProcessFile", func=process_file, description="Process a large file"),
    Tool(name="ExtractComponents", func=extract_components, description="Extract components from a file"),
    Tool(name="OptimizeStructure", func=optimize_structure, description="Optimize project structure"),
    Tool(name="GenerateSummary", func=generate_summary, description="Generate a summary of changes"),
]
logger.info("Tools initialized")