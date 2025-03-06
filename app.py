import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from requirement_analysis.main import extract_requirements
from architecture_and_tech_stack.main import get_tech_stack_recommendation
from typing import List, Dict


app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL if deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body model
class ExtractRequest(BaseModel):
    requirement_text: str
    url: str

# Define the request body model
class Requirements(BaseModel):
    functionalRequirement: List[str]  # Array of strings for functional requirements
    nonFunctionalRequirement: List[str]  # Array of strings for non-functional requirements
    featureBreakdown: Dict[str, str]  # Mixed type for feature breakdown (key-value pairs)


app = FastAPI()

# Define response endpoint
@app.get("/")
async def get_response():
    return "hello world"

@app.post("/extract")
async def extract(req: ExtractRequest):
    try:
        result = extract_requirements(req.requirement_text, req.url)
        return {"message": "Extraction successful", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tech-stack-recommendation")
async def tech_stack_recommendation(requirements: Requirements):
    """
    Accepts requirements in the request body, validates them, and returns a tech stack recommendation.
    """
    if not requirements:
        raise HTTPException(status_code=400, detail="Requirements are missing in the request body.")

    try:
        # Convert Pydantic model to a dictionary
        response = get_tech_stack_recommendation(requirements.dict())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Run the FastAPI app (only if executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
