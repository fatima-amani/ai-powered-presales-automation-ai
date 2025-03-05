import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from requirement_analysis.main import extract_requirements
from requirement_analysis.extract_from_doc import extract_text_from_pdf, extract_text_from_doc

# Initialize FastAPI
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL if deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define response endpoint
@app.get("/")
async def get_response():
    return "hello world"

# API: Process Extracted Text for Requirements
@app.post("/process")
async def process_text(text: str = Form(...)):
    if not text:
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    result = extract_requirements(text)
    return JSONResponse(content=result, status_code=200)

# Run the FastAPI app (only if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
