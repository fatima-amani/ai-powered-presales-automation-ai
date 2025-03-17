import json
import os
import pandas as pd
from dotenv import load_dotenv
from together import Together
from langchain.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel, Field, validator
from typing import List, Optional

# Load API key
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

# Pricing model (cost per day for each developer level)
pricing_model = {
    "Junior": 100,
    "Mid": 200,
    "Senior": 300
}

# Define Pydantic models for structured output parsing
class Subfeature(BaseModel):
    name: str = Field(description="Name of the subfeature")
    frontend_days: float = Field(description="Number of days required for frontend development")
    backend_days: float = Field(description="Number of days required for backend development")

class Feature(BaseModel):
    name: str = Field(description="Name of the feature")
    subfeatures: List[Subfeature] = Field(description="List of subfeatures with effort estimations")

class Module(BaseModel):
    module: str = Field(description="Name of the module")
    features: List[Feature] = Field(description="List of features in this module")
    frontend_days: Optional[float] = Field(None, description="Total frontend development days for the module")
    backend_days: Optional[float] = Field(None, description="Total backend development days for the module")

    @validator('frontend_days', 'backend_days', pre=True, always=False)
    def set_totals(cls, v, values):
        # This validator will be skipped during the parsing phase and only used for validation
        return v or 0.0

class EffortEstimation(BaseModel):
    effort_estimation: List[Module] = Field(description="List of modules with effort estimations")

    class Config:
        # Add schema_extra for additional schema customization if needed
        schema_extra = {
            "title": "Effort Estimation",
            "description": "Structured effort estimation for software development"
        }

def estimate_effort(feature_breakdown):
    """Estimate frontend and backend efforts using Mistral LLM with Langchain parser."""
    
    # Initialize the Pydantic parser
    parser = PydanticOutputParser(pydantic_object=EffortEstimation)
    
    # Load RAG context from file
    try:
        with open("C:/Users/aitha/Desktop/PreSales Automation/ai-powered-presales-automation-ai/time_estimate_context.txt", "r", encoding="utf-8") as file:
            time_estimate_context = file.read()
    except FileNotFoundError:
        # Fallback if file doesn't exist
        time_estimate_context = "No historical context available."
        print("\n⚠️ time_estimate_context.txt file not found. Proceeding without historical context.")
    
    try:
        with open("C:/Users/aitha/Desktop/PreSales Automation/ai-powered-presales-automation-ai/cost_estimate_context.txt", "r", encoding="utf-8") as file:
            cost_estimate_context = file.read()
    except FileNotFoundError:
        # Fallback if file doesn't exist
        cost_estimate_context = "No historical context available."
        print("\n⚠️ cost_estimate_context.txt file not found. Proceeding without historical context.")
    
    # Modified format instructions for Pydantic v1
    format_instructions = """
    The output should be formatted as a JSON instance that conforms to the JSON schema below.

    {
        "properties": {
            "effort_estimation": {
                "title": "Effort Estimation",
                "description": "List of modules with effort estimations",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "title": "Module",
                            "description": "Name of the module",
                            "type": "string"
                        },
                        "features": {
                            "title": "Features",
                            "description": "List of features in this module",
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "title": "Name",
                                        "description": "Name of the feature",
                                        "type": "string"
                                    },
                                    "subfeatures": {
                                        "title": "Subfeatures",
                                        "description": "List of subfeatures with effort estimations",
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "title": "Name",
                                                    "description": "Name of the subfeature",
                                                    "type": "string"
                                                },
                                                "frontend_days": {
                                                    "title": "Frontend Days",
                                                    "description": "Number of days required for frontend development",
                                                    "type": "number"
                                                },
                                                "backend_days": {
                                                    "title": "Backend Days",
                                                    "description": "Number of days required for backend development",
                                                    "type": "number"
                                                }
                                            },
                                            "required": ["name", "frontend_days", "backend_days"]
                                        }
                                    }
                                },
                                "required": ["name", "subfeatures"]
                            }
                        },
                        "frontend_days": {
                            "title": "Frontend Days",
                            "description": "Total frontend development days for the module",
                            "type": "number"
                        },
                        "backend_days": {
                            "title": "Backend Days",
                            "description": "Total backend development days for the module",
                            "type": "number"
                        }
                    },
                    "required": ["module", "features"]
                }
            }
        },
        "required": ["effort_estimation"]
    }
    """
    
    prompt = f"""
        Based on the given software features and subfeatures, estimate effort (in days) for each role:
        
        - **Frontend Development** (UI/UX implementation, client-side functionality)
        - **Backend Development** (Server-side logic, APIs, databases)
        
        The estimation should be **granular**, providing effort at the **subfeature level** while maintaining the module and feature hierarchy.

        Use the following historical context to improve time estimation accuracy:
        
        {time_estimate_context}

        Use the following historical context to improve cost estimation accuracy:
        
        {cost_estimate_context}

        {format_instructions}

        **Guidelines:**
        - Assign **realistic effort estimates** based on standard development practices.
        - For frontend development, consider complexity of UI components, responsiveness, and client-side logic.
        - For backend development, consider data models, API complexity, and business logic.
        - Complex subfeatures (e.g., authentication, API integrations) should have **higher effort estimates**.
        - Simple subfeatures (e.g., UI changes, minor configurations) should have **lower effort estimates**.
        - Ensure all values are in whole or decimal numbers representing effort in **days**.

        Features & Subfeatures:
        {feature_breakdown}

        Provide the output in valid JSON format only, without any additional text.
    """

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
        top_p=0.9,
        stop=["</s>"],
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        # Parse using the Langchain parser
        parsed_output = parser.parse(raw_output)
        return parsed_output.dict()
    except Exception as e:
        print(f"\n❌ Error parsing with Langchain: {e}")
        # Fallback to manual parsing if Langchain parser fails
        try:
            # Try to extract the JSON part from the response
            json_start = raw_output.find('{')
            json_end = raw_output.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = raw_output[json_start:json_end]
                json_output = json.loads(json_str)
                
                # Basic validation of the structure
                if "effort_estimation" not in json_output:
                    raise ValueError("Missing 'effort_estimation' key in the response")
                
                return json_output
            else:
                raise ValueError("Could not find valid JSON in the response")
        except Exception as e2:
            print(f"\n❌ Fallback parsing also failed: {e2}")
            return None

def parse_llm_response(response_text):
    """Original parse function kept for compatibility."""
    try:
        parsed_data = json.loads(response_text)

        if not isinstance(parsed_data, dict) or "effort_estimation" not in parsed_data:
            raise ValueError("Invalid JSON format received from the model.")

        for module in parsed_data["effort_estimation"]:
            if "module" not in module or "features" not in module:
                raise ValueError("Missing required keys in module structure.")

            for feature in module["features"]:
                if "name" not in feature or "subfeatures" not in feature:
                    raise ValueError("Missing required keys in feature structure.")

                for subfeature in feature["subfeatures"]:
                    required_keys = {"name", "frontend_days", "backend_days"}
                    if not required_keys.issubset(subfeature):
                        raise ValueError(f"Subfeature {subfeature.get('name', 'unknown')} is missing required keys.")

        return parsed_data

    except (json.JSONDecodeError, ValueError) as e:
        print(f"\n❌ Error parsing JSON: {e}")
        return None  # Return None to handle it gracefully

def generate_effort_excel(feature_breakdown, output_excel="effort_estimation.xlsx"):
    """Generate effort and cost estimation Excel file with two sheets."""
    
    effort_data = estimate_effort(feature_breakdown)

    # Handle parsing errors
    if not effort_data:
        print("\n⚠️ No valid effort estimation data available. Falling back to original parser.")
        raw_output = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[{"role": "user", "content": f"Parse this JSON and return only valid JSON: {feature_breakdown}"}],
            max_tokens=3000,
            temperature=0.2,
        ).choices[0].message.content.strip()
        
        effort_data = parse_llm_response(raw_output)
        if not effort_data:
            print("\n❌ All parsing attempts failed. Cannot generate Excel file.")
            return
    
    effort_rows = []
    cost_rows = []
    
    for module in effort_data["effort_estimation"]:
        module_name = module["module"]
        for feature in module["features"]:
            feature_name = feature["name"]
            for subfeature in feature.get("subfeatures", []):
                subfeature_name = subfeature["name"]

                # Skip 'testing' subfeature
                if subfeature_name.lower() == "testing":
                    continue

                # Get frontend and backend days directly from the LLM output
                frontend_days = subfeature["frontend_days"]
                backend_days = subfeature["backend_days"]
                
                # Calculate buffers (20% of respective efforts)
                frontend_buffer = frontend_days * 0.2
                backend_buffer = backend_days * 0.2

                # Calculate testing time (15% of respective effort + buffer)
                frontend_testing = (frontend_days + frontend_buffer) * 0.15
                backend_testing = (backend_days + backend_buffer) * 0.15

                # Append effort estimation data with new columns
                effort_rows.append([
                    module_name, feature_name, subfeature_name,
                    frontend_days, frontend_buffer, frontend_testing,
                    backend_days, backend_buffer, backend_testing
                ])

                # Cost calculations for cost sheet
                frontend_cost = frontend_days * pricing_model["Mid"]
                backend_cost = backend_days * pricing_model["Senior"]

                # Append cost estimation data
                cost_rows.append([
                    module_name, feature_name, subfeature_name,
                    frontend_days, frontend_buffer, frontend_cost,
                    backend_days, backend_buffer, backend_cost,
                ])

    # Convert to DataFrames with new column names
    effort_df = pd.DataFrame(effort_rows, columns=[
        "Module", "Feature", "Subfeature", 
        "Frontend Effort", "Frontend Buffer", "Frontend Testing",
        "Backend Effort", "Backend Buffer", "Backend Testing",
    ])
    
    cost_df = pd.DataFrame(cost_rows, columns=[
        "Module", "Feature", "Subfeature", 
        "Frontend Days", "Frontend Buffer", "Frontend Cost",
        "Backend Days", "Backend Buffer", "Backend Cost"
    ])

    # Calculate totals
    total_effort_row = ["Total", "", "Total"] + effort_df.iloc[:, 3:].sum().tolist()
    total_cost_row = ["Total", "", "Total"] + cost_df.iloc[:, 3:].sum().tolist()

    # Append units row
    unit_effort_row = ["", "", "Units", "days", "days", "days", "days", "days", "days"]    
    # Make sure this has exactly 11 elements to match the 11 columns in cost_df
    unit_cost_row = ["", "", "Units", "days", "days", "INR", "days", "days", "INR"]

    # Append total and unit rows
    effort_df.loc[len(effort_df)] = total_effort_row
    effort_df.loc[len(effort_df)] = unit_effort_row

    cost_df.loc[len(cost_df)] = total_cost_row
    cost_df.loc[len(cost_df)] = unit_cost_row

    # Save to Excel with two sheets
    with pd.ExcelWriter(output_excel, engine="xlsxwriter") as writer:
        effort_df.to_excel(writer, sheet_name="Effort Estimation", index=False)
        cost_df.to_excel(writer, sheet_name="Cost Estimation", index=False)

    print(f"\n✅ Effort estimation Excel file generated: {output_excel}")

if __name__ == "__main__":
    # Example JSON feature breakdown (same as your original example)
    feature_breakdown = {}

    # Generate Excel file
    generate_effort_excel(json.dumps(feature_breakdown))