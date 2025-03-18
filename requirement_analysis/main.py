from dotenv import load_dotenv
from together import Together
import os
import json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import requests
from .extract_from_doc import extract_text_from_doc, extract_text_from_pdf

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

# Function to process requirement text and document
def extract_requirements(requirement_text: str, url: str, tech_stack, platforms):
    """Extract requirements from a given requirement text and a Cloudinary PDF/DOCX URL."""

    # Determine the file type from the URL
    if url.endswith(".pdf"):
        file_type = "pdf"
    elif url.endswith(".docx"):
        file_type = "docx"
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    
    tech_stack = tech_stack if tech_stack else "No preference"
    platforms = platforms if platforms else "Any"

    # Download the file from Cloudinary
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed request
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

    # Save the downloaded file temporarily
    file_path = f"temp.{file_type}"
    with open(file_path, "wb") as f:
        f.write(response.content)

    # Extract text based on file type
    extracted_text = None
    if file_type == "pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        extracted_text = extract_text_from_doc(file_path)

    if not extracted_text:
        return {"error": "Failed to extract text from the document"}

    # Append requirement_text to extracted document text
    combined_text = requirement_text + "\n\n" + extracted_text + "\n\n" + "Tech Stack preferences are: " + tech_stack + "\n\n" + "Platforms required: " + platforms

    # Send the text to the LLM function
    processed_requirements = extract_requirements_llm(combined_text)

    return processed_requirements

def extract_requirements_llm(text):
    """Extract functional and non-functional requirements from software requirements text."""

    prompt = f"""
        Extract the following from the given software requirements document:
        
        1. **Functional Requirements**: Clearly list all functional aspects.
        2. **Non-Functional Requirements**: List performance, security, and other system constraints.
        3. **Feature Breakdown**: Break down features into components, descriptions, and intelligently inferred subfeatures.

        The AI must **analyze each feature’s description** and determine **subfeatures** that are logically required for implementation.
        These subfeatures should:
        - Represent smaller tasks or functionalities necessary for the feature to be fully functional.
        - Be based on standard best practices, common workflows, and implicit dependencies.
        - Be relevant to the given context and technical feasibility.

        Each **feature and subfeature must include a clear description** explaining what it does and why it is needed.

        Ensure the output strictly follows this JSON format:

        {{
            "functional_requirements": [
                "Requirement 1",
                "Requirement 2",
                ...
            ],
            "non_functional_requirements": [
                "Requirement 1",
                "Requirement 2",
                ...
            ],
            "feature_breakdown": [
                {{
                    "module": "Module Name",
                    "features": [
                        {{
                            "name": "Feature Name",
                            "description": "Brief but clear explanation of what this feature does and why it is necessary.",
                            "subfeatures": [
                                {{
                                    "name": "Subfeature Name",
                                    "description": "Detailed description of what this subfeature does and how it supports the feature."
                                }},
                                ...
                            ]
                        }},
                        ...
                    ]
                }}
            ]
        }}

        When generating subfeatures:
        - If a feature involves **user authentication**, include subfeatures like "Password Encryption", "Multi-Factor Authentication", or "Session Management".
        - If a feature involves **payments**, include subfeatures like "Payment Validation", "Transaction Logging", or "Refund Handling".
        - If a feature is related to **reporting**, consider subfeatures like "Export to PDF", "Graphical Summary", or "Data Filters".
        - If a feature involves **real-time updates**, include subfeatures like "WebSocket Integration", "Push Notifications", or "Live Data Sync".

        **Think like a software architect** when breaking down features into subfeatures.

        📌 **Every feature and subfeature must have a meaningful description**. Do not leave any descriptions empty.

        Input Text:
        {text}

        Provide the output in valid JSON format only, without any additional text.
        """


    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,  # Adjust token limit
        temperature=0.77,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["</s>"],
    )
    
    raw_output = response.choices[0].message.content  # Extract text from response
    
    # Define response schema
    response_schemas = [
        ResponseSchema(name="functional_requirements", description="List of functional requirements"),
        ResponseSchema(name="non_functional_requirements", description="List of non-functional requirements"),
        ResponseSchema(name="feature_breakdown", description="Breakdown of features into components")
    ]
    
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    try:
        parsed_output = parser.parse(raw_output)
    except Exception as e:
        print(f"Error: {e}. Returning raw output.")
        return raw_output

    return json.dumps(parsed_output,indent=4)


if __name__ == "__main__":
    requirement_text = "Specify the key requirements for the system."
    url = "https://res.cloudinary.com/depfpw7ym/image/upload/v1741325185/pre_sales_automation_dev/xultx0enrt8bj0wvpour.pdf"  # Replace with a valid Cloudinary URL
    
    processed_requirements = extract_requirements(requirement_text, url)
    
    print(processed_requirements)  # Ensure the output is printed