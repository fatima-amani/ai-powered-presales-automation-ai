import os
import json
import time
from together import Together
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

def extract_json(response_text):
    """Extracts JSON content from the response text."""
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_data = response_text[json_start:json_end]
        return json.loads(json_data)  # Ensure it's valid JSON
    except (ValueError, json.JSONDecodeError):
        return None  # Invalid JSON

def generate_ui_template(feature_breakdown, max_attempts=3, delay=2):
    """Generates a JSON-based UI wireframe template with retry logic for JSON validation."""
    
    prompt = f"""
        Given the following feature breakdown, generate a JSON-based UI wireframe template 
        where each module contains screens, layouts, and components. Ensure the output is strictly valid JSON.

        Feature Breakdown:
        {json.dumps(feature_breakdown, indent=2)}

        Expected JSON Output:
        - Each module has screens (features).
        - Each screen has a "layout" (grid, list, column).
        - Each screen has "components" with "type" and "position" (top, left, right, center, bottom).
        - Output must be STRICTLY valid JSON without any extra text.

        Example Output:
        {{"Football Club Website": {{"Homepage": {{"layout": "grid", "components": [
            {{"type": "Global Navigation", "position": "top"}},
            {{"type": "Header", "position": "top"}},
            {{"type": "Footer", "position": "bottom"}},
            {{"type": "Search", "position": "top"}},
            {{"type": "Featured Content", "position": "center"}}
        ]}}}}}}
    """

    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}...")

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

        ui_json = response.choices[0].message.content.strip()

        extracted_json = extract_json(ui_json)
        
        if extracted_json:
            return extracted_json  # Return if valid JSON
        
        print("Invalid JSON received. Retrying...")
        time.sleep(delay)  # Wait before retrying

    return {"error": "Failed to generate valid JSON after multiple attempts"}

# Example Input (Feature Breakdown)
feature_breakdown = {
    "feature_breakdown": [
        {
            "module": "User Authentication & Onboarding",
            "features": [
                {
                    "name": "Secure signup, login, and session management",
                    "description": "Allows users to securely sign up, log in, and manage their sessions using OAuth2, email/password.",
                    "subfeatures": []
                },
                {
                    "name": "User dashboard for managing database connections",
                    "description": "Provides a user interface for managing database connections.",
                    "subfeatures": []
                }
            ]
        },
        {
            "module": "Database Connectivity & Schema Analysis",
            "features": [
                {
                    "name": "Support for SQL and NoSQL databases",
                    "description": "Allows the platform to connect and analyze SQL and NoSQL databases.",
                    "subfeatures": []
                },
                {
                    "name": "Automatic parsing of database schema",
                    "description": "Analyzes the database schema to understand its structure, relationships, and indexes.",
                    "subfeatures": []
                }
            ]
        },
        {
            "module": "Use Case Generation & Approval",
            "features": [
                {
                    "name": "AI-driven identification of admin panel use cases",
                    "description": "Uses AI to identify common admin operations based on the database schema.",
                    "subfeatures": []
                },
                {
                    "name": "User interface for reviewing, modifying, and approving suggested use cases",
                    "description": "Provides a user interface for reviewing, modifying, and approving the suggested use cases.",
                    "subfeatures": []
                }
            ]
        },
        {
            "module": "Admin Panel UI Generation",
            "features": [
                {
                    "name": "Dynamic UI creation for CRUD operations",
                    "description": "Generates a dynamic user interface for performing CRUD operations based on approved use cases.",
                    "subfeatures": [
                        {
                            "name": "CRUD operations for tables",
                            "description": "Allows users to create, read, update, and delete data in tables."
                        },
                        {
                            "name": "CRUD operations for relationships",
                            "description": "Allows users to manage relationships between tables."
                        },
                        {
                            "name": "CRUD operations for indexes",
                            "description": "Allows users to manage indexes in the database."
                        }
                    ]
                }
            ]
        },
        {
            "module": "Security & Access Control",
            "features": [
                {
                    "name": "Role-based access control",
                    "description": "Enforces access control based on user roles.",
                    "subfeatures": []
                },
                {
                    "name": "Data encryption",
                    "description": "Encrypts sensitive data during transmission and storage.",
                    "subfeatures": []
                },
                {
                    "name": "Secure API communication",
                    "description": "Ensures secure communication between APIs.",
                    "subfeatures": []
                }
            ]
        },
        {
            "module": "Scalability & Performance Optimization",
            "features": [
                {
                    "name": "Optimized query execution",
                    "description": "Improves the performance of query execution for handling large datasets efficiently.",
                    "subfeatures": []
                },
                {
                    "name": "Support for concurrent users and multiple database connections",
                    "description": "Allows the platform to handle multiple users and database connections simultaneously.",
                    "subfeatures": []
                }
            ]
        }
    ]
}

# Generate UI Wireframe
ui_template = generate_ui_template(feature_breakdown)
print(json.dumps(ui_template, indent=2))
