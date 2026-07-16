"""
EduBridge AI — FastAPI Backend
Exposes the LangGraph multi-agent pipeline as a REST API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import time

from agent import run_pipeline

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="EduBridge AI API",
    description="Multi-agent AI pipeline for educational content localization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class ProcessRequest(BaseModel):
    source_material: str = Field(..., min_length=10, description="Textbook excerpt to process")
    target_language: str = Field(..., description="Target language for localization")
    target_region: str   = Field(..., description="Target region for cultural adaptation")

class ProcessResponse(BaseModel):
    success: bool
    processing_time_seconds: float
    structured_lessons: str
    localized_content: str
    evaluation_rubric: str

class LanguageOption(BaseModel):
    value: str
    label: str

class RegionOption(BaseModel):
    value: str
    label: str

# ---------------------------------------------------------------------------
# Static Data
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: List[LanguageOption] = [
    LanguageOption(value="Hindi", label="Hindi (हिन्दी)"),
    LanguageOption(value="Bengali", label="Bengali (বাংলা)"),
    LanguageOption(value="Tamil", label="Tamil (தமிழ்)"),
    LanguageOption(value="Telugu", label="Telugu (తెలుగు)"),
    LanguageOption(value="Marathi", label="Marathi (मराठी)"),
    LanguageOption(value="Gujarati", label="Gujarati (ગુજરાતી)"),
    LanguageOption(value="Kannada", label="Kannada (ಕನ್ನಡ)"),
    LanguageOption(value="Malayalam", label="Malayalam (മലയാളം)"),
    LanguageOption(value="Punjabi", label="Punjabi (ਪੰਜਾਬੀ)"),
    LanguageOption(value="Odia", label="Odia (ଓଡ଼ିଆ)"),
    LanguageOption(value="Urdu", label="Urdu (اردو)"),
    LanguageOption(value="Swahili", label="Swahili"),
    LanguageOption(value="Hausa", label="Hausa"),
    LanguageOption(value="Arabic", label="Arabic (العربية)"),
    LanguageOption(value="French", label="French (Français)"),
    LanguageOption(value="Portuguese", label="Portuguese (Português)"),
    LanguageOption(value="Spanish", label="Spanish (Español)"),
]

SUPPORTED_REGIONS: List[RegionOption] = [
    RegionOption(value="Rural Bihar, India", label="Rural Bihar, India"),
    RegionOption(value="Rural Uttar Pradesh, India", label="Rural Uttar Pradesh, India"),
    RegionOption(value="Rural Rajasthan, India", label="Rural Rajasthan, India"),
    RegionOption(value="Rural West Bengal, India", label="Rural West Bengal, India"),
    RegionOption(value="Rural Tamil Nadu, India", label="Rural Tamil Nadu, India"),
    RegionOption(value="Rural Maharashtra, India", label="Rural Maharashtra, India"),
    RegionOption(value="Rural Punjab, India", label="Rural Punjab, India"),
    RegionOption(value="Rural Gujarat, India", label="Rural Gujarat, India"),
    RegionOption(value="Sub-Saharan Africa (Kenya)", label="Sub-Saharan Africa (Kenya)"),
    RegionOption(value="Sub-Saharan Africa (Nigeria)", label="Sub-Saharan Africa (Nigeria)"),
    RegionOption(value="Rural Bangladesh", label="Rural Bangladesh"),
    RegionOption(value="Rural Pakistan", label="Rural Pakistan"),
    RegionOption(value="Rural Nepal", label="Rural Nepal"),
    RegionOption(value="Rural Egypt", label="Rural Egypt"),
    RegionOption(value="Rural Brazil", label="Rural Brazil"),
    RegionOption(value="Rural Mexico", label="Rural Mexico"),
]

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["System"])
def health_check():
    """Returns server health status."""
    return {"status": "ok", "service": "EduBridge AI API"}


@app.get("/api/languages", response_model=List[LanguageOption], tags=["Reference Data"])
def get_languages():
    """Returns the list of supported target languages."""
    return SUPPORTED_LANGUAGES


@app.get("/api/regions", response_model=List[RegionOption], tags=["Reference Data"])
def get_regions():
    """Returns the list of supported target regions."""
    return SUPPORTED_REGIONS


@app.post("/api/process", response_model=ProcessResponse, tags=["Pipeline"])
def process_content(request: ProcessRequest):
    """
    Run the full EduBridge AI multi-agent pipeline.

    Stages:
      1. Supervisor Router  — validates input
      2. Pedagogical Structurer — extracts learning objectives
      3. Localization Agent — translates & culturally adapts content
      4. Quiz Generator — creates worksheets & rubrics

    Returns all three outputs when the pipeline completes.
    """
    start = time.time()
    try:
        result = run_pipeline(
            source_material=request.source_material,
            target_language=request.target_language,
            target_region=request.target_region
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    elapsed = round(time.time() - start, 2)

    return ProcessResponse(
        success=True,
        processing_time_seconds=elapsed,
        structured_lessons=result["structured_lessons"],
        localized_content=result["localized_content"],
        evaluation_rubric=result["evaluation_rubric"]
    )
