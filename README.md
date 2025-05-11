# 🍳 ByteCook - Black Forest Hackathon, Freiburg, May 2025

> 🌐 **Experience our app live at [bytecook.philenius.de/](https://bytecook.philenius.de/)!** 🚀

**📄 Challenge:** [Challenge 2 - KOCH - Service Specification Document Transformer](https://www.blackforesthackathon.de/challenges-data-decoded/)

**👥 Team Name:** ByteCook

**🧑‍🤝‍🧑 Team Members:** Robert, Sebastian, Jannik, Christof, Philipp

🎉 Welcome! This repository contains the submission of team _ByteCook_. This project was crafted with passion during the **[Black Forest Hackathon in Freiburg in May 2025](https://www.blackforesthackathon.de/may/)**. The app is built using **Streamlit** 🖥️ and provides an intuitive interface for users to explore ByteCook's features.

## 🚀 Solution: Service Specification Document Transformer

Our Streamlit app directly addresses the challenge of transforming complex Service Specification Documents into actionable business insights. Here's how it works:

1. **PDF Upload:** Users can upload a Service Specification Document (PDF) through the app's intuitive interface.
2. **AI-Powered Analysis:** Using advanced Large Language Models (LLMs) via OpenRouter, the app analyzes the uploaded document to extract relevant sections.
3. **Structured Quotation Items:** Leveraging the capabilities of advanced LLMs, the extracted content is automatically categorized into KOCH's products, accessories, and services through prompt engineering. This content is then organized into editable Quotation Items for seamless user interaction.
4. **Side-by-Side View:** The app displays the structured Quotation Items alongside the original PDF for easy comparison and validation.
5. **User Interaction:** Users can edit the extracted items to ensure accuracy and completeness.
6. **ERP Integration:** Once finalized, the structured Quotation Items can be exported as a clean XML file, ready for seamless ERP system integration.

This solution combines the power of AI with a user-friendly interface, enabling non-technical users to process complex documents with ease and precision.

## 🛠️ How to Run This App

### 🚢 Deployment with Docker Compose

1. **To deploy the app using Docker Compose, run the following command:**
   ```bash
   OPENROUTER_API_KEY="<your_api_key_here>" docker-compose up
   ```
   > **Note:** If the `docker-compose` command is unavailable, use the following alternative:
   >
   > ```bash
   > OPENROUTER_API_KEY="<your_api_key_here>" docker compose up
   > ```
2. **You're all set! Access the app in your browser at http://localhost:8501.**

### 💻 Local Development

For local development, follow these steps:

1. **Create a Python virtual environment:**

   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies with Pip:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your OpenRouter API key in the `./src/.env` file:**

   ```env
   OPENROUTER_API_KEY = "<your_api_key_here>"
   ```

5. **Run the Streamlit app from the root directory of the app:**

   ```bash
   streamlit run src/streamlit-app.py
   ```

6. **You're all set! Access the app in your browser at http://localhost:8501.**
