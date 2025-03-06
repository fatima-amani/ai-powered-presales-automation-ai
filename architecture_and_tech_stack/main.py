import os
import json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
from together import Together

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

def get_tech_stack_recommendation(requirements_json):
    prompt = f"""
        You are an AI expert in software architecture and technology stacks. Given the following project requirements in JSON format, recommend a suitable tech stack in JSON format.

        Requirements:
        {json.dumps(requirements_json, indent=2)}

        Provide output in the following format:
        {{
            "frontend": [
                {{
                    "name": "Technology Name",
                    "description": "Reason for use"
                }}
            ],
            "backend": [
                {{
                    "name": "Technology Name",
                    "description": "Reason for use"
                }}
            ],
            "database": [
                {{
                    "name": "Technology Name",
                    "description": "Reason for use"
                }}
            ],
            "API_integrations": [
                {{
                    "name": "API Name",
                    "description": "Reason for use"
                }}
            ],
            "others": [
                {{
                    "name": "Technology/Tool Name",
                    "description": "Reason for use"
                }}
            ]
        }}

        Ensure the output is in valid JSON format only, without any additional text.
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
        ResponseSchema(name="frontend", description="Recommended frontend technologies"),
        ResponseSchema(name="backend", description="Recommended backend technologies"),
        ResponseSchema(name="database", description="Recommended database technologies"),
        ResponseSchema(name="API_integrations", description="List of third-party APIs, if applicable"),
        ResponseSchema(name="others", description="Other relevant tools or technologies")
    ]

    
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    try:
        parsed_output = parser.parse(raw_output)
    except Exception as e:
        print(f"Error: {e}. Returning raw output.")
        return raw_output
    
    return json.dumps(parsed_output,indent=4)

# if __name__ == "__main__":
#     requirements = { 
#         "functional_requirements": [
#             "Website Scope of Work",
#             "Components",
#             "Content types supported by these templates and components",
#             "Dual language functionality",
#             "News",
#             "Video services",
#             "Teams Listing",
#             "Polls and Quizzes",
#             "Fixtures",
#             "Results",
#             "Match Centre and Live Match Stats",
#             "Data provider integration",
#             "Additional Global Functionality and Components",
#             "iOS and Android Apps Scope of Work",
#             "Dual language functionality",
#             "Latest Tab",
#             "News",
#             "Polls and Quizzes",
#             "Ads/Marketing",
#             "Matches Tab",
#             "League Tables Full List",
#             "Live Scores Full List",
#             "Squad Full List (including Player Profiles)",
#             "Player Profile",
#             "Match Centre",
#             "Club TV tab",
#             "More tab",
#             "Account",
#             "Settings"
#         ],
#         "non_functional_requirements": [
#             "Performance: The website and apps should be optimized for fast loading times and smooth user experience.",
#             "Security: The website and apps should follow best practices for data security and privacy."
#         ],
#     }

#     recommendations = get_tech_stack_recommendation(requirements)
#     print(recommendations)