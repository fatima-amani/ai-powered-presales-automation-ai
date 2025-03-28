# AI-Powered Presales Automation AI

Welcome to the **AI-Powered Presales Automation AI** repository! This project leverages **Large Language Models (LLMs)** to automate key aspects of the presales process, such as requirement analysis, tech stack recommendations, effort estimation, and more. The goal is to reduce manual effort, enhance decision-making, and streamline presales workflows for greater efficiency.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [Start the FastAPI Server](#start-the-fastapi-server)
  - [Run with Docker](#run-with-docker)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

The **AI-Powered Presales Automation AI** system is designed to assist with automating presales workflows using **Large Language Models (LLMs)**. This AI-driven solution performs tasks like generating requirement breakdowns, suggesting tech stacks, creating architecture diagrams, and providing business insights—ultimately improving the speed and accuracy of presales decision-making. Whether you are looking for automated analysis or detailed reports, this project aims to optimize the presales process with AI.

---

## Features

- 📜 **Requirement Breakdown Generation**: Automatically generates **functional, non-functional**, and **feature breakdowns** based on client inputs using advanced LLMs.
- 🔧 **Tech Stack Recommendation**: Recommends the best technology stack for a project, based on specific business requirements and needs.
- 🏗️ **Architecture Diagram Generation**: Leverages AI to create architecture diagrams for systems, making it easier to visualize technical solutions.
- 📊 **AI-Powered Business Analyst**: Uses AI to analyze business requirements and generate meaningful insights that drive better decisions.
- 📈 **Effort Estimation & Excel Reports**: AI generates **effort estimations** and exports detailed analysis in **Excel reports**.
- 🎨 **Wireframe Generation**: AI-powered generation of wireframes with images stored in a database for easy access.

---

## Technologies Used

This project utilizes the following technologies:

- **Python**: Primary language for AI processing and backend development.
- **FastAPI**: High-performance web framework for building the API.
- **Large Language Models (LLMs)**: AI models used to generate insights, breakdowns, and recommendations.
- **OpenAI / Together.AI**: Used for AI-powered text generation and analysis.
- **MongoDB**: NoSQL database used to store processed data and reports.
- **Pandas**: Used for data manipulation and generating Excel reports.

---

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

Ensure you have the following tools installed:

- [Python 3.8+](https://www.python.org/)
- [MongoDB](https://www.mongodb.com/) (Local or cloud-based instance)
- [Docker](https://www.docker.com/) (Optional for containerized deployment)

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/fatima-amani/ai-powered-presales-automation-ai.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd ai-powered-presales-automation-ai
   ```

3. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:
   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

Create a `.env` file in the root directory and configure the following environment variables:

```env
TOGETHER_API_KEY=your_together_ai_api_key

EMAIL=your_usegalileo_ai_email
PASSWORD=your_usegalileo_ai_password

GITHUB_TOKEN=your_github_access_token
```

### Replace the placeholder values with actual credentials:

- **TOGETHER_API_KEY**: API key for Together.AI to facilitate AI processing.
- **EMAIL / PASSWORD**: Credentials for usegalileo.ai.
- **GITHUB_TOKEN**: GitHub access token for integration.

> 🚨 **Security Note**: Ensure that the `.env` file is **never committed** to version control. Add it to your `.gitignore` file for safety.

---

## Usage

### Start the FastAPI Server

To start the FastAPI backend, use the following command:

```bash
python app.py
```

The server will be accessible at [http://localhost:8000](http://localhost:8000).

### Run with Docker

If you prefer to run the project inside a Docker container, build and run the image using the following commands:

```bash
docker build -t ai-presales-automation-ai .
docker run -p 8000:8000 --env-file .env ai-presales-automation-ai
```

---


Thank you for checking out **AI-Powered Presales Automation AI**! We hope this project helps streamline and automate your presales process. If you have any questions or suggestions, feel free to open an issue or reach out! 😊
