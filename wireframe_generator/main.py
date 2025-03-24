import os
import re
import json
import time
from together import Together
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load API key from .env file
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# Initialize Together client
client = Together(api_key=api_key)

def generate_prompt(feature_breakdown):
    """Generates a natural language description of the feature breakdown."""
    prompt = (
        "Given the following JSON feature breakdown, generate a concise natural language description "
        "focusing **only on Website features**. "
        "Completely ignore any content related to Mobile or Apps, and exclude all mentions of mobile-specific tabs or features. "
        "The description must be strictly under 1000 characters, and avoid repeating similar sections:\n\n"
        f"{json.dumps(feature_breakdown, indent=2)}"
    )

    return prompt

def get_llm_response(prompt):
    """Fetches the response from an LLM (like OpenAI GPT) based on the feature breakdown."""
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

    return response.choices[0].message.content

def selenium_pipeline(feature_breakdown):
    """Executes the Selenium automation pipeline."""

    

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    # Step 1: Navigate to login page
    driver.get("https://www.usegalileo.ai/login")
    time.sleep(5)
    
    # Step 2 & 3: Enter credentials and log in
    email_box = driver.find_element(By.TAG_NAME, "input")
    email_box.click()
    email_box.send_keys(email)
    email_box.send_keys(Keys.ENTER)
    time.sleep(2)
    
    password_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='password']"))
    )
    password_box.send_keys(password)
    password_box.send_keys(Keys.ENTER)
    time.sleep(5)
    
    # Step 4: Navigate to create page and interact with UI
    driver.get("https://www.usegalileo.ai/create")
    time.sleep(5)

    driver.find_element(By.ID, "start-new-design").click()
    time.sleep(2)
    
    # # Step 5: Select Web option and input prompt
    driver.find_element(By.XPATH, "//html/body/div[1]/main/div[2]/div/div[2]/div/div[2]/div/div/footer/div/div/div[2]/div[1]/div/button[2]").click()
    time.sleep(2)
    
    # # Generate LLM-based prompt
    llm_prompt = generate_prompt(feature_breakdown)
    llm_response = get_llm_response(llm_prompt)

    # Wait for the textbox to appear
    textbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
    )

    # Click the textbox to activate it
    textbox.click()
    time.sleep(10)

    # print(llm_response)
    
    driver.execute_script("arguments[0].innerText = arguments[1];", textbox, llm_response)
    textbox.send_keys(Keys.SPACE)
    textbox.send_keys(Keys.ENTER)
    
    # # Step 6: Wait for UI to generate
    time.sleep(60)

    textbox = driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
    textbox.click()
    textbox.send_keys("Yes, generate it")
    textbox.send_keys(Keys.ENTER)
    # driver.execute_script("arguments[0].innerText = arguments[1];", textbox, "yes generate it")
    # textbox.send_keys(Keys.SPACE)
    # textbox.send_keys(Keys.ENTER)

    time.sleep(60)
    
    # Step 7: Extract image links
    image_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'https://cdn.usegalileo.ai/') or contains(@srcset, 'https://cdn.usegalileo.ai/')]")

    img_links = []

    for img in image_elements:
        srcset = img.get_attribute("srcset")
        if srcset:
            # Extract URLs from srcset that contain 'cdn.usegalileo.ai'
            urls = [entry.split(" ")[0] for entry in srcset.split(",") if "cdn.usegalileo.ai" in entry]
            img_links.extend(urls)

    # Print all extracted image links
    print(img_links)
    driver.quit()

    return img_links

# Example usage

if __name__ == "__main__":
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
    
    image_links = selenium_pipeline(feature_breakdown)
    print(image_links)