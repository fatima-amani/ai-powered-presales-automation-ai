import os
import json
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
from together import Together
import networkx as nx
import re

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

def get_user_persona(requirement_json: str):
    """
    Analyze requirements and generate detailed user personas with their workflows.
    
    Args:
        requirement_json (str): JSON string containing requirements analysis
        
    Returns:
        str: JSON string containing user personas and their workflows
    """
    
    prompt = f"""
    Analyze the following software requirements and create detailed user personas with their workflows.
    For each identified user type, provide their characteristics, goals, pain points, and typical workflow scenarios.
    
    Requirements Data:
    {requirement_json}
    
    Generate user personas in this exact JSON format:
    {{
        "personas": [
            {{
                "type": "Persona type/role",
                "description": "Detailed description of the user type",
                "workflows": [
                    {{
                        "name": "Workflow name",
                        "description": "Detailed description of the workflow",
                        "steps": [
                            {{
                                "step": 1,
                                "action": "What the user does",
                                "system_response": "How the system responds",
                                "features_used": ["Feature 1", "Feature 2"]
                            }}
                        ],
                        "success_criteria": ["Criterion 1", "Criterion 2"]
                    }}
                ]
            }}
        ]
    }}

    Provide the output in valid JSON format only, without any additional text.
    """

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["</s>"],
    )

    try:
        # Extract the JSON string from the response
        raw_output = response.choices[0].message.content
        # Parse and re-serialize to ensure valid JSON
        parsed_json = json.loads(raw_output)
        return json.dumps(parsed_json, indent=4)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Failed to parse LLM response: {str(e)}"})
    


def categorize_features(requirement_json: str):
    
    """
    Categorize features into must-have, nice-to-have, and future enhancements based on requirements.
    
    Args:
        requirement_json (str): JSON string containing requirements analysis
        
    Returns:
        str: JSON string containing categorized features with priorities
    """
    
    prompt = f"""
    Analyze the following software requirements and categorize features into priority levels.
    Consider business impact, technical dependencies, and user value when categorizing.
    
    Requirements Data:
    {requirement_json}
    
    Generate a prioritized feature categorization in this exact JSON format:
    {{
        "feature_categories": {{
            "must_have": [
                {{
                    "feature": "Feature name",
                    "description": "Feature description",
                    "rationale": "Why this is essential for MVP",
                    "business_impact": "High/Medium/Low",
                }}
            ],
            "nice_to_have": [
                {{
                    "feature": "Feature name",
                    "description": "Feature description",
                    "potential_value": "Description of added value",
                }}
            ],
            "future_enhancements": [
                {{
                    "feature": "Feature name",
                    "description": "Feature description",
                    "strategic_value": "Long-term benefit description",
                }}
            ]
        }}
    }}

    Provide the output in valid JSON format only, without any additional text.
    """

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["</s>"],
    )

    try:
        raw_output = response.choices[0].message.content
        parsed_json = json.loads(raw_output)
        return json.dumps(parsed_json, indent=4)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Failed to parse LLM response: {str(e)}"})


if __name__ == "__main__":
    # Sample user requirement JSON
    sample_requirement_json = r'''{"message":"Requirements already extracted","functionalRequirement":["AI-Powered Proficiency Assessment","Adaptive Lesson Planning","Conversational AI for Real-Life Dialogues","Spaced Repetition & Revision Scheduling"],"nonFunctionalRequirement":["Successful deployment of the MVP with all core AI-driven functionalities","AI adjusts lesson difficulty dynamically based on real-time user performance","Conversational AI engages naturally and provides contextual corrections","Speech recognition achieves at least 85% phonetic accuracy","Spaced repetition module improves recall and learning efficiency","Scalability and efficiency of AI-powered adaptive learning engine","Security compliance and data protection measures","Accuracy of AI-generated language explanations vs. human instructors"],"featureBreakdown":[{"component":"AI-Powered Proficiency Assessment","description":"AI evaluates the user's proficiency level via a diagnostic test at onboarding and ongoing performance analysis from lesson interactions using speech, text, and grammar evaluation. The frontend displays the UI for test-taking and proficiency, the backend stores user proficiency levels and learning history, and the AI Component uses NLP + ML models for proficiency detection and scoring."},{"component":"Adaptive Lesson Planning","description":"Provides personalized lesson plans targeting weak areas. AI generates tailored daily lessons based on user's availability and learning goals. Dynamically adjusts difficulty level based on real-time performance. The frontend displays adaptive lessons in an interactive format, the backend manages lesson data and user progression, and the AI Component uses reinforcement learning for content difficulty optimization."},{"component":"Conversational AI for Real-Life Dialogues","description":"AI simulates real-world conversations for practical learning. The AI can understand and correct grammar mistakes, adapt responses based on the user's proficiency, engage in natural conversations to improve fluency, analyze pronunciation and give real-time feedback, detect phonetic mistakes and provide corrections, and grade pronunciation accuracy and suggest improvements. The frontend is a chat-based conversational UI with voice and text support, the backend processes and stores conversation data, and the AI Component uses LLMs (GPT-4 / fine-tuned models) for realistic dialogue simulation and Whisper API / DeepSpeech for speech-to-text processing."},{"component":"Spaced Repetition & Revision Scheduling","description":"AI suggests revision schedules based on spaced repetition techniques. Users receive reminders for timely lesson reviews. Generates AI-powered summaries of past lessons for quick revision. The frontend displays recommended revision schedules and lesson summaries, the backend logs past lessons and user progress, and the AI Component uses spaced repetition algorithms (SM2) for retention optimization."}]}'''
    
    # Call the function and print the result
    output = categorize_features(sample_requirement_json)
    print(output)