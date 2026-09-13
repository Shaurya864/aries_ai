# ♈ ARIES (Local AI Assistant)

A secure, private, and efficient local AI assistant powered by the Google Gemini API. Aries is designed to give you direct control over your workflow, protect your personal data, and maintain strict local privacy without exposing your credentials or chat history to the cloud.

---

## 🚀 Features

* **Cloud-Powered Intelligence:** Integrates cleanly with the Google GenAI SDK using `gemini-3.6-flash` for fast and accurate processing.
* **Strict Local Privacy:** All conversation history, local databases (`.db`), and authentication tokens remain securely on your machine.
* **Zero-Leak Security:** Built with comprehensive `.gitignore` rules to ensure API keys and personal files are never accidentally committed or exposed.
* **Modular Architecture:** Clean separation of concerns between configuration management, core client logic, and user interfaces.

---

## 🛠️ Project Structure

```text
aries_phase2/
├── core/                # Core logic (AI client configuration, routing, etc.)
├── ui/                  # User interface components and app layout
├── .env                 # Local environment variables (Ignored by Git)
├── .env.example         # Template for required environment variables
├── .gitignore           # Git exclusion rules for secrets and local databases
├── config.py            # Centralized path and configuration resolver
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies

⚙️ Getting Started & Installation
1. Clone the Repository
Bash
git clone [https://github.com/YOUR-USERNAME/aries-local-assistant.git](https://github.com/YOUR-USERNAME/aries-local-assistant.git)
cd aries_phase2
2. Install Dependencies
Make sure you have Python installed, then install the required packages:

Bash
pip install -r requirements.txt
3. Configure Your Environment Secrets
Create a local .env file in the root directory by copying the template or creating one manually:

Code snippet
GEMINI_API_KEY=your_actual_gemini_api_key_here
(You can obtain a free API key from Google AI Studio.)

4. Run the Application
Start Aries locally from your terminal:

Bash
python main.py
🔒 Security & Privacy Notice
Aries is built with privacy-first principles:

API Keys: Never hardcode your API key into any python scripts. Always use environment variables (.env).

Databases: Local SQLite files (*.db) and history logs are excluded via .gitignore to prevent tracking personal chat logs.

📄 License
This project is open-source and available for personal use and customization.

Example-
<img width="1377" height="887" alt="image" src="https://github.com/user-attachments/assets/f9e49917-1783-4b16-9490-6473e5aca425" />
