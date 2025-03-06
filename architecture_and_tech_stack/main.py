import os
import json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
from together import Together
import networkx as nx

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
        max_tokens=1024,
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
    
    return json.dumps(parsed_output, indent=4)

def generate_architecture_diagram(requirements_json, tech_stack_json):
    if isinstance(tech_stack_json, str):
        tech_stack = json.loads(tech_stack_json)
    else:
        tech_stack = tech_stack_json

    G = nx.DiGraph()
    G.add_node("System", type="root")
    G.add_node("Frontend", type="layer")
    G.add_node("Backend", type="layer")
    G.add_node("Database", type="layer")

    G.add_edge("System", "Frontend")
    G.add_edge("System", "Backend")
    G.add_edge("Backend", "Database")

    for tech in tech_stack.get("frontend", []):
        G.add_node(tech["name"], type="frontend")
        G.add_edge("Frontend", tech["name"])

    for tech in tech_stack.get("backend", []):
        G.add_node(tech["name"], type="backend")
        G.add_edge("Backend", tech["name"])

    for tech in tech_stack.get("database", []):
        G.add_node(tech["name"], type="database")
        G.add_edge("Database", tech["name"])

    mermaid_format = "graph TD;\n"
    for edge in G.edges:
        mermaid_format += f"    {edge[0]} --> {edge[1]}\n"

    return json.dumps({"diagram": mermaid_format}, indent=4)

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
#     architecture_diagram = generate_architecture_diagram(requirements, recommendations)
    
#     print("Tech Stack Recommendations:")
#     print(recommendations)
    
#     print("\nGenerated Architecture Diagram:")
#     print(architecture_diagram)
