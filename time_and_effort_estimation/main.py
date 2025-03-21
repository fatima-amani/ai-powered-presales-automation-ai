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

# Updated pricing model (hourly rates in INR)
pricing_model = {
    "Frontend": 15,
    "Backend": 16,
    "Testing": 12
}

# Define Pydantic models for structured output parsing
class Subfeature(BaseModel):
    name: str = Field(description="Name of the subfeature")
    frontend_days: float = Field(description="Number of days required for frontend development")
    backend_days: float = Field(description="Number of days required for backend development")

class Feature(BaseModel):
    name: str = Field(description="Name of the feature")
    subfeatures: Optional[List[Subfeature]] = Field(default_factory=list, description="List of subfeatures with effort estimations")
    frontend_days: Optional[float] = Field(None, description="Direct frontend days if no subfeatures")
    backend_days: Optional[float] = Field(None, description="Direct backend days if no subfeatures")

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
        with open("time_estimate_context.txt", "r", encoding="utf-8") as file:
            time_estimate_context = file.read()
    except FileNotFoundError:
        # Fallback if file doesn't exist
        time_estimate_context = "No historical context available."
        print("\n⚠️ time_estimate_context.txt file not found. Proceeding without historical context.")
    
    try:
        with open("cost_estimate_context.txt", "r", encoding="utf-8") as file:
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
        
        The estimation must follow this EXACT structure:
        - Each module has a name and list of features
        - Each feature has a name and list of subfeatures
        - If a feature has direct effort values, still create a single subfeature with the same name
        
        {format_instructions}
        
        # IMPORTANT: Every feature MUST have a subfeatures array, even if it only contains one item.
        # Do NOT omit the subfeatures field for any feature.

        Features & Subfeatures:
        {feature_breakdown}

        Provide the output in valid JSON format only.
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
    
def manual_parse_effort(raw_output):
    """Last resort manual parsing of effort data with structural fixes."""
    try:
        # Preprocess to fix common issues
        json_str = preprocess_llm_response(raw_output)
        data = json.loads(json_str)
        
        # Check and fix module structure
        if "effort_estimation" in data:
            for i, module in enumerate(data["effort_estimation"]):
                # Ensure features exists
                if "features" not in module:
                    module["features"] = []
                
                # Add missing subfeatures
                for j, feature in enumerate(module["features"]):
                    if "subfeatures" not in feature:
                        if "frontend_days" in feature:
                            # Create subfeature from feature itself
                            feature["subfeatures"] = [{
                                "name": feature.get("name", "Unknown"),
                                "frontend_days": feature.get("frontend_days", 0),
                                "backend_days": feature.get("backend_days", 0)
                            }]
        
        return data
    except Exception as e:
        print(f"Manual parsing failed: {e}")
        return None
    
def preprocess_llm_response(raw_output):
    """Clean and fix common JSON formatting issues from LLM responses."""
    # Try to extract just the JSON part
    json_start = raw_output.find('{')
    json_end = raw_output.rfind('}') + 1
    
    if json_start >= 0 and json_end > json_start:
        json_str = raw_output[json_start:json_end]
        
        # Fix for features without subfeatures
        import re
        pattern = r'"features":\s*\[\s*{\s*"name":\s*"([^"]+)",\s*"frontend_days":'
        replacement = r'"features": [{"name": "\1", "subfeatures": [{"name": "\1", "frontend_days":'
        json_str = re.sub(pattern, replacement, json_str)
        
        # Fix for unclosed arrays or missing commas
        json_str = json_str.replace('"}]"}', '"}]}')
        json_str = json_str.replace('"Testing"}', '"Testing"}]')
        
        return json_str
    return raw_output

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
    
    # For collecting data for cost summary
    frontend_total_days = 0
    backend_total_days = 0
    testing_total_days = 0
    
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
                frontend_buffer = round(frontend_days * 0.2,2)
                backend_buffer = round(backend_days * 0.2,2)

                # Calculate testing time (15% of respective effort + buffer)
                frontend_testing = round((frontend_days + frontend_buffer) * 0.15,2)
                backend_testing = round((backend_days + backend_buffer) * 0.15,2)

                # Append effort estimation data with new columns
                effort_rows.append([
                    module_name, feature_name, subfeature_name,
                    frontend_days, frontend_buffer, frontend_testing,
                    backend_days, backend_buffer, backend_testing
                ])

                # Update total days for cost summary
                frontend_total_days += round((frontend_days + frontend_buffer) * 1.1,2)
                backend_total_days += round((backend_days + backend_buffer) * 1.1,2)
                testing_total_days += round(frontend_testing * 1.1, 2)  # Using frontend testing as requested

                # Original cost calculations (kept for compatibility)
                frontend_cost = round(frontend_days * pricing_model["Frontend"] * 8,2)
                backend_cost = round(backend_days * pricing_model["Backend"] * 8,2)

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
    unit_cost_row = ["", "", "Units", "days", "days", "INR", "days", "days", "INR"]

    # Append total and unit rows
    effort_df.loc[len(effort_df)] = total_effort_row
    effort_df.loc[len(effort_df)] = unit_effort_row

    cost_df.loc[len(cost_df)] = total_cost_row
    cost_df.loc[len(cost_df)] = unit_cost_row

    # Round numerical values to 2 decimal places
    # effort_df.iloc[:, 3:] = effort_df.iloc[:, 3:].round(2)
    # cost_df.iloc[:, 1:3] = cost_df.iloc[:, 1:3].round(2)

    # Create new cost summary format as per the screenshot
    cost_summary_data = [
        ["Frontend", frontend_total_days, pricing_model["Frontend"], round(frontend_total_days * 8 * pricing_model["Frontend"],2)],
        ["Backend", backend_total_days, pricing_model["Backend"], round(backend_total_days * 8 * pricing_model["Backend"],2)],
        ["Testing", testing_total_days, pricing_model["Testing"], round(testing_total_days * 8 * pricing_model["Testing"],2)]
    ]
    
    # Calculate total cost
    total_cost = sum(row[3] for row in cost_summary_data)
    cost_summary_data.append(["Total", "", "", total_cost])
    
    # Create DataFrame for cost summary
    cost_summary_df = pd.DataFrame(cost_summary_data, columns=[
        "Item", "Effort in Days", "Rate per hour (IN INR)", "Pricing"
    ])
    
    # Format the pricing column with Indian Rupee symbol
    cost_summary_df["Pricing"] = cost_summary_df["Pricing"].apply(lambda x: f"₹{x:,.2f}" if isinstance(x, (int, float)) else x)
    
    # Save to Excel with sheets
    with pd.ExcelWriter(output_excel, engine="xlsxwriter") as writer:
        effort_df.to_excel(writer, sheet_name="Effort Estimation", index=False)
        # cost_df.to_excel(writer, sheet_name="Cost Estimation", index=False)
        cost_summary_df.to_excel(writer, sheet_name="Cost Summary", index=False)
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets["Cost Summary"]
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # Apply formats to headers
        for col_num, value in enumerate(cost_summary_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-fit columns
        for i, col in enumerate(cost_summary_df.columns):
            column_width = max(cost_summary_df[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(i, i, column_width + 2)

    print(f"\n✅ Cost estimation Excel file generated with new Cost Summary sheet: {output_excel}")

if __name__ == "__main__":
    # Example JSON feature breakdown (same as your original example)
    feature_breakdown = {}

    # Generate Excel file
    generate_effort_excel(json.dumps(feature_breakdown))