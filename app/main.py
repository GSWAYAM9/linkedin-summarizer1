from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
from dotenv import load_dotenv

from app.scraper import extract_linkedin_text
from app.summarizer import summarize_text

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LinkedIn Summarizer API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlIn(BaseModel):
    url: str

class SummaryResponse(BaseModel):
    summary: str
    success: bool
    error: str = None

@app.get("/")
async def root():
    return {"message": "LinkedIn Summarizer API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/summarize", response_model=SummaryResponse)
async def summarize(inp: UrlIn):
    try:
        logger.info(f"Processing URL: {inp.url}")

        if "linkedin.com" not in inp.url:
            raise HTTPException(status_code=400, detail="Please provide a valid LinkedIn URL")

        text = extract_linkedin_text(inp.url)

        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="No meaningful text found in the LinkedIn post")

        summary = summarize_text(text)

        return SummaryResponse(summary=summary, success=True)

    except HTTPException as he:
        logger.error(f"HTTP error: {he.detail}")
        return SummaryResponse(summary="", success=False, error=str(he.detail))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return SummaryResponse(summary="", success=False, error="An unexpected error occurred. Please try again.")

@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})

@app.exception_handler(500)
async def server_error(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
