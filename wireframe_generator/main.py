import os
import re
import json
import time
from together import Together
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

def generate_wireframe(feature_breakdown, max_retries=3):
    prompt = f"""
        Based on the following feature breakdown, generate a JSON structure for a wireframe.

        Feature Breakdown:
        {json.dumps(feature_breakdown, indent=2)}

        The output should be a JSON object with "pages", each containing "name" and "elements". Each element should have:
        - "type" (e.g., textbox, button, header, chart)
        - "label" (a user-friendly name)
        - "position" with "x" and "y" coordinates
        - Optional size attributes like width and height if relevant.

        Return only valid JSON with no explanations or additional text.

        Example JSON format:
        {{
        "pages": [
            {{
            "name": "Login Page",
            "elements": [
                {{
                "type": "textbox",
                "label": "Username",
                "position": {{ "x": 50, "y": 100 }}
                }},
                {{
                "type": "textbox",
                "label": "Password",
                "position": {{ "x": 50, "y": 150 }}
                }},
                {{
                "type": "button",
                "label": "Login",
                "position": {{ "x": 50, "y": 200 }}
                }}
            ]
            }}
        ]
        }}
    """

    attempt = 0
    while attempt < max_retries:
        try:
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

            llm_output = response.choices[0].message.content

            # Extract only the JSON using regex
            json_match = re.search(r"\{[\s\S]*\}", llm_output)
            if json_match:
                wireframe_json = json_match.group(0)
                return json.loads(wireframe_json)  # Convert to dict

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Attempt {attempt + 1}: Invalid response from LLM, retrying... ({e})")
        
        attempt += 1
        time.sleep(2)  # Small delay before retrying

    raise ValueError("Failed to generate valid wireframe JSON after 3 attempts.")

# Example Input (Feature Breakdown)
feature_breakdown = {
    "feature_breakdown": [
        {
            "module": "Website",
            "features": [
                {
                    "name": "Homepage",
                    "description": "Displays the main landing page of the website",
                    "subfeatures": []
                },
                {
                    "name": "Match Fixtures",
                    "description": "Lists upcoming or currently in play fixtures",
                    "subfeatures": [
                        {
                            "name": "Fixture List",
                            "description": "Displays a list of fixtures with match details"
                        },
                        {
                            "name": "Buy Match Tickets",
                            "description": "Allows users to purchase match tickets"
                        },
                        {
                            "name": "Match Centre",
                            "description": "Displays real-time data (if available) for live match stats"
                        }
                    ]
                },
                {
                    "name": "Match Results",
                    "description": "Lists completed matches",
                    "subfeatures": [
                        {
                            "name": "Result List",
                            "description": "Displays a list of results with match details"
                        }
                    ]
                },
                {
                    "name": "News Listing",
                    "description": "Displays a list of news articles",
                    "subfeatures": [
                        {
                            "name": "News Article",
                            "description": "Displays a single news article with embedded polls"
                        }
                    ]
                },
                {
                    "name": "League Tables",
                    "description": "Displays the current league table for the league in which the club\u2019s first team is playing",
                    "subfeatures": []
                },
                {
                    "name": "Player Listing",
                    "description": "Lists the players that make up the squad for the club\u2019s first team",
                    "subfeatures": [
                        {
                            "name": "Player Profile",
                            "description": "Displays further details for each player"
                        }
                    ]
                },
                {
                    "name": "Video Hub",
                    "description": "Acts as a video hub allowing fans access to key curated collections of video feeds",
                    "subfeatures": []
                }
            ]
        },
        {
            "module": "Apps",
            "features": [
                {
                    "name": "Latest Tab",
                    "description": "Provides an aggregated collection of the latest news content from the club",
                    "subfeatures": []
                },
                {
                    "name": "News",
                    "description": "Displays news articles with imagery, written content, and video content",
                    "subfeatures": []
                },
                {
                    "name": "Polls and Quizzes",
                    "description": "Displays polls and quizzes created by admins",
                    "subfeatures": []
                },
                {
                    "name": "Matches Tab",
                    "description": "Provides a list of past results and upcoming fixtures for the current season",
                    "subfeatures": []
                },
                {
                    "name": "League Tables Full List",
                    "description": "Presents the current league table for the league in which the club\u2019s first team is playing",
                    "subfeatures": []
                },
                {
                    "name": "Live Scores Full List",
                    "description": "Lists all the live scores for the relevant match day",
                    "subfeatures": []
                },
                {
                    "name": "Squad Full List (including Player Profiles)",
                    "description": "Provides a list of players that make up the squad for the club\u2019s first team",
                    "subfeatures": []
                },
                {
                    "name": "Player Profile",
                    "description": "Displays further details for each player",
                    "subfeatures": []
                },
                {
                    "name": "Match Centre",
                    "description": "Contains any specific match-related content including, but not limited to, Commentary and Statistics",       
                    "subfeatures": []
                },
                {
                    "name": "Club TV tab",
                    "description": "Showcases video content presented via a latest feed of all latest videos",
                    "subfeatures": []
                },
                {
                    "name": "More Tab",
                    "description": "Houses quick links to Live Scores, League Tables, Fixtures, Quizzes, User Account, Stadium Info, Supporters Guides, HR, Hiring, Recruitment and Job Opportunities and Settings and will sit on the main tab bar navigation",
                    "subfeatures": []
                },
                {
                    "name": "Account",
                    "description": "Houses information for in-app ticketing and previous predictions",
                    "subfeatures": []
                },
                {
                    "name": "Settings",
                    "description": "Collects a number of administration and configuration features",
                    "subfeatures": []
                },
                {
                    "name": "iOS Widgets",
                    "description": "Allows fans to stay on top of all things related to the club from their Home Screens",
                    "subfeatures": []
                },
                {
                    "name": "iOS Live Activities",
                    "description": "Provides real-time information at a glance without needing to unlock the app",
                    "subfeatures": []
                }
            ]
        }
    ]
}

# try:
#     wireframe = generate_wireframe(feature_breakdown)
#     print(json.dumps(wireframe, indent=2))
# except ValueError as e:
#     print("Error:", str(e))