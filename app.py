import os
from fastapi import FastAPI, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from requirement_analysis.main import extract_requirements
from architecture_and_tech_stack.main import get_tech_stack_recommendation, generate_architecture_diagram
from time_and_effort_estimation.main import generate_effort_excel
from business_analyst.main import get_user_persona, categorize_features
from typing import List, Dict
import json

app = FastAPI()

# Enable CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body models
class ModuleFeature(BaseModel):
    name: str
    description: str

class Module(BaseModel):
    module: str
    features: List[ModuleFeature]

class Requirements(BaseModel):
    functionalRequirement: List[str]
    nonFunctionalRequirement: List[str]
    featureBreakdown: List[Module]

class TechComponent(BaseModel):
    name: str
    description: str

class TechStack(BaseModel):
    frontend: List[TechComponent]
    backend: List[TechComponent]
    database: List[TechComponent]
    API_integrations: List[TechComponent]
    others: List[TechComponent]

class RequirementRequest(BaseModel):
    requirement_json: Dict

class ExtractRequest(BaseModel):
     requirement_text: str
     url: str
     

@app.get("/")
async def get_response():
    return "hello world"

@app.post("/extract")
def extract(req: ExtractRequest):
     try:
         result = extract_requirements(req.requirement_text, req.url)
         return {"message": "Extraction successful", "data": result}
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/tech-stack-recommendation")
async def tech_stack_recommendation(req: Requirements):
    """
    Accepts a detailed requirement request body, validates it,
    and returns a tech stack recommendation.
    """
    if not req:
        raise HTTPException(status_code=400, detail="Requirements are missing in the request body.")

    try:
        response = get_tech_stack_recommendation(req.dict())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/architecture-diagram")
async def create_architecture_diagram(requirements: Requirements, tech_stack: TechStack):
    """
    Accepts requirements and tech stack in the request body,
    validates them, and returns an architecture diagram.
    """
    if not requirements:
        raise HTTPException(status_code=400, detail="Requirements are missing in the request body.")
    
    if not tech_stack:
        raise HTTPException(status_code=400, detail="Tech stack is missing in the request body.")

    try:
        response = generate_architecture_diagram(requirements.dict(), tech_stack.dict())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/estimate")
async def estimate_effort(req: Requirements):
    try:
        output_excel = "effort_estimation.xlsx"
        generate_effort_excel(req.dict(), output_excel)
        
        with open(output_excel, "rb") as file:
            excel_data = file.read()
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={output_excel}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-user-persona")
async def generate_user_persona(request: RequirementRequest):
    """
    FastAPI endpoint to process requirements and generate user personas.
    """
    try:
        requirement_str = json.dumps(request.requirement_json)
        user_persona = get_user_persona(requirement_str)
        categorized_features = categorize_features(requirement_str)
        response_json =  {"user_persona": json.loads(user_persona), "categorized_features": json.loads(categorized_features)}
        # print(response_json)

        return response_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-wireframe")
async def generate_wireframe(req: Requirements):
    """
    Accepts a detailed requirement request body, validates it,
    and returns a tech stack recommendation.
    """
    if not req:
        raise HTTPException(status_code=400, detail="Requirements are missing in the request body.")

    try:
        response ={"message" : "Wireframe generation is under maintenance"}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
