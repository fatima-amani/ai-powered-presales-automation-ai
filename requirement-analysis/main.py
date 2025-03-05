from dotenv import load_dotenv
from together import Together
import os
import json

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

    return response.choices[0].message.content  # Extract text from response

# Manually enter text
manual_text = input("Enter software requirements text: ")

# Extract and print results
result = extract_requirements(manual_text)
print("\nExtracted Requirements:\n", result)
