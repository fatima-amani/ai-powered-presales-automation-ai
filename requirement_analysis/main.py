from dotenv import load_dotenv
from together import Together
import os
import json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

def extract_requirements(text):
    prompt = f"""
        Extract the following from the given software requirements document:
        1. **Functional Requirements**: Clearly list all functional aspects.
        2. **Non-Functional Requirements**: List performance, security, and other system constraints.
        3. **Feature Breakdown**: Break down features into components.

        Input Text:
        {text}

        Provide the output in JSON format with keys: "functional_requirements", "non_functional_requirements", and "feature_breakdown".
        """

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,  # Adjust token limit
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

# Manually enter text
manual_text = "Enter software requirements text: Universities need a way to manage courses, students, and faculty better. The system should make things easy for students and teachers. Students should be able to sign up for courses without hassle. Teachers need to upload lectures, assignments, and quizzes. Students also need a way to turn in their assignments online, and grades should be handled smoothly. Notifications for deadlines should be automatic. There should also be a forum where students and instructors can discuss coursework."

# Extract and print results
result = extract_requirements(manual_text)
print("\nExtracted Requirements:")
print(result)