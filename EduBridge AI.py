import os
from typing import Dict, TypedDict, Optional
from groq import Groq
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import sys
import io

# Force standard output to support Unicode / Hindi characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load API key from .env file (never hardcode secrets)
load_dotenv()
# GROQ_API_KEY is read automatically from environment by ChatGroq
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3
)

# 1. Define the Global State Sch
# ema
class AgentState(TypedDict):
    source_material: str
    target_language: str
    target_region: str
    structured_lessons: Optional[str]
    localized_content: Optional[str]
    evaluation_rubric: Optional[str]
    routing_destination: str

# 2. Agent Node: Central Router & Supervisor
def supervisor_router(state: AgentState) -> Dict:
    """Evaluates input parameters and determines structural flow."""
    print("--- [Supervisor Router] Processing Raw Input Request ---")
    
    # Simple explicit conditional routing logic based on state validation
    if not state.get("source_material"):
        return {"routing_destination": "end"}
    
    # Direct initial processing trajectory to the pedagogical extraction engine
    return {"routing_destination": "structure_content"}

# 3. Agent Node: Pedagogical Structurer
def pedagogical_structurer(state: AgentState) -> Dict:
    """Isolates foundational concepts and strips out non-essential text fillers."""
    print("--- [Pedagogical Structurer] Extracting Core Academic Roadmap ---")
    
    prompt = (
        f"Analyze the following textbook excerpt. Extract the foundational learning objectives, "
        f"core definitions, and essential conceptual maps. Strip away all unnecessary filler text:\n\n"
        f"{state['source_material']}"
    )
    
    response = llm.invoke(prompt)
    return {
        "structured_lessons": response.content,
        "routing_destination": "localize_content"
    }

# 4. Agent Node: Cultural Localization Engine
def localization_agent(state: AgentState) -> Dict:
    """Translates text and swaps names, idioms, and units for regional context."""
    print(f"--- [Localization Agent] Adapting Context for {state['target_region']} ({state['target_language']}) ---")
    
    prompt = (
        f"You are an expert curriculum designer. Translate and adapt the following structured concepts "
        f"into '{state['target_language']}'. Critically, alter all names, idioms, cultural references, "
        f"and measurement units so they natively fit the localized real-world environment of children living in "
        f"'{state['target_region']}':\n\n"
        f"{state['structured_lessons']}"
    )
    
    response = llm.invoke(prompt)
    return {
        "localized_content": response.content,
        "routing_destination": "generate_assessment"
    }

# 5. Agent Node: Quiz & Worksheet Generator
def quiz_generator(state: AgentState) -> Dict:
    """Generates localized assessment items and matching teacher evaluation rubrics."""
    print("--- [Quiz Generator] Compiling Localized Assessments & Rubrics ---")
    
    prompt = (
        f"Based on this localized content, generate a comprehensive assessment worksheet for students "
        f"along with a corresponding teacher's answer key and grading rubric. Ensure the questions "
        f"reference the localized context:\n\n"
        f"{state['localized_content']}"
    )
    
    response = llm.invoke(prompt)
    return {
        "evaluation_rubric": response.content,
        "routing_destination": "end"
    }

# 6. Building the LangGraph State Machine Workflow Orchestration
workflow = StateGraph(AgentState)

# Add processing nodes to the graph state
workflow.add_node("router", supervisor_router)
workflow.add_node("structure_content", pedagogical_structurer)
workflow.add_node("localize_content", localization_agent)
workflow.add_node("generate_assessment", quiz_generator)

# Establish Entrypoint
workflow.set_entry_point("router")

# Define conditional execution routing rules
workflow.add_conditional_edges(
    "router",
    lambda state: state["routing_destination"],
    {
        "structure_content": "structure_content",
        "end": END
    }
)

workflow.add_conditional_edges(
    "structure_content",
    lambda state: state["routing_destination"],
    {
        "localize_content": "localize_content"
    }
)

workflow.add_conditional_edges(
    "localize_content",
    lambda state: state["routing_destination"],
    {
        "generate_assessment": "generate_assessment"
    }
)

workflow.add_conditional_edges(
    "generate_assessment",
    lambda state: state["routing_destination"],
    {
        "end": END
    }
)

# Compile Runtime Application
app = workflow.compile()

# --- Execution Example Blueprint ---
if __name__ == "__main__":
    initial_payload = {
        "source_material": (
            "Chapter 3: Financial Basics. John went to Wall Street in New York and bought 3 shares of "
            "tech stocks using USD. He calculated his compound interest using quarterly dividend distributions."
        ),
        "target_language": "Hindi",
        "target_region": "Rural Bihar, India",
        "structured_lessons": None,
        "localized_content": None,
        "evaluation_rubric": None,
        "routing_destination": ""
    }
    
    print("\nStarting EduBridge AI Agentic Processing pipeline...\n")
    final_state = app.invoke(initial_payload)
    
    print("\n================ PROCESSING RESULTS ================")
    print("\n### LOCALIZED CONTENT OUTPUT ###\n", final_state["localized_content"])
    print("\n### GENERATED WORKSHEETS & RUBRICS ###\n", final_state["evaluation_rubric"])