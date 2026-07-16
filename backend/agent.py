"""
EduBridge AI — Agent Pipeline (importable module)
Wraps the LangGraph multi-agent workflow for use by the FastAPI backend.
"""

import os
from typing import Dict, TypedDict, Optional
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Lazy LLM singleton — initialized on first use so .env is always loaded first
_llm = None

def _get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
    return _llm

# ---------------------------------------------------------------------------
# 1. Global State Schema
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    source_material: str
    target_language: str
    target_region: str
    structured_lessons: Optional[str]
    localized_content: Optional[str]
    evaluation_rubric: Optional[str]
    routing_destination: str


# ---------------------------------------------------------------------------
# 2. Agent Nodes
# ---------------------------------------------------------------------------

def supervisor_router(state: AgentState) -> Dict:
    """Evaluates input parameters and determines structural flow."""
    if not state.get("source_material"):
        return {"routing_destination": "end"}
    return {"routing_destination": "structure_content"}


def pedagogical_structurer(state: AgentState) -> Dict:
    """Isolates foundational concepts and strips out non-essential text fillers."""
    prompt = (
        "Analyze the following textbook excerpt. Extract the foundational learning objectives, "
        "core definitions, and essential conceptual maps. Strip away all unnecessary filler text:\n\n"
        f"{state['source_material']}"
    )
    response = _get_llm().invoke(prompt)
    return {
        "structured_lessons": response.content,
        "routing_destination": "localize_content"
    }


def localization_agent(state: AgentState) -> Dict:
    """Translates text and swaps names, idioms, and units for regional context."""
    prompt = (
        "You are an expert curriculum designer. Translate and adapt the following structured concepts "
        f"into '{state['target_language']}'. Critically, alter all names, idioms, cultural references, "
        "and measurement units so they natively fit the localized real-world environment of children living in "
        f"'{state['target_region']}':\n\n"
        f"{state['structured_lessons']}"
    )
    response = _get_llm().invoke(prompt)
    return {
        "localized_content": response.content,
        "routing_destination": "generate_assessment"
    }


def quiz_generator(state: AgentState) -> Dict:
    """Generates localized assessment items and matching teacher evaluation rubrics."""
    prompt = (
        "Based on this localized content, generate a comprehensive assessment worksheet for students "
        "along with a corresponding teacher's answer key and grading rubric. Ensure the questions "
        "reference the localized context:\n\n"
        f"{state['localized_content']}"
    )
    response = _get_llm().invoke(prompt)
    return {
        "evaluation_rubric": response.content,
        "routing_destination": "end"
    }


# ---------------------------------------------------------------------------
# 3. Build & Compile the LangGraph Workflow
# ---------------------------------------------------------------------------

def _build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("router", supervisor_router)
    workflow.add_node("structure_content", pedagogical_structurer)
    workflow.add_node("localize_content", localization_agent)
    workflow.add_node("generate_assessment", quiz_generator)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        lambda state: state["routing_destination"],
        {"structure_content": "structure_content", "end": END}
    )
    workflow.add_conditional_edges(
        "structure_content",
        lambda state: state["routing_destination"],
        {"localize_content": "localize_content"}
    )
    workflow.add_conditional_edges(
        "localize_content",
        lambda state: state["routing_destination"],
        {"generate_assessment": "generate_assessment"}
    )
    workflow.add_conditional_edges(
        "generate_assessment",
        lambda state: state["routing_destination"],
        {"end": END}
    )

    return workflow.compile()


# Compile once at module load time
_app = _build_graph()


# ---------------------------------------------------------------------------
# 4. Public Interface
# ---------------------------------------------------------------------------

def run_pipeline(source_material: str, target_language: str, target_region: str) -> Dict:
    """
    Execute the full EduBridge AI agentic pipeline.

    Returns a dict with keys:
        - structured_lessons: str
        - localized_content:  str
        - evaluation_rubric:  str
    """
    payload = {
        "source_material": source_material,
        "target_language": target_language,
        "target_region": target_region,
        "structured_lessons": None,
        "localized_content": None,
        "evaluation_rubric": None,
        "routing_destination": ""
    }

    final_state = _app.invoke(payload)

    return {
        "structured_lessons": final_state.get("structured_lessons", ""),
        "localized_content": final_state.get("localized_content", ""),
        "evaluation_rubric": final_state.get("evaluation_rubric", "")
    }
