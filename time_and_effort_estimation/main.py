import json
import os
import pandas as pd
from dotenv import load_dotenv
from together import Together

# Load API key
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=api_key)

# Pricing model (cost per day for each developer level)
pricing_model = {
    "Junior": 100,
    "Mid": 200,
    "Senior": 300
}

def estimate_effort(feature_breakdown):
    """Estimate development, testing, and DevOps efforts using Mistral LLM."""
    
    prompt = f"""
        Based on the given software features and subfeatures, estimate effort (in days) for each role:
        
        - **Development**
        - **Testing**
        - **DevOps**
        
        The estimation should be **granular**, providing effort at the **subfeature level** while maintaining the module and feature hierarchy.

        Ensure the output strictly follows this JSON format:

        {{
            "effort_estimation": [
                {{
                    "module": "Module Name",
                    "features": [
                        {{
                            "name": "Feature Name",
                            "subfeatures": [
                                {{
                                    "name": "Subfeature Name",
                                    "development_days": X,
                                    "testing_days": Y,
                                    "devops_days": Z
                                }}
                            ]
                        }}
                    ],
                    "development_days": X,
                    "testing_days": Y,
                    "devops_days": Z,
                }}
            ]
        }}

        **Guidelines:**
        - Assign **realistic effort estimates** based on standard development practices.
        - Complex subfeatures (e.g., authentication, API integrations) should have **higher effort estimates**.
        - Simple subfeatures (e.g., UI changes, minor configurations) should have **lower effort estimates**.
        - Ensure all values are in whole or decimal numbers representing effort in **days**.

        Features & Subfeatures:
        {feature_breakdown}

        Provide the output in valid JSON format only.
    """

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
        top_p=0.9,
        stop=["</s>"],
    )

    raw_output = response.choices[0].message.content.strip()

    # Debugging: Print raw output
    print("\n🔹 Raw Response from LLM:")
    print(raw_output)

    # Try to parse the output as JSON
    try:
        effort_data = json.loads(raw_output)
        if not isinstance(effort_data, dict) or "effort_estimation" not in effort_data:
            raise ValueError("Invalid JSON format received from the model.")
        return effort_data
    except json.JSONDecodeError as e:
        print(f"\n❌ Error parsing JSON: {e}")
        return None  # Return None to handle it gracefully

def generate_effort_csv(feature_breakdown, output_csv="effort_estimation.csv"):
    """Generate effort estimation CSV based on feature breakdown."""
    
    effort_data = estimate_effort(feature_breakdown)

    # Handle parsing errors
    if not effort_data:
        print("\n⚠️ No valid effort estimation data available.")
        return
    
    rows = []
    for module in effort_data["effort_estimation"]:
        module_name = module["module"]
        for feature in module["features"]:
            feature_name = feature["name"]
            for subfeature in feature.get("subfeatures", []):
                subfeature_name = subfeature["name"]
                dev_days = subfeature["development_days"]
                test_days = subfeature["testing_days"]
                devops_days = subfeature["devops_days"]

                # Cost calculations
                dev_cost = dev_days * pricing_model["Mid"]
                test_cost = test_days * pricing_model["Junior"]
                devops_cost = devops_days * pricing_model["Senior"]

                rows.append([
                    module_name, feature_name, subfeature_name,
                    dev_days, dev_cost, test_days, test_cost, devops_days, devops_cost
                ])

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(rows, columns=[
        "Module", "Feature", "Subfeature", "Dev Days", "Dev Cost",
        "Test Days", "Test Cost", "DevOps Days", "DevOps Cost"
    ])
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Effort estimation CSV generated: {output_csv}")

if __name__ == "__main__":
    # Example JSON feature breakdown
    feature_breakdown = {
        "functional_requirements": [
            "Website Scope of Work",
            "Development Site",
            "Content Migration",
            "Marketing",
            "iOS and Android Apps Scope of Work",
            "Dual language functionality",
            "Latest Tab",
            "News",
            "Polls and Quizzes",
            "Ads/Marketing",
            "Matches Tab",
            "League Tables Full List",
            "Live Scores Full List",
            "Squad Full List (including Player Profiles)",
            "Player Profile",
            "Match Centre",
            "Club TV tab",
            "More tab",
            "Account",
            "Settings",
            "Platform Parity and Deep Linking",
            "Push Notifications",
            "iOS Widgets",
            "iOS Live Activities"
        ],
        "non_functional_requirements": [
            "Dual language functionality",
            "Navigation Header (shared across different sites if feasible)"
        ],
        "feature_breakdown": [
            {
                "module": "Website",
                "features": [
                    {
                        "name": "Homepage",
                        "description": "Displays the main page of the website with live scores, news, and other important information.",
                        "subfeatures": []
                    },
                    {
                        "name": "Match Fixtures",
                        "description": "Lists upcoming football matches for the club.",
                        "subfeatures": [
                            {
                                "name": "Fixture Listing",
                                "description": "Displays a list of upcoming matches with details like date, time, opponent, and venue."
                            },
                            {
                                "name": "Buy Match Tickets",
                                "description": "Allows users to purchase tickets for upcoming matches."
                            }
                        ]
                    },
                    {
                        "name": "Match Results",
                        "description": "Displays the results of previously played matches.",
                        "subfeatures": [
                            {
                                "name": "Result Listing",
                                "description": "Displays a list of past match results with details like score, date, and opponent."
                            }
                        ]
                    },
                    {
                        "name": "Match Centre",
                        "description": "Provides real-time updates and detailed information about ongoing matches.",
                        "subfeatures": [
                            {
                                "name": "Live Match Stats",
                                "description": "Displays real-time statistics and updates about ongoing matches."
                            },
                            {
                                "name": "Commentary",
                                "description": "Provides live commentary and analysis of ongoing matches."
                            }
                        ]
                    },
                    {
                        "name": "League Tables",
                        "description": "Displays the current league standings for the club's football team.",
                        "subfeatures": []
                    },
                    {
                        "name": "News Listing",
                        "description": "Lists the latest news articles about the club.",
                        "subfeatures": [
                            {
                                "name": "News Article",
                                "description": "Displays a single news article with details like title, date, author, and content."
                            },
                            {
                                "name": "Export to PDF",
                                "description": "Allows users to export news articles as PDF files."
                            },
                            {
                                "name": "Graphical Summary",
                                "description": "Provides a visual summary of news articles, such as charts or graphs."
                            },
                            {
                                "name": "Data Filters",
                                "description": "Allows users to filter news articles by category, date, or author."
                            }
                        ]
                    },
                    {
                        "name": "Player Listing",
                        "description": "Lists all the players in the club's football team.",
                        "subfeatures": [
                            {
                                "name": "Player Profile",
                                "description": "Displays detailed information about a specific player, including biography, statistics, and social media links."     
                            }
                        ]
                    },
                    {
                        "name": "Video Hub",
                        "description": "Centralizes all video content related to the club.",
                        "subfeatures": [
                            {
                                "name": "Video Listing",
                                "description": "Displays a list of videos with details like title, date, and category."
                            },
                            {
                                "name": "Video Article",
                                "description": "Displays a single video article with details like title, description, and video player."
                            },
                            {
                                "name": "Export to PDF",
                                "description": "Allows users to export video articles as PDF files."
                            },
                            {
                                "name": "Graphical Summary",
                                "description": "Provides a visual summary of video articles, such as charts or graphs."
                            },
                            {
                                "name": "Data Filters",
                                "description": "Allows users to filter video articles by category, date, or player."
                            }
                        ]
                    },
                    {
                        "name": "Staff Listing",
                        "description": "Lists all the staff members in the club.",
                        "subfeatures": []
                    },
                    {
                        "name": "Partners",
                        "description": "Lists the club's partners and sponsors.",
                        "subfeatures": []
                    },
                    {
                        "name": "Maintenance",
                        "description": "Provides information about the club's maintenance schedule and policies.",
                        "subfeatures": []
                    },
                    {
                        "name": "Club Store",
                        "description": "Allows users to purchase merchandise related to the club.",
                        "subfeatures": []
                    },
                    {
                        "name": "Marketing",
                        "description": "Displays marketing materials and promotions for the club.",
                        "subfeatures": []
                    },
                    {
                        "name": "HR, Hiring, Recruitment and Job Opportunities",
                        "description": "Provides information about job opportunities within the club.",
                        "subfeatures": []
                    }
                ]
            },
            {
                "module": "iOS and Android Apps",
                "features": [
                    {
                        "name": "Latest Tab",
                        "description": "Displays the latest news, polls, and quizzes.",
                        "subfeatures": [
                            {
                                "name": "News Articles",
                                "description": "Displays the latest news articles with details like title, date, and author."
                            },
                            {
                                "name": "Polls",
                                "description": "Allows users to participate in polls and view the results."
                            },
                            {
                                "name": "Quizzes",
                                "description": "Allows users to participate in quizzes and view their scores."
                            }
                        ]
                    },
                    {
                        "name": "Matches Tab",
                        "description": "Displays information about upcoming and past matches.",
                        "subfeatures": [
                            {
                                "name": "Fixtures",
                                "description": "Displays a list of upcoming matches with details like date, time, opponent, and venue."
                            },
                            {
                                "name": "Results",
                                "description": "Displays a list of past match"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    

    # Generate CSV
generate_effort_csv(json.dumps(feature_breakdown))
