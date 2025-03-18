import json
import time
import re
from dotenv import load_dotenv
from together import Together
import os
import requests
from extract_from_doc import extract_text_from_doc, extract_text_from_pdf

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

def extract_json_from_text(text):
    """Extracts and validates the JSON part from a given text output."""
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_text = match.group(0)  # Extract matched JSON part
            parsed_json = json.loads(json_text)  # Validate JSON structure

            # Ensure every feature has 'subfeatures' explicitly set
            for module in parsed_json.get("feature_breakdown", []):
                for feature in module.get("features", []):
                    if "subfeatures" not in feature:
                        feature["subfeatures"] = []  # Ensure empty list if missing

            return json.dumps(parsed_json, indent=4)  # Return formatted JSON
        else:
            raise ValueError("No valid JSON found in the text.")
    except json.JSONDecodeError:
        raise ValueError("Extracted text is not valid JSON.")

def extract_requirements(requirement_text: str, url: str, tech_stack, platforms):
    """Extract requirements from a given requirement text and a Cloudinary PDF/DOCX URL."""

    if url.endswith(".pdf"):
        file_type = "pdf"
    elif url.endswith(".docx"):
        file_type = "docx"
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    
    tech_stack = tech_stack if tech_stack else "No preference"
    platforms = platforms if platforms else "Any"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

    file_path = f"temp.{file_type}"
    with open(file_path, "wb") as f:
        f.write(response.content)

    extracted_text = extract_text_from_pdf(file_path) if file_type == "pdf" else extract_text_from_doc(file_path)

    if not extracted_text:
        return {"error": "Failed to extract text from the document"}

    # Append requirement_text to extracted document text
    combined_text = requirement_text + "\n\n" + extracted_text + "\n\n" + "Tech Stack preferences are: " + tech_stack + "\n\n" + "Platforms required: " + platforms

    return extract_requirements_llm(combined_text)

def extract_requirements_llm(text, max_retries=3, delay=2):
    """Extract functional and non-functional requirements from software requirements text with retry logic."""

    attempt = 0
    while attempt < max_retries:
        prompt = f"""
        Extract the following from the given software requirements document:

        1. **Functional Requirements**: Clearly list all functional aspects.
        2. **Non-Functional Requirements**: List performance, security, and other system constraints.
        3. **Feature Breakdown**: Break down features into components, descriptions, and intelligently inferred subfeatures.

        Each **feature and subfeature must include a clear description** explaining what it does and why it is needed.

        **Ensure the output strictly follows this JSON format:**  

        {{
            "functional_requirements": ["Requirement 1", "Requirement 2", ...],
            "non_functional_requirements": ["Requirement 1", "Requirement 2", ...],
            "feature_breakdown": [
                {{
                    "module": "Module Name",
                    "features": [
                        {{
                            "name": "Feature Name",
                            "description": "Brief explanation of what this feature does and why it is necessary.",
                            "subfeatures": [
                                {{
                                    "name": "Subfeature Name",
                                    "description": "Detailed description of what this subfeature does."
                                }}
                            ] or []
                        }}
                    ]
                }}
            ]
        }}

        **Important:**  
        - Every **feature must contain the `subfeatures` key**.  
        - If a feature has no subfeatures, set `"subfeatures": []`.  
        - If a feature requires subfeatures, list at least **three relevant ones**.  

        Input Text:
        {text}

        Provide the output in valid JSON format only, without any additional text.
        """

        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.77,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["</s>"],
        )

        raw_output = response.choices[0].message.content

        try:
            # Extract only the valid JSON part and enforce structure
            clean_json = extract_json_from_text(raw_output)
            return clean_json

        except ValueError as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            attempt += 1
            time.sleep(delay)

    print("Max retries reached. Returning raw output.")
    return raw_output

if __name__ == "__main__":
    requirement_text = "Specify the key requirements for the system."
    url = "https://res.cloudinary.com/depfpw7ym/image/upload/v1742037301/pre_sales_automation_dev/fog6ak0b56aaffwosyku.pdf"  # Replace with a valid Cloudinary URL
    
    processed_requirements = extract_requirements(requirement_text, url)
    
    print(processed_requirements)