import os
import json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
from together import Together
import networkx as nx
import json
import re

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

def clean_json_response(response_text):
    """
    Cleans AI response by removing markdown formatting (json) and extra text.
    """
    try:
        # Remove Markdown code block indicators (json ... )
        if "json" in response_text:
            response_text = response_text.split("json")[1].split("```")[0].strip()
        return json.loads(response_text)  # Parse clean JSON
    except (json.JSONDecodeError, IndexError) as e:
        # logging.error(f"Error parsing AI JSON response: {e}")
        return {"error": str(e), "raw_output": response_text}

def generate_architecture_diagram(requirements_json, tech_stack_json):
    prompt = f"""
        You are an expert software architect. Given the following project requirements and recommended tech stack, generate a structured JSON representation of a system architecture graph.

        Requirements:
        {json.dumps(requirements_json, indent=2)}

        Tech Stack:
        {json.dumps(tech_stack_json, indent=2)}

        The JSON output must strictly follow this format:
        {{
            "nodes": [
                {{"id": "Frontend", "attributes": {{"type": "service", "technology": "React.js"}}}},
                {{"id": "Backend", "attributes": {{"type": "service", "technology": "Node.js"}}}},
                {{"id": "Database", "attributes": {{"type": "storage", "technology": "PostgreSQL"}}}}
            ],
            "edges": [
                {{"source": "Frontend", "target": "Backend", "attributes": {{"protocol": "REST API"}}}},
                {{"source": "Backend", "target": "Database", "attributes": {{"protocol": "SQL Queries"}}}}
            ]
        }}

        Return only valid JSON without any additional text.
    """

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
        top_p=0.8,
        top_k=50,
        repetition_penalty=1.1,
        stop=["</s>"]
    )

    raw_output = response.choices[0].message.content.strip()
    graph_data = clean_json_response(raw_output)  # Clean & parse JSON

    if "error" in graph_data:
        return json.dumps(graph_data, indent=4)  # Return error info

    # Convert JSON structure to NetworkX graph
    G = nx.DiGraph()

    for node in graph_data.get("nodes", []):
        G.add_node(node["id"], **node["attributes"])

    for edge in graph_data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], **edge["attributes"])

    # Convert NetworkX graph to JSON
    graph_json = {
        "nodes": [{"id": n, "attributes": G.nodes[n]} for n in G.nodes],
        "edges": [{"source": u, "target": v, "attributes": G[u][v]} for u, v in G.edges]
    }

    return graph_json

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
    
    # print("\nGenerated Architecture Diagram:")
    # print(architecture_diagram)
